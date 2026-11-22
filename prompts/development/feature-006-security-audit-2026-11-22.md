# TASK: FraudLens MVP — Security Audit and Adversarial Edge-Case Testing

Act as a **Senior Application Security Engineer, ML Security Engineer, QA Automation Engineer, and Spec-Driven Development Reviewer**.

Your responsibility is to conduct a controlled, evidence-based security and reliability assessment of the integrated FraudLens MVP.

**This is an authorized defensive audit of our own application.**

You must create an isolated security-testing branch, inspect the existing project specifications and implementation, develop synthetic security tests, execute safe local checks, and document the findings.

Do not train, refit, replace, or reevaluate the ML model.

Do not modify production implementation without separate authorization.

---

## PHASE 0 — Repository inspection and branch isolation

### 0.1 Inspect the current Git state

Before changing anything:

1. Identify the current branch and HEAD commit.
2. Run `git status --short`.
3. Identify the configured remote and integration branch.
4. Check for uncommitted or untracked work.
5. Verify that existing Feature 002 files and evidence are preserved.

The previous handoff identified:

- Current feature branch: `feature/002-clean-start`
- Previously observed HEAD: `28a938a`
- Integration branch: `origin/integration/capstone-mvp`
- Previously observed integration commit: `d46699f`

These commit identities are historical observations, not guarantees about the current remote.

### 0.2 Create the security branch

Use the latest integration candidate as the base, not Feature 002 directly.

Fetch the integration reference:

`git fetch origin integration/capstone-mvp`

Verify its updated commit.

If the working tree is clean, create:

`feature/006-security-edge-case-audit`

from:

`origin/integration/capstone-mvp`

Do not reset, force checkout, delete branches, overwrite files, or discard local changes.

If the working tree is dirty, prefer a safe separate Git worktree where feasible. If isolation cannot be performed without risking existing changes, stop and explain the blocker.

If fetching fails, do not silently use a stale integration reference.

If the proposed branch already exists, inspect it without overwriting anything. Report the conflict rather than silently reusing an unrelated branch.

After branch creation, report the exact base commit and working-tree status.

Do not push or merge automatically.

### 0.3 Inspect prior security work

Review the existing branch:

`feature/005-real-time-fraud-detection-mlops-spec`

Inspect relevant commits, especially:

`5ea0c4c`

Read, where available:

- `evidence/security/feature-005-security-edge-case-audit-2026-11-16.md`
- `evidence/security/feature-005-security-test-coverage-2026-11-16.md`
- `test_security_boundaries.py`
- `test_security_hardening.py`

Pay particular attention to the previously reported unauthenticated `GET /api/cases` behavior.

Determine whether the issue persists in the integrated application and whether it violates the documented local single-user security boundary.

Do not automatically classify the absence of authentication as an exploitable vulnerability without considering the approved deployment assumptions.

Do not cherry-pick or merge the old security commit automatically. Identify reusable tests and fixes for later review.

---

## PHASE 1 — Read authoritative project documents

Read the following repository files before designing tests:

- `specs/002-data-and-risk-scoring/spec.md`
- `specs/002-data-and-risk-scoring/protocol.md`
- `specs/002-data-and-risk-scoring/plan.md`
- `specs/002-data-and-risk-scoring/tasks.md`

Also inspect:

- Repository constitution and contributor instructions
- `next_work.md`
- Existing API and schema contracts
- `backend/src/fraudlens/`
- `backend/tests/`
- `frontend/src/`
- `frontend/tests/`
- `contracts/`
- `evidence/tasks/`
- Existing security tests and CI configuration

Reconcile outdated planning statements against current execution evidence.

The task list indicates that Feature 002 has completed local model integration, EDA integration and regression testing. T252 and T254–T255 remain incomplete or gated.

Do not reopen completed ML experiments merely because older protocol paragraphs describe historical pending work.

### Critical project constraints

FraudLens is a local, educational, single-user synthetic AML application.

