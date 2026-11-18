---
description: "Implementation tasks for Simulation Lab and Decision Intelligence"
---

# Tasks: Simulation Lab and Decision Intelligence

**Input**: [Specification](spec.md), [plan](plan.md), [research](research.md), [data model](data-model.md), [contract](contracts/replay-v1.md) and [quickstart](quickstart.md).

**Tests**: Use RED → GREEN → REFACTOR for critical behavior. Record the intended RED failure, GREEN result and regression commands under `evidence/tasks/`. Mechanical setup has no RED requirement.

**Format**: `[ID] [P?] [Story?]`. `[P]` identifies work that can run alongside the tasks named under Parallel Execution once the stated prerequisites are complete. Paths in task descriptions are repository-relative.

## Phase 1: Setup

**Purpose**: Verify this branch can run using the existing foundation and lockfiles.

- [x] T001 Select Feature 004 in the PowerShell session and run the locked setup from `specs/004-simulation-and-prioritization/quickstart.md`. Run `backend/tests/integration/test_startup.py` and `frontend/tests/api.test.ts` as a baseline. Record versions, commands and results in `evidence/tasks/feature-004-setup.md`.

## Phase 2: Foundational prerequisites

**Purpose**: Establish a frozen, validated fixture boundary that every story can exercise without Feature 02.

- [x] T002 [P] Author the hand-calculated `review-capacity-demo` v1 scenario in `data/fixtures/simulation/review-capacity-demo-v1.json` with the exact A–E scores, costs, equal weights, defaults and tie from the quickstart. Add time basis, score provenance, assumptions with stable IDs and a nullable generation seed. Store only the private outcome mapping and its matching scenario identity in `data/fixtures/simulation/review-capacity-demo-v1.outcomes.json`.
- [x] T003 [P] Add RED tests in `backend/tests/contracts/test_simulation_contracts.py` using inline or temporary scenario data for duplicate/mismatched identifiers, unresolved assumption references, invalid UTC/windows, invalid score/weight/minutes, size bounds, foreign or duplicate outcome IDs and duplicate revisions with conflicting content. Verify canonical fingerprints match across equivalent decimal, UTC precision and unordered input representations, and change when outcome content changes. The RED run must fail for missing validation or fingerprint behavior.
- [x] T004 Implement the strict types and local catalog in `backend/src/fraudlens/simulation/models.py` and `backend/src/fraudlens/simulation/scenarios.py`. Enforce “positive integer `scenario_version` and SHA-256 `content_sha256`”, “strictly increasing `window_starts`”, “The first start equals the horizon start”, “1–12 starts inside the horizon and at most 250 alerts”, “Unique `alert_id`, `available_at` inside the horizon, finite score in [0,1], positive scenario weight and positive whole estimated review minutes” and “Reject duplicate or foreign IDs” for separately keyed outcomes. Enforce closed payloads, ID format, one scenario-wide score source/version, resolved assumption references and canonical hash rules from the contract. Load the bundled facts and outcomes under the trusted catalog root. Verify T003 and a successful load of the T002 fixture.

**Checkpoint**: The fixture resolves to an immutable catalog revision and the replay can receive validated alert facts separately from outcomes.

## Phase 3: User Story 1 — Compare review strategies (P1)

**Goal**: Select a frozen fixture from the app and compare the three strategies with the scenario's default threshold and budget.

**Independent test**: At threshold 0.30 and budget 2, compare A / B / C,E against the quickstart. Verify all three ordered selections, missed-positive reasons and backlogs (SC-001). Also verify the three-alert acceptance example in the specification.

### Tests first

- [x] T005 [P] [US1] Add RED tests for the three-alert and A–E examples, threshold equality, exact weighted comparisons and arrival-time/ID tie-break in `backend/tests/unit/test_simulation_replay.py`. Cover arrival at window start, no review before availability, exclusive horizon end, budget reset, scanning past a case that cannot fit, carry-over, late arrivals in final backlog and each alert reviewed at most once per strategy. Assert queue ordering and used minutes (FR-002–004, FR-006, SC-001–002).
- [x] T006 [P] [US1] Add RED endpoint tests against the app factory in `backend/tests/integration/test_simulation_api.py` for catalog metadata and ordering, comparison response and counts, no per-alert outcome fields, no case mutations, strict bad payloads or contract version (422), unavailable scenario/digest or strategy version (409), and sanitized service failure (500). Assert shape and ordering against `specs/004-simulation-and-prioritization/contracts/replay-v1.md` (FR-001, FR-005–009).
- [x] T007 [P] [US1] Add RED tests in `frontend/tests/simulation.test.ts` using a fake simulation client for entering the view, choosing a scenario, displaying its provenance and rendering the three default results. Check that a malformed catalog or comparison response and a failed request show a readable error with no comparison (FR-001, FR-005, FR-008–009).

