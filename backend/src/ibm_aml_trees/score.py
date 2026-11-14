"""Offline score function for a trusted local experiment run."""

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np

from .core import FEATURES, build_features
from .io import sha256_file


def _records(frame):
    if hasattr(frame, "to_dict"):
        return frame.to_dict("records")
    return list(frame)


def load_scorer(run_dir):
    """Return score(df_history, df_new) -> model probabilities.

    ``run_dir`` must be a locally generated, trusted run. Joblib is executable
    serialization; never point this at a downloaded or user-uploaded artifact.
    """
    run_dir = Path(run_dir)
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    if tuple(manifest["features"]) != FEATURES:
        raise ValueError("feature order mismatch")
    first = manifest["variants"]["history"]["per_seed"][0]
    model_path = run_dir / first["model_file"]
    if model_path.name != "model.joblib" or sha256_file(model_path) != first["model_sha256"]:
        raise ValueError("model hash or filename mismatch")
    model = joblib.load(model_path)
    category_map = {
        name: {value: i for i, value in enumerate(values)}
        for name, values in manifest["categorical_mapping"].items()
    }

    def score(df_history, df_new):
        history = _records(df_history)
        new = _records(df_new)
        if not new:
            return np.empty(0, dtype=np.float64)
        rows = history + new
        account_map = {}
        bank_map = {}

        def code(mapping, value):
            value = str(value)
            if value not in mapping:
                mapping[value] = len(mapping)
            return mapping[value]

        def time_value(value):
            if isinstance(value, str):
                return int(datetime.strptime(value, "%Y/%m/%d %H:%M")
                           .replace(tzinfo=timezone.utc).timestamp())
            if hasattr(value, "timestamp"):
                return int(value.timestamp())
            return int(value)

        data = {
            "ts": np.array([time_value(row["ts"]) for row in rows], dtype=np.int64),
            "sender": np.array([code(account_map, row["from_acct"]) for row in rows]),
            "recv": np.array([code(account_map, row["to_acct"]) for row in rows]),
            "from_bank": np.array([code(bank_map, row["from_bank"]) for row in rows]),
            "to_bank": np.array([code(bank_map, row["to_bank"]) for row in rows]),
            "amt_paid": np.array([float(row["amt_paid"]) for row in rows]),
            "cur_recv": np.array([category_map["currency"].get(str(row["cur_recv"]), -1)
                                  for row in rows]),
            "cur_paid": np.array([category_map["currency"].get(str(row["cur_paid"]), -1)
                                  for row in rows]),
            "fmt": np.array([category_map["format"].get(str(row["fmt"]), -1)
                             for row in rows]),
            "label": np.zeros(len(rows), dtype=np.int8),
            "raw_index": np.arange(len(rows)),
        }
        order = np.argsort(data["ts"], kind="stable")
        sorted_data = {key: value[order] for key, value in data.items()}
        features = build_features(sorted_data)
        features["cross_cur"] = np.array([
            rows[i]["cur_recv"] != rows[i]["cur_paid"] for i in order
        ], dtype=np.float32)
        selected = np.flatnonzero(sorted_data["raw_index"] >= len(history))
        matrix = np.column_stack([features[name][selected] for name in FEATURES])
        probabilities = model.predict_proba(matrix)[:, 1]
        return probabilities[np.argsort(sorted_data["raw_index"][selected])]

    return score