It does not currently claim secure multi-user hosting or production deployment readiness.

The model predicts the IBM synthetic `Is Laundering` target, not verified financial fraud or actual criminal activity.

The application uses a FastAPI backend, a TypeScript frontend, and an optional local LightGBM scorer.

Preserve the currently accepted unweighted LightGBM:

- Model SHA-256: `3b4e4019312d60610dd0094c6697897a061611a60e7777ed7be35e133af9451c`
- Frozen validation threshold: `0.2489517623052024`
- Feature version: `hi-small-temporal-v1`

The native model, manifest, feature contracts, validation threshold, research partitions, protocol hashes, and sealed predictions must remain unchanged.

T230 has already completed one separately authorized test evaluation. This audit does not authorize repeating that evaluation, opening restricted test labels, or recalculating model performance.

Only use synthetic data and controlled test doubles unless a separately documented read-only verification of an existing trusted artifact is necessary and permitted.

---

## PHASE 2 — Architecture and threat-model assessment

Inspect the actual application before assuming any endpoints or services exist.

Map these trust boundaries:

1. Browser and TypeScript frontend
2. FastAPI HTTP endpoints
3. Pydantic validation and response contracts
4. Case and transaction lookup
5. Scorer abstraction
6. Local LightGBM artifact loading
7. Model inference and response generation
8. Authorized aggregate metrics
9. Label-free EDA
10. Configuration, local files, logs and runtime environment

For every boundary, identify:

- Untrusted inputs
- Sensitive data
- Validation mechanisms
- Authorization or local-workflow controls
- Error handling
- Resource limits
- Possible data exposure
- Expected failure behavior

Inventory all actual endpoints and record their accepted HTTP methods, input schemas, response schemas and error responses.

Pay particular attention to existing routes such as:

- `GET /api/health`
- `GET /api/cases`
- `GET /api/transactions/{transaction_id}/risk`
- `GET /api/model/results`
- `GET /api/eda/summary`

Verify actual route definitions before testing.

Do not invent a transaction-submission endpoint if the existing MVP only supports read-only transaction lookup.

---

## PHASE 3 — Security and edge-case test suites

Design and execute the following test groups using synthetic fixtures, mocks, and local test clients.

### SEC-001 — API boundary and exposure

Test:

- Valid and invalid HTTP methods
- Missing and malformed route parameters
- Unsupported query parameters
- Very long transaction identifiers
- Unicode and special-character identifiers
- Malformed request bodies, where applicable
- Unexpected content types
- Unexpected exceptions
- Request and response schema validation
- Accidental exposure of internal exception details

Review localhost binding configuration, network exposure, CORS, security headers and debug settings.

Verify that invalid inputs produce controlled responses.

Do not launch uncontrolled scans against any deployed instance.

### SEC-002 — Authorization and data isolation

Inspect how the application restricts access to cases, transaction results, model results and restricted ML evidence.

Test:

- Unauthenticated access to existing endpoints
- Attempts to access nonexistent or restricted resources
- Attempts to request restricted partition information
- Arbitrary test/showcase label queries
- Record-level target-label exposure
- Query-parameter attempts to expand permitted data
- Accidental exposure through error responses
- Attempts to bypass backend rules through direct API calls

Inspect the historical `GET /api/cases` finding.

Determine whether it represents:

A. Expected local single-user behavior

B. Unsafe exposure under the current runtime configuration

C. A vulnerability requiring additional deployment assumptions

Do not add accounts, roles, authentication providers, or multi-user infrastructure automatically.

Instead report the actual risk and the decision needed to change scope.

### SEC-003 — Transaction input and numeric validation

Review both canonical data validation and the actual scoring boundary.

Use synthetic input cases covering:

