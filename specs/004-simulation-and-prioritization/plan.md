# Implementation Plan: Simulation Lab and Decision Intelligence

**Branch**: `004-simulation-and-prioritization` | **Date**: 2026-11-18 | **Spec**: [Feature 004](spec.md)

## Summary

Add the Simulation & Evaluation screen for one analyst to compare FIFO, highest score and weighted score per review minute over a frozen alert stream. A deterministic Python engine selects reviews under the same per-window budget and thresholds for all three strategies. A separate calculation joins evaluation labels after selection. The first complete flow uses bundled synthetic data and a portable run recipe. A future Feature 02 adapter feeds the same input contract once the producer can supply a compatible frozen score population.

## Technical Context

| Area | Plan |
| --- | --- |
| Language and dependencies | Use the locked Python 3.14, FastAPI and Pydantic stack and the Node 24, vanilla TypeScript and Vite frontend on this branch. |
| Storage | Versioned local scenario and outcome files. The browser can download and reopen a run recipe. The service has no run database or runtime dependency on the Feature 02 store. |
| Testing | pytest for replay math, source validation and HTTP contracts. Vitest for decoding, state and rendering. One local browser walkthrough for SC-004. |
| Platform | Existing loopback backend and Vite proxy. Reuse the project's locked install commands. |
| Scale | Up to 250 replay alerts and 12 windows per scenario for the first interactive version. Require a declared cohort within these bounds. |
| Performance | Synchronous local comparison with the existing frontend request timeout. Capture observed turnaround in the walkthrough. No production throughput target in this feature. |

## Constitution Check

| Gate | Before research | After design |
| --- | --- | --- |
| Team scope and minimum complexity | Approved replay and prioritization for the existing four-screen MVP. | Add only the Simulation & Evaluation view, with local scenarios and the existing stack. |
| Specification and TDD | Keep this phase to planning and trace implementation tasks to the spec. | [Quickstart](quickstart.md) identifies critical RED cases, then exact contract, regression and human acceptance checks. |
| Determinism and human authority | Calculate ordering, budgets and metrics in code. Keep decisions with the analyst. | The [contract](contracts/replay-v1.md) exposes advisory ordering and read-only replay of scenario inputs. Case state and score records are outside its write model. |
| Independent evaluation | Keep labels and future facts outside decisions. | The engine receives only label-free inputs. Evaluation joins private outcomes after selections. CI should verify label-only changes preserve all selections. |
| Parallel work and provenance | Fixture-first with a replaceable boundary. | Scenario source, score kind, assumptions and exact recipe versions are explicit. Feature 02 integration has its own evidence gate. |
| Reproducibility and evidence | Record design choices and actual checks. | Preserve original prompt and design evidence. Keep user-downloaded recipes local. Record test outcomes and actual peer walkthrough during implementation. |

Both design reviews passed during planning. The [acceptance matrix](../../evidence/tasks/feature-004-acceptance.md) records the completed executable product acceptance and code review.

## Project Structure

### Documentation

- [Research decisions](research.md)
- [Data model](data-model.md)
- [Scenario and HTTP contract](contracts/replay-v1.md)
- [Validation quickstart](quickstart.md)
- Generate `tasks.md` in the subsequent `speckit-tasks` phase.

### Source Code

```text
backend/
├── src/fraudlens/
│   ├── main.py                         # register the simulator router
│   └── simulation/
│       ├── models.py                   # strict transport and scenario types
│       ├── scenarios.py                # validate and resolve frozen inputs
│       ├── replay.py                   # label-free queue and budget logic
│       └── api.py                      # orchestrate replay and outcome join
└── tests/
    ├── unit/test_simulation_replay.py
    ├── contracts/test_simulation_contracts.py
    └── integration/test_simulation_api.py
data/fixtures/simulation/               # versioned scenarios and separate outcomes
frontend/
├── src/main.ts                         # entry to the Simulation & Evaluation view
├── src/simulation.ts                   # controls, run recipe and result display
└── tests/simulation.test.ts
```

**Structure decision**: Add a simulation module to the current application and register it at the existing entry points. Keep the simulator's HTTP contract independent of the frontend framework for later integration with the team's chosen frontend. Preserve the existing case API and default case entry view.

## Delivery order

| Slice | Scope | Requirements and checks |
| --- | --- | --- |
| 1. Fixture and pure replay | Scenario validation, fixed-window admission and backlog, three exact orderings and budget enforcement. | FR-001–004, FR-006, FR-009. SC-001 and SC-002 for ordered selections and eligibility. |
| 2. Outcomes and reproducibility | Evaluate after replay, expose provenance and exact versioned comparison, export and reopen the recipe. | FR-005–009. SC-001 outcome counts and SC-003. |
| 3. Simulation screen | Add scenario selection, controls, a three-strategy comparison, per-window ordering and input inspection. Include unavailability and stale-result handling. | FR-001–002, FR-005, FR-007–009. SC-004 and case regressions. |
| Later integration | Validate a published Feature 02 export and map it to the simulator input. Agree on the frontend used for the capstone merge. | [Producer gate](research.md#batch-score-source). A bundled replay is the acceptance path for this feature. |
