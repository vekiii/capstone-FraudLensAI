# Investigation and knowledge API v1 (planned)

Status: proposed consumer contract, not implemented endpoints. Local same-origin FastAPI routes under `/api/investigation` and `/api/knowledge`; keep all existing feature 001/002 endpoints and errors unchanged. [schemas.json](schemas.json) defines closed request/response bodies. GETs never cause provider requests. All responses are JSON with explicit `contract_version=1`; no raw exception/provider body or path is returned.

## Request identity and local access

Create/retry/review mutations require `Idempotency-Key` UUID; cancel requires the key too. Same actor/operation/key and same normalized request returns the saved response (including original ID); changed payload is 409 request_conflict. Keys persist, not an in-memory cache. Header `If-Match` is the decimal attempt revision for retry/cancel/review; absent/invalid is 422, stale is 409 revision_conflict. Server returns ETag containing that revision. Review amendment also checks the expected current review ID. Actor comes from configured local demo analyst, never a model-controlled argument.

Local demo assumes loopback access and trusted operator; it is not multi-tenant authentication. Reject cross-origin mutations and unexpected Host/Origin, accept only application/json and closed fields, disable permissive CORS. Tools receive scope from server-loaded run, never browser-supplied permissions. The original case browser still starts when this feature is disabled/unconfigured.

## Endpoints

| Method/path | Input / success | Controlled errors |
|---|---|---|
| GET /api/knowledge/documents?corpus={id} | DocumentList with provenance, complete selected version | 422 invalid_request; 503 knowledge_unavailable |
| GET /api/knowledge/search?q={query}&corpus={id}&retrieval={id} | SearchResult with ranked passage hits or no_match | 422 invalid_request; 503 knowledge_unavailable |
| GET /api/knowledge/passages/{passage_id}?corpus={id} | Exact Passage and provenance | 404 evidence_not_found; 503 knowledge_unavailable |
| POST /api/investigation/runs | CreateRequest {case_id, source_mode, snapshot_ref}; 202 RunView | 404 case_not_found; 409 stale_snapshot/request_conflict; 503 context/knowledge/provider_unavailable |
| GET /api/investigation/runs?case_id={id}&context_revision={hash} | RunList; saved attempts only, no new generation | 422 invalid_request |
| GET /api/investigation/attempts/{attempt_id} | RunView with current state, safe tool trace, report/review, limits | 404 investigation_not_found |
| GET /api/investigation/attempts/{attempt_id}/evidence/{evidence_id} | Exact Evidence envelope with authorized provenance | 404 evidence_not_found |
| POST /api/investigation/attempts/{attempt_id}/retry | RetryRequest {reuse_evidence}; 202 RunView of new child | 409 invalid_transition/revision_conflict/stale_snapshot/request_conflict; 503 dependency unavailable |
| POST /api/investigation/attempts/{attempt_id}/cancel | Empty object; 200 updated RunView | 409 invalid_transition/revision_conflict/request_conflict |
| POST /api/investigation/attempts/{attempt_id}/reviews | ReviewRequest; 201 updated RunView | 409 invalid_transition/revision_conflict/request_conflict |

Global new-route statuses: 422 invalid_request, 403 forbidden_scope (cross-origin mutation/access), 503 store_busy, 500 internal_error. Unknown investigation resources use their feature's 404 code; do not reuse foundation's case_not_found for every missing route. New-route errors use ErrorEnvelope {contract_version:1,error:{code,message,retryable}} and fixed safe messages. Error code/status agreement is validated in client. Provider failure after enqueue is a persisted failed state, not a retroactive HTTP-create error. No live model call occurs just to check POST readiness; provider unavailability at create means missing local configuration, while credentials/capability failures are worker outcomes or opt-in probe results.

Knowledge search query is trimmed 1-500 characters; corpus/retrieval parameters must name configured complete versions (no paths). Limit fixed to 5, no browser override. List runs returns at most the latest 20 with explicit truncated flag and total_count; order created_at descending then run_id. A run view identifies its active/latest attempt; old attempts remain fetchable. All UI detail updates check case_id/context_revision/attempt_id and generation token, not selected case ID alone.

## Context proposal and producer review

`InvestigationContext` is an internal immutable boundary defined by schemas + [data model](../data-model.md), not a new publicly writable context endpoint. Client create payload cannot send source_payload, actor, corpus filesystem paths, permissions or arbitrary model ID. Server selects context/provider/retrieval configurations.

Dataset source_payload is CaseDetailV2 from the pinned producer snapshot at `2dd815d85bfc9c2fc70a28baef9c142d551e57e0`. [producer-v2.snapshot.json](producer-v2.snapshot.json) is a documentation/test reference, not a second producer implementation; its exact Git content is preserved. Fixture source_payload references the unchanged foundation CaseDetail definition. Context revision hashes all context fields except the revision itself; source_snapshot equality and semantic consistency are mandatory in addition to JSON Schema.

The pinned snapshot's original Git/LF content digest is `bf487d84ccac1e315d0e20fece0d2a7f45990bce954ba40bf97cd54e43929f88`. Verification normalizes checkout CRLF to LF before byte comparison, so a Windows text checkout is not mistaken for an edited contract. No JSON keys or values are normalized/reformatted during that check.

Before real dataset integration, producer and affected consumer record actual names/date/current source SHA/findings/decision in `evidence/tasks/feature-003-context-review.md`. Review must cover raw minute and timezone assumptions, history strict cutoff and bank identity, paid/received money precision/currencies, score meaning, partial/unavailable explanations and source privacy. No claim that this proposed wrapper is already approved.

## Public run and report projection

RunView contains no credentials, private labels, raw SDK request bodies, private continuation items or stack traces. Safe trace exposes operation names, sequence, status, timing and evidence IDs. User can inspect exact evidence locally; provider gets only allowlisted aliased subset. All outputs are schema-validated. Nullable report/review/failure are required fields with explicit null, not omitted keys.

Report sections retain structured claim types/citations; source numbers display unchanged. An available report is labeled automatic schema/reference validation passed, semantic review pending until a human review exists. Human disposition does not automatically imply every scientific evaluation rubric item passed; evaluation ratings are separate.

## Compatibility and examples

Examples under `examples/` are authored contract examples, not IBM execution or provider output. Contract tests must validate schema and cross-object identity separately, including mutated IDs, all error/status pairs, exact fixture behavior and current producer snapshot. On source run switch, new case reads/retries fail stale_snapshot instead of importing mixed data; a saved completed report remains inspectable as historical.
