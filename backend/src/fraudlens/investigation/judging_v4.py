"""Version-four OFFLINE rubric. No runtime imports, provider calls or old regrading.

The custodian supplies source-derived units, immutable packet assignments and private
calibration expectations. Binding checks cannot prove semantic truth; a calibrated
judge must still examine every atomic claim and all unenumerated prose.
"""

import argparse
import copy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from fraudlens.investigation import judging as legacy

CHECKS = (
    "required_disclosures_complete",
    "missing_values_not_invented",
    "no_cross_section_contradictions",
)
ASSESSMENT_FIELDS = (
    "transaction_id",
    "amount",
    "currency",
    "event_time",
    "score_meaning",
    "source_of_funds",
    "identity",
    "occupation",
    "device",
    "history",
    "human_authority",
)
SECTIONS = (
    "summary",
    "observations",
    "missing_information",
    "limitations",
    "recommended_checks",
    "alternative_explanations",
)
POLICY = (
    "Preserve exact source facts and score meaning; disclose unknowns and source limits. "
    "Synthetic labels are not findings; humans decide dispositions. "
    "Never invent customer facts, guilt or current legal duties. "
    "Enumerate every atomic recommendation; record unenumerated unsupported prose as "
    "additional_issues. No unknown-data disclaimer cancels an invented assertion."
)


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode()
    ).hexdigest()


def obj(properties):
    return dict(
        type="object", additionalProperties=False, required=list(properties), properties=properties
    )


TEXT = dict(type="string", minLength=1, maxLength=10000, pattern=r"\S")
STRINGS = dict(type="array", maxItems=100, uniqueItems=True, items=TEXT)
CHECK_SCHEMA = obj(
    dict(
        passed=dict(type="boolean"),
        reason=TEXT,
        report_locations=STRINGS,
        evidence_refs=STRINGS,
        fields=dict(
            type="array",
            uniqueItems=True,
            maxItems=len(ASSESSMENT_FIELDS),
            items=dict(enum=list(ASSESSMENT_FIELDS)),
        ),
    )
)
WITNESS_SCHEMA = obj(
    dict(
        claim_location=TEXT,
        claim_quote=TEXT,
        counter_location=dict(type=["string", "null"]),
        evidence_ref=dict(type=["string", "null"]),
        counter_quote=TEXT,
    )
)
RATING_SCHEMA = obj(
    dict(
        rating_version=dict(type="integer", const=4),
        packet_id=dict(type="string", pattern="^[a-f0-9]{64}$"),
        units=legacy.RATING_SCHEMA["properties"]["units"],
        checks=obj({k: CHECK_SCHEMA for k in CHECKS}),
        critical_error=dict(type="boolean"),
        additional_issues=legacy.RATING_SCHEMA["properties"]["additional_issues"],
        contradictions=dict(type="array", maxItems=50, items=WITNESS_SCHEMA),
    )
)


def pointer(report, location):
    """Resolve report-only RFC6901 pointers, rejecting malformed escapes/indexes."""
    if not isinstance(location, str) or not location.startswith("/"):
        raise ValueError("Invalid report pointer")
    node = report
    for part in location[1:].split("/"):
        for i, char in enumerate(part):
            if char == "~" and (i + 1 == len(part) or part[i + 1] not in "01"):
                raise ValueError("Invalid pointer escape")
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            raise ValueError("Unknown report pointer")
        node = node[part]
    if not isinstance(node, str):
        raise ValueError("Pointer does not identify report text")
    return node


