# Feature 005 security test coverage supplement

**Date:** 2026-11-16 (Europe/Budapest)  
**Branch:** `feature/005-real-time-fraud-detection-mlops-spec`  
**Scope:** local, synthetic, database-independent HTTP boundary and tracked-file
metadata. No production code, external network, real credentials, or database
lifecycle operation was used.

This supplement follows the focused audit in
`feature-005-security-edge-case-audit-2026-11-16.md`. It adds ten deterministic
tests in `backend/tests/integration/test_security_boundaries.py`. Assertions were
not weakened after execution. The authentication test remains RED because the
current API returns case data without an authenticated principal.

## Retained new-test results

| Test | Security risk | Result | Reason |
|---|---|---|---|
| `test_case_listing_requires_an_authenticated_principal` | Unauthenticated disclosure | **FAIL** | `/api/cases` returned 200 with case data; expected 401 or 403. Authentication remains unimplemented. |
| `test_hostile_origin_preflight_receives_no_cross_origin_permission` | Cross-origin access | **PASS** | Hostile preflight returned 405 with no allow-origin or allow-credentials header. |
| `test_dataset_sql_injection_payload_is_rejected_before_store_access` | SQL injection | **PASS** | Malicious case identifier returned generic 422 before the absent synthetic store could be opened; no SQL detail was exposed. |
| `test_xss_payload_is_not_reflected_by_case_validation` | Reflected XSS | **PASS** | Synthetic HTML/event-handler input returned generic JSON 422 and was not reflected. |
| `test_oversized_case_identifier_has_a_bounded_generic_response` | Oversized input / reflection | **PASS** | A 10,000-character identifier returned generic 422 under 512 response bytes without echo. |
| `test_unicode_confusable_case_identifier_is_rejected_without_echo` | Unicode identifier confusion | **PASS** | Full-width digits were rejected with generic 422 and were not echoed. |
| `test_encoded_path_traversal_does_not_expose_files_or_paths` | Path traversal / secret leakage | **PASS** | Encoded traversal returned a closed JSON error without repository paths, environment filename, or password-key text. |
| `test_unexpected_query_parameters_cannot_change_case_listing` | Parameter pollution / privilege confusion | **PASS** | Synthetic admin/role/limit parameters had no effect on status or payload. |
| `test_malformed_json_on_read_only_resource_is_not_parsed_or_reflected` | Malformed body / leakage | **PASS** | Unsupported POST returned generic 405 without reflecting the synthetic marker. |
| `test_tracked_files_exclude_private_env_and_key_material` | Secret material committed by filename | **PASS** | Git tracked no private `.env` filename or `.key`, `.pem`, `.p12`, or `.pfx` file; `.env.local` was not tracked. |

**Retained new tests:** 10 added; 9 passed; 1 failed; 0 skipped.

The 62 relevant existing tests in `test_api_errors.py`, `test_startup.py`,
`test_dataset_api.py`, and `test_cases.py` passed. The final combined focused run
therefore reported **71 passed, 1 failed, 0 skipped**, plus the existing
Starlette/httpx deprecation warning. Ruff passed for the new module.

## Commands executed

All commands ran from the repository root with `PYTHONPATH=.` for pytest,
locked offline dependencies, a task-specific uv cache, disabled pytest cache,
and workspace-local pytest temporary directories.

1. Initial test-first draft (11 collected; 10 passed, 1 authentication failure):
   `uv run --locked --offline pytest backend/tests/integration/test_security_boundaries.py -q -p no:cacheprovider --basetemp=.audit-tmp/security-coverage-new`
2. Retained ten-test module (9 passed, 1 authentication failure):
   `uv run --locked --offline pytest backend/tests/integration/test_security_boundaries.py -q -p no:cacheprovider --basetemp=.audit-tmp/security-new-final`
3. Relevant existing regressions (62 passed):
   `uv run --locked --offline pytest backend/tests/integration/test_api_errors.py backend/tests/integration/test_startup.py backend/tests/integration/test_dataset_api.py backend/tests/integration/test_cases.py -q -p no:cacheprovider --basetemp=.audit-tmp/security-existing-final`
4. Final combined focused run (71 passed, 1 authentication failure):
   `uv run --locked --offline pytest backend/tests/integration/test_security_boundaries.py backend/tests/integration/test_api_errors.py backend/tests/integration/test_startup.py backend/tests/integration/test_dataset_api.py backend/tests/integration/test_cases.py -q -p no:cacheprovider --basetemp=.audit-tmp/security-focused-final`
5. Final lint check (pass):
   `uv run --locked --offline ruff check backend/tests/integration/test_security_boundaries.py`

The first draft briefly contained a TRACE-method case. It was removed because
the existing framework method-negotiation test already covered the same 405
boundary, and the request limited additions to ten tests.