- Negative amounts
- Zero amounts
- Extremely large amounts
- Excessive fractional precision
- Empty and missing amount values
- Non-numeric strings
- `NaN`
- Positive and negative infinity
- Numeric overflow
- Invalid currencies
- Blank bank/account identifiers
- Leading-zero account identifiers
- Reserved category collisions
- Missing timestamps
- Invalid timestamps
- Timezone-equivalent timestamps

Apply the existing frozen amount, timestamp, identity and category policies.

Do not introduce arbitrary new validation rules.

For malformed inputs, verify that the system rejects data or returns a controlled error according to its contract.

A failure must never silently become a zero-risk assessment.

### SEC-004 — Model artifact integrity

Audit the existing artifact loader and local model activation process.

Test with temporary synthetic files and controlled mocks:

- Missing model file
- Missing artifact manifest
- Corrupted artifact bytes
- SHA-256 mismatch
- Wrong feature version
- Wrong feature order
- Unsupported artifact format
- Incompatible runtime/library metadata
- Invalid model metadata
- Invalid threshold metadata
- Malformed native LightGBM representation
- Unexpected file paths
- Unsafe path configuration
- Symbolic-link or path-substitution concerns, where applicable
- Attempted fallback to untrusted serialization formats

Verify that compatibility and trust checks occur before native model parsing.

The application must not download models, load untrusted pickle/joblib objects, or train models during startup.

Use temporary fixture artifacts only.

Do not alter or corrupt the frozen real model.

### SEC-005 — Feature vector consistency

The frozen `hi-small-temporal-v1` input contains exactly eleven ordered logical features.

Verify:

1. `sender_out_count_24h`
2. `sender_distinct_receivers_24h`
3. `sender_paid_count_same_currency_24h`
4. `sender_paid_sum_same_currency_24h`
5. `receiver_in_count_24h`
6. `receiver_distinct_senders_24h`
7. `receiver_received_count_same_currency_24h`
8. `receiver_received_sum_same_currency_24h`
9. `current_amount_paid_log1p`
10. `current_payment_currency`
11. `current_payment_format`

Test:

- Missing required features
- Reordered features
- Incorrect feature types
- Extra feature fields
- Negative historical counts
- Nonfinite numeric features
- Corrupted numeric values
- Feature-version mismatch
- Category mapping mismatch
- Unknown but valid payment categories
- Reserved `__UNKNOWN__` token collision
- Preprocessing output incompatible with the accepted model

Verify the required mapping from eleven logical inputs to the frozen trained model representation.

Do not assume the model uses eleven final encoded columns; consult the trusted artifact manifest and actual adapter.

Unknown categories must follow the frozen train-only vocabulary policy. Missing or invalid categories must not silently map to valid values.

### SEC-006 — ML output integrity

Mock scorer outputs containing:

- Valid finite bounded risk scores
- Negative scores
- Scores greater than 1
- `NaN` and infinity
- Missing model/version metadata
- Wrong transaction ID
- Incompatible feature version
- Malformed explanation payload
- Missing eligibility state
- Unexpected scorer exceptions

Verify that the public response requires the correct transaction identity and valid risk score.

Test that an invalid or failed assessment does not become:

- A zero-risk prediction
- An invented probability
- A successful model result
- An apparently valid analyst decision

Preserve the distinction between fixture, rules and model sources.

### SEC-007 — Resource exhaustion and resilience

Using safe, bounded local tests, inspect:

- Large identifiers
- Large supported request bodies
- Oversized query parameters
- Very large in-memory test batches
- Concurrent read requests
- Duplicate requests
- Repeated scoring requests
- Slow scorer responses
- Scorer exceptions
- Missing model artifacts
- Unavailable EDA summaries
- Corrupt aggregate outputs
- File-read failures
- Partial fixture/model startup failures

Use a controlled test client and small concurrency limits.

Do not perform load floods, prolonged stress tests, resource-starvation attacks or live denial-of-service testing.

Measure response behavior and, where practical, bounded memory/time characteristics.

If the current architecture uses an in-process scorer, simulate scorer unavailability rather than assuming a remote Python service.

