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

`inspect`, source-bound `import`, and local `build-features` are executable;
the other command names are stable planning targets. `build-features` requires
an existing complete, provenance-compatible DatasetVersion and writes
`history-v1` snapshots to the selected SQLite store. A repeated complete build
returns `repeated=true` without rebuilding. Do not expose import, fit,
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
review. These differ for CRLF files. Phase 3 local import and Phase 4 local
feature building are implemented; protocol freezing and training remain later work.

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
conditions. An available rule explanation must use `method=rules`,
`explained_scale=risk_score` and reconstruct the returned score from its
Decimal base, contributions and remainder; an inconsistent response is
rejected. The later logistic/tree model returns
uncalibrated_probability_estimate: the display calls it a risk score and
does not claim calibration. Optional future calibration requires a
new frozen artifact/protocol with separate fit/check roles and a
calibrated_probability score_kind only after independent evidence.

## Feature replay contract

### Frozen `history-v1` catalog

The replay input is only event-valid canonical operational facts from a
**complete** DatasetVersion. The private label table and its eligibility are
outside this interface. `J_s=(sender_bank,sender_account)` and
`J_r=(receiver_bank,receiver_account)` are exact bank-qualified join keys;
the two source strings remain separate and are never converted to a predictor.
For an event at interpreted time `t`, `H(t)` contains only event-valid facts
whose times satisfy `t−24h <= event_time < t`, in the same DatasetVersion.
The catalog below is frozen as `history-v1`. Each historical row is computed
from `H(t)`; `current_*` values come from the current validated event at `t`.
All values are available immediately before scoring that event at `t` (the
current fields at event observation, history after the prior time group has
been applied). No future or same-time fact is available.

| Exact feature key | Canonical input fields and direction / calculation | Unit | Permitted consumer; missing or unknown meaning |
|---|---|---|---|
| `sender_out_count_24h` | Current `J_s`; count prior outgoing events with the same `J_s` in `H(t)`. | Integer events | R1, model, rule explanation. Full coverage with no matches = measured `0`; incomplete/unavailable coverage = null, never zero. |
| `sender_distinct_receivers_24h` | Current `J_s`; count distinct prior `J_r` pairs among that sender's outgoing events in `H(t)`. Same account text at different banks is distinct. | Integer bank-qualified counterparties | Model and approved explanation; no R1–R3 condition. Full empty history = `0`; deficient coverage = null. |
| `sender_paid_count_same_currency_24h` | Current `J_s`, `paid_currency`; count prior outgoing events for `J_s` whose `paid_currency` exactly equals the current paid currency. | Integer events in the named paid currency | R3, model, rule explanation. Full empty/mismatched history = `0`; deficient coverage = null. |
| `sender_paid_sum_same_currency_24h` | Sum exact Decimal text `paid_amount` from the same prior rows selected by `sender_paid_count_same_currency_24h`; no FX or float conversion. | Decimal amount in current `paid_currency` | R3, model, rule explanation. Full zero matches = exact Decimal `0` with that currency; deficient coverage = null. |
| `receiver_in_count_24h` | Current `J_r`; count prior incoming events with the same `J_r` in `H(t)`. | Integer events | R2, model, rule explanation. Full empty history = `0`; deficient coverage = null. |
| `receiver_distinct_senders_24h` | Current `J_r`; count distinct prior `J_s` pairs among that receiver's incoming events in `H(t)`. | Integer bank-qualified counterparties | Model and approved explanation; no R1–R3 condition. Full empty history = `0`; deficient coverage = null. |
| `receiver_received_count_same_currency_24h` | Current `J_r`, `received_currency`; count prior incoming events for `J_r` whose `received_currency` exactly equals the current received currency. Do not compare to `paid_currency`. | Integer events in the named received currency | Model and approved explanation; no R1–R3 condition. Full empty/mismatched history = `0`; deficient coverage = null. |
| `receiver_received_sum_same_currency_24h` | Sum exact Decimal text `received_amount` from the same prior rows selected by `receiver_received_count_same_currency_24h`; no FX or float conversion. | Decimal amount in current `received_currency` | Model and approved explanation; no R1–R3 condition. Full zero matches = exact Decimal `0` with that currency; deficient coverage = null. |
| `current_paid_amount` | Current `paid_amount` on the sender's paid side, exactly as validated by the reviewed mapping. | Decimal amount in `current_paid_currency` | R3, model, rule explanation. Missing/invalid value rejects the event before replay; never impute it. |
| `current_paid_currency` | Current exact source `paid_currency`; never substitute the received currency or an ISO/FX alias. | Source currency name | R3 grouping, model, rule explanation. Missing/unsupported value rejects the event before replay. A category unseen during later model fit uses that model's frozen unknown encoding, never a new fit. |
| `current_payment_format` | Current `payment_format` only if present in the audited source mapping; IBM v8 allows its reviewed source values. | Optional source category | Model and approved explanation; R1–R3 do not use it. A blank permitted source value is explicit null, not a guessed category. A nonblank value outside the mapping is rejected before replay; a permitted category unseen during later fit uses frozen unknown encoding. If the reviewed source lacks this role, the key is absent from that feature schema/version. |

