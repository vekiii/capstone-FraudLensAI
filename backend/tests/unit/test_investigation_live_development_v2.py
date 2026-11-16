"""Durable live-runner guards over authored transports, never a real provider."""
import asyncio
import importlib.util
import json
from pathlib import Path

import httpx2
import pytest

from fraudlens.investigation.report_policy import HUMAN_AUTHORITY_NOTICE
from fraudlens.investigation.settings import InvestigationSettings

PATH = Path(__file__).resolve().parents[3] / 'evidence/tasks/feature-003-live-development-v2.py'
SPEC = importlib.util.spec_from_file_location('live_development_v2', PATH)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def test_reservation_is_persisted_as_unknown_before_any_io(tmp_path):
    ledger = runner.Ledger(tmp_path / 'ledger.json')
    item = ledger.reserve('generation', 'DEV2-701')
    assert item['outcome'] == 'unknown' and item['sequence'] == 1
    saved = json.loads(ledger.path.read_text())
    assert saved['attempts'] == [item]
    assert runner.Ledger(ledger.path).value == saved


def test_case_cap_survives_process_reload(tmp_path):
    path = tmp_path / 'ledger.json'
    for _ in range(8):
        runner.Ledger(path).reserve('generation', 'DEV2-701')
    with pytest.raises(ValueError):
        runner.Ledger(path).reserve('generation', 'DEV2-701')
    assert len(runner.Ledger(path).value['attempts']) == 8


def test_three_cases_and_only_one_judge_request(tmp_path):
    ledger = runner.Ledger(tmp_path / 'ledger.json')
    for identity in ('DEV2-701', 'DEV2-702', 'DEV2-703'):
        for _ in range(8):
            ledger.reserve('generation', identity)
    ledger.reserve('judge', 'batch')
    assert len(ledger.value['attempts']) == 25
    with pytest.raises(ValueError):
        ledger.reserve('judge', 'batch')
    with pytest.raises(ValueError):
        ledger.reserve('generation', 'DEV2-701')


@pytest.mark.parametrize('phase,identity', [('other', 'batch'), ('judge', 'foreign'),
                                        ('generation', '../escape'), ('generation', 'OLD-H01')])
def test_unknown_scope_cannot_dispatch(tmp_path, phase, identity):
    ledger = runner.Ledger(tmp_path / 'ledger.json')
    with pytest.raises(ValueError):
        ledger.reserve(phase, identity)
    assert ledger.value['attempts'] == []


def prepared(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'load_settings', lambda: InvestigationSettings(
        provider='openai', model='gpt-6-luna', api_key='AUTHORED-NOT-A-REAL-KEY'))
    return runner.prepare(tmp_path / 'out')


def test_prepare_hashes_but_never_parses_reference_or_dispatches(tmp_path, monkeypatch):
    original = runner.load

    def guarded(path):
        if Path(path).name == 'reference.json':
            pytest.fail('References parsed before generation')
        return original(path)

    monkeypatch.setattr(runner, 'load', guarded)
    inputs, _, _, _, _, freeze = prepared(tmp_path, monkeypatch)
    assert len(inputs) == 3 and freeze['cap'] == 25
    assert not (tmp_path / 'out/transport-ledger.json').exists()


def test_unknown_prior_dispatch_blocks_case_replay(tmp_path, monkeypatch):
    inputs, protocol, settings, knowledge, versions, freeze = prepared(tmp_path, monkeypatch)
    ledger = runner.Ledger(tmp_path / 'out/transport-ledger.json')
    ledger.reserve('generation', 'DEV2-701')
    with pytest.raises(ValueError, match='ambiguous'):
        asyncio.run(runner.generate(inputs, protocol, settings, knowledge, versions,
                                    freeze, ledger, tmp_path / 'out'))
    assert len(ledger.value['attempts']) == 1


def test_metered_transport_reserves_before_io_and_counts_connection_failure(tmp_path):
    ledger = runner.Ledger(tmp_path / 'ledger.json')

    def fail(request):
        assert json.loads(ledger.path.read_text())['attempts'][0]['outcome'] == 'unknown'
        raise httpx2.ConnectError('AUTHORED FAILURE')

    transport = runner.Metered(ledger, 'generation', 'DEV2-701', httpx2.MockTransport(fail))

    async def exercise():
        with pytest.raises(httpx2.ConnectError):
            await transport.handle_async_request(httpx2.Request('POST', 'https://example.invalid', content=b'{}'))
        await transport.aclose()

    asyncio.run(exercise())
    assert len(ledger.value['attempts']) == 1
    assert ledger.value['attempts'][0]['error_type'] == 'ConnectError'
    assert 'AUTHORED FAILURE' not in ledger.path.read_text()


def test_reference_marker_never_reaches_transport(tmp_path):
    ledger = runner.Ledger(tmp_path / 'ledger.json')
    transport = runner.Metered(ledger, 'generation', 'DEV2-701',
        httpx2.MockTransport(lambda request: pytest.fail('Reference marker sent')))

    async def exercise():
        with pytest.raises(ValueError):
            await transport.handle_async_request(httpx2.Request('POST', 'https://example.invalid', content=runner.CANARY))
        await transport.aclose()

    asyncio.run(exercise())
    assert not ledger.value['attempts']


