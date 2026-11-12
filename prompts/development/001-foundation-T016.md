# Original T016 instruction — 2026-11-12

Branch: initialization. Scope: T016 backend case endpoints and error normalization.
Instruction preserved before implementation, with no redactions.
Session commit attribution remains Isidora Popovic (see T012 evidence).

```text
You are working on FraudLens, Phase 4, User Story 2 (US2).

TASK: T016 — Implement backend case API endpoints and make T012 tests GREEN.

First inspect:
- contracts/api.md
- contracts/schemas.json
- data-model.md
- Existing backend application architecture
- backend/src/fraudlens/main.py
- backend/src/fraudlens/cases.py
- backend/src/fraudlens/scoring.py
- backend/tests/integration/test_cases.py
- FR-003, FR-005, and FR-006

Implement:

GET /api/cases
GET /api/cases/{case_id}

Use the case service in cases.py rather than implementing data access directly inside route handlers.

GET /api/cases must:
- Return the fixture collection in deterministic order.
- Match the API response schema exactly.
- Return the contract-defined empty response for an empty collection.
- Avoid leaking internal fixture structures or prohibited fields.

GET /api/cases/{case_id} must:
- Validate case_id according to the contract.
- Return the correct case and risk assessment.
- Return HTTP 404 for an unknown valid ID such as CASE-999.
- Return HTTP 422 for malformed IDs.
- Reject invalid or mismatched scorer output.
- Preserve list/detail consistency.

Error handling:

1. Normalize 404, 422, and 500 responses to the generic error envelope in contracts/api.md.
2. Never expose Python tracebacks or filesystem paths.
3. Never expose sensitive internal exception details.
4. Handle invalid scorer output as an internal error.
5. Ensure framework-generated validation errors conform to the public API contract.
6. Use appropriate server-side logging without exposing internal details publicly.

Important:
- Do not invent response fields.
- Follow schema definitions exactly.
- Avoid broad exception handlers that conceal programming errors or bypass validation.
- Preserve existing endpoints and application behavior.
- Do not change tests merely to force a passing result.

Run T012 backend tests until GREEN, then run the full applicable backend regression suite.

Report:
- Routes implemented
- Actual response examples for success and errors
- Files modified
- Exact test commands
- Pass/fail results
- Any remaining contract deviations
```
