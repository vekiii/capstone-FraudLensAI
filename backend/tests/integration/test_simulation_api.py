"""Future simulation routes through the real factory, never test-only routes."""

import copy
import json

import pytest
from fastapi.testclient import TestClient

from fraudlens.main import create_app
from fraudlens.simulation.models import fingerprint
from fraudlens.simulation.scenarios import Catalog


def recipe():
    facts = Catalog().resolve("review-capacity-demo", 1).facts
    return dict(
        contract_version=1,
        scenario=dict(
            scenario_id=facts.scenario_id, scenario_version=1, content_sha256=facts.content_sha256
        ),
        score_threshold="0.30",
        budget_minutes_per_window=2,
        strategy_versions=dict(fifo=1, highest_score=1, weighted_score_per_minute=1),
    )


@pytest.fixture
def client():
    with TestClient(create_app(), raise_server_exceptions=False) as c:
        yield c


def test_catalog_metadata_and_no_private_facts(client):
    response = client.get("/api/simulation/scenarios")
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"contract_version", "items"} and body["contract_version"] == 1
    item = body["items"][0]
    assert item == Catalog().resolve("review-capacity-demo", 1).metadata()
    assert "alerts" not in item and "outcomes" not in item


def test_catalog_sorting_with_trusted_test_catalog(tmp_path):
    facts = Catalog().resolve("review-capacity-demo", 1).facts.model_dump()
    # Future dependency seam: app.state.simulation_catalog is trusted app config.
    for i, (identity, version) in enumerate([("z", 1), ("a", 2), ("a", 1)]):
        s = {**facts, "scenario_id": identity, "scenario_version": version}
        o = dict(scenario_id=identity, scenario_version=version, outcomes=[])
        s["content_sha256"] = fingerprint(s, o)
        (tmp_path / f"{i}.json").write_text(json.dumps(s))
        (tmp_path / f"{i}.outcomes.json").write_text(json.dumps(o))
    app = create_app()
    app.state.simulation_catalog = Catalog(tmp_path)
    with TestClient(app) as c:
        response = c.get("/api/simulation/scenarios")
    assert response.status_code == 200
    assert [(i["scenario_id"], i["scenario_version"]) for i in response.json()["items"]] == [
        ("a", 1),
        ("a", 2),
        ("z", 1),
    ]


def test_default_comparison_closed_shape_order_counts_and_canonical_echo(client):
    response = client.post("/api/simulation/comparisons", json=recipe())
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"contract_version", "recipe", "scenario", "admitted_alerts", "strategies"}
    expected = recipe()
    expected["score_threshold"] = "0.3"
    assert body["contract_version"] == 1 and body["recipe"] == expected
    assert body["scenario"] == Catalog().resolve("review-capacity-demo", 1).metadata()
    assert [a["alert_id"] for a in body["admitted_alerts"]] == ["A", "B", "C", "E"]
    for a in body["admitted_alerts"]:
        assert set(a) == {
            "alert_id",
            "available_at",
            "score",
            "weight",
            "estimated_review_minutes",
            "weight_assumption_id",
            "duration_assumption_id",
        }
    strategies = body["strategies"]
    assert [s["strategy_id"] for s in strategies] == [
        "fifo",
        "highest_score",
        "weighted_score_per_minute",
    ]
    for row, reviewed, pending, found, mt, mb, negatives in zip(
        strategies,
        [["A"], ["B"], ["C", "E"]],
        [["B", "C", "E"], ["A", "C", "E"], ["A", "B"]],
        [0, 1, 1],
        [1, 1, 1],
        [2, 1, 1],
        [1, 0, 1],
    ):
        assert set(row) == {"strategy_id", "windows", "pending_alert_ids", "counts"}
        assert row["pending_alert_ids"] == pending
        assert row["windows"][0]["reviewed_alert_ids"] == reviewed
        assert row["windows"][0]["used_minutes"] == 2
        assert len(row["windows"]) == 1
        assert set(row["windows"][0]) == {
            "starts_at",
            "ranked_alert_ids",
            "reviewed_alert_ids",
            "used_minutes",
        }
        assert (
            row["windows"][0]["ranked_alert_ids"]
            == {
                "fifo": ["A", "B", "C", "E"],
                "highest_score": ["B", "C", "E", "A"],
                "weighted_score_per_minute": ["C", "E", "B", "A"],
            }[row["strategy_id"]]
        )
        assert row["counts"] == dict(
            reviewed=len(reviewed),
            backlog=len(pending),
            unknown_in_horizon=0,
            unknown_reviewed=0,
            outcomes=dict(
                positives_found=found,
                positives_missed=mt + mb,
                positives_missed_threshold=mt,
                positives_missed_backlog=mb,
                reviewed_negatives=negatives,
            ),
        )
    assert_no_private_labels(body)


