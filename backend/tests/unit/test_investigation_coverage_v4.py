"""Calibration/identity gates and immutable prompt binding, no live model calls."""
import asyncio

import pytest
from test_investigation_workflow import create
from test_investigation_workflow import runtime as workflow_runtime

from fraudlens.investigation.judge_calibration import assess_calibration

runtime = workflow_runtime


def calibration():
    packets = [dict(role='calibration', scenario_id='CAL4-STATUS', failed=False,
                    units=[dict(unit_id='fact', claim_kind='observation')])]
    rating = dict(units=[dict(unit_id='fact', judgment='supported', reason='Authored test evidence.',
                             critical_error=False)], missingness_correct=True,
                  missingness_reason='All declared disclosures present.', critical_error=False, additional_issues=[])
    expected = [dict(scenario_id='CAL4-STATUS', missingness_correct=True, critical_error=False,
                     no_additional_issues=True, units=dict(fact=dict(judgment='supported', critical_error=False)))]
    return packets, {('calibration', 'CAL4-STATUS'): rating}, expected


def test_calibration_accepts_correct_needs_information_assessment():
    packets, ratings, expected = calibration()
    result = assess_calibration(packets, ratings, expected)
    assert result['passed'] is True and result['cases'][0]['matched'] is True


@pytest.mark.parametrize('fault', ['false_disposition', 'critical_missed', 'missingness', 'unit', 'missing_rating'])
def test_calibration_failure_cannot_authorize_quality_pass(fault):
    packets, ratings, expected = calibration()
    rating = ratings[('calibration', 'CAL4-STATUS')]
    if fault == 'false_disposition':
        rating['additional_issues'] = ['needs_information is an unauthorized disposition.']
    elif fault == 'critical_missed':
        expected[0]['critical_error'] = True
    elif fault == 'missingness':
        expected[0]['missingness_correct'] = False
    elif fault == 'unit':
        rating['units'][0]['judgment'] = 'uncertain'
    else:
        ratings.clear()
    assert assess_calibration(packets, ratings, expected)['passed'] is False


def test_negative_control_is_passed_only_when_bad_report_is_recognized():
    packets, ratings, expected = calibration()
    expected[0].update(critical_error=True, missingness_correct=False, no_additional_issues=False)
    expected[0]['units']['fact'].update(judgment='unsupported', critical_error=True)
    value = ratings[('calibration', 'CAL4-STATUS')]
    value.update(critical_error=True, missingness_correct=False)
    value['units'][0].update(judgment='unsupported', critical_error=True)
    assert assess_calibration(packets, ratings, expected)['passed'] is True


def test_primary_report_ratings_cannot_substitute_for_calibration():
    packets, ratings, expected = calibration()
    ratings[('primary', 'CAL4-STATUS')] = ratings.pop(('calibration', 'CAL4-STATUS'))
    assert assess_calibration(packets, ratings, expected)['passed'] is False


def test_calibration_binding_error_is_not_accepted():
    packets, ratings, expected = calibration()
    ratings[('calibration', 'CAL4-STATUS')]['units'][0]['unit_id'] = 'foreign'
    assert assess_calibration(packets, ratings, expected)['passed'] is False


def test_new_attempt_pins_v3_and_retry_keeps_older_prompt(runtime, monkeypatch):
    from pathlib import Path
    _, request, make = runtime
    service = make('needs_information')
    read = Path.read_text
    old = Path('prompts/application/investigation-v2.md').read_text(encoding='utf-8')

    def older(self, *args, **kwargs):
        if self.name == 'investigation-v3.md':
            return old
        return read(self, *args, **kwargs)

    with monkeypatch.context() as scoped:
        scoped.setattr(Path, 'read_text', older)
        parent = create(service, request)
    assert asyncio.run(service.work_once())['state'] == 'needs_information'
    parent = service.read(parent['attempt_id'])
    child = service.retry(parent['attempt_id'], parent['revision'], False, 'local-analyst',
                          '00000000-0000-4000-8000-000000000004')
    assert service.binding(child['attempt_id'])['prompt'] == old
    fresh = create(service, request)
    assert service.binding(fresh['attempt_id'])['prompt'].startswith('# Investigation application prompt v3')
