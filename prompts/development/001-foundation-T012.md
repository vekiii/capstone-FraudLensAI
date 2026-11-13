# Original T012 instruction — 2026-11-12

Branch: initialization. Scope: T012 only; no production implementation.
The following is the original user instruction, preserved before test implementation.
No redactions.

```text
eveyrhitng you commit in this ession commit as isidora popovic and write in evidece file
You are working on FraudLens, Phase 4, User Story 2 (US2).

TASK: T012 — Write and run RED backend API and fixture-scorer tests.

First inspect:
- specs/001-project-foundation/
- contracts/api.md
- contracts/schemas.json
- data-model.md
- Existing backend source and test conventions
- Relevant FR-003, FR-004, FR-005, and FR-006 requirements

Use the actual repository paths if specifications are nested differently.

Implement tests in:
- backend/tests/integration/test_cases.py
- backend/tests/unit/test_fixture_scoring.py

Required test coverage:

1. GET /api/cases returns exactly three synthetic cases in deterministic order.
2. Case list and detail endpoints agree on identity and shared fields.
3. GET /api/cases/CASE-999 returns HTTP 404.
4. Malformed case IDs return HTTP 422.
5. An empty collection produces the contract-defined empty response.
6. Invalid scorer output produces HTTP 500.
7. A scorer result referencing the wrong transaction is rejected.
8. Public response payloads are closed to unexpected properties.
9. No ground-truth fraud labels or ML evaluation claims appear in responses.
10. Error responses use the generic envelope specified by api.md.
11. Error responses never expose stack traces, filesystem paths, or internal exception messages.
12. Fixture scoring satisfies deterministic behavior and required metadata.

Important:
- Follow existing pytest conventions and available fixtures.
- Use mocks and dependency injection where appropriate.
- Test actual JSON structures and status codes, not implementation details.
- Do not modify production code to make these tests pass.
- Do not weaken assertions.
- Ensure failures are caused by missing behavior rather than broken test setup.

Run the relevant backend test commands.

Expected result: RED, with meaningful failing assertions for functionality not yet implemented.

At completion, report:
- Files created or changed
- Tests added
- Exact test commands
- Number passed and failed
- Reasons for the failures
- Any contract ambiguities

Do not implement T014, T015, or T016.
```
