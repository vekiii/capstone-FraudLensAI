# T101 / T102 preparation and execution boundary — 2026-11-18

## Scope, branch and workflow

User requested continuing T101/T102 after merging onto `feature03`, then assessing
Feature 003 closure. User subsequently prohibited independently adding tasks.
No task was added, no existing task marker changed, and no commit/push/merge was
performed. Original action request: `prompts/development/003-t101-t102-20261118.md`.
Unrelated conversational questions are outside this record.

Actual branch/HEAD: `feature03`,
`5431299053660f982e93c4d5fc8909131281ec2a`
(`T098 finished; producer integration and history index verified`). Initial
worktree clean. Older handoff branch/uncommitted text is historical after the
user's commit/merge. Actual Git state, not that historical line, was checked.

Read root AGENTS/next_work, constitution, approved product context, relevant
feature spec/plan/tasks/research/data-model/contracts/quickstart, corrected v4
validation path and timing-v1 protocol. Applied `.agents/skills/speckit-implement/SKILL.md`.
Explicit feature selection:

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
powershell -NoProfile -ExecutionPolicy Bypass -File .specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
```

Prerequisites selected the requested absolute feature path. No extensions.yml
or hooks. Requirements checklist 16/16 checked, zero open; no markers changed.
Ignore patterns already cover local stores, credentials, caches and result files;
no dependency/lock/shared instruction changes.

## New source packet

[Review packet](../../evals/investigation/acceptance-v1-20261118/README.md):

- Four fresh DEVQ1 development inputs, eight QUAL1 prospective quality inputs,
  fixed paired-five positions 2/3/4/6/8, five ordinary TIME1 inputs and 20 English
  SEARCH1 queries. All 17 investigation inputs pass the existing input-only and
  InvestigationContext boundaries with recomputed context revisions.
- Source literals authored afresh, not copied from old outputs/templates. Compared
  against 27 historical public contexts: no identical context or case-ID overlap.
  Transactions retain the existing three-digit fixture identity contract; the
  first authoring attempt used four digits and correctly failed validation before
  creating the packet. Corrected to valid new IDs; no schema widening.
- Separate custodian-only source obligations/history and fixed role assignment.
  Author is Codex offline automation, source script hashes recorded. Team review
  remains pending; no invented human review or independent label claim.
- Actual HistoryReader results match frozen references. Available sender history
  has two eligible events, available receiver one. Source amounts 83.47/29.61,
  separate mixed-currency totals, unavailable sides preserved; same-focal-minute
  and future 987.65 distractors excluded. No label/expected rating in public input.
- All six T096 control packets project with the identical neutral field inventory.
  Existing controls are software-authored controls, not live calibration results.

These are reviewed-source proposals using synthetic fixture contexts, not ML
predictions/evaluation or a replacement for completed real T098 integration.
No source producer database was modified. Root `/api/cases`/UI composition remains
the pre-existing fixture journey; fresh evaluation contexts use the opt-in API
reader, not a claimed merged dataset browsing screen.

The prepared protocol's pending list records its initial authoring point. The
reader/meter/API/worker items were subsequently implemented and exercised below.
Read this evidence/packet README for the current status. Its `execution_ready=false`
remains correct: no team source review, new spend authorization, post-development
held-out freeze or actual report judgments yet. Initial snapshot/manifest preserved.

## Observer and transport boundaries

New opt-in modules, never imported by default app/worker composition:

- `backend/src/fraudlens/investigation/timing_observer.py`: exclusive fsynced UUID
  intent before POST; no POST retry; separate external GET observer; 250ms polling;
  external monotonic clock includes creation/queue/polls; immutable HTTP bodies,
  timestamps and result. Reports validated against bound saved evidence/context.
  Unknown/error/continuing-worker outcomes stop the batch; full overruns retained,
  never clipped to 120. Failed/cancelled states cannot be useful successes.
- `backend/src/fraudlens/investigation/acceptance_harness.py`: strict fresh
  input-only context/history readers, persistent FULL-synchronous dispatch ledger,
  model/cap pins, reserve-before-network including semantic/retry/repair traffic,
  response bytes/request IDs/usage. Unknown/access/quota stops further sends.
  No headers/keys in ledger. Completed results cannot be rewritten.
- Authorization check requires the recorded actual user approval, exact freeze
  digest, stage/model/cap, immutable code/source hashes and exact batch directory.
  It cannot establish consent itself. Wrong/missing approval, changed source and
  copied freeze are blocked before provider creation.
- `evidence/tasks/feature-003-t101-t102-runner-20261118.py`: offline new-batch prepare;
  separately launched matching API and worker; parent/child external observer.
  Parent enforces a 125s per-slot OS-process watchdog to detect a blocked observer
  (startup included in that diagnostic bound). Timeout records full parent elapsed
  and unknown server state, stops later POSTs and never claims killing a client
  terminated the worker. Primary visible timing remains the child's GET measurement.

No automatic dispatch command was run with a real provider. The driver explicitly
labels TEST batches ineligible. Actual report/unit materialization and v4 judge
dispatch/join remain staged work after new reports exist, within T101. Before a
live batch, verify final model/capability conditions, full machine identity, exact
source/queue and HTTP/UI observation bindings. No current model access was probed.

## Actual RED / GREEN / regression observations

1. Initial observer run hit an unrelated pytest temp-directory WinError5 setup
   error (8 errors); not counted as RED. Explicit new workspace basetemp resolved
   setup. Intended RED: **8 failures** for unimplemented observer behavior. GREEN
   8 passed; expanded observer checks **12 passed**, including real asynchronous
   network-wait cancellation, full overrun and validation-after-observation timing.
2. Reader/ledger intended RED: **8 failures** for unimplemented input-only/persistent
   budget behavior. GREEN 8; expanded transport/authorization checks **19 passed**.
   Mock transports contain no real model calls; consent records in tests are
   explicitly test fixtures, never copied into a live batch.
3. Combined final helper tests **31 passed**. Related existing v4 judge/timing/
   deadline checks passed. Full final backend run **1112 passed in 117.95s**, exit0.
   Log `.cache/t101-full-20261118.log`, exit sentinel
   `.cache/t101-full-20261118-exit.txt`. Frontend unchanged/not rerun this unit.
4. Ruff check/format and git diff whitespace checks passed after corrections.
   No runtime prompt/schema/threshold or dependency changes.

Commands:

```powershell
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_timing_observer.py -q --tb=line --basetemp=.cache/t101-observer-red-20261118
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_acceptance_harness.py -q --tb=line --basetemp=.cache/t101-harness-red-20261118
.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short --basetemp=.cache/t101-full-20261118
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe evidence/tasks/feature-003-t101-t102-prepare-20261118.py
.venv/Scripts/python.exe -m fraudlens.investigation.judging_v4 --verify-controls evals/investigation/report-quality-v4
```

Authoring is exclusive-create: do not rerun into these existing paths. All intended
REDs preceded their implementations. Software-control verifier returned
`software_controls_pass=true`, `model_quality_evaluated=false`, six matched controls;
that is not an actual-provider exact6/6 result.

## Actual HTTP test and no-spend gate

Prepared `.cache/t101-t102-http-smoke-20261118` with TEST provider. A local Python
supervisor launched hidden API and worker processes on loopback port8768, confirmed
GET documents readiness, then the actual external observer spawned five case
subprocesses. Five fresh POSTs/UUID intents, five GET-observed `ready_for_review`
states, five evidence/context-bound report validations. All five archives saved
with view/context/evidence/audit. Observer exit0; API/worker processes terminated
by the supervisor after completion. No injected faults, live calls or quality
acceptance. `provider=test`, `acceptance_eligible=false` retained in raw results.

Frozen smoke source snapshot predates later batch-clone authorization guard and
read-connection cleanup. Its exact hash snapshot/results remain intact; final
guard/source behavior is covered by the final 1112-test run. Do not describe that
earlier smoke as executing every later source byte.

Separately prepared a real-provider development PROPOSAL offline, then invoked
its worker WITHOUT approval. It returned exit2/ValueError before provider startup;
actual dispatch table has **0 rows**. No live approval record exists. Proposal:
`evals/results/feature-003/acceptance-preparation-20261118/development-proposal/`,
freeze SHA `0d72c9adfc27fe2f196fd496181a01663940c420163bd6069885bd52da9ac3c1`.
The configured model is `gpt-6-luna`; key presence checked without printing it.
Presence is not evidence of current capability/credits/availability.

## Local-only diagnostic and machine

After one unmeasured corpus load and no query warm-up, each of the 20 frozen
English queries was searched once through existing deterministic local search.
20 results, zero exceptions; nearest-rank19 p95 **0.0030023999861441553s**.
This is an unreviewed preparation diagnostic, explicitly **SC006_accepted=false**;
no relevance labels, semantic paid queries or favorable-subset selection. It does
not replace the reviewed live five+20 batch or establish report quality.

Corpus `corpus_2fa1aa3379fadf2749300897ef79b9239c2ced2da311b370a8974d709b0bfaf3`;
local retrieval `c17e43b9014a39c47b85c0e6b6e9926e11baaf9721ee406b960a25a44d0e8895`.
Machine Windows11 build26200, Intel64 Family6 Model141, Python3.14.7,
Node24.20.0, OpenAI SDK3.51.0, httpx0.28.1, Pydantic2.14.3. Physical RAM
34,065,952,768 bytes recorded via Win32 GlobalMemoryStatusEx. CIM reads were denied;
no escalation was attempted and no missing hardware value was invented.
Machine/clock details and full samples are in ignored result snapshots.

## Remaining review and approval; no feature closure

[Machine-readable observations](feature-003-t101-t102-preparation-20261118-results.json).
Ignored preparation folder retains initial freeze/knowledge DB, machine-v2,
source-snapshot-v2, local-search intent/raw samples and the unapproved development
proposal. The current snapshot explicitly lists intentional source differences
from the earlier preparation freeze; it is not a live acceptance result.

Concrete proposed new maximum: **T101 115 calls** (4x8 development +6 calibration
+8x8 quality +8 primary +5 secondary), **T102 40 calls** (5x8), combined **155**.
All semantic calls/retries/repairs count inside generation limits. Judge requests
have no retries, <=8192 output tokens/<=65536 input bytes/<=60s; generation retains
existing <=4096/48000/30s/120s limits. This is a request cap, not a known dollar cost.
No extra probes, old-run replay, fallback model, hidden rerun or exhausted budget.

Await team acceptance of fresh sources/private obligations, same-model isolated
judge method and the explicit new cap. Development is first; any justified
revision is frozen before held-out generation. Post-unblinding changes require
stopping and discussing alternatives with the user, not adding tasks or tuning
the same holdout into a pass. The same-model method is correlated automated
review, not independent human/model validation.

**T101/T102 remain open. Feature 003 is not ready to close.** New actual-provider
six-control calibration, all eight primary/fixed five secondary ratings and actual
five-case external timings have not run. Original quality0/8, failed/unavailable
calibration-quality and old timing2/5/7496.290s failure remain unchanged. T098 is
completed in its recorded real bounded producer/history scope; it grants no live
quality/performance acceptance. No new task/ML training/paid call/commit/push/merge.
