# Feature 005 Security and Edge-Case Audit

**Date:** 2026-11-16 (Europe/Budapest)
**Branch:** `feature/005-real-time-fraud-detection-mlops-spec`
**Baseline commit:** `487c427ea50e169f5e36898420d659f05ead2c60`
**Recommendation:** **GO for the local synthetic/read-only demonstration in the audited scope. NO-GO for external deployment or a real-time fraud-detection claim.** This recommendation does not evaluate or complete Phase 4.

## Scope and method

The initial working tree was clean. The audit covered the existing FastAPI/Feature 002 fixture and batch API, Feature 005 immutable PostgreSQL fact schema and synthetic producer, the `frontend/` app, and the separate `web/` showcase. It did not implement features, change runtime behavior, change task checkboxes, or contact production services. No real transaction data was used.

T022's live worker, live scoring, persisted assessments, and live API are not present. The task backlog records T022 and its Phase 3 prerequisites as incomplete; Phase 4 tasks depend on T022. Existing fraud scoring is in the Feature 002 fixture/batch path (`backend/src/fraudlens/scoring.py`, `rule_scoring.py`, `model_scoring.py`), not an online T022 path. The T057 showcase is illustrative and says it is not live scoring (`web/src/pages/Live.tsx`).

**Environment:** Windows 11; Python 3.14.10 in the locked uv environment (host `python` resolves to 3.13.3); uv 0.13.8; Node 24.21.0; npm 11.19.0; local PowerShell. Tests used locked/offline Python dependencies and installed npm lockfiles. Python temp/cache paths were moved to task-specific writable locations after default user cache/temp permissions denied access. No browser session or PostgreSQL integration run was used.

**Tools:** pytest, Ruff, uv audit, npm audit, Vitest, TypeScript compiler, Vite production builds, Git and source review. A dedicated secret scanner (for example, Gitleaks) was unavailable. No SQL scanner, browser automation, Lighthouse, or accessibility scanner was run.

## Results summary

| Check | Result | Observed result |
|---|---|---|
| Database-independent API and persistence regressions | **PASS** | 102 passed, 1 Starlette/httpx deprecation warning |
| Full backend unit suite | **FAIL** | 418 passed, 71 failed, 4 errors; details below |
| Ruff | **PASS** | `All checks passed!` |
| Frontend tests | **PASS** | 174 passed in 10 test files |
| Frontend typecheck/build | **PASS** | Both passed; no build warning |
| Showcase tests | **PASS** | 9 passed in 3 files |
| Showcase typecheck/build | **PASS with warning** | Both passed; Vite warned the 860.70 kB minified JS chunk exceeds 500 kB |
| npm dependency audits | **PASS, offline advisory data** | Both lockfiles reported 0 vulnerabilities; commands used `--offline` |
| Python dependency audit | **BLOCKED** | `uv audit --locked` reached OSV but its HTTPS connection was denied by host network policy; no vulnerability result obtained |
| PostgreSQL integration/security tests | **NOT RUN** | Existing fixture creates and drops a database and may drop test-created roles; avoided under the no-destructive-database rule |
| Browser route/accessibility/performance checks | **NOT TESTED** | No browser execution, Lighthouse, keyboard/contrast measurement, or performance measurement |
| T022 live worker/online scoring | **NOT TESTED / NOT IMPLEMENTED** | No implementation to exercise |

## Exact commands and outcomes

Commands below ran from the repository root. For Python commands, `UV_CACHE_DIR` was set to `%TEMP%\fraudlens-uv-cache-audit-2026-11-16`. `PYTHONPATH=.` was set for pytest. Pytest cache was disabled and its temporary base was under the repository's ignored audit temp directory.

| Command | Exit | Result |
|---|---:|---|
| `uv run --locked --offline pytest backend/tests/unit -q -p no:cacheprovider --basetemp=.audit-tmp/pytest` | 1 | 418 passed, 71 failed, 4 errors, 10.05s |
| `uv run --locked --offline pytest backend/tests/integration/test_api_errors.py backend/tests/integration/test_startup.py backend/tests/integration/test_dataset_api.py backend/tests/integration/test_overview_api.py backend/tests/integration/test_cases.py backend/tests/integration/test_run_publication.py backend/tests/integration/test_reproduction.py backend/tests/integration/test_evaluation_pipeline.py -q -p no:cacheprovider --basetemp=.audit-tmp/safe-integration` | 0 | 102 passed, 1 warning, 9.86s |
| `uv run --locked --offline ruff check backend/src backend/tests/unit` | 0 | All checks passed |
| `npm.cmd --prefix frontend run test -- --run` | 0 | 174 passed |
| `npm.cmd --prefix frontend run typecheck` | 0 | Passed |
| `npm.cmd --prefix frontend run build` | 0 | Passed |
| `npm.cmd --prefix frontend audit --offline --audit-level=low` | 0 | Found 0 vulnerabilities |
| `npm.cmd --prefix web run test -- --run` | 0 | 9 passed |
| `npm.cmd --prefix web run typecheck` | 0 | Passed |
| `npm.cmd --prefix web run build` | 0 | Passed; Vite large-chunk warning (860.70 kB minified JS) |
| `npm.cmd --prefix web audit --offline --audit-level=low` | 0 | Found 0 vulnerabilities |
| `uv audit --locked` | 2 | OSV request failed after retries; `api.osv.dev` connection denied by socket policy |

