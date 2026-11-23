# Timeout/quota v3 maintenance — 2026-11-16

Completed: runtime timeout/quota fix, new live development run and integrity audit.
Preparation history follows, then actual results. Branch feature03-reliability-v2,
baseline46a15ed, initially clean.
[Request](../../prompts/development/003-timeout-v3-2026-11-16.md),
[design/protocol](../../specs/003-ai-investigation/timeout-v3.md).
No commit/push or .env/dependency/model/public-contract changes in this follow-up.

Saved v2 dispatch5 had no headers for29.987s, then attempt failed37.971s after5
requests: per-request timer expiration is supported, underlying provider/network
cause and usage remain unknown. No evidence of a credit rejection in that trace.
Original failed output and all10 local v2 JSON artifacts are hash-preserved.

Implemented consistency fix: provider asyncio timer and workflow timer now map a
single-request timeout to retryable provider_failure, like SDK APITimeoutError.
At most ONE existing transient retry, only with time/request slots left. Persist
unknown first dispatch before retry, preserve potential duplicate provider spend.
Total attempt expiry remains budget_exhausted, no retry and no late lease writes.
Ceilings remain8requests/12tools/30s per request/120s total, same prompt/schema.

Known credit/billing/spend/usage codes and insufficient_quota error type now stop
without retry; ordinary429 rate limits remain bounded by one retry and<=2s delay.
Private allowlisted diagnostics record reason/status/known code, never raw error
text/arbitrary headers. Public Failure JSON/codes unchanged. Official error-code
and billing documentation consulted; installed SDK exception fields inspected.
User's reported several-hour reset does not establish account quota/reset values.

## Executed preparation verification

Scoped speckit-implement workflow, feature003 explicitly selected, prerequisites
PASS via child PowerShell -ExecutionPolicy Bypass, checklist16/16, no hooks.
Initial RED **13 failed**, intended assertions for timeout classification/recovery,
quota retry and missing private diagnosis. GREEN with existing workflow/SDK/recovery
checks **58 PASS**. Added quota-through-workflow/privacy guards: full backend
**848 PASS in60.09s**. New adapter stop/header/cancellation guards and timeout
module together **20 PASS**; final adapter-only repeat after metadata edit5 PASS.
Final complete suite including adapter checks: **853 PASS in59.75s**, exit0:
`.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short --basetemp=.cache/timeout-v3/final-full-tmp -o cache_dir=.cache/timeout-v3/final-full-cache`.
Ruff/diff PASS. Existing Python3.14.7/SDK3.51.0 used; no installation.

New v3 adapter reuses unchanged v2 runner functions with explicit separate paths,
IDs and ledger. Three NEW instances of development templates, not independent
cases/holdout. Amounts/time/accounts/scores/history totals changed; references
authored separately. All instructions/language metadata sr-Latn. v2 inputs only
used as templates; no v2 reference/output prose used in generation. First case
incomplete two-currency history, second unavailable history, third controlled
no-guidance cutoff. Core source/prompt/candidate unchanged except timeout fix.

Default prepare actually returned frozen_not_dispatched,3cases,max25. Separate
25-attempt cap (8/case+1judge), all failures count; no use of old unused8 attempts.
Whole batch stops after reported quota/credit/access/rate-limit failure, including
skipping judge on a final-case quota error. No hours-long automatic wait. The
runtime's one bounded transient retry remains allowed. No model switch or tuning
between cases. Generation references remain inaccessible until all outputs seal.