Verify that failures do not create unsafe fallback predictions.

### SEC-008 — Data privacy and restricted-label leakage

Inspect API responses, frontend decoding, server logging, exception handlers, EDA output and result-reporting code.

Verify:

- No public record-level `Is Laundering` labels
- No unauthorized test/showcase label access
- No restricted label files exposed through static serving
- No raw source CSV served to the browser
- No sensitive transaction fields unnecessarily logged
- No private local filesystem paths exposed
- No credentials or secrets in error responses
- No model or dataset artifacts accidentally tracked in Git
- No accidental publication of evaluation outputs
- No label-derived leakage in EDA responses

Verify the existing aggregate-results authorization controls using synthetic fixtures.

Do not inspect restricted real labels to demonstrate that access restrictions work.

### SEC-009 — Frontend security and failure handling

Review TypeScript source, runtime decoders, API calls, view rendering and tests.

Test:

- Malicious-looking text values handled as inert text
- HTML/script strings in transaction descriptions
- Invalid server JSON
- Unexpected additional response fields
- Missing required fields
- Incorrect field types
- Negative and nonfinite scores
- Empty arrays
- Loading and retry states
- API unavailable states
- Model unavailable states
- Malformed EDA chart values
- Large returned strings
- Unexpected Unicode

Check for unsafe DOM insertion, `innerHTML`, unvalidated external JSON, token storage issues if applicable, and overly permissive CORS assumptions.

Verify safe rendering without executing injected HTML or JavaScript.

### SEC-010 — ML governance and evaluation security

This is a critical project-specific test suite.

Verify through inspection, mocks and synthetic tests that:

- Inference cannot trigger training.
- Runtime APIs cannot request model fitting.
- The scorer does not require real labels.
- Restricted test/showcase labels cannot reach runtime responses.
- Warm-up records remain ineligible for scoring.
- Historical features use strictly earlier events.
- Equal-timestamp transactions do not influence one another.
- Currency-specific sums cannot mix currencies.
- Train-only vocabularies remain frozen.
- Frozen development/test partitions cannot be altered through API requests.
- The selected threshold cannot be changed through public input.
- Test metrics cannot be recomputed or exposed outside existing authorization rules.
- Showcase replay remains gated and cannot run implicitly.
- Missing model artifacts preserve the documented fixture behavior.

Use synthetic fixtures to verify temporal invariants.

Do not regenerate historical real-source features, access restricted labels, train models, tune thresholds or run showcase replay.

---

## PHASE 4 — Execute available security tools

Inspect existing tooling before running commands.

Use compatible, already available tools where appropriate:

**Python/backend**

- pytest
- Ruff
- Existing type checks
- Bandit, if installed
- pip-audit, if installed
- Semgrep, if installed

**TypeScript/frontend**

- Vitest
- TypeScript typecheck
- Existing Vite build checks
- npm dependency audit when permitted and available
- Existing static-analysis rules

**Repository**

- Git-tracked secret checks
- Gitleaks, if installed
- CI workflow inspection
- Dependency lockfile verification
- Ignore-rule review

Do not install dependencies, update lockfiles, or run network-dependent tooling without approval.

Document which tools were executed, skipped, unavailable, or blocked.

Do not claim a security scan passed unless it actually executed successfully.

---

## PHASE 5 — Implement automated security tests

After reviewing the project and existing test coverage, add missing tests where they provide new coverage.

Follow existing pytest and Vitest conventions.

Reuse established fixtures and test helpers.

Use synthetic data only.

Do not duplicate tests that already cover the same behavior.

Organize new tests logically under existing directories, for example:

- `backend/tests/security/`
- `backend/tests/integration/`
- `backend/tests/unit/`
- `frontend/tests/`

Choose the actual locations after inspecting repository conventions.

Requirements:

