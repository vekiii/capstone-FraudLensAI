# Next work - FraudLens AI

## Current feature 003 setup handoff - 2026-11-13
Branch feature03; phase-1 baseline fd6d724b83a3a35cee9bf821651e56ffc269b2f9.
T001-T004 complete. Isolated investigation settings/package, documented .env.example,
81 configuration tests and runtime/evaluation data policies delivered.
Actual RED: 81 executed failures at unimplemented importable config boundary.
GREEN: 81 passed; foundation startup 8 passed; full backend 391 passed; Ruff PASS.
Runtime: Python 3.14.3, uv 0.10.9, Node 24.20.0, npm 11.19.0. Existing locked sync
succeeded; no dependency/lockfile, foundation APP_MODE, ML or frontend modifications.
Ignore boundaries verified; generated DB/index/evaluation/temp outputs local only.
Original untracked feature3_tasks_prompt.md preserved. No active technical blocker.
Human review, provider model/access/corpus and producer review remain pending.
No provider/SDK/store/retrieval/workflow/UI/CLI/evaluation implementation or execution.
No Git publication performed.

Evidence: [setup](evidence/tasks/feature-003-setup.md),
[handoff](evidence/tasks/feature-003-phase-01-handoff.md),
[original prompt](prompts/development/003-investigation-phase-01.md).

**One concrete next step:** separately implement Phase 2 T005-T012 starting with
T005 contract RED tests, explicitly selecting specs/003-ai-investigation. This
handoff does not authorize beginning that phase or probing a live provider.

Previous handoffs below are historical and superseded where this section differs.

# Next work - FraudLens AI

## Current feature 003 plan/tasks handoff - 2026-11-13

Branch `feature03`: generated [plan](specs/003-ai-investigation/plan.md),
[research](specs/003-ai-investigation/research.md),
[data model](specs/003-ai-investigation/data-model.md),
[contracts](specs/003-ai-investigation/contracts/api.md),
[evaluation protocol](specs/003-ai-investigation/evaluation.md),
[quickstart target](specs/003-ai-investigation/quickstart.md) and
[67 unchecked tasks](specs/003-ai-investigation/tasks.md).
No implementation, provider/key access, corpus ingestion, runtime tests or
human acceptance performed. Existing spec and feature 002/ML files preserved.
Design checks passed for schemas/eight authored examples, IDs/dependencies,
FR/SC coverage and document links/whitespace; these are not runtime evaluation.

Evidence: [actual workflow/results/limits](evidence/tasks/feature-003-plan-and-tasks.md);
[original request](prompts/development/003-plan-and-tasks-request-2026-11-13.md).
Separate provider-access and producer-review gates do not block fixture work.
The literal producer schema reference at `2dd815d` is a proposal/test snapshot,
not current implementation or recorded human approval. Model ID/access remains
unverified. No commit/push performed.

**One concrete next step:** implement **Phase 1, T001-T004**, using
`$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'`, preserving
foundation and recording actual setup/RED/GREEN evidence. Continue with
T005-T012 after setup; do not skip from this plan straight to live evaluation.

Previous specification/merge handoffs below are historical.

## Current feature 003 handoff - 2026-11-13

On user-created branch `feature03`, baseline `0fbe313`, created
[003-ai-investigation/spec.md](specs/003-ai-investigation/spec.md) and its
[quality checklist](specs/003-ai-investigation/checklists/requirements.md).
Specification covers curated RAG, context/evidence tools, bounded AI report
generation, saved state, analyst disposition and independent evaluation.
Status: specification only, agent-reviewed; not implemented or team-accepted.
Documentation structure/ID/link/placeholder checks and Git whitespace passed;
no runtime tests or live-provider evaluation were performed.
Feature 002/ML files were not changed. The latest inspected producer reference
is `origin/model-implementations` at `2dd815d`; its contracts are newer than
this main baseline, so planning must reconcile them before dataset integration.

OpenAI key availability and intended GPT-6 Luna name are user-reported; actual
API model ID, access and capabilities have NOT been verified. No secret read
or provider call occurred. Development may use clearly labeled fixtures while
live report evaluation remains pending.

[Original request](prompts/development/003-specification-request-2026-11-13.md);
[workflow evidence and limits](evidence/tasks/feature-003-specification.md).
One concrete next step: run `speckit-plan` with
`$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'`, defining
schemas, provider/evidence boundaries and evaluation rubric; generate tasks
only after the plan. No automatic commit/push.

Earlier merge/recovery sections below are historical and do not describe
the current feature03 branch or current remote ML implementation state.

## Latest recovery - 2026-11-13

