# ADR 001: Committed SQL changes to an ordered event log

**Status:** Proposed; team scope approval pending (T001). **Context:** Feature 002 has no live write path, CDC or broker. A new PostgreSQL source must deliver only committed immutable facts, survive restart and retain a traceable source position.

The [T001 decision record](../../../evidence/tasks/feature-005-scope-decision.md) documents the proposed benefit and schedule/resource impact. No attributable team decision is recorded there; this proposal is not implementation authorization. T002 remains blocked.

**Decision proposed:** PostgreSQL `live_transactions` INSERT → Debezium logical slot/publication → Kafka-compatible topic `fraudlens.live-transactions.v1` with one partition → one Python consumer. Redpanda is the local Compose candidate; Apache Kafka is a compatible alternative subject to actual client/connector tests. Pin images and broker client after T006–T009, not in this paper. Store DB checkpoint before Kafka offset acknowledgment; quarantine unsupported changes/versions. Deliberately configure snapshot or consistent backfill/LSN handoff.

**Alternatives:** DB polling is simpler but difficult to reconcile without gaps/scan cost; a transactional outbox would give a domain event and may be preferable if producer changes are acceptable; direct Kafka producer dual-write can lose one side. One partition sacrifices throughput to preserve sender and receiver global order. [Research](../research.md) records the comparison.

**Consequences/risks:** replication-slot WAL retention and connector outages need monitoring; source schema evolution must be gated; at-least-once delivery requires DB dedup; no end-to-end transport exactly-once claim. Out-of-course operational cost and schedule impact require a named team decision. **Validation:** T008 connector snapshot/slot and committed-only tests; T009 topic ordering/restart tests; T010 duplicate/malformed envelope tests; T024 crash replay and lag/slot monitoring.
