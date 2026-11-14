"""Behavior checks for the isolated notebook reproduction."""

import json

import joblib
import numpy as np
import pytest

from ibm_aml_trees.core import (
    BASIC,
    FEATURES,
    build_features,
    split_indices,
    subsample_train,
)
from ibm_aml_trees.experiment import bootstrap_intervals, run_experiment
from ibm_aml_trees.io import HEADERS, load_csv
from ibm_aml_trees.score import load_scorer


def tiny():
    # Sorted order, including two same-minute rows and a self-transfer.
    return {
        "ts": np.array([0, 0, 1800, 3600, 90000], dtype=np.int64),
        "raw_index": np.arange(5),
        "sender": np.array([1, 1, 1, 2, 1]),
        "recv": np.array([1, 2, 2, 1, 2]),
        "from_bank": np.array([10, 10, 10, 20, 10]),
        "to_bank": np.array([10, 20, 20, 10, 20]),
        "amt_paid": np.array([10., 20., 30., 40., 50.]),
        "cur_recv": np.zeros(5, dtype=np.int16),
        "cur_paid": np.zeros(5, dtype=np.int16),
        "fmt": np.zeros(5, dtype=np.int16),
        "label": np.array([0, 1, 0, 0, 1], dtype=np.int8),
    }


def test_exact_feature_order_and_hand_computed_history():
    data = tiny()
    f = build_features(data)
    assert len(FEATURES) == 29 and len(BASIC) == 9
    assert f["self_xfer"].tolist() == [1, 0, 0, 0, 0]
    assert f["pair_prev_cnt"].tolist() == [0, 0, 1, 0, 2]
    assert f["sender_prev_cnt"].tolist() == [0, 1, 2, 0, 3]
    assert f["sender_prev_partners"].tolist() == [0, 1, 2, 0, 2]
    assert f["sender_tx_1h"].tolist() == [0, 1, 2, 0, 0]
    assert f["sender_new_ben_24h"].tolist() == [0, 1, 2, 0, 0]
    assert f["recv_tx_1h"].tolist() == [0, 0, 1, 1, 0]
    assert f["hrs_since_last_pair"][2] == 0.5
    assert np.isnan(f["hrs_since_last_pair"][1])


def test_future_deletion_and_label_mutation_do_not_change_earlier_features():
    data = tiny()
    full = build_features(data)
    partial = build_features({k: v[:4] for k, v in data.items()})
    changed = dict(data)
    changed["label"] = 1 - data["label"]
    changed_features = build_features(changed)
    for name in FEATURES:
        np.testing.assert_allclose(full[name][:4], partial[name], equal_nan=True)
        np.testing.assert_allclose(full[name], changed_features[name], equal_nan=True)
    assert "label" not in FEATURES


def test_temporal_split_keeps_ties_and_no_time_overlap():
    data = tiny()
    tr, va, te = split_indices(data, "temporal")
    assert len(np.concatenate((tr, va, te))) == len(data["ts"])
    assert data["ts"][tr].max() < data["ts"][va].min()
    assert data["ts"][va].max() < data["ts"][te].min()


def test_sampling_preserves_ratio_and_leaves_outer_splits_and_features_untouched():
    data = tiny()
    n = 10_000
    data = {k: np.resize(v, n) for k, v in data.items()}
    data["ts"] = np.arange(n, dtype=np.int64) * 60
    data["raw_index"] = np.arange(n)
    data["label"] = (np.arange(n) % 10 == 0).astype(np.int8)
    f = build_features(data)
    tr, va, te = split_indices(data, "temporal")
    sampled = subsample_train(tr, data["label"], 0.25, seed=42)
    original_rate = data["label"][tr].mean()
    assert abs(data["label"][sampled].mean() / original_rate - 1) <= 0.05
    assert len(sampled) < len(tr)
    assert len(va) == 2000 and len(te) == 2000
    for name in FEATURES:
        np.testing.assert_allclose(f[name][sampled], build_features(data)[name][sampled], equal_nan=True)


