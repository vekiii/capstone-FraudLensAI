# Coverage / calibrated judge v4 — 2026-11-16

Completed implementation, one live batch, calibration and audit. Preparation
history follows, then actual execution. Branch
feature03-reliability-v2 at46a15ed plus preserved uncommitted timeout-v3 work.
[Request](../../prompts/development/003-coverage-v4-2026-11-16.md),
[design](../../specs/003-ai-investigation/coverage-v4.md). No commit/push.

V3 raw scores0/3 and disputed state/disposition issue remain unchanged. V3 runtime
source was copied and hash-verified before this prompt-selection change under
ignored .cache/evidence-snapshots/timeout-v3. Old-source audits need that snapshot
or the corresponding revision, not the current runtime.20 local v2/v3 JSON result
artifacts are pinned by the new protocol and will be checked after execution.

## Implemented mechanics and calibration

Application prompt v3 explicitly requests supplied transaction identifiers,
exact money/time, source/score/version and permitted history counts/coverage/
per-currency totals. Distinguishes envelope keys from transaction IDs in claim
text. New attempts pin v3; retry preserves the parent's exact older prompt bytes.
No schema, model, provider limit or public contract changes. Timeout/quota fix kept.

Atomic positive essential facts are separate from mandatory required_disclosures.
Every disclosure still gates missingness_correct: synthetic/non-ML/uncalibrated/
not-guilt/not-loss/time provenance/history limitations/final human authority.
Unsupported inventions remain critical. >=90% factual support, >=80% coverage and
all conservative gates unchanged. Denominators/method changed: not a comparable
before/after measurement or correction to prior outcomes. Independent review pending.

Judge prompt v3 states that needs_information is draft insufficiency, not a human
disposition, and permits it without a procedure when recommended_checks is empty.
Semantic equivalence is accepted; absent readable facts remain missing. Three
authored controls use opaque CAL4-A/B/C and unit IDs: legitimate limited draft,
invented funds origin, missing human-authority disclosure. Expected labels stay
local, never in judge/generator input. All controls must match before calling
primary quality assessment valid. Failed calibration retains raw ratings but
passing_development_reports becomes unavailable, not a pass.

## Actual preparation verification

RED **10 failed**:9 calibration assertions at the unimplemented business gate and
the new prompt-binding assertion. No import/collection failures. GREEN **48 PASS**
with prior reliability/judge checks; focused calibration/adapter suite **17 PASS**.
Complete backend **870 PASS in56.20s**, exit0 (853+17); Ruff/diff PASS. Existing
Python3.14.7/SDK3.51.0/dependencies used, no install. Scoped feature003 prerequisites
PASS, checklist16/16; no extensions.yml hooks. No frontend changes/rerun.

Tests cover positive/negative controls, missing/foreign unit and role bindings,
uncertain ratings, absence of expected-label canary from posted packets, preservation
of raw scores with calibration failure and immutable old prompt on retry.
Authored mocks are not actual model quality or evidence of judge understanding.

New inputs are three fresh instances of development templates, not independent
holdout. Separate refs/calibrations/protocol/output/ledger; default preparation
actually returned frozen_not_dispatched,3 cases,max25. One batch, up to8 requests
per case and1 stateless judge request for3 primary+3 control packets. Judge cap8192
output tokens; existing generation caps unchanged. No old outcome reruns/unused
budget reuse. Quota/access stop policy inherited from tested v3 adapter.

