# Feature 002 API Contract v1

The prediction, aggregate results and EDA summary routes are implemented. The dedicated EDA page is pending the T243 team decision; the backend exposes a bounded summary through `GET /api/eda/summary`. Feature 001 routes and fixture payloads remain unchanged. Responses use `application/json`; prediction/results schemas are closed in Pydantic and TypeScript, while the EDA schema is closed in Pydantic, JSON Schema and a future T248 TypeScript decoder. This is a local single-user workflow, not an authentication claim.

| Method / path | Success | Controlled failures |
|---|---|---|
| `GET /api/transactions/{transaction_id}/risk` | 200 eligible `PredictionResult` | 404 `transaction_not_found`; 422 `invalid_request`; 409 `transaction_ineligible`; 503 `model_unavailable`; 500 `internal_error` |
| `GET /api/model/results` | 200 permitted aggregate `ModelResults` | 404 `results_unavailable`; 409 `evaluation_not_authorized`; 422 `invalid_request` for any query; 500 `internal_error` |
| `GET /api/eda/summary` | 200 bounded, independently hash-pinned `EdaSummary` | 404 `dataset_unavailable`; 422 `invalid_request` for any query; 500 `internal_error` |

Prediction IDs have the frozen `ibm-hi-small:<source-sha256>:row:<positive-integer>` form, not foundation `TX-###` IDs. The current local model source is the separately hashed, label-free train/validation/test feature snapshot. It has no showcase or warm-up records; an ID absent from that snapshot returns `transaction_not_found`. A known but explicitly unscoreable record returns `transaction_ineligible`. No write endpoint exists. No endpoint accepts record-level label queries or arbitrary showcase subranges.

Prediction contains no target label. Scores must be finite in `[0,1]`; call them risk scores unless calibration was actually evaluated. Response identity must equal request identity. Warm-up rows receive no assessment (409 `transaction_ineligible`). A missing/incompatible model returns 503 in model mode; fixture mode remains available without data/model files.

Model results contain only permitted aggregate metrics with partition, UTC coverage, row/positive/negative counts, denominators, synthetic provenance, exact frozen model and threshold, calibration status and limitations. The route is available only in explicit local model mode. It verifies the exact T230 authorization and completion evidence hashes, report SHA-256 `5027dae9354796718a080086a6cadc0319d1b376336ad4dac8d93b4e534d9cdb`, frozen experiment/lineage/model identities, validation report, prediction hash and feature manifest before returning validation and authorized test aggregates. Missing or changed authorization returns 409; missing or mismatched reports return 404. It accepts no query parameters and never opens source rows, label files or prediction CSVs or performs evaluation. Whole-partition P@K is named as such; UTC daily alert counts are uncapped and do not imply daily P@K. The full, hash-verified reports retain PR-curve data; the API exposes a bounded presentation subset.

EDA uses bounded Python-precomputed aggregates and excludes target values, label-derived rates, account identifiers, and individual rows. `EDA_SUMMARY_PATH` and `EDA_SUMMARY_SHA256` must both be set to a trusted local, previously generated summary; the independent digest is verified **before JSON parsing**, and the embedded source SHA-256 must equal the exact approved local source. There is no runtime source scan or aggregation on GET. If no pinned summary is configured, fixture startup and `/api/cases` continue normally while EDA returns 404 `dataset_unavailable`. The one verified local T210 summary has SHA-256 `b8900338ca375b2d632b260a794634fb19408012a1c14fc66e2f7b097a111820`; its full provenance is recorded in [T246 execution evidence](../../../evidence/tasks/T246-full-source-eda-2026-11-21.md). All query parameters are refused before loading.

`EdaSummary` carries synthetic origin, dataset/source identity, UTC coverage, source/accepted/rejected/warm-up/scoreable counts, non-label quality counts and at most 30 series. Quality counts use `source_count` as denominator. Categorical and UTC transaction-count series use `accepted_count` as denominator and sum to it, with rare categories grouped as `__OTHER__`. Per-currency paid/received amount series use transaction count in that side/currency as denominator and report **amount totals by UTC bucket**; the values have the stated currency unit, never a cross-currency sum. At most 12 currencies per side are shown and `omitted_amount_currencies` discloses any omitted currencies. Each series has at most 366 points; UTC buckets widen deterministically if coverage is longer. Amount totals serialized as numbers are presentation approximations from exact Decimal accumulation, not audit balances.

Errors use the foundation envelope `{"error":{"code":"...","message":"..."}}`; messages are safe and bounded. Do not expose traces, rejected input, paths, or row content. Invalid model output is a controlled failure, never a zero-risk assessment.

Example controlled error (schema illustration):

```json
{"error":{"code":"model_unavailable","message":"Model assessment is unavailable."}}
```

For each EDA series, bucket label and value arrays have equal length and each is capped at 366 entries. An `amount` series specifies one currency and paid/received side; a `transactions` series has no currency. No series combines currencies. A controlled unavailable example is `{"error":{"code":"dataset_unavailable","message":"EDA summary is unavailable."}}` (illustrative contract response, not a browser observation).

Illustrative EDA series inside a synthetic one-row summary (schema shape only, not source output):

```json
{"series_id":"paid_amount_USD","label":"Paid amount: USD","unit":"amount","bucket_labels":["2022-09-01"],"values":[10.0],"denominator":1,"currency":"USD","side":"paid","timezone":"UTC"}
```

## Illustrative prediction shape (not execution output)

```json
{"transaction_id":"ibm-hi-small:b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040:row:12345","risk_score":0.72,"review_status":"review_recommended","source":"model","model_version":"lightgbm-3b4e4019312d","feature_version":"hi-small-temporal-v1","synthetic_data":true,"scored_at":"2022-09-06T12:00:00Z","explanation":"Illustrative schema only; actual explanations use observed feature facts."}
```

## Compatibility

Do not alter Feature 001 `/api/health`, `/api/cases`, `/api/cases/{case_id}`, foundation source enum, or fixture schemas without a separately reviewed compatibility change. Add versioned Feature 002 schemas and regression checks.
