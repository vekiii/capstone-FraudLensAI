# Tasks: Project Foundation

**Input**: spec.md, plan.md, research.md, data-model.md, contracts/, quickstart.md.
**Status**: All tasks pending. This is a plan, not an implementation/evidence record.
**Tests**: TDD requested. Run each behavior test RED before its implementation, then GREEN and
relevant regression. Do not fabricate failures for mechanical setup or already-correct behavior.
**Format**: `- [ ] Tnnn [P?] [USn?] action with paths`. [P] is valid only after listed prerequisites.

## Phase 1: Setup (Shared Infrastructure)
- [ ] T001 Document team scope/approval and SDD/TDD instructions in AGENTS.md, referencing .specify/memory/constitution.md and original_idea.md; do not add out-of-course requirements.
- [ ] T002 Create evidence/README.md, evidence/templates/task.md and prompts/README.md covering real RED/GREEN outcomes, limitations, pending peer review, sanitized original development prompts in prompts/development/ and versioned application prompts in prompts/app/ (FR-008).
- [ ] T003 [P] Initialize backend dependencies and tests/lint config in pyproject.toml, .python-version and uv.lock; Python 3.12, FastAPI, Uvicorn, pytest, httpx, Ruff, jsonschema; configure backend/src import path and dev group. Record exact resolved versions in docs/decisions/foundation.md (FR-001).
- [ ] T004 [P] Initialize Vite vanilla TypeScript in frontend/package.json, frontend/package-lock.json, frontend/tsconfig.json, frontend/index.html and frontend/vite.config.ts with Vitest/jsdom, test/typecheck/build scripts and loopback /api proxy; record Node 22 patch and npm versions in frontend/README.md. No feature UI yet (FR-001).
- [ ] T005 Update .gitignore preserving existing entries; ignore .venv/, node_modules/, dist/, caches, .env files except .env.example, data/raw/, data/processed/ and local generated eval output; retain shared .agents and .specify and honor .specify/.gitignore. Document tracking policy in data/README.md (FR-009).

## Phase 2: Foundational (Blocking Prerequisites)
- [ ] T006 Write and execute RED validation tests in backend/tests/contracts/test_models.py using specs/001-project-foundation/contracts/schemas.json. Cover closed objects; IDs `^TX-[0-9]{3}$` and `^CASE-[0-9]{3}$`; nonempty account strings max 120; amount as nonnegative decimal string with exactly two fractional digits; currency three uppercase letters; UTC timestamps; finite score in [0, 1]; source fixture/rules/model; scorer_version nonempty max 80; explanation nonempty max 500; no labels. Save actual RED evidence under evidence/tasks/T006.md (FR-006/010).
- [ ] T007 Implement backend/src/fraudlens/contracts.py to satisfy T006 and the JSON Schema; test JSON Schema date-time format checking explicitly, run GREEN and record results in evidence/tasks/T006.md. Do not widen the schema silently (FR-006).

**Checkpoint**: Shared contracts and tooling ready. No real data/model needed. Tasks touching the
same file must stay sequential even if separate stories could otherwise proceed concurrently.

## Phase 3: US1 - Reproduce the Shared Environment (Priority: P1)
**Goal**: A teammate starts local fixture mode with no credentials or external AI services.
**Independent test**: quickstart.md setup + health + check/build commands; second-person result pending.
- [ ] T008 [US1] Write/run RED tests in backend/tests/integration/test_startup.py for health status/mode, default fixture settings, missing keys/model/corpus and rejection of unsupported APP_MODE; ensure startup does not call a provider (FR-001/002).
- [ ] T009 [US1] Implement backend/src/fraudlens/main.py and backend/src/fraudlens/settings.py with application factory, dependency injection point, local fixture settings and GET /api/health; satisfy T008 and record GREEN in evidence/tasks/T008.md (FR-002).
- [ ] T010 [US1] Add exact setup/run/check/build and prerequisite instructions to README.md, consistent with specs/001-project-foundation/quickstart.md; distinguish first lockfile creation from locked installs and no-network runtime from initial downloads (FR-001).
- [ ] T011 [US1] Execute documented automated checks/build and health smoke; record actual versions/results in evidence/tasks/T011.md, marking manual peer reproduction pending unless another teammate has actually performed it (SC-001).

## Phase 4: US2 - Inspect a Clearly Synthetic Case (Priority: P1)
**Goal**: First complete list → detail → synthetic score journey.
**Independent test**: Three cases, return navigation, empty list, unknown/malformed ID,
unavailable service/retry and stale selection.
- [ ] T012 [P] [US2] Write/run RED backend API and fixture-scorer tests in backend/tests/integration/test_cases.py and backend/tests/unit/test_fixture_scoring.py: three ordered cases; list/detail agreement; unknown CASE-999=404; malformed ID=422; empty items; invalid scorer/mismatch=500; closed payloads with no labels; generic error envelope (FR-003/004/005/006).
- [ ] T013 [P] [US2] Write/run RED fetch/DOM tests in frontend/tests/api.test.ts and frontend/tests/views.test.ts: valid/invalid payloads, 5-second timeout, loading/empty/error/not-found, retry, three selections and back navigation, visible synthetic notice and ignoring late previous-case results (FR-003/004/005).
- [ ] T014 [US2] Create exactly three synthetic case/transaction records in data/fixtures/cases.json, no labels or embedded ML claims; validate unique case/transaction IDs and deterministic ordering in backend/src/fraudlens/cases.py (data-model.md).
- [ ] T015 [US2] Implement fixture scorer and protocol in backend/src/fraudlens/scoring.py: `score(transaction: Transaction) -> RiskAssessment`; deterministic score and scored_at, source=fixture, scorer_version=fixture-v1, explanation explicitly illustrative. Enforce constraints from T006, and reject transaction identity mismatch in backend/src/fraudlens/cases.py (FR-004/006/007).
- [ ] T016 [US2] Add GET /api/cases and GET /api/cases/{case_id} to backend/src/fraudlens/main.py through case service in backend/src/fraudlens/cases.py; normalize 404/422/500 envelopes as contracts/api.md specifies, no traceback/path leakage; run T012 GREEN (FR-003/005/006).
- [ ] T017 [US2] Implement frontend/src/contracts.ts and frontend/src/api.ts boundary decoding matching schemas.json, timeout/cancellation and controlled errors; no unchecked casts as validation or hidden fallback scores (FR-005/006).
- [ ] T018 [US2] Implement frontend/src/main.ts, frontend/src/views.ts and frontend/src/styles.css with list/detail/back, source notice, loading/empty/error/not-found and retry; clear detail on selection change, cancel/ignore obsolete requests; use safe text rendering; run T013 GREEN (FR-003/004/005).
- [ ] T019 [US2] Run integrated regression and manual browser journey from specs/001-project-foundation/quickstart.md; record actual results and any manual scenarios not run in evidence/tasks/T019.md. Do not report fixture scores as ML evaluation (SC-002/003).

