"""Vectorized history and split functions for the notebook experiment.

All features use stable (timestamp, raw row) order. Same-minute earlier rows may
contribute, as in the reference notebook. This is an exploratory protocol and
does not implement FraudLens's ``history-v1`` timestamp-peer contract.
"""

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

BASIC = (
    "hour", "dow", "log_amt_paid", "cur_recv", "cur_paid", "fmt",
    "cross_cur", "cross_bank", "self_xfer",
)
HISTORY = (
    "is_first_pair", "pair_prev_cnt", "pair_age_days", "hrs_since_last_pair",
    "sender_prev_cnt", "sender_age_days", "hrs_since_last_sender_tx",
    "sender_prev_partners", "recv_prev_cnt", "recv_age_days", "new_ben_share_24h",
    "sender_tx_1h", "sender_new_ben_1h", "recv_tx_1h",
    "sender_tx_24h", "sender_new_ben_24h", "recv_tx_24h",
    "sender_tx_7d", "sender_new_ben_7d", "recv_tx_7d",
)
FEATURES = BASIC + HISTORY


def build_features(data):
    """Return 29 label-free float32 arrays in notebook order."""
    ts = np.asarray(data["ts"], dtype=np.int64)
    s = np.asarray(data["sender"], dtype=np.int64)
    r = np.asarray(data["recv"], dtype=np.int64)
    if len(ts) == 0:
        return {name: np.empty(0, dtype=np.float32) for name in FEATURES}
    if np.any(ts[1:] < ts[:-1]):
        raise ValueError("transactions must be sorted by timestamp")
    # Account codes are shared by sender and receiver, including self-transfers.
    base = max(int(s.max()), int(r.max())) + 1
    pair = _group_history(s * base + r, ts)
    first = (pair["cnt"] == 0).astype(np.int64)
    sender = _group_history(s, ts, first)
    recv = _group_history(r, ts)
    out = {
        "hour": (ts // 3600) % 24,
        "dow": (ts // 86400 + 3) % 7,
        "log_amt_paid": np.log1p(data["amt_paid"]),
        "cur_recv": data["cur_recv"],
        "cur_paid": data["cur_paid"],
        "fmt": data["fmt"],
        "cross_cur": data["cur_recv"] != data["cur_paid"],
        "cross_bank": data["from_bank"] != data["to_bank"],
        "self_xfer": s == r,
        "is_first_pair": first,
        "pair_prev_cnt": pair["cnt"],
        "pair_age_days": pair["age"] / 86400,
        "hrs_since_last_pair": pair["gap"] / 3600,
        "sender_prev_cnt": sender["cnt"],
        "sender_age_days": sender["age"] / 86400,
        "hrs_since_last_sender_tx": sender["gap"] / 3600,
        "sender_prev_partners": sender["flag_before"],
        "recv_prev_cnt": recv["cnt"],
        "recv_age_days": recv["age"] / 86400,
    }
    secs = ts - ts.min()
    ones = np.ones(len(ts), dtype=np.int64)
    for code, prefix, flags in (
        (s, "sender", {"tx": ones, "new_ben": first}),
        (r, "recv", {"tx": ones}),
    ):
        counts = _window_counts(code, secs, flags)
        for (kind, window), values in counts.items():
            name = f"{prefix}_{kind}_{window}"
            out[name] = values
    out["new_ben_share_24h"] = out["sender_new_ben_24h"] / np.maximum(
        out["sender_tx_24h"], 1
    )
    return {name: np.asarray(out[name], dtype=np.float32) for name in FEATURES}


def _group_history(code, ts, flag=None):
    order = np.argsort(code, kind="stable")
    ordered = code[order]
    starts = np.r_[0, np.flatnonzero(ordered[1:] != ordered[:-1]) + 1]
    start = starts[np.searchsorted(starts, np.arange(len(code)), side="right") - 1]
    pos = np.arange(len(code)) - start
    ordered_ts = ts[order]
    gap = (ordered_ts - np.r_[ordered_ts[:1], ordered_ts[:-1]]).astype(np.float64)
    gap[pos == 0] = np.nan
    result = {
        "cnt": _scatter(order, pos),
        "age": _scatter(order, ordered_ts - ordered_ts[start]),
        "gap": _scatter(order, gap),
    }
    if flag is not None:
        ordered_flag = flag[order]
        cumulative = np.cumsum(ordered_flag)
        result["flag_before"] = _scatter(
            order, cumulative - (cumulative[start] - ordered_flag[start]) - ordered_flag
        )
    return result


def _scatter(order, values):
    result = np.empty_like(values)
    result[order] = values
    return result


def _window_counts(group, secs, flags):
    # The offset keeps different groups in disjoint key ranges; prefix[idx]
    # excludes the current row and includes earlier rows at the same second.
    order = np.lexsort((secs, group))
    ordered_group = group[order]
    span = int(secs.max() - secs.min()) + 604800 + 1
    key = ordered_group * span + secs[order]
    if key.min() < 0 or key.max() < 0:
        raise OverflowError("window key overflow")
    prefix = {name: np.r_[0, np.cumsum(values[order])] for name, values in flags.items()}
    idx = np.arange(len(group))
    result = {}
    for name, seconds in (("1h", 3600), ("24h", 86400), ("7d", 604800)):
        left = np.searchsorted(key, key - seconds, side="left")
        for flag_name, sums in prefix.items():
            result[(flag_name, name)] = _scatter(order, sums[idx] - sums[left])
    return result


def split_indices(data, mode):
    n = len(data["ts"])
    if n < 3:
        raise ValueError("at least three rows are required")
    if mode == "stratified":
        labels = np.asarray(data["label"])
        groups = np.asarray(data["sender"])
        folds = list(StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42).split(
            np.zeros(n), labels, groups
        ))
        held = [test for _, test in folds]
        train = np.sort(np.concatenate(held[:3]))
        return train, np.sort(held[3]), np.sort(held[4])
    if mode != "temporal":
        raise ValueError(f"unknown split mode: {mode}")
    ts = np.asarray(data["ts"])
    if np.any(ts[1:] < ts[:-1]):
        raise ValueError("temporal split requires sorted timestamps")
    boundaries = np.flatnonzero(ts[1:] != ts[:-1]) + 1
    if len(boundaries) < 2:
        raise ValueError("at least three distinct timestamps are required")
    first = min(boundaries[:-1], key=lambda b: (abs(b - 0.6 * n), b))
    second = min((b for b in boundaries if b > first), key=lambda b: (abs(b - 0.8 * n), b))
    return np.arange(first), np.arange(first, second), np.arange(second, n)


def subsample_train(indices, labels, fraction, seed):
    if not 0 < fraction <= 1:
        raise ValueError("train fraction must be in (0, 1]")
    indices = np.asarray(indices)
    if fraction == 1:
        return indices.copy()
    positives = indices[np.asarray(labels)[indices] == 1]
    negatives = indices[np.asarray(labels)[indices] == 0]
    effective = max(fraction, min(1.0, 500 / len(positives))) if len(positives) else fraction
    rng = np.random.default_rng(seed)
    sampled = np.sort(np.r_[
        rng.choice(positives, round(effective * len(positives)), replace=False),
        rng.choice(negatives, round(effective * len(negatives)), replace=False),
    ])
    old_rate = len(positives) / max(len(indices), 1)
    new_rate = np.count_nonzero(np.asarray(labels)[sampled]) / max(len(sampled), 1)
    if old_rate and abs(new_rate / old_rate - 1) > 0.05:
        return indices.copy()
    return sampled
