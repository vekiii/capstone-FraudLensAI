"""Offline authored controls: these are software checks, not model evaluation."""

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from fraudlens.investigation import judging_v4 as v4

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "evals/investigation/report-quality-v4"


def controls():
    inputs = json.loads((PACK / "inputs/controls.json").read_text(encoding="utf-8"))
    private = json.loads((PACK / "reference/expectations.json").read_text(encoding="utf-8"))
    authored = json.loads((PACK / "reference/authored-ratings.json").read_text(encoding="utf-8"))
    packets = [v4.project_packet(p) for p in inputs]
    ratings = {}
    for p, r in zip(packets, authored, strict=True):
        r["packet_id"] = p["packet_id"]
        ratings[("calibration", p["scenario_id"])] = r
    return dict(packets=packets, ratings=ratings, expectations=private)


def batch():
    c = controls()
    source = c["packets"][0]
    rating = next(iter(c["ratings"].values()))
    packets, ratings = [], {}
    order = [f"H{i}" for i in range(1, 9)]
    for i, identity in enumerate(order):
        for role in ["primary", "secondary"] if i in (1, 2, 3, 5, 7) else ["primary"]:
            p = copy.deepcopy(source)
            p.update(scenario_id=identity, role=role)
            p = v4.project_packet(p)
            r = copy.deepcopy(rating)
            r["packet_id"] = p["packet_id"]
            packets.append(p)
            ratings[(role, identity)] = r
    return packets, ratings, order, c


def test_authored_six_controls_and_critical_disclaimer():
    c = controls()
    assert v4.assess_calibration(**c)["passed"] is True
    for p in c["packets"]:
        r = v4.validate_rating(p, c["ratings"][("calibration", p["scenario_id"])])
        assert r["missingness_correct"] is (p["scenario_id"] in {"C1", "C5"})
    assert c["ratings"][("calibration", "C3")]["critical_error"] is True


def test_projection_never_includes_private_expected_states():
    p = controls()["packets"][0]
    original = p["packet_id"]
    p.update(reference={"expected_missing_fields": ["GOLD_CANARY"]}, reviewer_notes="GOLD_CANARY")
    p["units"][0]["expected"] = "GOLD_CANARY"
    p["evidence"][0]["private_label"] = "GOLD_CANARY"
    clean = v4.project_packet(p)
    assert "GOLD_CANARY" not in json.dumps(clean)
    assert clean["packet_id"] == original
    assert clean["assessment_fields"] == list(v4.ASSESSMENT_FIELDS)


@pytest.mark.parametrize(
    "mutation", ["packet", "extra", "duplicate", "foreign", "quote", "pointer", "version"]
)
def test_reject_unbound_or_legacy_ratings(mutation):
    c = controls()
    p = c["packets"][2]
    r = c["ratings"][("calibration", "C3")]
    if mutation == "packet":
        r["packet_id"] = "0" * 64
    elif mutation == "extra":
        r["missingness_correct"] = True
    elif mutation == "duplicate":
        r["units"].append(r["units"][0])
    elif mutation == "foreign":
        r["contradictions"][0]["evidence_ref"] = "foreign"
    elif mutation == "quote":
        r["contradictions"][0]["claim_quote"] = "Invented quotation"
    elif mutation == "pointer":
        r["checks"][v4.CHECKS[1]]["report_locations"] = ["/does-not-exist"]
    else:
        r["rating_version"] = 3
    with pytest.raises(ValueError):
        v4.validate_rating(p, r)


def test_absent_support_is_not_necessarily_contradiction():
    c = controls()
    p, r = c["packets"][2], c["ratings"][("calibration", "C3")]
    p["evidence"][0]["text"] = "Amount: 1250.00 EUR. No information on origin."
    p = v4.project_packet(p)
    r["packet_id"] = p["packet_id"]
    r["checks"][v4.CHECKS[2]]["passed"] = True
    r["contradictions"] = []
    assert v4.validate_rating(p, r)["missingness_correct"] is False


def test_false_contradiction_requires_witness():
    c = controls()
    p, r = c["packets"][2], c["ratings"][("calibration", "C3")]
    r["contradictions"] = []
    with pytest.raises(ValueError):
        v4.validate_rating(p, r)


