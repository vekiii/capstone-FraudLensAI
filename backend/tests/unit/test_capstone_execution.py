"""Offline checks for the prepared EV pack and execution records."""

import copy
import json
from pathlib import Path

import pytest

from fraudlens.investigation.models import digest

PACK = Path(__file__).resolve().parents[3] / 'evals/capstone'
IDS = [f'EV-{number:02}' for number in range(1, 17)]


def load(path):
    return json.loads((PACK / path).read_text(encoding='utf-8'))


def test_pack_separates_all_inputs_from_offline_expectations():
    pack = load('inputs/cases.json')
    cases = pack['cases']
    reference = load('reference/expectations.json')
    assert [row['id'] for row in cases] == [row['id'] for row in reference['expectations']] == IDS
    assert [row['mode'] for row in cases] == ['live'] * 10 + ['deterministic'] * 6
    assert all(set(row) == {'id', 'mode', 'seed', 'input', 'steps'} for row in cases)
    assert all(row['seed'] and row['input'] and row['steps'] for row in cases)
    assert all(row['acceptable_outcome'] and row['required_signals'] for row in reference['expectations'])
    assert cases[5]['input'] == {'saved_attempt_from': {'id': 'EV-01', 'phase': 'same'}}

    def keys(value):
        if isinstance(value, dict):
            return set(value).union(*(keys(child) for child in value.values()))
        if isinstance(value, list):
            return set().union(*(keys(child) for child in value))
        return set()

    assert keys(pack).isdisjoint({
        'reference', 'expectations', 'rubric', 'acceptable_outcome', 'required_signals', 'labels',
    })


def phase(name, statuses):
    cases = load('inputs/cases.json')['cases']
    rows = []
    for case, status in zip(cases, statuses, strict=True):
        measured = status in ('pass', 'fail')
        rows.append(dict(
            id=case['id'], mode=case['mode'], input_sha256=digest(case),
            seed_sha256=digest(case['seed']), status=status,
            outcome='Synthetic observation' if measured else None,
            reason=None if status == 'pass' else 'Synthetic reason',
            trace=['evals/results/capstone/synthetic.json'] if measured else [],
            binding=None, retries=[],
            versions=dict(configuration_sha256='a' * 64, corpus=None, retrieval=None, prompt=None,
                          requested_model=None, returned_model=None),
            metering=dict(reservations=0, confirmed_requests=0, unknown_outcomes=0,
                          local_rejections=0, simulated_requests=0, usage=None) if measured else None,
        ))
    return dict(schema_version=1, phase=name, commit='b' * 40, package_version='synthetic-test',
                rows=rows)


def test_aggregation_counts_all_statuses_in_16_slots_per_phase():
    from evals.capstone.execution import summarize

    baseline = phase('baseline', ['pass'] * 5 + ['blocked'] + ['fail'] * 3 + ['not_run'] * 7)
    final = phase('final', ['not_run'] * 10 + ['pass'] * 6)
    assert summarize(baseline, final) == {
        'baseline': {'total': 16, 'pass': 5, 'fail': 3, 'blocked': 1, 'not_run': 7},
        'final': {'total': 16, 'pass': 6, 'fail': 0, 'blocked': 0, 'not_run': 10},
    }


@pytest.mark.parametrize('problem', ['absent', 'duplicate', 'bad_status', 'bad_meter', 'no_reason',
                                    'no_trace', 'bad_digest', 'reference_field', 'wrong_mode'])
def test_phase_rejects_invalid_rows_without_shrinking_the_denominator(problem):
    from evals.capstone.execution import validate_phase

    batch = phase('baseline', ['pass'] * 5 + ['not_run'] * 11)
    row = batch['rows'][0]
    if problem == 'absent':
        batch['rows'].pop()
    elif problem == 'duplicate':
        batch['rows'][1]['id'] = row['id']
    elif problem == 'bad_status':
        row['status'] = 'skipped'
    elif problem == 'bad_meter':
        row['metering']['reservations'] = 1
    elif problem == 'no_reason':
        batch['rows'][5]['reason'] = None
    elif problem == 'no_trace':
        row['trace'] = []
    elif problem == 'bad_digest':
        row['input_sha256'] = 'missing'
    elif problem == 'reference_field':
        row['expectations'] = {}
    else:
        row['mode'] = 'deterministic'
    with pytest.raises(ValueError):
        validate_phase(batch)


def test_ev06_pass_requires_exact_saved_binding_from_its_own_phase():
    from evals.capstone.execution import summarize, validate_phase

    binding = dict(case_id='C' + 'c' * 32, source_mode='dataset', snapshot_ref='run_test',
                   context_revision='d' * 64, run_id='inv_' + 'e' * 32,
                   attempt_id='att_' + 'f' * 32, report_id='1' * 64, review_id='rev_' + '2' * 32,
                   evidence_ids=['ev_' + '3' * 32])
    baseline = phase('baseline', ['pass'] * 6 + ['not_run'] * 10)
    baseline['rows'][0]['binding'] = binding
    baseline['rows'][5]['binding'] = copy.deepcopy(binding)
    assert validate_phase(baseline)['pass'] == 6

    final = copy.deepcopy(baseline)
    final['phase'] = 'final'
    final['rows'][0]['binding']['attempt_id'] = 'att_' + '4' * 32
    with pytest.raises(ValueError, match='EV-06'):
        summarize(baseline, final)
    final['rows'][5]['status'] = 'fail'
    final['rows'][5]['reason'] = 'Synthetic mismatched attempt'
    assert summarize(baseline, final)['final']['fail'] == 1
    baseline['rows'][5]['metering'].update(reservations=1, confirmed_requests=1)
    with pytest.raises(ValueError, match='EV-06'):
        validate_phase(baseline)