The builder alone may use `J_s`, `J_r`, transaction/case/source-row IDs,
DatasetVersion and time for joining, sorting and snapshot lineage. The model
and rules receive only the listed feature values plus validated current facts
required by their boundary; no raw/encoded/hashed IDs, source-order proxy,
label, label-eligibility flag, target copy or full-file/future aggregate is a
predictor. Snapshot metadata retains transaction and dataset/feature version,
event time, exclusive as-of cutoff `t`, coverage start/state, typed values,
currency units and feature-input digest. Public UI may receive only separately
approved v2 assessment/explanation fields, not the private snapshot or labels.

### Time, coverage and scoreability

Sort by interpreted UTC event time, not CSV ordinal. The window is half-open
`[t−24h,t)`: a fact exactly at `t−24h` is included; one just earlier and all
facts at `t` are excluded. Compute a snapshot for **every** event in a tied
time group from the same prior history, then append the entire group's
observable facts for strictly later groups. This makes replay independent of
input-row permutation and future append. Earlier held-out validation/test
facts may enter strictly later history without their labels. A valid event
with missing or ineligible private label also enters history.

Let `source_start` be the earliest trusted interpreted event time of the
completed source. Events with `t < source_start + 24h` are context-only
warm-up: they update later history but receive no score and enter no scoreable
benchmark denominator. At `t = source_start + 24h`, a full preceding window
first becomes possible. `coverage_state=full` means the completed declared
source provides the entire window relative to this benchmark's observed
source start, with no known missing segment. Warm-up has `incomplete` window
coverage because its lower bound precedes `source_start`. Sparse account
activity within that complete source is a measured zero. `incomplete` means
some window facts may be absent because coverage starts after `t−24h` or a segment is known
missing; numerical history values are null and no rule score is emitted.
`unavailable` means no trustworthy completed source or coverage provenance
can establish the window; values and score are also absent. An empty account
history under `full` is `0`, not `incomplete` or `unavailable`. A complete
import proves file integrity, not unobserved real-world account history.

If source span/eligibility makes the initial warm-up policy unusable,
freeze a prospective amendment before fit/selection; never choose a policy
after inspecting favorable validation/test labels.

## RulePolicy v1

`rules-v1` consumes only a validated current canonical transaction and its
matching `history-v1` HistoricalFeatureSnapshot from the same complete
DatasetVersion, with `as_of=t` and `coverage_state=full`, after warm-up.
Otherwise the event is **unscoreable** and no ordinal score is emitted.
Neither private label nor eligibility can change this decision. The version
and numeric conditions are frozen before evaluation-label inspection:

| Rule | Observable condition | Contribution | Unavailable behavior |
|---|---|---:|---|
| R1 sender velocity | sender_out_count_24h >= 3 | 0.35 | Incomplete history => unscoreable; full-history cold start count 0 => not fired |
| R2 receiver velocity | receiver_in_count_24h >= 3 | 0.30 | Same coverage rule as R1 |
| R3 paid amount relative to sender history | sender_paid_count_same_currency_24h >= 3 and current paid amount >= 2 × (sender_paid_sum_same_currency_24h / count) | 0.35 | If count < 3, comparison unavailable/not fired, with reason |

R1/R2 use the exact integer counts. R3 is evaluated only when its
same-**paid**-currency prior count is at least 3; with fewer rows it is
`comparison_unavailable`, contributes `0`, and does **not** make an otherwise
full-coverage event unscoreable. Compare exact Decimal values by
`current_paid_amount * count >= 2 * sender_paid_sum_same_currency_24h`;
this is equivalent to the two-times-mean condition without division or
premature rounding, including equality. No binary float, FX or display
rounding enters the comparison. Each rule fires independently. The score is
the exact Decimal sum of fired contributions (`0.35`, `0.30`, `0.35`), finite
and bounded in `[0,1]`; it is an **ordinal rule score**, not a calibrated
probability or a guilty finding. A full-coverage cold start can score `0.00`.
Reasons record `rule_id`, observed count and exact amount/currency as applicable,
comparison and threshold, `fired` or `comparison_unavailable` state,
contribution and `rules-v1`. A zero means no declared rule
fired, not that risk is proven absent.

