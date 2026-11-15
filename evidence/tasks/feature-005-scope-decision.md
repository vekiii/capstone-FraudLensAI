# Feature 005 T001 — team scope decision record

**Record prepared:** 2026-11-15 (repository task review; not an approval date)
**Status:** PENDING TEAM DECISION — T001 open; T002 blocked
**Requirements:** NFR-005, FR-015
**Proposal:** [ADR 001 — committed SQL changes to an ordered event log](../../specs/005-real-time-fraud-detection-mlops/proposals/001-cdc-and-streaming.md)

## Decision authority and evidence

The [constitution](../../.specify/memory/constitution.md) and root [contributor instructions](../../AGENTS.md) require explicit team approval, with benefit and schedule impact recorded, before implementing out-of-course additions. The [original project idea](../../original_idea.md) describes a four-member team and an approximately two-week delivery horizon. Neither that initial agreement nor the request to document T001 approves this later live infrastructure stack.

The [Feature 005 specification](../../specs/005-real-time-fraud-detection-mlops/spec.md), [plan](../../specs/005-real-time-fraud-detection-mlops/plan.md), [research](../../specs/005-real-time-fraud-detection-mlops/research.md), [three proposals](../../specs/005-real-time-fraud-detection-mlops/proposals/001-cdc-and-streaming.md), and [backlog](../../specs/005-real-time-fraud-detection-mlops/tasks.md) describe a proposal only. The root [handoff](../../next_work.md) also says team scope approval is pending. A repository search during this review found no Feature 005 team decision or named approval record. The current user request authorizes preparing this T001 document and stopping afterward; it supplies no approve, reject or defer decision by the team. This record does not infer consent from a specification, a request to start work, or a Git commit.

| Decision participant | Role in this decision | Evidence/status |
|---|---|---|
| Four-member project team | Scope decision authority under the constitution | Membership count appears in the original idea; names, individual positions and decision procedure for Feature 005 are not recorded here. |
| Requesting contributor | Requested T001 documentation | Current task request; no explicit team decision conveyed. |
| Technical reviewers/owners | Review affected data, model, API and operations boundaries | Names and reviews pending. No signature or confirmation attributed to Elena or any other member. |

## Proposed scope, benefit and cost for team review

| Proposed addition | Intended benefit | Added work or resource impact |
|---|---|---|
| PostgreSQL immutable live facts and durable state | One transactional source for a live producer, worker and read API. | New database, migrations, access roles, backups and recovery checks; existing SQLite batch path remains. |
| Debezium CDC and one-partition Kafka-compatible broker | Carry committed inserts to a replayable ordered stream. | Connector/slot, WAL and topic retention management; compatibility, restart, gap and duplicate tests. Redpanda versus Kafka remains a later pinned choice. |
| Single Python event-time worker and live model adapter | Reproduce `history-v1` features and publish versioned assessments for analyst review. | Durable buffer/checkpoint, watermark, late-event quarantine, parity and crash tests; approved same-hash model is still unavailable for real serving verification. |
| SQL/dbt, MLflow and monitoring | Reproducible offline datasets/model tracking plus operational visibility. | New services/dependencies, label isolation, deployment governance, metrics, role and secret handling. |

The [backlog](../../specs/005-real-time-fraud-detection-mlops/tasks.md) proposes **46 tasks across six phases**. This is a substantial expansion relative to the approximately two-week initial project horizon. No person-hour estimate, available hardware, service budget, revised milestone or assigned owner has been supplied; these impacts must be assessed by the team rather than invented here. The proposed first version limits throughput to one topic partition and one worker, retains human analyst decisions and does not claim measured latency, model quality or production readiness.

## Actual decision and conditions

**Actual team decision:** Not recorded. No approval, rejection or formal deferral was found or supplied. The effective implementation gate is **pending**. T001 is not complete, its checkbox stays unchecked, and dependent T002–T005 implementation must wait.

To complete T001, record the team's actual **approve / approve with conditions / defer / reject** decision, decision date, named participants or an attributable collective decision source, the exact approved or reduced component scope, anticipated benefit, schedule/resource impact, and any conditions or dissent. Link the supporting message, meeting record or signed review without committing private correspondence or credentials. If deferred or rejected, keep dependent work blocked or revise the feature scope and tasks through team review. An approval for this scope would not itself approve a model artifact, promotion, release or deployment.

If scope is approved, T002 must still choose and verify image/client versions, broker distribution, retention/outage horizon, secret method, database roles and resource limits. Later tasks must verify compatibility, data integrity, independent model evidence and operational behavior. None of those checks was run for T001.

## Review commands and outcome

- Inspected `AGENTS.md`, `next_work.md`, `.specify/memory/constitution.md`, `original_idea.md`, Feature 005 `spec.md`, `plan.md`, `research.md`, `tasks.md`, proposals and evidence register.
- Searched repository Markdown under `prompts/`, `evidence/` and `specs/005-real-time-fraud-detection-mlops/` for Feature 005 approval and decision records. No attributed approval record was found.
- `git diff --check` passed for tracked edits. A separate check of the two new Markdown files found 14 resolving local links and no trailing whitespace.
- Task files created: this decision record and [the original request](../../prompts/development/005-t001-scope-decision-request-2026-11-15.md). Task files updated: [ADR 001](../../specs/005-real-time-fraud-detection-mlops/proposals/001-cdc-and-streaming.md) and [root handoff](../../next_work.md). The tracked diff is two files with six added lines; Git does not include the two untracked new documents in `git diff --stat`. Four older, unrelated untracked drafts were preserved.
- Documentation-only review; no PostgreSQL, broker, model or application test was run. No commit or push was requested or made for T001.
