# T033 actual provider probe: executed, capability gate PENDING

2026-11-15 Europe/Belgrade, branch `feature03`, baseline HEAD `8334b89`.
The user explicitly authorized only T033, local `.env` loading and at most two
API calls. No installation, embedding integration, Phase 5 work or Git publication.
Original request: [prompt](../../prompts/development/003-investigation-t033.md).

## Configuration and verification

Investigation settings now read the repository-root `.env` independently of cwd,
then overlay process variables, including explicitly empty values. No global
environment mutation; foundation `Settings`/`APP_MODE` remains unchanged. The
small standard-library reader accepts single-line `KEY=value` literals, optional
`export`, single/double quotes and comments. No interpolation, escape decoding,
shell execution or dependency changes. Missing file is optional; invalid or
unreadable file fails with a generic error that does not include values/lines.
Key/model remain excluded from settings repr/serialization. Merely loading a key
does not enable investigation or select the real provider.

All backend tests replace the local-file path with a temporary authored file, so
the real `.env` is never consulted by the default suite. Actual executed checks,
using the already installed `.venv` and OpenAI SDK **3.51.0**:

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_investigation_environment.py -q --tb=short --basetemp=.cache/t033-red -o cache_dir=.cache/pytest-t033-red
# RED: 6 failed / 1 passed; missing file loading and importable unimplemented reader.
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_investigation_environment.py backend/tests/unit/test_investigation_settings.py backend/tests/unit/test_investigation_probe.py backend/tests/unit/test_investigation_openai.py backend/tests/integration/test_startup.py backend/tests/integration/test_investigation_feature_toggle.py -q --tb=short --basetemp=.cache/t033-green -o cache_dir=.cache/pytest-t033-green
# GREEN: 125 passed.
.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short --basetemp=.cache/t033-regression -o cache_dir=.cache/pytest-t033-regression
# 636 passed in 18.77 seconds (629 existing + 7 configuration checks).
.venv/Scripts/python.exe -m ruff check backend
# All checks passed.
```

Frontend was not changed or rerun. Earlier 166 frontend tests/build/browser results
in the offline handoff are historical, not fresh T033 verification.
Final checks also passed: Ruff on the recorded instrumentation, `git diff --check`,
local Markdown links, two-attempt JSON reconciliation, branch/unchanged HEAD,
`.env` ignored/untracked and a private comparison of the loaded key against all
changed/untracked shareable files. No key match; no process key/model override
was present, confirming the actual probe configuration came from local `.env`.

## Actual bounded execution

The existing `cli.main(['probe-provider', '--synthetic-only'])` was executed with
the configured `OPENAI_MODEL=gpt-6-luna`; no model substitution or model-list call.
Only the existing authored CASE-000 diagnostic/tool definitions/report schema
were eligible for outbound delivery. No stored cases, corpus, references or real
customer data. Request cap, bounded transport, deadlines, `store=false`, strict
tools/report, `parallel_tool_calls=false` and SDK `max_retries=0` remain unchanged.

The [recorded instrumentation](feature-003-provider-probe.py) wraps the existing
transport/turn method solely to capture safe status, IDs, usage and elapsed time.
It enforces a **cumulative cap of two transport attempts**, counting even the
failed connection. No request/response body, authorization header or exception
message was printed or saved. Safe machine-readable results:
[both attempts](feature-003-provider-probe-results.json).

Executed from root, first sandboxed, then with sandbox escalation for network
access. The same script was invoked twice; it retained the first result and
reduced the remaining budget to one. Recorded script was copied from `.cache`
to evidence after execution; it must not be rerun as an automatic test.

```powershell
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe .cache/t033-run-provider.py
```

| Attempt | Local time (UTC+01:00) | Observed result |
|---|---|---|
| 1, sandboxed | 06:11:57-06:11:58 | `ConnectError`, no HTTP response; CLI exit 2, `provider_failure`, `outcome_unknown=true`; 1.080 s total |
| 2, escalated | 06:12:50-06:12:53 | HTTP **400**; CLI exit 2, `unsupported_capability`, `outcome_unknown=false`; 2.647 s total |

Actual request ID for attempt 2:
`req_740bf4ff71d9420d9decca768e058fd8`.
No completed provider turn, returned model ID or usage was available in either
result. Usage and spend remain **unknown**. Two transport attempts total, one
actual HTTP response; no third attempt, repair, SDK retry or fallback.

HTTP 400 is the actual provider rejection. The existing adapter maps 400/404/422
to `unsupported_capability`; because raw error bodies were deliberately not
retained, this evidence cannot identify the rejected parameter/schema or establish
whether `gpt-6-luna` itself is accessible. It does not prove the model lacks a
particular capability. Neither tool calling nor final report-schema support was
verified; no report-quality or human acceptance claim follows.

**Task status:** keep T033 unchecked. The authorized probe was performed, but the
required capability gate did not pass. Offline T034-T038 remain complete. Next
concrete step: separately authorize diagnosis of this HTTP 400 using the recorded
request ID; any new provider request needs a new explicit budget. Phase 5 remains
unstarted. No commit/push.
