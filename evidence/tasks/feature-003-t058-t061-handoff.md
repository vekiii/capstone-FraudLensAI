# T058-T061 handoff - 2026-11-15 Europe/Belgrade

Scope: user requests all remaining related work through T061. No T062+ or Git
publication. Baseline HEAD 9796902f3b1b4c8670a1f7e15213b9e34678bf26. Existing
staged/user work preserved; resumed session reread AGENTS then next_work and the
live ledger before acting. No duplicate batch or repeated saved attempt started.
[Original request, 104 budget and raters](../../prompts/development/003-investigation-t058-t061.md).

| Task | Actual status |
|---|---|
| T058 | Complete execution: 8 primary + 5 ordinary live outcomes, including all failures; quality targets failed |
| T059 | Pending actual human review; Vedran primary, Milan independent secondary; user explicitly defers review until handoff |
| T060 | Partial: actual timing/known usage/failures aggregated, review importer tested; semantic support/coverage/critical judgments unavailable |
| T061 | Partial: current integrity/leakage/binding audit passed; final acceptance awaits T059/T060 |

## Implementation and freeze

Added closed, aliased dataset projection derived from pinned producer schema:
exact paid/received strings and currencies, raw minute/time-basis, score kind/
source and explanation status preserved. Raw bank/account identity removed from
provider context. This consumes authored T052 materialized examples ONLY, not an
actual producer database/integration or inferred producer approval. Ordinary
CaseContextReader still does not acquire a live dataset adapter.

InvestigationService optionally accepts a HistoryReader for exact materialized
fixture events/accounts; default foundation behavior is preserved. Live runner
uses the existing durable workflow/retry/repair/deadline/tool/validation controls,
an exact selected context reader and no case-ID-based replacement snapshots.
Generation reads only approved inputs and metadata, never reference judgments.

Runner/settings/model/prompt/schema/input/code/corpus/retrieval freeze saved
EXCLUSIVELY in ignored evals/results/feature-003/live-v1/freeze.json before calls.
Input instructions and procedure query hints are input-bound additions to the
fixed application prompt. gpt-6-luna only; no model switch, T033 re-probe, hidden
SDK retries, case cherry-picking or post-output prompt/config tuning.

## Actual live execution

User approved maximum 104 transport attempts (13 executions * up to 8), including
errors/retry. Durable ledger counted before transport. Actual **86/104** attempts,
**87 reserved dispatch slots**, **82 HTTP 200 responses**, **4 unknown transport
outcomes**. A reserved slot is not proof of network dispatch. No further calls
after thirteen saved executions; unused budget is not used to improve outputs.

| Primary ID | Outcome | Seconds | Failure |
|---|---|---:|---|
| INV-H01 | failed | 64.611 | output_invalid |
| INV-H02 | needs_information | 52.123 | none |
| INV-H03 | failed | 39.271 | budget_exhausted |
| INV-H04 | failed | 37.302 | budget_exhausted |
| INV-H05 | needs_information | 35.156 | none |
| INV-H06 | failed | 38.675 | output_invalid |
| INV-H07 | failed | 13.255 | budget_exhausted |
| INV-H08 | failed | 36.973 | budget_exhausted |

All eight primary outcomes count; six failures do not disappear. At most two can
meet report quality targets, so >=7/8 is already unattainable. Actual claim support,
essential coverage and critical hallucination counts remain UNKNOWN until people
rate them, not zero/perfect/inferred from structural validation.

Demo outcomes: INV-D01 needs_information 30.365s; INV-D02 failed/budget_exhausted
7496.290s; INV-D03 failed/budget_exhausted 41.686s; INV-H01 needs_information
25.479s; INV-H05 failed/output_invalid 44.786s. **2/5**, not required >=4/5,
were validated/needs-information within 90s; not all terminal within 120s.
The observed 7496.290s value spans the interrupted/resumed work session and is
preserved exactly. Its root cause has not been established; no replacement run
or fabricated active-time-only duration is reported. Live performance target fails.

Usage reported for 82 dispatch results: input 296871, output 28325, total 325196
tokens. Five reserved dispatches lack reported usage, including unknown outcomes/
local refusal; do not assume zero billing. Spend/cost UNKNOWN, no invented price.
[Actual execution summary](feature-003-live-results.json),
[hash/usage/import audit](feature-003-live-audit-results.json).