def test_valid_batch_and_paired_review_binding():
    p, r, order, c = batch()
    result = v4.aggregate(p, r, order, c)
    assert result["quality_pass"] is True
    assert result["passing_reports"] == 8
    assert result["original_ratings"][0]["rating"]["rating_version"] == 4
    p[-1]["report"]["summary"] = "Different report"
    p[-1] = v4.project_packet(p[-1])
    with pytest.raises(ValueError, match="Paired"):
        v4.aggregate(p, r, order, c)


@pytest.mark.parametrize(
    "defect", ["disclosure", "procedure", "uncertain", "additional", "zero", "missing_rating"]
)
def test_report_fail_boundaries(defect):
    p, r, order, c = batch()
    value = r[("primary", "H1")]
    if defect == "disclosure":
        value["checks"][v4.CHECKS[0]]["passed"] = False
    elif defect in ("procedure", "uncertain"):
        p[0]["units"].append(
            dict(
                unit_id="p1",
                claim_kind="procedure",
                text="Check identity",
                location="/summary",
                evidence_refs=["ev1"],
            )
        )
        p[0] = v4.project_packet(p[0])
        value["packet_id"] = p[0]["packet_id"]
        value["units"].append(
            dict(
                unit_id="p1",
                judgment="unsupported" if defect == "procedure" else "uncertain",
                reason="No procedure supports this",
                critical_error=False,
            )
        )
    elif defect == "additional":
        value["additional_issues"] = ["Unsupported recommendation outside listed units"]
    elif defect == "zero":
        p[0]["units"] = [u for u in p[0]["units"] if u["claim_kind"] != "observation"]
        p[0] = v4.project_packet(p[0])
        value["packet_id"] = p[0]["packet_id"]
        value["units"] = [u for u in value["units"] if u["unit_id"] != "o1"]
    else:
        del r[("primary", "H1")]
    result = v4.aggregate(p, r, order, c)
    assert result["reports"][0]["passed"] is False
    assert result["report_count"] == 8
    assert result["passing_reports"] == 7


def test_failed_calibration_cannot_be_overridden_by_favorable_reports():
    p, r, order, c = batch()
    c["ratings"][("calibration", "C3")]["checks"][v4.CHECKS[1]]["passed"] = True
    result = v4.aggregate(p, r, order, c)
    assert result["quality_assessment_valid"] is False
    assert result["quality_pass"] is None
    assert result["passing_reports"] is None
    assert len(result["original_ratings"]) == 13


def test_predicate_disagreement_preserved_even_same_conjunction():
    p, r, order, c = batch()
    a, b = r[("primary", "H2")], r[("secondary", "H2")]
    a["checks"][v4.CHECKS[0]]["passed"] = False
    b["checks"][v4.CHECKS[0]]["passed"] = False
    b["checks"][v4.CHECKS[1]].update(
        passed=False, fields=["source_of_funds"], report_locations=["/summary"]
    )
    result = v4.aggregate(p, r, order, c)
    assert any(d.get("predicate") == v4.CHECKS[1] for d in result["disagreements"])
    assert result["reports"][1]["passed"] is False


@pytest.mark.parametrize("defect", ["missing", "duplicate", "wrong", "extra_rating"])
def test_calibration_fixed_six_no_dropping(defect):
    c = controls()
    if defect == "missing":
        c["expectations"].pop()
    elif defect == "duplicate":
        c["packets"].append(c["packets"][0])
    elif defect == "wrong":
        c["ratings"][("calibration", "C4")]["units"][0]["judgment"] = "uncertain"
    else:
        c["ratings"][("calibration", "FOREIGN")] = {}
    assert v4.assess_calibration(**c)["passed"] is False


def test_secondary_critical_cannot_disappear_when_primary_rating_missing():
    p, r, order, c = batch()
    del r[("primary", "H2")]
    r[("secondary", "H2")]["critical_error"] = True
    result = v4.aggregate(p, r, order, c)
    assert result["passing_reports"] == 7
    assert result["reports"][1]["critical_error"] is True
    assert result["quality_pass"] is False


def test_missing_secondary_is_failed_review_and_two_failures_fail_pack():
    p, r, order, c = batch()
    del r[("secondary", "H2")]
    del r[("primary", "H1")]
    result = v4.aggregate(p, r, order, c)
    assert result["passing_reports"] == 6
    assert result["quality_pass"] is False
    assert result["reports"][1]["review_incomplete"] is True


