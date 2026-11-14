"""Offline, exploratory notebook training and evaluation."""

import json
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import sklearn
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, precision_recall_curve

from .core import BASIC, FEATURES, build_features, split_indices, subsample_train
from .io import load_csv, sha256_file

CATEGORICAL = ("cur_recv", "cur_paid", "fmt")
RETRO_WINDOWS = {"1h": 3600, "6h": 21600, "24h": 86400, "3d": 259200, "7d": 604800}
RETRO_LOWS = (1.0, 0.95, 0.8, 0.5, 0.2, 0.05, 0.01)


def best_threshold(y, scores):
    precision, recall, thresholds = precision_recall_curve(y, scores)
    if not len(thresholds):
        raise ValueError("validation predictions are empty")
    f1 = 2 * precision[:-1] * recall[:-1] / np.maximum(
        precision[:-1] + recall[:-1], 1e-12
    )
    return float(thresholds[int(np.argmax(f1))])


def classification_metrics(y, scores, threshold, flags=None):
    y = np.asarray(y, dtype=np.int8)
    flag = np.asarray(scores >= threshold if flags is None else flags, dtype=bool)
    tp = int(np.count_nonzero(flag & (y == 1)))
    fp = int(np.count_nonzero(flag & (y == 0)))
    fn = int(np.count_nonzero(~flag & (y == 1)))
    tn = int(np.count_nonzero(~flag & (y == 0)))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "f1": f1, "precision": precision, "recall": recall,
        "pr_auc": float(average_precision_score(y, scores)) if np.any(y) else None,
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
    }


def bootstrap_intervals(y, scores, threshold, samples=1000, seed=42, flags=None):
    """Ordinary row bootstrap, with AP computed from tied score groups."""
    if samples < 1000:
        raise ValueError("at least 1000 bootstrap resamples are required")
    y = np.asarray(y, dtype=np.int8)
    scores = np.asarray(scores)
    n = len(y)
    if n == 0 or not np.any(y):
        return {"f1": None, "pr_auc": None, "reason": "no positive test rows"}
    flag = scores >= threshold if flags is None else np.asarray(flags, dtype=bool)
    order = np.argsort(-scores, kind="stable")
    ranked = scores[order]
    starts = np.r_[0, np.flatnonzero(ranked[1:] != ranked[:-1]) + 1]
    rng = np.random.default_rng(seed)
    f1_values = np.empty(samples)
    ap_values = np.empty(samples)
    for i in range(samples):
        weights = np.bincount(rng.integers(0, n, size=n), minlength=n)
        positives = weights * y
        tp = int(positives[flag].sum())
        predicted = int(weights[flag].sum())
        total_pos = int(positives.sum())
        f1_values[i] = 2 * tp / (predicted + total_pos) if predicted + total_pos else 0
        if not total_pos:
            ap_values[i] = np.nan
            continue
        group_total = np.add.reduceat(weights[order], starts)
        group_pos = np.add.reduceat(positives[order], starts)
        cum_total = np.cumsum(group_total)
        cum_pos = np.cumsum(group_pos)
        precision = cum_pos / np.maximum(cum_total, 1)
        ap_values[i] = np.sum(precision * group_pos) / total_pos
    return {
        "f1": np.quantile(f1_values, [0.025, 0.975]).tolist(),
        "pr_auc": np.nanquantile(ap_values, [0.025, 0.975]).tolist(),
        "resamples": samples,
        "method": "ordinary transaction-row bootstrap; fixed model and threshold",
    }