Commands executed:

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
powershell -NoProfile -ExecutionPolicy Bypass -File .specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_investigation_timeout_v3.py -q --tb=short --basetemp=.cache/timeout-v3/red-tmp -o cache_dir=.cache/timeout-v3/red-cache
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_investigation_timeout_v3.py backend/tests/unit/test_investigation_workflow.py backend/tests/unit/test_investigation_openai.py backend/tests/integration/test_investigation_recovery.py -q --tb=short --basetemp=.cache/timeout-v3/green-tmp -o cache_dir=.cache/timeout-v3/green-cache
.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short --basetemp=.cache/timeout-v3/full-tmp -o cache_dir=.cache/timeout-v3/full-cache
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_investigation_timeout_v3_runner.py backend/tests/unit/test_investigation_timeout_v3.py -q --tb=short --basetemp=.cache/timeout-v3/guards-tmp -o cache_dir=.cache/timeout-v3/guards-cache
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-timeout-v3-inputs.py
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-timeout-v3.py
```

Human code review, independent reference review, producer integration and final
feature Converge remain pending. No improvement or live recovery claim from mocks;
fresh live outcomes will be recorded below without replacing previous failures.

## Actual live v3 execution

Executed once after freeze, exit0; no implementation/prompt/config changes between
cases. Model gpt-6-luna returned on all16 completed requests. **16/25 attempts**:
15 generation +1 stateless same-model batch judge, all HTTP200. No unknown usage,
quota/credit errors, actual request timeouts or transient retries in this batch.
The new timeout recovery is demonstrated by tests, not an observed live retry.

```powershell
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-timeout-v3.py --execute
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-timeout-v3.py --audit
```

| Case | Local validation / state | Seconds | Requests/tools/retries | Automated factual support | Essential coverage | Raw machine pass |
|---|---|---:|---|---|---|---|
| DEV3-721 incomplete multi-currency history | valid needs_information |32.617|5/4/0|4/4|5/7 (71.43%)|FAIL|
| DEV3-722 unavailable history | valid needs_information |23.739|5/4/0|4/4|3/5 (60%)|FAIL|
| DEV3-723 controlled no-guidance | valid needs_information |20.798|5/4/0|3/3|3/6 (50%)|FAIL|

Zero repairs. All3 valid drafts within90s and all3 terminal within120s. Technical
completion3/3 is distinct from **raw automated semantic pass0/3**. On these drafts
only,11/11 rated observational units supported,11/18 essential units present;
4/4 procedural units applicable across721/722,723 has0 procedural units (N/A).
Judge reported no critical unsupported claims. Missingness true on721/723, false
on722 due omission of an explicit human-final-authority limitation.

Most missing-coverage reasons concern explicit transaction IDs, transfer-not-bank-
loss and score-not-guilt disclaimers, and a negative no-invented-identity statement.
The predeclared essential items combine positive facts with required negative
wording; this is an assistant-authored, unreviewed development rubric. Therefore
its literal coverage scores are not a general report-quality estimate.

### Disputed judge interpretation, raw scores preserved

On723 the judge additionally treats the draft outcome needs_information as an
unsupported information-request disposition. Agent review disputes this against
the declared workflow semantics: a draft outcome is not a human disposition.
Actual saved run has review=null, zero analyst_review events and zero
recommended_checks. No intervention/review occurred. The same interpretation also
affected E06 coverage. Preserve original ratings and mark the issue disputed;
no second judge, rerating or post-hoc score correction. Coverage on723 would still
be below80% even if that single essential item were accepted. No automatic pass.

Known reported usage **68,484 input +13,734 output =82,218 tokens**; unknown-usage
attempts0; actual spend unknown. Judge timing is not included in case latencies.
Unused9 attempts are not a reason to regenerate or rerate. Old0/8 and all other
original failed release metrics remain unchanged. New cases/template instances
and single-judge method do not support a comparable before/after improvement claim.

## Audit and final status

Audit PASS, exit0. [Safe machine record](feature-003-timeout-v3-results.json)
preserves raw machine flags and hashes. Runtime/new protocol, inputs, separate
references and runner hashes match pre-dispatch freeze. All10 old local v2 JSON
files hash-match their prior bytes (LF-normalized policy); none rewritten. No
API calls made by audit. Additional offline validation rechecked all3 saved
report IDs/schema/reference/exact-fact binding; **13 cited evidence IDs resolve**.

853 full backend PASS,20 targeted timeout/adapter checks PASS, Ruff/diff PASS.
Frontend unchanged; no fresh frontend/browser run claimed. Private .env unchanged;
no key/raw output/SQLite/opaque reasoning added to Git. No commit/push this turn.
Local milan/feature03-provere-v2.md updated with offline timeout checks; **156 lines**,
still ignored by the existing local exclusion. The old guide144-line claim remains
historical, not its current size.

T076–T078 complete for this maintenance/check scope. Not full feature acceptance.
Human code review/independent reference review, producer integration, T066/T067
remain pending. Next concrete step: review/atomize development coverage expectations
and correct the judge's draft-state/disposition distinction under a NEW versioned
protocol, then plan a separate live quality check. Do not rewrite/rerun v2 or v3.
