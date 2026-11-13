# Original development request — T018

Recorded before implementation on 2026-11-12. Latest repeated T018 instruction:

```text
You are working on FraudLens, Phase 4, User Story 2 (US2).

TASK: T018 — Implement the complete synthetic case inspection UI and make T013 tests GREEN.

First inspect:

- specs/001-project-foundation/
- contracts/api.md
- contracts/schemas.json
- Existing frontend application architecture
- frontend/src/contracts.ts
- frontend/src/api.ts
- frontend/tests/views.test.ts
- FR-003, FR-004, and FR-005

Implement:

- frontend/src/main.ts
- frontend/src/views.ts
- frontend/src/styles.css

Primary user journey:

1. User opens FraudLens.
2. Application loads the synthetic case list.
3. Three fixture cases are displayed in deterministic order.
4. User selects a case.
5. Application displays case details and illustrative risk assessment.
6. User returns to the case list.
7. User selects another case.
8. Old details are cleared immediately.
9. The new case details are displayed correctly.

UI states:

- Initial loading
- Case list
- Empty list
- Case detail loading
- Case detail
- Recoverable API error
- Case not found
- Retry action

Requirements:

1. Display a prominent notice that data and scores are synthetic and illustrative.
2. Never present fixture scores as production ML predictions.
3. Make case selections visually distinguishable.
4. Implement reliable back navigation.
5. Clear stale case details when selection changes.
6. Cancel obsolete requests when possible.
7. Ignore late responses from previous selections even if cancellation fails.
8. Ensure delayed failures cannot overwrite newer successful results.
9. Implement retry for recoverable failures.
10. Avoid displaying raw server errors or stack traces.
11. Use safe DOM text rendering, not unsafe HTML interpolation.
12. Keep the interface usable with keyboard navigation.
13. Include accessible status and error messages.
14. Use responsive CSS for desktop and mobile screens.
15. Keep styling consistent with the existing frontend design.

Implementation guidance:

- Reuse the typed API boundary from T017.
- Use a simple explicit UI state model.
- Use request identity or generation tokens to prevent stale responses.
- Avoid unnecessary framework dependencies.
- Do not change backend contracts.
- Do not introduce fake fallback assessments.

Run:

- frontend/tests/views.test.ts
- frontend/tests/api.test.ts
- TypeScript checks
- Applicable frontend regression tests

Make the T013 tests GREEN without weakening assertions.

Report:

- UI architecture
- Implemented screens and states
- Race-condition prevention approach
- Files changed
- Exact test results
- Remaining issues
```

The user also requested T019 integrated/browser verification during this task.
Finish T018 first, then execute that compatible verification request separately.
Persistent instruction: eventual session commits must use Isidora Popovic as
author and be recorded in evidence. No automatic commit/push.