### Implementation

- [x] T008 [US1] Implement the label-free engine in `backend/src/fraudlens/simulation/replay.py`. Admit eligible scores inclusively, rank FIFO, highest score and exact weighted score per minute, and scan each window against an independent fresh budget. Return “ranked candidate IDs in order, reviewed IDs in selection order and total review minutes used” and final pending IDs in availability and ID order. Pass T005 (FR-002–004, FR-006, SC-001–002).
- [x] T009 [US1] Implement recipe validation and response models in `backend/src/fraudlens/simulation/models.py`. Join outcomes only after the replay in `backend/src/fraudlens/simulation/api.py`. Return threshold and backlog misses separately, horizon and reviewed unknown counts, null outcomes for nonempty unlabeled scenarios, and zero counts for an empty scenario. Register the two routes through `backend/src/fraudlens/main.py` with a simulator-specific version error. Pass T006, including exact defaults, recipe echo, sanitized failures, label-free public payloads and unchanged case state (FR-001, FR-005–009, SC-001).
- [x] T010 [P] [US1] In `frontend/src/simulation.ts`, implement the catalog/comparison client boundary, strict decoding, labeled synthetic provenance and the three-strategy results table. Use the catalog defaults on the first comparison. Register the Simulation & Evaluation entry in `frontend/src/main.ts` and keep the existing Cases entry as the default. Pass T007 against the same public contract used by T009 (FR-001, FR-005, FR-008–009).
- [x] T011 [US1] Run one fixture-only default comparison through the normal FastAPI and Vite entry points using `specs/004-simulation-and-prioritization/quickstart.md`. Verify the A / B / C,E selections and counts match SC-001. Run the new automated checks and record RED, GREEN and any refactor results in `evidence/tasks/feature-004-us1.md`.

**Checkpoint**: An analyst can run the default comparison and see the three strategies side by side.

## Phase 4: User Story 2 — Explore capacity and threshold (P2)

**Goal**: Change the score threshold or budget in the screen and see the resulting change in coverage.

**Independent test**: Replay the same two-window test stream after changing one setting at a time. Check next-window eligibility, mutually exclusive reasons for misses and the review of a smaller case when the first one exceeds the available budget (SC-002).

### Tests first

- [ ] T012 [P] [US2] Add two-window and edge-case endpoint regressions in `backend/tests/integration/test_simulation_api.py`. Use the same scenario reference for repeated requests and change one setting at a time. Verify differing selections and missed reasons, final backlog, zero budget, empty scenario and partial or wholly unknown outcomes. These checks may already pass against the Phase 3 implementation and should be recorded as regression checks if they do.
- [ ] T013 [P] [US2] Add RED tests in `frontend/tests/simulation.test.ts` for editing each setting, rejecting invalid scores or minutes, showing zero and unavailable outcomes distinctly, and clearing a stale comparison after settings or scenario changes. Use a late result that resolves even after cancellation to prove the current-request guard.

### Implementation

- [ ] T014 [US2] Add threshold and budget controls, validate “budget in whole minutes per window” with a nonnegative safe integer, and submit the exact threshold decimal string in `frontend/src/simulation.ts`. Display threshold versus backlog misses, explain missing outcome coverage and ignore stale successes or failures after edits, resubmission or navigation. Pass T012 and T013 and record the focused results in `evidence/tasks/feature-004-us2.md` (FR-002, FR-003, FR-005, FR-009, SC-002).

**Checkpoint**: An analyst can change settings and explain the resulting differences without mixing results from two runs.

## Phase 5: User Story 3 — Reproduce and explain a run (P3)

**Goal**: Save and reopen a comparison recipe and inspect the inputs used to rank any admitted alert.

**Independent test**: Reopen a saved recipe after refreshing the app and compare ordered selections, counts and backlog. Repeat the policy with a test variant that changes labels alone. The ordering must stay identical (SC-003).

### Tests first

- [ ] T015 [P] [US3] Add API regressions in `backend/tests/integration/test_simulation_api.py` for an exact canonical recipe round trip and a separate label-only variant. Verify all ordered windows, reviewed IDs and final backlog are identical for the variant and only outcome-derived counts may differ. Verify the changed fingerprint and 409 when a recipe names a missing revision, wrong digest or unavailable strategy version (FR-006–007, SC-003).
- [ ] T016 [P] [US3] Add RED frontend tests in `frontend/tests/simulation.test.ts` for JSON download and reopen, invalid and unavailable recipes, a late result after navigation, and per-window ranking inspection. Verify score, weight, estimated duration and linked assumption labels are visible without exposing raw outcome labels (FR-007–009).

### Implementation

