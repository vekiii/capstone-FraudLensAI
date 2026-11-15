# Feature 005: Real-time fraud detection and MLOps

**Branch:** `model-implementations` · **Date:** 2026-11-15 · **Status:** proposed specification; no Feature 005 implementation or team scope approval recorded. This is a future live AML review system, not automatic fraud adjudication. The existing [Feature 002 batch path](../002-data-and-risk-scoring/quickstart.md) remains available. The [constitution](../../.specify/memory/constitution.md) requires explicit team approval, with benefit and schedule impact, before implementing the out-of-course infrastructure in this proposal.

## Problem and outcome

Today, the application imports a local synthetic IBM CSV, builds 24-hour history in SQLite, scores an explicit completed batch run, then serves read-only cases. There is no transaction write API, CDC connector, broker, streaming state, live serving identity, registry or monitoring stack. The goal is a continuously operating **review queue**: an authorized transaction committed in PostgreSQL is captured by CDC, validated from a durable log, scored against point-in-time history by a pinned model, stored with an alert decision, and shown in FastAPI and the dashboard. A separate offline path uses confirmed, delayed investigation outcomes to prepare versioned training data and govern model promotion. A score alone never closes or escalates an account.

Proposed first version uses one ordered transaction topic partition and one stateful Python worker. This intentionally limits throughput until sender/receiver consistency, late-data semantics and crash recovery are measured. Performance numbers below are **proposed acceptance targets**, not measured properties.

## User stories and acceptance

1. **Ingestor:** I submit a valid synthetic transaction with a stable external ID; one committed fact appears once in the operational ledger. Duplicate ID plus identical facts is idempotent; different facts under the ID are rejected. **AC-01:** database, CDC envelope and broker identity agree.
2. **Analyst:** I see only completed assessments, their model/feature/alert-policy versions, event and processing times, coverage, score and explanation. **AC-02:** one SQL insert eventually yields one persisted assessment and one visible case when the alert policy selects it, without an offline batch CLI.
3. **Operator:** I can restart any connector/worker and replay delivery without duplicate predictions or lost work. **AC-03:** injected crashes before/after database commit preserve identical final state and recover from a durable checkpoint.
4. **Data steward:** I can detect late, malformed or incompatible events and reconcile them without silent history changes. **AC-04:** held events, quarantines and replay decisions are observable and audited.
5. **Model owner:** I can compare a candidate against a frozen protocol and delayed labels, register exact artifact identity, and promote/roll back only with team approval. **AC-05:** live traffic cannot load a mismatched/unreviewed artifact; rollback pins the prior approved digest.
6. **Existing user:** I can still run fixture and Feature 002 batch journeys. **AC-06:** their contracts and outcomes remain compatible.

## Requirements and traceability

IDs are stable within this proposed feature. “Verify” points to an acceptance scenario or an explicit test gate; paths and tasks are described in [plan.md](plan.md), [data-model.md](data-model.md), [contracts](contracts/README.md), and [tasks.md](tasks.md).

