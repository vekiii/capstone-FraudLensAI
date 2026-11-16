"""Offline scope/denominator guards for the new live diagnostic harness."""
import asyncio
import copy
import importlib.util
import json
from pathlib import Path

import httpx2
import pytest
from test_investigation_coverage_v4 import calibration

from fraudlens.investigation.provider import Turn, scripted_draft

PATH = Path(__file__).resolve().parents[3] / 'evidence/tasks/feature-003-live-repair-v6.py'
SPEC = importlib.util.spec_from_file_location('live_repair_v6_test', PATH)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def conversation():
    ref = 'ev_' + 'a' * 32
    return [dict(type='context', data=dict(case_id='CASE-763')),
            dict(type='tool_result', result=dict(evidence=[dict(evidence_id=ref,
                kind='case_fact', facts=[dict(path='transaction.amount', value='675.90'),
                                       dict(path='transaction.currency', value='GBP')])]))]


def test_injected_candidate_is_invalid_but_actual_provider_output_untouched():
    messages = conversation()
    draft = scripted_draft(messages, 'grounded')
    turn = Turn('draft', draft=draft, private_items=({'type': 'reasoning', 'encrypted_content': 'OPAQUE'},))
    before = copy.deepcopy((messages, turn))
    candidate = runner.invalid_candidate(messages, turn)
    assertion = candidate['observed_facts'][0]['exact_assertions'][0]
    assert assertion['value'] != '675.90'
    assert assertion['path'] == 'transaction.amount'
    assert (messages, turn) == before
    assert candidate is not draft


@pytest.mark.parametrize('case', ['CASE-761', 'CASE-762', 'CASE-999'])
def test_fault_injection_refuses_an_ordinary_or_foreign_case(case):
    messages = conversation()
    messages[0]['data']['case_id'] = case
    with pytest.raises(ValueError, match='diagnostic scope'):
        runner.invalid_candidate(messages, Turn('draft', draft=scripted_draft(messages, 'grounded')))


def test_no_case_fact_is_not_a_fabricated_repair_success():
    with pytest.raises(ValueError, match='case facts'):
        runner.invalid_candidate(conversation()[:1], Turn('draft', draft={}))


def test_diagnostic_packet_is_excluded_from_primary_quality_denominator():
    packets = [dict(role='primary', scenario_id=identity, failed=True, units=[])
               for identity in runner.IDS]
    before = copy.deepcopy(packets)
    result = runner.diagnostic_roles(packets)
    assert packets == before
    assert [p['scenario_id'] for p in result if p['role'] == 'primary'] == list(runner.IDS[:2])
    assert result[-1]['role'] == 'diagnostic'
    summary = runner.core.aggregate(result, {})
    assert summary['report_count'] == 2 and summary['failed_reports'] == 2


def test_wrapper_injects_once_and_keeps_original_turn_history_and_usage(monkeypatch):
    saved = []
    monkeypatch.setattr(runner.core, 'frozen', lambda path, value: saved.append(value))
    provider = runner.FaultProvider.__new__(runner.FaultProvider)
    provider.history = [{'type': 'reasoning', 'encrypted_content': 'AUTHORED-OPAQUE'}]
    messages = conversation()
    draft = scripted_draft(messages, 'grounded')
    turn = Turn('draft', draft=draft, private_items=tuple(provider.history), usage={'total_tokens': 42})
    before = copy.deepcopy((turn, provider.history))
    injected = provider.application_candidate(messages, turn)
    assert injected.draft != draft and injected.usage == turn.usage
    assert injected.private_items == turn.private_items
    assert (turn, provider.history) == before
    assert provider.application_candidate(messages, turn) is turn
    assert len(saved) == 1 and saved[0]['injected']


def test_wrapper_never_injects_an_ordinary_case(monkeypatch):
    monkeypatch.setattr(runner.core, 'frozen', lambda *args: pytest.fail('Ordinary fault artifact forbidden'))
    provider = runner.FaultProvider.__new__(runner.FaultProvider)
    messages = conversation()
    messages[0]['data']['case_id'] = 'CASE-761'
    turn = Turn('draft', draft={})
    assert provider.application_candidate(messages, turn) is turn
    assert provider.attempted is False


def test_judge_packets_have_two_primaries_and_no_expected_calibration_labels():
    records = [dict(id=identity, result=dict(report=None, failure=None), evidence=[]) for identity in runner.IDS]
    packets = runner.packets_after_generation(records, {identity: {} for identity in runner.IDS})
    assert len(packets) == 6
    assert [p['scenario_id'] for p in packets if p['role'] == 'primary'] == list(runner.IDS[:2])
    assert sum(p['role'] == 'diagnostic' for p in packets) == 1
    assert sum(p['role'] == 'calibration' for p in packets) == 3
    encoded = json.dumps(packets)
    assert 'CAL6_EXPECTED_ONLY_CANARY' not in encoded and 'expectations' not in encoded


def test_failed_calibration_still_blocks_v6_quality_claims(monkeypatch):
    packets, ratings, expected = calibration()
    ratings[('calibration', 'CAL4-STATUS')]['additional_issues'] = ['Authored calibration failure']
    monkeypatch.setattr(runner.base, 'BASE_SUMMARIZE', lambda *args: dict(passing_development_reports=2, judge_status='completed'))
    monkeypatch.setattr(runner.core, 'load', lambda path: dict(expectations=expected))
    monkeypatch.setattr(runner, 'controlled_result', lambda *args: dict(mechanism_pass=True))
    result = runner.summarize([], packets, ratings, {}, None, {})
    assert result['ordinary_case_count'] == 2
    assert result['raw_passing_development_reports'] == 2
    assert result['passing_development_reports'] is None
    assert result['controlled_report_quality_pass'] is None
    assert result['quality_assessment_valid'] is False


def test_calibration_expected_canary_never_reserves_or_dispatches(tmp_path):
    ledger = runner.core.Ledger(tmp_path / 'ledger.json')

    def forbidden(request):
        pytest.fail('Calibration label reached transport')

    async def exercise():
        metered = runner.Metered(ledger, 'generation', runner.IDS[0], inner=httpx2.MockTransport(forbidden))
        try:
            request = httpx2.Request('POST', 'https://example.invalid', content=b'CAL6_EXPECTED_ONLY_CANARY')
            with pytest.raises(ValueError, match='provider_input_invalid'):
                await metered.handle_async_request(request)
        finally:
            await metered.aclose()

    asyncio.run(exercise())
    assert ledger.value['attempts'] == []
