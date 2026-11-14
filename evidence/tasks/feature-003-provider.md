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
