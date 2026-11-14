"""Bounded-memory CSV reader for the exact IBM HI-Small transaction header."""

import csv
import hashlib
from array import array
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HEADERS = (
    "Timestamp", "From Bank", "Account", "To Bank", "Account",
    "Amount Received", "Receiving Currency", "Amount Paid", "Payment Currency",
    "Payment Format", "Is Laundering",
)


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_csv(path):
    """Read as strings before coding IDs; stable-sort by (timestamp, raw row)."""
    path = Path(path)
    raw = {
        "ts": array("q"), "sender": array("i"), "recv": array("i"),
        "from_bank": array("i"), "to_bank": array("i"),
        "amt_paid": array("d"), "cur_recv": array("h"), "cur_paid": array("h"),
        "fmt": array("h"), "label": array("b"),
    }
    codes = {name: {} for name in ("account", "bank", "currency", "format")}
    times = {}

    def code(kind, value):
        if not value:
            raise ValueError(f"blank {kind}")
        mapping = codes[kind]
        if value not in mapping:
            mapping[value] = len(mapping)
        return mapping[value]

    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        if tuple(next(reader, ())) != HEADERS:
            raise ValueError("CSV header does not match the IBM HI-Small schema")
        for ordinal, row in enumerate(reader):
            if len(row) != 11:
                raise ValueError(f"row {ordinal + 1} has {len(row)} columns")
            timestamp = row[0]
            if timestamp not in times:
                times[timestamp] = int(
                    datetime.strptime(timestamp, "%Y/%m/%d %H:%M")
                    .replace(tzinfo=timezone.utc).timestamp()
                )
            raw["ts"].append(times[timestamp])
            raw["from_bank"].append(code("bank", row[1]))
            raw["sender"].append(code("account", row[2]))
            raw["to_bank"].append(code("bank", row[3]))
            raw["recv"].append(code("account", row[4]))
            paid = float(row[7])
            if not np.isfinite(paid) or paid < 0:
                raise ValueError(f"invalid paid amount at row {ordinal + 1}")
            raw["amt_paid"].append(paid)
            raw["cur_recv"].append(code("currency", row[6]))
            raw["cur_paid"].append(code("currency", row[8]))
            raw["fmt"].append(code("format", row[9]))
            if row[10] not in ("0", "1"):
                raise ValueError(f"invalid label at row {ordinal + 1}")
            raw["label"].append(int(row[10]))
    values = {name: np.frombuffer(items, dtype={
        "q": np.int64, "i": np.int32, "d": np.float64,
        "h": np.int16, "b": np.int8,
    }[items.typecode]) for name, items in raw.items()}
    n = len(values["ts"])
    values["raw_index"] = np.arange(n, dtype=np.int32)
    order = np.argsort(values["ts"], kind="stable")
    sorted_values = {name: v[order] for name, v in values.items()}
    categories = {
        kind: list(mapping)
        for kind, mapping in codes.items()
    }
    return sorted_values, categories