The machine policy identifier is `rules-v1` with feature catalog
`history-v1`. Its policy digest is SHA-256 of the following JSON object
serialized as UTF-8 with sorted keys, `ensure_ascii=True`, compact comma/colon
separators and no terminal newline. Weights are decimal **strings**; the
time/coverage semantics are supplied by the versioned `history-v1` contract.

```json
{"aggregation":"sum_fired_weights_exact_decimal","coverage_required":"full_after_source_start_plus_24h","feature_version":"history-v1","r1":{"feature":"sender_out_count_24h","minimum":3,"weight":"0.35"},"r2":{"feature":"receiver_in_count_24h","minimum":3,"weight":"0.30"},"r3":{"comparison":"current_times_count_gte_multiplier_times_sum_exact_decimal","count":"sender_paid_count_same_currency_24h","current":"current_paid_amount","minimum_count":3,"multiplier":"2","sum":"sender_paid_sum_same_currency_24h","weight":"0.35","when_count_below_minimum":"comparison_unavailable_zero_contribution"},"rule_version":"rules-v1","score_kind":"ordinal_rule_score"}
```

Policy SHA-256: `a281d38b8777b53882f4515dda7de927ff64dce43188e99c258419b1d605b5ce`.
Any rule threshold, weight, input or catalog change requires a new policy/version and digest before
evaluation; no label-derived tuning is permitted under `rules-v1`.

### Hand-computed synthetic examples frozen for T018/T019/T023

These are authored examples, not IBM observations or executed replay. Use
`source_start = 2026-01-01 00:00 UTC` and complete, gap-free source coverage
unless a row explicitly says otherwise. Accounts are `(bank,account)` pairs.

| Example | Earlier facts / current event | Expected snapshot and rules |
|---|---|---|
| Window edges | At `t=2026-01-02 12:00`, sender `A:1` has outgoing facts at `t−24h−1min`, `t−24h`, and `t−1min`; another is at `t`. | Only the latter two enter `[t−24h,t)`: `sender_out_count_24h=2`; the `t` peer does not. R1 false. |
| Tied peers and currency direction | Before `t=2026-01-02 12:00`, `A:1` sent `10`, `20`, `30` Euro at 11:00/11:10/11:20 to `B:7`, `C:7`, `D:8`; `R:1` received `7`, `9`, `11` US Dollar from `U:1`, `V:1`, `W:2` at 11:25/11:30/11:35. Two current `A:1 → R:1` peers at `t` pay `40` and `39.999999` Euro and receive US Dollar. | Both peers see sender counts `3/3`, distinct receivers `3`, paid sum `60` Euro; receiver counts `3/3`, distinct senders `3`, received sum `27` US Dollar. Neither sees the other. R1/R2 fire for both. R3 fires at exact `40*3 = 2*60`, so score `1.00`; at `39.999999*3 < 120`, R3 does not fire, so score `0.65`. The tied facts enter only later history. |
| Count threshold and unavailable R3 | With only two prior `A:1` outgoing Euro events (`10`, `20`) and two prior incoming `R:1` events in a full window, current `A:1 → R:1` pays `40` Euro. | Sender/receiver counts `2/2`: R1/R2 false; same-paid count `2`, sum `30` Euro; R3 `comparison_unavailable` even though `40 >= 2*(30/2)`. Score `0.00`. The third prior event changes counts to `3` and permits each threshold check. |
| Warm-up boundary | At `2026-01-01 23:59` a valid event occurs; at `2026-01-02 00:00` another occurs. | First is context-only and unscoreable; it still enters later history. Second is at `source_start+24h` and can be `full`; a fact at `source_start` is included at its lower window boundary. |
| Measured zero versus missing history | At `2026-01-02 12:00`, new `NEW:1 → NEW:2` has no prior matching facts; compare full coverage with a known missing preceding segment and with unknown coverage provenance. | Under `full`, all counts and currency sums are measured `0`, R1/R2 false, R3 unavailable, score `0.00`. Under `incomplete` or `unavailable`, historical values are null and no score exists. |
| Private label independence | One of the three prior `A:1` facts above has an empty/invalid private label; change only that label or append a later event at `t+1min`. | All three valid facts remain in prior history; both tied peers retain the same snapshot and score. Neither private label nor eligibility nor future event is a feature. |

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
