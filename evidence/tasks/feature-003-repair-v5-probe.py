"""One opt-in synthetic capability probe, capped at two transports with no replay."""
import argparse
import asyncio
import hashlib
import json
from datetime import UTC, datetime

import httpx2

from fraudlens.investigation.models import ROOT, canonical
from fraudlens.investigation.provider import ProviderError, compile_report_schema, probe_provider
from fraudlens.investigation.settings import load_settings

OUT = ROOT / '.cache/repair-v5-synthetic-probe'


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


async def execute():
    settings = load_settings()
    if settings.model.get_secret_value() != 'gpt-6-luna' or not settings.api_key.get_secret_value():
        raise ValueError('Expected configured model and key required')
    OUT.mkdir(parents=True, exist_ok=True)
    freeze = dict(started_at=datetime.now(UTC).isoformat(), model='gpt-6-luna', maximum_transports=2,
        kind='synthetic_capability_not_report_quality',
        schema_sha256=hashlib.sha256(canonical(compile_report_schema())).hexdigest(),
        provider_sha256=hashlib.sha256((ROOT / 'backend/src/fraudlens/investigation/provider.py')
                                     .read_bytes().replace(b'\r\n', b'\n')).hexdigest())
    # Exclusive marker before any transport construction: interrupted work cannot replay.
    with (OUT / 'freeze.json').open('x', encoding='utf-8') as stream:
        json.dump(freeze, stream, indent=2)
    attempts = []

    class Metered(httpx2.AsyncBaseTransport):
        def __init__(self):
            self.inner = httpx2.AsyncHTTPTransport(retries=0)

        async def handle_async_request(self, request):
            if len(attempts) >= 2:
                raise ProviderError('budget_exhausted')
            item = dict(sequence=len(attempts) + 1, status='unknown', input_bytes=len(request.content))
            attempts.append(item)
            write(OUT / 'transport-ledger.json', attempts)
            result = await self.inner.handle_async_request(request)
            item.update(status='headers_received', http_status=result.status_code)
            write(OUT / 'transport-ledger.json', attempts)
            return result

        async def aclose(self):
            await self.inner.aclose()

    try:
        value = await probe_provider(settings, transport=Metered())
        assert value['status'] == 'capability_probe_passed'
        result = dict(status='PASS', capability=value)
    except ProviderError as error:
        result = dict(status='FAIL', code=error.code, outcome_unknown=error.outcome_unknown,
                      diagnostic=error.diagnostic)
    result.update(freeze=freeze, finished_at=datetime.now(UTC).isoformat(),
                  transport_attempts=len(attempts), transports=attempts, report_quality_evaluated=False,
                  spend=None)
    write(OUT / 'result.json', result)
    write(ROOT / 'evidence/tasks/feature-003-repair-v5-probe-results.json', result)
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if not args.execute:
        parser.error('--execute required; never replay an existing freeze')
    raise SystemExit(asyncio.run(execute()))