def project_packet(raw):
    """Allowlist projection: never copy reference, private outcomes or peer reviews.

    Input is an offline materialized envelope, NOT a runtime InvestigationView.
    Source prose must already be selected by the authorized evidence custodian.
    """
    if raw["role"] not in ("primary", "secondary", "calibration"):
        raise ValueError("Invalid role")
    if type(raw["failed"]) is not bool:
        raise ValueError("Invalid generation status")
    report = {k: raw["report"].get(k, "") for k in SECTIONS}
    if any(not isinstance(v, str) for v in report.values()):
        raise ValueError("Materialize textual report sections first")
    evidence = [dict(evidence_id=e["evidence_id"], text=e["text"]) for e in raw["evidence"]]
    if len({e["evidence_id"] for e in evidence}) != len(evidence) or any(
        not isinstance(e[k], str) or not e[k].strip()
        for e in evidence
        for k in ("evidence_id", "text")
    ):
        raise ValueError("Invalid evidence inventory")
    units = [
        {
            k: copy.deepcopy(u[k])
            for k in ("unit_id", "claim_kind", "text", "location", "evidence_refs")
        }
        for u in raw["units"]
    ]
    ids = {u["unit_id"] for u in units}
    authorized = {e["evidence_id"] for e in evidence}
    if len(ids) != len(units) or len(units) > 100:
        raise ValueError("Duplicate or oversized unit set")
    for u in units:
        if (
            u["claim_kind"] not in ("observation", "procedure", "essential_fact")
            or any(not isinstance(u[k], str) or not u[k].strip() for k in ("unit_id", "text"))
            or not isinstance(u["evidence_refs"], list)
            or any(ref not in authorized for ref in u["evidence_refs"])
        ):
            raise ValueError("Invalid unit")
        if u["location"]:
            pointer(report, u["location"])
        elif u["claim_kind"] != "essential_fact":
            raise ValueError("Report claim requires location")
    if not isinstance(raw["scenario_id"], str) or not raw["scenario_id"].strip():
        raise ValueError("Invalid scenario")
    result = dict(
        packet_version=4,
        scenario_id=raw["scenario_id"],
        role=raw["role"],
        failed=raw["failed"],
        report=report,
        evidence=evidence,
        units=units,
        assessment_fields=list(ASSESSMENT_FIELDS),
        disclosure_policy=POLICY,
    )
    result["packet_id"] = digest(result)
    return result


def validate_rating(packet, value):
    try:
        if project_packet(packet) != packet:
            raise ValueError("Packet changed or contains private fields")
        Draft202012Validator(RATING_SCHEMA).validate(value)
        if value["packet_id"] != packet["packet_id"]:
            raise ValueError("Rating packet mismatch")
        refs = {e["evidence_id"]: e["text"] for e in packet["evidence"]}
        for check in value["checks"].values():
            for location in check["report_locations"]:
                pointer(packet["report"], location)
            if any(ref not in refs for ref in check["evidence_refs"]):
                raise ValueError("Foreign check evidence")
        invention = value["checks"][CHECKS[1]]
        if not invention["passed"] and (
            not invention["report_locations"] or not invention["fields"]
        ):
            raise ValueError("Invented value needs field and report attribution")
        contradictions = value["contradictions"]
        if value["checks"][CHECKS[2]]["passed"] == bool(contradictions):
            raise ValueError("Contradiction flag/witness mismatch")
        for witness in contradictions:
            if witness["claim_quote"] not in pointer(packet["report"], witness["claim_location"]):
                raise ValueError("Altered claim quotation")
            location, ref = witness["counter_location"], witness["evidence_ref"]
            if (location is None) == (ref is None):
                raise ValueError("Exactly one conflicting source required")
            if location is not None:
                if location == witness["claim_location"]:
                    raise ValueError("Distinct contradiction location required")
                counter = pointer(packet["report"], location)
            else:
                if ref not in refs:
                    raise ValueError("Foreign contradiction evidence")
                counter = refs[ref]
            if witness["counter_quote"] not in counter:
                raise ValueError("Altered counter quotation")
        normalized = dict(
            units=copy.deepcopy(value["units"]),
            missingness_correct=all(value["checks"][k]["passed"] for k in CHECKS),
            # The legacy calculation only consumes the Boolean. Full v4 reasons
            # stay in original_ratings, without its old 2000-character limit.
            missingness_reason="Derived v4 predicate conjunction; full reasons retained in v4 originals.",
            critical_error=value["critical_error"],
            additional_issues=value["additional_issues"],
        )
        return legacy.validate_rating(packet, normalized)
    except Exception as exc:
        raise ValueError("Invalid v4 rating") from exc


