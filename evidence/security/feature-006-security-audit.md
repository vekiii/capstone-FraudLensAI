# Feature 006 controlled security audit — 2026-11-22

## Scope and provenance

Branch `feature/006-security-edge-case-audit` was created from fetched `origin/integration/capstone-mvp` at `d46699fbd11219ebc92c6ef002d4924a4c7d4b34`. Source checkout before branching was clean at `28a938ab68824c6eb7e896882adfd65984e336cc`. This is a local, single-user, synthetic AML capstone, not a production or multi-user security claim. The Feature 002 spec explicitly says the local workflow gate is not user authentication (FR-034). No production code, model, feature publication, threshold, protocol, predictions, labels, or evaluation was changed or opened. The untracked T230 ZIP and checksum became visible after switching branches; they were not opened, modified, or added to Git.

Authoritative context: `specs/002-data-and-risk-scoring/{spec,protocol,plan,tasks}.md`, `AGENTS.md`, `.specify/memory/constitution.md`, `next_work.md`, and current implementation. T252 human reproduction and T254–T255 showcase replay remain open. Historical planning text about pending model fitting is superseded by execution evidence. The branch adds one synthetic test module and documentation only.

## Architecture and trust boundaries

| Boundary | Inputs and controls | Failure and exposure assessment |
|---|---|---|
| Browser → FastAPI | `web/` decodes external JSON with closed contracts; React and legacy scoring views use text rendering; CSP meta in `web/index.html` | No CORS middleware observed. Browser origin restrictions are not authentication. Malformed responses are rejected in existing Vitest coverage. |
| HTTP → Pydantic | `backend/src/fraudlens/main.py` has generic validation, HTTP, response and exception handlers; bounded canonical risk ID; closed response models | Risk route does not reject unknown query keys (F006-01). API response lacks hardening headers (F006-02). |
| Case lookup | Fixture `CaseService`; no account principal or multi-user isolation | Anonymous `/api/cases` returns fixture cases by design for local demo. Network exposure changes the risk (F006-03). |
| Canonical row → features | Decimal text amount check; exact bank/account text; strict timestamp parser; `_validate_row` requires eleven ordered logical fields, nonnegative counts and finite values | Existing synthetic tests cover malformed amounts, row identity, strict-prior history, ties, warm-up, currency separation. No arbitrary public transaction submission route exists. |
| Features → model | `FeatureStore` hash checks manifest and all three label-free files; `ModelScorer` validates 11 logical fields, maps categories via frozen vocabulary to 32 matrix columns, checks finite `[0,1]` score | Each lookup rehashes/scans files; bounded local availability concern (F006-04). No score fallback. |
| Artifact → native parser | Independent manifest/source/protocol/model pins, format/runtime/feature/threshold checks before `lgb.Booster`; path containment and bounded reads | Existing synthetic tests cover tamper, metadata mismatch and symlink escape. No pickle/joblib/download/startup training found. Same-root file substitution race was not proven exploitable. |
| Reports/EDA → API | `ResultsService` demands local model mode and frozen authorization/completion/report lineage; EDA reads hash-pinned label-free summary | Query expansion returns 422. Closed schemas exclude record-level labels. Real reports were absent in this checkout, so live 200 was not verified. |
| Runtime/logs/files | README Uvicorn command binds `127.0.0.1`; generic errors and type-only logs; generated data/model paths ignored | Direct Uvicorn can be rebound by an operator. No static route for raw CSV or restricted labels found. Tracked-file filename scan found no raw/model/key files. |

### Actual endpoint inventory

Observed in `main.py`, `bridge_api.py`, `investigation/api.py`, `investigation/semantic_api.py`, and `simulation/api.py` (GET routes also support framework HEAD only where defined):

