# Accepted producer boundary, 2026-11-16

Team confirmation was explicitly conveyed by the user in this conversation.
This records that confirmation, not separate individual signatures. Reviewed
producer: origin/feature/005-real-time-fraud-detection-mlops-spec at
487c427ea50e169f5e36898420d659f05ead2c60, particularly data_store.py,
the feature002 schema and docs/decisions/ml-data-investigation-technical-agreement.md.
The colleague document's unavailable 9454bfc SHA remains a deferred post-feature
documentation correction; the available SHA above binds this adapter review.

Feature003 owns a read-only consumer adapter for the existing published SQLite
layout, with trusted server-configured paths and score source. It does not import
ML code, train, modify either producer database or access private label tables.
Producer contributors retain store/import/model/scoring ownership. Integration
does not activate or accept a boosted research candidate automatically.

Context contract version2 explicitly pins producer-v2-reviewed-20261116.snapshot.json.
Version1 and producer-v2.snapshot.json remain unchanged for historical reports.
The only producer schema difference is the additional available-explanation method
boosted_sequential_probability, on positive_class_estimate scale. Contributions
are sequential/order/baseline dependent, not causal, SHAP or calibrated probability.
Validate producer identities, time/cutoff equality, source/kind/method, scale and
additive reconstruction within 1e-8. Preserve all exact directional strings,
source currency names, raw minute time and assumed UTC basis.

History port: read(context, account_side, limit=50), side sender or receiver,
integer limit1..50. Query both incoming and outgoing matching the focal side's
bank AND account, within t-7d inclusive and focal minute exclusive; exclude focal
ID. Each transfer direction is one event, self-transfers yield both movements.
Outgoing uses paid; incoming uses received. Direction and raw/time-basis fields
are retained in dataset evidence. Order by time, transaction ID, direction.
Return availability, coverage, cutoff/start/lookback, events, returned_count,
eligible_count, truncated and totals. Totals are exact Decimal strings grouped
by direction AND currency over ALL eligible movements, before truncation; no FX
or incoming/outgoing netting. Maximum50 returned, whole-item byte truncation can
reduce this further. Coverage is incomplete if import rejects exist or dataset
starts after requested start; full refers only to this synthetic store's window,
never all real bank/customer activity. Missing store/history is unavailable with
eligible_count null, distinct from available empty (count0). Source/run changes
reject stale work; saved attempts retain their archived context/evidence.

Fixed SQL is internal, parameterized and read-only, never a model tool. No arbitrary
path/SQL is accepted from requests. Source queries have a finite deadline and
bounded memory; unavailable/invalid sources never fall back to fixture history.
No full IBM import/run stores are present locally. Controlled producer-generated
rules and model-shaped publication checks are compatibility, not ML evaluation.
