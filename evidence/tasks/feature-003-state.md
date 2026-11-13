# T009/T010 storage invariants
Date 2026-11-14 Europe/Belgrade; started 2026-11-13. Branch feature03; baseline 6db94af3471a9007a8a0d88cba8c7ece32886483; initial tree clean.
Prompt: ../../prompts/development/003-investigation-phase-02.md. Human review pending.

Initial RED: 6 executed failures, NotImplementedError in importable repository
initializer; no collection/environment errors. Initial GREEN 6 passed.
Additional regression found request replay returned current revision instead of
saved original response: 1 failed assertion, then persisted response with request
identity fixed it. Test keys changed to valid authored UUIDs to respect API contract.
A missing reserve_tool primitive produced 1 AttributeError RED; minimal transactional
reservation now limits to 12 validated argument records, without executing tools.

SQLite schema v1, 500ms busy timeout, foreign keys, parameterized values, immutable
context/evidence/report/review/audit/request records, actor/operation/key identity,
state revision CAS, atomic disposition+audit and pre-I/O dispatch intent. A worker
claim is global and expires within 120 seconds; no external calls inside transactions.
8 dispatch / 12 tool reservation limits tested. Claims tested from independent
connections/threads; second claimant rejected. Unknown schema file unchanged.
No producer store opened; tests create dedicated files only under .cache.
This is a primitive repository, not worker/recovery or full report/quote validation.

Command: `uv run --locked pytest backend/tests/integration/test_investigation_store.py --basetemp D:\AIBootcamp\capstone\.cache\003-p2-b9fb3cccc98448598f241fbf0fcf20b9 -o cache_dir=D:\AIBootcamp\capstone\.cache\003-p2-cache-b9fb3cccc98448598f241fbf0fcf20b9 --tb=short -q`

Exit 0.

```text
........                                                                 [100%]
8 passed in 0.97s
```