The backend unit failures are not represented as security-test passes. The output showed absent trusted Feature 002 artifact manifests under ignored `artifacts/`, missing `fraudlens.pretrained_inference` adapter tests marked RED, unavailable model artifacts, and a Windows symlink privilege error (`WinError 1314`). Several pretrained loader/model tests therefore failed or errored. The broad run is **not green**. It is consistent with the handoff's known artifact/Windows limitations, but this audit did not rerun a baseline commit in an isolated checkout and does not claim every failure was proven pre-existing.

The first uv attempts also encountered denied default cache/temp access; those were harness failures, not product results. The final recorded pytest run used the workspace-local temp base. No local database was created, dropped, or modified by this audit.

## Security findings

### Medium — API has no authentication boundary

`backend/src/fraudlens/main.py:109-177` exposes health, overview, case-list, and case-detail GET routes without authentication or authorization dependencies. The current application has no public mutation route, and dataset mode is an explicitly selected local mode, but anyone who can reach an instance can read its configured case/run data. The showcase itself uses synthetic illustrative data. Keep the API loopback-only for local use; before any shared or externally reachable deployment, add and test analyst authorization and ensure the service binds behind an approved access boundary. This is also explicitly future work in T028, which remains unchecked. **Release impact:** blocks external deployment; it does not block the local synthetic demo.

No Critical or High exploitable finding was established in the reviewed local scope. This is a focused review, not a formal penetration test.

## Security review notes

- **Secrets/configuration:** `.env`/`.env.*` are ignored and `.env.example` is explicitly allowed. The local PostgreSQL credential file path is described as ignored in `infra/compose/README.md`; the file contents were never read or printed. The tracked-file/path review found no tracked environment credential file. No dedicated secret scanner was available, so this is not a comprehensive secret-history scan.
- **SQL injection:** `backend/src/fraudlens/live_store.py:76-111` binds transaction fields as parameters; the migration's function uses typed parameters. Dataset queries are reviewed as parameterized in `backend/src/fraudlens/data_store.py`. No dynamic SQL composed from request strings was identified in reviewed API paths.
- **PostgreSQL roles and mutation:** `backend/migrations/001_live_facts.sql:35-55` applies required fields, identity uniqueness, finite timestamps, amount bounds and scale limits. The security-definer ingestion function pins `search_path` (`:108-109`), is revoked from `PUBLIC`, and is granted to `live_producer` only (`:157-167`). The immutable trigger and receipt function are present. Catalog/privilege assertions exist in `backend/tests/integration/test_live_transactions.py`, but were not executed in this audit because the fixture creates/drops databases and roles.
- **Input boundaries:** `LiveTransaction.__post_init__` at `backend/src/fraudlens/live_store.py:36-45` rejects naive timestamps, non-Decimal amounts, NaN and infinity. Non-negative, maximum magnitude, scale, field length, identifier syntax and nonblank constraints are enforced by PostgreSQL, not at Python object construction. There is no live HTTP ingestion route. Direct producer callers should expect database constraint failures for invalid values; more friendly pre-insert validation remains a gap if this boundary is expanded.
- **Duplicate/concurrency/transactions:** the schema has primary/unique identities and `record_live_transaction` uses `ON CONFLICT DO NOTHING` followed by exact-fact comparison (`backend/migrations/001_live_facts.sql:108-152`). Existing tests cover exact duplicate and changed-fact conflict. Concurrent same-key writes, database outage/timeout, rollback behavior and recovery were **not tested** here.
- **API errors and validation:** public error bodies are normalized and exception details are redacted in `backend/src/fraudlens/main.py`; selected tests passed, including malformed request and generic error handling. Dataset mode has strict ID/snapshot patterns and returns closed errors. CSRF is not applicable to the current read-only API because it has no cookie-authenticated state-changing routes. No permissive CORS middleware was found; browser CORS behavior was not exercised.
- **XSS/HTML:** React-rendered content is used in the inspected frontend/showcase; searches found no `dangerouslySetInnerHTML` or direct `innerHTML` assignment. This is source inspection, not browser-based XSS testing.
- **Frontend resilience/accessibility:** route fallback sends unknown showcase routes to Overview (`web/src/main.tsx`); data loading/fixture fallback and reduced-motion logic have unit coverage. WebGL renderer construction catches failure and sets a fallback marker (`web/src/webgl/capabilities.ts:5-14`), but no direct WebGL capability test or real browser failure injection was run. Reduced-motion helper tests passed; browser preference behavior, keyboard navigation, focus behavior, contrast and screen-reader accessibility were not verified.
- **Dependency status:** npm's local/offline advisory result is zero for both committed lockfiles. Python's dependency vulnerability status remains unknown because OSV access was blocked. No dependency upgrades were made.

