# Foundation Data Model

The normative field shapes are in contracts/schemas.json. All objects are closed:
`additionalProperties: false`. These are design contracts, not implemented runtime validators.

## Transaction
`transaction_id`: `TX-` followed by three digits. `occurred_at`: RFC3339 UTC timestamp.
`sender_account` and `receiver_account`: nonempty bank-qualified opaque strings (max 120 chars).
`amount`: nonnegative decimal string with exactly two fractional digits; never binary float.
`currency`: three uppercase letters; fixtures use EUR. This is a foundation demo constraint,
not a claim that all IBM currencies map to this representation; later importer must review it.

## RiskAssessment
`transaction_id`: same constraint as Transaction and MUST match the associated transaction.
`score`: finite numeric value in [0, 1], not a probability claim.
`source`: fixture, rules or model. Foundation produces fixture only; test substitution may use rules.
`scorer_version`: nonempty string (max 80 chars).
`scored_at`: RFC3339 UTC timestamp. `explanation`: nonempty string (max 500 chars).
No fabricated SHAP/model explanation; fixture explanation says illustrative score.

## CaseSummary / CaseDetail
`case_id`: `CASE-` followed by three digits, unique in the fixture repository.
Summary: case_id, transaction_id, score and score_source. Detail: case_id, transaction,
risk_assessment. Summary values MUST agree with corresponding detail. Case delivery scores
through the injected scorer; changing scorer must not require changing the case service.
Stable fixture scored_at values make requests reproducible. No state transitions or writes here.

## Fixture collection
Implementation will create exactly three cases. Store only transactions and case references;
the scorer owns illustrative scores. Validate unique case and transaction identifiers on load.
Ordering is ascending case_id for deterministic display. An empty repository returns an empty
list. Never store an isFraud/Is Laundering/reference decision in these public demo records.

## Scorer boundary
`score(transaction: Transaction) -> RiskAssessment`. Synchronous and deterministic in foundation.
Validation at delivery rejects wrong transaction IDs, unknown sources and nonfinite/out-of-range
scores. A future scorer can replace it without altering HTTP/UI contracts; model quality is later work.

## ExecutionEvidence (documentation, not runtime storage)
Task + requirement IDs; original prompt link; commit/diff reference; tool/data versions;
RED command, observed failure and explanation; GREEN command and result; regression; limitations;
review state (not_requested/pending/reviewed) and actual reviewer when available.
Unknown outcomes remain 'not run'. Sanitized logs only; never credentials.
