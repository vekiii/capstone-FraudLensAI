# Fixture scoring v1

Date: 2026-11-12. Scope: T015, FR-004/006/007.
Authority: specs/001-project-foundation/data-model.md and contracts/schemas.json.

## Interface and ownership

`fraudlens.scoring.Scorer` is a structural Python Protocol:
`score(transaction: Transaction) -> RiskAssessment`. It is synchronous and does
not require inheritance from a concrete scorer. FixtureScorer implements it with
no model, network access, randomness, training or new dependency.

Transaction inputs stay in data/fixtures/cases.json without any assessment fields.
`fraudlens.cases.score_case(case, scorer)` accepts an explicit scorer and produces
a validated CaseDetail for later HTTP delivery. T016 will add endpoints and map
FixtureLoadError/CaseScoringError to the documented HTTP error envelope.

## Deterministic demo rule

The transaction ID selects one of three illustrative constants:

```text
index = (numeric transaction-ID suffix - 1) % 3
score = (0.75, 0.40, 0.10)[index]
```

| Transaction | Score |
|---|---|
| TX-001 | 0.75 |
| TX-002 | 0.40 |
| TX-003 | 0.10 |
| TX-004 | 0.75 |

The same rule applies to every valid TX-000 through TX-999 identifier. This is a
display-fixture convention with no AML meaning, predictive accuracy or probability
interpretation. Amount/account attributes are not used to suggest a trained model
or calibrated risk. No default/fallback result is returned for invalid input.

Every result has source=fixture and scorer_version=fixture-v1. scored_at copies
the validated transaction's occurred_at, explicitly as a fixture timestamp, not a
claim about actual execution time. The explanation states illustrative/synthetic
provenance, no ML inference or verified fraud finding, and the timestamp convention.
The same transaction therefore produces identical complete output on every call,
independent of clock, instance, request order or process-local state.

The canonical schema defines finite numeric scores in [0,1] and source values
fixture/rules/model; it does not define a risk-category field or band thresholds.
No additional categories, labels or payload fields are introduced.

## Validation and identity

Input and output validation reuse the strict T006 Transaction/RiskAssessment
models. Existing instances are revalidated from their stored field dictionaries:
Pydantic otherwise trusts instances by default, and model_dump can hide extra
keys inserted by an unchecked model_copy. Extra model fields are rejected too.

score_case validates a fresh case/transaction snapshot before invoking the scorer.
It passes a separate copy, rejects input mutation, revalidates the assessment and
requires the result's transaction_id to match the original validated transaction.
An adapter cannot bypass the identity check by mutating its input ID. Returned
details do not share mutable records with the caller or adapter.

Invalid results, unknown sources, nonfinite/out-of-range scores, mismatches and
adapter exceptions raise generic controlled failures with suppressed chaining.
There is no clamping, fabricated zero score, alternate scorer or silent recovery.
No HTTP normalization or frontend behavior is claimed by this Python boundary.

Execution evidence: [T015.md](../../evidence/tasks/T015.md).