- [ ] T017 [US3] Add exact recipe download and reopen and an inspectable per-window ordering in `frontend/src/simulation.ts`. Submit the saved recipe unchanged, retain its scenario reference and strategy versions, display unavailable versions clearly and require an explicit new run to use different settings. Show ranked and reviewed order, provenance and scenario assumptions. Pass T015 and T016, and record results in `evidence/tasks/feature-004-us3.md` (FR-007–009, SC-003).

**Checkpoint**: A reviewer can explain the order and reproduce the same comparison from a saved recipe.

## Phase 6: Final verification and handoff

**Purpose**: Verify the fixture flow through the app and capture reproducible evidence.

- [ ] T018 [P] Run the full backend suite and Ruff as listed in `specs/004-simulation-and-prioritization/quickstart.md`. Include existing case and health endpoint regressions and record actual output in `evidence/tasks/feature-004-backend-validation.md`.
- [ ] T019 [P] Run the full frontend suite, TypeScript typecheck and production build as listed in `specs/004-simulation-and-prioritization/quickstart.md`. Include the existing Cases navigation and stale request regressions and record actual output in `evidence/tasks/feature-004-frontend-validation.md`.
- [ ] T020 Run the teammate browser walkthrough in `specs/004-simulation-and-prioritization/quickstart.md` (SC-004). Record the actual reviewer, revision, versions, settings, scenario digest, observed turnaround, budget change and recipe rerun in `evidence/tasks/feature-004-browser-acceptance.md`. Retain any unverified step as pending until the corresponding check occurs.
- [ ] T021 Confirm coverage of FR-001–009 and SC-001–004 against actual evidence and update `next_work.md` and `evidence/tasks/feature-004-acceptance.md`. Record remaining integration and human review status. Describe fixture outcomes as synthetic replay results.

## Dependencies and execution order

| Phase | Prerequisites and completion order |
| --- | --- |
| Setup and foundation | T001 → T002 and T003 → T004. |
| US1 | T004 → T005, T006 and T007. T005 → T008. T006 and T008 → T009. T007 → T010. T009 and T010 → T011. |
| US2 | T011 → T012 and T013 → T014. |
| US3 | T014 → T015 and T016 → T017. |
| Final verification | T017 → T018 and T019 → T020 → T021. |

The stories build on one screen and a single replay contract. Each checkpoint has a focused test that can be run without the later stories. Feature 02 integration is deferred until the [producer gate](research.md#batch-score-source) is met. Its active and filtered cases list must never supply a replay denominator.

| Spec coverage | Main implementation and verification tasks |
| --- | --- |
| FR-001 Frozen scenarios and provenance | T002–T004, T006, T009–T011 |
| FR-002 Common threshold and budget | T005, T008, T012–T014 |
| FR-003 Availability, capacity and carry-over | T005, T008, T012 |
| FR-004 Strategy calculation and ties | T005, T008, T011 |
| FR-005 Outcome and backlog metrics | T006, T009, T011–T014 |
| FR-006 Point-in-time inputs and outcome isolation | T003–T006, T008–T009, T015 |
| FR-007 Run identity and reproducibility | T003–T004, T006, T009, T015–T017 |
| FR-008 Inspectable and advisory ordering | T006–T010, T016–T017, T020 |
| FR-009 Validation, unknown outcomes and empty results | T003–T004, T006–T007, T009, T012–T017 |
| SC-001 Exact strategy comparison | T005–T006, T011 |
| SC-002 Budget, eligibility and uniqueness | T005, T012–T014 |
| SC-003 Rerun and label invariance | T015–T017, T020 |
| SC-004 Teammate walkthrough | T020 |

## Parallel execution examples

- **Foundation**: One contributor authors the fixture in T002 while another writes source validation RED tests from temporary data in T003.
- **US1**: Run T005, T006 and T007 in parallel. Once T007 has a valid RED result, T010 can proceed against contract-shaped mock responses while T008 and T009 finish the engine and API.
- **US2**: Write endpoint regressions in T012 alongside the independent browser-state RED tests in T013.
- **US3**: Verify replay invariants in T015 alongside recipe and order-inspection RED tests in T016.
- **Final verification**: Run the backend and frontend suites in T018 and T019 independently before the teammate walkthrough. Coordinate shared `next_work.md` updates at the handoff.

## Implementation strategy

1. Deliver **T001–T011** as the first demo slice. Show the bundled comparison at default settings through the app and verify its counts before moving on.
2. Add editable settings and edge-case coverage in **T012–T014**.
3. Add reproducibility and order inspection in **T015–T017**.
4. Finish with actual automated and browser evidence in **T018–T021**. The first demo slice establishes US1. Full Feature 04 acceptance includes US2 and US3.