| ID | Requirement | Design/contract | Task | Verify |
|---|---|---|---|---|
| FR-001 | Store immutable, validated live transaction facts under source-provided stable IDs; reject conflicting reuse. | data model, event schema | T003–T005 | AC-01 |
| FR-002 | Capture committed inserts through PostgreSQL CDC with explicit snapshot/slot policy. | CDC contract | T008–T009 | AC-01 |
| FR-003 | Retain events durably with ordered, documented topic/offset semantics. | plan, CDC contract | T007–T010 | AC-03 |
| FR-004 | Validate envelope and canonical facts; quarantine malformed/incompatible records with safe replay. | event schema, CDC contract | T010–T011 | AC-04 |
| FR-005 | Compute 11 `history-v1` features from prior 24-hour facts, excluding self and equal-time peers. | feature contract | T015–T017 | AC-02, AC-04 |
| FR-006 | Buffer out-of-order events and apply a bounded event-time finalization policy; quarantine later arrivals. | state proposal, data model | T012–T014 | AC-04 |
| FR-007 | Distinguish full history, warm-up and unavailable coverage; never score insufficient history as zero. | feature contract | T013, T017 | AC-02 |
| FR-008 | Score with a pinned, trusted existing scikit-learn artifact through an explicitly validated live adapter. | serving contract | T018–T020 | AC-02, AC-05 |
| FR-009 | Atomically persist feature snapshot, prediction, alert decision and processed position; make retries idempotent. | data model, prediction schema | T021–T022 | AC-03 |
| FR-010 | Expose bounded, read-only live alert list/detail and health endpoints with stable snapshot pagination. | API contract | T026–T028 | AC-02 |
| FR-011 | Show live score provenance, coverage and explanation in the dashboard without changing fixture/batch views. | API contract | T029–T030 | AC-02, AC-06 |
| FR-012 | Provide deterministic replay/backfill and reconciliation with complete audit records. | plan, data model | T023–T025 | AC-03, AC-04 |
| FR-013 | Capture confirmed investigation outcomes in a restricted label store, separated from inference. | label contract | T031–T032 | AC-05 |
| FR-014 | Build versioned point-in-time offline training datasets with SQL/dbt and provenance. | data model, lifecycle proposal | T033–T035 | AC-05 |
| FR-015 | Track, evaluate, approve, promote and roll back exact model versions; keep scores distinct from alert policy. | serving contract, lifecycle proposal | T036–T040 | AC-05 |
| NFR-001 | Demonstrate a proposed local p95 insert-to-persisted-assessment target of 180 seconds at 1 event/second after warm-up, with measured hardware and exclusions. | plan | T045 | AC-02 |
| NFR-002 | Recover from process restart without lost/duplicate observable results; expose lag and failure backlog. | plan | T024, T042, T045 | AC-03 |
| NFR-003 | Restrict writer, CDC, worker, label, registry and read-only API roles; protect credentials and raw data. | security checklist | T002, T043 | AC-04, AC-05 |
| NFR-004 | Export pipeline, CDC/slot, lag, watermark, failure and model-version metrics with actionable alerts. | plan | T041–T042 | AC-03 |
| NFR-005 | Preserve existing fixture v1, batch v2, CLI and frozen model behavior; use additive versioned live contracts. | serving/API contracts | T001, T020, T030, T046 | AC-06 |
| ML-001 | Never expose target or confirmed label fields to inference, historical state or feature transforms. | feature/label contracts | T016, T032, T035 | AC-05 |
| ML-002 | Compare live incremental features with offline `history-v1` replay, including ties, currency and warm-up. | feature contract | T017, T034 | AC-02, AC-04 |
| ML-003 | Separate serving-compatibility identity from source dataset lineage; retain trusted artifact validation. | serving contract | T019–T020, T037 | AC-05 |
| ML-004 | Evaluate with delayed confirmed labels, fixed windows and capacity metrics, reporting exposure/uncertainty honestly. | label contract | T038–T039 | AC-05 |
| ML-005 | Promotion/rollback changes an approved digest atomically; live workers pin a digest per assessment. | serving contract | T040 | AC-05 |

## Boundaries, dependencies and questions

**In scope:** a local Compose prototype for PostgreSQL, Debezium, Kafka-compatible broker, one Python worker, FastAPI/dashboard live read path, SQL/dbt offline preparation, MLflow tracking/registry, Prometheus/Grafana observability, and recovery/reconciliation tests. Existing batch and fixture flows remain. **Out of scope:** payment blocking, automatic case disposition, production multi-region HA, unbounded throughput, mandatory Flink/Spark/Feast/Airflow/Kubernetes, new model families, and claims of real-world predictive quality.

Dependencies: team scope approval before implementation; Docker/Compose resources and approved container versions; a reviewed live source contract; a trusted same-hash trained artifact and approved serving decision; appropriate delayed confirmed labels. The original boosted artifact and peer checks for Feature 002 are currently unavailable/blocked in this checkout. Initial integration may use a **synthetic, separately named fixture artifact** to verify the transport/contract path, but may not call that a real model evaluation or activate it for reviewed cases.

Open decisions for T001/T002: (a) named team decision and schedule/benefit for out-of-course services; (b) exact synthetic live transaction producer and ID issuer; (c) whether an approved Feature 002 artifact and its exact dependencies can be transferred and validated; (d) chosen broker distribution and pinned image/client versions after local testing; (e) permitted data retention and access rules. If any gate fails, stop the dependent implementation task and record the blocker; do not relax validation.