## Phase 5: US3 - Independent Contribution Boundaries (Priority: P2)
**Goal**: Prove adapter replacement and document reliable handoff.
**Independent test**: Alternate test scorer changes the score/source without altering service/API code.
- [ ] T020 [US3] Write/run RED substitution and failure tests in backend/tests/unit/test_scoring_boundary.py using an injected test-only rules scorer; require source=rules, correct transaction identity and rejection of out-of-range/nonfinite values. Keep the production fixture data unchanged (FR-007).
- [ ] T021 [US3] Complete injection/validation in backend/src/fraudlens/scoring.py and backend/src/fraudlens/cases.py as needed for T020; do not introduce a remote service or provider implementation; record GREEN or already-correct evidence in evidence/tasks/T020.md (SC-004).
- [ ] T022 [US3] Document owners A/B/C/D, replaceable boundaries, shared-contract change review and next specs 002–005 in docs/decisions/foundation.md. Describe approval recording for out-of-course requests and dependencies; assign no invented team-member names (FR-011).
- [ ] T023 [US3] Record the original implementation instruction and subsequent changes using prompts/development/001-foundation.md; verify evidence/README.md distinguishes app prompts, dev prompts, fixture tests, model evaluations and pending human review (FR-008/010).

## Phase 6: Polish & Cross-Cutting Concerns
- [ ] T024 Review all FR and SC coverage in specs/001-project-foundation/tasks.md and specs/001-project-foundation/spec.md; update genuine changes at their source, without weakening assertions to obtain green tests.
- [ ] T025 Have a second teammate follow README.md, record their actual result or pending status in evidence/tasks/peer-reproduction.md and fix reproducibility issues; SC-001 is not complete while this review is pending.
- [ ] T026 Run backend tests/Ruff, frontend tests/typecheck/build and git diff --check, inspect tracked files for secrets/large data and document all outcomes/limitations in evidence/tasks/foundation-validation.md; no commit/push/deploy unless requested.
- [ ] T027 Run Spec-kit convergence against specs/001-project-foundation/spec.md, plan.md and tasks.md, append remaining work to tasks.md if needed; remove the temporary Sync Impact Report in .specify/memory/constitution.md after its review, before committing.

## Dependencies & Execution Order
T001 → T002; T003 and T004 may proceed together after T002; T005 follows setup policy review.
T006 → T007 after backend tooling. Then T008 → T009 → T010 → T011 (US1).
After T007/T009 and frontend tooling, T012 and T013 can run in parallel in different subsystems.
Backend chain T012 → T014 → T015 → T016; frontend chain T013 → T017 → T018.
T019 joins both. T020 → T021 follows the scorer implementation; T022/T023 follow conventions
and are reviewed against actual code. T024–T027 follow all applicable story work.
T023 must preserve original instructions at start of implementation, then maintain the record;
do not reconstruct an allegedly original prompt after changes.

## Requirement Traceability
| Requirement | Tasks | Verification |
|---|---|---|
| FR-001 | T003/004/008–011/025 | Setup, health, locked checks and peer reproduction |
| FR-002 | T008/009/011 | No provider/data/model dependency |
| FR-003 | T012–019 | List/detail/navigation |
| FR-004 | T012/013/015/018/019 | Synthetic notice and explicit provenance |
| FR-005 | T012/013/016–019 | Error/empty/loading/retry/stale behavior |
| FR-006 | T006/007/012/015–017 | Schema and identity enforcement |
| FR-007 | T015/020/021 | Scorer substitution |
| FR-008 | T002/023 | Prompt/evidence convention review |
| FR-009 | T005/026 | Git tracking and secret/data exclusions |
| FR-010 | T006/008/012/013/020/024/026 | Actual RED/GREEN and regression records |
| FR-011 | T001/022 | Four-stream handoff and scope approval policy |

## Parallel Examples and Implementation Strategy
US1: T003 backend and T004 frontend setup are independent after evidence conventions exist.
US2: one contributor owns T012/014–016; another owns T013/017/018 against reviewed contracts.
US3: handoff documentation T022 can be drafted while T020/T021 execute, then reconciled before review.
For minimum delivery complete setup, foundations and US1, then the US2 journey, then the
substitution proof/handoff and final checks. Do not wait for ML or start later product features.
Suggested owners: A backend/contracts; B data/fixtures/validation; C frontend/journey;
D tooling/evidence/handoff, with review rotation. This temporary foundation split does not replace
the longer-term four product workstreams in original_idea.md.
