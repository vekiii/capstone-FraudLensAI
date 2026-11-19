"""Explicit offline, label-free consumer index; never modifies producer stores."""

import hashlib
import json
import sqlite3
import time
from contextlib import closing, contextmanager
from datetime import UTC, datetime
from pathlib import Path

FIELDS = (
    "event_time_utc",
    "event_time_raw",
    "time_basis",
    "sender_bank",
    "sender_account",
    "receiver_bank",
    "receiver_account",
    "paid_amount",
    "paid_currency",
    "received_amount",
    "received_currency",
)


def file_digest(path):
    with Path(path).open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def signature(path):
    stat = Path(path).stat()
    return [stat.st_size, stat.st_mtime_ns]


def frozen(path):
    wal = Path(str(path) + "-wal")
    if wal.exists() and wal.stat().st_size:
        raise ValueError("stale_snapshot")


def instant_key(value):
    at = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if at.utcoffset() is None or at.utcoffset().total_seconds() != 0:
        raise ValueError("History time must be UTC")
    delta = at - datetime(1970, 1, 1, tzinfo=UTC)
    return (delta.days * 86400 + delta.seconds) * 1000000 + delta.microseconds


@contextmanager
def read_connection(path, tables, bounded=True):
    with closing(
        sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True, timeout=1)
    ) as db:
        db.execute("PRAGMA query_only=ON")
        deadline = time.monotonic() + 5
        if bounded:
            db.set_progress_handler(lambda: int(time.monotonic() >= deadline), 1000)
        db.set_authorizer(
            lambda action, table, column, database, trigger: (
                sqlite3.SQLITE_DENY
                if action == sqlite3.SQLITE_READ and table not in tables
                else sqlite3.SQLITE_OK
            )
        )
        db.execute("BEGIN")
        yield db


def prepare_history_index(source, output):
    """Build a NEW index from a frozen, completed actual or authored-test source.

    Offline streaming preparation has no five-second scan deadline. Runtime
    queries keep that deadline. Only explicit operational columns are copied.
    Failed/incomplete outputs remain unusable, never silently republished.
    """
    source, output = Path(source).resolve(), Path(output).resolve()
    if output.exists() or source == output:
        raise FileExistsError("History index output must be new")
    frozen(source)
    before, source_hash = signature(source), file_digest(source)
    with read_connection(
        source, {"active_dataset", "dataset_versions", "operational_events"}, bounded=False
    ) as db:
        row = db.execute("""SELECT d.id,d.rejected_records FROM active_dataset a
            JOIN dataset_versions d ON a.version=d.id
            WHERE a.singleton=1 AND d.status='complete'""").fetchone()
        if row is None:
            raise ValueError("Completed active history source required")
        version, rejected = row
        # Reserve exclusively: preparation never overwrites an existing file.
        with output.open("xb"):
            pass
        with closing(sqlite3.connect(output)) as target:
            target.execute("PRAGMA journal_mode=WAL")
            target.execute("PRAGMA synchronous=FULL")
            target.execute(
                "CREATE TABLE history_source(singleton INTEGER PRIMARY KEY,content TEXT)"
            )
            target.execute("""CREATE TABLE history_events(
                transaction_id TEXT PRIMARY KEY,event_key INTEGER NOT NULL,
                event_time_utc TEXT NOT NULL,event_time_raw TEXT NOT NULL,time_basis TEXT NOT NULL,
                sender_bank TEXT NOT NULL,sender_account TEXT NOT NULL,
                receiver_bank TEXT NOT NULL,receiver_account TEXT NOT NULL,
                paid_amount TEXT NOT NULL,paid_currency TEXT NOT NULL,
                received_amount TEXT NOT NULL,received_currency TEXT NOT NULL)""")
            target.commit()
            count, earliest, earliest_key = 0, None, None
            select = ",".join("json_extract(payload_json,'$." + field + "')" for field in FIELDS)
            cursor = db.execute(
                "SELECT transaction_id," + select + " FROM operational_events WHERE version=?",
                (version,),
            )
            target.execute("BEGIN IMMEDIATE")
            batch = []
            for event in cursor:
                if not all(isinstance(value, str) for value in event):
                    raise ValueError("Invalid operational history projection")
                key = instant_key(event[1])
                if earliest_key is None or key < earliest_key:
                    earliest, earliest_key = event[1], key
                batch.append((event[0], key, *event[1:]))
                count += 1
                if len(batch) == 1000:
                    target.executemany(
                        "INSERT INTO history_events VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", batch
                    )
                    batch.clear()
            if batch:
                target.executemany(
                    "INSERT INTO history_events VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", batch
                )
            target.execute(
                "CREATE INDEX sender_history ON history_events(sender_bank,sender_account,event_key)"
            )
            target.execute(
                "CREATE INDEX receiver_history ON history_events(receiver_bank,receiver_account,event_key)"
            )
            frozen(source)
            if signature(source) != before or file_digest(source) != source_hash:
                raise ValueError("History source changed during preparation")
            metadata = dict(
                version=1,
                status="complete",
                dataset_version=version,
                source_path=str(source),
                source_signature=before,
                source_sha256=source_hash,
                rejected_records=rejected,
                earliest=earliest,
                row_count=count,
            )
            target.execute("INSERT INTO history_source VALUES(1,?)", (json.dumps(metadata),))
            target.commit()
    return dict(
        source_sha256=source_hash,
        index_sha256=file_digest(output),
        dataset_version=version,
        row_count=count,
    )


