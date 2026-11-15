# Proposed `history-v1` live feature contract

The required output is an ordered, label-free `history-v1` snapshot with the **same eleven feature names, definitions, units and order** as [the current catalog](../../../backend/src/fraudlens/feature_history.py) and [training loader](../../../backend/src/fraudlens/train_phase5.py). The first nine are numeric, the final two categorical. This document freezes the intended parity target; the streaming implementation does not exist.

| Order | Feature | Unit / exact rule |
|---:|---|---|
| 1 | `sender_out_count_24h` | Count of earlier outgoing sender events. |
| 2 | `sender_distinct_receivers_24h` | Distinct bank-qualified receivers in earlier sender events. |
| 3 | `sender_paid_count_same_currency_24h` | Earlier outgoing paid events in current paid currency. |
| 4 | `sender_paid_sum_same_currency_24h` | Decimal sum of earlier paid amounts in current paid currency. |
| 5 | `receiver_in_count_24h` | Count of earlier incoming receiver events. |
| 6 | `receiver_distinct_senders_24h` | Distinct bank-qualified senders in earlier receiver events. |
| 7 | `receiver_received_count_same_currency_24h` | Earlier incoming received events in current received currency. |
| 8 | `receiver_received_sum_same_currency_24h` | Decimal sum of earlier received amounts in current received currency. |
| 9 | `current_paid_amount` | Current exact paid amount, no currency conversion. |
| 10 | `current_paid_currency` | Current source currency name. |
| 11 | `current_payment_format` | Current optional format, explicit null if absent. |

Historical window is `[event_time - 24 hours, event_time)`. Events at the same timestamp share a pre-group snapshot; none sees itself or equal-time peers. A sender and receiver identity is `(bank,account)`. Never aggregate paid and received sides or different currencies. Immutable event facts feed history even when their label is missing/invalid; label columns and target-derived aggregates are forbidden. Use exact Decimal for sums, and convert to model numeric representation only at the validated serving boundary. Unknown categories use the trained encoder's unknown-ignore behavior; do not invent a new category mapping.

Coverage is `full`, `incomplete` or `unavailable`. Start-up history is incomplete until a verified contiguous prior 24 hours exist; missing broker/WAL ranges make it unavailable. Only `full` may produce a model prediction. `feature_digest` hashes the canonical ordered values plus source lineage, feature version, coverage and as-of time under a versioned recipe to be frozen/tested in T016. Historical values may be null only when coverage is deficient; zero means observed zero with full coverage. `source_lineage_id` identifies the live source/generation and is distinct from the trained artifact's offline dataset version.

Parity gate: for a common synthetic event timeline, compare every live snapshot with `iter_feature_snapshots`, including reordered arrival, equal-time groups, `[t-24h,t)` boundaries, two banks sharing an account string, both currency sides, zero-vs-unavailable and late replay. Any mismatch blocks serving. See [state proposal](../proposals/002-state-and-event-time.md).
