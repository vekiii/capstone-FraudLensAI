"""Authored independent scenario contract and canonical identity checks."""

import copy
import json

import pytest

from fraudlens.simulation.models import fingerprint, validate_pair
from fraudlens.simulation.scenarios import Catalog


def pair():
    s = dict(
        scenario_id="test",
        scenario_version=1,
        content_sha256="0" * 64,
        title="Test",
        source=dict(kind="bundled_synthetic", data_version="v1", time_basis="Authored UTC"),
        score_provenance=dict(
            source="fixture", score_kind="illustrative_score", scorer_version="v1"
        ),
        assumptions=[dict(id="w", description="weight"), dict(id="d", description="duration")],
        horizon=dict(starts_at="2026-01-01T00:00:00Z", ends_at="2026-01-01T01:00:00Z"),
        window_starts=["2026-01-01T00:00:00Z"],
        defaults=dict(score_threshold="0.3", budget_minutes_per_window=2),
        alerts=[
            dict(
                alert_id="A",
                available_at="2026-01-01T00:00:00Z",
                score="0.40",
                weight="1",
                estimated_review_minutes=2,
                weight_assumption_id="w",
                duration_assumption_id="d",
            )
        ],
    )
    return s, dict(
        scenario_id="test", scenario_version=1, outcomes=[dict(alert_id="A", outcome="positive")]
    )


@pytest.mark.parametrize(
    "path,value",
    [
        (("scenario_id",), "bad/id"),
        (("scenario_id",), "é"),
        (("scenario_id",), "x" * 81),
        (("scenario_id",), "valid\n"),
        (("scenario_version",), True),
        (("scenario_version",), 0),
        (("scenario_version",), 2**53),
        (("alerts", 0, "score"), 0.4),
        (("alerts", 0, "score"), "NaN"),
        (("alerts", 0, "score"), "1.01"),
        (("alerts", 0, "score"), "01"),
        (("alerts", 0, "score"), "1e-2"),
        (("alerts", 0, "score"), "-0.1"),
        (("alerts", 0, "score"), "0." + "1" * 127),
        (("alerts", 0, "weight"), "0"),
        (("alerts", 0, "weight"), 1),
        (("alerts", 0, "estimated_review_minutes"), True),
        (("alerts", 0, "estimated_review_minutes"), 1.0),
        (("alerts", 0, "estimated_review_minutes"), 0),
        (("alerts", 0, "weight_assumption_id"), "unknown"),
        (("alerts", 0, "alert_id"), "bad!"),
        (("alerts", 0, "available_at"), "2026-01-01T01:00:00Z"),
        (("alerts", 0, "available_at"), "2025-12-31T23:59:59Z"),
        (("alerts", 0, "available_at"), "2026-02-30T00:00:00Z"),
        (("alerts", 0, "available_at"), "2026-01-01T00:00:00+00:00"),
        (("alerts", 0, "available_at"), "2026-01-01T00:00:00.1234567Z"),
        (("horizon", "ends_at"), "2026-01-01T00:00:00Z"),
        (("window_starts",), []),
        (("window_starts",), ["2026-01-01T00:01:00Z"]),
        (("window_starts",), ["2026-01-01T00:00:00Z"] * 2),
        (("window_starts",), ["2026-01-01T00:00:00Z", "2026-01-01T01:00:00Z"]),
        (("window_starts",), [f"2026-01-01T00:{i:02d}:00Z" for i in range(13)]),
        (
            ("window_starts",),
            ["2026-01-01T00:00:00Z", "2026-01-01T00:02:00Z", "2026-01-01T00:01:00Z"],
        ),
        (("defaults", "score_threshold"), "2"),
        (("defaults", "budget_minutes_per_window"), -1),
        (("generation_seed",), True),
        (("generation_seed",), 2**53),
        (("source", "extra"), 1),
        (("score_provenance", "source"), "model"),
        (("extra",), 1),
        (("alerts", 0, "outcome"), "positive"),
    ],
)
def test_invalid_scenario(path, value):
    s, o = pair()
    target = s
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(ValueError):
        validate_pair(s, o)


