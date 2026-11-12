# Feature 002 data model and invariants

Status: technical design, not implemented. Source-specific mappings are frozen
only after the authorized IBM file audit. Public wire details are in
[contracts/api.md](contracts/api.md) and [contracts/schemas.json](contracts/schemas.json).

## Identity and version rules

- **SourceRowRef:** one-based CSV record ordinal assigned before validation;
  a quoted multiline record is one record, not several physical lines.
  For a multi-file release, include a declared member key. A source row can
  produce one event, one event rejection, or a file-level failure that leaves
  the import incomplete.
- **Source namespace:** reviewed release identifier plus source member. It
  cannot be inferred from a target label. A changed event fact under the
  same namespace/row key is a collision requiring review, not a silent update.
- **Transaction ID:** prefix D followed by 32 lowercase hexadecimal digits,
  the first 128 bits of SHA-256 over a length-delimited source namespace,
  member, and source-row ordinal. **Case ID:** prefix C with the same digest
  input plus a distinct domain separator. Full input is retained locally
  for collision checks. These IDs are opaque URL-safe keys, not source
  accounts or labels. A same-file reimport yields the same IDs; equal-valued
  distinct rows remain distinct.
- **DatasetVersion ID:** prefix dv_ plus a digest of the raw content SHA-256,
  mapping hash and time-policy hash. Unlike transaction ID, this changes
  when a label-only file edit changes raw content. The underlying event
  identity can remain stable, and histories must remain unchanged.
- **Run ID:** unique local execution identifier. Reproduction compares
  semantic fingerprint, predictions and metrics rather than requiring
  wall-clock execution timestamps or run IDs to match.
- **Snapshot reference:** the active run ID in v2 responses. Detail lookup
  requires that reference and succeeds only while it still names the active
  complete run. A switch yields a controlled stale-snapshot error.

The digest scheme is a proposed reviewed contract choice. Do not implement
it before the source audit confirms a stable source namespace/member/row
reference. The full SHA-256 is checked for collisions even though public IDs
are shorter. No target label, raw file hash or accepted-row position appears
in the transaction/case identity input.

## DatasetVersion

| Field | Meaning / validation |
|---|---|
| dataset_version | Stable digest of source content and reviewed mapping/time policy; unique in local store. |
| source_name, release_id, member | Declared local IBM AML HI-Small distribution and file member; no secret URL/token. |
| source_sha256, source_size_bytes | Hash/size of unmodified local source. |
| license_reference | Reviewed source-data license reference, distinct from repository code license. |
| mapping_version, mapping_sha256, time_policy | Exact mapping/parse policy used for this import. |
| observed_schema, time_span, currencies | Results of actual source audit, never populated from assumptions. |
| status | staged, complete, failed; only complete is selectable. |
| imported_at, row_counts | Actual execution time and report reference. |

Different source or mapping versions coexist by ID; no operation overwrites a
complete version. An incomplete import is invisible to dataset selection.

## ImportReport and row accounting

For each CSV record, record a source-row reference and one event status:
event_valid or event_rejected with a reason. Event-valid rows receive one
private label status: eligible_positive, eligible_negative, missing, invalid
or unsupported. The exact source label mapping is part of the reviewed
mapping. Counts obey:

    source_records = event_valid + event_rejected
    event_valid = label_eligible + label_ineligible
    label_eligible = positives + negatives

File-level parse failure before a trustworthy total row count marks the whole
attempt failed; it cannot publish a partial report as a complete import.
The report also records duplicate/unknown headers, field mapping, missingness,
timestamp/currency coverage, rejected reasons, class denominator and examples
sanitized of sensitive paths/values. Unknown fields are never predictors by
default. Raw source remains unchanged.

## CanonicalTransaction

Operational projection, with no target or label-validity field:

| Field | Meaning / validation |
|---|---|
| transaction_id, dataset_version, source_row_ref | Stable identity and provenance; source-row reference stays internal. |
| event_time_raw | Exact source timestamp text. |
| event_time_utc, event_time_epoch_ns | Lossless interpreted UTC time and sortable integer nanoseconds under the reviewed policy. If source precision cannot be represented losslessly, block mapping/import until resolved. |
| sender_bank, sender_account | Nonempty source values preserved with reviewed normalization; qualified join key is derived with unambiguous length-delimited encoding. |
| receiver_bank, receiver_account | Same, separately directed; never swapped or inferred. |
| paid_amount, paid_currency | Exact nonnegative decimal text and source currency. No binary float or FX conversion in canonical storage. |
| received_amount, received_currency | Separate exact decimal/currency; never collapsed into paid values. |
| payment_format | Optional source value only when actually present and reviewed. |
| event_fact_digest | Digest of normalized observable facts, excluding label, for cross-version collision checks. |

The mapping declares supported decimal scale/magnitude, zero policy, currency
syntax, timestamp timezone/granularity and optional field behavior after
source inspection. Unsupported/nonfinite/negative/overflowing input receives
a row rejection reason, not a rounded value. Event time, feature cutoff and
actual scored time are separate fields in downstream records.

## PrivateEvaluationLabel

Keyed by dataset version and transaction ID, stored in a private table read
only by offline fit/evaluation code. Fields: label value (0/1 when eligible),
eligibility/reason, source-row reference, and source label mapping version.
The operational repository, ScoreRequest, feature snapshot, explanation,
public API and UI models do not contain this entity. An event with an invalid
label can still contribute its observable facts to history.

## FeatureDefinition and HistoricalFeatureSnapshot

The versioned catalog gives each feature a key, meaning, input fields,
availability time, lookback [t−24h,t), direction, unit/currency, null/unknown
semantics, lineage, and visibility to rule/model/UI. Initial catalog:

