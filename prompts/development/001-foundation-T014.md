# Original T014 instruction — 2026-11-12

Branch: initialization. Scope: T014 fixture data/loading/validation only.
Instruction preserved before implementation, with no redactions.
Session commit attribution remains Isidora Popovic (see T012 evidence).

```text
You are working on FraudLens, Phase 4, User Story 2 (US2).

TASK: T014 — Create synthetic fixture data and implement fixture validation.

First read:
- specs/001-project-foundation/data-model.md
- contracts/schemas.json
- contracts/api.md
- Relevant FR-003 and FR-004 requirements
- Existing backend project structure

Implement changes in:
- data/fixtures/cases.json
- backend/src/fraudlens/cases.py

Requirements:

1. Create exactly three clearly synthetic cases.
2. Follow the canonical structures in data-model.md and schemas.json.
3. Every case must have a unique case ID.
4. Every transaction must have a unique transaction ID.
5. Use stable, deterministic identifiers and ordering.
6. Provide realistic but entirely fictional transaction attributes.
7. Do not include real PII, real financial account details, or identifiable customer information.
8. Do not include ground-truth labels such as is_fraud, fraud_label, or confirmed_fraud.
9. Do not embed ML predictions, model accuracy, training claims, or evaluation metrics.
10. Keep transaction inputs separate from scoring outputs.

In cases.py:

- Implement fixture loading using repository conventions.
- Validate fixture structure against the established data model.
- Reject duplicate case IDs.
- Reject duplicate transaction IDs.
- Reject malformed or missing required attributes.
- Preserve deterministic case ordering.
- Ensure repeated reads produce consistent results.
- Reject unexpected fields where the contract requires closed objects.
- Avoid exposing raw internal exceptions to API callers.

Do not create new field names without checking the specifications.

Add or update focused validation tests if necessary.

Run applicable tests and perform direct fixture validation.

Report:
- Fixture structure
- Three case IDs
- Transaction counts
- Validation behavior
- Files changed
- Tests executed and actual outcomes

Do not implement API routes or the scoring engine in this task.
```
