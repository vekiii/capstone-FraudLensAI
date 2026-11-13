# Feature 002 dataset API contract v2

Status: technically amended and collectively team-approved on 2026-11-13; runtime integration remains pending. See the Feature 002 contract-review evidence for the approval basis.
[schemas.json](schemas.json) is the machine-readable
public shape; [data-and-scoring.md](data-and-scoring.md) covers offline and
internal boundaries. Foundation fixture v1 remains authoritative in
[its existing contract](../../001-project-foundation/contracts/api.md).

## Mode and compatibility

- APP_MODE=fixture continues to return the exact v1 fixture health/list/detail
  bodies, three demo cases, v1 case-ID ordering and v1 controlled errors.
  Existing v1 validators and decoders stay closed; no new v2 fields appear
  in fixture responses.
- APP_MODE=dataset requires APP_SCORER=rules or model and a selected complete
  run whose recorded scorer matches. Neither source selection nor missing
  artifact may silently fall back to fixture or the other scorer.
- Dataset responses use the same read-only GET paths with an explicit numeric
  contract_version of 2. The frontend dispatches on that discriminator in
  each response; it cannot rely on a prior health request.
- All success objects are closed and label-free. Dataset source and scorer
  source are distinct. The score is always finite in [0,1], with a declared
  score_kind. No public import, train, evaluate or activate endpoint exists.

## Endpoints

| Method/path | Dataset success | Controlled errors |
|---|---|---|
| GET /api/health | 200 HealthV2: ok or unavailable with explicit mode/source/active run | 500 internal_error for server fault |
| GET /api/cases | 200 CaseListV2 from one active completed run; zero alerts is a valid empty list | 503 run_unavailable; 500 internal_error |
| GET /api/cases/{case_id}?snapshot={snapshot_ref} | 200 CaseDetailV2 for exactly that active snapshot | 422 invalid_request; 404 case_not_found; 409 stale_snapshot; 503 run_unavailable; 500 internal_error |

case_id must match C followed by 32 lowercase hexadecimal digits in dataset
mode. snapshot_ref must be a nonempty opaque run ID returned by the list.
Malformed or absent snapshot is 422. If a complete run exists but the
reference no longer names the current active run, return 409 stale_snapshot;
never return a detail from another run. A well-formed case ID absent from
that active snapshot is 404. If there is no complete active run, list/detail
return 503 run_unavailable. No filesystem path, raw label, stack trace,
credential or model binary is included in errors.

The application captures one active run pointer per request. The list
references that pointer; detail verifies its snapshot query before reading
an assessment. A run switch between requests yields stale_snapshot.
Completed runs may remain stored for reproducibility, but the analyst API
exposes only the active one under this initial contract.

## HealthV2

Fields: contract_version=2, status=ok|unavailable, mode=dataset,
data_source=ibm_aml_hi_small, score_source=rules|model,
dataset_version (string or null), active_run_id (string or null).
An unavailable health state is an explicit dataset state, not a fixture
response or evidence of a successful model run.

## CaseListV2

Fields: contract_version=2, snapshot_ref, dataset_version,
data_source, score_source, scorer_version, total_alerts,
displayed_count, truncated, selected_time_range {from,to}, items.
The interval is null/null when no alert is displayed. total_alerts counts
all threshold alerts in the completed scored run; displayed_count equals
items length and is at most 100. truncated is true exactly when
total_alerts > displayed_count. The list is a review display, not the
test/evaluation population.

When more than 100 alerts exist, select the most recent 100 by descending
event time, then ascending transaction ID for ties. Return the chosen
items ascending by event time and transaction ID. The frontend must not
re-sort v2 items by case ID. Every item contains case_id, transaction_id,
event_time, score, score_kind and score_source. One transaction appears
at most once in a completed run's alert list.

## CaseDetailV2

Fields: contract_version=2, snapshot_ref, dataset_version, case_id, transaction,
risk_assessment. The transaction and assessment IDs match the case list
item. The assessment run_id equals snapshot_ref. The required detail-envelope
dataset_version equals risk_assessment.dataset_version, the pinned list's
dataset_version and the selected completed run's dataset_version. The repository
also checks its internal canonical transaction.dataset_version against that run.
Public TransactionV2 intentionally has no dataset_version property. These are
mandatory semantic equality rules for later coordinated producer/consumer
validators; JSON Schema alone does not enforce cross-object equality. Detail
never returns private labels.

TransactionV2 contains transaction_id, event_time_utc, event_time_raw,
time_basis, sender and receiver bank/account objects, paid and received
amount/currency objects, and payment_format (string or null). Amounts
are exact nonnegative decimal strings with source-supported scale;
they are not converted or forced into Foundation's two-decimal form.
time_basis is source_explicit_timezone, documented_source_timezone, or
assumed_utc_for_synthetic_benchmark. The last is the user-approved fixed UTC+00
analysis convention for this synthetic source: it does not assert source UTC,
clock synchronization or transaction settlement time. Preserve raw minute text
and minute ties; `:00` seconds are a coordinate convention, not measured precision.
The selected policy/hash must match the source mapping and completed run, and
the dataset UI/investigation/priority context must disclose the assumption.
Actual scored_at remains real execution time in UTC. Source-row ordinals and private labels are omitted
from this analyst response.

Money preserves the original source amount/currency on each side. Currency
length is 1–17 characters; the import mapping additionally restricts the exact
reviewed source currency names. No ISO conversion, truncation or FX inference.
All identifier/amount/instant patterns use strict terminal assertions; a final
newline is invalid even where a regular-expression dollar anchor would match.

