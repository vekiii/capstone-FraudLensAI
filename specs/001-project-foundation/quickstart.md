# Foundation Quickstart — Target Runbook

**Status**: Planned commands for implementation. The application and lockfiles do not yet exist.
Do not report this guide as executed. First install needs network; application runtime needs no
model, dataset, corpus, provider key or external service.

## Prerequisites
Git, uv, Python 3.12, Node 22 (>=22.12), npm, Windows PowerShell. Record exact versions during
setup. Spec-kit 1.4.0 is already initialized. Preserve existing initialization branch.

## Install (after implementation setup generates and commits lockfiles)
From repository root:
```powershell
uv sync --locked --group dev
npm --prefix frontend ci
```
For the first implementation only, resolve dependencies with uv lock and npm install in frontend;
review and commit resulting lockfiles before using locked installs. Do not handwrite hashes.

## Run in two terminals
Repository root, terminal 1:
```powershell
uv run --locked uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8000
```
Repository root, terminal 2:
```powershell
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173 --strictPort
```
Open http://127.0.0.1:5173. Expect three explicitly synthetic cases. No key entry is required.
The frontend development proxy forwards /api to 127.0.0.1:8000.

## Automated checks
```powershell
uv run --locked pytest backend/tests
uv run --locked ruff check backend
npm --prefix frontend run test -- --run
npm --prefix frontend run typecheck
npm --prefix frontend run build
```
Implementation setup must define these scripts and dev dependencies. Backend pytest config
sets pythonpath=backend/src. A generated dist directory is not committed or a public deployment.

## Manual acceptance
1. Start without keys/datasets/models. Open all three cases and verify identifiers and provenance.
2. Go back; select a second case rapidly and confirm no stale first-case details.
3. Stop backend, request cases, observe controlled unavailable state; restart and retry.
4. Check a well-formed absent case through /api/cases/CASE-999: controlled 404.
5. Automated tests substitute an empty repository and a failing/mismatching scorer; do not
   add debug or write endpoints merely for these scenarios.
6. A second teammate repeats setup and writes their own actual result; until then peer
   reproducibility remains pending.

## Evidence and handoff
Record task IDs, commands, actual outcomes, versions and limitations using evidence/templates/task.md
when created. Preserve original development prompts separately from application prompts.
Never mark future commands successful or record fixture outputs as live LLM/ML evaluations.
If PowerShell blocks reviewed Spec-kit scripts, invoke the individual script with
`powershell -NoProfile -ExecutionPolicy Bypass -File <script> ...`; no machine-wide policy change.

Spec-kit's active feature pointer is local and ignored. In a new checkout set the session variable
before downstream commands:
```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/001-project-foundation'
```
This selects the feature directory, not a Git branch. Keep branch initialization until the team
chooses its normal merge flow. No commit/push/deploy is performed by this planning step.
