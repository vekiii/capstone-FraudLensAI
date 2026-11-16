"""Role binding and label isolation for calibrated judge batches, no real API."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest
from test_investigation_coverage_v4 import calibration

PATH = Path(__file__).resolve().parents[3] / 'evidence/tasks/feature-003-coverage-v4.py'
SPEC = importlib.util.spec_from_file_location('coverage_v4_runner_test', PATH)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def test_packet_builder_excludes_calibration_expected_labels():
    records = [dict(id=identity, result=dict(report=None, failure=None), evidence=[]) for identity in runner.IDS]
    packets = runner.packets_after_generation(records, {identity: {} for identity in runner.IDS})
    assert len(packets) == 6
    assert sum(p['role'] == 'primary' for p in packets) == 3
    assert sum(p['role'] == 'calibration' for p in packets) == 3
    body = json.dumps(packets)
    assert 'CAL4_EXPECTED_ONLY_CANARY' not in body and 'no_additional_issues' not in body
    assert all('expectations' not in p for p in packets)


def test_batch_rating_role_is_bound_to_packet_not_assumed_primary():
    packets, ratings, _ = calibration()
    value = dict(ratings=[dict(scenario_id='CAL4-STATUS', rating=ratings[('calibration', 'CAL4-STATUS')])])
    result = runner.validate_batch(packets, value)
    assert set(result) == {('calibration', 'CAL4-STATUS')}


@pytest.mark.parametrize('fault', ['duplicate', 'foreign', 'missing'])
def test_calibrated_batch_rejects_foreign_or_missing_scenarios(fault):
    packets, ratings, _ = calibration()
    row = dict(scenario_id='CAL4-STATUS', rating=ratings[('calibration', 'CAL4-STATUS')])
    value = dict(ratings=[row])
    if fault == 'duplicate':
        value['ratings'].append(copy.deepcopy(row))
    elif fault == 'foreign':
        row['scenario_id'] = 'foreign'
    else:
        value['ratings'].clear()
    with pytest.raises(ValueError):
        runner.validate_batch(packets, value)


def test_failed_calibration_preserves_raw_scores_without_claiming_quality_pass(monkeypatch):
    packets, ratings, expected = calibration()
    ratings[('calibration', 'CAL4-STATUS')]['additional_issues'] = ['Incorrect disposition interpretation.']
    monkeypatch.setattr(runner, 'BASE_SUMMARIZE', lambda *args: dict(passing_development_reports=3, judge_status='completed'))
    monkeypatch.setattr(runner.core, 'load', lambda path: dict(expectations=expected))
    result = runner.summarize([], packets, ratings, {}, None, {})
    assert result['raw_passing_development_reports'] == 3
    assert result['passing_development_reports'] is None
    assert result['quality_assessment_valid'] is False


def test_missing_judge_response_never_passes_calibration(monkeypatch):
    packets, _, expected = calibration()
    monkeypatch.setattr(runner, 'BASE_SUMMARIZE', lambda *args: dict(passing_development_reports=None, judge_status='unavailable'))
    monkeypatch.setattr(runner.core, 'load', lambda path: dict(expectations=expected))
    result = runner.summarize([], packets, None, {}, None, {})
    assert result['passing_development_reports'] is None and not result['quality_assessment_valid']