@pytest.mark.parametrize(
    "defect", ["failed", "unit_critical", "report_critical", "additional", "disclosure"]
)
def test_calibration_checks_every_frozen_flag(defect):
    c = controls()
    r = c["ratings"][("calibration", "C1")]
    if defect == "failed":
        c["packets"][0]["failed"] = True
        c["packets"][0] = v4.project_packet(c["packets"][0])
        r["packet_id"] = c["packets"][0]["packet_id"]
    elif defect == "unit_critical":
        r["units"][0]["critical_error"] = True
    elif defect == "report_critical":
        r["critical_error"] = True
    elif defect == "additional":
        r["additional_issues"] = ["Unexpected issue"]
    else:
        r["checks"][v4.CHECKS[0]]["passed"] = False
    assert v4.assess_calibration(**c)["passed"] is False


def test_cli_offline_and_exclusive_output(tmp_path, monkeypatch, capsys):
    p, r, order, c = batch()
    c["ratings"] = v4.legacy.ratings_to_list(c["ratings"])
    envelope = dict(
        packets=p, ratings=v4.legacy.ratings_to_list(r), scenario_order=order, calibration=c
    )
    source, output = tmp_path / "input.json", tmp_path / "output.json"
    source.write_text(json.dumps(envelope), encoding="utf-8")
    monkeypatch.setattr(
        sys, "argv", ["judging_v4", "--input", str(source), "--output", str(output)]
    )
    v4.main()
    assert json.loads(output.read_text())["quality_pass"] is True
    original = output.read_bytes()
    with pytest.raises(FileExistsError):
        v4.main()
    assert output.read_bytes() == original
    assert '"quality_pass": true' in capsys.readouterr().out


def test_frozen_control_verifier_and_tampering(tmp_path):
    import shutil

    result = v4.verify_controls(PACK)
    assert result["software_controls_pass"] is True
    assert result["model_quality_evaluated"] is False
    copied = tmp_path / "pack"
    shutil.copytree(PACK, copied)
    with (copied / "inputs/controls.json").open("a", encoding="utf-8") as stream:
        stream.write(" ")
    with pytest.raises(ValueError, match="hash"):
        v4.verify_controls(copied)


def test_no_provider_import_in_offline_process():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; from fraudlens.investigation import judging_v4; assert 'openai' not in sys.modules",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "PYTHONPATH": str(ROOT / "backend/src")},
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("supported,present,passes", [(9, 4, True), (8, 4, False), (9, 3, False)])
def test_unchanged_support_and_coverage_boundaries(supported, present, passes):
    p, r, order, c = batch()
    units, judgments = [], []
    for kind, count, good_count, good, bad in [
        ("observation", 10, supported, "supported", "unsupported"),
        ("essential_fact", 5, present, "present", "missing"),
    ]:
        for i in range(count):
            identity = f"{kind}-{i}"
            units.append(
                dict(
                    unit_id=identity,
                    claim_kind=kind,
                    text="Atomic fixture fact",
                    location="/summary",
                    evidence_refs=["ev1"],
                )
            )
            judgments.append(
                dict(
                    unit_id=identity,
                    judgment=good if i < good_count else bad,
                    reason="Authored boundary",
                    critical_error=False,
                )
            )
    p[0]["units"] = units
    p[0] = v4.project_packet(p[0])
    r[("primary", "H1")].update(packet_id=p[0]["packet_id"], units=judgments)
    result = v4.aggregate(p, r, order, c)
    assert result["reports"][0]["passed"] is passes
    assert result["reports"][0]["support_rate"] == supported / 10
    assert result["reports"][0]["essential_coverage"] == present / 5


def test_generation_failure_retained_in_eight_slots():
    p, r, order, c = batch()
    p[0]["failed"] = True
    p[0] = v4.project_packet(p[0])
    del r[("primary", "H1")]
    result = v4.aggregate(p, r, order, c)
    assert result["report_count"] == 8
    assert result["failed_reports"] == 1
    assert result["passing_reports"] == 7
    assert result["reports"][0]["failed"] is True


def test_schema_valid_check_reasons_survive_legacy_math_bridge():
    c = controls()
    packet = c["packets"][0]
    rating = c["ratings"][("calibration", "C1")]
    for check in rating["checks"].values():
        check["reason"] = "Grounded explanation. " * 150
    assert v4.validate_rating(packet, rating)["missingness_correct"] is True
