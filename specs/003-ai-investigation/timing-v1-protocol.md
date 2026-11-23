# T097 prospective five-case timing protocol, 2026-11-17

2026-11-18 successor addendum: actual initial fresh TIME1 batch is2/5 useful,
all5 visibly terminal<=120 and local20p95.0032897s; failure retained. User then
accepted corrective v7 formatting and an explicit45s drafting cap for NEW fresh
cases after a second30s drafting timeout. Default/legacy30, semantic30, total120,
useful90 and8/12 remain. RUN3 prospective timing sample is the FIRST five of
eight quality reports, selected before dispatch with overlapping-sample disclosure.
All first outcomes retained; no best-of-retry replacement. No new task/budget.
Check next_work for successor execution; this addendum alone is not timing PASS.

Status: protocol/tooling only. NO live execution or new provider budget authorized.
Original SC-006 unchanged: at least4of5 validated ready_for_review/needs_information
within90 seconds; ALL5 visibly terminal within120; local20-search p95<=2 seconds.

## Historical/current reconciliation

Original five demo cases: INV-D01 30.365s needs_information; INV-D02 7496.290s
failed; INV-D03 41.686s failed; INV-H01 25.479s needs_information; INV-H05 44.786s
failed. Actual result2/5 successes<=90 and not all terminal<=120, hence FAIL.
The long outlier is preserved. The old runner measured perf_counter around
service.work_once(), after creation (feature-003-live-run.py lines92-95), NOT
external UI-visible timing. Recomputing old arithmetic does not establish visible
terminal observations. Aggregate timestamps do not prove the outlier root cause.
Raw ignored archives are not reconstructed from summaries.

Later timeout-v3 development3cases ran32.617/23.739/20.798 seconds, all needs_information.
V8 has TWO ordinary cases46.789/26.687 plus ONE injected repair38.841, not five
ordinary cases. Neither3/3 nor2+1 replaces the old five-case acceptance failure.

Current workflow: claim persisted lease; derive monotonic remaining deadline;
request=min(30, configured request cap, remaining); one transient retry/backoff
within same request/time budget; one repair; semantic retrieval consumes SAME
8request/12tool/120second limits. SDK max_retries=0, provider timer includes response
body read; wall-clock lease/state guards reject stale results. Cleanup <=min(1s,
remaining time), and terminal results survive cleanup errors. Existing timeout-v3
and reliability-v2 tests exercise these behaviors. Cooperative asyncio cannot bound
host suspension, blocked synchronous code or cancellation-suppressing dependencies.
No remaining runtime defect is established just by the old outlier. Do not change
runtime timers or thresholds without reproducing a current defect.

## Fresh frozen run design (must be materialized before spend)

Five new ordinary IDs TIME1-01..TIME1-05, in that order: supported transaction with
available history; unavailable history; incomplete/mixed-currency history; no
adequate procedure; ordinary elevated illustrative risk with missing customer
facts. No injected faults. Author new exact amounts/times/accounts, no old report
prose or private labels in generation. A no-guidance outcome may be needs_information.
All cases use approved fixture or reviewed synthetic context, clearly identified;
fixture timing is not evidence of full producer/ML performance.

Freeze BEFORE first dispatch into a NEW ignored results directory: all five actual
input objects and context/snapshot/history/evidence/corpus hashes, English retrieval
queries/config/semantic policy, model/provider capability/settings, prompt bytes,
code commit AND dirty source hash map, SDK/Python/Node locks, machine/CPU/RAM/OS,
role of observer and clock policy. No placeholders in executable freeze. Pin same
source/model/retrieval mode for all cases, zero tuning between outcomes. If model/
corpus/context changes, stop; preserve batch, no replacement subset or automatic rerun.
Hash all artifacts. The five materialized inputs and budget need separate team
approval before actual dispatch; this document alone never makes provider calls.

