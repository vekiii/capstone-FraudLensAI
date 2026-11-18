"""Hand-calculated RED expectations; no outcomes supplied to replay."""

import copy

import pytest

from fraudlens.simulation.models import Scenario
from fraudlens.simulation.replay import replay
from fraudlens.simulation.scenarios import Catalog


def scenario(alerts=None, windows=None):
    facts = Catalog().resolve("review-capacity-demo", 1).facts.model_dump()
    if alerts is not None:
        template = facts["alerts"][0]
        facts["alerts"] = [{**template, **row} for row in alerts]
    if windows is not None:
        facts["window_starts"] = windows
    return Scenario.model_validate(facts)


def run(facts, threshold="0.30", budget=2):
    assert "outcomes" not in facts.model_dump()
    original = copy.deepcopy(facts.model_dump())
    results = replay(facts, threshold, budget)
    assert [r["strategy_id"] for r in results] == [
        "fifo",
        "highest_score",
        "weighted_score_per_minute",
    ]
    assert facts.model_dump() == original
    return results


@pytest.mark.parametrize("three", [False, True], ids=["A-E", "three-alert"])
def test_hand_calculated_default_orders(three):
    facts = scenario()
    if three:
        facts = facts.model_copy(update={"alerts": facts.alerts[:3]})
    rows = run(facts, "0" if three else "0.30")
    for row, reviewed, ranked, pending in zip(
        rows,
        [["A"], ["B"], ["C"] if three else ["C", "E"]],
        [
            ["A", "B", "C"] if three else ["A", "B", "C", "E"],
            ["B", "C", "A"] if three else ["B", "C", "E", "A"],
            ["C", "B", "A"] if three else ["C", "E", "B", "A"],
        ],
        [
            ["B", "C"] if three else ["B", "C", "E"],
            ["A", "C"] if three else ["A", "C", "E"],
            ["A", "B"],
        ],
    ):
        assert row["windows"][0] == dict(
            starts_at=facts.window_starts[0],
            ranked_alert_ids=ranked,
            reviewed_alert_ids=reviewed,
            used_minutes=1 if three and row["strategy_id"] == "weighted_score_per_minute" else 2,
        )
        assert row["pending_alert_ids"] == pending


def test_threshold_is_inclusive():
    rows = run(scenario([dict(alert_id="X", score="0.30", estimated_review_minutes=1)]))
    assert all(r["windows"][0]["reviewed_alert_ids"] == ["X"] for r in rows)


def test_weighted_exact_rational_priorities_do_not_round_to_float_tie():
    # B has a strictly higher weight far beyond float/Decimal default precision.
    rows = run(
        scenario(
            [
                dict(alert_id="A", score="0.5", weight="1", estimated_review_minutes=1),
                dict(
                    alert_id="B",
                    score="0.5",
                    weight="1." + "0" * 60 + "1",
                    estimated_review_minutes=1,
                ),
            ]
        ),
        budget=1,
    )
    assert rows[2]["windows"][0]["ranked_alert_ids"] == ["B", "A"]
    assert rows[2]["windows"][0]["reviewed_alert_ids"] == ["B"]


def test_tie_break_uses_availability_then_case_sensitive_id():
    rows = run(
        scenario(
            [
                dict(
                    alert_id="a",
                    available_at="2026-01-01T00:01:00Z",
                    score="0.8",
                    estimated_review_minutes=1,
                ),
                dict(alert_id="B", score="0.8", estimated_review_minutes=1),
                dict(alert_id="A", score="0.8", estimated_review_minutes=1),
            ],
            ["2026-01-01T00:00:00Z", "2026-01-01T00:02:00Z"],
        ),
        budget=0,
    )
    assert all(r["windows"][1]["ranked_alert_ids"] == ["A", "B", "a"] for r in rows)


def test_window_start_arrivals_reset_scan_carry_over_and_uniqueness():
    facts = scenario(
        [
            dict(alert_id="A", estimated_review_minutes=3, score="0.9"),
            dict(alert_id="B", estimated_review_minutes=1, score="0.8"),
            dict(
                alert_id="C",
                available_at="2026-01-01T00:10:00Z",
                estimated_review_minutes=1,
                score="0.7",
            ),
            dict(
                alert_id="D",
                available_at="2026-01-01T00:11:00Z",
                estimated_review_minutes=1,
                score="0.6",
            ),
        ],
        ["2026-01-01T00:00:00Z", "2026-01-01T00:10:00Z", "2026-01-01T00:20:00Z"],
    )
    for row in run(facts, budget=1):
        assert [w["reviewed_alert_ids"] for w in row["windows"]] == [["B"], ["C"], ["D"]]
        assert [w["used_minutes"] for w in row["windows"]] == [1, 1, 1]
        assert row["pending_alert_ids"] == ["A"]
        flat = [i for w in row["windows"] for i in w["reviewed_alert_ids"]]
        assert len(flat) == len(set(flat))
        assert "C" not in row["windows"][0]["ranked_alert_ids"]


def test_late_arrivals_enter_final_backlog_in_availability_id_order():
    rows = run(
        scenario(
            [
                dict(alert_id="Z", available_at="2026-01-01T00:59:59.999999Z"),
                dict(alert_id="B", available_at="2026-01-01T00:01:00Z"),
                dict(alert_id="A", available_at="2026-01-01T00:01:00Z"),
            ]
        )
    )
    assert all(r["windows"][0]["ranked_alert_ids"] == [] for r in rows)
    assert all(r["pending_alert_ids"] == ["A", "B", "Z"] for r in rows)


def test_exclusive_horizon_end_is_rejected_before_replay():
    with pytest.raises(ValueError):
        scenario([dict(alert_id="X", available_at="2026-01-01T01:00:00Z")])


def test_whole_case_carry_over_can_fit_next_reset_budget():
    rows = run(
        scenario(
            [
                dict(alert_id="A", score="0.9", estimated_review_minutes=2),
                dict(alert_id="B", score="0.8", estimated_review_minutes=1),
            ],
            ["2026-01-01T00:00:00Z", "2026-01-01T00:10:00Z"],
        )
    )
    for i, row in enumerate(rows):
        assert [w["reviewed_alert_ids"] for w in row["windows"]] == (
            [["B"], ["A"]] if i == 2 else [["A"], ["B"]]
        )
        assert [w["used_minutes"] for w in row["windows"]] == ([1, 2] if i == 2 else [2, 1])
        assert row["pending_alert_ids"] == []