| Feature key | Meaning and type |
|---|---|
| sender_out_count_24h | Integer count of earlier outgoing events for the bank-qualified sender. |
| sender_distinct_receivers_24h | Integer distinct bank-qualified receivers in earlier sender outgoing history. |
| sender_paid_count_same_currency_24h | Integer count of earlier sender outgoing paid amounts with current paid currency. |
| sender_paid_sum_same_currency_24h | Exact Decimal sum in current paid currency; mean is sum/count only when count > 0. |
| receiver_in_count_24h | Integer count of earlier incoming events for the bank-qualified receiver. |
| receiver_distinct_senders_24h | Integer distinct bank-qualified senders in earlier receiver incoming history. |
| receiver_received_count_same_currency_24h | Integer count of earlier receiver incoming received amounts with current received currency. |
| receiver_received_sum_same_currency_24h | Exact Decimal sum in current received currency. |
| current_paid_amount, current_paid_currency | Current observable paid side, preserving unit; float/model transform occurs only after canonical validation. |
| current_payment_format | Optional categorical value if actual source mapping supports it; otherwise absent from the frozen feature schema. |

Snapshot fields: transaction ID, dataset/feature version, event time, as-of
cutoff, coverage_start, coverage_state (full, incomplete, unavailable),
typed feature values, currency units, feature-input digest and creation time.
The first 24h of source observation is context-only warm-up. After that
point, a new account can have a measured zero; missing prior source coverage
is never represented as a measured zero. All events at one timestamp use
the same earlier history, then update later history as a group.

## RulePolicy and ScorerArtifact

**RulePolicy v1** has the three conditions/weights in research.md, a score
aggregation rule, comparison boundaries, missing-feature treatment, reason
templates and a policy hash. It is frozen before evaluation. Rules accept
only current canonical facts and the matching feature snapshot.

**ScorerArtifact** stores scorer source (rules/model), version, exact feature
schema and transform version, training/data/protocol references, selected
hyperparameters/seed, calibration status, local artifact path and SHA-256
where applicable, dependency versions and trusted-origin record. Loading
an artifact with a mismatched hash, schema, dataset role or version fails.
The fixture scorer is a separate Foundation v1 artifact-free mode.

## SplitManifest and EvaluationProtocol

Manifest fields: dataset version, observable benchmark-view rule, warm-up
cutoff, whole-timestamp train/validation/test boundaries, exact transaction
IDs and class/eligibility counts per partition, protocol hash and freeze
time. The split algorithm chooses nearest 70/15/15 row counts with whole
timestamp groups, breaking equal-distance choices toward the earlier
boundary. Boundaries are chosen before target labels are joined; class
counts are then checked for eligibility.

Protocol fields: feature allowlist/lineage, candidate grids, seed, train-only
transform policy, validation AP/P@K/simplicity selection, AP tolerance,
calibration role (initially none), K=20, per-scorer validation F0.5 threshold
policy, positive label 1, metric implementation/dependency version,
resource budget and holdout disclosure status. Training labels fit
supervised models; validation labels select/tune; test labels join only
frozen predictions. A consumed holdout can be reused only with
exploratory status.

## ScoreRequest, RiskAssessment and Explanation

ScoreRequest contains one CanonicalTransaction, matching
HistoricalFeatureSnapshot, dataset version, run ID, scorer version and
feature as-of cutoff. It has no label. The scorer validates identity,
schema and coverage before returning an assessment.

RiskAssessment contains transaction/run/dataset identity, source
(rules/model), finite score in [0,1], score interpretation
(ordinal_rule_score or uncalibrated_probability_estimate or
calibrated_probability), scorer/feature/artifact versions, event/as-of/
actual scored times, and a matching Explanation or explicit unavailable
reason. Never clamp a bad score.

Explanation stores method, explained output scale, exact input snapshot
digest, up to three strongest items with observed value/unit/direction and
contribution/condition, plus base/remainder when additive reconstruction
is claimed. Rule items cite fired conditions and weights. Linear model
items explain log odds, not the displayed sigmoid score; tree path items
explain positive-class leaf output. A top-three subset is labeled partial
unless base/remainder permit exact method-specific reconstruction.

## ScoredRun, ReviewCaseSnapshot and EvaluationReport

ScoredRun fields: unique run ID, semantic fingerprint, dataset/feature/scorer/
artifact/protocol references, frozen threshold policy/value, score population
count, alert count, status (staging, completed, failed), created/completed/
activated times, artifact hashes and validation summary. Rows and
assessments are immutable after completed. A failed run cannot activate.

ReviewCaseSnapshot contains one stable case ID per threshold alert, its
transaction ID, run ID, immutable assessment reference, event time, rank
used for display selection, total alert count, displayed count, selected
time range and truncation. Select most recent 100 by descending event
time and ascending transaction ID at ties; display selected rows in
ascending event time/ID. An alert that vanishes under a later scorer
vanishes from the active list, while its stable case ID remains reserved
for that source event.

EvaluationReport stores exact row IDs/denominators, baseline/model
predictions and metrics, tie groups, scorer-specific thresholds/alert
counts, Brier/reliability status where model output is a probability
estimate, uncertainty status/limits, class and seen/unseen-account
coverage, machine/time/resource facts, hashes, test-holdout disclosure
state and limitations. It is separate from public case payloads.

## State transitions and invariants

    DatasetVersion: staged -> complete | failed
    ScoredRun: staging -> completed | failed
    ActiveRunPointer: none | one completed run ID

Only complete imports may feed a run. Only a completed run may become
active. Active pointer replacement and its visibility happen atomically.
On process failure before activation, the old pointer remains unchanged.
At read time, both list and detail bind one complete active run; detail
requires the list's snapshot reference and returns stale-snapshot when
it no longer matches. No public projection contains PrivateEvaluationLabel.