Run one matching API+worker pair, idle local queue, one case at a time. Confirm
source/mode and UI against frozen context. No cached/reused attempts. Persist one
batch marker and one per-case intent BEFORE POST; exclusive files, idempotency
keys, no automatic replay of unknown outcomes. Never reset counters/ledger.
Proposed future cap:40 actual provider requests total (5x8, INCLUDING semantic,
transient retries and repairs), zero extra judge/search/probe requests. This is a
proposal, NOT authorization. On access/quota/credit failure stop batch; unstarted
slots remain not_run failures in denominator5, never dropped. No unused-budget
spending or model fallback. Judge report quality separately under T096 protocol.

## Measurements and watchdog

Observer uses time.perf_counter/monotonic on one machine. Start immediately before
POST, include creation/queue delay, worker dispatch, retries, tools, repair, network
and UI/poll wait. First HTTP GET/UI observation of terminal state stops visible
clock. Poll fixed <=250ms; record polling interval and actual observation times.
Also record worker_started, server terminal audit, worker return incl cleanup,
provider per-dispatch headers/body/unknown usage and wall UTC for diagnostics.
Never substitute worker-only elapsed for externally observed completion.

At120s take a final status observation, stop waiting on this slot, archive failure
if no visible terminal by120; do not infer server terminal state from a killed
client. An external observer/watchdog must remain separate from worker so blocking
or suspension is not silently excluded. Record overruns at full measured duration;
never cap reported seconds at120 or subtract sleeps/suspension after results.
If a timed-out worker continues, stop further cases and preserve uncertainty;
explicit cancellation/cleanup is outside primary timing outcome and cannot fix it.
A completed failed/cancelled state may satisfy terminal<=120 but never success<=90.
Successful states require locally validated report. Missing observations are failures.

Local search: freeze20 unique English queries SEARCH1-01..20 and expected source
versions separately from labels. Measure deterministic LOCAL search (not paid
semantic calls), one measured call each in frozen order, after one unmeasured
corpus load only. No query warmup/repeats/minimum selection. Record raw durations
and exceptions; errors/missing queries fail search gate. p95 nearest rank19/20,
not interpolation or mean. Full SC-006 requires BOTH demo and local-search gates.

## Offline assessment implementation design

New separate timing_evaluation module, no provider/runtime imports. assess_demo
requires frozen5 unique IDs, preserves absent slots, rejects duplicate/foreign rows,
uses finite nonnegative seconds (never bool/NaN), known states, report_validated
Boolean. Computes success count<=90 and terminal<=120 separately. assess_searches
requires frozen20 unique IDs, one sample each, errors/missing fail; rank19 p95.
CLI reads explicit new envelope and exclusively creates output; no overwrites,
no remote calls, no archive rewrite. Offline fixtures prove arithmetic only.

## Completion boundary

T097 completes reconciliation, relevant offline checks and this prospective
protocol. It does NOT assert new live timing PASS/SC-006 or reproduce old latency.
Separate bounded authorization is required after freezing actual five+20 inputs.

## Offline command and envelope

```powershell
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe -m fraudlens.investigation.timing_evaluation --input evals/results/feature-003/NEW-TIMING/input.json --output evals/results/feature-003/NEW-TIMING/result.json
```

Command consumes already archived observations only; it creates no attempts and
makes no API calls. NEW-TIMING is a future path, not an existing result or execution
authorization. JSON envelope: scenario_order (five frozen IDs), observations (list
of {id, state, seconds, report_validated}), search_order (twenty frozen IDs),
searches (list of {id, seconds, error}). Use full nonrounded externally measured
seconds. Set report_validated only after actual local report validation. Active or
unknown states do not qualify as terminal. Absent observations remain failed slots;
duplicate/foreign IDs, malformed states/flags and nonfinite seconds are rejected.
Search error=true requires finite recorded elapsed; p95 unavailable if any missing/
error sample. Output includes full observations and separate demo/local_search
results; performance_pass requires both. Existing output is never overwritten.
Evaluator validates arithmetic, not provenance or observer honesty. Freeze/audit
and actual UI/GET observation records are required for any acceptance claim.

T097 implementation has19 new offline tests:17 measurement/CLI checks plus2
characterization regressions for backoff expiry and combined request/slow cleanup.
Current runtime is unchanged; these regressions did not reproduce a remaining
runtime defect. Prior timeout/cleanup fixes are supported by existing tests, not
by a fabricated diagnosis of the historical outlier.
