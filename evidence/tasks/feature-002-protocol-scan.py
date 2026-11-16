"""Recreate the Feature 002 split identity and label-only eligibility summary."""

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fraudlens.data_import import derive_dataset_version
from fraudlens.evaluation import (
    EvaluationProtocol,
    Partition,
    _LABEL_ROLES,
    _boundary,
    _feature_policy_hash,
    _manifest_digests,
)
from fraudlens.feature_history import feature_catalog

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = json.loads((ROOT / "evals/protocols/feature_002_v1.json").read_text())
SOURCE = ROOT / "data/raw/HI-Small_Trans.csv"
NAMESPACE = "kaggle:ealtman2019/ibm-transactions-for-anti-money-laundering-aml:v8"
MEMBER = "HI-Small_Trans.csv"


def _frame(value: str) -> bytes:
    raw = value.encode("utf-8")
    return len(raw).to_bytes(4, "big") + raw


def _source_rows():
    with SOURCE.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        header = next(reader)
        if len(header) != 11 or header[0] != "Timestamp" or header[10] != "Is Laundering":
            raise ValueError("source_header_mismatch")
        for ordinal, row in enumerate(reader, 1):
            if len(row) != 11:
                raise ValueError("source_row_width_mismatch")
            yield ordinal, row


def main() -> None:
    digest = hashlib.sha256()
    with SOURCE.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    source_sha = digest.hexdigest()
    if source_sha != PROTOCOL["dataset"]["source_sha256"]:
        raise ValueError("source_identity_mismatch")

    group_counts: Counter[datetime] = Counter()
    parsed_times: dict[str, datetime] = {}
    source_count = 0
    for _, row in _source_rows():
        event_time = parsed_times.get(row[0])
        if event_time is None:
            event_time = datetime.strptime(row[0], "%Y/%m/%d %H:%M").replace(
                tzinfo=timezone.utc
            )
            parsed_times[row[0]] = event_time
        group_counts[event_time] += 1
        source_count += 1

    start = min(group_counts)
    cutoff = start + timedelta(hours=24)
    scoreable_times = sorted(value for value in group_counts if value >= cutoff)
    scoreable_count = sum(group_counts[value] for value in scoreable_times)
    groups = [tuple([None] * group_counts[value]) for value in scoreable_times]
    train_end = _boundary(groups, 7, 10, scoreable_count, 0, len(groups) - 2)
    train_group = next(
        index
        for index in range(len(groups))
        if sum(len(group) for group in groups[: index + 1]) == train_end
    )
    validation_end = _boundary(
        groups, 17, 20, scoreable_count, train_group + 1, len(groups) - 1
    )
    role_by_time: dict[datetime, str] = {}
    cumulative = 0
    for event_time in scoreable_times:
        role_by_time[event_time] = (
            "train"
            if cumulative < train_end
            else "validation"
            if cumulative < validation_end
            else "test"
        )
        cumulative += group_counts[event_time]

    framed_prefix = (
        b"FraudLensAI/tx/v1\x00" + _frame(NAMESPACE) + _frame(MEMBER)
    )
    member_rows: dict[str, list[tuple[datetime, str]]] = {
        role: [] for role in ("train", "validation", "test")
    }
    label_counts = {role: Counter() for role in member_rows}
    warmup: list[tuple[datetime, str]] = []
    for ordinal, row in _source_rows():
        event_time = parsed_times[row[0]]
        tx_digest = hashlib.sha256(
            framed_prefix + ordinal.to_bytes(8, "big")
        ).digest()
        transaction_id = "D" + tx_digest[:16].hex()
        if event_time < cutoff:
            warmup.append((event_time, transaction_id))
            continue
        role = role_by_time[event_time]
        member_rows[role].append((event_time, transaction_id))
        label = row[10]
        label_counts[role][
            "eligible_positive"
            if label == "1"
            else "eligible_negative"
            if label == "0"
            else "ineligible"
        ] += 1

    partitions: dict[str, Partition] = {}
    for role, rows in member_rows.items():
        rows.sort()
        positives = label_counts[role]["eligible_positive"]
        negatives = label_counts[role]["eligible_negative"]
        eligible = positives + negatives
        partitions[role] = Partition(
            role,
            tuple(transaction_id for _, transaction_id in rows),
            rows[0][0] if rows else None,
            rows[-1][0] if rows else None,
            len(rows),
            eligible,
            label_counts[role]["ineligible"],
            positives,
            negatives,
            positives / eligible if eligible else None,
        )

    mapping_sha = PROTOCOL["dataset"]["mapping_sha256"]
    time_sha = PROTOCOL["dataset"]["time_policy_sha256"]
    dataset_version = derive_dataset_version(
        bytes.fromhex(source_sha), bytes.fromhex(mapping_sha), bytes.fromhex(time_sha)
    )
    split_policy = EvaluationProtocol(
        "feature-002-split-v1",
        "history-v1",
        _feature_policy_hash(frozenset(feature_catalog())),
        70,
        15,
        15,
        24,
        20,
        _LABEL_ROLES,
    )
    reasons = []
    for role, part in partitions.items():
        if not part.positives or not part.negatives:
            reasons.append(f"{role}_requires_both_classes")
        if role in {"validation", "test"} and part.positives < 20:
            reasons.append(f"{role}_requires_20_positives")
    membership_sha, manifest_protocol_sha = _manifest_digests(
        dataset_version,
        source_sha,
        mapping_sha,
        time_sha,
        split_policy,
        start,
        cutoff,
        partitions,
        tuple(transaction_id for _, transaction_id in sorted(warmup)),
        (),
        not reasons,
        tuple(reasons),
    )

    result = {
        "dataset_version": dataset_version,
        "source_records": source_count,
        "scoreable_count": scoreable_count,
        "warmup_excluded_count": len(warmup),
        "source_start": start.isoformat(),
        "warmup_cutoff": cutoff.isoformat(),
        "roles": {
            role: {
                "rows": part.event_valid_count,
                "first_event_time": part.first_event_time.isoformat(),
                "last_event_time": part.last_event_time.isoformat(),
                "label_eligible": part.label_eligible_count,
                "label_ineligible": part.label_ineligible_count,
                "positives": part.positives,
                "negatives": part.negatives,
                "prevalence": part.prevalence,
            }
            for role, part in partitions.items()
        },
        "membership_sha256": membership_sha,
        "manifest_protocol_sha256": manifest_protocol_sha,
        "eligible": not reasons,
        "ineligibility_reasons": reasons,
    }

    for key, expected in PROTOCOL["partition"]["roles"].items():
        if result["roles"][key] != {
            field: expected[field]
            for field in result["roles"][key]
        }:
            raise ValueError(f"partition_mismatch:{key}")
    expected_refs = {
        "dataset_version": PROTOCOL["dataset"]["dataset_version"],
        "source_records": PROTOCOL["dataset"]["source_records"],
        "source_start": PROTOCOL["partition"]["source_start"],
        "warmup_cutoff": PROTOCOL["partition"]["warmup_cutoff"],
        "scoreable_count": PROTOCOL["feature_snapshot"]["scoreable_count"],
        "warmup_excluded_count": PROTOCOL["feature_snapshot"]["warmup_excluded_count"],
        "membership_sha256": PROTOCOL["partition"]["membership_sha256"],
        "manifest_protocol_sha256": PROTOCOL["partition"]["manifest_protocol_sha256"],
        "eligible": PROTOCOL["partition"]["eligibility"]["eligible"],
        "ineligibility_reasons": PROTOCOL["partition"]["eligibility"]["ineligibility_reasons"],
    }
    for key, expected in expected_refs.items():
        if result[key] != expected:
            raise ValueError(f"protocol_reference_mismatch:{key}")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
