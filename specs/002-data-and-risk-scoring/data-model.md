# Feature 002 data model and invariants

Status: team-approved identity/mapping direction; Phase 3 import and Phase 4
`history-v1` replay, v2 scorer boundary and rules-only scoring are implemented.
Protocol, trained-model scoring and public v2 integration remain later work.
Source-specific mappings are frozen only after the authorized IBM file audit
and confirmation of final bytes by the responsible reviewers. Public wire details are in
[contracts/api.md](contracts/api.md) and [contracts/schemas.json](contracts/schemas.json).

Technical amendment, 2026-11-13: pinned Kaggle v8 member equivalence is verified
and adopted as the reproducible reference; original acquisition history remains
unknown. [Current mapping](../../data/mappings/ibm_hi_small_v1.json) retains
the historical `pending_team_review` and `import_allowed=false` inspection
flags; separate final-byte team approval and the source-bound CLI gate govern
the implemented import without inventing an individual reviewer.
User-approved clock interpretation is an explicit fixed UTC+00 synthetic analysis
assumption, not a source timezone fact. Source/raw minute text and equal-time
groups remain intact. The policy hash is recorded in the mapping. The team's
2026-11-13 technical decision and calculated working mapping hash are recorded outside
the mapping in [the T007/T008 review record](../../evidence/tasks/feature-002-t007-t008-team-review-2026-11-13.md).
The historical inspect mapping flag remains false; the separately approved,
source-bound local import CLI is available as recorded in the Phase 3 evidence.

## Identity and version rules

- **SourceRowRef:** one-based CSV record ordinal assigned before validation;
  a quoted multiline record is one record, not several physical lines.
  For a multi-file release, include a declared member key. A source row can
  produce one event, one event rejection, or a file-level failure that leaves
  the import incomplete.
- **Source namespace and member:** `N` is exactly the UTF-8 encoding of
  mapping `source.namespace`; `F` is exactly the UTF-8 encoding of mapping
  `source.member`. The member is encoded separately and is not appended to N.
  Neither value can be inferred from a target label. A changed event fact under the
  same namespace/row key is a collision requiring review, not a silent update.
- **Transaction/Case IDs:** encode N and F without Unicode normalization or
  case folding. Let `o` be the one-based pre-filter CSV record ordinal
  (1..2^64−1). `I = U32BE(len(N)) || N || U32BE(len(F)) || F || U64BE(o)`;
  lengths count bytes, each is an unsigned four-byte big-endian integer, and
  ordinal is an unsigned eight-byte big-endian integer. Namespace/member must
  be nonempty and fit U32. `D = "D" || lowercase_hex(SHA256(
  ASCII("FraudLensAI/tx/v1") || 0x00 || I)[0:16])` and
  `C = "C" || lowercase_hex(SHA256(ASCII("FraudLensAI/case/v1") ||
  0x00 || I)[0:16])`. The 16-byte digest prefix gives exactly 32 lowercase
  hex digits after each letter; retain the full 32-byte digest, framed input
  and label-free event-fact digest locally to detect collisions or changed
  facts under one row identity. Never silently overwrite a collision.
  These opaque URL-safe keys exclude accounts, labels, raw source hash and
  accepted-row position. Equal-valued distinct rows retain distinct IDs.
- **DatasetVersion ID:** `S = SHA256(exact original CSV bytes)`,
  `M = SHA256(NormalizeLF(exact mapping-file bytes))`, and `T` is the
  existing time-policy digest defined below. Use the three full 32-byte
  digests, not their hexadecimal text: `"dv_" || lowercase_hex(SHA256(
  ASCII("FraudLensAI/dataset-version/v1") || 0x00 || S || M || T))`.
  Fixed 32-byte widths require no added delimiters. The `dv_` suffix is
  all 64 lowercase hex digits. A label-only edit changes S/dv_ while D/C
  and observable facts stay fixed; edited IBM v8 bytes fail its pinned
  original-source SHA-256 check and cannot be imported as that release.
- **Run ID:** unique local execution identifier. Reproduction compares
  semantic fingerprint, predictions and metrics rather than requiring
  wall-clock execution timestamps or run IDs to match.
- **Snapshot reference:** the active run ID in v2 responses. Detail lookup
  requires that reference and succeeds only while it still names the active
  complete run. A switch yields a controlled stale-snapshot error.

`NormalizeLF` requires strict UTF-8 without a BOM, rejects bare CR bytes,
then replaces each CRLF byte pair with LF; it preserves all other bytes,
including JSON spacing, key order, status fields and final newline. JSON
validity and duplicate-key rejection are separate prerequisites. `T` is
SHA-256 of `time.selected_policy` serialized as UTF-8 JSON with sorted keys,
compact comma/colon separators and ASCII escaping (`ensure_ascii=True`),
as in the existing inspector. The current `T` is
`67a408fc52e57035115186c3c9863dfeac5a72d709292e0f7baeef560086d781`.
The separate review record records the approved `M`; its own bytes are never
hashed into M. A later mapping-content change requires a new M and new review
before import.
The raw Git blob SHA-256 is a byte-level revision identifier and may differ
from M for CRLF files. [Vectors for the previous and current mappings](../../evidence/tasks/feature-002-t007-t008-team-review-2026-11-13.md#identity-vectors)
fix the exact recipe without claiming importer execution.

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
| event_time_utc, event_time_epoch_ns | Lossless interpreted time coordinate and sortable integer nanoseconds under the selected policy. For assumed_utc_for_synthetic_benchmark this is a fixed UTC+00 analysis coordinate, not verified source UTC; minute `:00` padding does not claim second-level measurement. If source precision cannot be represented losslessly, block mapping/import until resolved. |
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