def assess_calibration(packets, ratings, expectations):
    """Exact six controls. Malformed/missing/extra rows remain failures, not dropped."""
    wanted = {f"C{i}" for i in range(1, 7)}
    cases = []
    complete = False
    try:
        by_id = {p["scenario_id"]: p for p in packets}
        exp = {e["scenario_id"]: e for e in expectations}
        complete = (
            len(packets) == len(expectations) == 6
            and set(by_id) == set(exp) == wanted
            and all(p["role"] == "calibration" for p in packets)
            and set(ratings) == {("calibration", i) for i in wanted}
        )
        for identity in sorted(wanted):
            matched = False
            try:
                packet, expected, value = (
                    by_id[identity],
                    exp[identity],
                    ratings[("calibration", identity)],
                )
                clean = validate_rating(packet, value)
                actual_units = {
                    u["unit_id"]: {k: u[k] for k in ("judgment", "critical_error")}
                    for u in clean["units"]
                }
                matched = (
                    actual_units == expected["units"]
                    and value["critical_error"] is expected["critical_error"]
                    and {k: value["checks"][k]["passed"] for k in CHECKS} == expected["checks"]
                    and expected["no_additional_issues"] is True
                    and not value["additional_issues"]
                )
            except ValueError, KeyError, TypeError:
                pass
            cases.append(dict(scenario_id=identity, matched=matched))
    except ValueError, KeyError, TypeError:
        cases = [dict(scenario_id=i, matched=False) for i in sorted(wanted)]
    return dict(
        passed=complete and len(cases) == 6 and all(c["matched"] for c in cases),
        cases=cases,
        denominator=6,
    )


def aggregate(packets, ratings, scenario_order, calibration):
    """Offline eight primary + same preselected five secondary, exact frozen order.

    Recompute calibration from actual supplied outputs, never accept a caller's
    Boolean assertion of success. Missing/invalid judge outputs fail their slots.
    """
    if len(scenario_order) != 8 or len(set(scenario_order)) != 8:
        raise ValueError("Exactly eight predeclared scenarios required")
    subset = {scenario_order[i] for i in (1, 2, 3, 5, 7)}
    expected_keys = {("primary", i) for i in scenario_order} | {("secondary", i) for i in subset}
    by_key = {(p["role"], p["scenario_id"]): p for p in packets}
    if (
        len(by_key) != len(packets)
        or set(by_key) != expected_keys
        or not set(ratings) <= expected_keys
    ):
        raise ValueError("Incomplete, duplicate or foreign packet assignments")
    for identity in subset:
        a, b = (by_key[(role, identity)] for role in ("primary", "secondary"))
        if any(a[k] != b[k] for k in ("report", "units", "evidence", "failed")):
            raise ValueError("Paired reviewers must assess the same report/evidence")
    normalized, prepared, invalid = {}, [], []
    for key, packet in by_key.items():
        if project_packet(packet) != packet:
            raise ValueError("Invalid public packet")
        p = copy.deepcopy(packet)
        if not p["failed"]:
            try:
                normalized[key] = validate_rating(p, ratings[key])
            except ValueError, KeyError:
                p["failed"] = True
                invalid.append(
                    dict(role=key[0], scenario_id=key[1], error="missing_or_invalid_rating")
                )
        prepared.append(p)
    # Legacy deterministic math is reused without changing its schema or old results.
    result = legacy.aggregate(prepared, normalized)
    by_report = {r["id"]: r for r in result["reports"]}
    # A missing primary rating must never hide critical flags found by its peer.
    for (_, identity), value in normalized.items():
        if value["critical_error"] or any(u["critical_error"] for u in value["units"]):
            by_report[identity]["critical_error"] = True
            by_report[identity]["passed"] = False
    for identity in subset:
        keys = [("primary", identity), ("secondary", identity)]
        if any(k not in normalized for k in keys):
            by_report[identity]["passed"] = False
            by_report[identity]["review_incomplete"] = True
            continue
        for check in CHECKS:
            originals = [ratings[k]["checks"][check] for k in keys]
            if originals[0]["passed"] != originals[1]["passed"]:
                result["disagreements"].append(
                    dict(
                        id=identity,
                        predicate=check,
                        originals=copy.deepcopy(originals),
                        unresolved=True,
                    )
                )
                by_report[identity]["passed"] = False
    gate = assess_calibration(**calibration)
    passing = sum(r["passed"] for r in result["reports"])
    result.update(
        rubric_version=4,
        calibration=gate,
        quality_assessment_valid=gate["passed"],
        passing_reports=passing if gate["passed"] else None,
        quality_pass=(passing >= 7 and not any(r.get("critical_error") for r in result["reports"]))
        if gate["passed"]
        else None,
        original_ratings=copy.deepcopy(legacy.ratings_to_list(ratings)),
        invalid_ratings=invalid,
        limitations="Software binding is not semantic truth; authored fixtures are not model evaluation.",
    )
    # Do not expose an uncalibrated per-report pass as a validated quality judgment.
    if not gate["passed"]:
        for report in result["reports"]:
            report["unvalidated_raw_pass"] = report.pop("passed")
            report["passed"] = None
    return result


