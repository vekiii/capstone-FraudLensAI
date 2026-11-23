# Investigation and knowledge API v1 (planned)

2026-11-17 additive implementation: explicit paid semantic POST/status/cancel
contract is in [semantic-search-v1.md](semantic-search-v1.md). Existing GET paths
remain free. Semantic worker stages use original attempt budgets, with pinned
semantic policy/runtime hashes in binding audit in addition to the base lexical
retrieval version. Semantic mode is opt-in for new attempts, preserved on retry.
Only safe model/request/usage metadata is public; raw SDK bodies stay in local audit.

Status (2026-11-15): knowledge, create/list/attempt/evidence, retry/cancel and Phase 6 review/amendment routes implemented offline. Human acceptance remains pending. Local same-origin FastAPI routes under `/api/investigation` and `/api/knowledge`; existing feature 001/002 endpoints and errors unchanged. [schemas.json](schemas.json) defines closed request/response bodies. GETs never cause provider requests. All responses are JSON with explicit `contract_version=1`; no raw exception/provider body or path is returned.

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

## Context proposal and producer review (historical v1)

The dated proposal below preserves the original v1 boundary/review state. The
current context-v2 addendum later in this document supersedes its pending-review
status for the accepted adapter only; it does not redefine historical contracts.

Phase 4 fixture binding clarification (2026-11-14): list accepts `case_id` alone
to resolve the server's current source context without modifying foundation JSON.
It returns `X-Investigation-Snapshot` and `X-Investigation-Context` headers alongside
the unchanged closed RunList body. Supplying `context_revision` pins subsequent
reads; a current-source mismatch returns 409 stale_snapshot. The browser uses the
resolved snapshot in CreateRequest, never a fabricated placeholder or source path.
Historical attempts remain accessible by their immutable attempt ID. No dataset
producer approval is implied.

Phase 6 review clarification: POST reviews also appends amendments. The exact
saved report_id, If-Match attempt revision and current supersedes_review_id are
checked together. Initial review requires supersedes_review_id=null; amendment
requires the latest review ID and a nonempty correction_note. Stale report,
revision or superseded review returns 409 revision_conflict. A missing amendment
note or prohibited disposition returns 409 invalid_transition. Blank/oversized
text, forged actor, missing headers or unknown fields return 422 invalid_request.
Rationale, correction note and configured actor are trimmed; actor is server-owned.
The HTTP review body is bounded to 64 KiB to accommodate legal escaped Unicode
in both 2000-character text fields; field limits remain unchanged.

Review record, audit, revision/state and saved original 201 RunView commit in one
transaction. Same normalized request/actor/key returns that original response
even after later amendments; changing target/revision/body with the same key
returns request_conflict. All reviews remain immutable in SQLite. RunView exposes
the latest review including its supersedes link; it does not expose the full
audit history. Corrections are separate human notes bound to the same original
report, never rewritten AI prose. Original report/evidence rows and validation
events remain unchanged. semantic_review=reviewed_with_notes is derived in the
public projection; it is not a scientific quality rating or inferred signature.
Needs-information restrictions persist through amendments. Reviewed work cannot
be retried/cancelled. No source refresh or provider call occurs during review.

Phase 5 clarification: a run list returns the latest attempt of each run, with
total_count counting runs, not parent/child attempts. Retry reserves/increments
the parent's revision in the same transaction as child creation, without changing
the parent's terminal state, report or counters. Distinct keys using that old
revision cannot create two children; same-key replay returns the original child
response. Retry/cancel responses are persisted atomically with their mutations.
Cancel may retain Failure with outcome_unknown when a dispatched request could
already have executed. Its state remains cancelled. Reuse requires compatible
context/corpus/retrieval and revalidated exact content; reuse=false may select
the latest corpus/retrieval while retaining the pinned prompt/provider/limits.

`InvestigationContext` is an internal immutable boundary defined by schemas + [data model](../data-model.md), not a new publicly writable context endpoint. Client create payload cannot send source_payload, actor, corpus filesystem paths, permissions or arbitrary model ID. Server selects context/provider/retrieval configurations.

