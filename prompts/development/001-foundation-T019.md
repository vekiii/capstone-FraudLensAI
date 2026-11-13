# Original development request — T019

Recorded before T019 execution on 2026-11-12. T018 was completed first.

```text
You are working on FraudLens, Phase 4, User Story 2 (US2).

TASK: T019 — Execute integrated regression, manually verify the complete journey, and create evidence.

Read:
- specs/001-project-foundation/quickstart.md
- contracts/api.md
- contracts/schemas.json
- Relevant SC-002 and SC-003 requirements
- Tests and implementations from T012 through T018
- Existing evidence/task documentation conventions

Do not assume functionality is correct merely because unit tests pass.

PART 1 — Backend verification

Run the documented backend setup and test commands.

Verify:
- Three deterministic synthetic cases
- List/detail consistency
- Unknown case returns 404
- Malformed ID returns 422
- Invalid scorer output is rejected
- Transaction identity mismatch is rejected
- Generic error envelopes
- No internal information leakage
- No ground-truth labels or ML evaluation claims

PART 2 — Frontend verification

Run:
- Frontend tests
- TypeScript checks
- Existing build command
- Applicable lint checks

Verify loading, empty, error, not-found, retry, and cancellation behavior.

PART 3 — Integrated application

Follow quickstart.md exactly where applicable.

Start the real backend and frontend.

Verify the frontend communicates correctly with the backend and that real responses conform to contracts.

PART 4 — Browser journey

If browser automation or an interactive browser is available, perform:

1. Open the application.
2. Verify exactly three cases are listed.
3. Open case 1.
4. Verify case 1 details and assessment.
5. Return to the list.
6. Open case 2.
7. Verify case 2 details.
8. Return and open case 3.
9. Verify case 3 details.
10. Verify synthetic/illustrative notice.
11. Test an unknown case.
12. Test malformed case ID behavior.
13. Test unavailable backend and retry.
14. Test empty-list behavior.
15. Test rapid case switching and stale response prevention.
16. Check browser console errors.

Use available tools and test fixtures to simulate exceptional scenarios.

Do not claim manual browser testing was performed unless it actually was.

PART 5 — Evidence

Create:
evidence/tasks/T019.md

Include:
- Date and environment
- Git commit/revision if available
- Commands executed
- Actual exit codes
- Test suites and pass/fail counts
- Build/type-check results
- API verification results
- Browser journey results
- Manual scenarios actually executed
- Scenarios not executed and why
- Known defects
- Requirement coverage for SC-002 and SC-003
- Final PASS/FAIL/PARTIAL assessment

Important:
Fixture scores are synthetic demonstrations, NOT machine-learning evaluation results.

Do not claim precision, recall, accuracy, AUC, or predictive performance based on fixture scores.

Do not fabricate test results, screenshots, browser interactions, or evidence.

Fix only minor issues directly related to T019 validation. Record larger defects rather than making unrelated architectural changes.

At completion, provide:
1. Overall verification status
2. Tests passed/failed
3. Browser scenarios completed
4. Known defects and untested scenarios
5. Evidence file location
6. Whether US2 acceptance criteria are satisfied
```

Persistent session instruction: eventual commits must use Isidora Popovic as
author and be recorded in evidence. Git commit/push remains nonautomatic.
