# Feature 006 security test coverage — 2026-11-22

All new probes use FastAPI `TestClient`, synthetic IDs, stubs and fixture mode. No real artifact, restricted label, external endpoint or training procedure was used. Status reflects this branch at `d46699f` plus the uncommitted audit test.

| Test ID | Component | Scenario | Expected behavior | Actual result | Status |
|---|---|---|---|---|---|
| SEC-001-A | Five read-only API routes | POST with malformed JSON and synthetic marker | Generic 405, no reflection | 5 parameter cases passed | PASS |
| SEC-001-B | Risk ID | 10,000 chars, fixture ID, row zero/leading zero, HTML, Unicode | 422, bounded, no lookup/echo | 6 parameter cases passed | PASS |
| SEC-001-C | Risk query | Showcase/label/threshold keys | 422 before store/scorer | 503 after store/scorer; retained RED | FAIL |
| SEC-001-D | API errors | Unexpected scorer exception | Generic 500, no zero-risk result or private marker | Passed | PASS |
| SEC-001-E | HTTP configuration | Headers, CORS, debug, localhost | Observe actual controls | No API hardening/CORS headers; README bind 127.0.0.1; no debug enabling found | PASS |
| SEC-002-A | Fixture cases | Anonymous local case list | 200 per FR-034 local workflow | 200, list only | PASS |
| SEC-002-B | Results/EDA | Arbitrary showcase/label query | 422 with no marker | 2 parameter cases passed | PASS |
| SEC-002-C | Public hosting/access controls | Account isolation and roles | Deployment decision first | No multi-user system in scope | NOT IMPLEMENTED |
| SEC-003-A | Canonical rows | Bad amount, time, identity, label encoding | Bounded rejection codes | Existing `test_dataset_validation.py` passed in a separate 39-test run | PASS |
| SEC-003-B | Feature input | Negative count, nonfinite, category collision and frozen order | Reject before model | Existing `test_scoring_boundary.py` and related checks in 129-pass run | PASS |
| SEC-004-A | Native artifact | Tamper, wrong pins/format/runtime, traversal/symlink | Reject before native parser | `test_artifacts.py` passed except Windows symlink skip | PASS |
| SEC-004-B | Symlink escape | Create local symlink fixture | Reject escape | Windows privilege unavailable | SKIPPED |
| SEC-004-C | Path substitution race | Concurrent mutation during verification | Fail closed | No safe deterministic reproduction in this pass | NOT IMPLEMENTED |
| SEC-005-A | 11 logical features → matrix | Frozen order, vocabulary, width 32 | Reject malformed input; frozen map | `test_scoring_boundary.py` passed; source inspection | PASS |
| SEC-006-A | Risk output | Identity mismatch, NaN/malformed result, unavailable scorer | Controlled unavailable/error | `test_risk_api.py` and new exception probe passed | PASS |
| SEC-007-A | Large ID and repeated reads | Bounded response and no leaked content | Controlled rejection | Large ID passed; full-scale repeated-read timing not executed | PASS |
| SEC-007-B | Full-source model lookup load | Safe bounded concurrency/time | Measure without real source | No full-source load run under audit restrictions | SKIPPED |
| SEC-008-A | Aggregate and label boundary | No record labels or arbitrary subsets | Closed output / 422 | Results/EDA contracts and query probes passed; real report 200 skipped | PASS |
| SEC-008-B | Git tracked paths | Raw/model/key filenames absent | None tracked | `git ls-files` pattern scan returned no matches | PASS |
| SEC-008-C | Secret scanner and dependency audit | Tool reports | Run if installed/permitted | Bandit/pip-audit/Semgrep/Gitleaks unavailable; npm audit requires network | BLOCKED |
| SEC-009-A | React frontend | XSS text, malformed JSON, score/EDA failure states | Inert text or explicit error | Existing 290 Vitest tests passed; typecheck/build passed | PASS |
| SEC-010-A | Temporal and ML governance | Same-instant, warm-up, currency, labels and no fit | Strict prior; no implicit eval/training | Existing temporal/scoring tests passed; code inspection of runtime routes | PASS |
| SEC-010-B | Real frozen artifact/evaluation | Preserve hashes and sealed test labels | No mutation or repeat | No artifacts opened; status/diff contain audit test/docs only | PASS |
| REG-RESULTS | Existing results API | Missing approval/report synthetic path | 409/404 by fixture setup | Two 409 vs expected 404 because prerequisite approval/completion absent locally; one live case skipped | FAIL |

## Exact execution

1. `.\.venv\Scripts\python.exe -m pytest -q backend/tests/integration/test_security_audit.py -p no:cacheprovider` — **15 passed, 1 failed**, 1 warning.
2. `.\.venv\Scripts\python.exe -m pytest -q backend/tests/integration/test_api_errors.py backend/tests/integration/test_cases.py backend/tests/integration/test_risk_api.py backend/tests/integration/test_eda_api.py backend/tests/unit/test_artifacts.py backend/tests/unit/test_scoring_boundary.py backend/tests/unit/test_temporal_features.py -p no:cacheprovider` — **129 passed, 1 skipped**, 1 warning.
3. Combined command above plus `test_security_audit.py` and `test_results_api.py` — **146 passed, 3 failed, 2 skipped**. The two existing results failures are conditional on missing local approval/completion evidence; see audit report.
4. `npm.cmd --prefix web run test -- --run` — **290 passed, 19 files**.
5. `npm.cmd --prefix web run typecheck` and `npm.cmd --prefix web run build` — both passed; build chunk-size warning.
6. `.\.venv\Scripts\python.exe -m ruff check backend/tests/integration/test_security_audit.py` and `git diff --check` — passed.
7. `uv run --offline --locked --group ml pytest ...` — blocked before collection by machine-local uv cache lock access denial. Pre-existing `.venv` was used without dependency changes.
8. `.\.venv\Scripts\python.exe -m pytest -q backend/tests/unit/test_dataset_validation.py backend/tests/unit/test_training_boundaries.py backend/tests/unit/test_model_scorer.py -p no:cacheprovider` — **39 passed**.

Counts from separate commands overlap and must not be added as unique tests. The only new retained test failure is SEC-001-C. `REG-RESULTS` is an existing test/environment prerequisite mismatch, not counted as a confirmed vulnerability. No full backend suite, network dependency audit, live load test or restricted label verification ran.