## Edge-case matrix

| Area | Expected | Actual / coverage |
|---|---|---|
| Missing, malformed API query/path values | Closed 4xx without internals | **PASS** selected API tests (invalid IDs, request validation and errors) |
| Missing local fixture/run store | Safe generic failure/unavailable state | **PASS** selected API tests; no paths leaked |
| Scoring input/output failures in fixture/batch path | Reject/fail closed; no silent zero-risk fallback | **PARTIAL** scoring unit suite in full run includes failures/errors from missing model assets/adapter; fixture API error tests pass |
| Null/non-finite/negative/oversized amounts | Reject before persistence or at DB constraint | **PARTIAL** code review: Python rejects non-Decimal/non-finite; SQL enforces nonnegative/max/scale. PostgreSQL boundary tests **NOT RUN** |
| Timestamp without timezone / boundary timestamp | Reject naive; retain UTC-aware timestamp | **PARTIAL** Python check reviewed; PostgreSQL UTC round-trip test **NOT RUN** |
| Invalid/oversized/duplicate IDs and currencies | Contract rejection or safe DB constraint failure; duplicate exact replay is idempotent | **PARTIAL** SQL constraints and test cases reviewed; DB tests **NOT RUN**; application constructor does not fully validate text fields |
| DB unavailable, timeout, rollback, concurrent writes | Bounded fail-closed behavior and atomic/idempotent result | **NOT TESTED**; no live worker/DB outage drill executed |
| JSON/local files malformed or missing | Controlled fallback/error | Showcase JSON tests passed for current generated fixtures; malformed response/missing file injection and browser response failures **NOT TESTED** |
| XSS/CSRF/CORS | No unsafe injection, unnecessary CSRF surface or permissive cross-origin access | Source review found no unsafe HTML sink, state-changing browser route or CORS middleware; browser-origin tests **NOT TESTED** |
| Route failures | Usable fallback / not-found behavior | Showcase wildcard route maps to Overview by code; no browser navigation test. Frontend API failure lifecycle unit tests are included in 174 passing tests |
| Reduced motion/WebGL | Motion is reduced; renderer failure falls back safely | Reduced-motion unit coverage passed. WebGL construction fallback exists; actual browser/WebGL execution **NOT TESTED** |
| Live fraud scoring | Exercise only if implemented | **NOT APPLICABLE** to T022: live worker/scoring absent. Existing Feature 002 fixture/batch scoring is not equivalent to online scoring |

## Reproduction steps for failures / blockers

1. Run the full backend unit command in the exact-commands table with a writable uv cache, `PYTHONPATH=.`, and workspace-local `--basetemp`. It returns 1 and reports 71 failed, 418 passed, 4 errors. Failure details include missing Feature 002 model manifests/artifacts, RED/missing pretrained-adapter tests, and Windows symlink privilege (`WinError 1314`).
2. Run `uv audit --locked`; it returns 2 after retrying `https://api.osv.dev/v1/querybatch`, with Windows socket access denied. Re-run only when an approved network path is available.
3. PostgreSQL live transaction/producer integration tests are intentionally omitted: their `isolated_live_postgres` fixture in `backend/tests/integration/conftest.py` issues `CREATE DATABASE`, then `DROP DATABASE ... WITH (FORCE)` and may drop globally created test roles. A separate disposable PostgreSQL instance and explicit safe lifecycle would be required to execute them.

## Residual risks and recommended fixes

1. Keep API binding restricted to loopback or add analyst authentication/authorization and deployment-boundary tests before sharing it; T028 is the planned implementation gate.
2. Restore the exact trusted model artifacts needed by Feature 002 and resolve the Windows symlink test environment; rerun the failing backend suite and record a verified baseline comparison before treating failures as regressions or waiving them.
3. Run Python dependency audit when OSV access is permitted, retaining the lockfile and exact advisory database date/result.
4. Arrange a disposable isolated PostgreSQL environment, then run migration/catalog, validation, duplicate, rollback, concurrent-write, timeout, and database-unavailable cases without touching the persistent local database.
5. If ingestion is added, validate identifiers, text bounds, currency syntax and amount sign/size/scale before database work, and test malformed/oversized payload limits.
6. Run browser route-failure, WebGL-disabled, reduced-motion, keyboard/focus/contrast, and performance checks on the built showcase; current unit/build checks do not establish those properties.
7. Preserve the existing task state. T022, Phase 4, T002, and T058 remain at their recorded states; this audit does not verify or advance those gates.

## Final decision

**GO:** the reviewed local synthetic/read-only demo and current Feature 002 fixture/batch API may be used for local development under the documented loopback/local assumptions, based on passing selected regressions, frontend suites/builds, Ruff, and local npm audits.

**NO-GO:** external/shared exposure or any claim of live real-time fraud scoring. The current API has no auth boundary, Python dependency advisories are unverified, PostgreSQL fault/concurrency security checks were deliberately not run, and T022/Phase 4 are not implemented/verified. This is strictly a recommendation for the audited scope, not a Phase 4 completion assessment.
