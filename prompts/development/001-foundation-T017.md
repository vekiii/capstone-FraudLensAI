# Original development request — T017

Recorded before implementation on 2026-11-12. Scope: Phase 4, US2.

```text
You are working on FraudLens, Phase 4, User Story 2 (US2).

TASK: T017 — Implement the frontend API boundary and runtime contract validation.

Inspect:
- contracts/api.md
- contracts/schemas.json
- data-model.md
- Existing frontend architecture and dependencies
- frontend/tests/api.test.ts
- Existing TypeScript configuration
- FR-005 and FR-006

Implement:
- frontend/src/contracts.ts
- frontend/src/api.ts

contracts.ts requirements:

1. Define TypeScript types matching the canonical JSON schemas.
2. Implement runtime decoding and validation of external JSON.
3. Validate required fields and field types.
4. Enforce allowed values and numeric constraints.
5. Reject unknown fields where schemas declare closed objects.
6. Validate nested case, transaction, risk assessment, and error objects.
7. Distinguish valid empty collections from invalid responses.
8. Avoid unchecked type assertions as a substitute for validation.
9. Never treat untrusted JSON as valid merely because TypeScript compilation succeeds.

Use existing validation libraries if available. Do not add dependencies unnecessarily.

api.ts requirements:

1. Implement typed API functions for listing cases and retrieving case details.
2. Decode every successful response through contracts.ts.
3. Implement a five-second timeout.
4. Support AbortSignal cancellation.
5. Clean up timeout resources after requests settle.
6. Handle network failures.
7. Handle HTTP 404, 422, and 500.
8. Decode server error envelopes.
9. Reject invalid JSON or contract-invalid responses.
10. Expose controlled, typed errors to the view layer.
11. Distinguish cancellation from real failures.
12. Never fabricate fallback cases, scores, or explanations.

Make the code testable with mocked fetch and deterministic timing.

Run frontend/tests/api.test.ts and relevant TypeScript checks.

Expected result:
All T017-related API tests GREEN.

Do not implement list/detail UI rendering in this task.

Report:
- Public API functions and types
- Runtime validation approach
- Timeout and cancellation behavior
- Files changed
- Commands executed
- Test results and remaining issues
```

Persistent session instruction: any eventual session commits must use Isidora
Popovic as author and be recorded in evidence. No automatic commit/push is requested.
