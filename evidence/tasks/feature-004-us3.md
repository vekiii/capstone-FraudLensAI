# Feature 004 US3 — Reproduce and explain a run, 2026-11-19 (Europe/Belgrade)

- **Status** T015–T017 complete. [Tasks](../../specs/004-simulation-and-prioritization/tasks.md#phase-5-user-story-3--reproduce-and-explain-a-run-p3) · [Original request](../../prompts/development/004-simulation-phase-05.md)
- **Trace** FR-006–009 and SC-003. [Specification](../../specs/004-simulation-and-prioritization/spec.md) · [Replay contract](../../specs/004-simulation-and-prioritization/contracts/replay-v1.md)
- **Baseline** Branch `004-simulation-and-prioritization`, clean at `e15ee1f5fd0750f017b55f672d1fbc515d08f750`. Used the existing environments and lockfiles. Python 3.14.7, pytest 9.2.0, Ruff 0.17.4, Uvicorn 0.54.0, Node 24.20.0, npm 11.19.0, TypeScript 7.0.2, Vitest 5.1.0, Vite 8.3.8 and Chrome 157.0.8103.79. The `uv` executable was unavailable on `PATH`, so commands invoked the existing `.venv` directly. It was created with uv 0.10.9.
- **Spec Kit** `SPECIFY_FEATURE_DIRECTORY=specs/004-simulation-and-prioritization`. Running `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks` selected the requested feature and returned its design documents, exit 0. `requirements.md` was 16/16. `.specify/extensions.yml` was absent during both hook checks.

## Test-first results

T015 added five API regression cases. A two-window comparison with a long decimal threshold returned a canonical recipe whose JSON round trip reproduced the entire response through a fresh app instance. A separate temporary catalog with A and B's outcome labels swapped changed the fingerprint and label-derived counts. All three strategies kept identical ranked windows, review selections, minutes, pending lists and coverage counts. A saved recipe with the old fingerprint returned 409 on the variant catalog. Separate cases verified 409 for a missing revision, wrong digest and unavailable strategy version. All 35 API tests passed before implementation. The production API and bundled fixture required no changes.

T016 added 12 frontend cases. All 12 failed before implementation at the missing download control, file input or window details. The 30 existing cases passed. The new cases exercise the canonical download and reopen after remounting, exact revision and decimal handling, malformed files, HTTP 409 with explicit rerun, ignored late responses after navigation, ignored late file reads after a newer comparison, and label-free ranking inspection.

T017 validates recipe files locally and sends the original scenario reference, threshold text, budget and strategy versions. It downloads the canonical recipe returned by the API. A version failure clears the previous results and waits for a new action. The results expose the ranked and reviewed orders, consumed minutes, score provenance, scenario weight and duration assumptions, and final pending IDs. A separate expandable view exposes inputs for all admitted alerts, including those arriving after the final review start. Results and exported JSON omit per-alert outcome labels.

## Commands and observed results

Commands ran from the repository root. Each pytest run used a fresh `$testDir` under the ignored `.cache/`.

| Command | Observed result | Exit |
| --- | --- | ---: |
| `.venv/Scripts/python.exe -m pytest backend/tests/integration/test_simulation_api.py --basetemp "$testDir/tmp" -o "cache_dir=$testDir/cache" -q --tb=short` | 35 passed before implementation, including all five T015 cases | 0 |
| `npm.cmd --prefix frontend run test -- --run tests/simulation.test.ts` | RED 12 failed and 30 passed. GREEN 42 passed | 1 / 0 |
| `.venv/Scripts/python.exe -m pytest backend/tests --basetemp "$testDir/tmp" -o "cache_dir=$testDir/cache" -q --tb=short` | 410 passed | 0 |
| `.venv/Scripts/python.exe -m ruff check backend` | All checks passed | 0 |
| `npm.cmd --prefix frontend run test -- --run` | 193 passed in six files | 0 |
| `npm.cmd --prefix frontend run typecheck` | Passed before and after implementation | 0 |
| `npm.cmd --prefix frontend run build` | Typecheck and production build passed | 0 |
| `node .cache/004-us3-browser.mjs` | 16 grouped Chrome checks passed after the final update. Loopback services and isolated Chrome processes were cleaned up | 0 |
| `git diff --check` | Passed | 0 |

The Chrome verifier extended the Phase 4 local script. It used FastAPI and the Vite proxy with the bundled scenario `review-capacity-demo` v1, digest `894136f422d013cf0d1d52820acf26e3a3a95076a4b8ab044c4e24faf4105198`, threshold `0.3` and budget `4`. Chrome wrote the recipe to an isolated download directory and opened the same file after a reload. The observed replay matched all three summary rows and the weighted window's ranked `[C,E,B,A]` and reviewed `[C,E,B]` orders. The local check from file selection through comparison and window inspection took 68 ms. A modified strategy version yielded exactly one HTTP 409, followed by HTTP 200 only after explicit submission. Malformed JSON cleared the view before any request. Cases startup, detail/back and HTTP 404/422 also passed. [Browser results](feature-004-us3-browser-results.json)

## Review and continuation

These checks cover synthetic fixture replay. Human review and teammate reproduction are pending. Phase 6 remains open. Its first task is T018, formal backend validation and evidence for final Feature 004 handoff.