def test_invalid_fraction_rejected():
    with pytest.raises(ValueError):
        subsample_train(np.arange(3), np.zeros(3, dtype=np.int8), 0, 42)


def test_dev_group_split_keeps_sender_groups_disjoint():
    data = tiny()
    data = {key: np.resize(value, 100) for key, value in data.items()}
    data["sender"] = np.repeat(np.arange(20), 5)
    data["label"] = (data["sender"] % 2).astype(np.int8)
    train, validation, test = split_indices(data, "stratified")
    assert len(np.r_[train, validation, test]) == 100
    assert not (set(data["sender"][train]) & set(data["sender"][validation]))
    assert not (set(data["sender"][train]) & set(data["sender"][test]))
    assert not (set(data["sender"][validation]) & set(data["sender"][test]))


def test_csv_stable_sort_keeps_original_order_and_bank_zeroes(tmp_path):
    path = tmp_path / "tiny.csv"
    path.write_text(
        ",".join(HEADERS) + "\n"
        "2022/09/01 00:20,010,A,010,A,1,US Dollar,1,US Dollar,ACH,0\n"
        "2022/09/01 00:00,001,A,010,B,2,US Dollar,2,US Dollar,ACH,1\n"
        "2022/09/01 00:20,010,A,001,B,3,US Dollar,3,US Dollar,ACH,0\n",
        encoding="utf-8",
    )
    data, cats = load_csv(path)
    assert data["raw_index"].tolist() == [1, 0, 2]
    assert cats["bank"] == ["010", "001"]
    assert data["sender"][0] == data["sender"][1]


def test_bootstrap_intervals_cover_fixed_metric_shape():
    y = np.array([0, 1, 0, 1, 0, 1], dtype=np.int8)
    scores = np.array([0.1, 0.9, 0.2, 0.8, 0.3, 0.7])
    ci = bootstrap_intervals(y, scores, 0.5, samples=1000, seed=7)
    assert ci["f1"][1] == 1.0
    assert ci["pr_auc"][1] == 1.0
    assert ci["resamples"] == 1000


def test_manifest_model_reload_and_score_round_trip(tmp_path):
    path = tmp_path / "train.csv"
    rows = []
    for i in range(1000):
        minute = i // 2
        row = {
            "ts": f"2022/09/01 {minute // 60:02d}:{minute % 60:02d}",
            "from_bank": "010" if i % 2 else "001", "from_acct": f"A{i % 17}",
            "to_bank": "001", "to_acct": f"B{i % 23}",
            "amt_paid": str(i % 71 + 1), "cur_recv": "US Dollar",
            "cur_paid": "US Dollar", "fmt": "ACH",
        }
        rows.append(row)
    path.write_text(
        ",".join(HEADERS) + "\n" + "".join(
            f"{r['ts']},{r['from_bank']},{r['from_acct']},{r['to_bank']},"
            f"{r['to_acct']},{r['amt_paid']},{r['cur_recv']},{r['amt_paid']},"
            f"{r['cur_paid']},{r['fmt']},{int(i % 13 == 0)}\n"
            for i, r in enumerate(rows)
        ), encoding="utf-8",
    )
    run_dir, manifest = run_experiment(path, tmp_path / "artifacts", seeds=(0,), retro=True)
    round_trip = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert round_trip == manifest
    assert round_trip["variants"]["history"]["per_seed"][0][
        "delayed_alerts_not_real_time"
    ]["test"]["pr_auc"] is None
    score = load_scorer(run_dir)
    probability = score(rows[:801], rows[801:802])
    assert probability.shape == (1,)
    assert np.isfinite(probability[0]) and 0 <= probability[0] <= 1
    assert probability[0] == score(rows[:801], rows[801:802])[0]
    original, _ = load_csv(path)
    full_features = build_features(original)
    original_matrix = np.column_stack([full_features[name][801:802] for name in FEATURES])
    reloaded = joblib.load(run_dir / "model.joblib")
    np.testing.assert_allclose(probability, reloaded.predict_proba(original_matrix)[:, 1])