def retro_flag(ts, sender, recv, scores, threshold, window, low):
    """Delayed alerts: a later alert may flag an earlier transaction."""
    ts = np.asarray(ts, dtype=np.int64)
    sender = np.asarray(sender, dtype=np.int64)
    recv = np.asarray(recv, dtype=np.int64)
    flagged = np.asarray(scores) >= threshold
    if not np.any(flagged):
        return flagged
    secs = ts - ts.min()
    span = int(secs.max()) + window + 1
    event_keys = np.sort(np.r_[sender[flagged] * span + secs[flagged],
                               recv[flagged] * span + secs[flagged]])
    gap = np.full(len(ts), np.inf)
    for accounts in (sender, recv):
        pos = np.searchsorted(event_keys, accounts * span + secs + 1, side="left")
        exists = pos < len(event_keys)
        following = event_keys[np.minimum(pos, len(event_keys) - 1)]
        gap = np.minimum(gap, np.where(
            exists & (following // span == accounts),
            following - accounts * span - secs, np.inf,
        ))
    return flagged | ((gap <= window) & (np.asarray(scores) >= low))


def tune_retro(data, val_idx, labels, val_scores, threshold):
    best = (-1.0, None, None)
    y = labels[val_idx]
    total_positive = int(np.count_nonzero(y))
    for name, window in RETRO_WINDOWS.items():
        for low in RETRO_LOWS:
            flags = retro_flag(
                data["ts"][val_idx], data["sender"][val_idx], data["recv"][val_idx],
                val_scores, threshold, window, low,
            )
            tp = int(np.count_nonzero(flags & (y == 1)))
            score = 2 * tp / (int(np.count_nonzero(flags)) + total_positive)
            if score > best[0]:
                best = (score, name, low)
    return {"validation_f1": best[0], "window": best[1], "low_score": best[2]}


def _split_report(data, idx):
    labels = data["label"][idx]
    return {
        "rows": int(len(idx)), "positives": int(labels.sum()),
        "positive_rate": float(labels.mean()) if len(idx) else None,
        "first_ts": int(data["ts"][idx[0]]) if len(idx) else None,
        "last_ts": int(data["ts"][idx[-1]]) if len(idx) else None,
        "first_raw_index": int(data["raw_index"][idx[0]]) if len(idx) else None,
        "last_raw_index": int(data["raw_index"][idx[-1]]) if len(idx) else None,
    }


def run_experiment(csv_path, output_root, train_frac=1.0, split_mode="temporal",
                   retro=False, bootstrap=1000, seeds=(0, 1, 2)):
    if bootstrap < 1000:
        raise ValueError("bootstrap must be at least 1000")
    if split_mode == "stratified":
        warnings.warn(
            "DEV ONLY: stratified group split leaks time; results are NOT comparable "
            "to the temporal protocol", stacklevel=2,
        )
    stages = {}
    began = time.perf_counter()
    data, categories = load_csv(csv_path)
    stages["load_seconds"] = time.perf_counter() - began
    began = time.perf_counter()
    features = build_features(data)
    stages["features_seconds"] = time.perf_counter() - began
    train_full, val, test = split_indices(data, split_mode)
    train = subsample_train(train_full, data["label"], train_frac, seed=42)
    full_rate = float(data["label"][train_full].mean())
    sampled_rate = float(data["label"][train].mean())
    if full_rate and abs(sampled_rate / full_rate - 1) > 0.05:
        raise AssertionError("train class ratio changed by over 5%")
    for name, idx in (("train_full", train_full), ("train_used", train),
                      ("validation", val), ("test", test)):
        row = _split_report(data, idx)
        print(f"{name}: rows={row['rows']}, positives={row['positives']}, "
              f"positive_rate={row['positive_rate']:.6%}", flush=True)
    if any(np.unique(data["label"][idx]).size != 2 for idx in (train, val, test)):
        raise ValueError("each split must contain both labels")
    started_at = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    input_sha = sha256_file(csv_path)
    run_id = f"trees-{started_at}-{input_sha[:8]}"
    run_dir = Path(output_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    manifest = {
        "run_id": run_id, "status": "exploratory_not_application_model",
        "source_csv_sha256": input_sha, "source_csv_name": Path(csv_path).name,
        "split_mode": split_mode, "train_frac": train_frac,
        "features": list(FEATURES), "basic_features": list(BASIC),
        "categorical_mapping": categories,
        "split_boundaries": {
            name: _split_report(data, idx)
            for name, idx in (("train_full", train_full), ("train_used", train),
                              ("validation", val), ("test", test))
        },
        "seeds": list(seeds), "bootstrap_resamples": bootstrap,
        "versions": {
            "sklearn": sklearn.__version__, "numpy": np.__version__,
            "pandas": None,
        },
        "tie_policy": "stable timestamp sort; earlier raw rows at same timestamp count as history",
        "model": "HistGradientBoostingClassifier(max_iter=300,class_weight=balanced,"
                 "early_stopping=True,validation_fraction=0.1)",
        "variants": {}, "stage_seconds": stages,
    }
    labels = data["label"]
    for variant, names in (("basic", BASIC), ("history", FEATURES)):
        began = time.perf_counter()
        matrix = np.column_stack([features[name] for name in names])
        per_seed = []
        for seed in seeds:
            model = HistGradientBoostingClassifier(
                max_iter=300, class_weight="balanced",
                categorical_features=[names.index(n) for n in CATEGORICAL],
                early_stopping=True, validation_fraction=0.1, random_state=seed,
            )
            model.fit(matrix[train], labels[train])
            validation_scores = model.predict_proba(matrix[val])[:, 1]
            threshold = best_threshold(labels[val], validation_scores)
            test_scores = model.predict_proba(matrix[test])[:, 1]
            measured = classification_metrics(labels[test], test_scores, threshold)
            measured["bootstrap_95_ci"] = bootstrap_intervals(
                labels[test], test_scores, threshold, bootstrap, seed=seed + 42,
            )
            entry = {"seed": seed, "threshold": threshold, "test": measured}
            if retro and variant == "history":
                settings = tune_retro(data, val, labels, validation_scores, threshold)
                flags = retro_flag(
                    data["ts"][test], data["sender"][test], data["recv"][test],
                    test_scores, threshold, RETRO_WINDOWS[settings["window"]],
                    settings["low_score"],
                )
                delayed = classification_metrics(labels[test], test_scores, threshold, flags)
                # Delayed alerts are binary decisions, not a new ranking score.
                delayed["pr_auc"] = None
                delayed["bootstrap_95_ci"] = bootstrap_intervals(
                    labels[test], test_scores, threshold, bootstrap, seed=seed + 142,
                    flags=flags,
                )
                delayed["bootstrap_95_ci"]["pr_auc"] = None
                entry["delayed_alerts_not_real_time"] = {"settings": settings, "test": delayed}
            filename = "model.joblib" if variant == "history" and seed == seeds[0] else (
                f"model_{variant}_seed{seed}.joblib"
            )
            joblib.dump(model, run_dir / filename)
            entry["model_file"] = filename
            entry["model_sha256"] = sha256_file(run_dir / filename)
            per_seed.append(entry)
            print(f"{variant} seed {seed}: F1={measured['f1']:.4f}, "
                  f"AP={measured['pr_auc']:.4f}", flush=True)
        summary = {name: float(np.mean([r["test"][name] for r in per_seed]))
                   for name in ("f1", "precision", "recall", "pr_auc")}
        manifest["variants"][variant] = {"features": list(names),
                                           "per_seed": per_seed, "mean": summary}
        stages[f"{variant}_fit_evaluate_seconds"] = time.perf_counter() - began
        del matrix
    manifest["stage_seconds"] = stages
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (run_dir / "scoring.py").write_text(
        "from pathlib import Path\n"
        "from ibm_aml_trees.score import load_scorer\n"
        "score = load_scorer(Path(__file__).parent)\n", encoding="utf-8"
    )
    return run_dir, manifest
