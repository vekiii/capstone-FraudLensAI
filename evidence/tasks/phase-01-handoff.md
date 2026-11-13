# Phase 1 setup handoff

Date: 2026-11-11 (Europe/Belgrade). Scope: T001–T005 only.
Branch: `initialization`; starting commit: `e62c4fe108b9cf9ee1052c8ed130c44c386855ff`.
Initial `git status --short`: empty. No existing AGENTS.md or evidence records.
Original instruction: [phase-01 prompt](../../prompts/development/001-foundation-phase-01.md).
Requirements: FR-001, FR-008, FR-009, FR-010, FR-011 (setup portions only).
Code reference: uncommitted working-tree changes against the starting commit.
Human review: pending; no reviewer or peer reproduction claimed.

## Progress
- T001 complete: AGENTS.md reviewed against constitution and targeted original idea
  sections; scope, approval, SDD/TDD and real verification instructions documented.
- T002 complete: evidence README/template and prompt conventions reviewed for all
  requested fields, real outcomes, RED/GREEN applicability and pending review.
- T003 complete: generated uv.lock, locked sync and Python imports/config/lint verified.
- T004 complete: Node 22 locked install, typecheck, build and Vitest/jsdom
  configuration/availability verified. No feature UI or behavior tests added.
- T005 complete: .gitignore preserved existing PDF rule and added exclusions;
  data/README.md documents local data, reviewed fixtures, evaluation and Git policy.
- T006 onward untouched; SC-001 remains pending.

## Actual checks and findings
- Read constitution, spec, plan, tasks, research, quickstart, data model/contracts,
  ignore rules and local speckit-implement skill. No extension configuration exists.
- With SPECIFY_FEATURE_DIRECTORY=specs/001-project-foundation, ran
  `powershell -NoProfile -ExecutionPolicy Bypass -File .specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks`:
  exit 0; correct absolute feature directory and design documents returned.
- Checklist requirements.md: 11 total, 11 checked, 0 unchecked; no markers changed.
- `uv --version`: 0.10.9; default `python --version`: 3.14.7;
  `node --version`: v24.20.0; `npm.cmd --version`: 11.19.0.
- `npm --version` blocked by PowerShell script policy; use npm.cmd without changing
  persistent policy. `uv python list --only-installed` could not access default uv
  cache (access denied); use a workspace-local cache for subsequent commands.

## Files changed so far
AGENTS.md; prompts/development/001-foundation-phase-01.md; prompts/README.md;
evidence/README.md; evidence/templates/task.md; this handoff.
T003 adds pyproject.toml, .python-version, uv.lock,
backend/src/fraudlens/__init__.py and docs/decisions/foundation.md.
T004 adds frontend/package.json, package-lock.json, tsconfig.json, index.html,
vite.config.ts, src/main.ts and README.md.
T005 changes .gitignore and adds data/README.md. tasks.md marks only T001–T005
complete and updates its status header; all later tasks remain unchecked.

## T004 actual execution
- Official nodejs.org index selected v22.23.4. First PowerShell index selection
  produced an empty version and HTTP 400; explicit array enumeration corrected it.
  Downloaded node-v22.23.4-win-x64.zip under .cache/node-runtime and compared
  Get-FileHash SHA256 with official release SHASUMS256.txt: match
  `cbc74b5e0982c9dbb41525fd8fb5dcd32fbee237863f7829072f4639a1ce5f20`.
  Extracted locally; Node v22.23.4, bundled npm 10.9.9; no global changes.
- Initial `npm.cmd --prefix frontend install --save-dev vite@latest typescript@latest vitest@latest jsdom@latest @types/node@22 --no-fund --no-audit`:
  exit 0, generated lockfile, 67 packages installed. Extraction had not yet exposed
  local npm.cmd, so the global wrapper ran Node 24.20.0/npm 11.19.0 and emitted the
  project's Node 22 engine warning. All later checks select the extracted Node 22.
- Session: `$nodeDir = Join-Path $PWD '.cache/node-runtime/node-v22.23.4-win-x64'`;
  `$env:PATH = "$nodeDir;$env:PATH"`;
  `$env:npm_config_cache = Join-Path $PWD '.cache/npm'`.
