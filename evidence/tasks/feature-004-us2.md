# Feature 004 US2 — Capacity and threshold, 2026-11-19 (Europe/Belgrade)

- **Status** T012–T014 complete. [Tasks](../../specs/004-simulation-and-prioritization/tasks.md#phase-4-user-story-2--explore-capacity-and-threshold-p2) · [Original request](../../prompts/development/004-simulation-phase-04.md)
- **Trace** FR-002, FR-003, FR-005, FR-009 and SC-002. [Specification](../../specs/004-simulation-and-prioritization/spec.md) · [Replay contract](../../specs/004-simulation-and-prioritization/contracts/replay-v1.md)
- **Baseline** Branch `004-simulation-and-prioritization`, HEAD `e710d49e148b65433811f16414e82afb3f2e2723`. The initial `.gitignore` edit adding `/data/artifacts/` was preserved. Commands ran from the repository root with the existing dependencies. Python 3.14.7, pytest 9.2.0, Ruff 0.17.4, FastAPI 0.162.4, Pydantic 2.14.3, Uvicorn 0.54.0, Node 24.20.0, npm 11.19.0, Vitest 5.1.0, Vite 8.3.8, Chrome 157.0.8103.79. `uv` was unavailable on `PATH`. The existing `.venv` reports uv 0.10.9 as its creator, and the installed pytest, Ruff, FastAPI, Pydantic, Uvicorn, httpx and Starlette versions matched `uv.lock`.
- **Spec Kit** With `SPECIFY_FEATURE_DIRECTORY=specs/004-simulation-and-prioritization`, `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks` returned the requested feature and all expected design documents, exit 0. The child-process flag addressed a script policy error on direct invocation. `requirements.md` was 16/16. `.specify/extensions.yml` was absent during both hook checks.

## Tests first and implementation

T012 added four API regressions. The two-window requests used one catalog reference and varied one setting at a time. At threshold `0.3` and budget `2`, all strategies skipped oversized A, reviewed B at the first start and C at the second, and left A and E pending. Each reported one threshold miss (D) and one backlog miss (A). Budget `4` allowed A to be reviewed, and threshold `0.8` admitted B at equality and excluded C. The other runs exercised zero budget, empty input and partial or entirely missing outcomes. All 30 API tests passed before frontend implementation. Backend behavior required no changes.

T013 added 22 frontend cases. Before T014, 21 failed and 9 passed (exit 1). The failures were missing inputs or coverage cells and a disabled resubmission button. The eight existing tests and the new navigation regression passed. Deferred comparison responses deliberately ignore cancellation. Tests cover stale successes after either edit even when the value is restored, a late failure across scenario changes, an older response after resubmission, and a late response after navigation.

T014 sends the exact decimal text for a threshold in `[0,1]` and sends the validated whole-minute budget as a nonnegative safe integer. Scenario changes restore catalog defaults. Submitting again replaces the pending comparison. Edits clear the table immediately, and only the current request can publish a result or error. Result rows show total missed positives and their threshold and backlog components, along with unknown-outcome counts. A known zero is rendered as `0`, and unavailable metrics as `Nedostupno`. The Phase 3 browser verifier now locates its original metrics by their data attributes to accommodate the additional columns.

## Commands and observed results

For pytest, each run used a fresh `$testDir` under the ignored `.cache/`, with `--basetemp "$testDir/tmp" -o "cache_dir=$testDir/cache"`.

| Command | Observed result | Exit |
| --- | --- | ---: |
| `.venv/Scripts/python.exe -m pytest backend/tests/integration/test_simulation_api.py --basetemp "$testDir/tmp" -o "cache_dir=$testDir/cache" -q --tb=short` | 30 passed before implementation, including all four T012 regressions | 0 |
| `npm.cmd --prefix frontend run test -- --run tests/simulation.test.ts` | RED 21 failed, 9 passed. GREEN 30 passed | 1 / 0 |
| `.venv/Scripts/python.exe -m pytest backend/tests --basetemp "$testDir/tmp" -o "cache_dir=$testDir/cache" -q --tb=short` | Final regression 405 passed | 0 |
| `.venv/Scripts/python.exe -m ruff check backend` | All checks passed | 0 |
| `npm.cmd --prefix frontend run test -- --run` | Final regression 181 passed across six files | 0 |
| `npm.cmd --prefix frontend run typecheck` | Passed before and after implementation, and again during the build | 0 |
| `npm.cmd --prefix frontend run build` | Vite production build passed | 0 |
| `node .cache/004-us2-browser.mjs` | Escalated retry passed 11 grouped local checks in Chrome, with an isolated profile and process cleanup | 0 |
| `node --check evidence/tasks/feature-004-us1-browser.mjs` | Updated verifier syntax check passed | 0 |
| `git diff --check` | Passed | 0 |

The automated browser check extended the Phase 3 verifier and used real HTTP with `.venv/Scripts/python.exe -m uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8000` and `node frontend/node_modules/vite/bin/vite.js frontend --config frontend/vite.config.ts --host 127.0.0.1 --port 5173 --strictPort` in fixture mode. The first sandboxed attempt verified the direct and proxied API, then timed out enabling the Chrome page. Its local listeners were stopped, and the isolated retry succeeded. The ports were free after the retry. At threshold `0.3`, increasing the budget from `2` to `4` changed positives found from `0/1/1` to `1/2/2` and backlog from `3/3/2` to `2/1/1` in FIFO, highest-score and weighted-per-minute order. Threshold `0.850`, zero capacity and rejection of fractional minutes were also verified in the browser. The default comparison took 61 ms in this run. [Browser observations](feature-004-us2-browser-results.json)

## Review and continuation

The checks exercise synthetic fixture replay. Human review and second-person reproduction are pending. The next scoped task is T015, the canonical recipe round-trip and label-only API regressions. Recipe export and reopen, per-window inspection and the teammate acceptance walkthrough remain pending.
