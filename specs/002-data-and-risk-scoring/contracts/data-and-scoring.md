# Feature 002 offline and scoring interfaces

Status: team-agreed technical direction from the 2026-11-13 decision,
communicated by the user. Pinned v8 source equivalence and reference-implementation
semantics are verified. This document specifies the boundaries tasks must
implement; it is not executable code or evidence of a trained model.
See [data-model.md](../data-model.md) for entity invariants and
[api.md](api.md) for public read responses.

## Local command interface

One backend module, provisionally fraudlens.pipeline_cli, exposes these
subcommands. Exact Python argument parser/library is an implementation
choice. Every command writes a small machine-readable result and a concise
human summary, returns nonzero on controlled failure, and never prints
secrets, row-level private labels, stack traces or full raw rows by default.
Aggregate label counts are allowed in the private inspection report.
The source path and local store/artifact root are explicit arguments or
settings; no download occurs at application startup.

| Command | Inputs | Output/side effect | Failure behavior |
|---|---|---|---|
| inspect | Local source path, declared release, source-data license reference | Read-only source/data card: hash, schema, dialect/encoding, types, row/label/time/currency observations and ambiguities | Invalid/inaccessible source or ambiguous parsing => nonzero; no active version changes |
| import | Local `--source`, `--mapping`, `--namespace`, `--expected-sha256`, `--store` | Staged then completed DatasetVersion, ImportReport, canonical event facts and private labels | File/structural or processed-byte hash/size mismatch => failed attempt, no active incomplete import; row-level rejection counted |
| build-features | Completed dataset version, frozen feature version | Point-in-time snapshots and coverage report | Any identity/time/feature mismatch => incomplete output, no scorer publication |
| freeze-protocol | Dataset/feature version and reviewed protocol configuration | Immutable SplitManifest/EvaluationProtocol and eligibility report | Ineligible classes/positives => explicit ineligible report; no fit or test metric |
| evaluate | Frozen protocol ID | Training/validation selection, frozen predictions, one final test comparison/report and holdout-consumed record | Failed candidate or missing artifact => explicit incomplete report, no fabricated improvement |
| score-run | Completed dataset, feature/scorer/artifact version and frozen threshold | Label-free staged ScoredRun and ReviewCaseSnapshot, completed after validation | Failure => no active pointer change |
| activate-run | Completed run ID | One atomic active pointer update after compatibility/hash checks | Missing/incomplete/incompatible run => no pointer change |
| reproduce | Report/protocol ID and matching local source/artifacts | Recomputed prediction/metric comparison under frozen tolerance | Missing hash/version or divergence => explicit failure and difference report |

`inspect` and source-bound `import` are executable in Phase 3; the other
command names are stable planning targets. Do not expose import, fit,
evaluation or activation through the analyst HTTP API.

## Reviewed source mapping contract

The mapping is a small versioned configuration tracked in Git only after
the real source audit. It binds abstract roles to observed source headers:
event timestamp; sender bank/account; receiver bank/account; paid and
received amount/currency; optional payment format; and private target
label. It records CSV encoding/dialect, header normalization and aliases,
unknown-column policy, decimal magnitude/scale/zero handling, currency
syntax, timestamp format/timezone/precision, label mapping and source
namespace/member. Duplicate headers after normalization block processing except
the exact, user-approved source-bound HI-Small Account occurrences at positions
2 and 4: the complete eleven ordered raw headers, member, source SHA-256 and
verified v8 reference binding must all match. Every other normalized collision,
alias, missing/extra field, reorder or target-like extra stops processing.
The current inspector can observe this exact pair through the pending mapping;
that exception does not satisfy the team-review/import gate. Missing required
roles, ambiguous aliases and unreviewed target-like columns block import.
Unknown fields are reported but never included as predictors without an
explicit mapping revision.

The final reviewed mapping's normalized SHA-256 contributes to DatasetVersion. A modified mapping
never silently overwrites a completed import. The importer assigns a
source-row reference before applying event or label validation. A valid
event with invalid label remains available to history and is excluded
from fit/evaluation.

### Exact identity and version bytes

The separate [team review record](../../../evidence/tasks/feature-002-t007-t008-team-review-2026-11-13.md)
records the current candidate mapping hash and vectors. For nonempty reviewed namespace
and exact member name, encode each as UTF-8 without Unicode normalization or
case folding. Let `I = U32BE(namespace byte length) || namespace bytes ||
U32BE(member byte length) || member bytes || U64BE(pre-filter CSV ordinal)`.
The lengths are unsigned four-byte big-endian values; the one-based ordinal is
unsigned eight-byte big-endian, valid 1..2^64−1. A multiline quoted record
counts once. `D` is `D` plus the lowercase hex of the first 16 bytes of
`SHA256(ASCII("FraudLensAI/tx/v1") || 0x00 || I)`; `C` is `C` plus the same
16-byte prefix of `SHA256(ASCII("FraudLensAI/case/v1") || 0x00 || I)`.
The public suffix is 32 lowercase hex digits. Retain each full digest, framed
input and label-free fact digest for collision/changed-fact detection; fail
instead of overwriting. Neither label nor source-file hash enters D/C.

