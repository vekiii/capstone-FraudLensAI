# Simulation contract v1

This draft defines the fixture source boundary and the local HTTP interface for the Simulation & Evaluation screen. See the [data model](../data-model.md) for relationships and invariants.

## Frozen input

A trusted scenario source provides one immutable scenario and its separate outcome set. The runtime loads the bundled data by reference from its catalog. Scenario files are deployed with the app. Caller-supplied filesystem paths, alerts, labels and strategy formulas are outside the interface.

- Scenario facts consist of the scenario metadata defined below and an `alerts` array. A separate outcome file contains `scenario_id`, `scenario_version` and an array of `{alert_id, outcome}` objects, with `outcome` equal to `positive` or `negative`. Missing IDs mean unknown. A scenario without labels may have an empty outcome set.
- Each alert has `alert_id`, `available_at`, `score`, `weight`, `estimated_review_minutes`, `weight_assumption_id` and `duration_assumption_id`. Use case-sensitive stable ASCII IDs consisting of 1–80 letters, digits, underscores or hyphens.
- Use RFC 3339 UTC timestamps ending in `Z`, with seconds and at most six fractional digits. The canonical form for hashing always includes six fractional digits. Windows are ordered by instant. Sort alerts and outcomes by ID before hashing.
- Scores, thresholds and weights are JSON strings using unsigned plain decimal notation, with at most 128 characters, no exponents or leading zeros on the integral part. Scores and thresholds are in [0,1]. Weights are strictly positive. Remove trailing fractional zeros and any remaining decimal point in their canonical form. Use exact arithmetic for ranking. Use positive, JavaScript-safe integers for durations and versions and nonnegative safe integers for budgets and seeds.
- Canonical hashing uses sorted object keys, compact JSON encoded as UTF-8 without ASCII escaping, and SHA-256 in lowercase hex. Hash the object with keys `scenario` and `outcomes`, using the metadata without `content_sha256`, normalized alert facts and the separately normalized outcome file. Preserve array order except for alerts, outcomes and assumptions, which sort by ascending ID. Always represent an absent seed as `null`.

## HTTP requests

| Method and path | Success | Controlled errors |
| --- | --- | --- |
| `GET /api/simulation/scenarios` | 200 with `contract_version: 1` and `items`, sorted by scenario ID and then ascending version. | 500 `internal_error` for invalid bundled data or a service failure. |
| `POST /api/simulation/comparisons` | 200 with a comparison. The operation is synchronous and has no persistent side effects. | 422 `invalid_request` for malformed input or unsupported contract version. 409 `simulation_version_unavailable` for unknown scenario revision, digest mismatch or unsupported strategy version. 500 `internal_error` for service failure. |

Error bodies follow `{"error":{"code":"…","message":"…"}}`. A failure has no partial comparison and discloses no local path, outcome rows or internals. The simulator handles its own version error without changing existing case responses.

Each scenario catalog item is a closed object with:

| Field | Value |
| --- | --- |
| `scenario_id`, `scenario_version`, `content_sha256` | Immutable reference used in the recipe. |
| `title`, `horizon`, `window_starts` | Title, UTC `{starts_at, ends_at}` and ordered UTC starts. |
| `source` | `kind` (`bundled_synthetic` for initial acceptance), `data_version` and a displayable `time_basis`. Future batch metadata must use a reviewed contract. |
| `score_provenance` | `source` (`fixture` for the bundled data), `score_kind` (`illustrative_score` for the bundled data), and `scorer_version`. |
| `assumptions`, `generation_seed` | List of `{id, description}` and a seed or null. |
| `defaults` | `score_threshold` and `budget_minutes_per_window`, using the recipe's types. |

The POST accepts this closed recipe object. The digest below illustrates the format. Use the catalog's actual digest in a request.

```json
{
  "contract_version": 1,
  "scenario": {
    "scenario_id": "review-capacity-demo",
    "scenario_version": 1,
    "content_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "score_threshold": "0.30",
  "budget_minutes_per_window": 2,
  "strategy_versions": {
    "fifo": 1,
    "highest_score": 1,
    "weighted_score_per_minute": 1
  }
}
```

The browser downloads the returned recipe as JSON. Reopening a recipe submits it unchanged to the comparison endpoint. Reject an invalid file locally where possible and surface unavailable versions with a readable failure. Require the user to explicitly start a new run if an exact rerun is unavailable.

## Comparison response

The closed response contains `contract_version: 1`, `recipe` in the request shape with canonical decimal text, `scenario` in the catalog shape, `admitted_alerts` using the label-free alert shape sorted by availability and ID, and `strategies` in FIFO, highest score, weighted score per minute order.

Each strategy record contains:

- `strategy_id`, matching one key in `strategy_versions`.
- `windows`, each with `starts_at`, `ranked_alert_ids`, `reviewed_alert_ids` and `used_minutes`. The ranked list includes items scanned but skipped for budget. Review order is a subsequence of that list.
- `pending_alert_ids` in availability and ID order.
- `counts` with integers `reviewed`, `backlog`, `unknown_in_horizon`, `unknown_reviewed` and `outcomes`. When outcomes are available, `outcomes` contains integer `positives_found`, `positives_missed`, `positives_missed_threshold`, `positives_missed_backlog` and `reviewed_negatives`. For a nonempty scenario with no known labels it is null. For an empty scenario it is an object whose counts are all zero.

All counts are nonnegative. Backlog equals pending length. The missed-positive total is the sum of its two reasons. A comparison can include partial label coverage and must show the unknown counts. Its recipe and result contain no per-alert evaluation labels.
