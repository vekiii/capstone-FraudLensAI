"""Validate frozen protocol structure, canonical hash inputs and provenance refs."""

import hashlib
import json
from pathlib import Path

from fraudlens.data_import import derive_dataset_version
from fraudlens.evaluation import _feature_policy_hash
from fraudlens.feature_history import feature_catalog
from fraudlens.rule_scoring import POLICY_SHA256

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_PATH = ROOT / "evals/protocols/feature_002_v1.json"


def main() -> None:
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    required = {
        "protocol_version", "status", "created_date", "canonical_serialization",
        "dataset", "feature_snapshot", "partition",
        "label_roles", "candidates", "preprocessing", "selection",
        "threshold_selection", "baseline", "reporting", "resource_budget",
        "reproducibility", "holdout", "reference_methodology",
    }
    if set(protocol) != required:
        raise ValueError("protocol_top_level_shape_mismatch")
    dataset = protocol["dataset"]
    source_sha = hashlib.sha256((ROOT / "data/raw/HI-Small_Trans.csv").read_bytes()).hexdigest()
    mapping_bytes = (ROOT / "data/mappings/ibm_hi_small_v1.json").read_bytes()
    mapping_sha = hashlib.sha256(mapping_bytes.replace(b"\r\n", b"\n")).hexdigest()
    mapping = json.loads(mapping_bytes)
    time_sha = hashlib.sha256(
        json.dumps(
            mapping["time"]["selected_policy"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()
    dataset_version = derive_dataset_version(
        bytes.fromhex(source_sha), bytes.fromhex(mapping_sha), bytes.fromhex(time_sha)
    )
    if (
        source_sha != dataset["source_sha256"]
        or mapping_sha != dataset["mapping_sha256"]
        or time_sha != dataset["time_policy_sha256"]
        or dataset_version != dataset["dataset_version"]
    ):
        raise ValueError("dataset_provenance_mismatch")
    if _feature_policy_hash(frozenset(feature_catalog())) != protocol["feature_snapshot"][
        "feature_policy_sha256"
    ]:
        raise ValueError("feature_policy_mismatch")
    if POLICY_SHA256 != protocol["baseline"]["policy_sha256"]:
        raise ValueError("baseline_policy_mismatch")

    partition = protocol["partition"]
    roles = partition["roles"]
    if tuple(roles) != ("train", "validation", "test"):
        raise ValueError("partition_role_order_mismatch")
    if sum(role["rows"] for role in roles.values()) != protocol["feature_snapshot"][
        "scoreable_count"
    ]:
        raise ValueError("partition_count_mismatch")
    if not partition["eligibility"]["eligible"] or partition["eligibility"][
        "ineligibility_reasons"
    ]:
        raise ValueError("benchmark_ineligible")
    if any(role["positives"] < 1 or role["negatives"] < 1 for role in roles.values()):
        raise ValueError("partition_class_coverage_mismatch")
    if roles["validation"]["positives"] < 20 or roles["test"]["positives"] < 20:
        raise ValueError("outer_positive_minimum_mismatch")
    if not (
        roles["train"]["last_event_time"] < roles["validation"]["first_event_time"]
        < roles["validation"]["last_event_time"] < roles["test"]["first_event_time"]
    ):
        raise ValueError("partition_chronology_mismatch")
    candidates = protocol["candidates"]["candidate_order_and_tie_rank"]
    if len(candidates) != protocol["candidates"]["fit_limit"] or len(candidates) != 6:
        raise ValueError("candidate_fit_budget_mismatch")
    if protocol["holdout"]["label_access_before_frozen_predictions"]:
        raise ValueError("holdout_policy_invalid")

    canonical = json.dumps(
        protocol, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    print(
        json.dumps(
            {
                "status": "valid",
                "canonical_sha256": hashlib.sha256(canonical).hexdigest(),
                "raw_file_sha256": hashlib.sha256(PROTOCOL_PATH.read_bytes()).hexdigest(),
                "dataset_version": dataset_version,
                "source_sha256": source_sha,
                "mapping_sha256": mapping_sha,
                "time_policy_sha256": time_sha,
                "feature_policy_sha256": protocol["feature_snapshot"][
                    "feature_policy_sha256"
                ],
                "baseline_policy_sha256": POLICY_SHA256,
                "split_membership_sha256": partition["membership_sha256"],
                "candidate_count": len(candidates),
                "eligible": partition["eligibility"]["eligible"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
