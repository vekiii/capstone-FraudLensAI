# Feature 005 T001 — team scope decision record

**Status: APPROVED — T001 DONE.** The requester confirms that the team discussed and agreed to everything in this branch before implementation. This records that prior decision as reported on 2026-11-16; it is not a request for new approval. Individual participant names and the exact earlier discussion date were not supplied. The approved scope is all Feature 005 branch work as proposed, subject to specification requirements and technical verification gates. No additional conditions were reported.

**Proposal:** [Proposal 001 — live transaction ingestion and streaming review path](../../specs/005-real-time-fraud-detection-mlops/proposals/001-cdc-and-streaming.md)
**Relevant requirements:** NFR-005, FR-015
**Specification:** [Feature 005](../../specs/005-real-time-fraud-detection-mlops/spec.md)
**Governance:** [Constitution Principle I — Team-Controlled Scope](../../.specify/memory/constitution.md#i-team-controlled-scope)

## Governance requirement

The constitution says: **“Any out-of-course technique or functionality MUST receive explicit team approval before implementation, with benefit and schedule impact recorded.”** The proposed live stack is beyond the approved MVP. The requester confirms that the team discussed and agreed to everything in this branch before implementation. The report was recorded on 2026-11-16. Individual names and the exact earlier discussion date were not supplied. No additional conditions were reported beyond specification requirements and verification gates.

## Scope proposed for review

The proposal covers a local synthetic-data path using PostgreSQL for committed facts and durable state; Debezium for change capture; a Kafka-compatible broker for ordered replay; a Python worker for event-time processing, scoring and persistence; dbt for offline dataset transformations and lineage; MLflow for candidate tracking/registry metadata; and Prometheus/Grafana for operational metrics and dashboards. The reasons, alternatives and risks are detailed in [Proposal 001](../../specs/005-real-time-fraud-detection-mlops/proposals/001-cdc-and-streaming.md).

The existing SQLite batch and fixture paths are explicitly out of scope for change. No account intervention, automatic disposition, model activation or production deployment is authorized by this proposal.

## Estimated impact for team review

These are planning estimates only, not measured facts or commitments:

- **Potential benefit:** demonstrate a traceable live path from committed synthetic transaction to analyst review, with recovery and model-version provenance.
- **Schedule:** rough estimate of 1–2 additional calendar weeks with parallel work, or 6–12 person-days across integration, security, parity, recovery and acceptance. The estimate excludes artifact acquisition/approval and environment blockers; the team should revise it.
- **Resources:** rough estimate of 2–3 contributors and local Docker capacity for the proposed services, plus storage for WAL, broker retention and model artifacts. Actual service budget, hardware headroom and staffing are unknown and unmeasured.

## Alternatives considered

1. **Do nothing:** avoid scope and service burden; no live streaming demonstration.
2. **Keep SQLite batch only:** preserve the current simpler batch/fixture scope; no streaming source or replayable event path.
3. **Application transactional outbox instead of CDC:** explicit event written with the source transaction, but requires producer changes and a relay; consider if CDC access/operations are unacceptable.
4. **Proposed CDC stack:** PostgreSQL + Debezium + Kafka-compatible broker + Python worker + dbt + MLflow + Prometheus/Grafana; supports committed-change capture and replay at the cost of added operational complexity.

## Risks and open decisions

Risks include WAL growth during slot/connector outages; broker retention gaps; duplicate delivery; ordering and late-event effects on history; new secrets, roles, backups and retention burden; compatibility across services; label/temporal leakage in offline data; and lack of a validated serving artifact. None of these risks has been tested or measured as part of this draft.

Open decisions (a)–(e), copied from Feature 005 `spec.md`:

| ID | Decision needed | Decision/status |
|---|---|---|
| (a) | Named team decision and schedule/benefit for out-of-course services. | APPROVED before implementation per requester; individual names and exact discussion date not supplied. Benefit/schedule/resource figures remain planning estimates. |
| (b) | Exact synthetic live transaction producer and ID issuer. | Pending; blank |
| (c) | Whether an approved Feature 002 artifact and its exact dependencies can be transferred and validated. | Pending; blank |
| (d) | Chosen broker distribution and pinned image/client versions after local testing. | Pending; blank |
| (e) | Permitted data retention and access rules. | Pending; blank |

## Reviewers

Individual names remain blank because the requester did not supply them. The requester attributes prior discussion and agreement to the team. The report was recorded on 2026-11-16; the exact earlier discussion date was not supplied. No additional conditions were reported.

| Name | Role | Review date | Comments |
|---|---|---|---|
|  | Requesting contributor |  |  |
|  | Data/ML reviewer |  |  |
|  | Backend/operations reviewer |  |  |
|  | Team decision representative |  |  |

## Decision record — prior team approval, attributed by requester

**Decision:** APPROVE — the team discussed and agreed to everything in this branch before implementation.
**Attributable source:** Requester's direct confirmation, recorded 2026-11-16.
**Earlier discussion date:** Not supplied; requester confirms it preceded implementation.
**Named participants/reviewers:** Individual names not supplied; requester attributes the decision to the team.
**Conditions:** No additional conditions were reported; existing specification requirements and verification gates apply.
**Approved scope:** All work in this branch as discussed and represented by its specifications and proposals.
**Benefit/schedule/resource estimates:** Proposal figures are planning estimates; no measured outcomes are claimed.

T001 is recorded as DONE based on the requester's attributed confirmation of prior team agreement. Unknown names and the exact historical discussion date are explicitly left unspecified, not invented. Technical verification tasks and real-service gates still apply.