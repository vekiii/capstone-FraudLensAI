# Feature 002 — specification preparation

Date: 2026-11-12, Europe/Belgrade. Branch: initialization.
Starting revision: 33bcf62 (T025 and T028 finish). Initial working tree: clean.
Scope: specification only; no new application/data/model implementation.
Original request: [prompt record](../../prompts/development/002-data-and-risk-scoring-specification.md).

## Inputs and decisions
- Read AGENTS.md, next_work.md and the local speckit-specify skill before drafting.
- Applied speckit-specify using the resolved spec/checklist template stack. No extensions.yml
  exists, so before/after specify hooks are not registered. No Git branch creation hook ran.
- Used constitution 1.0.0, original_idea.md and implemented foundation contracts/settings/
  scoring/case boundaries. Data directory contained fixtures and README, no raw IBM release.
- Consulted the IBM repository and dataset authors' paper, linked from the spec. These do not
  replace the future acquired-data audit; no source-row/class-count measurements claimed.
- Feature number 002 follows the only existing feature directory 001. Existing Git branch kept.
- Defined five user stories, 26 functional requirements and nine success criteria.
- Explicit defaults cover 70/15/15 chronology, timestamp ties, a one-day historical window,
  pooled synthetic multi-bank view, finite review budgets and eligibility checks.
- Required explicit contract migration for larger identities and faithful currencies/amounts,
  with closed validation and the fixture regression preserved. No existing contract was edited.
- Retained optional bounded AutoML and baseline-first progress; no ML improvement asserted.
- Corrected AGENTS.md's hardcoded foundation selection so future commands select the requested
  feature. Updated ignored local .specify/feature.json and tracked next_work.md.

## Verification and honest limits
Quality checklist: [requirements.md](../../specs/002-data-and-risk-scoring/checklists/requirements.md).
Agent review covers all 16 checklist criteria and requirement/story/outcome mapping.
No unresolved clarification markers; technical design choices are explicitly planning work.
During review, clarified that holdout *labels/answers* must not affect operations, while
observable heldout event facts may be used in their allowed scoring/history role. Explained
review samples do not require manufacturing five threshold-triggered alerts.

Commands/checks for this documentation change:
- `powershell -NoProfile -ExecutionPolicy Bypass -File .specify/scripts/powershell/resolve-template.ps1 spec-template -Json`: exit 0; composed template used as starting spec.
- Same resolver for checklist-template: exit 0; checklist structure reviewed.
- Paths-only feature resolution, document/link/ID/placeholder/whitespace checks and final
  git diff review are recorded in the completion note below after actual execution.

RED/GREEN: not applicable to specification writing. No dependencies installed, raw data
downloaded, models fit, metrics computed, browser checks or application regressions run.
Human feature review: pending; checklist marks are agent document-quality review only.
Existing foundation acceptance evidence is historical and unchanged.

## Next action
Review the spec, clarify only if needed, then run speckit-plan for
specs/002-data-and-risk-scoring. Plan/contracts/tasks are not generated in this request.
No commit, push, merge or deployment performed.

## Completion verification
- `check-prerequisites.ps1 -PathsOnly -Json` with explicit feature 002 selection: exit 0;
  FEATURE_DIR/FEATURE_SPEC resolve to the new directory. Paths-only does not assert that
  plan/tasks exist. Its logical BRANCH value is the feature name; actual Git branch remains
  initialization, confirmed by git status.
- A dependency-free Python documentation check: exit 0; five stories, FR-001–026 and SC-001–009
  unique/sequential, 16 checked quality criteria, required section order, local links, UTF-8,
  fence balance, whitespace and no unresolved template tokens all PASS.
- Local feature.json points to 002 and `git check-ignore .specify/feature.json` confirms it
  is ignored. New feature has no plan.md or tasks.md, as expected for this request.
- `git diff --check`: exit 0. Git notes normal LF/CRLF conversion for AGENTS.md, not a failure.
- Reviewed tracked diff paths: AGENTS.md and next_work.md only; new specification/checklist,
  prompt and evidence files are the intended untracked additions. No source/lockfile change.
- Final specify hook check: extensions.yml absent, no before/after hooks to execute.

## Adversarial-review revision — 2026-11-12

Prompt: [review remediation request](../../prompts/development/002-review-remediation-2026-11-12.md).
Input review: [002-review.md](../../prompts/development/002-review.md), including
the second-level reclassification, scientific/data-engineering review and
Foundation compatibility review. Scope: specification and quality-checklist
revision only; no product code, dataset, model or contract implementation.

The revised spec keeps FR-001–FR-026 and SC-001–SC-009. It clarifies event-fact
validity versus label eligibility, import completeness, identity before filtering,
unknown-column policy, decimal/time fidelity, point-in-time replay, a genuine
label-free rule baseline, per-scorer validation-only threshold policy, zero alerts,
K-boundary ties, holdout consumption, artifact checking, explanation fidelity,
atomic completed-run selection and versioned Foundation migration. Added acceptance
scenarios, a label-role table, proposed interface sketches and ten contributor
work packages. Exact observed IBM schema, numeric rule values, lookback boundary,
threshold objective, local storage mechanism and resource budget remain planning
decisions. Authoritative Phase 2 assignment requirements remain unavailable, so
course compliance is not asserted.

The updated checklist records open human, Phase 2, contract/plan and implementation
gates. Its checked document-quality items do not claim Feature 002 is implemented.
RED/GREEN and runtime tests are not applicable to this documentation revision;
the historical Foundation test results are not new runs.

Documentation verification actually run for this revision:
- PowerShell structure check: exit 0; five user stories, unique sequential
  FR-001–FR-026 and SC-001–SC-009, no clarification placeholders.
- Local-link check of the five touched handoff/spec/checklist/prompt/evidence
  documents: exit 0; all local Markdown link targets resolve. An initial helper
  invocation used an empty parent path for root next_work.md and printed Join-Path
  errors; the corrected strict-error run above is the valid result.
- git diff --check on the revised tracked documents: exit 0; no whitespace errors.
- Repository inventory: only Feature 002 spec/checklist exist under its feature
  directory; data/ contains README and the Foundation fixture, no raw IBM dataset.
  The only repository requirements.md files are feature quality checklists.
