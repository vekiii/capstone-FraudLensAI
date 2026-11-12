# FraudLens AI

Educational AML prototype. Current delivery is foundation phases 1–3: strict
contracts, local backend startup/health and a minimal vanilla TypeScript frontend
showing the project name. Case list/detail, fixture scoring and their browser
acceptance journey belong to phase 4 and do not work yet.

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
Open http://127.0.0.1:5173 for the project-name scaffold. Vite forwards relative
/api requests to http://127.0.0.1:8000. Both services bind to loopback only;
this is a local demo, with no production multi-user security or ML-ready claim.
Stop your own foreground servers with Ctrl+C.

In another PowerShell terminal check health directly and through the proxy:
```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/health'
Invoke-RestMethod -Uri 'http://127.0.0.1:5173/api/health'
```
Both must return HTTP 200 JSON `{"status":"ok","mode":"fixture"}`.
APP_MODE defaults to fixture and is the only supported value. If APP_MODE is set
otherwise, startup fails validation; remove it or explicitly set it to fixture.
Settings resolve data/fixtures/cases.json relative to the repository, but startup
and health do not open it. Creating those cases remains T014.

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
Backend coverage currently includes contracts and startup/health. Vitest has no
frontend behavior tests yet: “No test files found” exits 1 and is not a passing
suite. Run the remaining checks separately even after that expected exit.
Build output frontend/dist/ is local and ignored; it is not a deployment.

The [target quickstart](specs/001-project-foundation/quickstart.md) also describes
future three-case navigation and failure-state checks. Those and the browser
case journey are pending phase 4; do not claim them from this health smoke.

## Evidence and next work
See [phase 3 handoff](evidence/tasks/phase-03-handoff.md),
[startup RED/GREEN](evidence/tasks/T008.md), [setup/smoke](evidence/tasks/T011.md)
and [next_work.md](next_work.md). Human review and independent second-member
reproduction remain pending (SC-001). Local fixture checks are not ML evaluation.
