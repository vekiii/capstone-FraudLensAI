# Phase 4 provider boundary - 2026-11-14

Baseline feature03 1a99c34. T027 RED: 15 executed failures on importable
NotImplementedError boundary. T028 GREEN: 15 PASS. Protocol is asynchronous for
cancellable provider waits; test helper awaits each call. Scripted provider is
explicitly authored TEST output, not model evaluation. Three ordered tool types,
preserved call IDs, grounded/needs-information/invalid-citation scenarios and
explicit refusal/incomplete outcomes. Per-turn projection checks initial context
and subsequent results for closed allowlisted fields, no raw source/labels/
reviewer notes, result/input/output limits. Private continuation is a separate
field, empty for the authored provider. No client/network initialization calls.
Backend Ruff PASS; combined tools/repository/reports/provider/workflow 86 PASS.

## Interrupted SDK preparation and recovery

T031/T032 adapter work is NOT complete. First `uv add openai` inside sandbox
failed connecting to PyPI (socket Access denied). Authorized network execution
resolved openai 3.51.0 but download/cache rename failed with Windows Access denied.
A subsequent installer attempt was interrupted by the user's reported sudden
computer shutdown. No conclusion about the shutdown cause is established.

After restart: Git remains feature03 / 1a99c34, all prior edits present, no SDK
dependency/lock changes from the failed installs. No stale uv/node/chrome process
was found by the targeted process check. Fresh full backend: 595 PASS / 3 existing
T035 failures; Ruff PASS; default SQLite integrity_check returns ok.

`py -3.14 -m uv add openai --no-sync`, with isolated
UV_CACHE_DIR=.cache/uv-phase04-recovery, succeeded (48 resolved packages, exit 0).
This records a mechanical dependency/lock step, not T031/T032 completion.
Installation retry uses --locked --group dev --no-cache --link-mode copy,
workspace-local TEMP/TMP and single download/install/build concurrency.
Installation outcome and actual installed version must be verified separately.
No model/API call, key read or live capability/quality claim.

Primary SDK design sources inspected (implementation must match installed code):
[official SDK](https://github.com/openai/openai-python),
[HTTPX2 migration](https://github.com/openai/openai-python/blob/main/httpx2.md),
[strict structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs),
[conversation state](https://developers.openai.com/api/docs/guides/conversation-state).

## T031/T032 completed offline, 2026-11-15 Europe/Belgrade

Supersedes the interrupted-install status above. Baseline fece114 already tracked
openai >=3.51.0 and generated uv.lock. The user installed the locked SDK manually
with exit 0 before this continuation; no installer was repeated. Actual imports
and MockTransport tests use OpenAI **3.51.0**, httpx2/httpcore2 **2.16.0**.

Executed RED: 16 SDK tests against an importable NotImplementedError adapter.
GREEN: 16 PASS. Subsequent malformed-envelope checks observed two real REDs:
non-dict message part caused AttributeError; non-string model passed through.
Both now produce typed provider_incomplete; SDK module **18 PASS**. Probe command
RED: 2 missing-command failures plus one passing authored HTTP exchange; GREEN:
initial **3 PASS**. Additional CLI RED: capability failure was hidden behind a
generic message. It now emits a safe typed JSON code/outcome_unknown; probe module
**4 PASS**. Combined with existing provider/workflow modules: 50 checks; all
are included in the final 629 PASS backend regression. Ruff PASS.

Official AsyncOpenAI, Responses API, explicit model ID, max_retries=0, parallel
tools=false, store=false, strict closed tools/report shape. Schema compiler
inlines reachable local definitions and explicitly leaves conditional outcome
rules to the unchanged local schema/semantic validator; it does not weaken local
acceptance. Required reasoning/function-call output items and call IDs are
replayed privately, never exposed as evidence or report prose.

All-turn allowlist runs before every dispatch. Entire payload (prompt/tools/schema/
private continuation) checked, and transport checks actual encoded request bytes
<=48,000 before network I/O. Output <=4096 tokens; <=30s request under shared <=120s
workflow deadline. Bounded response byte stream <=2 MiB applies to success AND
SDK error responses without Content-Length. Compression is refused; identity
encoding requested, avoiding unbounded decompression. Error messages never include
provider body/key. Access/refusal/incomplete/capability are explicit; at most one
workflow transient retry and one local-validator repair, with prior request budget
reservation. Usage/request/model come from actual response or remain unknown;
no price/spend inference. Clients close in finally. No environment proxy/redirect
fallback or model substitution.

`probe-provider --synthetic-only` uses only authored CASE-000 data, forces one
tool then a limitations-only strict report, max two SDK requests with all configured
smaller limits honored. Command requires explicit flag and key/model configuration;
tests use MockTransport and dummy keys only. **T033 capability pending**: a later
authorized 2026-11-15 probe used root .env/configured `gpt-6-luna`, first
ConnectError then actual HTTP 400 / unsupported_capability (two attempts total).
No completed turn, returned model or usage; no further requests. Configuration
now supports private root .env literals with process overrides and isolated tests;
fresh backend 636 PASS / Ruff PASS. See
[provider access](feature-003-provider-access.md). No provider capability/access,
live report or model-quality claim follows from mocked GREEN.
