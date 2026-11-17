# TypeScript-first web application consolidation

Date: 2026-11-17
Branch: `feature/005-real-time-fraud-detection-mlops-spec`

## Request and scope

The original request is preserved in
[`prompts/development/typescript-first-web-app-2026-11-17.md`](../../prompts/development/typescript-first-web-app-2026-11-17.md).
The requester explicitly authorized consolidating the current vanilla TypeScript
dashboard and React showcase into one strict TypeScript/React application, while
preserving Python/FastAPI and ML services.

## Architecture review

- `frontend/` contains the existing TypeScript case browser, v1/v2 API decoders,
  request lifecycle, and dataset model overview. Its Vite app uses strict TS.
- `web/` contains the React 18/TypeScript showcase, four pages, motion system,
  fallback data, and separate Vite/package setup. Its TS config is strict but
  initially excludes tests.
- A source scan found no `.js`, `.jsx`, `.mjs`, or `.cjs` application files in
  either frontend.
- Backend and ML implementation remain Python/FastAPI; the database migration
  remains SQL.

## Migration plan

1. Keep `web/` as canonical because the requested end state is React and it
   already contains the four-route Feature 005 showcase.
2. Bring the existing typed API/contracts and case/dataset-overview behavior
   into React routes, with React-level regression coverage.
3. Run preserved API/contract tests, React behavior tests, typecheck and build.
4. Only after verification, remove the duplicate Vite app and update active
   setup documentation, project handoff, and this evidence record.
5. Review scope, diff, and checks; commit the scoped result.

## Scope decision

Decision: proceed as explicitly requested by the user on 2026-11-17. Benefit:
one React/TypeScript app and one set of frontend dependencies/build commands,
while keeping existing typed API integration and showcase pages. Schedule impact:
one consolidation unit that includes porting the existing dashboard flows and
regression checks; no backend migration or new product capability is authorized
or included.

## Implementation and verification log

Implemented the consolidation in `web/`, the single React/TypeScript/Vite app.
Moved the existing typed API and v1/v2 contract decoders, then added React
`/cases` and `/dataset-overview` routes. Case list sorting, snapshot-pinned
detail reads, stale recovery, safe rendering, cancellation of older selections,
and aggregate overview states are covered by React tests. Existing showcase
routes/data, motion, API fallback, and CSP remain in the same app. Added the
`/api` Vite proxy and made typechecking include source, tests, and Vite config.
Removed all 23 tracked files from the duplicate `frontend/` app only after the
replacement checks passed; ignored local dependencies/build output were left
untouched. Updated active setup, feature plan/task paths, architecture notes,
and the scope decision follow-up. No Python/FastAPI, ML, database, contract, or
fixture source was modified.

### Checks run

| Command | Result |
|---|---|
| `npm.cmd --prefix web run test -- --run` | PASS: 12 files, 163 tests. Includes migrated API/contract tests and React case/dashboard tests. |
| `npm.cmd --prefix web run typecheck` | PASS: strict TypeScript, including `src`, `tests`, and `vite.config.ts`. |
| `npm.cmd --prefix web run build` | PASS: Vite production build. Existing large-chunk warning remains: main JS chunk is 893.52 kB minified. |
| `$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'; $env:PYTHONPATH = '.'; uv run --locked pytest backend/tests/integration/test_overview_api.py backend/tests/integration/test_dataset_api.py backend/tests/integration/test_cases.py -q` | PASS: 60 tests, 1 Starlette/httpx deprecation warning. |
| `npm.cmd install --package-lock-only --ignore-scripts --offline --prefix web` | PASS: lock metadata reconciled; npm reported 0 vulnerabilities among 92 packages. |
| JavaScript source scan in `web/src` and `web/tests` | PASS: no `.js`, `.jsx`, `.mjs`, or `.cjs` application files; no `any` type annotations/casts found. |
| `git diff --check` | PASS: no whitespace errors. Git only reported expected working-copy LF/CRLF notices. |

The first backend test invocation was blocked by access to the machine-level
uv cache lock. The workspace-cache retry first exposed a missing repository
root `PYTHONPATH`; with both documented local settings in place, all 60 tests
passed. The initial React test run intentionally failed because the missing
React `Cases` page had not yet been implemented; its replacement tests now pass.

### Remaining limitations

- No interactive visual browser review was performed in this migration unit.
- The production bundle exceeds Vite's 500 kB warning threshold; it built
  successfully, but chunk optimization and performance measurement remain open.
- This was frontend integration coverage, not model evaluation or an independent
  teammate reproduction.
- This record and the implementation are included in the requested commit; no
  push is included in this task.