class HistoryIndex:
    """Lazy adapter component, created only for a live context/history read."""

    def __init__(self, source, path, expected_sha256):
        self.source, self.path = Path(source).resolve(), Path(path).resolve()
        frozen(self.source)
        frozen(self.path)
        if file_digest(self.path) != expected_sha256:
            raise ValueError("stale_snapshot")
        with read_connection(self.path, {"history_source"}) as db:
            row = db.execute("SELECT content FROM history_source WHERE singleton=1").fetchone()
        if row is None:
            raise ValueError("stale_snapshot")
        self.metadata = json.loads(row[0])
        if (
            self.metadata.get("version") != 1
            or self.metadata.get("status") != "complete"
            or Path(self.metadata["source_path"]) != self.source
            or signature(self.source) != self.metadata["source_signature"]
            or file_digest(self.source) != self.metadata["source_sha256"]
        ):
            raise ValueError("stale_snapshot")
        self.index_signature = signature(self.path)
        self.guard(self.metadata["dataset_version"])

    def guard(self, version):
        frozen(self.source)
        frozen(self.path)
        if (
            version != self.metadata["dataset_version"]
            or signature(self.source) != self.metadata["source_signature"]
            or signature(self.path) != self.index_signature
        ):
            raise ValueError("stale_snapshot")

    def earliest(self, version):
        self.guard(version)
        return self.metadata["earliest"]

    @contextmanager
    def rows(self, version, identity, start, cutoff, focal):
        self.guard(version)
        with read_connection(self.path, {"history_events"}) as db:
            cursor = db.execute(
                """SELECT transaction_id,event_time_utc,event_time_raw,time_basis,
                sender_bank,sender_account,receiver_bank,receiver_account,
                paid_amount,paid_currency,received_amount,received_currency
                FROM history_events WHERE event_key>=? AND event_key<? AND transaction_id<>?
                AND ((sender_bank=? AND sender_account=?) OR (receiver_bank=? AND receiver_account=?))
                ORDER BY event_key,transaction_id""",
                (
                    instant_key(start),
                    instant_key(cutoff),
                    focal,
                    identity["bank"],
                    identity["account"],
                    identity["bank"],
                    identity["account"],
                ),
            )
            yield cursor
        self.guard(version)