The user's pull of feature 002 into main started a merge with `0f5ad9a` and
conflicted in this file. Verification found **566 passed / 6 failed** on Windows;
the same CRLF/LF test-helper issue remains. Ran `git merge --abort` successfully.
Main is still `b9650a1`; the new feature commit remains available on
`origin/002-data-and-risk-scoring`. No push, completed feature 002 merge or code
fix occurred. Only this handoff and the recovery evidence were subsequently
edited, left uncommitted.
See [actual recovery checks](evidence/tasks/main-pull-recovery-2026-11-13.md).
Next step remains fixing and verifying the hash expectation on the feature
branch before another merge review. Use `git fetch origin` to obtain updates
without merging a feature branch into whichever branch is currently active.

## Current handoff - main merge review, 2026-11-13

Main incorporates verified `origin/initialization` at `f37e67a`, preserving its
history. Feature 001 is accepted in its synthetic fixture scope. Fresh checks:
310 backend tests, 151 frontend tests, Ruff, TypeScript typecheck and build passed.
The prepared main runtime is identical to the isolated tested candidate.
See [merge review and limitations](evidence/tasks/main-merge-review-2026-11-13.md).
No push was performed. Use `git log -1` for the resulting local merge commit.

Feature 002 specification/planning documents are present on main; its importer
implementation is NOT merged. `origin/002-data-and-risk-scoring` was `5530608`:
459 backend tests passed, six failed on Windows because a test helper compares a
raw CRLF mapping hash against the approved LF-normalized hash. The prior macOS
success and full IBM import are historical branch evidence, not fresh Windows
verification. Remaining feature 002 implementation is still incomplete.

**One concrete next step:** on the feature 002 branch, correct the helper's
expected-hash calculation to match the approved normalization policy, cover
LF/CRLF explicitly, and rerun backend/regression checks before another merge
review. Read that branch's current tasks and evidence before changing it. Do not
restart feature 002 from the older planning snapshot on main.

Important: the local branch named `initialization` already points to `5530608`,
unlike `origin/initialization` at `f37e67a`. This review deliberately selected the
remote snapshot by exact commit. Local branch pointers and collaborators' work
were preserved. Do not blindly merge the local initialization branch into main.

## Historical pre-merge handoff (preserved below)

Updated 2026-11-12 Europe/Belgrade. Branch initialization; HEAD at specification start: 33bcf62.

## Current state
Feature 001-project-foundation completed/accepted in its local synthetic-demo scope:
T001-T028 checked. Vedran Mitic confirms joint setup verification and human
code/contracts/evidence review by all team members. No individual signatures or
separate-machine installations claimed. Historical pending entries superseded.
- Peer results: 310 backend passed (exit 0), 151 frontend passed, Ruff,
  typecheck/build, health/UI/retry and 404/422 results recorded.
- Project Python 3.14.3; system py 3.14.7; Node 24.20.0; npm 11.19.0; uv 0.10.9.
- Prior temp permission errors resolved through unique workspace temp/cache paths.
- Known Starlette/httpx warning remains, no outstanding failure reported.
- Evidence: evidence/tasks/peer-reproduction.md, human-review.md,
  phase-06-handoff.md and foundation-validation.md. Browser evidence remains the
  historical T019 run; no new browser/test run during acceptance recording.

Feature **002-data-and-risk-scoring is revised after adversarial review, not implemented**:
- [Specification](specs/002-data-and-risk-scoring/spec.md): import/provenance, historical
  features and rules, bounded ML comparison, local explanations and dataset-backed case review.
- [Quality checklist](specs/002-data-and-risk-scoring/checklists/requirements.md): agent
  document review recorded; human, Phase 2, technical-plan and implementation gates
  remain open. No unresolved clarification markers.
- [Specification evidence](evidence/tasks/feature-002-specification.md) and
  [original request](prompts/development/002-data-and-risk-scoring-specification.md).
- [Technical plan](specs/002-data-and-risk-scoring/plan.md),
  [research decisions](specs/002-data-and-risk-scoring/research.md),
  [data model](specs/002-data-and-risk-scoring/data-model.md),
  [v2 contracts](specs/002-data-and-risk-scoring/contracts/api.md),
  [quickstart](specs/002-data-and-risk-scoring/quickstart.md) and
  [Codex prompts](prompts/development/002-implementation-prompts.md) are drafted.
  tasks.md, source audit, affected-consumer contract review, implementation and
  actual Feature 002 verification remain pending.
- [Adversarial review transcript](prompts/development/002-review.md) is reflected in the
  revised specification: label-independent event history, meaningful rule baseline,
  temporal/threshold/evaluation safeguards, import/run completion, contract migration,
  acceptance scenarios and a proposed contributor code/task handoff. See
  [revision evidence](evidence/tasks/feature-002-specification.md).
