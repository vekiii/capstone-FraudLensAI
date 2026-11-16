# Proposal 001: Live transaction ingestion and streaming review path

**Status: APPROVED — prior team agreement confirmed by requester.** The requester confirms that the team discussed and agreed to everything in this branch before implementation. This records that prior decision as reported on 2026-11-16; it is not a request for new approval. Individual names and the exact earlier discussion date were not supplied. No additional conditions were reported; specification requirements and verification gates remain in force.

## Proposed scope

Add a local, synthetic-data live transaction path using the following out-of-course stack:

| Component | Proposed role | Why it is proposed |
|---|---|---|
| PostgreSQL | Store canonical committed live transaction facts, worker state, checkpoints, predictions and alerts. | A transactional database can make persisted assessment state and progress recoverable and consistent across producer, worker and API. |
| Debezium | Capture committed PostgreSQL changes through a logical replication slot/publication. | CDC can observe committed source changes without polling tables and provides source positions for recovery. |
| Kafka-compatible broker | Hold a replayable event stream; initial proposal uses one partition. | Durable retention and replay can bridge producer and worker restarts. A single partition preserves a simple global order while throughput remains limited. |
| Python worker | Consume events, validate them, maintain event-time history, score and persist assessments. | Reuses project language and scoring boundaries while isolating stream state and deterministic processing from the API. |
| dbt | Build versioned offline datasets and lineage from stored facts and eligible delayed outcomes. | SQL transformations can make offline training data reproducible and support comparison with online features. |
| MLflow | Track candidate runs and register model metadata/artifacts. | Provides a record of candidate versions; serving still requires a separate human-approved immutable artifact digest. |
| Prometheus and Grafana | Collect operational metrics and present dashboards/alerts. | Operators need visibility into WAL/slot, broker, worker lag, failures, latency and recovery state. |

The proposed first deployment is local Compose, one worker and one broker partition. It is a review prototype, not a production readiness claim. Model selection, promotion, account actions and analyst dispositions remain human-controlled under existing boundaries.

## Alternatives

| Alternative | Benefit | Cost or limitation |
|---|---|---|
| Do nothing | Avoids out-of-course scope, new services and schedule pressure. | No live ingestion or streaming review demonstration. |
| Keep SQLite batch only | Preserves the existing, simpler batch path and current project footprint. | Does not provide a committed live write path, CDC, durable event replay or streaming operations. |
| Application transactional outbox instead of CDC | Emits an explicit domain event in the source transaction and avoids replication-slot/WAL capture complexity. | Requires producer/application changes and an outbox relay; this remains a viable alternative if CDC access or operational complexity is unacceptable. |
| Proposed PostgreSQL + Debezium + broker | Captures committed facts and supports replay while keeping the source write path explicit. | Adds services, compatibility gates, storage and operating work described below. |

## Expected benefit and planning estimates

**Potential benefit (estimate):** demonstrate a traceable path from committed synthetic transaction to analyst review, including recovery and model-version provenance. This could make integration behavior easier to inspect than a batch-only demonstration; no measured benefit is claimed.

**Schedule impact (rough planning estimate, not a commitment):** approximately 1–2 additional calendar weeks if work can proceed in parallel, or roughly 6–12 person-days across integration, security, parity, recovery and acceptance work. This estimate assumes local Compose and synthetic data; it excludes time to obtain/approve a compatible model artifact or resolve environment incompatibilities. The existing specification backlog has 46 tasks across six phases, but that task count is not a duration estimate. The team should revise this range before deciding.

**Resource impact (rough planning estimate, not measured):** likely 2–3 contributors across data/ML, backend/operations and review; local Docker capacity for PostgreSQL, broker, connector, worker, dbt/MLflow and monitoring; added storage for WAL, broker retention and artifacts. Actual host capacity, cloud/service budget, ownership and person-hours are unknown and must be assessed by the team. No services have been provisioned for this proposal.

## Constitution requirement

The constitution's [Principle I — Team-Controlled Scope](../../../.specify/memory/constitution.md#i-team-controlled-scope) states: **“Any out-of-course technique or functionality MUST receive explicit team approval before implementation, with benefit and schedule impact recorded.”** This proposal records an estimated benefit and estimated schedule/resource impact for review; the prior team approval is recorded in the linked T001 decision record.

## Risks and limits

- Replication-slot or connector outages can retain WAL and exhaust disk; broker outages or insufficient retention can create unrecoverable gaps.
- At-least-once delivery can duplicate work; event identity, idempotency, checkpoints and transaction boundaries need explicit validation.
- One partition limits throughput. Multiple partitions can break cross-account ordering needed for sender and receiver history.
- Late, malformed, changed or out-of-order events can corrupt point-in-time features unless held, quarantined or replayed under a defined policy.
- New services, permissions, secrets, network paths, backups and retention increase operational and security burden.
- dbt/MLflow do not establish model validity; label leakage, temporal leakage, incompatible artifacts and missing independent evaluation remain risks.
- The trusted model artifact and its compatibility evidence may be unavailable, delaying a meaningful model-serving demonstration.
- Existing SQLite batch and fixture journeys must remain unchanged; this proposal does not authorize changing them.
- These are identified design risks, not test results or measured failure rates.

## Open decisions from Feature 005

The following decisions (a)–(e) remain open as listed in [spec.md](../spec.md):

| ID | Decision needed |
|---|---|
| (a) | Named team decision and recorded benefit/schedule impact for the out-of-course services. |
| (b) | Exact synthetic live transaction producer and transaction ID issuer. |
| (c) | Whether an approved Feature 002 artifact and its exact dependencies can be transferred and validated. |
| (d) | Broker distribution and pinned image/client versions after local compatibility testing. |
| (e) | Permitted data retention and access rules. |

## Reviewers and decision record

Individual reviewer names remain blank because none were supplied. The requester confirms collective team discussion and agreement before implementation; the date of that earlier discussion is not supplied.

| Reviewer name | Role | Review date | Comments |
|---|---|---|---|
|  | Data/ML |  |  |
|  | Backend/operations |  |  |
|  | Team scope reviewer |  |  |

**Decision:** APPROVE — prior team discussion and agreement, confirmed by the requester.
**Attribution/source:** Requester's direct confirmation, recorded 2026-11-16; individual approver names not supplied.
**Earlier discussion date:** Not supplied; requester confirms it preceded implementation.
**Conditions or objections:** No additional conditions were reported; existing specification requirements and verification gates apply.
**Approved scope:** Everything in this branch as discussed and represented by its specifications and proposals.
**Recorded benefit and schedule/resource impact:** Proposal figures are planning estimates; they are not measured outcomes.

T001 is recorded as DONE in the linked decision record based on the requester's attributed confirmation. Unknown names and the exact earlier discussion date remain explicitly unspecified; they are not inferred.
