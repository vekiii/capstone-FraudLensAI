# T101 / T102 fresh source review packet — 2026-11-18

This is offline preparation on `feature03` after commit `5431299`. Nothing in
this packet authorizes dispatch. No live report, judge rating, calibration result
or SC-003/SC-006 pass has been produced. T101 and T102 remain open. No new tasks
are proposed or added.

## Reviewable inputs and custody

| File | New instances | Purpose |
| --- | ---: | --- |
| `inputs/development.json` | DEVQ1-01..04 | Development before final holdout freeze |
| `inputs/quality.json` | QUAL1-01..08 | Eight prospective held-out reports |
| `inputs/timing.json` | TIME1-01..05 | Five ordinary external API/worker timings |
| `inputs/search.json` | SEARCH1-01..20 | Twenty English deterministic local searches |
| `reference/*.json` | Source-derived obligations/history; fixed roles | OFFLINE custodian only |

Authored source literals are new, with new transaction/account identities,
amounts and event times. No old report or rating was used as an input template.
These are synthetic fixture contexts, explicitly not trained-model predictions
or independent ML evaluation. The already completed real producer integration
remains T098 evidence. Supported-history examples supply partial records, never
complete account coverage. Unavailable history does not mean zero activity.
Mixed currencies remain separate. Same-minute and future distractors are excluded.

The timing order is supported history, unavailable history, mixed/incomplete
history, no adequate jurisdiction-specific procedure, elevated illustrative risk
with missing customer facts. The no-guidance question is about an exact current
Portuguese filing deadline absent from the curated educational corpus. It is a
source review question, not a forced retrieval failure or modified adequacy cutoff.
Its actual live retrieval/report outcome is unknown. No fault is injected.

Private obligations are derived from the supplied transaction, score meaning
and actual `HistoryReader` responses before generation. They are not pass labels.
Only public inputs enter the generator; no `reference/` file enters runtime
readers, tools or indexes. Judges receive projected v4 packets, authorized source
evidence and predeclared source facts, with the uniform neutral field inventory.
Calibration expectations and peer ratings stay outside judge contexts. There
are no human reviews yet: the author/custodian is Codex offline automation with
source script/version hashes. Team review is pending and must not be invented.

Primary roles cover all eight quality instances. Secondary roles cover the SAME
positions 2, 3, 4, 6, 8 (`QUAL1-02/03/04/06/08`). The six new T096 controls in
`../report-quality-v4/inputs/controls.json` are the prospective calibration sources;
their authored software ratings must never be submitted as actual model results.

## Concrete execution proposal, not approval

Use the configured model `gpt-6-luna`, source `fixture`, semantic v6 retrieval
enabled, existing generation prompt v4 plus English-query addendum. Same-model,
isolated-context LLM judging is proposed; it measures agreement and does not
establish independent human/model validation. T095 approval does not authorize
this T101 judging method or budget.

| Stage | Maximum new provider requests |
| --- | ---: |
| Four development investigations, at most eight each | 32 |
| Exact six-control v4 calibration | 6 |
| Eight fresh quality investigations, at most eight each | 64 |
| Eight primary plus five paired secondary judgments | 13 |
| **T101 maximum** | **115** |
| Five ordinary timing investigations, at most eight each | **40** |
| **Combined proposed maximum** | **155** |

Every semantic selection, retry and repair counts inside the corresponding
eight-request limit. No extra probes, judging retries, fallback model, old-budget
reuse, automatic reruns or replacement cases. Generation uses <=4096 output
tokens/request, <=48000 input bytes, <=30s per request, <=120s per investigation.
Judging uses <=8192 output tokens, <=65536 input bytes, <=60s/request, zero retries.
These are request/size limits, not an asserted dollar price or available credit.
The 20 local lexical searches use zero paid requests and do not grade relevance.

Execution sequence:

1. Team reviews public sources, separate private obligations and this method/cap.
2. After explicit new approval, run only the four development instances. Review
   actual outputs offline. Any justified changes are recorded within T101.
3. Freeze the resulting exact code/prompts/settings, transport meter, contexts,
   corpus and separate roles/references before opening held-out outputs. No
   tuning after those outcomes; changes invalidate that acceptance attempt.
