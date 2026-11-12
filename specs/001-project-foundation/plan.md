# Implementation Plan: Project Foundation

**Branch**: `initialization` | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)
**Input**: `specs/001-project-foundation/spec.md`
**Status**: Implemented through T023; phase 6 verification recorded in ../../evidence/tasks/phase-06-handoff.md. Peer reproduction and human review pending.

## Summary
Build a local read-only fixture journey with FastAPI and Vite vanilla TypeScript. Deliver
case list/detail, explicit source labeling, replaceable scorer and reproducible development
checks. Do not implement later ML, RAG or investigation features.

## Technical Context
**Language/Version**: Python 3.14.x; TypeScript; Node.js 24.x.
Record exact runtime patch versions in implementation, rather than inventing installed versions.
**Primary Dependencies**: FastAPI/Pydantic, Uvicorn, pytest/httpx; Vite, TypeScript,
Vitest with jsdom for DOM/fetch behavior tests. Resolve compatible versions and commit
`uv.lock` and `frontend/package-lock.json` in setup; use locked installs afterward.
**Storage**: In-memory fixture repository reading three small synthetic records. No database.
**Testing**: pytest contract/integration/unit checks; Vitest UI boundary checks; TypeScript
typecheck and Vite build; manual browser smoke with a second teammate.
**Target Platform**: Windows PowerShell, local browser; loopback-only services.
**Project Type**: Web application in one repository.
**Performance Goals**: No production throughput claim. Correct local journey with three cases;
frontend request timeout 5 seconds and visible retry on timeout/unavailability.
**Constraints**: No keys, model download or real dataset for foundation; no external requests
at application runtime. First dependency installation can require network access.
**Scale/Scope**: Three fixture cases, two views in the first MVP screen; four future workstreams.

## Constitution Check
Pre-research: PASS by design, not by executed tests. I/X: bounded foundation, approved stack;
II/III: specified stories and test-first tasks; IV/VI: no LLM or disposition writes;
V/VII: synthetic sources, no labels; VIII: scorer protocol; IX: lockfiles and honest evidence.
Post-design: PASS. No new product techniques or infrastructure outside approved scope.
The local demo has no authentication; it MUST NOT be described as secure multi-user hosting.

## Project Structure
### Documentation (this feature)
```text
specs/001-project-foundation/
  spec.md
  plan.md
  research.md
  data-model.md
  quickstart.md
  contracts/api.md
  contracts/schemas.json
  checklists/requirements.md
  tasks.md
```

### Source Code (planned, not created by this planning step)
```text
README.md
AGENTS.md
.python-version
pyproject.toml
uv.lock
backend/src/fraudlens/
  main.py
  contracts.py
  settings.py
  cases.py
  scoring.py
backend/tests/{contracts,integration,unit}/
frontend/
  package.json
  package-lock.json
  index.html
  src/{main.ts,api.ts,contracts.ts,views.ts,styles.css}
  tests/{api.test.ts,views.test.ts}
data/fixtures/cases.json
data/README.md
prompts/{README.md,app/,development/}
evidence/{README.md,templates/task.md,tasks/}
docs/decisions/foundation.md
```
**Structure Decision**: Modular backend and a small frontend; tests stay beside their subsystem.
Feature contracts are authoritative design artifacts, not a second root contracts copy.
Scoring replacement is a Python protocol, not an additional network service.
Create future directories only when they have a meaningful file, not empty scaffolding.

## Design Decisions
- Serve `GET /api/health`, `GET /api/cases`, `GET /api/cases/{case_id}`. See contracts/api.md.
- Bind backend to 127.0.0.1:8000 and Vite to 127.0.0.1:5173 with strict port selection.
- Vite proxies `/api` to the backend; the browser uses relative URLs. No wildcard CORS.
- Explicit settings: `APP_MODE=fixture` (only supported mode); local fixture path. No secrets
  or provider variables required. Health reports mode, not an ML-ready claim.
- UI list selection uses a selected-case identifier and aborts/ignores obsolete fetch results;
  never renders prior case details under a new selection. Retry is an explicit user action.
- Errors use the documented envelope; unexpected errors return generic text without traces,
  paths or data. Test internal logging for redaction if logging is added.
- Backend validators and frontend boundary decoding enforce closed schemas; invalid upstream
  payloads become explicit errors, not successful values via TypeScript casts.
- Tests compare behavior and source of truth; do not test directory counts or duplicate code.
- Evidence and development prompt templates precede business implementation. No invented RED.
- Keep `.agents/skills`, shared `.specify` content, specifications, fixtures and lockfiles in
  Git. Honor `.specify/.gitignore`; exclude venvs, node_modules, build/cache output, secrets,
  raw/processed data and local generated eval output. Preserve existing ignore entries.

## Delivery and Verification
US1 establishes toolchain/config and onboarding. US2 builds API + UI against the same
contracts. US3 proves injection through a test scorer and documents the handoff/evidence rules.
See tasks.md for ordering and quickstart.md for executable checks after implementation.
No CI service, containers or deployment required by this feature.

## Complexity Tracking
No constitution exceptions requested. JSON Schema is a design contract; use Pydantic on the
backend and explicit frontend decoding rather than adding a code generation platform.

## Acceptance update - 2026-11-12
Earlier pending acceptance statements above are superseded by the team's reported
joint setup verification and code/contracts/evidence review. T025/SC-001 and T028
are complete; see evidence/tasks/peer-reproduction.md and human-review.md from the
repository root. No additional automated/browser executions claimed by this update.
