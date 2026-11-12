# Original T013 instruction — 2026-11-12

Branch: initialization. Scope: T013 only; no T017/T018 implementation.
Instruction preserved before test implementation; no redactions.
Session commit-attribution instruction remains Isidora Popovic (see T012 evidence).

```text
You are working on FraudLens, Phase 4, User Story 2 (US2).

TASK: T013 — Write and run RED frontend fetch and DOM tests.

Before editing, inspect:
- specs/001-project-foundation/
- contracts/api.md
- contracts/schemas.json
- data-model.md
- Existing frontend package.json and test framework
- Existing frontend architecture and test patterns
- FR-003, FR-004, and FR-005

Create or extend:
- frontend/tests/api.test.ts
- frontend/tests/views.test.ts

API test requirements:

1. Decode valid case list responses.
2. Decode valid case detail responses.
3. Reject malformed or contract-invalid payloads.
4. Reject unexpected additional properties when prohibited by schemas.json.
5. Handle HTTP 404, 422, and 500 using controlled errors.
6. Enforce a five-second request timeout.
7. Support request cancellation.
8. Distinguish timeout, cancellation, network failure, and invalid server responses.
9. Never silently substitute fallback scores or fabricated case data.

DOM test requirements:

1. Display a loading state during requests.
2. Display three synthetic cases when available.
3. Display an empty state for an empty list.
4. Display a controlled error state when requests fail.
5. Display a not-found state for unknown cases.
6. Provide working retry behavior.
7. Allow selecting each of the three cases.
8. Support returning from detail to list.
9. Display an obvious synthetic/illustrative data notice.
10. Clear old detail content when selection changes.
11. Ignore responses arriving late from previously selected cases.
12. Never display stale case details under a newly selected case.

Use the repository's existing frontend test framework and DOM environment.

Use mocked fetch responses and controlled asynchronous promises to simulate races, timeouts, and failures.

Do not implement production frontend features yet.

Run the relevant frontend tests and verify that missing functionality produces meaningful RED failures.

Report:
- Files changed
- Test cases added
- Exact commands executed
- Pass/fail counts
- Remaining implementation requirements

Do not implement T017 or T018.
```