All raw attempts/errors/budgets/tool traces/opaque continuation/usage/durations,
report/source bindings and immutable per-outcome seals remain under ignored
evals/results/feature-003/live-v1, with no overwrites. No secrets in shareable files.

## Actual verification and commands

Python 3.14.3, existing SDK/runtime/lockfiles. RED authored dataset projection
failed for intentionally unavailable old projection; GREEN targeted 24 PASS.
Authored dataset end-to-end test then 2 PASS. First full regression 756 PASS.
Input/fixture tests do not open real eval references or make API calls.

Before execution:
```powershell
$env:PYTHONPATH=Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-live-run.py
```
Network execution used approved sandbox escalation. Resume stayed with the SAME
running session/ledger; exit 0 after eight primary then five demos. No new runner
launched on session resume. Full transport cap never exceeded.

Only AFTER all eight primary files were sealed, explicit offline join:
```powershell
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-live-review-cards.py
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-live-summary.py
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-live-audit.py
```
All exit 0; 8 review cards, 31 primary and 17 secondary planned rating units;
actual ratings ZERO. No reviews.json with fictitious reviewers/scores was created.

Human importer RED: initial wrong-call-signature error was not business RED;
corrected authored assertion showed incomplete units were marked complete, exit 1.
Added exact-unit completeness/duplicate checks and preservation of both original
ratings/disagreements. Second RED: seven passing reports plus one critical error
incorrectly passed pack; corrected all-eight zero-critical requirement, exit 1
then GREEN. Uncertain remains unsupported, zero observations N/A, failures stay
in denominator, no-guidance is bound in explicit offline reference join. Unresolved
disagreement keeps acceptance pending, never silently overwrites human originals.

Final regression counts/commands recorded in next_work/evaluation evidence after
completion. No frontend edits, so frontend/build/browser not rerun here. No
source/cutoff/glossary/prompt changes after live generation started.

## Audit limits and review handoff

Actual audit verifies all live generation code/runner hashes, original evaluation
input/reference/split hashes, T055 retrieval freeze artifacts, every input/context/
corpus/retrieval/evidence binding, 13 result seals, transport count and known usage.
Runtime modules have no offline evaluator/reference loader imports; generation
function never opens references. T057 MockTransport all-turn canary evidence is
separate from this live run; this run does not claim recorded raw HTTP bodies or
independent packet-level canary inspection. No retrieval/ML evaluation conflation.

User: "Dobro, to cu kada zavrsis sa radom." Human review explicitly deferred.
Ready local [review index](../../evals/results/feature-003/live-v1/review-cards/README.md),
[Vedran units](../../evals/results/feature-003/live-v1/review-cards/primary-units.md),
[Milan units](../../evals/results/feature-003/live-v1/review-cards/secondary-units.md).
Vedran reviews all eight case cards; Milan independently H02/H03/H04/H06/H08.
Two actual reports need per-unit judgments; failure cards need actual failure
confirmation, identity/date/reason, not invented support ratings. Uncertain is
unsupported pending resolution. Templates carry null reviewer/date/judgments and
are NOT signatures or actual reviews. Assignment is not completed evaluation.

**One next step:** Vedran and Milan supply actual independent judgments/failure
confirmations against these concrete artifacts. Then import with
feature-003-finalize-reviews.py, retain/resolve disagreements without erasing them,
and complete final T060/T061 evidence. Do not mark those tasks complete now, or
start T062+ or retune/repeat this exposed holdout. No commit/push/merge/deploy.

## Final checks

Final `uv run --locked pytest backend/tests --basetemp "$runRoot/temp" -o
"cache_dir=$runRoot/cache" --tb=short`: **759 passed in 54.60s**, exit 0.
Actual absolute parent under root: .cache/t058-061-verified-ab9bd14112e74dccafad4c804ad71ad7.
Ruff PASS; diff/UTF-8/local links/key-exclusion checks PASS. One extra test after
initial 758-pass run covers all-eight critical-error pack rule; no generation code
changed after live freeze, and no live/holdout job rerun during regression.
Actual ratings remain zero; templates/index are concrete review handoff only.
