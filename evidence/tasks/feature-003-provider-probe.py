"""One authorized existing CLI probe; metadata only, never request/response bodies."""
import contextlib
import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx2

from fraudlens.investigation import provider
from fraudlens.investigation.cli import main
from fraudlens.investigation.settings import load_settings

settings = load_settings()
if (settings.model.get_secret_value() != 'gpt-6-luna'
        or not settings.api_key.get_secret_value().strip()):
    raise SystemExit('Expected private key/model configuration unavailable; no dispatch.')

result_path = Path('.cache/t033-provider-result.json')
previous = json.loads(result_path.read_text(encoding='utf-8')) if result_path.exists() else None
previous_attempts = ((previous.get('previous_transport_attempts', 0) + len(previous['sdk_requests']))
                     if previous else 0)
if previous:
    Path('.cache/t033-provider-first-result.json').write_text(
        json.dumps(previous, indent=2) + '\n', encoding='utf-8')
record = dict(started_at=datetime.now(timezone.utc).isoformat(),
              requested_model=settings.model.get_secret_value(),
              sdk_requests=[], maximum_requests=2,
              previous_transport_attempts=previous_attempts, completed_turns=[])
original = provider._bounded_transport
original_turn = provider.OpenAIProvider.next_turn


async def observed_turn(self, *args, **kwargs):
    turn = await original_turn(self, *args, **kwargs)
    record['completed_turns'].append(dict(kind=turn.kind, returned_model=turn.returned_model,
                                        request_id=turn.request_id, usage=turn.usage))
    return turn


provider.OpenAIProvider.next_turn = observed_turn


class MeteredTransport(httpx2.AsyncBaseTransport):
    def __init__(self, inner):
        self.inner = inner

    async def handle_async_request(self, request):
        if previous_attempts + len(record['sdk_requests']) >= 2:
            raise provider.ProviderError('budget_exhausted')
        item = dict(sequence=previous_attempts + len(record['sdk_requests']) + 1)
        record['sdk_requests'].append(item)
        started = time.monotonic()
        try:
            response = await self.inner.handle_async_request(request)
            item.update(http_status=response.status_code,
                        request_id=response.headers.get('x-request-id'))
            return response
        except Exception as exc:
            item['transport_error_type'] = type(exc).__name__
            raise
        finally:
            item['headers_elapsed_seconds'] = round(time.monotonic() - started, 3)

    async def aclose(self):
        await self.inner.aclose()


provider._bounded_transport = lambda inner: original(MeteredTransport(inner))
captured = io.StringIO()
started = time.monotonic()
with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(io.StringIO()):
    try:
        record['cli_exit_code'] = main(['probe-provider', '--synthetic-only'])
    except Exception as exc:
        record.update(cli_exit_code=1, unexpected_error_type=type(exc).__name__)
record['elapsed_seconds'] = round(time.monotonic() - started, 3)
try:
    record['cli_result'] = json.loads(captured.getvalue())
except ValueError:
    record['cli_result'] = {'status': 'no_json_result'}
record['completed_at'] = datetime.now(timezone.utc).isoformat()
safe = json.dumps(record, indent=2)
Path('.cache/t033-provider-result.json').write_text(safe + '\n', encoding='utf-8')
print(safe)
raise SystemExit(record['cli_exit_code'])
