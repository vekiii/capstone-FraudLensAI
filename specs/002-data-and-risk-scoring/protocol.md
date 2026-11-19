# Feature 002 protocol

Status: canonical-preparation resource settings frozen by T209 and the temporal feature contract frozen by T212 on 2026-11-19. T213 implements and synthetically verifies the temporal kernel; no full-source temporal output is published. The timezone of the selected source remains undocumented; the conditional project UTC convention below is frozen for this exact local copy. The user authorized a content-addressed local-copy exception for T203/T210 on 2026-11-19; its limits are below. Partitions, full model protocol, and model decisions remain open.

## T203 local-copy decision and T210 scope

The user confirmed a local download of `HI-Small_Trans.csv`, could not provide its Kaggle version or receipt, and explicitly directed us to close T203 and execute T210. For this local educational preparation, identify the exact selected source revision by its measured SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040` and 475,664,283-byte size. The publisher's Kaggle revision, acquisition date and method beyond the user-reported local download remain unknown. IBM's AML-Data README is the source for CDLA-Sharing-1.0 data terms; the Kaggle listing's own terms field was unavailable. These are explicit reproducibility and licensing limitations, not verified facts. No data redistribution is authorized by this decision.

This decision permits a **local canonical preparation and quality report** only for the exact matching bytes, with exact-header/schema validation and the T209 resource ceilings. It does not permit substituting a different source, treating the unknown upstream release as known, fitting models, inspecting record-level labels outside the restricted pipeline, or claiming temporal partitions complete. Contrary source or license evidence is a stop condition. T203 closes under this documented exception; T210 must report any missing manifest/data-card fields honestly.

## T209 preparation resource contract

The following settings apply only to the T208 canonical validation and snapshot runner. They do not establish capacity for temporal sorting, feature generation, model fitting, or API serving. The measurements and exact commands are in [T209 evidence](../../evidence/tasks/T209.md).

| Control | Frozen setting | Operational response |
|---|---:|---|
| Source batch / chunk size | 10,000 records | Do not increase without a new synthetic benchmark. |
| Checkpoint cadence | Every complete 10,000-record chunk; final partial chunk also committed | Resume only after source, configuration, input-prefix and staged-output verification. |
| Process peak working-set ceiling | 512 MiB | Stop the run if monitored peak exceeds the ceiling; investigate before retry. This is an operational ceiling, not yet an in-process limiter. |
| Minimum free-space reserve | 10 GiB on staging and output volumes | Pass `min_free_bytes=10737418240` to `run_pipeline`; a low-space check stops the run. |
| Start-of-run free space | At least 20 GiB on each relevant volume | Check before invoking the runner; the 10 GiB reserve alone is not a capacity forecast. |
| Maximum canonical preparation runtime | 15 minutes for approximately 5.1 million records on the measured workstation | Stop and review a slower run. This is an operational ceiling, not yet an in-process timeout. |
| Published snapshot | One immutable directory with verified `COMPLETE` marker | Never treat staged or partial output as complete. |

These values must be reconsidered if source size, record width, machine, volume, code, or output format changes. A real-source run also requires the T203 local-copy decision above, verified input SHA-256, and a processing configuration hash. Any ceiling breach is a stop condition; it is not permission to drop records or relax validation.

The full-size synthetic run processed 5,078,345 rows in 331.236 seconds with an 83,034,112-byte process peak working set. Stage plus published snapshot occupied 6,120,299,645 bytes before cleanup. The 20 GiB initial free-space rule allows over 4 GiB beyond that observed footprint while preserving the 10 GiB reserve; it is a preflight threshold for this format, not a promise that every source will fit. The runner checks disk reserve automatically; an operator must monitor the memory and runtime ceilings until a bounded watchdog is added.

### T210 real-source runtime review, 2026-11-19

The first exact-source T210 run combined source hashing, CSV parsing, canonical validation, a bounded non-label quality scan, snapshot publication and full output verification. It completed in 903.834 seconds, exceeding the T209 **canonical synthetic** 900-second operational ceiling by 3.834 seconds. This breach was observed and reviewed after completion, not hidden or relabeled as a pass. The snapshot's `COMPLETE` marker, manifest counts and processed-file hashes verified; 5,078,345 source rows reconciled with 5,078,345 accepted and zero rejected. Highest sampled process peak working set was 84,594,688 bytes, with 67,546,107,904 bytes free afterward. No memory or disk threshold was approached.

For a **repeat of this exact-source integrated T210 preparation plus quality-scan configuration on this workstation**, set a reviewed 20-minute operational runtime ceiling. This gives about 1.33× headroom over the measured run; the original 15-minute T209 ceiling remains the synthetic canonical-run comparison and its breach remains recorded. The verified T210 snapshot can be retained for later permitted local preparation steps without rerunning the entire CSV solely for a 3.834-second overrun. A different source, code/configuration, volume or machine requires a new review, and downstream feature/partition/model work still has separate gates. Runtime and peak working set remain operator-monitored until enforced by code.

## HI-Small source interpretation for preparation

The selected input is **`HI-Small_Trans.csv` only**. The publisher's Kaggle description lists it separately from `HI-Small_Patterns.txt` and the other independent HI/LI variants. Its published approximate counts and date span are context, not measured facts for the local CSV. The description warns that some transactions occur after the primary Sep 1–10, 2022 period and reports that these late transactions are laundering. This label-related statement is a publisher caveat; it does not authorize record-level label inspection or changing the frozen chronological split from the feature spec.

The checked Kaggle description excerpt, IBM README and accessible paper do not assign a timezone to `HI-Small_Trans.csv`. The local timestamp field has minute precision and no offset. **Project assumption for later temporal processing:** interpret a valid naive source timestamp as UTC at minute precision, without changing its displayed text during initial canonical preparation. This is an explicit modeling convention, not a publisher claim. If source documentation for the selected bytes states another timezone, stop and revise the policy before temporal processing.

## T212 frozen temporal feature contract (2026-11-19)

This contract applies to the exact local `HI-Small_Trans.csv` bytes pinned above and to synthetic cases exercising the same boundary. It freezes feature definitions **before** feature experiments; it does not authorize model fitting, real-source feature generation, label access, or publishing a ready-to-model snapshot. Feature contract identifier: `hi-small-temporal-v1`. T219 will bind the implemented schema and dataset/partition hashes into the full training protocol. A change to any definition below requires a new feature version and reviewed protocol change, never a validation/test-driven edit.

### Time and row eligibility

- Rechecked the [IBM AML-Data README](https://github.com/IBM/AML-Data/blob/main/README.md), the [publisher paper](https://papers.nips.cc/paper_files/paper/2023/file/5f38404edff6f3f642d6fa5892479c42-Paper-Datasets_and_Benchmarks.pdf), the available user-supplied Kaggle description excerpt and the [Kaggle listing](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml). None of the readable materials assigns a timezone to this CSV; the Kaggle page returned no readable text. The T203 header/lexical scan found every local timestamp in `YYYY/MM/DD HH:MM`, without an offset. **UTC is a project convention, not a verified publisher timezone.** Contrary authoritative evidence is a stop condition before temporal processing. Upstream release, download date and Kaggle listing terms remain unknown under the T203 exception.
- Parse the selected source's valid naive minute-precision text as an aware UTC instant, with seconds and microseconds zero. For explicitly offset synthetic/input values, use the stated offset to identify the instant and normalize to UTC without rounding away seconds or finer provided precision. Reject invalid, ambiguous or unsupported timestamp text rather than guessing. Keep original text as provenance; order and feature windows use normalized instants.
- Sort by normalized instant, then positive `source_row_number`. Compute all members of an equal-instant group from state containing **strictly earlier** events, then add the whole group. The history interval is `[t−24h,t)`: the exact lower edge is included, the entire current instant excluded. Earliest valid instant `t0` sets warm-up `[t0,t0+24h)`; warm-up rows contribute history but cannot be scored. At exactly `t0+24h`, scoring is eligible. Partition boundary details remain T214–T215.

### Exact feature order and types

The ordered feature vector is the following **eleven** fields. Names, order, side-specific currencies and numeric representations are part of `hi-small-temporal-v1`; source identifiers, timestamp, transaction ID and eligibility are metadata, not model features.

| Position | Feature | Value / definition |
|---:|---|---|
| 1 | `sender_out_count_24h` | Nonnegative integer; prior rows with the same exact `(sender_bank, sender_account)` key. |
| 2 | `sender_distinct_receivers_24h` | Nonnegative integer; distinct exact `(receiver_bank, receiver_account)` keys among those rows. |
| 3 | `sender_paid_count_same_currency_24h` | Nonnegative integer; sender rows whose `payment_currency` exactly matches the current payment currency. |
| 4 | `sender_paid_sum_same_currency_24h` | Exact nonnegative Decimal sum of those rows' `amount_paid`; no conversion between currencies. |
| 5 | `receiver_in_count_24h` | Nonnegative integer; prior rows with the same exact `(receiver_bank, receiver_account)` key. |
| 6 | `receiver_distinct_senders_24h` | Nonnegative integer; distinct exact `(sender_bank, sender_account)` keys among those rows. |
| 7 | `receiver_received_count_same_currency_24h` | Nonnegative integer; receiver rows whose `receiving_currency` exactly matches the current receiving currency. |
| 8 | `receiver_received_sum_same_currency_24h` | Exact nonnegative Decimal sum of those rows' `amount_received`; no conversion between currencies. |
| 9 | `current_amount_paid_log1p` | Finite binary64 value `math.log1p(float(Decimal(amount_paid)))`, using validated nonnegative source text; natural logarithm, no currency conversion. This deliberate float conversion occurs only for this model feature, never historical summation or identity. |
| 10 | `current_payment_currency` | Exact nonempty payment-currency text as a categorical value, subject to the train-only unknown policy below. |
| 11 | `current_payment_format` | Exact nonempty payment-format text as a categorical value, subject to the same policy. |

Use bank-qualified keys as exact text, preserving leading zeroes. Empty prior history yields integer `0` counts and Decimal `0` sums. Current-transaction fields come only from the current event; no future row or same-instant peer may influence historical values. `receiving_currency` is used for receiver history but is **not** a separate current categorical feature in this version. `amount_received` is likewise not a current feature. Do not add a candidate field based on validation/test outcomes.

### Precision, missing values and categories

- The 2026-11-19 non-label local scan of all 5,078,345 source rows found at most **13 integer digits**, **6 fractional digits**, and **15 total written digits** in each amount column, with zero malformed amount texts in that scan. These are observed bounds for the pinned copy, not publisher-declared types. Parse amount text with `Decimal`, retain its source scale, and calculate history sums in a local Decimal context with precision **38** and traps for inexact/rounded arithmetic. No intermediate float conversion or silent quantization is allowed. Reject a different source or a value exceeding the selected-copy six-fractional-digit bound pending a new reviewed version; do not round it into compliance. Counts stay exact integers. Serialize Decimal sums as decimal strings in stored feature snapshots; convert to model numeric representation only under the frozen training preprocessing contract.
- Every required timestamp, bank/account ID, amount, payment currency, receiving currency and payment format must be present and valid under the canonical validator. Missing, blank, malformed, nonfinite or negative required values reject the row with a bounded reason; no imputation. The current validator handles the selected naive CSV form; T213 must implement UTC normalization and handle explicit offsets at its temporal boundary without silently widening the selected raw-source schema.
- Preserve category spelling and case exactly; no trim/casefold, currency exchange conversion or vocabulary inferred from the full source, quality report, validation, test or showcase partitions. Fit separate payment-currency and payment-format vocabularies on **scoreable training rows only** after partitions freeze. Reserve an internal `__UNKNOWN__` bucket for each field and include it in the encoder even if unseen in training. Any nonempty category absent from that field's training vocabulary maps to its `__UNKNOWN__` bucket in validation, test, showcase and runtime; missing/blank values reject rather than map. Sort known vocabulary values by exact Unicode code-point order, then append the reserved bucket. Keep the two vocabularies and their order with the model metadata; a literal source `__UNKNOWN__` value is rejected as a reserved-token collision. Train-only preprocessing and compatibility checks belong to later tasks.
- Exclude `is_laundering`, future records, investigation data and analyst conclusions from feature rows, training preprocessing inputs and runtime/public contracts. Keep labels in the restricted layer. A feature row's `is_scoreable` flag is eligibility metadata; warm-up rows may update history state but never receive prediction or alert outputs.

## Later protocol decisions

- Upstream Kaggle release and exact acquisition date: unknown under the explicit T203 local-copy exception; selected bytes are pinned by SHA-256.
- Naive timestamp interpretation: T212 rechecked the available documentation and froze the conditional UTC project convention above; T213's normalization passed synthetic checks. The publisher timezone remains unknown, and no full-source temporal pass ran.
- Feature order, precision, missing/category policy and `hi-small-temporal-v1` identifier: frozen by T212 above. T213 implements the label-free feature kernel and exact current/history order; train-only encoder artifacts remain pending later training tasks. External sorting, resource benchmarking and completed real-source temporal output are separate work.
- Development/showcase and train/validation/test boundaries and hashes: pending T214–T219.
- Candidate grid, class strategy, threshold objective and artifact format: pending T221/T222.
- Label access and separately authorized evaluation: pending T216–T230.