- `node --version` / `npm.cmd --version`: v22.23.4 / 10.9.9.
- `npm.cmd --prefix frontend ci --no-fund --no-audit`: exit 0, 67 packages installed
  from lockfile. Sandbox EACCES fetches for optional WASM dependencies appear in
  local npm debug log; npm completed successfully and native tooling works.
- `npm.cmd --prefix frontend run typecheck`: exit 0.
- `npm.cmd --prefix frontend run build`: exit 0 (includes typecheck), Vite 8.3.8,
  4 modules transformed; dist/index.html and asset JS generated locally.
- `npm.cmd --prefix frontend run test -- --run`: exit 1, Vitest 5.1.0 loaded
  configuration, no test files found. This is not a passing test suite.
- `node --input-type=module -e "import { JSDOM } from './frontend/node_modules/jsdom/lib/api.js'; const dom = new JSDOM('<main></main>'); console.log('jsdom:', dom.window.document.querySelector('main').tagName); dom.window.close();"`:
  exit 0, `jsdom: MAIN` under Node 22.
- `npm.cmd --prefix frontend ls --depth=0`: exit 0, all five direct dependencies
  present at the versions recorded in frontend/README.md.
- `node --input-type=module -e "import { loadConfigFromFile } from './frontend/node_modules/vite/dist/node/index.js'; const result = await loadConfigFromFile({command:'serve',mode:'development'},'frontend/vite.config.ts'); console.log(JSON.stringify(result.config));"`:
  exit 0; config host 127.0.0.1, port 5173, strictPort true,
  /api proxy http://127.0.0.1:8000 and test environment jsdom confirmed.

## T005 actual execution
From repository root, checked representative nonexistent paths as well as real
files with `git check-ignore --no-index -v -- <path>` (expected ignored), and
`git check-ignore --no-index -q -- <path>` (expected exit 1 for shareable files).
The wrapper asserted each expected status; overall exit 0.
- Ignored: .venv/pyvenv.cfg, frontend/node_modules/vite/package.json,
  frontend/dist/index.html, .cache/node-runtime/node.exe,
  backend/src/fraudlens/__pycache__/x.pyc, .pytest_cache/probe, .ruff_cache/probe,
  .mypy_cache/probe, .coverage, .coverage.sample, coverage.xml, junit.xml,
  frontend/coverage/index.html, frontend/.vite/probe, frontend/.vitest/probe,
  frontend/probe.tsbuildinfo, .env, .env.local, frontend/.env.local,
  data/raw/probe.csv, data/processed/probe.csv, evals/results/probe.json.
- Existing .specify/.gitignore also correctly ignored feature.json,
  extensions/sample/local-config.yml, integrations/packages/probe and
  integrations/packages.json. That file was not changed.
- Shareable: uv.lock, frontend/package-lock.json, root/frontend .env.example,
  data/fixtures/cases.json, evals/datasets/reviewed.json,
  .agents/skills/speckit-implement/SKILL.md, .specify/memory/constitution.md,
  .specify/scripts/powershell/check-prerequisites.ps1, .specify/init-options.json,
  specs/001-project-foundation/tasks.md, prompts/development/001-foundation-phase-01.md,
  prompts/app/example-v1.md, evidence/tasks/phase-01-handoff.md and data/README.md.
- `git status --short --untracked-files=all`: reviewed all source/docs/config/lock
  paths; local runtime, installed dependencies, build and caches do not appear.
- `git diff --check`: exit 0; Git's LF-to-CRLF informational warning only.

## Final review
- `git diff --check` after task marking: exit 0. Also ran
  `git diff --no-index --check -- NUL <path>` for each path returned by
  `git ls-files --others --exclude-standard`; no whitespace findings.
- Reviewed `git diff -- specs/001-project-foundation/tasks.md`: only T001–T005
  checked and status header updated. T006–T027 remain unchecked.
- `git diff --stat` covers the two changed tracked files (.gitignore and tasks.md);
  separately reviewed all 19 untracked files and their sizes. Largest are generated
  frontend/package-lock.json (64,576 bytes) and uv.lock (50,431 bytes).
- Compared saved prompt with the UTF-8 attachment using case-sensitive exact text
  equality: True. No prompt reconstruction or additional T023 record.