def assert_no_private_labels(value):
    if isinstance(value, dict):
        assert not set(value) & {"outcome", "label", "is_laundering", "positive", "negative"}
        for child in value.values():
            assert_no_private_labels(child)
    elif isinstance(value, list):
        for child in value:
            assert_no_private_labels(child)


@pytest.mark.parametrize(
    "path,value",
    [
        (("contract_version",), 2),
        (("contract_version",), True),
        (("extra",), 1),
        (("scenario", "path"), "private.json"),
        (("scenario", "scenario_version"), True),
        (("scenario", "content_sha256"), "not-hash"),
        (("score_threshold",), 0.3),
        (("score_threshold",), "NaN"),
        (("budget_minutes_per_window",), True),
        (("budget_minutes_per_window",), -1),
        (("budget_minutes_per_window",), 1.5),
        (("strategy_versions", "extra"), 1),
        (("alerts",), []),
        (("labels",), []),
    ],
)
def test_bad_payload_is_422(client, path, value):
    body = recipe()
    target = body
    for k in path[:-1]:
        target = target[k]
    target[path[-1]] = value
    response = client.post("/api/simulation/comparisons", json=body)
    assert response.status_code == 422
    assert response.json() == {"error": {"code": "invalid_request", "message": "Invalid request."}}


def test_missing_field_and_malformed_json_are_422(client):
    body = recipe()
    del body["scenario"]
    for kwargs in [
        dict(json=body),
        dict(content="{broken", headers={"content-type": "application/json"}),
    ]:
        assert client.post("/api/simulation/comparisons", **kwargs).status_code == 422


@pytest.mark.parametrize(
    "change", ["unknown_id", "wrong_digest", "wrong_revision", "strategy_version"]
)
def test_unavailable_version_is_safe_409(client, change):
    body = recipe()
    if change == "unknown_id":
        body["scenario"]["scenario_id"] = "missing"
    elif change == "wrong_digest":
        body["scenario"]["content_sha256"] = "0" * 64
    elif change == "wrong_revision":
        body["scenario"]["scenario_version"] = 999
    else:
        body["strategy_versions"]["fifo"] = 999
    response = client.post("/api/simulation/comparisons", json=body)
    assert response.status_code == 409
    assert set(response.json()) == {"error"}
    assert response.json()["error"]["code"] == "simulation_version_unavailable"


def test_service_failure_is_sanitized_without_partial_comparison(client, monkeypatch):
    def fail(self):
        raise RuntimeError("PRIVATE C:/private/outcomes.json positive secret traceback")

    monkeypatch.setattr(Catalog, "metadata", fail)
    response = client.get("/api/simulation/scenarios")
    assert response.status_code == 500
    assert response.json() == {
        "error": {"code": "internal_error", "message": "Internal server error."}
    }
    assert "PRIVATE" not in response.text and "strategies" not in response.text


def test_simulation_does_not_mutate_cases(client):
    before = copy.deepcopy(client.get("/api/cases").json())
    detail = client.get("/api/cases/CASE-001").json()
    response = client.post("/api/simulation/comparisons", json=recipe())
    assert client.get("/api/cases").json() == before
    assert client.get("/api/cases/CASE-001").json() == detail
    assert response.status_code == 200


