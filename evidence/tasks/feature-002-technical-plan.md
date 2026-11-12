# Feature 002 technical planning evidence

Date: 2026-11-12. Actual Git branch: `initialization`. Scope: documentation
and future Codex prompts only. [Original request](../../prompts/development/002-technical-plan-request-2026-11-12.md).

## Inputs and state

Read root AGENTS.md and next_work.md first, then the constitution,
original_idea.md, Feature 002 spec/checklist/review history, Feature 001
contracts/decisions and relevant backend/frontend implementation and tests.
The Phase 2 assignment requirements document is still unavailable: the
Feature 002 `checklists/requirements.md` is a specification-quality checklist.
No IBM AML source file is present under data/. Existing local changes predate
this planning unit and were preserved. No model, import or Feature 002 test
result was inferred from documentation.

Used the local speckit-plan workflow with explicit
`SPECIFY_FEATURE_DIRECTORY=specs/002-data-and-risk-scoring`. The first direct
setup script invocation was blocked by the current PowerShell execution
policy. A child PowerShell invocation with `-ExecutionPolicy Bypass` completed
the setup and returned the logical feature directory. It did not switch the
actual Git branch. The feature setup created the plan template, which was
filled with the design below. The optional `.specify/extensions.yml` hook
configuration is absent.

## Outputs and decisions

- [plan.md](../../specs/002-data-and-risk-scoring/plan.md): scope, architecture,
  proposed module layout, dependency order, RED/GREEN verification matrix,
  risk gates and handoff sequence.
- [research.md](../../specs/002-data-and-risk-scoring/research.md): 14 explicit
  local technical choices and alternatives, including source-audit gate,
  event/label separation, timestamp-group replay, deterministic rules,
  frozen evaluation/threshold policy and artifact trust.
- [data-model.md](../../specs/002-data-and-risk-scoring/data-model.md): canonical
  identity, financial/time facts, private labels, features, reports, scorer
  artifacts and completed-run state invariants.
- [API contract](../../specs/002-data-and-risk-scoring/contracts/api.md),
  [offline/scoring contract](../../specs/002-data-and-risk-scoring/contracts/data-and-scoring.md)
  and [JSON Schema](../../specs/002-data-and-risk-scoring/contracts/schemas.json):
  proposed v2 dataset responses and internal interfaces, pending affected
  producer/consumer review. Foundation fixture v1 stays strict.
- [quickstart.md](../../specs/002-data-and-risk-scoring/quickstart.md): planned
  commands and evidence expectations, clearly marked unexecuted.
- [Codex prompts](../../prompts/development/002-implementation-prompts.md):
  eight copy-ready prompts for task generation, source/contract audit,
  import, history/rules, model/evaluation, artifacts/explanations,
  publication/UI and convergence. Task IDs await tasks.md.

The local `data/artifacts/` path was found absent from `.gitignore`, though
raw and processed data paths are ignored. The plan, quickstart and first
implementation prompt explicitly gate artifact generation on adding and
checking that ignore rule. The inspection contract permits aggregate label
counts in its private report while prohibiting row-level label output by
default.

## Checks actually run

- `git status --short` and document/source inventory: planning files appear
  as intended; no source code or lockfile was changed in this unit.
- `python --version`: Python 3.13.3 in this shell. The final Python
  documentation check covered ten planning/prompt/handoff Markdown files:
  52 local links resolved and no unbalanced fences, missing final newlines
  or trailing-whitespace errors.
- `schemas.json` parsed as JSON with 23 `$defs`; its internal references
  resolved. Both API example JSON blocks parsed; the displayed rule
  contributions reconstruct the example score within floating tolerance.
- Full JSON Schema metaschema validation was **not run** because the current
  shell's Python lacks `jsonschema`. The current shell also could not invoke
  Python 3.14 through `py -3.14`; neither is an application test result.
- `git diff --check`: exit 0 for tracked changes. This command does not
  inspect untracked files; the Python documentation check covers the new
  Markdown files. `git branch --show-current` confirmed `initialization`.
  `Test-Path .specify/extensions.yml` returned False, so no Spec Kit
  extension hook was present.
- No backend/frontend tests, model training, dataset import, browser check,
  independent reproduction or human contract review was run for this unit.

## Open gates and next action

The source mapping/time/currency decisions need actual IBM release evidence;
Phase 2 compliance needs its authoritative assignment document. The v2
contract needs affected consumer review before integration. Generate
Feature 002 tasks.md from the current spec and plan, trace every FR/SC to
tasks and evidence, then begin the source/contract audit slice. Record actual
reviewers, commands and results when they exist. No Git commit or push was
performed.