- Final extension-hook existence check: False, so no before/after hooks to dispatch.
  No checklist, constitution, specification, plan or contract content changed.

## T003 actual execution
Session setting: `$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'`.
- `uv python list --only-installed`: exit 0 with local cache; Python 3.12.10 available.
- `uv lock`: sandbox exit 1, PyPI socket access denied; authorized retry exit 0,
  41 packages resolved (including project). Upstream metadata warnings about trailing
  commas in version specifiers were normalized by uv; resolution succeeded.
- `uv sync --locked --group dev`: exit 0; .venv created with CPython 3.12.10,
  40 dependencies installed. No global runtime changed.
- `uv run --locked python -c "import sys, importlib.metadata as m; import fastapi, pydantic, uvicorn, pytest, httpx, ruff, jsonschema; print(sys.version); print('\n'.join(f'{n}=={m.version(n)}' for n in ['fastapi','pydantic','uvicorn','pytest','httpx','ruff','jsonschema'])); import pytest as p; c=p.Config.fromdictargs({}, []); print('pytest config:', c.inipath); print('pythonpath:', c.getini('pythonpath')); import fraudlens; print('package:', fraudlens.__file__)"`:
  exit 0; all imports available, pyproject.toml loaded, backend/src resolved, package
  imported from backend/src/fraudlens. Exact versions in docs/decisions/foundation.md.
- `uv run --locked ruff check backend`: exit 0, all checks passed.
- `uv run --locked ruff check --show-settings backend/src/fraudlens/__init__.py`:
  exit 0; pyproject.toml selected, target Python 3.12, line length 100.
- `uv run --locked pytest --collect-only backend`: exit 5, zero tests collected;
  configuration loads correctly, behavior tests have not been written.

## Verification limits and next step
Mechanical scaffolding: RED/GREEN not applicable. No behavior tests exist yet.
No health/case smoke, model evaluation, browser journey or peer reproduction run.
No external blocker remains. First next step: human review of this setup and its
lockfiles, then T006 contract validation tests (RED) in a separately authorized
phase 2. Do not start health/case smoke or claim SC-001 until later tasks and
actual second-person reproduction. No commit/push/merge/deploy performed.

## Runtime amendment — 2026-11-11
User explicitly replaced Python 3.12 / Node 22 with Python 3.14 / Node 24.
Earlier execution entries above remain historical; this section supersedes their
runtime selection. T001–T005 remain complete; later tasks remain untouched.
Updated .python-version, pyproject.toml (requires-python >=3.14,<3.15 and Ruff
py314), uv.lock, frontend/package.json/package-lock.json (@types/node 24.19.2),
frontend/README.md, docs/decisions/foundation.md and feature plan/research/quickstart/
task runtime references. Preserved original prompt and appended the user amendment.
T001/T002/T005 instructions, conventions and ignore policy remain applicable.

Actual commands from repo root, UV_CACHE_DIR=.cache/uv:
- uv lock: exit 0; resolution regenerated for Python 3.14, direct versions unchanged.
- uv sync --locked --group dev: exit 0; recreated project .venv with Python 3.14.3.
- uv run --locked python -c "import sys, fastapi,pydantic,uvicorn,pytest,httpx,ruff,jsonschema; print(sys.version)": exit 0, Python 3.14.3; imports available.
- uv run --locked ruff check backend: exit 0.
- uv run --locked pytest --collect-only backend: exit 5, zero tests.
- node --version / npm.cmd --version: v24.20.0 / 11.19.0.
- npm.cmd --prefix frontend install --save-dev @types/node@24 --no-audit --no-fund: exit 0; generated lock update.
- npm.cmd --prefix frontend ci --no-audit --no-fund: exit 0, 67 packages.
- npm.cmd --prefix frontend run typecheck: exit 0.
- npm.cmd --prefix frontend run build: exit 0, 4 modules built.
- npm.cmd --prefix frontend run test -- --run: exit 1, no test files.
- npm.cmd --prefix frontend ls --depth=0: exit 0; @types/node 24.19.2, other direct versions unchanged.
No behavior test suite, health/case smoke or second-person reproduction claimed.
Human review remains pending; next step remains review followed by T006.
