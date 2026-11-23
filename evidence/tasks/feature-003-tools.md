# T023/T024 controlled tool execution - 2026-11-14

Branch feature03, baseline 1a99c34, initially clean. Scope Phase 4;
[original request](../../prompts/development/003-investigation-phase-04.md).
Local speckit-implement workflow used: feature explicitly selected, prerequisite
script succeeds via child PowerShell -ExecutionPolicy Bypass (initial direct
invocation blocked by script execution policy; machine policy unchanged).
requirements.md 16/16 checked, 0 unchecked; no extensions.yml or hooks.

Executed T023 RED: 23 assertion/NotImplementedError failures against an importable
tool boundary; no import/collection failure. T024 GREEN: tools 23 + existing
store 8 = 31 PASS. Ruff backend PASS. Commands use `py -3.14 -m uv run --locked
--offline pytest` with unique .cache absolute --basetemp/cache_dir and module
paths backend/tests/unit/test_investigation_tools.py and
backend/tests/integration/test_investigation_store.py.

Exactly three strict closed tools; context bound to persisted attempt and worker
lease; reserve execution before reading, <=12 calls, duplicate call-ID rejection.
Rejected scope/arguments audited without arbitrary input; completed/failed
outcomes and evidence refs persisted. Evidence/outcome commit atomically and
late/expired worker commits reject. History <=50 events, per-currency full
permitted-lookback totals labeled, explicit unavailable vs empty state. Exact
aliases replace account/bank identity outbound. Procedure text/provenance is
archived locally; provider projection excludes reviewer identity. <=5 passages,
explicit no-match, <=16000 UTF-8 result bytes; remove only whole events/passages,
fail individual oversized facts without clipping.

Narrow URL/path/SQL/scope-changing query rejection is defense in depth, not a
general injection detector. Returned source prose remains untrusted data and
cannot execute code/change application permissions. No provider/workflow/UI
execution or actual dataset integration claimed by these tool tests.
