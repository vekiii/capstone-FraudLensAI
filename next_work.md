# Next work - FraudLens AI
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

Feature **002-data-and-risk-scoring is now specified, not implemented**:
- [Specification](specs/002-data-and-risk-scoring/spec.md): import/provenance, historical
  features and rules, bounded ML comparison, local explanations and dataset-backed case review.
- [Quality checklist](specs/002-data-and-risk-scoring/checklists/requirements.md): agent review
  complete; human feature review pending. No unresolved clarification markers.
- [Specification evidence](evidence/tasks/feature-002-specification.md) and
  [original request](prompts/development/002-data-and-risk-scoring-specification.md).
- Technical plan, new contracts, tasks and phase prompt template do not exist yet.
- No IBM dataset downloaded/audited, no model trained, no dependencies or product code changed.
- Defaults: chronological 70/15/15, strict past-only history, label-free operational data,
  one deployed explainable model compared to rules. AutoML is optional and bounded.
- Foundation's fixed-size IDs and amount/currency limits require explicit reviewed contract
  migration; do not relax validators or lose source precision silently.
- Current user request was specification only. No feature 002 implementation authorized.

## One concrete next step
Review feature 002 spec and request its technical plan (speckit-plan); use speckit-clarify
first only if the team identifies unresolved product choices. Planning must define the data
mapping/versioned contracts, concrete model/evaluation protocol and artifact boundaries before
tasks or implementation. Select specs/002-data-and-risk-scoring explicitly in the session;
the local .specify/feature.json now points there and is ignored, not shared through Git.
Review/publish documentation changes through the team's normal Git workflow; no agent commit/push.
Read AGENTS and this handoff before further work; preserve existing local changes.
