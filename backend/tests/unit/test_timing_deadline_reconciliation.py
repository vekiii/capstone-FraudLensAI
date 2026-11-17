"""Current total-deadline behavior, not a diagnosis of the historical outlier."""

import asyncio
import time

from test_investigation_workflow import create, runtime  # noqa: F401

from fraudlens.investigation.provider import ProviderError
from fraudlens.investigation.settings import InvestigationSettings


def test_retry_backoff_cannot_start_another_request_after_total_expiry(runtime):  # noqa: F811
    class Transient:
        calls = 0

        async def next_turn(self, *args):
            self.calls += 1
            raise ProviderError("provider_failure", retryable=True, retry_after=2)

    _, request, make = runtime
    provider = Transient()
    service = make(provider=provider, settings=InvestigationSettings(total_timeout_seconds=1))
    attempt = create(service, request)
    started = time.monotonic()
    result = asyncio.run(service.work_once())
    assert time.monotonic() - started < 3
    assert provider.calls == 1
    assert result["state"] == "failed"
    assert result["failure"]["code"] == "budget_exhausted"
    assert result["budget"]["provider_requests"] == 1
    assert result["budget"]["transient_retries"] == 1
    assert service.read(attempt["attempt_id"])["state"] == "failed"


def test_expired_request_and_slow_cleanup_share_total_budget(runtime):  # noqa: F811
    class Slow:
        calls = 0

        async def next_turn(self, *args):
            self.calls += 1
            await asyncio.sleep(10)

        async def aclose(self):
            await asyncio.sleep(10)

    _, request, make = runtime
    provider = Slow()
    service = make(provider=provider, settings=InvestigationSettings(total_timeout_seconds=1))
    attempt = create(service, request)
    started = time.monotonic()
    result = asyncio.run(service.work_once())
    assert time.monotonic() - started < 3
    assert result["state"] == "failed" and result["failure"]["outcome_unknown"] is True
    assert provider.calls == 1 and result["budget"]["transient_retries"] == 0
    assert any(
        e["operation"] == "provider_cleanup" and e["status"] == "timeout"
        for e in service.events(attempt["attempt_id"])
    )
    assert service.read(attempt["attempt_id"])["state"] == "failed"