@pytest.mark.parametrize(
    "mutation",
    [
        "alert_duplicate",
        "assumption_duplicate",
        "foreign",
        "outcome_duplicate",
        "wrong_id",
        "wrong_version",
        "outcome_extra",
        "bad_outcome",
        "251",
    ],
)
def test_cross_object_failures(mutation):
    s, o = pair()
    if mutation == "alert_duplicate":
        s["alerts"] *= 2
    elif mutation == "assumption_duplicate":
        s["assumptions"] *= 2
    elif mutation == "foreign":
        o["outcomes"][0]["alert_id"] = "foreign"
    elif mutation == "outcome_duplicate":
        o["outcomes"] *= 2
    elif mutation == "wrong_id":
        o["scenario_id"] = "other"
    elif mutation == "wrong_version":
        o["scenario_version"] = 2
    elif mutation == "outcome_extra":
        o["extra"] = 1
    elif mutation == "bad_outcome":
        o["outcomes"][0]["outcome"] = "unknown"
    else:
        s["alerts"] = [{**s["alerts"][0], "alert_id": str(i)} for i in range(251)]
    with pytest.raises(ValueError):
        validate_pair(s, o)


def test_valid_empty_partial_and_maximum():
    s, o = pair()
    s["alerts"] = [{**s["alerts"][0], "alert_id": str(i)} for i in range(250)]
    o["outcomes"] = []
    validate_pair(s, o)
    o["outcomes"] = [dict(alert_id="0", outcome="negative")]
    validate_pair(s, o)
    s["alerts"] = []
    o["outcomes"] = []
    validate_pair(s, o)


def test_canonical_equivalence_and_sensitivity():
    s, o = pair()
    old = fingerprint(s, o)
    s["content_sha256"] = "a" * 64
    s["alerts"][0]["score"] = "0.4000"
    s["alerts"][0]["available_at"] = "2026-01-01T00:00:00.000000Z"
    s["generation_seed"] = None
    s["assumptions"].reverse()
    assert fingerprint(s, o) == old
    o["outcomes"][0]["outcome"] = "negative"
    assert fingerprint(s, o) != old
    s, o = pair()
    s["title"] = "Changed"
    assert fingerprint(s, o) != old


def test_all_unordered_arrays_and_long_decimal_precision():
    s, o = pair()
    s["alerts"].append({**s["alerts"][0], "alert_id": "B"})
    o["outcomes"].append(dict(alert_id="B", outcome="negative"))
    s["alerts"][0]["weight"] = "1." + "0" * 100 + "1"
    old = fingerprint(s, o)
    s["alerts"].reverse()
    o["outcomes"].reverse()
    s["assumptions"].reverse()
    assert fingerprint(s, o) == old
    s["alerts"][1]["weight"] = "1." + "0" * 100 + "2"
    assert fingerprint(s, o) != old


def write_pair(root, stem, s, o):
    s = copy.deepcopy(s)
    s["content_sha256"] = fingerprint(s, o)
    (root / (stem + ".json")).write_text(json.dumps(s))
    (root / (stem + ".outcomes.json")).write_text(json.dumps(o))


def test_catalog_conflict_hash_isolation_and_trusted_paths(tmp_path):
    s, o = pair()
    write_pair(tmp_path, "one", s, o)
    catalog = Catalog(tmp_path)
    revision = catalog.resolve("test", 1)
    assert "outcomes" not in revision.facts.model_dump()
    assert "outcomes" not in revision.metadata()
    with pytest.raises(ValueError):
        catalog.resolve("../one", 1)
    s["title"] = "Conflicting"
    write_pair(tmp_path, "two", s, o)
    with pytest.raises(ValueError):
        Catalog(tmp_path)


def test_catalog_rejects_wrong_digest(tmp_path):
    s, o = pair()
    write_pair(tmp_path, "one", s, o)
    p = tmp_path / "one.json"
    data = json.loads(p.read_text())
    data["title"] = "tampered"
    p.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        Catalog(tmp_path)


def test_catalog_root_boundary_and_returned_copies(tmp_path):
    from fraudlens.simulation.scenarios import read

    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "private.json"
    outside.write_text("{}")
    with pytest.raises(ValueError):
        read(root / ".." / "private.json", root.resolve())
    s, o = pair()
    write_pair(root, "one", s, o)
    c = Catalog(root)
    rev = c.resolve("test", 1)
    rev.facts.alerts.clear()
    assert len(c.resolve("test", 1).facts.alerts) == 1
    private = c.resolve("test", 1).evaluation_outcomes()
    private.outcomes.clear()
    assert len(c.resolve("test", 1).evaluation_outcomes().outcomes) == 1
