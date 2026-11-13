"""Local versioned SQLite store for Feature 002 canonical imports.

No HTTP or CLI import surface is exposed here. Private evaluation labels use a
separate table and an explicit offline role read boundary.
"""
import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path

from fraudlens.data_contracts import (
    CanonicalTransaction,
    StoredOperationalEvent,
    StoredPrivateLabel,
)
from fraudlens.data_import import derive_dataset_version

_SCHEMA_VERSION = 1
_VERSION_ID = re.compile(r'dv_[0-9a-f]{64}\Z')
_TX_ID = re.compile(r'D[0-9a-f]{32}\Z')
_CASE_ID = re.compile(r'C[0-9a-f]{32}\Z')
_BATCH_SIZE = 512


class DatasetStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.connection = sqlite3.connect(self.path)
        self.connection.execute('PRAGMA foreign_keys = ON')
        version = self.connection.execute('PRAGMA user_version').fetchone()[0]
        if version not in (0, _SCHEMA_VERSION):
            self.connection.close()
            raise ValueError('Unsupported SQLite schema version')
        if version == 0:
            with self.connection:
                self.connection.executescript('''
                    CREATE TABLE dataset_versions (
                        id TEXT PRIMARY KEY,
                        status TEXT NOT NULL CHECK(status IN ('staged','complete','failed')),
                        source_records INTEGER NOT NULL CHECK(source_records >= 0),
                        rejected_records INTEGER NOT NULL DEFAULT 0,
                        source_sha256 TEXT,
                        mapping_sha256 TEXT,
                        time_policy_sha256 TEXT,
                        error TEXT
                    );
                    CREATE TABLE operational_events (
                        version TEXT NOT NULL REFERENCES dataset_versions(id),
                        transaction_id TEXT NOT NULL,
                        case_id TEXT NOT NULL,
                        payload_json TEXT,
                        PRIMARY KEY(version, transaction_id),
                        UNIQUE(version, case_id)
                    );
                    CREATE TABLE private_evaluation_labels (
                        version TEXT NOT NULL,
                        transaction_id TEXT NOT NULL,
                        status TEXT NOT NULL,
                        value INTEGER,
                        PRIMARY KEY(version, transaction_id),
                        FOREIGN KEY(version, transaction_id)
                            REFERENCES operational_events(version, transaction_id)
                    );
                    CREATE TABLE active_dataset (
                        singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                        version TEXT NOT NULL REFERENCES dataset_versions(id)
                    );
                    CREATE INDEX operational_identity_lookup ON operational_events(transaction_id);
                    CREATE INDEX operational_case_lookup ON operational_events(case_id);
                    PRAGMA user_version = 1;
                ''')

    def close(self):
        self.connection.close()

    def _status(self, version: str):
        row = self.connection.execute(
            'SELECT status,source_records,source_sha256,mapping_sha256,time_policy_sha256 '
            'FROM dataset_versions WHERE id=?', (version,)
        ).fetchone()
        return row

    def version_status(self, version: str) -> str | None:
        row = self._status(version)
        return row[0] if row else None

    def stage(self, version: str, *, source_records: int,
              source_sha256: str | None = None, mapping_sha256: str | None = None,
              time_policy_sha256: str | None = None) -> None:
        if _VERSION_ID.fullmatch(version) is None or type(source_records) is not int or source_records < 0:
            raise ValueError('Invalid dataset version or record count')
        provenance = (source_sha256, mapping_sha256, time_policy_sha256)
        if any(value is not None for value in provenance):
            if (not all(isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value)
                        for value in provenance)
                    or derive_dataset_version(*(bytes.fromhex(value)
                                                for value in provenance)) != version):
                raise ValueError('DatasetVersion provenance does not match ID')
        with self.connection:
            existing = self._status(version)
            if existing is None:
                self.connection.execute(
                    'INSERT INTO dataset_versions(id,status,source_records,source_sha256,'
                    'mapping_sha256,time_policy_sha256) VALUES (?,?,?,?,?,?)',
                    (version, 'staged', source_records, *provenance))
            elif existing[0] == 'complete':
                if existing[1] != source_records or (any(provenance) and existing[2:] != provenance):
                    raise ValueError('Complete import is immutable')
            else:
                self.connection.execute('DELETE FROM private_evaluation_labels WHERE version=?',
                                        (version,))
                self.connection.execute('DELETE FROM operational_events WHERE version=?', (version,))
                if any(provenance) and any(existing[2:]) and existing[2:] != provenance:
                    raise ValueError('Retry provenance differs from previous attempt')
                self.connection.execute(
                    "UPDATE dataset_versions SET status='staged',source_records=?,"
                    'rejected_records=0,error=NULL,source_sha256=?,mapping_sha256=?,'
                    'time_policy_sha256=? WHERE id=?',
                    (source_records, *(provenance if any(provenance) else existing[2:]),
                     version))

    @staticmethod
    def _payload(event: CanonicalTransaction) -> str:
        facts = {
            'source_ordinal': event.source_ordinal,
            'event_time_raw': event.event_time_raw,
            'event_time_utc': event.event_time_utc.isoformat(),
            'event_time_epoch_ns': event.event_time_epoch_ns,
            'time_basis': event.time_basis,
            'sender_bank': event.sender_bank,
            'sender_account': event.sender_account,
            'receiver_bank': event.receiver_bank,
            'receiver_account': event.receiver_account,
            'sender_join_key': event.sender_join_key.hex(),
            'receiver_join_key': event.receiver_join_key.hex(),
            'paid_amount': event.paid_amount,
            'paid_currency': event.paid_currency,
            'received_amount': event.received_amount,
            'received_currency': event.received_currency,
            'payment_format': event.payment_format,
            'event_fact_digest': event.event_fact_digest.hex(),
        }
        return json.dumps(facts, sort_keys=True, separators=(',', ':'), ensure_ascii=True)

    def _insert_event(self, version: str, transaction_id: str,
                      case_id: str, payload: str | None):
        if (_TX_ID.fullmatch(transaction_id) is None
                or _CASE_ID.fullmatch(case_id) is None):
            raise ValueError('Invalid D/C identity')
        old = self.connection.execute(
            'SELECT case_id,payload_json FROM operational_events '
            'WHERE version=? AND transaction_id=?',
            (version, transaction_id)).fetchone()
        if old:
            if old != (case_id, payload):
                raise ValueError('Identity collision or changed fact')
            return
        prior = self.connection.execute(
            'SELECT case_id,payload_json FROM operational_events '
            'WHERE transaction_id=? AND version<>?',
            (transaction_id, version)).fetchall()
        if any(previous != (case_id, payload) for previous in prior):
            raise ValueError('Cross-version identity collision or changed fact')
        prior_case = self.connection.execute(
            'SELECT transaction_id FROM operational_events WHERE case_id=? AND version<>?',
            (case_id, version)).fetchall()
        if any(previous[0] != transaction_id for previous in prior_case):
            raise ValueError('Cross-version C identity collision')
        self.connection.execute(
            'INSERT INTO operational_events(version,transaction_id,case_id,payload_json) '
            'VALUES (?,?,?,?)', (version, transaction_id, case_id, payload))

    def add_event(self, version: str, transaction_id: str | CanonicalTransaction,
                  *, case_id: str | None = None):
        event = transaction_id if isinstance(transaction_id, CanonicalTransaction) else None
        if event is not None:
            transaction_id, case_id = event.transaction_id, event.case_id
        if case_id is None:
            raise ValueError('Canonical C identity is required')
        payload = self._payload(event) if event is not None else None
        state = self.version_status(version)
        if state not in ('staged', 'complete'):
            raise ValueError('Dataset version is not staged')
        with self.connection:
            if state == 'complete':
                old = self.connection.execute(
                    'SELECT case_id,payload_json FROM operational_events '
                    'WHERE version=? AND transaction_id=?',
                    (version, transaction_id)).fetchone()
                if old != (case_id, payload):
                    raise ValueError('Complete import is immutable')
                return
            self._insert_event(version, transaction_id, case_id, payload)

    def add_rejection(self, version: str):
        if self.version_status(version) != 'staged':
            raise ValueError('Dataset version is not staged')
        with self.connection:
            self.connection.execute(
                'UPDATE dataset_versions SET rejected_records=rejected_records+1 WHERE id=?',
                (version,))

    def set_source_records(self, version: str, source_records: int):
        """Finalize the stream count before completion; never alter a complete version."""
        if self.version_status(version) != 'staged' or type(source_records) is not int or source_records < 0:
            raise ValueError('Invalid staged source record count')
        with self.connection:
            self.connection.execute('UPDATE dataset_versions SET source_records=? WHERE id=?',
                                    (source_records, version))

    def add_private_label(self, version: str, transaction_id: str,
                          *, value: int | None, status: str):
        if self.version_status(version) != 'staged':
            raise ValueError('Private labels cannot change a completed version')
        if ((status == 'eligible_positive' and value != 1)
                or (status == 'eligible_negative' and value != 0)
                or (status in {'missing', 'invalid', 'unsupported'} and value is not None)
                or status not in {'eligible_positive', 'eligible_negative', 'missing',
                                  'invalid', 'unsupported'}):
            raise ValueError('Invalid private label')
        with self.connection:
            self.connection.execute(
                'INSERT INTO private_evaluation_labels(version,transaction_id,status,value) '
                'VALUES (?,?,?,?)', (version, transaction_id, status, value))

    def ingest(self, version: str, rows):
        """Consume bounded batches atomically; parser exceptions fail the stage."""
        if self.version_status(version) != 'staged':
            raise ValueError('Dataset version is not staged')
        try:
            with self.connection:
                batch = []
                for row in rows:
                    if isinstance(row, tuple):
                        transaction_id, case_id = row
                        payload = None
                    else:
                        transaction_id, case_id = row.transaction_id, row.case_id
                        payload = self._payload(row)
                    batch.append((transaction_id, case_id, payload))
                    if len(batch) >= _BATCH_SIZE:
                        self._flush_batch(version, batch)
                        batch.clear()
                self._flush_batch(version, batch)
        except Exception:
            self.fail(version, reason='parser_or_batch_failure')
            raise

    def ingest_canonical_rows(self, version: str, rows) -> dict[str, int]:
        """Stream canonical rows through bounded SQLite transactions.

        The caller verifies the source hash before staging and completes only
        after the iterator has exhausted without a structural error.
        """
        if self.version_status(version) != 'staged':
            raise ValueError('Dataset version is not staged')
        has_prior_events = self.connection.execute(
            'SELECT 1 FROM operational_events WHERE version<>? LIMIT 1',
            (version,)).fetchone() is not None
        counts = dict(source_records=0, event_valid=0, event_rejected=0,
                      label_eligible=0, label_ineligible=0, positives=0,
                      negatives=0)
        batch = []
        for row, event, label in rows:
            counts['source_records'] += 1
            if event is None:
                counts['event_rejected'] += 1
            else:
                counts['event_valid'] += 1
                if label.value is None:
                    counts['label_ineligible'] += 1
                else:
                    counts['label_eligible'] += 1
                    counts['positives' if label.value == 1 else 'negatives'] += 1
            batch.append((row, event, label))
            if len(batch) >= _BATCH_SIZE:
                self._flush_canonical_batch(version, batch, has_prior_events)
                batch.clear()
        self._flush_canonical_batch(version, batch, has_prior_events)
        return counts

    def _flush_canonical_batch(self, version, batch, has_prior_events):
        if not batch:
            return
        events = [(version, event.transaction_id, event.case_id, self._payload(event))
                  for _, event, _ in batch if event is not None]
        labels = [(version, event.transaction_id, label.status, label.value)
                  for _, event, label in batch if event is not None]
        rejected = len(batch) - len(events)
        with self.connection:
            if has_prior_events:
                for _, transaction_id, case_id, payload in events:
                    self._insert_event(version, transaction_id, case_id, payload)
            else:
                self.connection.executemany(
                    'INSERT INTO operational_events(version,transaction_id,case_id,payload_json) '
                    'VALUES (?,?,?,?)', events)
            self.connection.executemany(
                'INSERT INTO private_evaluation_labels(version,transaction_id,status,value) '
                'VALUES (?,?,?,?)', labels)
            if rejected:
                self.connection.execute(
                    'UPDATE dataset_versions SET rejected_records=rejected_records+? WHERE id=?',
                    (rejected, version))

    def _flush_batch(self, version, batch):
        for transaction_id, case_id, payload in batch:
            self._insert_event(version, transaction_id, case_id, payload)

    def event_count(self, version: str) -> int:
        return self.connection.execute(
            'SELECT COUNT(*) FROM operational_events WHERE version=?', (version,)
        ).fetchone()[0]

    def case_count(self, version: str) -> int:
        return self.connection.execute(
            'SELECT COUNT(DISTINCT case_id) FROM operational_events WHERE version=?',
            (version,)).fetchone()[0]

    def complete(self, version: str):
        with self.connection:
            row = self._status(version)
            if row is None:
                raise ValueError('Dataset version is not staged')
            if row[0] == 'complete':
                return
            if row[0] != 'staged':
                raise ValueError('Failed import cannot complete')
            rejected = self.connection.execute(
                'SELECT rejected_records FROM dataset_versions WHERE id=?',
                (version,)).fetchone()[0]
            valid_count = self.event_count(version)
            if row[1] != valid_count + rejected:
                raise ValueError('Import row reconciliation failed')
            if row[2] is not None:
                label_count = self.connection.execute(
                    'SELECT COUNT(*) FROM private_evaluation_labels WHERE version=?',
                    (version,)).fetchone()[0]
                if label_count != valid_count:
                    raise ValueError('Private label status missing for an event-valid row')
            self.connection.execute(
                "UPDATE dataset_versions SET status='complete' WHERE id=?", (version,))

    def fail(self, version: str, *, reason: str):
        if self.version_status(version) != 'staged':
            raise ValueError('Only staged import can fail')
        with self.connection:
            self.connection.execute('DELETE FROM private_evaluation_labels WHERE version=?',
                                    (version,))
            self.connection.execute('DELETE FROM operational_events WHERE version=?',
                                    (version,))
            self.connection.execute(
                "UPDATE dataset_versions SET status='failed',error=? WHERE id=?",
                (reason[:120], version))

    def activate(self, version: str):
        if self.version_status(version) != 'complete':
            raise ValueError('Only complete import is selectable')
        with self.connection:
            self.connection.execute(
                'INSERT INTO active_dataset(singleton,version) VALUES (1,?) '
                'ON CONFLICT(singleton) DO UPDATE SET version=excluded.version', (version,))

    def active_version(self) -> str | None:
        row = self.connection.execute(
            'SELECT version FROM active_dataset WHERE singleton=1').fetchone()
        return row[0] if row else None

    def operational_events(self, version: str) -> list[StoredOperationalEvent]:
        if self.version_status(version) != 'complete':
            raise ValueError('Only complete import is selectable')
        rows = self.connection.execute(
            'SELECT transaction_id,case_id,payload_json FROM operational_events WHERE version=? '
            'ORDER BY transaction_id', (version,)).fetchall()
        result = []
        for transaction_id, case_id, payload in rows:
            facts = json.loads(payload) if payload else None
            if facts is not None:
                facts.pop('source_ordinal', None)  # internal reconciliation key, not an input
            result.append(StoredOperationalEvent(transaction_id, case_id, facts))
        return result

    def private_labels(self, version: str, *, role: str) -> list[StoredPrivateLabel]:
        if role != 'offline_evaluation':
            raise PermissionError('Private evaluation labels require offline role')
        if self.version_status(version) != 'complete':
            raise ValueError('Only complete import is selectable')
        rows = self.connection.execute(
            'SELECT transaction_id,value,status FROM private_evaluation_labels '
            'WHERE version=? ORDER BY transaction_id', (version,)).fetchall()
        return [StoredPrivateLabel(*row) for row in rows]

    def complete_report(self, version: str):
        if self.version_status(version) != 'complete':
            return None
        row = self.connection.execute(
            'SELECT source_records,rejected_records FROM dataset_versions WHERE id=?',
            (version,)).fetchone()
        labels = dict(self.connection.execute(
            'SELECT status,COUNT(*) FROM private_evaluation_labels WHERE version=? '
            'GROUP BY status', (version,)).fetchall())
        positives = labels.get('eligible_positive', 0)
        negatives = labels.get('eligible_negative', 0)
        valid = self.event_count(version)
        eligible = positives + negatives
        return {'source_records': row[0], 'event_valid': valid,
                'event_rejected': row[1], 'label_eligible': eligible,
                'label_ineligible': valid - eligible, 'positives': positives,
                'negatives': negatives}

    def _ensure_feature_tables(self):
        """Add the feature projection lazily; opening an import never changes it."""
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS feature_builds (
                    version TEXT NOT NULL REFERENCES dataset_versions(id),
                    feature_version TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('staged','complete','failed')),
                    snapshot_count INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY(version, feature_version)
                )''')
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS feature_snapshots (
                    version TEXT NOT NULL,
                    feature_version TEXT NOT NULL,
                    transaction_id TEXT NOT NULL,
                    event_time TEXT NOT NULL,
                    as_of TEXT NOT NULL,
                    coverage_start TEXT NOT NULL,
                    coverage_state TEXT NOT NULL,
                    scoreable INTEGER NOT NULL,
                    feature_input_digest TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    PRIMARY KEY(version, feature_version, transaction_id),
                    FOREIGN KEY(version, feature_version)
                        REFERENCES feature_builds(version, feature_version)
                )''')

    def iter_canonical_events(self, version: str):
        """Stream complete operational facts by event time, never private labels."""
        if self.version_status(version) != 'complete':
            raise ValueError('dataset_incomplete')
        cursor = self.connection.execute('''
            SELECT transaction_id, case_id, payload_json FROM operational_events
            WHERE version=?
            ORDER BY CAST(json_extract(payload_json, '$.event_time_epoch_ns') AS INTEGER),
                     transaction_id''', (version,))
        for transaction_id, case_id, payload in cursor:
            if payload is None:
                raise ValueError('dataset_incompatible')
            facts = json.loads(payload)
            yield CanonicalTransaction(
                transaction_id=transaction_id, case_id=case_id,
                source_ordinal=facts['source_ordinal'],
                event_time_raw=facts['event_time_raw'],
                event_time_utc=datetime.fromisoformat(facts['event_time_utc']),
                event_time_epoch_ns=facts['event_time_epoch_ns'],
                time_basis=facts['time_basis'],
                sender_bank=facts['sender_bank'], sender_account=facts['sender_account'],
                receiver_bank=facts['receiver_bank'],
                receiver_account=facts['receiver_account'],
                sender_join_key=bytes.fromhex(facts['sender_join_key']),
                receiver_join_key=bytes.fromhex(facts['receiver_join_key']),
                paid_amount=facts['paid_amount'], paid_currency=facts['paid_currency'],
                received_amount=facts['received_amount'],
                received_currency=facts['received_currency'],
                payment_format=facts['payment_format'],
                event_fact_digest=bytes.fromhex(facts['event_fact_digest']))

    def feature_snapshot_count(self, version: str, feature_version: str = 'history-v1'):
        """Only completed builds are visible, including after interrupted processes."""
        if not self._feature_tables_exist():
            return None
        row = self.connection.execute('''
            SELECT snapshot_count FROM feature_builds
            WHERE version=? AND feature_version=? AND status='complete' ''',
            (version, feature_version)).fetchone()
        return row[0] if row else None

    def _feature_tables_exist(self):
        return self.connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='feature_builds'"
        ).fetchone() is not None

    def build_features(self, version: str, *, feature_version: str = 'history-v1') -> dict:
        """Stage bounded snapshot batches and publish only after full reconciliation."""
        from fraudlens.feature_history import FEATURE_VERSION, iter_feature_snapshots

        if feature_version != FEATURE_VERSION:
            raise ValueError('dataset_incompatible')
        row = self._status(version)
        if row is None or row[0] != 'complete':
            raise ValueError('dataset_incomplete')
        provenance = row[2:]
        if (not all(isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value)
                    for value in provenance)
                or derive_dataset_version(*(bytes.fromhex(value)
                                            for value in provenance)) != version):
            raise ValueError('dataset_incompatible')
        self._ensure_feature_tables()
        existing = self.connection.execute('''
            SELECT status,snapshot_count FROM feature_builds
            WHERE version=? AND feature_version=?''', (version, feature_version)).fetchone()
        if existing and existing[0] == 'complete':
            actual = self.connection.execute('''
                SELECT COUNT(*) FROM feature_snapshots
                WHERE version=? AND feature_version=?''',
                (version, feature_version)).fetchone()[0]
            if actual != existing[1] or actual != self.event_count(version):
                raise ValueError('dataset_incompatible')
            return {'snapshot_count': existing[1], 'repeated': True}
        with self.connection:
            self.connection.execute('''
                INSERT INTO feature_builds(version,feature_version,status,snapshot_count)
                VALUES (?,?,'staged',0)
                ON CONFLICT(version,feature_version)
                DO UPDATE SET status='staged',snapshot_count=0''',
                (version, feature_version))
            self.connection.execute('''
                DELETE FROM feature_snapshots WHERE version=? AND feature_version=?''',
                (version, feature_version))
        count = 0
        batch = []
        try:
            events = self.iter_canonical_events(version)
            first = next(events, None)
            if first is not None:
                from itertools import chain

                for snapshot in iter_feature_snapshots(
                        chain((first,), events), dataset_version=version,
                        coverage_start=first.event_time_utc):
                    values = {key: str(value) if hasattr(value, 'as_tuple') else value
                              for key, value in snapshot.feature_values.items()}
                    payload = json.dumps(values, sort_keys=True, separators=(',', ':'))
                    batch.append((version, feature_version, snapshot.transaction_id,
                                  snapshot.event_time.isoformat(), snapshot.as_of.isoformat(),
                                  snapshot.coverage_start.isoformat(), snapshot.coverage_state,
                                  int(snapshot.scoreable), snapshot.feature_input_digest,
                                  snapshot.created_at.isoformat(), payload))
                    count += 1
                    if len(batch) >= _BATCH_SIZE:
                        self._write_feature_batch(batch)
                        batch.clear()
            self._write_feature_batch(batch)
            if count != self.event_count(version):
                raise ValueError('feature_count_mismatch')
            with self.connection:
                self.connection.execute('''
                    UPDATE feature_builds SET status='complete',snapshot_count=?
                    WHERE version=? AND feature_version=? AND status='staged' ''',
                    (count, version, feature_version))
            return {'snapshot_count': count, 'repeated': False}
        except Exception:
            with self.connection:
                self.connection.execute('''
                    DELETE FROM feature_snapshots WHERE version=? AND feature_version=?''',
                    (version, feature_version))
                self.connection.execute('''
                    UPDATE feature_builds SET status='failed',snapshot_count=0
                    WHERE version=? AND feature_version=? AND status='staged' ''',
                    (version, feature_version))
            raise

    def _write_feature_batch(self, batch):
        if batch:
            with self.connection:
                self.connection.executemany('''
                    INSERT INTO feature_snapshots(
                        version,feature_version,transaction_id,event_time,as_of,
                        coverage_start,coverage_state,scoreable,feature_input_digest,
                        created_at,payload_json)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)''', batch)

    def iter_feature_snapshots(self, version: str, feature_version: str = 'history-v1'):
        """Return only published feature snapshots; preserve Decimal value types."""
        from decimal import Decimal

        from fraudlens.feature_history import HistoricalFeatureSnapshot

        if self.feature_snapshot_count(version, feature_version) is None:
            raise ValueError('feature_build_incomplete')
        cursor = self.connection.execute('''
            SELECT transaction_id,event_time,as_of,coverage_start,coverage_state,
                   scoreable,feature_input_digest,created_at,payload_json
            FROM feature_snapshots WHERE version=? AND feature_version=?
            ORDER BY event_time,transaction_id''', (version, feature_version))
        decimal_keys = {'sender_paid_sum_same_currency_24h',
                        'receiver_received_sum_same_currency_24h', 'current_paid_amount'}
        for (transaction_id, event_time, as_of, coverage_start, state,
             scoreable, digest, created_at, payload) in cursor:
            values = json.loads(payload)
            for key in decimal_keys:
                if values[key] is not None:
                    values[key] = Decimal(values[key])
            yield HistoricalFeatureSnapshot(
                transaction_id=transaction_id, dataset_version=version,
                feature_version=feature_version,
                event_time=datetime.fromisoformat(event_time),
                as_of=datetime.fromisoformat(as_of),
                coverage_start=datetime.fromisoformat(coverage_start),
                coverage_state=state, scoreable=bool(scoreable),
                feature_values=values, feature_input_digest=digest,
                created_at=datetime.fromisoformat(created_at))