| Method and path | Input / response / controlled failure |
|---|---|
| GET `/api/health` | No input; `Health` or `ModelHealth`; generic 500. |
| GET `/api/cases`, `/api/cases/{case_id}` | Case ID validated by Pydantic; `CaseList` / `CaseDetail`; 404/422/500 generic errors. |
| GET `/api/transactions/{transaction_id}/risk` | Canonical ID; `PredictionResult`; 404, 409, 422, 503; unknown query keys currently ignored. |
| GET `/api/model/results` | No query allowed; `ModelResults`; 409/404/422/500. |
| GET `/api/eda/summary` | No query allowed; `EdaSummary`; 404/422/500. |
| GET `/api/model/cases`, `/api/model/cases/by-transaction/{transaction_id}`, `/api/model/cases/{case_id}` | Closed list/binding/detail requests; bounded published case/binding response or 409/422/404/503. |
| GET `/api/knowledge/documents`, `/api/knowledge/search`, `/api/knowledge/passages/{passage_id}` | Closed corpus/retrieval/query arguments; validated knowledge responses or 404/422/503. |
| POST `/api/knowledge/semantic-search`, GET `/api/knowledge/semantic-search/status`, POST `/api/knowledge/semantic-search/cancel` | Feature-gated semantic workflow with request validation and controlled errors. |
| `/api/investigation/*` routes | Feature-gated local investigation state and review operations; per-route validation and `local_guard` host/origin checks for mutation. See `investigation/api.py` and its existing integration suites. |
| GET `/api/simulation/scenarios`, POST `/api/simulation/comparisons` | Bounded simulation catalog and comparison contracts; no fitting or real-label access. |

There is no transaction-submission route. The integrated `web/` app is the browser frontend; historical `frontend/` and Feature 005 PostgreSQL/dataset routes are absent from this candidate.

## Findings

### F006-01 — Unsupported risk query reaches lookup (Low, confirmed reliability defect)

- **Type/component:** API input boundary, `backend/src/fraudlens/main.py:176–196`.
- **Requirement:** FR-031/FR-034 and `plan.md` read-only closed assessment boundary; results/EDA explicitly reject queries.
- **Evidence/reproduction:** `backend/tests/integration/test_security_audit.py::test_risk_query_cannot_expand_or_change_assessment` sends `partition=showcase&include_labels=true&threshold=0` to a synthetic model app. Expected 422 before lookup/scoring; actual 503 after the stub lookup and scorer ran. The test remains failing. The query keys did not change the assessment or expose labels; no bypass of the frozen threshold was demonstrated.
- **Impact/confidence:** High confidence in inconsistent request validation; low local security impact, potential needless lookup work and misleading response. No direct data leak established.
- **Recommendation:** Reject any query parameter at route entry and prove the store/scorer were not called. **Team scope decision:** no, routine closed-contract correction after review.

### F006-02 — API security headers absent (Low, missing hardening control)

