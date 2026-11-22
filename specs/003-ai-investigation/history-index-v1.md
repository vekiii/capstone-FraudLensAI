# Optional consumer history index for actual producer scale — T098

2026-11-18 implementation design within the feature003-owned history boundary.
Actual partial IBM import (~2.5million rows) already interrupts the existing
MIN(event_time_utc) metadata scan at5.031s. This is a scaling diagnostic, not
completed T098, full-population inference or SC-006 acceptance. Preserve the
five-second query deadline rather than enlarging it or misreporting unavailable
history as empty. Confirm again on the completed canonical source.

Prepare an **optional separate consumer-owned SQLite index**, explicitly offline
through a trusted operator CLI. The original producer source/run files, schemas,
scorer/policies and public context/report contracts stay unchanged. Default
unindexed behavior and all historical bindings remain supported. No provider,
training, labels, evaluation references, HTTP ingestion or new service.

Preparation reads only completed active dataset metadata and explicit operational
fields through a read-only SQLite connection/authorizer. Source must be frozen
with no nonempty WAL; hash before/after, refuse concurrent changes and an existing
output. Store only transaction ID, exact original event time/raw/basis, sender/
receiver bank/account and paid/received strings/currencies; never copy whole
operational JSON, private tables or feature/evaluation data. Persist source path,
size/mtime, SHA-256, dataset ID, reject count, earliest event and row count. Cache
publication is atomic; incomplete outputs cannot be used. Index bank+account+time
for both directions. Integer UTC microseconds are internal indexing keys; source
time/money strings remain unchanged in evidence.

Activation requires explicit paired private settings
`INVESTIGATION_DATASET_HISTORY_INDEX` and
`INVESTIGATION_DATASET_HISTORY_INDEX_SHA256` in dataset mode. API and worker use
the same pins. Validate index digest, frozen source digest/identity and metadata
at initialization, then stat/WAL guards on each read; fail closed on changed or
unavailable stores. No fallback to fixtures or a stale index. Startup hashing is
separate from bounded SQL; it is not a new performance acceptance claim.

The adapter still checks the original active source dataset/run and exact context
revision. Metadata uses the verified index's earliest event/reject count. History
uses indexed operational facts with the same seven-day start, strict focal-minute
cutoff, bank+account scope, focal exclusion, two self-transfer movements,50-event
limit, whole-item tool-byte bounds and Decimal totals over all eligible movements
grouped by direction and currency. All queries retain finite five-second limits.
Absent/unavailable remains distinct from available-empty. Archived attempts keep
their original contexts/evidence; nothing is regraded or silently migrated.

RED/GREEN checks: exact indexed/legacy parity on authored data; privacy and source
immutability; both directions/self-transfer/window/truncation/totals; empty versus
unavailable; source/index/hash/version corruption and source switches; existing
output refusal; settings pairing and actual API/worker wiring. Then exercise the
completed real IBM source and actual bounded producer publications. Fixtures prove
software properties only; no T098 completion until actual checks are recorded.
