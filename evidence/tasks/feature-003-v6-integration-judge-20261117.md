# T095 semantic runtime integration + blind LLM reference evaluation

User authorized wiring v6 into API/worker and separate LLM-as-judge evaluation.
Actual approval/method boundary: specs/003-ai-investigation/retrieval-v6-judge-decision.md.
Original prompt: prompts/development/003-v6-integration-judge-20261117.md.
Branch feature03-retrieval-v4, base68aa027 with preserved prior uncommitted v4/v5/
v6 work. No merge/commit/push. Used scoped speckit-implement, explicitly selected
feature003, prerequisite PASS; requirements checklist had no unchecked gate.

## Implemented runtime behavior

Opt-in INVESTIGATION_SEMANTIC_RETRIEVAL=true, explicit OpenAI configuration.
Worker validates/reserves tool BEFORE semantic spend, reserves an existing provider
dispatch, keeps shared max8 requests/max12 tools/max120seconds and remaining
per-call deadline. New binding pins semantic policy, runtime, model and corpus;
old/retried attempts preserve mode. Stale source/context, changed policy/code,
cancelled owner or exhausted budget cannot publish semantic evidence or a report.
Semantic-only worker prompt addendum requests English procedure queries and keeps
Serbian reports/human decision requirements. Existing mandatory notice unchanged.

Explicit POST /api/knowledge/semantic-search: same-origin/loopback, UUID idempotency,
closed <=4096byte body, max1 provider reservation per key, lifetime store cap10
(trusted config1..30), no automatic retries. GET status and POST cancel/replay do
not dispatch; same key+different source/body/runtime conflicts. Pending/expired/
interrupted/cancelled calls remain counted; late output cannot replace terminal
state. Existing GET knowledge browsing stays deterministic/free. No frontend paid
button or hidden GET model call. Contract: contracts/semantic-search-v1.md.

## Actual tests and execution

Initial RED: missing runtime module (2 setup errors) and missing settings flag
(1 failure). GREEN3. Explicit POST RED405; GREEN4. Public raw-SDK audit exposure
RED1, then corrected projection GREEN. Additional tests cover lowered/reopened
budgets, cancel during API/worker await, timeout not no-match, changed source,
invalid query zero extra spend, positive citation/report path, schema/quote refusal,
raw failed-response retention, and bad-calibration/missing-output grading controls.

Final production integration regression:
- Full backend1008 PASS72.26s,exit0. One additional raw-audit regression was added
  after collection; final34 focused runtime/core/judge tests PASS3.91s,exit0.
- Frontend193 PASS; typecheck/build PASS; source frontend unchanged.
- Ruff, git diff --check PASS after final code. No package install/lock changes.
- Offline archived-evaluation verifier PASS: executed code hashes,44 unique
  dispatch intents,20 input/gold/output rows, recomputed metrics, zero calls.
- Current HTTP projection read all20 archived jobs with semantic mode DISABLED:
  statuses/results identical, raw provider/diagnostic bodies absent, provider
  factory never invoked. First helper probe failed because Windows default cp1252
  decoded UTF-8 reviewer metadata; corrected explicit UTF-8 probe PASS. A separate
  lineage helper initially needed PYTHONPATH/Windows separator correction. These
  were audit command errors, not retrieval successes or suppressed application bugs.

## Automated reference protocol and outcomes

New44-request ceiling, no retries:4 calibrations+20 blind reference annotations+
20 integrated API searches. Judge used SAME explicitly configured gpt-6-luna in
separate stateless contexts, never candidate outputs/author references. This is
blind process separation, not independent model or human review. Questions from
previously proposed/unexecuted English held-out20, with16answerable+4no-answer.
Code/prompt/source/input hashes frozen before any call. No question-specific
rerouting, threshold tuning, discarded failures or label changes after outcomes.