AssessmentV2 contains transaction_id, run_id, dataset_version, score,
score_kind (ordinal_rule_score, uncalibrated_probability_estimate,
calibrated_probability), score_source, scorer_version, feature_version,
event_time_utc, history_cutoff_exclusive_at, scored_at,
history_coverage {state,start}, and explanation. The score_kind is
truthful for the selected artifact; a rule score cannot be called a
probability. scored_at is actual execution time, not a copy of event time.

ExplanationV2 is either available or unavailable. Available explanations
carry method (rules, linear_log_odds or tree_path), explained_scale,
feature_snapshot_digest, partial, base_value/remainder if an additive
reconstruction is claimed, and up to three items with actual feature
key, observed value/unit, direction, numeric contribution, and optional
rule condition. A linear log-odds explanation is identified as explaining
log odds even when the displayed risk score is transformed to [0,1].
Unavailable explanations carry a reason code and snapshot digest; no
invented narrative is substituted. Case copy never implies guilt.

## Example: rules list and detail

These are **contract examples**, not observed IBM records or an executed
scoring result. IDs/values are illustrative valid shapes. The JSON Schema
is authoritative for field-level validation.

    GET /api/cases
    {
      "contract_version": 2,
      "snapshot_ref": "run_example_1",
      "dataset_version": "dv_example_1",
      "data_source": "ibm_aml_hi_small",
      "score_source": "rules",
      "scorer_version": "rules-v1",
      "total_alerts": 1,
      "displayed_count": 1,
      "truncated": false,
      "selected_time_range": {"from": "2026-01-01T10:00:00Z", "to": "2026-01-01T10:00:00Z"},
      "items": [{
        "case_id": "C0123456789abcdef0123456789abcdef",
        "transaction_id": "D0123456789abcdef0123456789abcdef",
        "event_time": "2026-01-01T10:00:00Z",
        "score": 0.65,
        "score_kind": "ordinal_rule_score",
        "score_source": "rules"
      }]
    }

    GET /api/cases/C0123456789abcdef0123456789abcdef?snapshot=run_example_1
    {
      "contract_version": 2,
      "snapshot_ref": "run_example_1",
      "dataset_version": "dv_example_1",
      "case_id": "C0123456789abcdef0123456789abcdef",
      "transaction": {
        "transaction_id": "D0123456789abcdef0123456789abcdef",
        "event_time_utc": "2026-01-01T10:00:00Z",
        "event_time_raw": "2026/01/01 10:00",
        "time_basis": "assumed_utc_for_synthetic_benchmark",
        "sender": {"bank": "SYNTH-BANK-A", "account": "001"},
        "receiver": {"bank": "SYNTH-BANK-B", "account": "002"},
        "paid": {"amount": "1250.000", "currency": "Australian Dollar"},
        "received": {"amount": "1250.000", "currency": "Australian Dollar"},
        "payment_format": null
      },
      "risk_assessment": {
        "transaction_id": "D0123456789abcdef0123456789abcdef",
        "run_id": "run_example_1",
        "dataset_version": "dv_example_1",
        "score": 0.65,
        "score_kind": "ordinal_rule_score",
        "score_source": "rules",
        "scorer_version": "rules-v1",
        "feature_version": "history-v1",
        "event_time_utc": "2026-01-01T10:00:00Z",
        "history_cutoff_exclusive_at": "2026-01-01T10:00:00Z",
        "scored_at": "2026-01-02T09:00:00Z",
        "history_coverage": {"state": "full", "start": "2025-12-31T10:00:00Z"},
        "explanation": {
          "status": "available",
          "method": "rules",
          "explained_scale": "risk_score",
          "feature_snapshot_digest": "sha256:example",
          "partial": false,
          "base_value": 0,
          "remainder": 0,
          "items": [{
            "feature_key": "sender_out_count_24h",
            "observed_value": "3",
            "unit": "transfers",
            "direction": "increases",
            "contribution": 0.35,
            "rule_condition": "prior sender outgoing count >= 3"
          }, {
            "feature_key": "receiver_in_count_24h",
            "observed_value": "3",
            "unit": "transfers",
            "direction": "increases",
            "contribution": 0.30,
            "rule_condition": "prior receiver incoming count >= 3"
          }]
        }
      }
    }

The two listed rule weights reconstruct the example score of 0.65. A
contract/semantic test must reject an additive explanation whose declared
base, items and remainder do not reconstruct its declared output.

## Error envelope

Dataset errors use the same outer shape as v1:

    {"error":{"code":"stale_snapshot","message":"Selected snapshot is no longer active."}}

Allowed dataset error codes are invalid_request, case_not_found,
stale_snapshot, run_unavailable and internal_error. Status/code mapping
is fixed in the endpoint table above. Message text is generic and bounded;
clients must not derive identity or failure semantics from free text.

## Consumer migration and review

Update the v2 producer and frontend decoder together. Preserve v1 schema,
FixtureScorer, fixture case ordering, existing cancellation/retry/empty/error
behavior and Foundation regression tests. The frontend currently sorts
case IDs in main.ts and always shows fixture/no-ML copy in views.ts; those
behaviors must become v1-only. Existing API client detail calls must pass
the v2 snapshot reference and handle 409/503 while retaining v1 calls.
Affected consumers review the new contract under
[foundation decisions](../../../docs/decisions/foundation.md) before
dependent implementation. Record actual reviewers/date only after review.