For `DatasetVersion`, let `S` be SHA-256 of the exact original CSV bytes,
`M` be SHA-256 of the complete mapping file's UTF-8 bytes after CRLF-to-LF
replacement, and `T` be the existing selected time-policy SHA-256. Mapping
normalization rejects BOM or bare CR, keeps every other byte and never
reserializes JSON. `T` uses UTF-8 JSON of `time.selected_policy`, sorted keys,
compact comma/colon separators and ASCII escaping (`ensure_ascii=True`).
Use the full 32-byte digests in order: `dv_` plus all 64 lowercase hex digits
of `SHA256(ASCII("FraudLensAI/dataset-version/v1") || 0x00 || S || M || T)`.
No hex text or added framing is inserted between these fixed-width digests.
The separate review record is excluded from M. A mapping-content change
requires a new M and new review before import; changed IBM v8 CSV bytes fail
the pinned source SHA-256 even if only a private label changed.

### Team-approved HI-Small technical policy; source-bound local import

The current configuration is [ibm_hi_small_v1.json](../../../data/mappings/ibm_hi_small_v1.json).
The file retains the historical pending inspection configuration:
`pending_team_review`, `executable_mapping=false`, `import_allowed=false`;
the read-only `inspect` command still reports those fields. Its historical null
review fields are not individual approvals. The later collective final-byte
approval, source, date and exact M live in the separate review record. The local
`import` CLI requires that approval and a matching source SHA-256, namespace,
member, size, mapping M and time policy before staging. This source-bound
authorization does not turn the mapping's flags into general import permission.
The importer also verifies the hash and size of the bytes fed to the CSV parser
before completing and activating a new DatasetVersion.

Verified reference: Kaggle v8 HI-Small_Trans.csv, SHA-256
`b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`.
Original acquisition history stays unknown. Accounts remain exact separate
bank/account strings; source-bound position 2 is sender, position 4 receiver.
Paid/received amounts use Decimal text, at most 13 integer and 6 fractional
digits, supported scales 0–6, zero allowed as a design policy (not observed).
Currencies remain the fifteen exact source names, maxLength 17; no FX/ISO coercion.
Values outside the selected policy are rejected explicitly. Optional payment
format values remain source-backed; unknown categories require mapping review.
Binary labels are private: 1=synthetic laundering, 0=synthetic non-laundering,
supported by the publisher's reference implementation. Missing/invalid labels
make only supervised use ineligible; valid observable facts remain available.

Source timezone is unknown. The user-approved analysis policy is
synthetic-common-wall-clock-fixed-offset-zero-v1, basis
assumed_utc_for_synthetic_benchmark. It assigns minute coordinates at fixed +00:00
without claiming source UTC, clock synchronization or lifecycle semantics.
Preserve raw time/minute ties; do not use host-local timezone. Policy hash is
SHA-256 of canonical UTF-8 JSON (sorted keys, separators comma/colon), recorded
in the configuration. The inspector reports the raw mapping file SHA-256;
the normalized M used for DatasetVersion is recorded in the separate final-byte
review. These differ for CRLF files. Phase 3 local import is implemented;
feature building and training remain later work.

## ScoreRequestV2 and ScorerV2

The dataset scorer boundary is separate from Foundation's
Scorer.score(Transaction) -> RiskAssessment. Its request contains:

    ScoreRequestV2:
        canonical_transaction: CanonicalTransaction
        feature_snapshot: HistoricalFeatureSnapshot
        dataset_version: string
        run_id: string
        scorer_version: string
        feature_version: string
        history_cutoff_exclusive_at: timestamp

    ScorerV2.score(request: ScoreRequestV2) -> RiskAssessmentV2

Before scoring, verify matching transaction/dataset/feature/as-of IDs,
known feature schema, scoreable coverage and trusted scorer artifact.
The request, scorer object and response contain no target label or
label-eligibility flag. Copy/validate request data across the boundary
so an injected scorer cannot mutate it. Reject a response with a changed
transaction/run, nonfinite or out-of-range score, incompatible artifact,
wrong explanation input digest or unexpected fields. Do not clamp a
score or substitute fixture/rules/model output on failure.

The rule implementation returns ordinal_rule_score and actual fired
conditions. The initial logistic/tree model returns
uncalibrated_probability_estimate: the display calls it a risk score and
does not claim calibration. Optional future calibration requires a
new frozen artifact/protocol with separate fit/check roles and a
calibrated_probability score_kind only after independent evidence.

## Feature replay contract

