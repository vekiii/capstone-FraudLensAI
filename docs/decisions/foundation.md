# Foundation setup decisions

Date: 2026-11-11. Scope: phase 1, T003 (FR-001). Architecture authority:
[plan](../../specs/001-project-foundation/plan.md),
[research](../../specs/001-project-foundation/research.md).

## Python environment
Use Python 3.14.x (`.python-version`, constrained to >=3.14,<3.15 in pyproject.toml).
Actual project runtime: CPython 3.14.3, Windows x86_64; uv 0.10.9.
The machine default Python is 3.14.7 and is not the project interpreter.
`uv lock` generated uv.lock; subsequent installs use `uv sync --locked --group dev`.
The dev dependency group contains pytest, httpx, Ruff and jsonschema with format
extras for later JSON Schema date-time checks. Production dependencies are FastAPI,
Pydantic 2 and Uvicorn. No server, routes, contracts or business logic exist yet.
No build backend is needed for this non-distributed application skeleton.

Actual resolved direct dependencies (complete transitive resolution: uv.lock):

| Dependency | Version | Group |
|---|---|---|
| fastapi | 0.162.4 | runtime |
| pydantic | 2.14.3 | runtime |
| uvicorn | 0.54.0 | runtime |
| pytest | 9.2.0 | dev |
| httpx | 0.28.1 | dev |
| ruff | 0.17.4 | dev |
| jsonschema | 4.26.0 | dev |

pytest reads pyproject.toml and adds backend/src to its import path. Ruff targets
Python 3.14 with import sorting and basic error/undefined-name rules. The only
package file is backend/src/fraudlens/__init__.py.

In this restricted workspace the default uv cache is inaccessible. Session-only
workaround used here (the cache is ignored):

```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
uv sync --locked --group dev
```

Initial sandbox network access to PyPI failed (socket access denied); authorized
execution outside the sandbox generated the lock and installed dependencies.
Locked sync, dependency imports, pytest config/import path and Ruff were checked.
pytest collection reported zero tests (exit 5), which is expected before T006 and
is not a passing behavior suite. See [handoff](../../evidence/tasks/phase-01-handoff.md)
for commands, results, runtime caveats and pending human review.

Later ownership/boundary documentation is T022 and remains unimplemented.
