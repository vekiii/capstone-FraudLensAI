# T095 reviewed development selection — 2026-11-17

Outcome: **executed development-only, below quality targets**. Both variants
Recall@5/MRR@5=0.25/0.25 on12 answerable development questions;6/6 correct
no-answer outcomes, zero execution errors. Baseline wins the predeclared tie.
No actual deployment/default change. T095 stays OPEN; SC-002 UNMET.

## Actual user decision and scope

[Original request/steering](../../prompts/development/003-t095-development-selection-20261117.md).
Milan Gavrić (`milangavric2003`) said the documents/table were in order and
authorized continuation. Accepted as his concrete18-row development
question/reference decision with no reported row objections. Exact input/ref
hashes were already bound in review.json and remain unchanged. Recorded actual
actor/date/decision and his earlier old-holdout non-exposure declaration.

The development `novelty_confirmed` flag records acceptance of the presented
newly authored development packet/provenance. It does **not** claim Milan compared
unseen old questions, performed a semantic duplicate audit, authored the answers,
or gave independent held-out acceptance. These limits are explicit in the review
record. The separate new held-out review remains pending and its files absent.
No new human observation about exact per-row review actions is invented.

Subsequent English-only discussion was a question, explicitly not a code-change
request. No language scope change, added translation/embedding capability,
new synonyms, threshold relaxation, live provider use or old regrading occurred.
Questions about the meanings of0.50 and English outcomes were answered while
continuing this authorized development unit, not treated as implementation scope.

Applied speckit-implement to T095 only. Read AGENTS.md/next_work.md before work;
reviewed current spec/plan/tasks/v3 design, evaluator/tests, approved corpus and
glossary, contracts, governance and actual earlier evidence. Starting clean
feature03-retrieval-v3 atcc712513d3a30286c23a9f1059aaffaa5dbae79e; feature03 remains
18e930a. Explicit feature003 prerequisite exit0; requirements checklist16/16 PASS;
no before/after extension hooks. Existing ignore/environment/locks preserved;
no installations, .env reads, service/process interaction, push or merge.

## Demonstrated evaluator bookkeeping correction

Before selection, inspection found that later recording the separate held-out
author would invalidate a development selection solely because the whole protocol
file hash changed. The previous README required assigning that author first,
although development does not depend on held-out author identity/text. This could
force replay of the completed comparison. Corrected this within the existing
versioned boundary, before any actual development search.

Added a synthetic positive regression for completing held-out author/status
metadata after development and a negative glossary-change guard. Intended RED:
**1 failed/28 passed in11.85s**, exit1, with Development artifact hash mismatch
for metadata-only completion. GREEN after fix:**29 PASS in11.93s**, exit0.

Development now pins its exact meaning: protocol version, corpus manifest/version,
glossary and development author, plus unchanged input/reference/review/source/
corpus/config hashes. Adding held-out author/status metadata requires no rerun;
changing development semantics still rejects. A complete acceptance freeze still
hashes the **entire final protocol and both reviewed splits**. No runtime search
policy, authorization, held-out review, reference-isolation or quality gate relaxed.

## Executed commands and results

