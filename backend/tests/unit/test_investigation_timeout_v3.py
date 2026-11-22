"""Timeout/retry/quota regressions: authored fixtures and actual SDK mocks only."""
import asyncio
import json

import httpx2
import pytest
from test_investigation_openai import LIMITS, run
from test_investigation_workflow import create
from test_investigation_workflow import runtime as workflow_runtime

from fraudlens.investigation.provider import OpenAIProvider, ProviderError, ScriptedProvider
from fraudlens.investigation.settings import InvestigationSettings

runtime = workflow_runtime


def test_sdk_outer_request_timeout_is_retryable_and_unknown():
    async def slow(request):
        await asyncio.sleep(2)
        pytest.fail('Timed-out transport not cancelled')
    with pytest.raises(ProviderError) as caught:
        run(slow, limits={**LIMITS, 'request_timeout': .02})
    error = caught.value
    assert error.code == 'provider_failure' and error.retryable and error.outcome_unknown
    assert getattr(error, 'diagnostic', {}) == dict(reason='request_timeout')


@pytest.mark.parametrize('code', ['insufficient_quota', 'credit_balance_exhausted',
    'organization_usage_limit_exceeded', 'organization_spend_limit_exceeded',
    'project_spend_limit_exceeded', 'usage_limit_exceeded'])
def test_known_quota_or_credit_429_is_not_retried(code):
    with pytest.raises(ProviderError) as caught:
        run(lambda request: httpx2.Response(429, json=dict(error=dict(
            code=code, type='insufficient_quota', message='AUTHORED-PRIVATE-ERROR'))))
    error = caught.value
    assert not error.retryable and not error.outcome_unknown
    assert getattr(error, 'diagnostic', {}) == dict(reason='quota_exhausted', http_status=429, provider_code=code)
    assert 'AUTHORED-PRIVATE-ERROR' not in str(error)


def test_quota_type_with_unknown_code_does_not_leak_or_retry():
    with pytest.raises(ProviderError) as caught:
        run(lambda request: httpx2.Response(429, json=dict(error=dict(
            code='AUTHORED-PRIVATE-CODE', type='insufficient_quota', message='AUTHORED-PRIVATE-MESSAGE'))))
    error = caught.value
    assert not error.retryable
    assert getattr(error, 'diagnostic', {}) == dict(reason='quota_exhausted', http_status=429)
    assert 'AUTHORED-PRIVATE' not in json.dumps(getattr(error, 'diagnostic', {}))


def test_short_rate_limit_keeps_one_retry_and_safe_code():
    with pytest.raises(ProviderError) as caught:
        run(lambda request: httpx2.Response(429, headers={'retry-after': '1'},
            json=dict(error=dict(code='rate_limit_exceeded', type='rate_limit_error', message='PRIVATE'))))
    error = caught.value
    assert error.retryable and error.retry_after == 1
    assert getattr(error, 'diagnostic', {}) == dict(reason='rate_limit', http_status=429,
                                                   provider_code='rate_limit_exceeded')


def test_one_request_timeout_recovers_and_keeps_unknown_dispatch(runtime):
    class OnceSlow(ScriptedProvider):
        first = True

        async def next_turn(self, *args):
            if self.first:
                self.first = False
                await asyncio.sleep(10)
            return await super().next_turn(*args)

    _, request, make = runtime
    service = make(provider=OnceSlow(), settings=InvestigationSettings(
        request_timeout_seconds=1, total_timeout_seconds=4))
    run_view = create(service, request)
    result = asyncio.run(service.work_once())
    assert result['state'] == 'ready_for_review'
    assert result['budget']['provider_requests'] == 5 and result['budget']['transient_retries'] == 1
    events = service.events(run_view['attempt_id'])
    failed = [e for e in events if e['operation'] == 'dispatch_result' and e['outcome'] == 'unknown']
    assert len(failed) == 1 and failed[0]['diagnostic']['reason'] == 'request_timeout'
    with service.repo.connection() as db:
        outcomes = db.execute('SELECT outcome FROM provider_dispatches WHERE attempt_id=? ORDER BY sequence',
                              (run_view['attempt_id'],)).fetchall()
    assert outcomes == [('unknown',)] + [('completed',)] * 4


def test_repeated_timeouts_stop_after_one_retry(runtime):
    class AlwaysSlow:
        async def next_turn(self, *args):
            await asyncio.sleep(10)

    _, request, make = runtime
    service = make(provider=AlwaysSlow(), settings=InvestigationSettings(
        request_timeout_seconds=1, total_timeout_seconds=4))
    run_view = create(service, request)
    result = asyncio.run(service.work_once())
    assert result['state'] == 'failed' and result['failure']['code'] == 'provider_failure'
    assert result['failure']['outcome_unknown'] is True
    assert result['budget']['provider_requests'] == 2 and result['budget']['transient_retries'] == 1
    assert service.events(run_view['attempt_id'])[-2]['operation'] in ('failure', 'transition')


def test_total_attempt_timeout_remains_budget_exhausted_without_retry(runtime):
    class Slow:
        async def next_turn(self, *args):
            await asyncio.sleep(10)

    _, request, make = runtime
    service = make(provider=Slow(), settings=InvestigationSettings(total_timeout_seconds=1))
    run_view = create(service, request)
    result = asyncio.run(service.work_once())
    assert result['failure']['code'] == 'budget_exhausted'
    assert result['failure']['outcome_unknown'] is True
    assert result['budget']['provider_requests'] == 1 and result['budget']['transient_retries'] == 0
    failures = [e for e in service.events(run_view['attempt_id']) if e['operation'] == 'failure']
    assert failures[-1]['diagnostic']['reason'] == 'attempt_timeout'


def test_timeout_in_last_request_slot_does_not_reserve_retry(runtime):
    class Slow:
        async def next_turn(self, *args):
            await asyncio.sleep(10)

    _, request, make = runtime
    service = make(provider=Slow(), settings=InvestigationSettings(
        max_provider_requests=1, request_timeout_seconds=1, total_timeout_seconds=4))
    create(service, request)
    result = asyncio.run(service.work_once())
    assert result['failure']['code'] == 'provider_failure'
    assert result['budget']['provider_requests'] == 1 and result['budget']['transient_retries'] == 0


def test_sdk_quota_failure_is_private_audited_and_never_retried_by_workflow(runtime):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx2.Response(429, json=dict(error=dict(code='credit_balance_exhausted',
            type='insufficient_quota', message='AUTHORED-PRIVATE-QUOTA-BODY')))

    provider = OpenAIProvider('AUTHORED-NOT-REAL', 'explicit-test-model', transport=httpx2.MockTransport(handler))
    _, request, make = runtime
    service = make(provider=provider)
    run_view = create(service, request)
    result = asyncio.run(service.work_once())
    assert len(seen) == result['budget']['provider_requests'] == 1
    assert result['budget']['transient_retries'] == 0 and result['failure']['code'] == 'provider_failure'
    events = service.events(run_view['attempt_id'])
    failure = next(e for e in events if e['operation'] == 'failure')
    assert failure['diagnostic'] == dict(reason='quota_exhausted', http_status=429,
                                         provider_code='credit_balance_exhausted')
    assert 'diagnostic' not in result['failure']
    assert 'AUTHORED-PRIVATE-QUOTA-BODY' not in json.dumps(events)


def test_diagnostic_boundary_rejects_arbitrary_error_fields():
    error = ProviderError('provider_failure', diagnostic=dict(reason=['PRIVATE'],
        http_status=True, provider_code={'private': 'secret'}, message='AUTHORED-PRIVATE-MESSAGE'))
    assert error.diagnostic == {}
