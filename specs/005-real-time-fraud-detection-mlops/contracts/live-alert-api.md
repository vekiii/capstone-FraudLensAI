# Proposed read-only live alert API v1

**Base:** `/api/live/v1`. This route does not exist today. Existing `/api/health`, `/api/cases` and fixture/dataset mode semantics remain intact. Authentication/authorization is required before exposure beyond a loopback demo; no raw account identifiers in list responses.

| Method/path | Request | Response and behavior |
|---|---|---|
| `GET /api/live/v1/health` | None | `status` (`ok`, `degraded`, `unavailable`), active generation/model/policy, last processed timestamp, watermark lag and redacted failure count. 503 if live store unavailable. |
| `GET /api/live/v1/alerts?limit=...&cursor=...` | `limit` 1–100, default 20; opaque signed/validated cursor | Only committed active-generation alerts. Response: `generation_id`, `policy_version`, `items`, `next_cursor`, `total_if_available`, `as_of`. Items include case/transaction ID, score string, score kind, event time, coverage, model digest prefix and explanation status. Deterministic order `(event_time DESC, transaction_id ASC)`. |
| `GET /api/live/v1/alerts/{case_id}?generation=...` | Required generation/snapshot token | Case detail with full canonical **redacted** facts permitted for analyst role, score, model/feature/deployment lineage, alert reason/policy, event/ingest/score times, coverage and explanation. 404 unknown, 409 stale generation, 422 malformed ID/token, 503 unavailable. |

Every list cursor binds generation, policy, sort tuple and page limit; a pointer switch invalidates it with 409 rather than mixing versions. `total_if_available` must not claim an exact count without a consistent snapshot. API only reads persisted predictions/decisions and never performs model inference or accesses `confirmed_labels`. Empty list is valid when no decision selects an alert. Versioned error envelope `{ "error": { "code": "...", "message": "..." } }` contains no internal SQL/secret detail. Contract tests cover pagination boundaries, stale cursor/detail, no-alert, redaction, authorization and fixture/batch regression.
