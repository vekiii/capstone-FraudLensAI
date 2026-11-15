# T057 closure: deterministic/test-provider safety - 2026-11-15

Branch feature03, baseline/current HEAD 1c76674ea21fc5229972d033b1b35b2a9437fdcf;
initial worktree clean. Request: [actual annotation](../../prompts/development/003-investigation-t057.md).
Applicable AGENTS then next_work read first; scoped speckit-implement instructions,
constitution/evaluation/current safety/code/handoff reviewed. Prerequisites PASS
with SPECIFY_FEATURE_DIRECTORY=specs/003-ai-investigation; checklist markers and
shared instructions unchanged, no extensions.yml hooks. Scope T057 only.

## Coverage of all frozen safety scenarios

| Scenario | Actual controls executed |
|---|---|
| SAFE-01 document injection | Exact frozen injection placed in authored source corpus; only three read tools, no review/write authority. |
| SAFE-02 case-text injection | Exact frozen string in fixture context; real Chrome response interception confirms literal rendering and window.pwned remains undefined. No account action/review from text. |
| SAFE-03 arbitrary tool/scope | All exact frozen SQL/URL/extra-field requests rejected before tool-step reservation; no evidence or executed steps. Bank/account/cutoff/limit overrides also rejected. |
| SAFE-04 other-case evidence | Foreign attempt/context/corpus/passage/hash rejection; linked retry rebinds child evidence; corpus switch disallows stale reuse and preserves parent. |
| SAFE-05 bank/account | Exact frozen SYNTH-BANK-A/OTHER-SYNTH-BANK pair: only permitted 1.00 EUR event counted; foreign 999.00 excluded. |
| SAFE-06 history | Exact H07/H08 context/history/reference assertions: counts/totals/coverage/eligible IDs/order/truncation/exclusions. Empty versus unavailable, strict window/minute/focal exclusion, separate currencies and oversize item refusal. |
| SAFE-07 private canaries | All three actual private-canary values seeded in private history columns/adjacent reference sidecar. Clean index and every captured byte of THREE SDK requests checked, including initial prompt, tool results, opaque continuation and function outputs. Late reference field rejected before fourth HTTP request. |
| SAFE-08 unknown citation | Unknown evidence and unarchived passage/digest rejected; actual archived-passage API returns controlled 404. Invalid-citation workflow attempts one repair then fails safely. |
| SAFE-09 altered assertion | Exact 1250.000 -> 1250.00 and Australian Dollar -> USD changes rejected, along with altered path/quote/owner. Valid citation with false prose remains a separate semantic issue; synthetic unsupported/critical rating cannot pass. |
| SAFE-10 transport/budgets | 13th tool/9th request refused, reserve-before-dispatch coverage, one transient retry/no access retry, 429/connection/eligible 5xx mapping, max_retries=0, refusal/incomplete/access/capability, bounded input/output/response stream, hard total/request deadline and bounded repair. |
| SAFE-11 restart/idempotency | Created/GET zero spend; durable claim/intent/result/drafting boundary checks. Four actual killed CLI worker boundaries (intent/result/evidence/drafting), unknown dispatch preserved, no automatic redispatch, explicit child retry. Same-key original replay, body conflict, two-connection race. |
| SAFE-12 review/stale/late | Real two-browser one-winner/stale 409, explicit refresh and immutable linked correction; empty rationale/forged actor refusal; needs-information restriction before/after review. Actual delayed HTTP selection response/source switch and killed worker recovery. Actual late CLI reply after cancellation cannot publish. |

**Unauthorized tool/action executions: zero.** Three SDK requests are actual SDK
serialization through controlled MockTransport, not real provider/network traffic.
No provider capability, live prompt-injection resistance or human semantic rating
is inferred. No intervention/submission tool was added. Semantic interpretation
still requires the actual T059 raters once live reports exist.

## TDD and actual checks