## Files created or modified by this unit

- Created `backend/tests/integration/test_security_boundaries.py`.
- Created this evidence supplement.
- Created `prompts/development/feature-005-security-test-coverage-2026-11-16.md`.
- Updated `next_work.md` with the actual result and next step.

No production application file was modified by this unit. Other pre-existing
working-tree changes were left intact.

## Related working-tree hardening verified during evidence reconciliation

The working tree already contained two related change groups that were outside
the ten-test-only unit above:

- `backend/src/fraudlens/local_api.py`, `backend/run_local_api.py`,
  `backend/README.md`, and `backend/tests/unit/test_local_api.py` define and test
  the supported local launcher. It fixes the bind to `127.0.0.1:8000`, disables
  reload, ignores hostile host environment variables, and documents that direct
  public Uvicorn launch is unsupported. This limits the supported local command;
  it is not an authentication control and can be bypassed by invoking Uvicorn
  directly with another host.
- `.gitignore`, `pyproject.toml`, `backend/tests/integration/conftest.py`,
  `backend/tests/integration/test_postgres_fixture_safety.py`, and additions to
  `backend/tests/integration/test_live_transactions.py` harden the PostgreSQL
  test lifecycle. Live tests require an explicit disposable-cluster flag and a
  loopback host, use a unique `fraudlens_test_<uuid>` database, serialize setup
  with an advisory lock, reject collisions, verify owner/name before cleanup,
  and never drop roles. Added live cases cover negative and inclusive/maximal
  amounts, malicious/oversized text, reused transaction identifiers, rollback,
  and concurrent exact retries, but those live cases have not yet executed
  under the new opt-in boundary.

Actual non-destructive reconciliation command:

`uv run --locked --offline pytest backend/tests/unit/test_local_api.py backend/tests/integration/test_postgres_fixture_safety.py backend/tests/integration/test_live_transactions.py -q -p no:cacheprovider --basetemp=.audit-tmp/evidence-reconcile`

Result: **14 passed, 20 skipped**. The pass count comprises one loopback-launcher
test and thirteen pure PostgreSQL guard cases. All live PostgreSQL cases skipped
because `FRAUDLENS_TEST_PG_DISPOSABLE` was removed from the command environment.
No database connection, creation, mutation, or cleanup was attempted.

The related Ruff command covered the launcher, fixture, live tests, and security
module and returned `All checks passed!`:

`uv run --locked --offline ruff check backend/src/fraudlens/local_api.py backend/run_local_api.py backend/tests/unit/test_local_api.py backend/tests/integration/conftest.py backend/tests/integration/test_postgres_fixture_safety.py backend/tests/integration/test_live_transactions.py backend/tests/integration/test_security_boundaries.py`

## Security gaps still untested or not implemented

- Authentication and authorization are **NOT IMPLEMENTED** on the reviewed API;
  the retained RED test demonstrates the unauthenticated disclosure.
- RBAC/ABAC, MFA, sessions, password hashing, and secure cookies are **NOT
  IMPLEMENTED / NOT TESTABLE** in the current API.
- TLS, WAF, DDoS controls, HSTS, origin-IP protection, host hardening, backups,
  encryption at rest, and deployment port policy are **NOT TESTABLE** in this
  local application-test scope.
- No real-browser DOM XSS, CSP, browser CORS, cookie, or security-header test ran.
- The PostgreSQL injection-shaped text, concurrency, rollback, and lock-timeout
  cases are present but require the disposable opt-in. The new loopback outage
  test passes with a bounded connection timeout; the lock-timeout case skipped
  because Docker was unavailable. The HTTP SQL-injection case covers validation
  before store access only.
- The tracked-file check detects secret-like filenames, not secret values or Git
  history. No dedicated secret scanner was available.
- Request-size enforcement at a production ASGI server or reverse proxy was not
  tested; the oversized case covers a path parameter through `TestClient`.
- Python dependency advisories remain unverified because this unit used no
  external network and the prior OSV request was blocked.

## Recommended next testing priorities

1. Implement the separately approved analyst authentication boundary, then make
   the retained RED test pass and add role-denial, role-allow, token expiry, and
   session/cookie tests.
2. Restore an explicitly disposable PostgreSQL instance and run the skipped
   parameterized-query, duplicate, concurrent-write, rollback, and lock-timeout
   cases; retain the passing bounded loopback-outage test.
3. Test the built site in a real browser for DOM XSS, CSP/security headers,
   hostile origins, navigation, and sensitive-data rendering.
4. Run an approved local secret scanner over tracked content and Git history,
   then run locked dependency audits with a dated advisory database.
5. Verify body and header size limits at the actual ASGI server and deployment
   proxy boundary when those components are defined.