def test_actual_sdk_mocked_generation_pins_configs_and_never_reads_expectations(tmp_path, monkeypatch):
    inputs, protocol, settings, knowledge, versions, freeze = prepared(tmp_path, monkeypatch)
    ledger = runner.Ledger(tmp_path / 'out/transport-ledger.json')
    seen = []
    original = runner.load

    def guarded(path):
        if Path(path).name == 'reference.json':
            pytest.fail('Reference opened by generator')
        return original(path)

    monkeypatch.setattr(runner, 'load', guarded)
    draft = dict(outcome='needs_information', summary=[], observed_facts=[], risk_indicators=[],
        alternative_explanations=[], recommended_checks=[], citations=[],
        missing_information=['Authored test missing information.'],
        limitations=['Authored test only.', HUMAN_AUTHORITY_NOTICE])

    def handler(request):
        body = json.loads(request.content)
        assert runner.CANARY not in request.content and b'essential_facts' not in request.content
        seen.append(body)
        return httpx2.Response(200, json=dict(id='authored_response', model='gpt-6-luna',
            status='completed', usage=dict(input_tokens=5, output_tokens=5, total_tokens=10),
            output=[dict(type='message', role='assistant', content=[dict(type='output_text', text=json.dumps(draft))])]))

    transport_class = runner.Metered
    monkeypatch.setattr(runner, 'Metered', lambda ledger, phase, identity:
        transport_class(ledger, phase, identity, httpx2.MockTransport(handler)))
    records = asyncio.run(runner.generate(inputs, protocol, settings, knowledge, versions,
                                         freeze, ledger, tmp_path / 'out'))
    assert len(records) == len(seen) == 3
    assert all(r['result']['state'] == 'needs_information' for r in records)
    assert records[0]['result']['retrieval_version'] == versions['candidate']
    assert records[2]['result']['retrieval_version'] == versions['controlled_no_match']
    assert all(a['usage']['total_tokens'] == 10 for a in ledger.value['attempts'])
    asyncio.run(runner.generate(inputs, protocol, settings, knowledge, versions,
                               freeze, ledger, tmp_path / 'out'))
    assert len(seen) == 3  # Saved outcomes are reused without new dispatches.


def test_judge_cannot_open_references_until_all_generation_outcomes_are_saved(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'load', lambda path: pytest.fail('Reference opened too early'))
    with pytest.raises(ValueError, match='sealed'):
        asyncio.run(runner.judge([{}] * 3, None, None, None, tmp_path))


@pytest.mark.parametrize('change', ['duplicate', 'missing', 'foreign', 'unit_binding'])
def test_batch_judgment_cannot_omit_duplicate_or_reassign_ratings(change):
    from test_investigation_judging import packet, rating
    packets = [packet(identity='DEV2-701'), packet(identity='DEV2-702')]
    rows = [dict(scenario_id=p['scenario_id'], rating=rating()) for p in packets]
    if change == 'duplicate':
        rows[1]['scenario_id'] = rows[0]['scenario_id']
    elif change == 'missing':
        rows.pop()
    elif change == 'foreign':
        rows[1]['scenario_id'] = 'OLD-H01'
    else:
        rows[0]['rating']['units'][0]['unit_id'] = 'foreign-unit'
    with pytest.raises(ValueError):
        runner.validate_batch(packets, dict(ratings=rows))


def test_actual_sdk_batch_judge_is_one_stateless_request_and_saved_rating_is_reused(tmp_path, monkeypatch):
    _, _, settings, _, _, freeze = prepared(tmp_path, monkeypatch)
    out = tmp_path / 'out'
    records = []
    for identity in runner.IDS:
        record = dict(id=identity, result=dict(report=dict(draft={k: [] for k in (
            'summary', 'observed_facts', 'risk_indicators', 'alternative_explanations',
            'recommended_checks')}), failure=None), evidence=[])
        runner.write_frozen(out / (identity + '.json'), record)
        records.append(record)
    ledger = runner.Ledger(out / 'transport-ledger.json')
    seen = []

    def handler(request):
        body = json.loads(request.content)
        assert body['store'] is False and 'previous_response_id' not in body and 'tools' not in body
        assert body['model'] == 'gpt-6-luna' and body['max_output_tokens'] == 8192
        seen.append(body)
        packets = json.loads(body['input'])['packets']
        ratings = [dict(scenario_id=p['scenario_id'], rating=dict(
            units=[dict(unit_id=u['unit_id'], judgment='present', reason='Authored MOCK rating only.',
                        critical_error=False) for u in p['units']], missingness_correct=True,
            missingness_reason='Authored MOCK only.', critical_error=False, additional_issues=[])) for p in packets]
        return httpx2.Response(200, json=dict(id='authored_judge_response', status='completed',
            model='gpt-6-luna', usage=dict(input_tokens=5, output_tokens=5, total_tokens=10),
            output=[dict(type='message', role='assistant', content=[dict(type='output_text',
                    text=json.dumps(dict(ratings=ratings)))])]))

    transport_class = runner.Metered
    monkeypatch.setattr(runner, 'Metered', lambda ledger, phase, identity:
        transport_class(ledger, phase, identity, httpx2.MockTransport(handler)))
    _, ratings, _ = asyncio.run(runner.judge(records, settings, ledger, freeze, out))
    assert len(ratings) == 3 and len(seen) == len(ledger.value['attempts']) == 1
    asyncio.run(runner.judge(records, settings, ledger, freeze, out))
    assert len(seen) == 1


def test_new_history_and_controlled_no_guidance_fixture_semantics(tmp_path, monkeypatch):
    from fraudlens.investigation.context import HistoryReader
    from fraudlens.investigation.retrieval import search
    inputs, _, _, knowledge, versions, freeze = prepared(tmp_path, monkeypatch)
    item = inputs[0]
    reader = HistoryReader(**item['history_fixture'])
    history = reader.read(item['context'], 'sender')
    assert history['eligible_count'] == 2 and history['coverage'] == 'incomplete'
    assert history['totals'] == dict(EUR='320.10', USD='75.20')
    assert reader.read(item['context'], 'receiver')['availability'] == 'unavailable'
    assert search(knowledge, 'missing evidence', freeze['corpus_version'],
                  versions['controlled_no_match'])['status'] == 'no_match'
