# FraudLens AI

Educational AML prototype. Current delivery includes foundation phases 1–3: strict
contracts, local backend startup/health and a minimal vanilla TypeScript frontend
showing the project name. T014 adds three synthetic transaction fixtures and a
validated loader; T015 adds deterministic illustrative scoring and a validated
case-scoring boundary. T016 serves GET /api/cases and GET /api/cases/{case_id}
with generic errors. T017 adds a typed frontend API client with strict runtime
decoding, timeout and cancellation. T018 adds case list/detail/back, explicit states,
retry and stale-response protection. T019 regression/live HTTP passes; interactive
browser verification is pending because browser access was unavailable.

## Prerequisites and setup
Use Git, uv, Python 3.14.x, Node 24.x and npm in Windows PowerShell.
Versions checked during this phase: Python 3.14.3, uv 0.10.9,
Node v24.20.0 and npm 11.19.0. Run commands from the repository root.

For an existing checkout, install the committed locked dependencies:
```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
uv sync --locked --group dev
npm.cmd --prefix frontend ci
```
The workspace-local uv cache avoids machine-cache access restrictions. npm.cmd
avoids npm.ps1 execution-policy restrictions without changing system policy.
Initial dependency installation needs network access. Runtime startup and health
need no provider key, model, RAG corpus, dataset or external AI service.
No .env file or fixture data file is needed for health.

Lockfile creation was performed during initial setup with `uv lock` and
`npm.cmd --prefix frontend install`; those resolve dependencies and generate
uv.lock / frontend/package-lock.json. Do not repeat them for routine installs or
hand-edit lockfile hashes. Use locked installs above; intentional dependency
changes require review and genuine lockfile regeneration.

## Run in two terminals
In terminal 1, from repository root:
```powershell
uv run --locked uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8000
```
In terminal 2, from repository root:
```powershell
npm.cmd --prefix frontend run dev -- --host 127.0.0.1 --port 5173 --strictPort
```
Open http://127.0.0.1:5173 for the synthetic case inspection UI. Vite forwards relative
/api requests to http://127.0.0.1:8000. Both services bind to loopback only;
this is a local demo, with no production multi-user security or ML-ready claim.
Stop your own foreground servers with Ctrl+C.

In another PowerShell terminal check health directly and through the proxy:
```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/health'
Invoke-RestMethod -Uri 'http://127.0.0.1:5173/api/health'
```
Both must return HTTP 200 JSON `{"status":"ok","mode":"fixture"}`.
The case API is available directly and through the same proxy:
```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/cases'
Invoke-RestMethod -Uri 'http://127.0.0.1:5173/api/cases/CASE-001'
```
Unknown CASE-999 returns 404; malformed CASE-1 returns 422. Errors use the closed
`{"error":{"code":"...","message":"..."}}` envelope. See T016 evidence for actual bodies.
APP_MODE defaults to fixture and is the only supported value. If APP_MODE is set
otherwise, startup fails validation; remove it or explicitly set it to fixture.
Settings resolve data/fixtures/cases.json relative to the repository, but startup
and health do not open it. T014's three synthetic cases are stored there without scores.

## Checks and build
```powershell
uv run --locked pytest backend/tests/integration/test_startup.py
uv run --locked pytest backend/tests
uv run --locked ruff check backend
npm.cmd --prefix frontend run test -- --run
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend run build
git diff --check
```
All 291 backend tests pass, including the unchanged 49 T012 API/scorer tests and
8 additional framework/logging checks (rerun successfully in T019).
The frontend has 151 passing tests, including all 82 original API and 19 DOM tests.
T019 typecheck/build/Ruff pass. See T012–T019 evidence for actual results and limits.
Build output frontend/dist/ is local and ignored; it is not a deployment.

The [fixture scoring rule](docs/decisions/fixture-scoring.md) rotates illustrative
constants by transaction ID and copies transaction time into scored_at. Results
are explicitly synthetic, without ML inference, calibrated probabilities or labels.

The [target quickstart](specs/001-project-foundation/quickstart.md) also describes
three-case navigation and failure-state checks. T019's real-server/browser
verification is partial: live backend/proxy HTTP checks pass, but browser access
failed. Do not claim interactive verification from automated DOM tests.

## Evidence and next work
See [T019 integrated verification and limits](evidence/tasks/T019.md),
[T018 UI/DOM verification](evidence/tasks/T018.md),
[T017 frontend API/validation](evidence/tasks/T017.md),
[T016 API/error verification](evidence/tasks/T016.md),
[T015 scorer/validation](evidence/tasks/T015.md),
[T014 fixtures/validation](evidence/tasks/T014.md),
[T012 backend RED](evidence/tasks/T012.md), [T013 frontend RED](evidence/tasks/T013.md),
[phase 3 handoff](evidence/tasks/phase-03-handoff.md),
[startup RED/GREEN](evidence/tasks/T008.md), [setup/smoke](evidence/tasks/T011.md)
and [next_work.md](next_work.md). Human review and independent second-member
reproduction remain pending (SC-001). Local fixture checks are not ML evaluation.
