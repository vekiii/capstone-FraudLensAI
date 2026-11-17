"""SC-006 measurement arithmetic; no actual-provider performance claims."""

import copy
import json
import sys

import pytest

from fraudlens.investigation import timing_evaluation as timing


def demo():
    ids = [f"TIME-{i}" for i in range(5)]
    rows = [dict(id=i, seconds=90, state="needs_information", report_validated=True) for i in ids]
    return ids, rows


def test_exact_thresholds_and_failed_outcome_separate_from_terminal():
    ids, rows = demo()
    rows[-1].update(state="failed", seconds=120, report_validated=False)
    result = timing.assess_demo(ids, rows)
    assert result["successful_within_90"] == 4
    assert result["all_terminal_within_120"] is True
    assert result["passed"] is True
    rows[-1]["seconds"] = 120.001
    assert timing.assess_demo(ids, rows)["passed"] is False


def test_no_three_case_substitution_or_dropped_failures():
    ids, rows = demo()
    with pytest.raises(ValueError):
        timing.assess_demo(ids[:3], rows[:3])
    result = timing.assess_demo(ids, rows[:3])
    assert result["denominator"] == 5 and result["successful_within_90"] == 3
    assert result["passed"] is False and len(result["rows"]) == 5
    assert result["all_terminal_within_120"] is False


@pytest.mark.parametrize("state", ["failed", "cancelled", "created", "drafting"])
def test_fast_failure_or_active_is_not_success(state):
    ids, rows = demo()
    for r in rows:
        r.update(state=state, seconds=1, report_validated=False)
    result = timing.assess_demo(ids, rows)
    assert result["successful_within_90"] == 0
    assert result["all_terminal_within_120"] is (state in {"failed", "cancelled"})


@pytest.mark.parametrize("seconds", [True, -1, float("nan"), float("inf"), "12"])
def test_invalid_elapsed_cannot_pass(seconds):
    ids, rows = demo()
    rows[0]["seconds"] = seconds
    with pytest.raises(ValueError):
        timing.assess_demo(ids, rows)


def test_boundary_and_report_validation():
    ids, rows = demo()
    for row in rows:
        row["seconds"] = 90.001
    assert timing.assess_demo(ids, rows)["successful_within_90"] == 0
    for row in rows:
        row.update(seconds=1, report_validated=False)
    assert timing.assess_demo(ids, rows)["successful_within_90"] == 0


@pytest.mark.parametrize("mutation", ["duplicate", "foreign", "duplicate_ids"])
def test_no_replacement_or_double_count(mutation):
    ids, rows = demo()
    if mutation == "duplicate":
        rows.append(copy.deepcopy(rows[0]))
    elif mutation == "foreign":
        rows[0]["id"] = "NOT-FROZEN"
    else:
        ids[0] = ids[1]
    with pytest.raises(ValueError):
        timing.assess_demo(ids, rows)


def test_search_p95_rank19_not_max_or_average_and_no_dropped_error():
    ids = [f"Q{i}" for i in range(20)]
    samples = [dict(id=i, seconds=2, error=False) for i in ids]
    samples[-1]["seconds"] = 100
    result = timing.assess_searches(ids, samples)
    assert result["p95_seconds"] == 2 and result["passed"] is True
    samples[-2]["seconds"] = 2.01
    assert timing.assess_searches(ids, samples)["passed"] is False
    samples[-2]["seconds"] = 1
    samples[0]["error"] = True
    result = timing.assess_searches(ids, samples)
    assert result["passed"] is False and result["p95_seconds"] is None
    assert timing.assess_searches(ids, samples[:19])["passed"] is False


def test_cli_keeps_original_output(tmp_path, monkeypatch):
    ids, rows = demo()
    queries = [f"Q{i}" for i in range(20)]
    source, output = tmp_path / "input.json", tmp_path / "output.json"
    source.write_text(
        json.dumps(
            dict(
                scenario_order=ids,
                observations=rows,
                search_order=queries,
                searches=[dict(id=i, seconds=1, error=False) for i in queries],
            )
        )
    )
    monkeypatch.setattr(sys, "argv", ["timing", "--input", str(source), "--output", str(output)])
    timing.main()
    assert json.loads(output.read_text())["performance_pass"] is True
    original = output.read_bytes()
    with pytest.raises(FileExistsError):
        timing.main()
    assert output.read_bytes() == original