Judge calibration4/4 PASS (specific missing fact, score-not-proof negative rule,
historical/current jurisdiction, embedded instruction/credential lure). All20 gold
sets/quotes validated and frozen BEFORE candidate execution. Judge expanded source
sets for EN5-019 and EN5-022 versus AI proposals; differences published and used
as frozen references, producing real partial-recall penalties. No answerability
denominator change. No independent-human gold accuracy guarantee inferred.

Initial execution stopped at candidate10 (EN5-020), HTTP503/provider_failure,
outcome_unknown=true; raw error response/usage unavailable. Its exact cause is
unknown, not asserted to be a timeout or provider outage. The9 earlier results
and initial failed aggregate were preserved. Within remaining10 allowed calls,
explicit continuation ran ONLY10 UNDISPATCHED IDs under SAME source/prompt freeze.
No retry of failed020, no replay of completed rows. Complete20 includes19 HTTP200
and1 failed503 counted zero. All44 allowance consumed.

| Frozen configuration / same20 inputs and blind references | Recall@5 | MRR@5 | No-answer |
|---|---:|---:|---:|
| Demo BM25 .5 |.979167|1.00|0/4|
| V3 selected BM25 |.1875|.1875|4/4|
| V5 |.614583|.6875|4/4|
| Semantic v6 integrated API |.864583|.9375|4/4|

V6 passes .80Recall/.70MRR/all4 no-answer under approved automated reference
method, despite retained failure. Lexical comparisons were local fixed-config
predictions then reference join, no tuning or model calls. Known usage56204input+
6573output=62777tokens across43 returned usage records;1 unknown. Monetary cost
unknown. No additional live worker reports, probes, retries or LLM calls made.
The script pipeline is ASGI HTTP integration, not a new browser/proxy/live-report
acceptance claim. Existing failed report quality/timing/full-IBM criteria unchanged.

Raw partial and complete reports: feature-003-v6-integrated-judge-20261117.json
and feature-003-v6-integrated-judge-complete-20261117.json. Baseline/source-set
differences/public-projection/code-lineage checks are separate JSON siblings.
Frozen bundle includes executed code snapshots, inputs, blind refs, responses,
calibration and ledger in evals/investigation/retrieval-v6-integrated-judge-20261117/.

## Post-evaluation changes and limitations

Executed runtime archived BEFORE these infrastructure fixes:
1. Public HTTP projects only safe model/request/usage audit fields, not raw SDK.
2. Future SDK replies captured server-side BEFORE strict quote validation, including
   late/invalid outputs, with no client mutation/new request. Historical missing020
   raw response is NOT reconstructed. Public error diagnostics remain redacted.
3. New-semantic-attempt-only English query addendum pinned in prompt binding.

No semantic selector core/prompt/model/corpus/ranking/threshold changed after live
results. Final code has offline regression and all20 saved-output HTTP equivalence;
no live rerun after fixes, budget exhausted. Exact executed/current code lineage
is published separately; live numbers refer to archived executed runtime.

This is stronger generalization evidence than exposed6-row development but cannot
prove absence of overfitting: same-model judge bias, six-document coverage and
semantic topic overlap remain. Calibrations are limited controls, not universal
safety proof. No report-quality, production-auth or full-data acceptance claimed.
T095 checkbox remains unchanged for team's reserved acceptance/merge decision;
numeric retrieval gate and requested integration work now have concrete evidence.
T094/T096-T098 and their failures/pending work remain separate. No merge/push.


## Actual user acceptance - 2026-11-17

User: "Okej. reviewovao sam, da li mozes sada da cekiras T095?"
Recorded explicit review/acceptance and marked T095 complete. This is the user's
review of the delivered work/evidence, not an invented independent-human labeling
exercise or model-independence claim. All evaluation caveats, failed020, original
artifacts and other open feature criteria remain. Offline archived verifier rerun
PASS with zero provider calls before changing marker. No new runtime changes,
live calls, commit, push or merge. Earlier pending-checkbox statements preserved
as historical status, superseded by this actual acceptance.
