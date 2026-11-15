"""Authored judge-boundary tests, not actual model evaluation."""
import copy

import pytest

from fraudlens.investigation.judging import aggregate, validate_rating


def packet(role='primary', identity='H1', failed=False):
    return dict(role=role, scenario_id=identity, failed=failed,
                units=[] if failed else [dict(unit_id='fact', claim_kind='observation'),
                                        dict(unit_id='essential', claim_kind='essential_fact')])


def rating():
    return dict(units=[dict(unit_id='fact', judgment='supported', reason='Evidence confirms',
                           critical_error=False),
                       dict(unit_id='essential', judgment='present', reason='Explicitly stated',
                            critical_error=False)], missingness_correct=True,
                missingness_reason='All gaps disclosed', critical_error=False, additional_issues=[])


@pytest.mark.parametrize('change', ['extra', 'missing', 'duplicate', 'foreign', 'wrong_kind',
                                   'blank_reason', 'bool_string', 'missingness'])
def test_reject_invalid_machine_judgments(change):
    value = rating()
    if change == 'extra':
        value['reviewer_identity'] = 'Vedran'
    elif change == 'missing':
        value['units'].pop()
    elif change == 'duplicate':
        value['units'][1] = copy.deepcopy(value['units'][0])
    elif change == 'foreign':
        value['units'][0]['unit_id'] = 'other'
    elif change == 'wrong_kind':
        value['units'][0]['judgment'] = 'present'
    elif change == 'blank_reason':
        value['units'][0]['reason'] = ' '
    elif change == 'bool_string':
        value['units'][0]['critical_error'] = 'false'
    else:
        value['missingness_correct'] = 'yes'
    with pytest.raises(ValueError):
        validate_rating(packet(), value)


def test_failures_not_dropped_empty_claims_not_perfect_and_disagreements_preserved():
    primary = packet()
    secondary = packet('secondary')
    value = rating()
    other = rating()
    other['units'][0]['judgment'] = 'uncertain'
    result = aggregate([primary, secondary, packet(identity='H2', failed=True)],
                       {('primary', 'H1'): value, ('secondary', 'H1'): other})
    assert result['report_count'] == 2 and result['failed_reports'] == 1
    assert result['passing_reports'] == 0 and not result['quality_pass']
    assert result['reports'][0]['support_rate'] == 0
    assert result['reports'][1]['support_rate'] is None
    assert len(result['disagreements']) == 1
    assert value['units'][0]['judgment'] == 'supported'


@pytest.mark.parametrize('gate', ['missingness', 'critical', 'additional'])
def test_quality_cannot_ignore_missingness_critical_or_unlisted_prose(gate):
    value = rating()
    if gate == 'missingness':
        value['missingness_correct'] = False
    elif gate == 'critical':
        value['critical_error'] = True
    else:
        value['additional_issues'] = ['Unsupported unlisted prose']
    result = aggregate([packet()], {('primary', 'H1'): value})
    assert result['passing_reports'] == 0


def test_incomplete_ratings_cannot_be_aggregated_as_a_pass():
    with pytest.raises(ValueError):
        aggregate([packet(), packet('secondary')], {('primary', 'H1'): rating()})


def test_unresolved_disagreement_prevents_pass_even_if_support_threshold_met():
    p = packet()
    first = rating()
    for i in range(9):
        p['units'].append(dict(unit_id=f'extra{i}', claim_kind='observation'))
        first['units'].append(dict(unit_id=f'extra{i}', judgment='supported',
                                   reason='Authored evidence', critical_error=False))
    second = copy.deepcopy(first)
    second['units'][0]['judgment'] = 'unsupported'
    result = aggregate([p, {**p, 'role': 'secondary'}],
                       {('primary', 'H1'): first, ('secondary', 'H1'): second})
    assert result['reports'][0]['support_rate'] == .9
    assert not result['reports'][0]['passed']


def test_actual_sdk_serialization_is_stateless_and_ledger_counts_transports(tmp_path, monkeypatch):
    import importlib.util
    import json
    import sys

    import httpx2

    from fraudlens.investigation.models import ROOT

    path = ROOT / 'evidence/tasks/feature-003-judge-run.py'
    spec = importlib.util.spec_from_file_location('authored_judge_runner', path)
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    packets = [packet(), packet('secondary'), packet(identity='H2')]
    monkeypatch.setattr(runner, 'prepare', lambda: packets)
    monkeypatch.setattr(runner, 'OUT', tmp_path / 'judge')
    monkeypatch.setattr(sys, 'argv', [str(path), '--execute', '--approved-cap', '6'])
    monkeypatch.setenv('OPENAI_API_KEY', 'AUTHORED-TEST-ONLY')
    bodies = []

    def handle(request):
        body = json.loads(request.content)
        bodies.append(body)
        assert body['store'] is False and 'previous_response_id' not in body
        assert 'tools' not in body and 'primary_judgments' not in body['input']
        return httpx2.Response(200, json=dict(id='resp_authored', object='response',
            created_at=1, status='completed', model='gpt-6-luna', output=[dict(type='message',
                id='msg_authored', role='assistant', status='completed', content=[dict(
                    type='output_text', text=json.dumps(rating()), annotations=[])])],
            usage=dict(input_tokens=1, output_tokens=1, total_tokens=2)))

    monkeypatch.setattr(httpx2, 'HTTPTransport', lambda **kwargs: httpx2.MockTransport(handle))
    assert runner.main() == 0
    assert len(bodies) == 3
    assert len(json.loads((runner.OUT / 'transport-ledger.json').read_text())['attempts']) == 3
