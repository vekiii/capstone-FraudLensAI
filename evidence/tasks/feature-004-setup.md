# T001 - Feature 004 locked setup and baseline

- Date/timezone: 2026-11-18, Europe/Belgrade.
- Status: **complete**, mechanical setup only. Stop before T002.
- Feature: [tasks](../../specs/004-simulation-and-prioritization/tasks.md),
  [specification](../../specs/004-simulation-and-prioritization/spec.md),
  [plan](../../specs/004-simulation-and-prioritization/plan.md),
  [quickstart](../../specs/004-simulation-and-prioritization/quickstart.md).
- [Exact received prompt](../../prompts/development/004-simulation-phase-01.md)
  copied byte-for-byte from the attached Pasted text.txt before setup mutations.
- Working directory: `D:\AIBootcamp\capstone` for all commands below.
- Initial branch: `004-simulation-and-prioritization`; HEAD
  `ff389744e2529e248371b69a998375b32784d2ae`.
- Initial status: only untracked
  `specs/004-simulation-and-prioritization/feature4_tasks_prompt.md`; preserved.
- AGENTS then next_work read before work; constitution, requested feature/setup
  documents, configs, target tests, evidence/prompt conventions and ignores read.
  Scoped speckit-implement applied only to T001. No subagents.

## Runtime and existing lockfiles

| Command | Actual result | Exit |
|---|---|---|
| `uv --version` | uv 0.10.9 (f675560f3 2026-03-06) | 0 |
| `uv run --locked python --version` | Project Python 3.14.3 | 0 |
| `py --version` | System launcher Python 3.14.7, distinct from project interpreter | 0 |
| `node --version` | v24.20.0 | 0 |
| `npm.cmd --version` | 11.19.0 | 0 |

Existing `.python-version` pins 3.14 and pyproject requires Python 3.14.x;
frontend engine >=24.0.0 <25. Lockfiles: `uv.lock` revision 3 and
`frontend/package-lock.json` lockfileVersion 3; no regeneration or upgrades.
SHA256 before/after setup (exact file bytes):

| File | SHA256 |
|---|---|
| uv.lock | 3038b420aa9e4ccd1f3010ca9c1db915953b5b9660647b1f7a897b9a8248dd12 |
| frontend/package-lock.json | 81f2b73c47a723aeb4ab0a272c367fa388808311d0f5b64ef4b0c8e91c03709c |
| pyproject.toml | a087206334a3bca07239a29b63667505114134c86e12e9cde882b53f37c306c4 |
| .python-version | 73880611a18bf211ab229c2a2d93ec11a622693e79532c0b797b91fd056704dc |
| frontend/package.json | 2da5a59d191ac1f6572140ea9eea881a786120df8b25b7e5af021d1ff9812112 |
| Existing untracked feature4_tasks_prompt.md | 88e2b27da901281192d3bf9d75325c2084e234d274581789c7aaeb9b9b79c31f |

## Commands and actual outcomes

```powershell
$env:SPECIFY_FEATURE_DIRECTORY='specs/004-simulation-and-prioritization'
powershell -NoProfile -ExecutionPolicy Bypass -File .specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
```

Exit 0; FEATURE_DIR resolves to the requested absolute feature directory, with
research/data-model/contracts/quickstart/tasks available. Execution policy applies
only to the child command, no persistent policy change. Requirements checklist
**16 checked / 0 unchecked**; markers unchanged. `.specify/extensions.yml` absent:
no pre/post implementation hooks to execute. Ignore rules cover .venv,
node_modules, .cache, test/build output and local environment files.

```powershell
$env:SPECIFY_FEATURE_DIRECTORY='specs/004-simulation-and-prioritization'
$env:UV_CACHE_DIR=Join-Path $PWD '.cache/uv'
uv sync --locked --group dev
npm.cmd --prefix frontend ci
```

Both exit 0. uv resolved 41 packages, removing six packages left in the local
environment from another dependency set: httpcore2/httpx2/jiter/openai/sniffio/
truststore. This aligns ignored .venv with this checkout's existing lock; it is
not a dependency-file edit or provider operation. npm added 67 packages in 7 s.
No uv lock/npm install, dataset download, provider key access or external service
execution. No sandbox escalation was required by these commands.

Backend command, actual unique absolute cache paths:

```powershell
$env:SPECIFY_FEATURE_DIRECTORY='specs/004-simulation-and-prioritization'
$env:UV_CACHE_DIR=Join-Path $PWD '.cache/uv'
$t=Join-Path $PWD ('.cache/004-t001-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $t | Out-Null
# Actual $t: D:\AIBootcamp\capstone\.cache\004-t001-72463795f80447fabb8fab0219fffb9e
uv run --locked python --version
uv run --locked pytest backend/tests/integration/test_startup.py --basetemp "$t/tmp" -o "cache_dir=$t/cache" -q --tb=short
```

Exit 0: **8 passed, 1 warning in 0.79 s**. Existing startup/health network guard
and fixture-mode contracts passed. Warning: StarletteDeprecationWarning about
httpx with starlette.testclient. No dependency change to suppress it.

```powershell
npm.cmd --prefix frontend run test -- --run tests/api.test.ts
```

Exit 0: Vitest 5.1.0, **1 file / 82 tests passed**, duration 1.00 s.
Existing fetch/decoding boundary baseline, not a real browser/backend journey.

## RED, preservation and limitations

RED: **not applicable** to mechanical setup; existing regression tests were
executed without artificial failures or new simulation tests. Both prescribed
modules ran and passed, no empty-suite pass. No setup blockers encountered.
Final git diff --check and prompt/hash/source/task-state preservation checks PASS.
Only T001 marked; all later task markers unchanged. Application source/tests,
dependency manifests/locks, shared instructions and the existing untracked
template remain unchanged. No branch change, pull, stash, reset, merge, commit,
push or deploy. Full suites, lint/typecheck/build and browser walkthrough are
not run: outside this requested baseline-only increment. No simulation scenario,
outcomes, replay engine, API/UI or Feature 02 adapter created.

Human review: **pending**, reviewer/date/findings not supplied. Second-person
reproduction **pending**; this is one agent's actual setup/baseline, not model
evaluation or teammate acceptance. Next separately scoped work: T002-T004.
See [phase handoff](feature-004-phase-01-handoff.md).