4. Judge the six controls in isolated contexts and require exact 6/6. Preserve
   failures and stop acceptance if calibration is invalid. Do not relabel.
5. Run all eight quality slots and fixed paired-five judgments under v4, saving
   outputs/usage/errors before joining private references. Aggregate with
   `judging_v4.py`; >=7/8, support>=.90, coverage>=.80, zero critical across eight,
   all disclosure/procedure/disagreement gates apply unchanged.
6. Separately freeze a fresh five-case timing batch on one idle matching local
   API/worker pair. External observer starts before POST and records first GET
   terminal state; validate saved reports against their evidence. All five stay
   in the denominator. Stop further cases on unknown/continuing-worker outcomes
   or access/quota failure. Never substitute client cancellation for server state.
7. Measure the 20 frozen local queries once each after a single corpus load.
   Assess all five/20 observations with `timing_evaluation.py`: >=4/5 useful <=90s,
   all five visibly terminal <=120s, nearest-rank-19 search p95<=2s.

## Prepared tooling and remaining execution setup

`evidence/tasks/feature-003-t101-t102-prepare-20261118.py` created and schema-checked
this pack without initializing a provider. `manifest.json` pins input/reference
bytes and the initial ignored machine snapshot. It is a preparation snapshot,
not a final executable freeze. Later verified snapshots explicitly supersede
initial code hashes after observer tests/formatting; originals are retained.

`backend/src/fraudlens/investigation/timing_observer.py` is a tested external HTTP
helper, separate from application/worker. It persists exclusive/fsynced intent,
UUID idempotency key, each HTTP body/timestamp and result; never retries POST;
includes create/queue/poll time; records full overruns; stops on unknown outcomes.
The helper itself has no dispatch CLI and grants no budget. Socket cancellation
is bounded with an observer-side asyncio timeout. The separate runner below adds
an independent parent-process watchdog for a blocked observer. Software checks
are not live timing evidence.

`backend/src/fraudlens/investigation/acceptance_harness.py` now supplies the strict
fresh context/history reader and persistent SQLite transport ledger. The ledger
archives payload/response bytes, request IDs and usage, reserves before network,
cannot reset cap/model, and blocks further sends after unknown/access/quota
outcomes. It saves no Authorization header. Approval binds exact stage/cap/model,
freeze bytes, source hashes and batch directory; cloning a freeze cannot reset
its budget. This validates a recorded approval, never creates human consent.

`evidence/tasks/feature-003-t101-t102-runner-20261118.py` connects those readers to
the existing API and matching worker in separate processes. Its `prepare` command
is offline and creates a new batch only. `api`, `worker`, `observe` and per-case
`slot` require explicit hash-bound authorization for an OpenAI batch. TEST mode is
explicitly ineligible for acceptance. Observer/worker/API remain separate; the
parent allows 125s for an observer subprocess, records a watchdog failure at full
elapsed duration and stops dispatch on unknown outcomes. Killing an observer
never proves server termination. All HTTP/terminal evidence and source-bound local
report revalidation are retained. A fresh idle queue and exclusive batch/slot
markers prevent old-attempt reuse. No root application composition is changed.

Example offline-only development preparation (NEW path required):

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe evidence/tasks/feature-003-t101-t102-runner-20261118.py prepare --stage development --provider openai --batch evals/results/feature-003/NEW-DEVELOPMENT
```

Do not run a paid batch until review/authorization. An approval record must contain
`approved=true`, the exact `freeze_sha256`, `stage`, `maximum_requests`, `model`
and the actual `user_authorization` text; no such live approval exists here.
The driver does not fetch secrets or approvals from this README.

Before held-out execution, generated development outputs still need review and
the resulting exact settings must be frozen. Generated report prose and atomic
units can only be materialized/reviewed after those reports actually exist; the
v4 judge dispatch/join remains a separate staged step within T101. Before live
T102, final physical machine/observer identities, the exact five+20 inputs and
source/queue/UI-or-GET preflight must be checked. No new product task or runtime
contract is needed. No placeholder freeze or unmetered runner should be dispatched.

Read the actual preparation evidence for checks and limitations. Preserve the
historical 0/8 report result, failed/unavailable calibration-quality results,
2/5 timing failure and 7496.290s outlier. This packet does not close Feature 003.
