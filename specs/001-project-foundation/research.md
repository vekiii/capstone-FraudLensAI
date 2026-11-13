# Foundation Research and Decisions

Date: 2026-11-11. Research completed for planning; no runtime compatibility claim is made.
No unresolved technical decisions block the foundation.

## 1. Minimal web stack
**Decision**: FastAPI + Vite vanilla TypeScript, as approved by the team.
**Rationale**: Small local application; no extra frontend framework or orchestration needed.
**Alternatives considered**: Streamlit would change the approved frontend; React adds scope.
Vite supports vanilla-ts. User-approved runtime update: choose Python 3.14 and
Node 24; verify patch releases and dependency resolution when creating lockfiles.
Sources: [Vite](https://vite.dev/guide/), [FastAPI](https://fastapi.tiangolo.com/).

## 2. Tests and reproducibility
**Decision**: pytest/TestClient/httpx, focused Vitest DOM tests, typecheck/build and browser smoke.
**Rationale**: Test actual contracts and failure states without an external model. Use uv.lock,
npm lockfile and recorded runtimes for reproducibility. Browser smoke remains explicitly manual.
**Alternatives considered**: A full browser automation platform is unnecessary for this small
foundation; it may be reconsidered for larger user journeys with team scope review.
Sources: [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/),
[uv locked sync](https://docs.astral.sh/uv/concepts/projects/sync/),
[Vitest](https://vitest.dev/guide/).

## 3. Remove ML from the critical path
**Decision**: Inject a scorer protocol and an in-memory repository. Fixture outputs explicitly
identify synthetic provenance; public payloads exclude labels. No database yet.
**Rationale**: UI and delivery can progress while the data/model owner experiments separately.
**Alternatives considered**: Training first delays everyone; a scoring microservice adds no
necessary value to foundation. Decisions follow original_idea.md and constitution VIII/X.

## 4. Git and Spec-kit state
**Decision**: Track shared `.agents/skills` and `.specify` templates/scripts/memory/init metadata.
Keep local `feature.json` and other paths listed in `.specify/.gitignore` ignored.
**Rationale**: Teammates need the same workflows and constitution, not each other's active state.
**Alternatives considered**: Blanket ignore would remove shared governance from checkout.
Evidence: local `.specify/.gitignore` and `init-options.json` (Spec-kit 1.4.0).
Actual Git branch is initialization; Spec-kit may report the feature name as its logical branch.
For a new checkout, select `specs/001-project-foundation` explicitly before downstream commands.

## 5. Educational security boundary
**Decision**: Fixture-only local read-only demo bound to loopback, no auth claim or secret inputs.
**Rationale**: Production auth is a later scoped design, not a hidden requirement of bootstrap.
**Alternatives considered**: Public hosting or real customer data would need additional design.
Input validation and generic errors still apply to local demonstration.

## Research workflow
A read-only research agent checked official stack/testing/locking sources and existing ignore
configuration as requested by speckit-plan. No application code or third-party packages installed.