Commands actually executed:

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
powershell -NoProfile -ExecutionPolicy Bypass -File .specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_investigation_coverage_v4.py -q --tb=short --basetemp=.cache/coverage-v4/red-tmp -o cache_dir=.cache/coverage-v4/red-cache
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_investigation_coverage_v4.py backend/tests/unit/test_investigation_reliability_v2.py backend/tests/unit/test_investigation_judging.py -q --tb=short --basetemp=.cache/coverage-v4/green-tmp -o cache_dir=.cache/coverage-v4/green-cache
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_investigation_coverage_v4.py backend/tests/unit/test_investigation_coverage_v4_runner.py -q --tb=short --basetemp=.cache/coverage-v4/guard-tmp -o cache_dir=.cache/coverage-v4/guard-cache
.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short --basetemp=.cache/coverage-v4/full-tmp -o cache_dir=.cache/coverage-v4/full-cache
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-coverage-v4-inputs.py
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-coverage-v4.py
```

No live result, improvement, spend or human/reference approval inferred from prep.

## Actual execution, calibration and quality

Executed once after freeze, exit0; no runtime/prompt/config/expectation edits
between cases. Model gpt-6-luna, **17/25 actual transport attempts**:16 generation
+1 stateless batch judge.16HTTP200, one cancelled unknown-outcome generation
request without headers. All3 outcomes retained; no old/new reruns or extra judge.

```powershell
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-coverage-v4.py --execute
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-coverage-v4.py --audit
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-coverage-v4-repair-diagnose.py
```

| Case | Actual result | Seconds | Reserved requests/tools/retries/repairs | Machine support | Essential coverage | Development pass |
|---|---|---:|---|---|---|---|
| DEV4-741 incomplete history | valid needs_information |65.404|6/4/1/0|5/5|11/11|PASS|
| DEV4-742 unavailable history | failed,budget_exhausted |35.218|6/4/0/1|N/A|N/A|FAIL|
| DEV4-743 controlled no-guidance | valid needs_information |26.515|5/4/0/0|3/3|8/8|PASS|

**Actual timeout recovery observed** on741: dispatch5 cancelled after29.993s with
unknown outcome; one private request_timeout retry event; dispatch6 returned200
and produced a valid report. The unknown dispatch is retained, not assumed free.
All3 terminal<120s;2/3 valid drafts<90s. Caps unchanged. No credit/quota rejection.

The one judge request rated2 actual reports plus3 calibration controls. Calibration
**3/3 matched**: legitimate needs-information/no-guidance accepted; invented funds
recognized as unsupported/critical; missing human-authority disclosure recognized.
Expected labels/canary were not sent to the judge. This checks narrow calibration,
not broad correctness or independent human validation. Failed actual case remains
failed; calibration examples do not enter the3-report denominator.

Conditional on that successful calibration, development result **2/3 passed**.
On the TWO delivered reports:8/8 rated observational claims supported,19/19 atomic
essential facts present,2/2 procedures applicable (741 only;743 has0,N/A), mandatory
disclosures/missingness correct, no critical or additional machine flags. These
denominators do not count the absent report as successful. No comparable before/
after improvement estimate: prompt, cases and rubric representation changed.
Original failed release outcomes/thresholds remain unchanged.

Known usage **67,688 input +11,814 output =79,502 tokens**, plus one unknown-usage
attempt. Actual spend unknown. Judge time separate from generation latencies.
Unused8 transports are not reused for retries of these completed outcomes.

## Remaining failure: exact typed assertion and repair input size

742 returned a draft after5 HTTP200 requests. Strict validation rejected two
exact_assertions on path eligible_count with string value "null": unavailable
history has null in its text/metadata, but no such scalar Fact exists in facts.
It is not an exact fact value and must not silently become zero or a source fact.
Private repair reason exact_assertion_mismatch was correctly recorded.

Sixth application slot was reserved for its single repair, but no sixth HTTP
request was sent for742. Offline reconstruction used the immutable provider
items, exact saved tool outputs, prompt, schema and repair instruction; no model
request or output was regenerated. **49,925 UTF-8 bytes**, confirmed by canonical
and httpx JSON encoders, exceed configured48,000. Full original private continuation
was preserved locally; no opaque reasoning or body printed/published. This
explains the controlled budget failure without invoking a credit-limit hypothesis.
[Reconstruction metadata](feature-003-coverage-v4-repair-diagnosis.json).

This is remaining unbuilt work: budget-aware repair context must retain required
tool continuation/provenance and strict validation while fitting48k. Do not raise
the cap, discard mismatch checks, mutate the old failure or automatically replay it.

## Audit, local guide and completion boundary

Audit PASS, exit0; [machine record](feature-003-coverage-v4-results.json) binds9
raw/metadata artifacts.8 cited IDs resolve; all accepted reports revalidated and
source/input/protocol/retrieval hashes match freeze.20 prior v2/v3 JSON artifacts
and the v3 source snapshot hash-match. New raw outputs/SQLite/opaque items remain
ignored. .env/dependencies unchanged; no commit/push. Frontend unchanged/not rerun.
870 backend PASS,17 focused/48 related PASS, Ruff/diff PASS. Local guide updated
with calibration/offline checks and remains below200 lines/ignored.

T079–T081 complete for this maintenance/check scope. Human review, independent
reference review, actual producer integration, T066 and full feature ConvergeT067
remain pending. Next concrete step: reproduce/fix48k repair-context exhaustion
with authored SDK tests, preserving all old outcomes and existing input ceiling,
before any separately scoped new live check. No further API calls in this batch.
