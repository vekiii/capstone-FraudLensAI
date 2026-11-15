# Proposed Feature 005 contracts

All contracts in this directory are **proposed v1**, not implemented endpoints or broker schemas. Implementation tasks must freeze exact bytes, review producers/consumers, add positive/negative schema tests, and record compatibility decisions before live activation. Existing fixture v1 and dataset v2 contracts under [Feature 001](../../001-project-foundation/contracts/api.md) and [Feature 002](../../002-data-and-risk-scoring/contracts/api.md) remain unchanged.

| Contract | Producer → consumer | Identity and failure rule |
|---|---|---|
| [Transaction event JSON Schema](transaction-event.schema.json) | Authorized SQL producer / CDC mapper → worker | `transaction_id` and source ID stable, facts immutable; unknown version/fact conflict quarantined. |
| [CDC contract](cdc-contract.md) | PostgreSQL/Debezium → broker/worker | Committed insert only, source LSN/offset checked; no update/delete interpreted as new transaction. |
| [Feature contract](feature-contract.md) | Finalized ordered event state → live adapter | Eleven ordered `history-v1` inputs, strict-past 24-hour window and full coverage. |
| [Model-serving contract](model-serving-contract.md) | Reviewed artifact/deployment → worker | Separate live serving ID and source lineage; full trusted hash/dependency checks. |
| [Prediction JSON Schema](prediction.schema.json) | Live adapter → SQL/API | Immutable score/provenance/explanation; policy decision stored separately. |
| [Live alert API](live-alert-api.md) | PostgreSQL read model → FastAPI/dashboard | Read-only, bounded cursor and generation consistency. |
| [Label feedback](label-feedback-contract.md) | Authorized investigator → restricted offline label store | Confirmed delayed labels; never exported on inference topic. |

Schema evolution: all payloads carry `schema_version`; add optional fields only after compatibility tests, keep unknown required values fail-closed, and use a new major version for renamed/changed semantics. Consumers reject unknown major versions; registry/DB migrations use expand → migrate → contract. The current JSON Schemas cover **canonical worker-facing records**, not the raw Debezium envelope; [CDC mapping](cdc-contract.md) defines that transformation. See [data-model.md](../data-model.md) for table keys and [plan.md](../plan.md) for transactional guarantees.
