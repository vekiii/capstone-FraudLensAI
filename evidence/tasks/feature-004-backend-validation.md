# T018 — Feature 004 backend validation

- **Status** Complete on 2026-11-19 (Europe/Belgrade).
- **Revision** `a0dfa5e6a8ccc117afe432e9c056549d41b6aec9` on `004-simulation-and-prioritization`. The worktree was clean at the start of verification.
- **Environment** Windows, CPython 3.14.7, uv 0.10.9 (`f675560f3`), pytest 9.2.0, Ruff 0.17.4, FastAPI 0.162.4, Pydantic 2.14.3, Uvicorn 0.54.0, Starlette 1.10.0 and httpx 0.28.1. `uv.lock` SHA-256 is `3038b420aa9e4ccd1f3010ca9c1db915953b5b9660647b1f7a897b9a8248dd12`.
- **Fixture** `review-capacity-demo` v1, content SHA-256 `894136f422d013cf0d1d52820acf26e3a3a95076a4b8ab044c4e24faf4105198`. Edge cases use temporary synthetic fixtures.
- **References** [Quickstart](../../specs/004-simulation-and-prioritization/quickstart.md#test-first-validation) · [Request](../../prompts/development/004-simulation-phase-06.md)

## Commands and results

Commands ran from the repository root. The pinned uv executable was extracted from the PyPI `uv==0.10.9` Windows wheel into the ignored `.cache/004-phase06-tools/` directory because uv was absent from `PATH`. `$uvTool` points to that executable. The test run used the existing `.venv`, `UV_CACHE_DIR=.cache/uv`, `UV_OFFLINE=1`, and a fresh `$testDir` under `.cache/` for pytest output.

| Command | Observed result | Exit |
| --- | --- | ---: |
| `& $uvTool lock --check` | Resolved 41 packages in 1 ms. Lock check passed | 0 |
| `& $uvTool run --locked pytest backend/tests --basetemp "$testDir/tmp" -o "cache_dir=$testDir/cache" --junitxml "$testDir/pytest.xml" -q --tb=short` | `410 passed in 2.81s` | 0 |
| `& $uvTool run --locked ruff check backend` | `All checks passed!` | 0 |

The JUnit report recorded eight startup and health tests, 43 Cases endpoint tests, 56 simulation contract tests, nine replay unit tests and 35 simulation API tests among the full suite. The Cases regressions include normal list and detail responses and 404/422 behavior. The simulation suite confirms Cases responses before and after replay, exact hand-calculated choices and counts, capacity and window invariants, closed contracts, outcome isolation and identical recipe replay. Every JUnit case passed.

This phase reran existing regression tests. The story evidence contains the original RED and GREEN runs. Independent review and reproduction are pending. [US1](feature-004-us1.md) · [US2](feature-004-us2.md) · [US3](feature-004-us3.md)