- **Type/component:** HTTP response, `backend/src/fraudlens/main.py:80–225`.
- **Requirement:** Local-only serving assumption; no Feature 002 requirement mandates these headers.
- **Evidence/reproduction:** In-process `GET /api/health` returned no `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, `Cache-Control`, or CORS header. `web/index.html` does declare a restrictive CSP meta tag. This is a direct response observation, not proof of XSS or cache disclosure.
- **Impact/confidence:** High confidence header absence; low risk in approved loopback workflow. HTTP headers would matter more for shared hosting.
- **Recommendation:** If a deployment boundary is defined, add appropriate API and web headers at the server/reverse proxy and test both success/error responses. **Team scope decision:** yes for new deployment expectations; local defense in depth can be reviewed separately.

### F006-03 — Anonymous case reads depend on loopback deployment (Informational locally; exposure concern if hosted)

- **Type/component:** Access boundary, `backend/src/fraudlens/main.py:163–171`, `README.md:37,69`.
- **Requirement:** FR-032 preserves foundation cases; FR-034 expressly uses local workflow authorization and disclaims user authentication; Feature 002 excludes multi-user/deployment claims.
- **Evidence/reproduction:** `test_fixture_case_listing_is_local_single_user_behavior` passes: unauthenticated `GET /api/cases` returns 200. Supported README launch binds `127.0.0.1`. No CORS middleware was found. A direct operator-selected public bind would expose the unauthenticated API, including cases and potentially aggregate/model routes.
- **Impact/confidence:** High confidence in current behavior; severity for a public bind cannot be assigned without a deployment decision. This is **A: intended local single-user behavior**, and **C: vulnerability under additional public/shared exposure assumptions**. No current unsafe bind was observed.
- **Recommendation:** Keep loopback-only operational guidance explicit. Decide deployment and identity scope before exposing beyond the local machine. **Team scope decision:** yes for authentication, accounts, or public hosting.

### F006-04 — Model lookup scans and rehashes all feature partitions per request (Low, confirmed design limit)

- **Type/component:** Availability, `backend/src/fraudlens/scoring/model_scorer.py:60–100`.
- **Requirement:** FR-006 bounded preparation and FR-030/031 controlled local serving. No strict latency SLO is frozen.
- **Evidence/reproduction:** Source inspection shows every lookup streams each train/validation/test JSONL, updates a digest for every line, and checks the digest at the end. A hit does not stop the scan. No load or real-data timing test was run under this audit.
- **Impact/confidence:** High confidence in linear per-request work; performance impact on the full snapshot is unmeasured. Repeated requests can impose repeated disk/CPU work locally; no demonstrated denial of service.
- **Recommendation:** Measure on approved synthetic scale and consider a hash-verified local index/cache with immutable publication semantics. **Team scope decision:** likely no for local optimization; yes if service or hosting guarantees change.

## Prior Feature 005 comparison

The `5ea0c4c` tests and Feature 005 audit were inspected, not copied or cherry-picked. Its unauthenticated `/api/cases` RED remains observable, but the Feature 002 FR-034 local assumption supersedes the earlier expected 401/403 for this candidate. The prior CSP browser check is present in `web/src/security.test.tsx` and passes; its backend security-header and >1 MiB body middleware are absent from this integration branch. Feature 005 PostgreSQL, dataset-mode, and old `frontend/` cases are not applicable. The prior credential traceback concerned a separate PostgreSQL fixture; this audit did not read credentials or test a database. Feature 005's historical security work does not constitute deployment approval here.

## Execution and limits

- New suite: **15 passed, 1 failed**. Initial draft also had a 404 for an HTML probe containing `/`; the probe was corrected to remain within one route segment before the final run. The retained failure is F006-01.
- Closest independent backend regressions: **129 passed, 1 skipped** (Windows symlink permission), one Starlette/httpx deprecation warning.
- Additional canonical validation, train-only boundary, and synthetic model scorer regressions: **39 passed**.
- Combined selected backend run including results tests: **146 passed, 3 failed, 2 skipped**. One failure is F006-01. Two existing `test_results_api.py` cases expected 404 but received 409 because this checkout has no frozen authorization/completion files; they do not demonstrate a report-loader defect. The live report test skipped.
- React/Vitest: **290 passed**. TypeScript typecheck and Vite build passed; build warned about a large Three.js chunk. Ruff on the new test file and `git diff --check` passed.
- `uv run --offline --locked` could not acquire the machine-local uv cache lock; checks used the pre-existing `.venv` Python 3.14.10 without installation or lockfile changes. Bandit, pip-audit, Semgrep, and Gitleaks were unavailable. npm audit and network-dependent scans were not run. No full backend suite was run; broader investigation/simulation boundaries have existing suites but were not exhaustively adversarially assessed here.
- The Git tracked-file path scan found no raw/processed/eval files, model text, CSV, private environment or key filenames. This is not a full secret scan. No external service was scanned.

The preserved frozen invariants were checked by source/tests and by no-change status, not by reopening restricted artifacts. There is no new ML quality or evaluation conclusion. Human review is required before production fixes or broader deployment decisions.