def test_original_case_errors_remain_unchanged(client):
    assert client.get("/api/cases/CASE-999").status_code == 404
    assert client.get("/api/cases/CASE-1").status_code == 422


def test_comparison_service_failure_is_sanitized(client, monkeypatch):
    body = recipe()

    def fail(self, *args):
        raise RuntimeError("PRIVATE C:/private/outcomes.json positive traceback")

    monkeypatch.setattr(Catalog, "resolve", fail)
    response = client.post("/api/simulation/comparisons", json=body)
    assert response.status_code == 500
    assert response.json() == {
        "error": {"code": "internal_error", "message": "Internal server error."}
    }


@pytest.fixture
def two_window_replay(tmp_path):
    def prepare(coverage="partial"):
        facts = Catalog().resolve("review-capacity-demo", 1).facts.model_dump()
        start = "2026-01-01T00:00:00Z"
        second_start = "2026-01-01T00:30:00Z"
        template = facts["alerts"][0]
        facts.update(
            scenario_id="two-window-demo",
            horizon=dict(starts_at=start, ends_at="2026-01-01T01:00:00Z"),
            window_starts=[start, second_start],
            alerts=[
                {
                    **template,
                    "alert_id": alert_id,
                    "available_at": available_at,
                    "score": score,
                    "estimated_review_minutes": minutes,
                }
                for alert_id, available_at, score, minutes in [
                    ("A", start, "0.9", 3),
                    ("B", start, "0.8", 1),
                    ("C", "2026-01-01T00:15:00Z", "0.6", 1),
                    ("D", "2026-01-01T00:15:00Z", "0.2", 1),
                    ("E", "2026-01-01T00:45:00Z", "0.7", 1),
                ]
            ],
        )
        labels = {"A": "positive", "B": "negative", "C": "positive", "D": "positive"}
        if coverage == "unknown_reviewed":
            del labels["B"]
        if coverage in {"unlabeled", "empty"}:
            labels.clear()
        if coverage == "empty":
            facts["alerts"] = []
        outcomes = dict(
            scenario_id=facts["scenario_id"],
            scenario_version=facts["scenario_version"],
            outcomes=[dict(alert_id=key, outcome=value) for key, value in labels.items()],
        )
        facts["content_sha256"] = fingerprint(facts, outcomes)
        (tmp_path / "two.json").write_text(json.dumps(facts), encoding="utf-8")
        (tmp_path / "two.outcomes.json").write_text(json.dumps(outcomes), encoding="utf-8")
        app = create_app()
        app.state.simulation_catalog = Catalog(tmp_path)
        return TestClient(app)

    return prepare


def scenario_recipe(client):
    response = client.get("/api/simulation/scenarios")
    assert response.status_code == 200
    (item,) = response.json()["items"]
    return {
        **recipe(),
        "scenario": {
            key: item[key] for key in ("scenario_id", "scenario_version", "content_sha256")
        },
        **item["defaults"],
    }


def compare(client, body):
    response = client.post("/api/simulation/comparisons", json=body)
    assert response.status_code == 200
    result = response.json()
    assert result["recipe"]["scenario"] == body["scenario"]
    assert result["recipe"]["budget_minutes_per_window"] == body["budget_minutes_per_window"]
    assert_no_private_labels(result)
    return result