1. All tests must be deterministic.
2. Tests must not require real datasets or model artifacts.
3. Tests must not mutate frozen research files.
4. Tests must not perform external network calls.
5. Tests must not require production credentials.
6. Tests must clean up temporary files.
7. Tests must have bounded execution time.
8. Tests must clearly distinguish expected rejection from unexpected failure.
9. Tests must report actual results.
10. Existing behavior must not be silently redefined.

Execute the new tests and relevant existing regression suites.

If a test discovers a genuine vulnerability, preserve the failing test and record the observed behavior.

Do not weaken assertions or rewrite the test simply to make it pass.

Do not change application implementation to fix the finding yet.

---

## PHASE 6 — Produce the security audit report

Create:

`evidence/security/feature-006-security-audit.md`

For each finding, record:

- Finding ID
- Severity: Critical, High, Medium, Low or Informational
- Finding type
- Affected component
- File and line reference
- Relevant spec/protocol requirement
- Evidence
- Reproduction test
- Expected behavior
- Actual behavior
- Security or reliability impact
- Confidence
- Recommended remediation
- Whether a production fix requires a team scope decision

Distinguish:

- Confirmed vulnerabilities
- Confirmed reliability defects
- Unverified security concerns
- Missing security controls
- Out-of-scope production-hardening recommendations
- Intended behavior under the local single-user MVP

Do not inflate severity based on hypothetical public deployment when the current application only claims a local workflow.

Report deployment exposure risks separately.

---

## PHASE 7 — Test coverage and remediation plan

Create:

`evidence/security/feature-006-security-test-coverage.md`

Include a matrix with:

| Test ID | Component | Scenario | Expected behavior | Actual result | Status |
|---|---|---|---|---|---|

Use:

- PASS
- FAIL
- SKIPPED
- BLOCKED
- NOT IMPLEMENTED

Do not equate a skipped test with a pass.

Create:

`evidence/security/feature-006-remediation-plan.md`

Group findings into:

**P0 — Critical:** Immediate security or integrity risks.

**P1 — High:** Serious security and data-exposure risks.

**P2 — Medium:** Validation, resilience and defense-in-depth improvements.

**P3 — Low:** Hardening and maintainability improvements.

For each proposed fix, include:

- Exact affected files
- Proposed change
- Expected result
- Regression tests
- Compatibility risks
- Whether a specification update is required
- Whether explicit team approval is required

Do not implement the remediation plan yet.

---

## PHASE 8 — Final verification and handoff

Before finishing:

1. Run relevant existing backend regression tests.
2. Run relevant frontend tests, typecheck and build.
3. Run newly added security tests.
4. Inspect all changed files.
5. Check that no tracked datasets, generated model artifacts or secrets were added.
6. Verify that frozen source, model, protocol and prediction artifacts were not modified.
7. Verify the branch remains separate from the integration branch.
8. Record the final Git diff and working-tree status.
9. Record every failed, skipped or blocked verification honestly.

Do not commit, push or merge unless explicitly authorized.

### Required final response

Provide:

**1. Branch summary**

Branch name, base branch and verified base commit.

**2. Executive security summary**

Overall risk assessment and important qualifications about local-only versus deployed operation.

**3. Findings table**

ID, severity, component, issue, evidence and recommended fix.

**4. Test execution results**

Total executed, passed, failed, skipped and blocked.

**5. Existing test regression results**

Exact commands and actual outcomes.

**6. ML integrity verification**

Whether frozen model invariants and restricted-label boundaries were preserved.

**7. Prior Feature 005 comparison**

Which older findings are still relevant, resolved, or superseded.

**8. Prioritized remediation plan**

Suggested sequence for fixing issues without breaking Feature 002 functionality.

**9. Outstanding scope decisions**

Especially authentication, public deployment, additional security infrastructure or any other changes beyond the approved local MVP.

### FINAL RULE

The purpose is to identify and reproduce vulnerabilities safely, establish regression coverage, and document evidence.

**Do not start implementing production security fixes until I review the findings and explicitly authorize the next phase.**