From repository root; existing Python3.14.7/pytest9.2.0/Ruff0.17.4 environment.
Unique cache/output paths; Tee-Object logs with explicit exit propagation.

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
powershell -NoProfile -ExecutionPolicy Bypass -File .specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_retrieval_fresh_v3.py -q --tb=short --basetemp=.cache/t095-v3-development-20261117/red-temp -o cache_dir=.cache/t095-v3-development-20261117/red-cache
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_retrieval_fresh_v3.py -q --tb=short --basetemp=.cache/t095-v3-development-20261117/green-temp -o cache_dir=.cache/t095-v3-development-20261117/green-cache
$env:PYTHONPATH = 'backend/src'
.venv/Scripts/python.exe -m fraudlens.investigation.retrieval_fresh_v3 develop --pack evals/investigation/retrieval-fresh-v3 --output .cache/t095-v3-development-20261117/selection
.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short --basetemp=.cache/t095-v3-development-20261117/full-temp -o cache_dir=.cache/t095-v3-development-20261117/full-cache
.venv/Scripts/python.exe -m ruff check backend
git diff --check
```

Real develop command executed **once**, exit0/status eligible:18 questions x2
configs=36 local searches. `eligible` means cutoff selection found nonzero recall
with zero development false answers; it does not mean SC-002 passed. A new ignored
store was created; original/manual stores untouched. No held-out file opened and
zero provider calls. No search replay/second tuning round or changed glossary.

Final full backend:**968 PASS in56.61s**, exit0. Ruff PASS, exit0. Frontend,
typecheck/build/browser/live evaluation NOT RUN; unchanged. Focused tests are
synthetic workflow controls, distinct from these actual development metrics.

[Committed ranks/scores/metrics and configurations](feature-003-t095-development-results-20261117.json).
They are an offline summary/filtering of the sealed raw development predictions,
not a second retrieval execution. Raw file:
`.cache/t095-v3-development-20261117/selection/selection.json`;
SHA-256 `47676d2757003938dc50bb56330f3f7f2d030476e876c9a43b145083b8e84956`;
sealed payload `165d50966eb803a8ac5dfad5d2af4e47f74abf4ade6c1ac052645c679766c62b`.
Raw logs:red.txt,green.txt,selection.txt,full.txt,ruff.txt under the same cache root.

| Development configuration | Selected cutoff | Overall Recall/MRR (12 answerable) | en (4) | sr-Latn (4) | sr-Cyrl (4) | Correct no-answer (6) |
|---|---|---|---|---|---|---|
| Baseline B3 |8.863342357405378 |0.25/0.25 |0.75/0.75 |0/0 |0/0 |6/6 |
| Candidate C3 |9.745718240901956 |0.25/0.25 |0.75/0.75 |0/0 |0/0 |6/6 |

Thresholds are **new development outputs only**. Original frozen cutoffs and demo
0.5 remain unchanged. Baseline is preselected by the prescribed tie-break;
candidate shows no aggregate improvement after cutoff. No release quality claim.

Read-only inspection of the preserved unthresholded rows explains the tradeoff:
both variants find the relevant source first for all4 English answerable queries,
but also return lexical hits for both English no-answer queries. The chosen
cutoffs reject those false answers and one answerable English result. Seven of
eight Serbian answerable queries have no lexical hits even at cutoff0; the
remaining one retrieves its relevant passage below first rank and is subsequently
rejected by the cutoff. This describes these exact queries, not all future input.
No cutoff lowered, no inflections/translations added to fit these results.

## Preserved history and next decision

Old held-out Recall/MRR0.50/0.50 on16 answerable+4 no-answer remains intact. Its
English8/8 perfect and Serbian8/8 zero language metrics are historical results,
not a current English-only acceptance proof. The new18-development sample uses
different questions/counts/thresholds and cannot establish performance degradation
or improvement by subtracting its0.25 from the old0.50.

The approved v3 design forbids widening this same candidate after its one bounded
comparison. Next concrete step: team reviews the actual development failure and
records a separately versioned next retrieval design or an explicit language-scope
decision. English-only has been discussed but NOT selected; current en/sr-Latn/
sr-Cyrl requirements remain. Do not consume a fresh acceptance holdout to tune
this failure. No fresh freeze/run or full-feature acceptance, T094/T096–T098 work.

Final integrity audit PASS:522 initial tracked files,511 byte-identical; exactly
11 expected evaluator/test/review/progress edits and three new prompt/evidence
files. All100 task markers unchanged;79 local Markdown links resolve. Raw seal,
current source/development projection/review bindings and summary metrics verified;
held-out files remain absent. git diff --check/explicit whitespace scan PASS.
Output `.cache/t095-v3-development-20261117/integrity.json`. Scope review found no
default/runtime/legacy-evaluator change. User-authorized local commit only.
Normal git add failed creating .git/index.lock with permission denied; the index
was unchanged. Authorized scoped Git metadata writes require sandbox escalation.
No push/merge requested or performed. Final local commit identity is in Git history.
