# Feature 002 API Contract Proposal v1

Design only. Feature 001 routes and payloads remain unchanged. Responses use `application/json`; schemas are closed, validated in Pydantic and decoded from `unknown` in TypeScript. This is a local single-user workflow, not an authentication claim.

| Method / path | Success | Controlled failures |
|---|---|---|
| `GET /api/transactions/{transaction_id}/risk` | 200 eligible `PredictionResult` | 404 `transaction_not_found`; 422 `invalid_request`; 409 `transaction_ineligible`; 503 `model_unavailable`; 500 `internal_error` |
| `GET /api/model/results` | 200 permitted aggregate `ModelResults` | 404 `results_unavailable`; 409 `evaluation_not_authorized`; 500 `internal_error` |
| `GET /api/eda/summary` | 200 bounded `EdaSummary` | 404 `dataset_unavailable`; 422 `invalid_request`; 500 `internal_error` |

IDs are opaque stable canonical transaction strings, not foundation `TX-###` IDs. No write endpoint exists. No endpoint accepts record-level label queries or arbitrary showcase subranges.

Prediction contains no target label. Scores must be finite in `[0,1]`; call them risk scores unless calibration was actually evaluated. Response identity must equal request identity. Warm-up rows receive no assessment (409 `transaction_ineligible`). A missing/incompatible model returns 503 in model mode; fixture mode remains available without data/model files.

Model results contain only permitted aggregate metrics with partition and provenance. Before separate test-evaluation authorization, no test metrics are returned. EDA uses bounded precomputed aggregates and excludes target values, label-derived rates, account identifiers, and individual rows. Monetary series identify exactly one currency; all counts identify their denominator.

Errors use the foundation envelope `{"error":{"code":"...","message":"..."}}`; messages are safe and bounded. Do not expose traces, rejected input, paths, or row content. Invalid model output is a controlled failure, never a zero-risk assessment.

Example controlled error (schema illustration):

```json
{"error":{"code":"model_unavailable","message":"Model assessment is unavailable."}}
```

For each EDA series, bucket label and value arrays have equal length and each is capped at 366 entries. An `amount` series must specify one currency; a `count` series has no currency unit. No series combines currencies.

## Illustrative prediction shape (not execution output)

```json
{"transaction_id":"ibm-hi-small:row:12345","risk_score":0.72,"review_status":"review_recommended","source":"model","model_version":"aml-model-v1","feature_version":"aml-features-v1","scored_at":"2026-11-18T12:00:00Z","explanation":"Illustrative schema only."}
```

## Compatibility

Do not alter Feature 001 `/api/health`, `/api/cases`, `/api/cases/{case_id}`, foundation source enum, or fixture schemas without a separately reviewed compatibility change. Add versioned Feature 002 schemas and regression checks.