The input is the completed import's event-valid facts, including facts
whose labels are ineligible. The output is exactly one feature snapshot
per event or an explicit unscoreable warm-up/coverage state. Replay is
deterministic under input-row permutation. Use interpreted UTC event time
and a half-open [t−24h,t) window. All events tied at t use the same
history from times strictly earlier than t. Only after every tied event
has a snapshot do their observable facts update later history.
Future events, same-time peers, labels and label-validity indicators
cannot affect the snapshot. Prior validation/test facts can affect
strictly later events after their time; their labels cannot.

The first 24h from observed source start are context-only warm-up and
are excluded from the scoreable benchmark view under the initial policy.
If source span/eligibility makes that impossible, freeze a documented
prospective amendment before fit/selection; never pick a policy by
favorable final-test metrics.

## RulePolicy v1

All conditions use the matching current canonical transaction and
HistoricalFeatureSnapshot. The version is frozen before label inspection:

| Rule | Observable condition | Contribution | Unavailable behavior |
|---|---|---:|---|
| R1 sender velocity | sender_out_count_24h >= 3 | 0.35 | Incomplete history => unscoreable; full-history cold start count 0 => not fired |
| R2 receiver velocity | receiver_in_count_24h >= 3 | 0.30 | Same coverage rule as R1 |
| R3 paid amount relative to sender history | sender_paid_count_same_currency_24h >= 3 and current paid amount >= 2 × (sender_paid_sum_same_currency_24h / count) | 0.35 | If count < 3, comparison unavailable/not fired, with reason |

Score is the exact sum of fired contributions, finite in [0,1].
Use Decimal comparisons before any display conversion. The score is an
ordinal heuristic, not a calibrated probability or guilty finding.
Reason payloads include the actual observed count/amount/currency,
condition, threshold, contribution and rule version. A zero score
with complete coverage says no declared rule fired, not that risk
is proven absent.

## Evaluation protocol contract

The protocol is immutable before fitting. It records:

- Observable scoreable benchmark view and exact whole-timestamp
  70/15/15 split IDs/times, with class/label eligibility counts joined
  afterward. Both classes must occur in train, validation and test;
  outer validation/test need at least 20 positives each.
- Explicit role table: train labels for supervised fitting and all
  learned transforms; validation labels for candidate/hyperparameter
  selection and per-scorer threshold choice; no calibration fit/check
  initially; test labels only for final metrics after predictions freeze.
- Feature allowlist/lineage and rejected target/identifier/source-order/
  full-file aggregate proxies. Categorical unknown handling is frozen.
- Candidate grid: L2 logistic regression C 0.1/1.0; tree depth 3/5
  and min leaf 100/500; seed 42; at most six fits. Validation
  winner: AP, then Precision@K if AP difference <=1e-6, then
  logistic regression before tree and shallower tree first. Exact
  fit/transform/dependency versions and pilot resource budget recorded.
- K=min(20, eligible partition size). Rank descending score, then
  ascending stable transaction ID. Report any tie crossing K.
  Recall@K denominator is every positive eligible row.
- For each scorer, candidate thresholds are distinct validation scores
  with inclusive comparison plus a symbolic no-alert choice.
  Preserve tied scores. Keep thresholds with <=20 validation alerts;
  maximize validation F0.5, then fewer alerts, then higher threshold.
  F0.5 for no predictions is zero. Freeze each scorer's selected
  threshold/no-alert choice before test scoring. Test alert count may
  exceed 20 and must be reported.
- Average Precision is the pinned scikit-learn non-interpolated
  implementation with positive label 1. Report prevalence, P@K,
  Recall@K, TP/FP/TN/FN, precision/recall at frozen threshold and
  alert rate on identical eligible IDs for rules and model.
  For model probability estimates, report Brier and feasible reliability
  table with explicit uncalibrated status; never label rule scores
  probabilities. Report exact counts and uncertainty limitations.

The protocol records a frozen hash and whether final holdout labels
have been disclosed. A changed protocol after disclosure can run only
as exploratory against that consumed holdout; it cannot produce a
new confirmatory claim. No retraining or threshold adjustment uses
the final test result.

## Artifact and run publication contract

Model artifacts are local/ignored, created by the reviewed training
command and accompanied by a manifest with SHA-256, source/protocol/
feature/transform/dependency/scorer versions and expected input schema.
Before deserializing, confirm path containment under the trusted local
artifact root, hash and compatibility. A pickle-derived file is
executable if untrusted: never accept uploads or arbitrary external
paths. An invalid artifact fails closed; fixture mode remains independent.

ScoredRun is staged with its complete score/assessment set and
threshold-selected alert cases. Validate unique event/case IDs,
finite scores, run/dataset/feature/artifact references, explanation
identity/scale, alert count and deterministic latest-100 selection.
Then mark complete and activate by one SQLite transaction updating
the active pointer. The API never reads staging rows. Mid-run failure,
restart or failed activation leaves the previous active complete run
unchanged. A selected run's list/detail responses must agree; a
superseded snapshot reference yields 409 stale_snapshot.
