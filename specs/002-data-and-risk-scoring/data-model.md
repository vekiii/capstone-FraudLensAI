# Data Model: Dataset, Risk Scoring and EDA

All records are local development artifacts unless explicitly designated as runtime output. Closed contracts reject unknown fields. Ground-truth visibility is stated per entity.

## Raw IBM transaction

One CSV row as source text, with `source_row_number: uint64` (1-based data row after header) and exact original field text. Preserve raw bytes/checksum separately. Expected named positions must be verified from the selected source revision; two `Account` columns are mapped by index into `sender_account_raw` and `receiver_account_raw`. Raw `Is Laundering` is restricted label material, never part of runtime transaction.

## Canonical transaction (restricted local dataset)

| Field | Type / rule | Notes |
|---|---|---|
| `transaction_id` | string, stable and unique | Derived deterministically from source file identity + source row number; no label-based component. |
| `source_row_number` | positive integer | Stable provenance/order tie-break. |
| `occurred_at_utc` | UTC instant at verified source precision | Explicit offsets normalize; timezone-naive policy recorded. |
| `sender_bank_id`, `sender_account_id` | exact nonempty source text | Leading zeros preserved. |
| `receiver_bank_id`, `receiver_account_id` | exact nonempty source text | Bank-qualified identities. |
| `amount_received` | nonnegative decimal text / canonical decimal | Precision verified from source; no float parsing for identity. |
| `receiving_currency` | source category string | Never merged with payment currency. |
| `amount_paid` | nonnegative decimal text / canonical decimal | As above. |
| `payment_currency` | source category string | Sender-side paid aggregation currency. |
| `payment_format` | source category string | Unknown values recorded/handled by frozen policy. |
| `is_laundering` | binary 0/1, restricted | Isolated label store/access layer; absent from public/runtime record. |

Canonical sender and receiver account keys are tuples `(bank_id, account_id)`, preserving exact text. Transaction IDs remain stable only for an identical source hash and row mapping; protocol stores the source hash.

## Historical feature vector

Ordered fields: eight FR-011 features, then frozen current-transaction features. Counts are nonnegative integers; distinct counterparties are counts over distinct bank-qualified counterparty keys; sums use decimal arithmetic and are currency-homogeneous. The history interval is `[t−24h,t)`, grouped by canonical account and side-specific currency for amount fields. No event at `t` contributes. Empty counts/sums are zero. Null or invalid required source fields reject the row rather than impute silently. Feature schema/version/hash is stored with each dataset snapshot and model.

| Feature | Formula |
|---|---|
| `sender_out_count_24h` | count earlier transactions with same sender key |
| `sender_distinct_receivers_24h` | distinct receiver keys among those rows |
| `sender_paid_count_same_currency_24h` | count those rows matching current payment currency |
| `sender_paid_sum_same_currency_24h` | sum their `amount_paid` in that payment currency |
| `receiver_in_count_24h` | count earlier transactions with same receiver key |
| `receiver_distinct_senders_24h` | distinct sender keys among those rows |
| `receiver_received_count_same_currency_24h` | count those rows matching current receiving currency |
| `receiver_received_sum_same_currency_24h` | sum their `amount_received` in that receiving currency |

T212 froze the current-feature tail as `current_amount_paid_log1p`, `current_payment_currency`, `current_payment_format`, following the eight historical fields in exactly that order under `hi-small-temporal-v1`. The [protocol](protocol.md#t212-frozen-temporal-feature-contract-2026-11-19) specifies the Decimal-to-log transform, source precision, missing-value rejection and train-only categorical vocabularies with reserved unknown buckets. Currency remains a categorical identity, not a conversion factor. Implementation and stored feature-schema hash remain pending T213/T219.

## Dataset manifest

`manifest_version`, dataset/source/release, acquisition timestamp/method, source URL/license text reference, source filename/size/SHA-256, schema/header positional map, parser/code revision, config hash, UTC/timezone policy, source/accepted/rejected counts and rejection counts by reason, warm-up/scoreable counts, timestamp min/max, category counts, restricted label audit reference, processed file names/sizes/hashes, checkpoint hashes, and completion state. Incomplete staging manifests cannot be consumed by training or scoring.

## Chronological partition

`partition_id ∈ {development, showcase, train, validation, test}`; UTC start/end instants and inclusivity, row count, scoreable count, timestamp-group boundary, scoreable-ID hash, and parent partition. Development/showcase are contiguous by source-row cumulative boundary at whole timestamp. Train/validation/test divide scoreable development rows 70/15/15. Partition entities carry counts and hashes; labels are not fields. Allowed aggregate label audit is stored separately with query log and approval reference.

## Frozen training protocol and model metadata

Protocol fields: dataset/source hash; time/warm-up rules; exact partition boundaries, counts/hashes and allowed prevalence summary; feature schema/version; seed 42; tie rules; training preprocessing; class strategy; fixed candidate grid; metrics; threshold objective; resource ceilings; label access policy; showcase role; protocol hash and freeze timestamp. No model fitting until protocol validates.

Model metadata fields: `model_id`, model type/config, model artifact format/version/hash, preprocessing hash, Python and dependency versions, training-code revision, dataset/protocol/partition hashes, feature order/version, seed, selected validation AP/P@20/simplicity rationale, validation threshold and method, calibration status, permitted evaluation references, and creation time. Never embed record-level labels in runtime metadata.

## Prediction result (runtime)

| Field | Type / constraint |
|---|---|
| `transaction_id` | opaque stable string; must match request |
| `risk_score` | finite number in `[0,1]`; not called probability absent calibration evidence |
| `review_status` | `review_recommended` or `below_threshold` from frozen threshold |
| `source` | `fixture`, `rules`, or `model` |
| `model_version`, `feature_version` | nonempty identifiers; fixture may identify fixture scorer |
| `scored_at` | RFC3339 UTC |
| `explanation` | bounded text, observed facts and defensible values only |
| `eligibility` | eligible result only; ineligible requests use explicit error contract |

No `is_laundering`, label, target-derived indicator or analyst conclusion appears in this or transaction UI model.

## Evaluation summary

Partition and authorization reference; model/protocol hashes; metric names/values/denominators; prevalence; threshold; confusion counts; top-k precision/recall; PR curve points (bounded); daily alert counts; calibration status; synthetic-data caveat; execution evidence reference. No record-level IDs/labels in public summary. Test summary exists only after explicit authorization.

## EDA summary and chart series

Summary: dataset version, snapshot time, UTC range, source/accepted/rejected/warm-up/scoreable counts, quality categories and bounded categorical counts. Public summary excludes target distribution. Chart series have `series_id`, `label`, `unit`, `bucket_labels`, numeric `values`, denominator definition, currency (required for monetary values), UTC timezone where applicable, and bounded point/category count. No transaction row, account identifier, target label, or label-derived prevalence is included.
