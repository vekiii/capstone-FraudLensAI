"""New live adapter's stop/privacy guards; no external network or real key."""
import asyncio
import importlib.util
import sys
from pathlib import Path

import httpx2
import pytest

from fraudlens.investigation.settings import InvestigationSettings

PATH = Path(__file__).resolve().parents[3] / 'evidence/tasks/feature-003-timeout-v3.py'
SPEC = importlib.util.spec_from_file_location('timeout_v3_adapter', PATH)
adapter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adapter)


@pytest.mark.parametrize('blocked_index', [0, 2])
def test_credit_error_stops_further_cases_and_judge_even_on_final_case(tmp_path, monkeypatch, blocked_index):
    out = tmp_path / 'run'
    monkeypatch.setattr(adapter, 'OUT', out)
    monkeypatch.setattr(adapter.core, 'load_settings', lambda: InvestigationSettings(
        provider='openai', model='gpt-6-luna', api_key='AUTHORED-NOT-REAL'))
    monkeypatch.setattr(sys, 'argv', ['timeout-v3.py', '--execute'])
    calls = []

    async def generate(inputs, protocol, settings, knowledge, versions, freeze, ledger, out):
        item = inputs[0]
        calls.append(item['id'])
        ledger.reserve('generation', item['id'])
        blocked = len(calls) == blocked_index + 1
        return [dict(id=item['id'], seconds=.01,
            result=dict(state='failed' if blocked else 'needs_information',
                budget=dict(transient_retries=0),
                failure=dict(code='provider_failure') if blocked else None),
            events=[dict(operation='failure', diagnostic=dict(reason='quota_exhausted'))] if blocked else [])]

    async def forbidden(*args, **kwargs):
        pytest.fail('Quota rejection must stop new judge calls')

    monkeypatch.setattr(adapter.core, 'generate', generate)
    monkeypatch.setattr(adapter.core, 'judge', forbidden)
    assert asyncio.run(adapter.main()) == 0
    summary = adapter.verify_seal(adapter.core.load(out / 'summary.json'))
    assert summary['stopped_for'] == 'quota_exhausted'
    assert summary['passing_development_reports'] is None and summary['judge_status'] == 'not_run'
    assert len(calls) == blocked_index + 1
    assert len(summary['not_executed_ids']) == 2 - blocked_index


def test_only_validated_numeric_rate_headers_enter_ledger(tmp_path):
    ledger = adapter.core.Ledger(tmp_path / 'ledger.json')
    transport = adapter.DiagnosticMetered(ledger, 'generation', 'DEV3-721', httpx2.MockTransport(
        lambda request: httpx2.Response(200, headers={
            'x-ratelimit-remaining-requests': '123', 'x-ratelimit-limit-tokens': 'AUTHORED-PRIVATE',
            'authorization': 'AUTHORED-PRIVATE'}, json={})))

    async def exercise():
        response = await transport.handle_async_request(httpx2.Request('POST', 'https://example.invalid', content=b'{}'))
        await response.aclose()
        await transport.aclose()

    asyncio.run(exercise())
    assert ledger.value['attempts'][0]['rate_headers'] == {'x-ratelimit-remaining-requests': 123}
    assert 'AUTHORED-PRIVATE' not in ledger.path.read_text()


def test_cancelled_transport_attempt_remains_unknown_and_is_counted(tmp_path):
    ledger = adapter.core.Ledger(tmp_path / 'ledger.json')

    async def slow(request):
        await asyncio.sleep(10)

    transport = adapter.DiagnosticMetered(ledger, 'generation', 'DEV3-721', httpx2.MockTransport(slow))

    async def exercise():
        with pytest.raises(TimeoutError):
            async with asyncio.timeout(.01):
                await transport.handle_async_request(httpx2.Request('POST', 'https://example.invalid', content=b'{}'))
        await transport.aclose()

    asyncio.run(exercise())
    assert len(ledger.value['attempts']) == 1
    item = ledger.value['attempts'][0]
    assert item['outcome'] == 'unknown' and item['error_type'] == 'CancelledError'


def test_recovered_rate_limit_does_not_block_later_cases():
    record = dict(result=dict(state='needs_information', failure=None),
                  events=[dict(diagnostic=dict(reason='rate_limit'))])
    assert adapter.blocked_reason(record) is None