def ratings_map(rows):
    result = {}
    for row in rows:
        key = (row["role"], row["scenario_id"])
        if key in result:
            raise ValueError("Duplicate rating row")
        result[key] = row["rating"]
    return result


def file_digest(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def verify_controls(root):
    """Verify committed artifacts and authored software controls, not model scores."""
    root = Path(root).resolve()
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    for relative, expected in manifest["files_sha256_lf"].items():
        path = (root / relative).resolve()
        if not path.is_relative_to(root) or file_digest(path) != expected:
            raise ValueError("Control artifact hash mismatch")
    repo = Path(__file__).resolve().parents[4]
    if (
        file_digest(repo / "prompts/evaluation/report-judge-v4.md") != manifest["prompt_sha256_lf"]
        or file_digest(__file__) != manifest["implementation_sha256_lf"]
    ):
        raise ValueError("Prompt/implementation hash mismatch")
    if json.loads((root / "rating-schema.json").read_text(encoding="utf-8")) != RATING_SCHEMA:
        raise ValueError("Schema drift")
    inputs = json.loads((root / "inputs/controls.json").read_text(encoding="utf-8"))
    expectations = json.loads((root / "reference/expectations.json").read_text(encoding="utf-8"))
    authored = json.loads((root / "reference/authored-ratings.json").read_text(encoding="utf-8"))
    packets = [project_packet(p) for p in inputs]
    ratings = {}
    for packet, value in zip(packets, authored, strict=True):
        value["packet_id"] = packet["packet_id"]
        ratings[("calibration", packet["scenario_id"])] = value
    result = assess_calibration(packets, ratings, expectations)
    return dict(
        software_controls_pass=result["passed"],
        model_quality_evaluated=False,
        calibration=result,
        artifact_bundle_sha256=digest(manifest),
    )


def main():
    parser = argparse.ArgumentParser(description="Offline v4 grading; no network or generation")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--verify-controls", type=Path, help="Verify authored software fixtures only")
    mode.add_argument(
        "--input",
        type=Path,
        help="Frozen envelope with packets, ratings, scenario_order, calibration",
    )
    parser.add_argument("--output", type=Path, help="New output file; never overwrite")
    args = parser.parse_args()
    if args.verify_controls:
        if args.output:
            parser.error("Control verification prints results; no quality output file")
        result = verify_controls(args.verify_controls)
        print(json.dumps(result))
        if not result["software_controls_pass"]:
            raise SystemExit(1)
        return
    if not args.output:
        parser.error("--input requires --output")
    envelope = json.loads(args.input.read_text(encoding="utf-8"))
    calibration = copy.deepcopy(envelope["calibration"])
    calibration["ratings"] = ratings_map(calibration["ratings"])
    result = aggregate(
        envelope["packets"],
        ratings_map(envelope["ratings"]),
        envelope["scenario_order"],
        calibration,
    )
    # Exclusive create preserves every previous result, including failed runs.
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
    print(
        json.dumps(
            dict(
                quality_assessment_valid=result["quality_assessment_valid"],
                quality_pass=result["quality_pass"],
            )
        )
    )


if __name__ == "__main__":
    main()