- Authoritative Phase 2 assignment requirements remain unavailable; the checklist
  is not that source and no Phase 2 compliance claim is made.
- No IBM dataset downloaded/audited, no model trained, no dependencies or product code changed.
- Defaults: chronological 70/15/15, strict past-only history, label-free operational data,
  one deployed explainable model compared to rules. AutoML is optional and bounded.
- Foundation's fixed-size IDs and amount/currency limits require explicit reviewed contract
  migration; do not relax validators or lose source precision silently.
- The preceding planning request authorized technical planning and future
  prompts only. No Feature 002 implementation was performed by that unit.

## One concrete next step
Generate Feature 002 tasks.md from the current spec and technical plan using
the [Prompt 0 task-generation handoff](prompts/development/002-implementation-prompts.md),
tracing FR-001–026 and SC-001–009 to tasks and evidence. Then begin the source audit
and affected-consumer contract review. Track the missing authoritative Phase 2
assignment as an open compliance source. Select specs/002-data-and-risk-scoring
explicitly; the local .specify/feature.json is ignored, not shared through Git.
Review/publish documentation changes through the team's normal Git workflow;
the current publication request is recorded separately below.
Read AGENTS and this handoff before further work; preserve existing local changes.

## Contribution evidence report added 2026-11-12

- Added [consolidated evidence and contribution plan](evidence/tasks/project-evidence-plan-2026-11-12.md),
  with the complete 19-commit ledger through f63bffe, three identifiable contributors,
  task-level attribution, shared T019 credit and future evidence/time capture plan.
- [Reproducible calculation](evidence/tasks/project-evidence-calculations-2026-11-12.json)
  gives 10.76 provisional person-hours centrally, 7.17–14.34 under explicit
  publication-window assumptions. These are not measured hours or confidence bounds.
  No work/hours assigned to an unnamed fourth member, per current user clarification.
- Documentation only; no application tests/browser runs, feature implementation,
  acceptance marker changes or Git commit/push. Historical runtime/test results above
  remain unchanged. See report for source limitations and participant confirmation needs.
- Audit verification passed: calculation script; 19-row Git/date/author reconciliation;
  independent arithmetic; 43 local links; UTF-8/fences/whitespace/helper syntax;
  historical test-count reconciliation. Source inventory covers 69 pinned files.
- This contribution report does not authorize implementation; the current next
  development step is Feature 002 task generation described above.

## Feature 002 technical-plan handoff added 2026-11-12

- See [planning evidence](evidence/tasks/feature-002-technical-plan.md) and
  [original request](prompts/development/002-technical-plan-request-2026-11-12.md).
  The plan and supporting research/data/API/scoring contracts, JSON Schema,
  quickstart and eight future Codex prompts are documentation proposals.
- The current shell lacks an invokable Python 3.14 and `jsonschema`; JSON parse,
  internal schema references, example arithmetic and 52 local Markdown links
  were checked with Python 3.13.3. `git diff --check` passed. No application
  tests or IBM import/model run occurred.
- `data/artifacts/` is not yet ignored by Git. The first implementation slice
  must add/check that ignore rule before artifact generation. Raw/processed
  paths are already ignored. Source audit, Phase 2 document, contract review,
  tasks, human review and independent reproduction are open.
- This handoff preserves existing local edits and makes no Git commit/push.

## Documentation publication request — 2026-11-12

- The user explicitly requested commits and a push for all pending documentation;
  see the [original publication request](prompts/development/002-publication-request-2026-11-12.md).
  That instruction supersedes earlier no-commit/no-push statements for this
  session. It does not expand Feature 002 implementation scope.
- The [contribution report addendum](evidence/tasks/project-evidence-plan-2026-11-12.md)
  names the four publication commits and their distinct contents. The historical
  19-commit time calculation remains pinned and does not count unmeasured hours
  from these documentation commits.
- Verify the current local/remote branch state with Git. The concrete next
  development step remains Feature 002 tasks.md generation and source/contract
  audit; human, Phase 2, dataset and implementation gates remain open.

## Feature 003 phase 1 in progress - 2026-11-13
T001 complete. Next T002 configuration RED. Evidence: evidence/tasks/feature-003-setup.md. No provider initialization or runtime composition.

T002 RED recorded: 81 executed configuration failures, no import/setup errors. Next T003 configuration/GREEN.

Feature 003 setup: T003 GREEN 81/Ruff PASS. T004 knowledge/evaluation policies written; final ignore/startup/full-regression verification next.
