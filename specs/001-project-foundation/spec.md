# Feature Specification: Project Foundation

**Feature Branch**: `initialization` (directory: `001-project-foundation`)
**Created**: 2026-11-11
**Status**: Implemented through T023; phase 6 verification recorded in ../../evidence/tasks/phase-06-handoff.md. Peer reproduction and human review pending.
**Input**: Elaborate initialization step 3 using original_idea.md and approved principles.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reproduce the shared environment (Priority: P1)
As a teammate, I can follow a documented setup and run the foundation without financial
datasets, trained ML or an LLM key, so all four members can begin useful development.

**Why this priority**: Removes dependence on ML experiments and provider availability.
**Independent Test**: A second teammate follows the quickstart and records actual outcomes.
**Acceptance Scenarios**:
1. **Given** a clean checkout and documented prerequisites, **When** setup is followed,
   **Then** the local application starts and identifies its synthetic demonstration mode.
2. **Given** no model, corpus or credentials, **When** the application starts,
   **Then** the foundation still operates without contacting external AI services.
3. **Given** a fresh checkout, **When** documented checks run with locked dependencies,
   **Then** checks and a distributable frontend build can be reproduced.

### User Story 2 - Inspect a clearly synthetic case (Priority: P1)
As a demo analyst, I can select a case and inspect its transaction and score before real
scoring exists.

**Why this priority**: Smallest visible product journey.
**Independent Test**: Inspect all three sample cases and exercise empty, unavailable and
unknown-case outcomes.
**Acceptance Scenarios**:
1. **Given** three fixture cases, **When** I open the list, **Then** their identifiers and
   scores appear with a persistent synthetic-data notice.
2. **Given** a selected case, **When** its details load, **Then** transaction, score, source
   and explanation match the selected item and I can return to the list.
3. **Given** an unknown case, **When** requested, **Then** a controlled not-found outcome
   appears; no old case is presented as the requested case.
4. **Given** an empty collection or unavailable service, **When** cases are requested,
   **Then** an explicit empty/error state appears and retry can recover when available.

### User Story 3 - Develop independently with trustworthy boundaries (Priority: P2)
As a contributor, I can replace scoring and find instruction/evidence conventions so my
work remains compatible and reviewable.

**Why this priority**: Enables subsequent parallel work without speculative product code.
**Independent Test**: Substitute a test scorer without modifying case delivery and trace a
task to its requirement and evidence convention.
**Acceptance Scenarios**:
1. **Given** a substitute scorer honoring the same contract, **When** used by case delivery,
   **Then** delivery still works and identifies the new result source.
2. **Given** a task, **When** evidence is recorded, **Then** original instructions, commands,
   actual outcomes, limitations and review status can be linked.
3. **Given** a proposed out-of-course capability, **When** its task is reviewed,
   **Then** implementation requires recorded team approval and schedule impact.

### Edge Cases
- Unknown/malformed identifiers, empty collections, transient service failure and retry.
- A changed selection during loading must not display stale data as the newly selected case.
- Out-of-range scores and score/transaction identity mismatches are rejected.
- Missing keys, production datasets and models do not block fixture-mode startup.
- Synthetic scores do not imply calibrated risk or known evaluation labels.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: Provide reproducible setup, start, check and build instructions.
- **FR-002**: Operate using small synthetic examples without external AI services.
- **FR-003**: Provide a case list, detail view and return navigation.
- **FR-004**: Identify the source of each score; label fixture scores synthetic and never
  present them as calibrated probabilities.
- **FR-005**: Represent loading, empty, error and unknown-case states explicitly.
- **FR-006**: Document and enforce shared data contracts; reject invalid scores and mismatched
  transaction identities before successful delivery.
- **FR-007**: Permit scorer replacement without changing case selection or delivery.
- **FR-008**: Define where original development instructions, app prompts and real execution
  evidence belong; never fabricate completed checks.
- **FR-009**: Version shared instructions/specifications and exclude secrets, large datasets,
  generated dependencies and machine-local state.
- **FR-010**: Develop business behavior test-first, including negative and regression checks.
- **FR-011**: Document boundaries/dependencies of four subsequent workstreams and require team
  approval for out-of-course additions.

### Key Entities
- **Transaction**: Synthetic transfer ID, time, bank-qualified account references, amount and
  currency; no label or invented customer profile.
- **RiskAssessment**: Transaction reference, bounded score, source, version, scoring time and
  explanation; distinguishes fixture, rule and future model results.
- **Case**: Stable identifier linking one transaction and its assessment; read-only here.
- **ExecutionEvidence**: Task/requirement, original instructions, commands, actual results,
  limitations and review status.

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: A second teammate starts the demo from documented prerequisites without a model,
  production dataset or provider key and records actual execution.
- **SC-002**: All three sample cases can be selected, inspected and revisited with correct
  identities and synthetic-source notices on both views.
- **SC-003**: Every specified negative scenario has automated coverage; errors never appear
  as successful cases or zero-risk conclusions.
- **SC-004**: A substitute scorer passes boundary checks without changes to case delivery.
- **SC-005**: Every implementation task maps to a story or cross-cutting requirement and a
  verification method. Completion evidence reports actual checks.

## Assumptions
- Local single-user educational demo, synthetic data only. No production authentication,
  tenant isolation or secure hosting claim. Loopback is the foundation boundary.
- Four screens remain the full MVP scope; foundation only establishes the list/detail journey.
- Dataset download, ML training, RAG, providers, analyst disposition writes, persistent audit,
  real prioritization and simulation belong to later specifications.
- Fixture scores are illustrative constants and contain no ground-truth labels.
- Preserve the existing initialization branch. Technical artifacts are in English, aligned
  with the course; user-facing explanations are Serbian Latin.

## Acceptance update - 2026-11-12
Earlier pending acceptance statements above are superseded by the team's reported
joint setup verification and code/contracts/evidence review. T025/SC-001 and T028
are complete; see evidence/tasks/peer-reproduction.md and human-review.md from the
repository root. No additional automated/browser executions claimed by this update.
