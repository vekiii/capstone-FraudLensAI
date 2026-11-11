# Foundation API Contract v1

Design only. JSON shapes: [schemas.json](schemas.json). Responses use application/json.
No write endpoints or production authentication. Serve only local fixture data.

| Method / path | Success | Controlled failures |
|---|---|---|
| GET /api/health | 200: {"status":"ok","mode":"fixture"} | 500 internal_error |
| GET /api/cases | 200: {"items":[CaseSummary,...]} | 500 internal_error |
| GET /api/cases/{case_id} | 200: CaseDetail | 422 invalid_request; 404 case_not_found; 500 internal_error |

case_id must match `^CASE-[0-9]{3}$`. A well-formed but absent ID is 404; malformed is 422.
All errors use {"error":{"code":"...","message":"..."}}. Do not return stack traces,
filesystem paths or credentials. Invalid scorer/repository results are internal_error,
never a successful payload. Validation errors must be normalized to this envelope.

List ordering: case_id ascending. Empty: {"items":[]}. No pagination/filtering in foundation.
No ground-truth labels or reference decisions, including nested payloads.

## Example summary
```json
{"items":[{"case_id":"CASE-001","transaction_id":"TX-001","score":0.75,"score_source":"fixture"}]}
```
## Example detail (synthetic, not an execution result)
```json
{"case_id":"CASE-001","transaction":{"transaction_id":"TX-001","occurred_at":"2026-01-01T10:00:00Z","sender_account":"DEMO-BANK-A:001","receiver_account":"DEMO-BANK-B:002","amount":"1250.00","currency":"EUR"},"risk_assessment":{"transaction_id":"TX-001","score":0.75,"source":"fixture","scorer_version":"fixture-v1","scored_at":"2026-01-01T10:00:00Z","explanation":"Illustrative synthetic score; no ML inference performed."}}
```
## Example error
```json
{"error":{"code":"case_not_found","message":"Case not found."}}
```

## Frontend behavior
Use relative /api URLs through the development proxy. Always show 'Demonstracioni podaci —
sintetički skor, bez ML predikcije' for foundation fixture results. Render loading, no-data,
not-found and unavailable states separately. Retry is explicit; timeout after 5 seconds.
Clear previous detail when selection changes; cancel/ignore late responses. Render text using
safe DOM text methods, not untrusted HTML. Reject malformed success payloads as errors.