Dataset source_payload is CaseDetailV2 from the pinned producer snapshot at `2dd815d85bfc9c2fc70a28baef9c142d551e57e0`. [producer-v2.snapshot.json](producer-v2.snapshot.json) is a documentation/test reference, not a second producer implementation; its exact Git content is preserved. Fixture source_payload references the unchanged foundation CaseDetail definition. Context revision hashes all context fields except the revision itself; source_snapshot equality and semantic consistency are mandatory in addition to JSON Schema.

The pinned snapshot's original Git/LF content digest is `bf487d84ccac1e315d0e20fece0d2a7f45990bce954ba40bf97cd54e43929f88`. Verification normalizes checkout CRLF to LF before byte comparison, so a Windows text checkout is not mistaken for an edited contract. No JSON keys or values are normalized/reformatted during that check.

Before real dataset integration, producer and affected consumer record actual names/date/current source SHA/findings/decision in `evidence/tasks/feature-003-context-review.md`. Review must cover raw minute and timezone assumptions, history strict cutoff and bank identity, paid/received money precision/currencies, score meaning, partial/unavailable explanations and source privacy. No claim that this proposed wrapper is already approved.

## Current context-v2 / reviewed-producer addendum (2026-11-17)

The [accepted adapter agreement](../dataset-adapter-agreement-v2.md) and
[superseding T062 review decision](../../../evidence/tasks/feature-003-context-review.md#superseding-review-decision-2026-11-16-t062)
record user-conveyed team confirmation on 2026-11-16. This is not a set of separate
individual signatures. The available reviewed producer is
`487c427ea50e169f5e36898420d659f05ead2c60` on
`origin/feature/005-real-time-fraud-detection-mlops-spec`. The colleague document's
unavailable `9454bfc` reference remains a deferred documentation correction; this
adapter is bound to the available SHA above.

### Version selection and retained identities

| Boundary | Schema / producer pin | Meaning |
|---|---|---|
| Internal `InvestigationContext.contract_version=1` | [schemas.json](schemas.json), [producer-v2.snapshot.json](producer-v2.snapshot.json), producer `2dd815d85bfc9c2fc70a28baef9c142d551e57e0` | Historical dataset contexts and current authored fixture contexts retain their original shapes. Fixture payload remains foundation CaseDetail, without fabricated dataset metadata. |
| Internal `InvestigationContext.contract_version=2` | [context-v2.json](context-v2.json), [producer-v2-reviewed-20261116.snapshot.json](producer-v2-reviewed-20261116.snapshot.json), producer `487c427ea50e169f5e36898420d659f05ead2c60` | Dataset-only context selected explicitly by the implemented adapter; embedded CaseDetailV2 retains its own `contract_version=2`. |
| Public investigation/knowledge HTTP envelopes | [schemas.json](schemas.json) | `contract_version=1` remains unchanged for RunView/RunList/Evidence/errors and other versioned request/response objects. Internal context-v2 does not introduce HTTP API v2. |

The original snapshot's LF-normalized SHA-256 remains
`bf487d84ccac1e315d0e20fece0d2a7f45990bce954ba40bf97cd54e43929f88`.
The reviewed snapshot's LF-normalized SHA-256 is
`3bb54c0bcad5f4683db8ee6ef1e663749993a25ab144869190ce0182ac6f7ab2`.
Normalize checkout CRLF to LF for these checks, without reformatting JSON. Both
snapshots and historical v1 schemas/examples/report bindings remain preserved.
The authored [context-dataset.json](examples/context-dataset.json) is still a v1
context example; it is not an execution of the reviewed adapter or trained model.

The only parsed producer-schema difference is the additional available-explanation
method `boosted_sequential_probability`. Context-v2 accepts it on
`positive_class_estimate` scale. Sequential contributions depend on order/baseline;
they are not causal, SHAP or calibrated probabilities. Existing methods retain
their scales: `rules` → `risk_score`, `linear_log_odds` → `log_odds`, `tree_path` →
`positive_class_estimate`. Old v1 contexts continue to reject the new method.
[models.py](../../../backend/src/fraudlens/investigation/models.py) selects the
context schema by version; unknown versions fail closed. Cross-object case,
transaction, snapshot/run, dataset and cutoff equality plus the context digest
remain mandatory. The adapter additionally checks event-time/cutoff and scorer/
score-source/kind/method consistency, and available additive reconstruction when
base/remainder are supplied (tolerance `1e-8`, sigmoid for log-odds). Exact
directional money strings, currencies, raw minute and assumed UTC basis survive.

### Implemented read-only composition

[InvestigationService](../../../backend/src/fraudlens/investigation/workflow.py)
constructs [DatasetReader](../../../backend/src/fraudlens/investigation/dataset.py)
when `INVESTIGATION_SOURCE=dataset`, passing it through CaseContextReader and
HistoryReader. API service construction and CLI worker use this service boundary.
Both processes must use the same investigation store, source settings and trusted
server paths: `INVESTIGATION_DATASET_RUN_STORE`, `INVESTIGATION_DATASET_STORE`,
`INVESTIGATION_DATASET_SCORE_SOURCE=rules|model`. The worker's `--store` must match
the API's `INVESTIGATION_STORE`. See [quickstart](../quickstart.md#reviewed-dataset-adapter-t062-t064-2026-11-16).
Clients cannot submit filesystem paths, SQL, context payloads, model configuration
or permissions; the existing create/list/attempt routes and closed bodies apply.

The adapter reads completed active published scored runs for the configured score
source and alert cases. Connections use SQLite `mode=ro`, fixed parameterized SQL,
an allowlist excluding private label tables and finite query deadlines. It does
not import producer code, create/update producer stores, train, score or activate
a model. Unavailable/invalid sources never fall back to fixtures. An absent case
in a valid published run is `404 case_not_found`; active-source mismatches are
`409 stale_snapshot`; unavailable/invalid context is `503 context_unavailable`
(existing busy/error handling still applies).

Dataset history is scoped to the chosen side's bank **and** account, both movement
directions, from cutoff minus seven days inclusive to the focal minute exclusive,
excluding the focal transaction. Outgoing uses paid money; incoming uses received
money, and self-transfers yield both movements. At most 50 events are returned;
whole-item tool byte truncation may reduce that count. Eligible counts and exact
Decimal totals cover all eligible movements before truncation, grouped by
direction and currency, without FX or netting. Full/incomplete coverage refers
only to this synthetic store's window. Missing history has unavailable coverage
and `eligible_count=null`, distinct from available empty (`eligible_count=0`).
New reads/retries enforce active-source binding; archived contexts, reports and
evidence remain inspectable by saved attempt ID without provider dispatch.

### Verification boundary

The existing [controlled adapter evidence](../../../evidence/tasks/feature-003-context.md)
covers authored-store/API/archive checks and a separate actual-producer-code
smoke with authored rules/model-shaped publications. These establish controlled
compatibility, not full IBM population import, trained inference, ML quality or
application assembly. Foundation `/api/cases` and current case browser/UI still
use the unchanged fixture contracts. Full producer dataset/model assembly remains
unrun under open T098; this addendum does not close it, repeat T062–T067 or accept
SC-007 in full. Existing failed retrieval/quality/timing results and T094–T098
remain unchanged; no new live call, evaluation, merge or acceptance is implied.

## Public run and report projection

RunView contains no credentials, private labels, raw SDK request bodies, private continuation items or stack traces. Safe trace exposes operation names, sequence, status, timing and evidence IDs. User can inspect exact evidence locally; provider gets only allowlisted aliased subset. All outputs are schema-validated. Nullable report/review/failure are required fields with explicit null, not omitted keys.

Report sections retain structured claim types/citations; source numbers display unchanged. An available report is labeled automatic schema/reference validation passed, semantic review pending until a human review exists. Human disposition does not automatically imply every scientific evaluation rubric item passed; evaluation ratings are separate.

## Compatibility and examples

Examples under `examples/` are authored contract examples, not IBM execution or provider output. Contract tests must validate schema and cross-object identity separately, including mutated IDs, all error/status pairs, exact fixture behavior and current producer snapshot. On source run switch, new case reads/retries fail stale_snapshot instead of importing mixed data; a saved completed report remains inspectable as historical.