def test_two_window_comparison_changes_one_setting_at_a_time(two_window_replay):
    with two_window_replay() as client:
        body = scenario_recipe(client)
        baseline = compare(client, body)
        higher_budget = compare(client, {**body, "budget_minutes_per_window": 4})
        higher_threshold = compare(client, {**body, "score_threshold": "0.8"})
        zero_budget = compare(client, {**body, "budget_minutes_per_window": 0})

    for result, threshold, admitted in [
        (baseline, "0.3", ["A", "B", "C", "E"]),
        (higher_budget, "0.3", ["A", "B", "C", "E"]),
        (higher_threshold, "0.8", ["A", "B"]),
        (zero_budget, "0.3", ["A", "B", "C", "E"]),
    ]:
        assert result["recipe"]["score_threshold"] == threshold
        assert [a["alert_id"] for a in result["admitted_alerts"]] == admitted
        assert [row["strategy_id"] for row in result["strategies"]] == [
            "fifo",
            "highest_score",
            "weighted_score_per_minute",
        ]

    for row in baseline["strategies"]:
        first, second = row["windows"]
        assert set(first["ranked_alert_ids"]) == {"A", "B"}
        assert first["reviewed_alert_ids"] == ["B"]
        assert set(second["ranked_alert_ids"]) == {"A", "C"}
        assert second["reviewed_alert_ids"] == ["C"]
        assert [first["used_minutes"], second["used_minutes"]] == [1, 1]
        assert row["pending_alert_ids"] == ["A", "E"]
        assert row["counts"] == dict(
            reviewed=2,
            backlog=2,
            unknown_in_horizon=1,
            unknown_reviewed=0,
            outcomes=dict(
                positives_found=1,
                positives_missed=2,
                positives_missed_threshold=1,
                positives_missed_backlog=1,
                reviewed_negatives=1,
            ),
        )

    for row, first_order in zip(
        higher_budget["strategies"], [["A", "B"], ["A", "B"], ["B", "A"]], strict=True
    ):
        first, second = row["windows"]
        assert first["reviewed_alert_ids"] == first_order
        assert second["reviewed_alert_ids"] == ["C"]
        assert [first["used_minutes"], second["used_minutes"]] == [4, 1]
        assert row["pending_alert_ids"] == ["E"]
        assert row["counts"]["outcomes"] == dict(
            positives_found=2,
            positives_missed=1,
            positives_missed_threshold=1,
            positives_missed_backlog=0,
            reviewed_negatives=1,
        )

    for row in higher_threshold["strategies"]:
        assert [w["reviewed_alert_ids"] for w in row["windows"]] == [["B"], []]
        assert row["pending_alert_ids"] == ["A"]
        assert row["counts"]["outcomes"] == dict(
            positives_found=0,
            positives_missed=3,
            positives_missed_threshold=2,
            positives_missed_backlog=1,
            reviewed_negatives=1,
        )

    for row in zero_budget["strategies"]:
        assert all(w["reviewed_alert_ids"] == [] and w["used_minutes"] == 0 for w in row["windows"])
        assert row["pending_alert_ids"] == ["A", "B", "C", "E"]
        assert row["counts"] == dict(
            reviewed=0,
            backlog=4,
            unknown_in_horizon=1,
            unknown_reviewed=0,
            outcomes=dict(
                positives_found=0,
                positives_missed=3,
                positives_missed_threshold=1,
                positives_missed_backlog=2,
                reviewed_negatives=0,
            ),
        )


@pytest.mark.parametrize(
    "coverage, reviewed, pending, unknown, unknown_reviewed, outcomes",
    [
        (
            "empty",
            0,
            0,
            0,
            0,
            dict(
                positives_found=0,
                positives_missed=0,
                positives_missed_threshold=0,
                positives_missed_backlog=0,
                reviewed_negatives=0,
            ),
        ),
        ("unlabeled", 2, 2, 5, 2, None),
        (
            "unknown_reviewed",
            2,
            2,
            2,
            1,
            dict(
                positives_found=1,
                positives_missed=2,
                positives_missed_threshold=1,
                positives_missed_backlog=1,
                reviewed_negatives=0,
            ),
        ),
    ],
)
def test_comparison_reports_outcome_coverage(
    two_window_replay, coverage, reviewed, pending, unknown, unknown_reviewed, outcomes
):
    with two_window_replay(coverage) as client:
        result = compare(client, scenario_recipe(client))
    for row in result["strategies"]:
        assert row["counts"] == dict(
            reviewed=reviewed,
            backlog=pending,
            unknown_in_horizon=unknown,
            unknown_reviewed=unknown_reviewed,
            outcomes=outcomes,
        )
        if coverage == "empty":
            assert result["admitted_alerts"] == []
            assert row["pending_alert_ids"] == []
            assert all(
                w["ranked_alert_ids"] == [] and w["used_minutes"] == 0 for w in row["windows"]
            )
