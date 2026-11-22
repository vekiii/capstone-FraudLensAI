# T095 v3 evaluator and development review packet — 2026-11-17

Status: implementation unit complete for the separate offline evaluator and
development draft. **T095 remains open; SC-002 remains UNMET**. No actual fresh
development selection, held-out freeze/acceptance experiment or provider call.

## Authority and branch

[Original request](../../prompts/development/003-t095-v3-implementation-20261117.md).
Milan Gavrić (`milangavric2003`) explicitly approved the v3 plan and implementation
on a new branch from feature03. Verified clean feature03 at
18e930ab4ad86e75f6f908b4a40a0a87def20e5b, then normal
`git switch -c feature03-retrieval-v3` succeeded, exit0. No target-branch merge,
push or other-feature implementation authorized/inferred. Local commit permitted,
using the existing branch's imperative English message style.

Plan approval records bind the original plan at18e930a and its LF hash in
[review.json](../../evals/investigation/retrieval-fresh-v3/review.json).
Milan subsequently stated he had not seen the old held-out questions. Recorded
as his declaration, not an independent audit. His earlier request to explain
held-out terminology was not treated as an exposure answer. No answer or approval
of new question/reference rows was inferred; those records remain pending.

Used speckit-implement for T095 only. Read root AGENTS.md and current next_work.md
first, then constitution/product context, feature spec/plan/tasks/design,
research/data model, relevant contracts/quickstart, previous T095/evaluation and
reliability evidence. Selected feature003 explicitly; prerequisite command exit0:

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
powershell -NoProfile -ExecutionPolicy Bypass -File .specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
```

Resolved actual absolute feature003 directory and research.md/data-model.md/
contracts/quickstart.md/tasks.md. Requirements checklist16/16,0 unchecked, PASS;
markers read-only. No extensions.yml/pre/post hooks. Existing ignores suffice for
caches/stores/results/credentials/dependencies; no installs or lock changes.
No delegation, actual .env read, network/provider use, old question/reference
parsing, source-store/manual-service interaction or frontend change.

## Implemented boundary and packet

New module: [retrieval_fresh_v3.py](../../backend/src/fraudlens/investigation/retrieval_fresh_v3.py).
Its separate CLI supports develop/freeze/execute/join; application runtime never
imports it. Old evaluator/CLI/retrieval policy/defaults/packs/results unchanged.

- Development requires actual plan and concrete reference review, exact review
  hashes, author/reviewer separation, novelty/exposure declaration, split-ID and
  intent-family separation,18 inputs with12 answerable/6 no-answer and per-language
  counts. It never opens held-out question/reference files. Only reviewed fresh
  development can select cutoffs; infeasible/error outcomes remain ineligible.
- Baseline body-only BM25 and candidate title/reviewed-glossary/script lookup use
  existing mechanics and a separate configuration version5. Neither is installed
  as the application default. Candidate cutoffs are not selected in this session.
- Freeze requires reviewed complete pack metadata, eligible development, unchanged
  review/source/manifest/document hashes, archived exact corpus digest and configs.
  It hashes held-out files without parsing their text and creates sealed output
  exclusively. LF hashes avoid platform newline drift.
- Execution requires a concrete freeze-bound human authorization for exactly40
  local searches/zero provider calls. Validates sources, inputs, archive/config
  content before claiming a one-shot ledger anchored to development selection;
  copying a freeze or changing output paths cannot reset that claim. Interrupted
  claims stay consumed; no automatic retry/deletion. Prediction never opens
  private references, including for hashing. Authorization records are trusted
  local records, not a new authentication/signature system.
- Join validates complete sealed predictions and exact identities/scores/ranks
  before reference access, then checks frozen private hashes and relevance sets.
  It reports both configurations, all20 question comparisons with regressions,
  language denominators, Recall/MRR, distinct false answers/no-answer errors and
  unchanged0.80/0.70/4-of-4 gate. Search failures count zero on answerable questions
  and never earn correct-no-match. Raw exceptions are not saved as result text.

[Concrete packet](../../evals/investigation/retrieval-fresh-v3/README.md) contains
18 new AI-authored development questions, proposed complete relevant passage sets,
input hashes/rationales, split metadata, protocol and honest pending reviews.
The [readable review table](../../evals/investigation/retrieval-fresh-v3/development-review.md)
links via README to all six exact source texts. Rows were authored from the
curated documents, without retrieval runs or old held-out content. Novelty and
semantic relevance still require a real reviewer; source hashes prove identity,
not that the AI's proposed relevance judgments are correct.

New held-out inputs/references are deliberately absent. Their separate authoring
must preserve the implementation/tuning boundary, avoid development intent
families/published diagnostics and receive actual independent reference review.
No placeholder answers, artificial human approvals or premature quality claim.

## Actual RED, GREEN and checks

Existing Windows environment: Python3.14.7, pytest9.2.0, Ruff0.17.4;
jsonschema4.26.0/pydantic2.14.3. No dependency resolution/installation.
Cache parent `.cache/t095-v3-20261117` created first. Commands used Tee-Object
with explicit exit-code propagation; unique basetemp/cache/output paths preserve
all earlier attempts.

```powershell
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_retrieval_fresh_v3.py -q --tb=short --basetemp=.cache/t095-v3-20261117/red-temp -o cache_dir=.cache/t095-v3-20261117/red-cache
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_retrieval_fresh_v3.py -q --tb=short --basetemp=.cache/t095-v3-20261117/green-temp -o cache_dir=.cache/t095-v3-20261117/green-cache
# Review RED/GREEN and final RED/GREEN use their distinct prefixes, listed below.
.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short --basetemp=.cache/t095-v3-20261117/final-full-temp -o cache_dir=.cache/t095-v3-20261117/final-full-cache
.venv/Scripts/python.exe -m ruff check backend
$env:PYTHONPATH = 'backend/src'
.venv/Scripts/python.exe -m fraudlens.investigation.retrieval_fresh_v3 develop --pack evals/investigation/retrieval-fresh-v3 --output .cache/t095-v3-20261117/real-development-blocked
git diff --check
```

| Stage | Actual outcome |
|---|---|
| Initial19 control/workflow tests before implementation |19 FAILED in2.71s, exit1, explicit missing-behavior stubs; no import/environment failure |
| First GREEN |19 PASS in5.29s, exit0 |
| Review tests for exact archive bytes / changed source documents |2 intended failures /24 PASS in6.79s, exit1 |
| GREEN after archive/document hash guards |26 PASS in6.65s, exit0 |
| Intermediate full suite before final two corrections |965 PASS in72.73s, exit0; not the final source snapshot |
| Final RED: explicit comparison outcome + SQLite error accounting |2 intended failures /25 PASS in12.45s, exit1 |
| Final focused GREEN |27 PASS in11.96s, exit0 |
| Ruff |PASS before/after final edits, exit0 |
| Actual unreviewed development CLI gate |Expected exit2; fixed blocked message; no output directory/search created |
| Packet structural/hash/link probe |PASS:18 rows,12/6 overall,4/2 per language, reviewed-source IDs, input/reference/review bindings; held-out absent |

Final full backend suite: **966 PASS in78.31s**, exit0, after the final runtime
changes. Ruff PASS, exit0. Frontend/typecheck/build/browser not rerun because
unchanged; no new manual acceptance claimed.

Final integrity audit PASS:511 baseline tracked files snapshotted before edits;
506 remain byte-identical, only five expected progress/design documents changed,
and exactly11 reviewed additions. All100 task markers unchanged,76 local Markdown
links resolve, explicit whitespace scan and git diff --check PASS. Original
runtime/evaluator/CLI/corpus/glossary/prompt/locks/evaluation inputs/references/
freezes/results and manual evidence retain their exact baseline bytes. Audit
output: `.cache/t095-v3-20261117/integrity.json`. Before/after extension hooks
absent. This proves scoped preservation, not semantic reference correctness.
All synthetic unit experiments use independent test-only packs/review identities
and temporary stores. Their successful metrics do not evaluate the real new pack
or change SC-002. No real question was searched in this unit.

Raw logs under `.cache/t095-v3-20261117/`: red.txt,green.txt,review-red.txt,
green2.txt,full.txt,final-red.txt,green3.txt,final-full.txt,ruff.txt,final-ruff.txt,
real-gate.txt,packet-check.txt. A source-file inspection initially guessed
ibm-fields.md in a newly drafted README; checked actual directory and corrected
to ibm-guide.md before link validation. No missing corpus input was substituted.

## Next human step and limits

Milan reviews the18 concrete development rows/rationales, reports actual row IDs
with objections or a scoped reference-review decision, and records identity/date.
Plan approval is already accepted and does not need repeating. After reference
review/necessary corrections, arrange separate held-out authoring/novelty review,
then scope development selection and freeze. Actual fresh acceptance still needs
authorization for the concrete frozen payload. T095 stays unchecked; no T094 or
T096–T098 work, semantic quality/live timing/full producer acceptance inferred.

Local publication preparation: normal git add failed creating .git/index.lock
with permission denied, leaving the index unchanged. Scoped escalation staged
the16 explicitly reviewed files successfully, exit0; no approval-review rejection.
Final staged scope/whitespace checks precede the authorized local commit.
No push/merge requested or performed. Git history identifies the committed snapshot.
