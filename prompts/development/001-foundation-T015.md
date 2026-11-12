# Original T015 instruction — 2026-11-12

Branch: initialization. Scope: T015 scorer/protocol and case validation, no endpoints.
Instruction preserved before implementation, with no redactions.
Session commit attribution remains Isidora Popovic (see T012 evidence).

```text
You are working on FraudLens, Phase 4, User Story 2 (US2).

TASK: T015 — Implement the fixture scorer and scoring protocol.

Inspect first:
- specs/001-project-foundation/
- contracts/schemas.json
- data-model.md
- T006 constraints and existing validation code
- backend/src/fraudlens/cases.py
- backend/tests/unit/test_fixture_scoring.py
- FR-004, FR-006, and FR-007

Primary implementation file:
backend/src/fraudlens/scoring.py

Also update:
backend/src/fraudlens/cases.py

Implement the required protocol:

score(transaction: Transaction) -> RiskAssessment

Requirements:

1. Define the scoring interface using the existing project's Python typing and validation conventions.
2. Implement a deterministic fixture scorer.
3. The same transaction must produce the same risk score and assessment fields across repeated calls.
4. scored_at must also be deterministic according to the applicable contract, not uncontrolled current wall-clock time.
5. Set source = "fixture".
6. Set scorer_version = "fixture-v1".
7. Ensure explanations explicitly identify results as illustrative or synthetic.
8. Follow the required score range, types, risk categories, and metadata constraints from the specifications.
9. Enforce all relevant T006 validation constraints.
10. Reject invalid inputs and invalid scorer outputs.
11. Reject transaction identity mismatches in cases.py.
12. Do not generate or imply verified fraud labels.

Design principles:

- Keep the scorer replaceable through a clear protocol.
- Separate transaction inputs from risk assessment outputs.
- Avoid unnecessary dependencies.
- Avoid randomness and nondeterministic timestamps.
- Do not train or integrate a machine-learning model.
- Do not claim that fixture scores represent predictive accuracy.
- Do not silently recover from invalid scoring results.

Use deterministic, documented scoring rules that are suitable for a demo and consistent with the existing contract.

Run:
- Unit tests from T012
- Relevant fixture validation tests
- Existing backend regression tests

Report:
- Scorer architecture
- Deterministic scoring rules
- Identity validation behavior
- Files changed
- Exact test commands and outcomes
- Remaining failures related to later tasks

Do not implement the API endpoints in this task.
```