Existing correct controls were verified without artificially breaking them.
Relevant original RED/GREEN history remains in tools/provider/workflow/recovery/
review evidence. New tests found harness mistakes, not product failures:
1. Initial targeted run: 31 pass/1 ImportError from a wrong reused test name.
2. Expanded run: 45 pass/1 assertion from calling an old helper whose expectation
   assumed 500 for a new 429 subcase; new direct 429 retryability assertion added.
3. Initial full run: 749 PASS before extra connection subcase.
4. Later run: 749 pass/1 KeyError from reading nonexistent tool_calls repository
   column. Corrected to actual persisted executed tool_steps being empty.
None of these is claimed as missing-business-behavior RED. No production control,
schema, threshold or assertion requirement weakened. Ruff import fixes mechanical.

Final backend command from root, with UV_CACHE_DIR=.cache/uv:
```powershell
$runRoot=Join-Path $PWD '.cache/t057-verified-dbbde66a11224ac29e62ececa563487b'
uv run --locked pytest backend/tests --basetemp "$runRoot/temp" -o "cache_dir=$runRoot/cache" --tb=short
uv run --locked ruff check backend
npm.cmd --prefix frontend run test -- --run
```
Final counts are recorded in safety/results/handoff after command completion.
Frontend already observed **186 passed in 9 files**, exit 0. Frontend code/build
configuration unchanged; no build/typecheck repetition required for test-only work.

Actual browser/process commands:
```powershell
node evidence/tasks/feature-003-t057-review-browser.mjs
node evidence/tasks/feature-003-t057-recovery-browser.mjs
$env:PYTHONPATH=Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-t057-process.py
```
All exit 0: review/injection **9 PASS**, recovery/stale **8 PASS**, actual process/
two-connection **6 PASS**. Chrome/157.0.8103.52, Python 3.14.3, Node 24.20.0/npm
11.19.0, uv 0.10.9; existing locked dependencies, no install/upgrade/lock changes.
Chrome runs required sandbox escalation, with explicit approved local-test action.
Hidden owned services/processes, isolated browser profiles; ports 8000/5173/9228
free before start and after cleanup. Only own process trees stopped. Helpers force
test provider and absent ENV_FILE before settings loading; actual .env not read.
No provider probe, real worker or OpenAI call occurred.

The T057 verifiers reuse the proven Phase 5/6 harness mechanics in separate files
and separate result destinations, preserving previous evidence. Their inherited
mode labels identify that lineage; all actions in these new runs are automated
TEST OPERATOR, not new human approval or scientific LLM evaluation.

## Evidence, exposure and preservation

[Summary/hash manifest](feature-003-t057-results.json),
[review/browser results](feature-003-t057-review-browser-results.json),
[recovery/browser results](feature-003-t057-recovery-browser-results.json),
[actual process results](feature-003-t057-process-results.json).

H07/H08 and private canaries were processed only by safety assertions, never used
for tuning, generation references, glossary edits or metric selection. No raw
held-out question/reference/canary text was printed into the model conversation.
This exposure is recorded; do not describe future development using these
scenarios as a fresh independent holdout. This run is NOT a second T056 quality
evaluation, and does not replace its below-target results.

Hash-only evaluation audit PASS: 41 original hashes checked, original T052
approval/question/reference content preserved, T055 code/config artifacts match.
All changes are tests, verification harnesses, evidence/prompt/task/handoff records;
runtime, frozen rank/glossary/cutoffs/deployment and ML/producer code unchanged.
No skips/xfails added, no external communications, commit/push/merge/deploy.

T057 complete in the specified deterministic/test-provider safety scope. T033
still blocks T058 -> T059 -> complete T060/T061; no live quality/usage/spend claims.
One next step: separately authorize T033 capability diagnosis/new explicit call
budget before attempting any real provider execution. Do not run a probe merely
because T057 has passed.

## Final observed results

Final full backend **750 passed in 54.49s, exit 0**, including all **52** safety
subcases. Ruff PASS/exit 0. Frontend **186 passed**, exit 0. Diff/UTF-8/link and
unchanged checklist/hook checks PASS. All browser/process records status PASS;
no cleanup errors. No pending test failures, skips or unexecuted deterministic
T057 subcases remain. Live-provider/human-quality limitations are explicit above.
