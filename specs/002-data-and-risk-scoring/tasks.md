# Tasks: Feature 002 — Data Ingestion and Risk Scoring

Generated 2026-11-13 (Europe/Belgrade). Current status: **T001–T016 complete; Phase 3 local import verified on the declared IBM v8 source and its final streaming-byte cleanup rerun.** [Collective final-byte approval and matching hashes](../../evidence/tasks/feature-002-t007-t008-team-review-2026-11-13.md#collective-final-byte-approval-conveyed-by-the-user); [complete RED/GREEN and actual-source import evidence](../../evidence/tasks/feature-002-import-identity.md#phase-3-final-cleanup--2026-11-13). Later v2 runtime integration and T060 full documentation remain unimplemented.

Historical proposal-stage T006–T008 continuation (superseded by technical resolution): [independent source investigation](../../evidence/tasks/feature-002-source-investigation.md) and [concrete mapping/v2 review packet](proposals/README.md) prepared. Public v8/license metadata and account direction now have primary evidence; local release binding, clock/label policy and actual owner decisions remain pending. No gate is closed by proposal validation; authoritative contracts and application code remain unchanged.

Historical technical resolution before final approval: [verified v8 reference, applied amendments and actual checks](../../evidence/tasks/feature-002-technical-resolution.md). T006 is complete. The later [joint team decision relayed by the user](../../evidence/tasks/feature-002-t007-t008-team-review-2026-11-13.md) adopts the technical direction, but final changed bytes and component review have not been confirmed by the producing/affected consumers. At that earlier stage T007/T008 remained unchecked; the collective approval linked in the current status above has since closed them. Import and v2 application integration remain disabled/unimplemented.

**Input:** current `specs/002-data-and-risk-scoring/spec.md`, `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, both contracts and `contracts/schemas.json`; constitution, approved original idea, Foundation v1 API/schema, current code/tests and `docs/decisions/foundation.md`. The historical review at `prompts/development/002-review.md` is background; current spec/plan govern. No application implementation, download, training or runtime check was performed to generate this list.

**Workflow:** local `.agents/skills/speckit-tasks/SKILL.md` and resolved `.specify/templates/tasks-template.md`. Explicit PowerShell selection: `$env:SPECIFY_FEATURE_DIRECTORY = 'specs/002-data-and-risk-scoring'`. Feature selection does not change the Git branch. Task IDs are local to Feature 002; prefix evidence with feature-002 to avoid Foundation T-number ambiguity.

## Execution and evidence rules

- Format: unchecked checkbox, sequential ID, optional [P], story tag in story phases, kind and concrete repository-relative paths. `Depends: none` or explicit prerequisite IDs defines readiness; transitive prerequisites also apply. [P] permits only the named ready tasks in different files; it is not permission to parallelize shared-module edits.
- Each RED task writes/runs tests before its GREEN consumer. RED must fail for the intended missing behavior using valid test collection, not missing dependencies, import-time exceptions or environment failures. GREEN runs those tests and relevant v1 regressions; refactor only while retaining the assertions. A GREEN task depending on another GREEN inherits its original RED tests.
- A task closes only after its own deliverable and evidence exist. Every unit records its actual original prompt, task/FR/SC, working revision, source/mapping/protocol/artifact/lock hashes as applicable, exact commands/exits/results, intended and actual RED reason, GREEN/regression outcomes, limitations, contributor and review state using `evidence/templates/task.md`. The slice evidence paths below are future deliverables, not existing results.
- Freeze/review shared contracts before dependent implementation, update producer/consumer validators/examples/negative tests together, and never loosen v1 to fit v2. If audit exposes a design/schema conflict (including amount, account, timestamp precision or identifier bounds), stop affected work and resolve it through T007/T008 before proceeding.
- T003 can finish recording an unavailable assignment; compliance remains `pending_requirements_unavailable`. That state alone does not block independent approved Feature 002 work or authorize a course-compliance claim.
- If no authorized source exists, T006 is `pending_source_unavailable`, T007 is `pending_mapping_review`, and dependent IBM mapping/import/pilot/protocol/evaluation/reproduction stay pending. T004–T005 may use explicitly authored source-shaped test inputs; do not publish them as observed IBM fields/counts. Independent document review can continue, but dependent implementation waits for its applicable gate.
- Absent actual consumer/human review means `pending_consumer_review` / `pending_human_review`; absent another teammate's run means `pending_independent_reproduction`. Ineligible classes, failed fitting, dependency/resource failure or divergent reproduction remain explicit incomplete/unresolved states, never model-delivery success. Zero alerts and no measured improvement remain valid reported outcomes.
- Do not introduce RAG, LLM scoring, a new screen, automatic account interventions, public ingestion/training endpoints or an extra model family. Calibration/AutoML are deferred in the initial protocol. No automatic commit or push.

## Path conventions and planned files

All paths are relative to the repository root. Existing Foundation modules/tests and both feature contracts were inspected during generation. New module/test/config/evidence paths are **planned**, not discovered implementation. The complete classified path inventory and static validation observations are in `evidence/tasks/feature-002-task-plan-validation.json`; the documentation-only validator is `evidence/tasks/feature-002-task-plan-validation.ps1`.

New source modules follow the plan: `backend/src/fraudlens/data_contracts.py`, `data_import.py`, `data_store.py`, `feature_history.py`, `rule_scoring.py`, `model_scoring.py`, `evaluation.py`, `explanations.py` and `pipeline_cli.py` (all under the same package). Tests go in the existing backend unit/contracts/integration and frontend tests directories. `data/mappings/ibm_hi_small_v1.json` and `evals/protocols/feature_002_v1.json` are new reviewed configurations; create their directories only during the appropriate later task. Do not create placeholder source data or generated artifacts now.

## Phase 1: Setup and evidence boundaries

Preserve Foundation and start honest evidence records. No business RED is required for mechanical setup. Record the Phase 2 source outcome separately from source-data availability.

- [x] T001 SETUP — Preserve the working diff, read AGENTS.md then next_work.md, select Feature 002 in PowerShell, and start the implementation prompt/command ledger in `evidence/tasks/feature-002-implementation.md` using `evidence/templates/task.md`; link the actual original prompt in `prompts/development/002-implementation-prompts.md`. Record task/FR/SC, revision, environment and human-review state per unit (FR-026). (Depends: none.)

- [x] T002 SETUP — Add `/data/artifacts/` to `.gitignore` before any artifact generation; verify raw/processed/artifacts and large evaluation outputs are ignored and absent from tracked files, retaining shared skills and the original fixture. Record actual ignore commands in `evidence/tasks/feature-002-artifacts-explanations.md` (FR-018). (Depends: T001.)

- [x] T003 GATE — Search local project references for the authoritative Phase 2 assignment and record its provenance/traceability or `pending_requirements_unavailable` in `evidence/tasks/feature-002-phase2.md`; the Feature 002 checklist and Foundation Phase 2 handoff are not substitutes. No compliance percentage or team approval may be inferred. This gate blocks compliance claims, not independent in-scope behavior work (FR-026). (Depends: T001.)

## Phase 2: Foundational — inspection, source audit, mapping and consumer gates

Source-independent inspection is the only application behavior that can proceed before actual source mapping is reviewed. Audit (T006), mapping (T007) and consumer review (T008) are separate deliverables. T006/T007 cannot close on invented observations. The current task-generation session executes none of these future tasks.

- [x] T004 RED — Write source-independent inspection tests in `backend/tests/unit/test_source_inspection.py`: inaccessible source, duplicate headers including normalized/BOM/case/whitespace collisions, ambiguous aliases, missing roles, unknown/target-like columns, invalid bytes, unsupported encoding, header-only/empty and truncated quoted records, multiline records and partial parse after valid rows. Assert controlled nonzero result, unchanged source and no active-state change; missing inspect behavior must fail in a test body, not collection/setup (FR-001–002). (Depends: T001, T002.)

- [x] T005 GREEN — Implement read-only streaming inspection in `backend/src/fraudlens/data_import.py` and only the inspect command in `backend/src/fraudlens/pipeline_cli.py`: explicit local path/release/license, SHA-256/size, encoding/dialect, observed schema, field forms, record/label/time/currency summaries and ambiguity report. Return bounded machine/human results without secrets, raw rows or row-level labels; no download, inferred mapping or activation. Record RED/GREEN in `evidence/tasks/feature-002-source-audit.md` (FR-001–002). (Depends: T004.)

- [x] T006 GATE — Audit only an authorized locally supplied IBM HI-Small file and its source-data license into `evidence/tasks/feature-002-source-audit.md`: actual release/member/hash/size, headers/dialect/encoding, missingness, timestamp span/granularity/timezone evidence, directional amount/currency forms and label meanings/counts/denominators. If absent, record `pending_source_unavailable`, command/path scope and needed input; leave observed fields empty. Source-shaped tests are not IBM observations (FR-001–003, SC-001). (Depends: T005.)

- [x] T007 GATE — Freeze the separately reviewed source mapping in `data/mappings/ibm_hi_small_v1.json` only after T006 has real source evidence: roles/aliases, unknown-column policy, decimal range/scale/zero, currency syntax, timezone/precision, label roles, namespace/member/pre-filter ordinal, identity/collision and mapping/time hashes. Record actual mapping reviewer/date/decision in `evidence/tasks/feature-002-source-audit.md`. Ambiguity or unavailable source leaves `pending_mapping_review`; do not invent source columns (FR-001–004). (Depends: T006.)

- [x] T008 GATE — Complete producer/affected-consumer review of `specs/002-data-and-risk-scoring/contracts/api.md`, `specs/002-data-and-risk-scoring/contracts/data-and-scoring.md` and `specs/002-data-and-risk-scoring/contracts/schemas.json` under `docs/decisions/foundation.md`; record rationale, compatibility/version matrix, exact reviewed hashes, real reviewers/date and unresolved migrations in `evidence/tasks/feature-002-contract-review.md`. Include data/scoring owner, frontend/API owner and affected investigation/priority consumers; preserve v1, fix contradictions through reviewed v2 changes before implementation. No invented approvals (FR-023, FR-026). (Depends: T007.)

## Phase 3: US1 — import a trustworthy, traceable dataset (P1; first increment)

**2026-11-13 Phase 3 status:** the user first authorized synthetic T009–T011 RED preparation while final-byte review was pending. [Twenty tests collected and failed for intended missing behavior](../../evidence/tasks/feature-002-import-identity.md). The user subsequently [confirmed collective final-byte approval](../../evidence/tasks/feature-002-t007-t008-team-review-2026-11-13.md#collective-final-byte-approval-conveyed-by-the-user), completing T007/T008. The initial 20-case set was partial; the [79-case RED matrix](../../evidence/tasks/feature-002-import-identity.md#completed-t009t011-red-matrix--2026-11-13) now covers the specified cases and fails for intended missing T013/T014 behavior. T009–T011 are complete as RED tasks. [T012–T016 GREEN and actual-source import evidence](../../evidence/tasks/feature-002-import-identity.md) covers the source-bound CLI, IBM v8 import and exact replay. The subsequent cleanup protects the hash-to-parser byte binding and repeats T016 on a new local database. T017 remains the next open task.

Goal: exact canonical facts, stable identity, private labels and repeatable completed imports.

Independent test: reviewed source-shaped samples with valid/rejected/label-ineligible/equal-valued/different-bank rows reconcile 100% of records, preserve precision, and survive interrupted retry with no incomplete active import. T016 separately requires the declared real source.

- [x] T009 [P] [US1] RED — Write canonical parsing/accounting tests in `backend/tests/unit/test_data_import.py` for exact directional paid/received Decimal text, bank-qualified direction, raw/UTC timestamps, zero/supported scale and unsupported precision/overflow/negative/nonfinite/missing currency/timezone; all malformed/header/encoding/partial-file cases from T004; every record's event and private label status. Valid facts with missing/invalid/unsupported labels remain operational; unknown fields never become predictors (FR-001–003, SC-001). (Depends: T008.)

- [x] T010 [P] [US1] RED — Write stable identity tests in `backend/tests/unit/test_data_identity.py`: one-based CSV ordinal before filtering, quoted multiline as one record, distinct equal-valued rows, bank distinctions, rejected-row stability, label-only edits, raw-hash/mapping/release changes, source member domain separation and deliberate digest/fact collisions. Repeat imports cannot duplicate events/cases; arbitrary reordered files get no guessed identity guarantee (FR-003–004, SC-001). (Depends: T008.)

- [x] T011 [P] [US1] RED — Write staged-import repository tests in `backend/tests/integration/test_data_store.py` for schema-version mismatch, private-label access exclusion from operational projection, row reconciliation, retry/idempotency, changed-version coexistence, injected interruption/parser failure and restart. No incomplete import becomes selectable and an existing complete version survives (FR-002, FR-004, FR-009, SC-001). (Depends: T008.)

- [x] T012 [US1] GREEN — Create internal canonical/import models in `backend/src/fraudlens/data_contracts.py` with closed label-free operational objects and private labels confined to offline import/fit/evaluation. Preserve data-model constraints verbatim: DatasetVersion status "staged, complete, failed; only complete is selectable"; parties "Nonempty source values preserved with reviewed normalization"; money "Exact nonnegative decimal text and source currency. No binary float or FX conversion in canonical storage"; timestamp "If source precision cannot be represented losslessly, block mapping/import until resolved"; payment format "Optional source value only when actually present and reviewed". Use mapping-supported bounds; public v2 models follow T050 (FR-001–004, FR-012). (Depends: T009, T010, T011.)

- [x] T013 [US1] GREEN — Implement streaming canonical parsing, pre-filter source identity and row accounting in `backend/src/fraudlens/data_import.py`: "prefix D followed by 32 lowercase hexadecimal digits" and "Case ID: prefix C" with distinct domain separator, full digest input/collision checks and separate dv_ hash of raw/mapping/time policy. Facts/labels validate independently. Enforce source_records=event_valid+event_rejected, event_valid=label_eligible+label_ineligible and label_eligible=positives+negatives; no rounding/FX, renumbering or silent overwrite (FR-001–004). (Depends: T012.)

- [x] T014 [US1] GREEN — Implement versioned SQLite imports in `backend/src/fraudlens/data_store.py` using staged/complete/failed transitions, bounded batches, private label role access, immutable complete imports and transactional completion. Structural failure cannot activate partial results or a partial trustworthy-total report; retry preserves old complete state. Run T009–T011 GREEN and targeted Foundation loader/scorer regressions; log actual outcomes in `evidence/tasks/feature-002-import-identity.md` (FR-002–004, FR-009). (Depends: T013.)

- [x] T015 [US1] GREEN — Wire local import and error/report handling in `backend/src/fraudlens/pipeline_cli.py`; require the reviewed mapping, explicit namespace and source hash; expose no HTTP writes. Use `backend/tests/integration/test_data_store.py` to exercise CLI nonzero failure, row accounting, repeat and interrupted retry. Record commands, counts, hashes and limitations in `evidence/tasks/feature-002-import-identity.md` (FR-001–004, FR-009). (Depends: T014.)

- [x] T016 [US1] EVIDENCE — Run the actual declared IBM import and same-version reimport, reconcile every row and separate label eligibility, verify zero extra identities and immutable source bytes, and record source/mapping/store versions in `evidence/tasks/feature-002-import-identity.md`. If source/mapping is unavailable this acceptance remains `pending_source_unavailable`/`pending_mapping_review`; behavioral fixtures do not complete SC-001's declared-source reproduction (FR-001–004, SC-001). (Depends: T015.)

## Phase 4: US2 — label-free feature replay and rules baseline (P1)

Goal: a usable, meaningful non-ML scoring boundary.

Independent test: hand-computed timelines and R1–R3 trigger/non-trigger/cold-start examples agree exactly; permutations, future events, labels and opaque IDs cannot change allowed features/scores. No provider/model file is required. This is the first scoring increment; full Feature 002 remains open.

- [ ] T017 [US2] GATE — Freeze the complete feature catalog and RulePolicy v1 in `specs/002-data-and-risk-scoring/contracts/data-and-scoring.md`, retaining `data-model.md` definitions: sender outgoing count/distinct receivers/same-paid-currency count and Decimal sum; receiver incoming count/distinct senders/same-received-currency count and sum; current paid amount/currency and only audited optional payment format. Record inputs/availability, units, direction, lineage, visibility and unknown semantics. Preserve "coverage_state (full, incomplete, unavailable)" and "The first 24h of source observation is context-only warm-up"; freeze R1–R3 and examples before evaluation-label inspection (FR-005–007). (Depends: T008, T014.)

- [ ] T018 [P] [US2] RED — Write hand-computed replay tests in `backend/tests/unit/test_feature_history.py`: [t−24h,t) lower inclusion/upper exclusion, shuffled rows, equal-time peers, future append, earlier held-out facts, all catalog values, bank-qualified joins, currency grouping, source warm-up versus full-history account cold start and incomplete/unavailable coverage. Label removal/invalidity cannot remove valid events or change later history; scoring/training replay must match (FR-005–006, SC-002). (Depends: T017.)

- [ ] T019 [P] [US2] RED — Write allowlist/lineage tests in `backend/tests/unit/test_feature_lineage.py` rejecting raw/encoded/hashed transaction/account/case/row IDs, target copies, label-validity flags, source-order proxies and future/full-file aggregates; freeze unknown-category semantics and prove labels never enter feature requests even through nested extras (FR-005–006, FR-012, SC-002, SC-005). (Depends: T017.)

- [ ] T020 [US2] GREEN — Implement pure timestamp-group replay and the versioned feature catalog in `backend/src/fraudlens/feature_history.py`: compute every snapshot before updating any peer at t, retain label-ineligible valid history, separate exact paid/received currency arithmetic, context-only warm-up and measured-zero coverage. Extend `backend/src/fraudlens/pipeline_cli.py` with build-features and persist only complete compatible snapshots through `backend/src/fraudlens/data_store.py`; record RED/GREEN in `evidence/tasks/feature-002-feature-rules.md` (FR-005–006). (Depends: T018, T019.)

- [ ] T021 [US2] RED — Write v2 scorer-boundary tests in `backend/tests/contracts/test_data_scoring.py` for transaction/dataset/run/feature/as-of identity, schema/coverage, actual scoring time versus event time, semantic reproducibility, request mutation and nested unexpected labels; reject wrong identities/digests/versions, missing artifacts and bool/string/nonfinite/out-of-range scores with no clamp, zero default or scorer fallback (FR-008–009, FR-012). (Depends: T020.)

- [ ] T022 [US2] GREEN — Add ScoreRequestV2/ScorerV2 and assessment validation in `backend/src/fraudlens/data_contracts.py`: "It has no label"; "finite score in [0,1]"; source "(rules/model)"; score interpretation "(ordinal_rule_score or uncalibrated_probability_estimate or calibrated_probability)"; distinct event/as-of/actual scored times and exact run/feature metadata. Deep-copy/revalidate inputs/results across injection boundaries. Leave Foundation `backend/src/fraudlens/scoring.py` intact (FR-008–009, FR-012). (Depends: T021.)

- [ ] T023 [US2] RED — Write hand-calculated rule tests in `backend/tests/unit/test_rule_scoring.py`: R1 sender count >=3 contributes 0.35; R2 receiver count >=3 contributes 0.30; R3 same-paid-currency count >=3 and amount >=2×prior mean contributes 0.35. Test equality edges, all/no triggers, insufficient-count unavailable comparison, unscoreable incomplete coverage, measured cold start, real reasons/values and label/future/identifier invariance. No fixture constants or test-only replacement scorer qualify (FR-007–009, FR-019–020, SC-002–003). (Depends: T022.)

- [ ] T024 [US2] GREEN — Implement exact Decimal rule conditions, aggregation and rule explanation values in `backend/src/fraudlens/rule_scoring.py`, returning ordinal_rule_score with the frozen rule hash, actual triggers and unavailable comparisons. Reuse T022 validation; no network/LLM/RAG/model artifact dependency. Run rule/boundary tests GREEN and relevant v1 replacement checks; record actual results in `evidence/tasks/feature-002-feature-rules.md` (FR-007–009, FR-019–020, FR-025). (Depends: T023.)

- [ ] T025 [US2] EVIDENCE — Record hand-checkable catalog/rule reconciliation, semantic repeated-score comparison excluding run IDs/wall-clock times, and rules-only operation with model/provider files absent in `evidence/tasks/feature-002-feature-rules.md`; replay actual source when available and otherwise leave source results pending. This is a rules integration increment; trained-model SC-003 remains pending (FR-005–009, SC-002–003). (Depends: T024.)

## Phase 5: US3 — split/protocol and bounded model/metrics behavior (P1)

Goal: leakage-safe selection and evaluation behavior with a frozen real experiment protocol.

Independent test: controlled populations prove membership/eligibility, train-only learned transforms, deterministic selection/threshold policy, hand-computed metrics and holdout lifecycle. Actual IBM comparison and numerical reproduction are T062, T064 after US4 safety; controlled behavior tests do not satisfy SC-004.

- [ ] T026 [US3] RED — Write split/protocol tests in `backend/tests/unit/test_evaluation_protocol.py`: observable view after warm-up, nearest 70/15/15 whole-timestamp boundaries with earlier-boundary distance tie, membership fixed before label eligibility join, exact exclusions/counts, natural validation/test prevalence, both classes in each partition and >=20 positives in outer validation/test. Ineligibility stops fit/selection and emits an explicit report; no favorable-window search (FR-010–013, SC-005). (Depends: T020, T024.)

- [ ] T027 [US3] GREEN — Implement immutable SplitManifest/EvaluationProtocol state and eligibility in `backend/src/fraudlens/evaluation.py`, with "exact transaction IDs and class/eligibility counts per partition" and "holdout disclosure status". Keep operational facts available for permitted history independently of metric eligibility; label-role joins stay offline. Run T026 GREEN on controlled samples and record in `evidence/tasks/feature-002-protocol.md` (FR-010–013, FR-015). (Depends: T026.)

- [ ] T028 [US3] GATE — Verify the actual Python 3.14 ML stack compatibility, resolve the minimum scikit-learn/NumPy/SciPy dependency set through `pyproject.toml` and generated `uv.lock`, then use locked installs. Run the consecutive 100,000-record pilot (whole file if smaller) with full import/history semantics; record hardware/versions, row/rejection counts, elapsed time, peak-memory estimate, store/artifact sizes and projected feasibility in `evidence/tasks/feature-002-resource-pilot.md`. Freeze memory/time/search ceilings before model search; source/dependency/resource failure remains pending, no silent runtime switch (FR-013, FR-017–018). (Depends: T002, T016, T020, T027.)

- [ ] T029 [US3] GATE — Freeze the real benchmark protocol in `evals/protocols/feature_002_v1.json` and hash/role/eligibility evidence in `evidence/tasks/feature-002-protocol.md` before any fit/validation metric: pooled observable view, exact split IDs/times/counts, train-only transforms/fitting, validation-only selection/threshold, no calibration/AutoML initially, test metrics only after frozen predictions; K=20, seed 42, AP tie 1e-6, <=6 fits, resource budget. Predeclare numeric prediction/metric reproduction and explanation reconstruction tolerances plus deterministic label-free five-example review sampling. Resolve residual candidate ties prospectively using a fixed grid order. Any reduced training view/amendment preserves full chronological history/validation/test and reruns eligibility (FR-010–015, FR-017–019). (Depends: T025, T027, T028.)

- [ ] T030 [US3] RED — Write fit/selection/threshold tests in `backend/tests/unit/test_model_selection.py` instrumenting every imputer/encoder/scaler/selector/statistic and supervised fit to use only training IDs; unknown categories never refit. Verify six-fit bound, candidate AP then P@K then frozen simplicity/grid tie rule, failure/incomplete states, and scorer-specific inclusive distinct-score thresholds plus symbolic no-alert: <=20 validation alerts preserving ties, max F0.5 then fewer alerts then higher threshold, no-prediction F0.5=0. Test outcomes cannot affect selection (FR-012–015, SC-005). (Depends: T029.)

- [ ] T031 [US3] GREEN — Implement train-only transforms and bounded candidate fitting in `backend/src/fraudlens/evaluation.py`: L2 logistic C={0.1,1.0}, tree depth={3,5} × min_leaf={100,500}, seed 42 and maximum six fits within the frozen pilot budget. Persist transform/input-schema/dependency metadata and explicit failures. No optional third search track, calibration, resampling of validation/test or refit on future categories; record controlled GREEN results in `evidence/tasks/feature-002-model-metrics.md` (FR-012–013, FR-017–018). (Depends: T030.)

- [ ] T032 [US3] GREEN — Implement validation winner selection and per-scorer F0.5 threshold policy in `backend/src/fraudlens/evaluation.py` with the T029 tie rules and T030 edge cases. Freeze exactly one model, transforms, feature schema, calibration status and each scorer's threshold or symbolic no-alert before final predictions; zero alerts remains valid. Record controlled results and failure limits in `evidence/tasks/feature-002-model-metrics.md` (FR-013–015). (Depends: T031.)

- [ ] T033 [US3] RED — Write hand-computed metrics and holdout tests in `backend/tests/unit/test_evaluation_metrics.py`: non-interpolated AP, K=min(20,n), Recall@K denominator all eligible positives, stable-ID score ties and crossing-K disclosure, identical rules/model row IDs, prevalence, TP/FP/TN/FN, threshold precision/recall/alert rate, zero alerts, undefined metrics and insufficient classes. Test Brier/reliability support/status only for probability estimates, frozen-prediction-before-test-label join, atomic first disclosure and exploratory consumed-holdout reuse (FR-011, FR-015–017, SC-004–005). (Depends: T032.)

- [ ] T034 [US3] GREEN — Implement frozen-prediction evaluation/reporting and holdout-consumption state in `backend/src/fraudlens/evaluation.py` using pinned positive-label-1 AP, exact denominators/ties/thresholds, uncalibrated model Brier and feasible reliability bins or not-estimable reason; no Brier for ordinal rules. Record not-quantified uncertainty with reason unless predeclared otherwise, seen/unseen-account coverage, actual resources, failures and lack of improvement without bank-loss/production claims. Run controlled metric tests GREEN in `evidence/tasks/feature-002-model-metrics.md` (FR-011, FR-015–018). (Depends: T033.)

- [ ] T035 [US3] RED — Write command-level RED tests for freeze-protocol/evaluate in `backend/tests/integration/test_evaluation_pipeline.py`: missing/ineligible source, immutable protocol, failed candidate, frozen outputs/report hashes, first holdout disclosure and refusal of fresh-confirmatory claims on reuse. Use controlled samples and assertion failures for intended missing command behavior (FR-010–018, SC-004–005). (Depends: T034.)

- [ ] T036 [US3] GREEN — Wire freeze-protocol and evaluate commands in `backend/src/fraudlens/pipeline_cli.py` to the tested protocol/evaluation behavior. Record command tests GREEN in `evidence/tasks/feature-002-model-metrics.md`; controlled samples establish behavior only. No real test-label disclosure yet; the substantive benchmark follows artifact/explanation safety (FR-010–018, SC-004–005). (Depends: T035.)

## Phase 6: US4 — explanations and artifact safety (P1)

Goal: faithful per-assessment evidence and safe loading of a frozen local model.

Independent test: fixed known rule/linear/tree inputs reconstruct the declared scale within a tolerance frozen before runs; mismatched event/run/features, corrupt or untrusted artifacts and invalid scores reject. Every valid assessment has supported explanation or explicit unavailable state. Teammate five-example review is T065.

- [ ] T037 [P] [US4] RED — Write trusted-artifact tests in `backend/tests/unit/test_model_artifacts.py`: local-root containment including traversal/escaped resolved paths, trusted-origin manifest, corruption/SHA mismatch, incompatible dataset/protocol/scorer/feature/transform/dependency versions, missing binaries and unexpected uploads. Spy on deserialization so every rejection occurs before executable loading; no fallback (FR-009, FR-018). (Depends: T036.)

- [ ] T038 [US4] GREEN — Implement manifest creation/checking and trusted local loading in `backend/src/fraudlens/model_scoring.py` with training metadata emitted by `backend/src/fraudlens/evaluation.py`: hash and compatibility before deserialization, only reviewed locally created artifacts under ignored root, no uploaded/arbitrary paths. Fixture/rules require no binary. Record tests and serialization trust limits in `evidence/tasks/feature-002-artifacts-explanations.md` (FR-009, FR-018). (Depends: T037.)

- [ ] T039 [P] [US4] RED — Write faithful explanation tests in `backend/tests/unit/test_explanations.py` from fixed known rule/linear/tree inputs: actual observed value/unit/direction, top-three by absolute contribution (deterministic ties), fewer if fewer available, method/scale/digest and exact event/run/scorer binding. Check linear intercept+items+remainder in log odds before sigmoid, tree root/path/leaf reconstruction within T029 tolerance, partial/unavailable semantics, wrong snapshot/scale/run and global-importance-only rejection; reject nonfinite contributions (FR-019–020, SC-006). (Depends: T036.)

- [ ] T040 [US4] GREEN — Implement deterministic explanations in `backend/src/fraudlens/explanations.py`: "up to three strongest items with observed value/unit/direction"; "plus base/remainder when additive reconstruction is claimed"; linear log odds, tree positive-class leaf estimate and actual rule conditions. Keep facts/contributions/uncertainty separate; missing explanation has an explicit supported unavailable reason, invalid/mismatched explanation rejects publication. No LLM narrative or causal/guilt claim. Record method-specific GREEN results in `evidence/tasks/feature-002-artifacts-explanations.md` (FR-019–020). (Depends: T038, T039.)

- [ ] T041 [US4] RED — Write model adapter tests in `backend/tests/unit/test_model_scoring.py` for parity with frozen fitted predictions, correct transformed feature order, unseen category handling without refit, label-free requests, request mutation, actual scored time, semantic repeatability, matching explanations and explicit artifact/input/output failures. Assert model source/uncalibrated score kind, never illustrative constants, clipping or a rules fallback (FR-008–009, FR-012, FR-018–020, SC-003, SC-006). (Depends: T040.)

- [ ] T042 [US4] GREEN — Implement frozen ModelScorer in `backend/src/fraudlens/model_scoring.py` composing T038 artifact checks, T022 scorer boundary and T040 explanations. Verify parity and all negative/contract tests; record separate fixture/rules/model behavior and semantic fingerprints in `evidence/tasks/feature-002-artifacts-explanations.md`. Real model acceptance still requires T062 and independent explanation review T065 (FR-008–009, FR-018–020). (Depends: T041.)

## Phase 7: US5 — completed-run publication, API and UI migration (P2)

Goal: one immutable active dataset snapshot in the existing list/detail journey while retaining strict fixture v1.

Independent test: publish/retry/switch/restart controlled runs, inject mid-run failure, exercise zero and >100 alerts including >999 transaction IDs and source-supported precision/currency. List/detail either agree on snapshot or produce 409; 503 remains explicit. Confirm truthful rules/model/data notices and original fixture journey without dataset/model artifacts.

- [ ] T043 [P] [US5] RED — Write completed-run failure/restart tests in `backend/tests/integration/test_run_publication.py`: incomplete import/features/artifact, injected failures during scoring/validation/activation, immutable completed rows, atomic active pointer, previous-run preservation or none, scorer mismatch, label-free repository projections, repeated activation, restart and competing run switch. A request must capture one run and never rescore or mix staging records (FR-009, FR-021, SC-007). (Depends: T024, T042.)

- [ ] T044 [P] [US5] RED — Write bounded snapshot tests in `backend/tests/unit/test_review_snapshot.py`: stable one-case-per-alert identities across reruns/scorers/disappear/reappear, zero alerts, >999 transactions, >100 alerts, ties at latest-100 boundary, display ascending event time/transaction ID, total/display counts/range/truncation and exclusion of labels. Selection uses scores/frozen threshold alone; display subset never substitutes for metric population (FR-004, FR-021–022, SC-007–008). (Depends: T024, T042.)

- [ ] T045 [US5] GREEN — Implement run staging/validation/completion/activation in `backend/src/fraudlens/data_store.py` with "status (staging, completed, failed)" and "ActiveRunPointer: none | one completed run ID". Validate all identities/scores/explanations/artifact versions before completion, keep completed rows immutable and switch one pointer atomically. Readers and restart validate only complete state; failures leave old active state unchanged. Record GREEN failure-injection evidence in `evidence/tasks/feature-002-publication.md` (FR-009, FR-021). (Depends: T043, T044.)

- [ ] T046 [US5] GREEN — Implement case reservation and deterministic review snapshot queries in `backend/src/fraudlens/data_store.py`: most recent 100 by descending event time/ascending transaction ID, display ascending event time/ID, exact counts/range and null/null empty range. Detail requires the list's active completed run reference and rejects stale reference; no runtime rescoring. Record T044 GREEN including high-precision/directional currency identities in `evidence/tasks/feature-002-publication.md` (FR-004, FR-021–022). (Depends: T045.)

- [ ] T047 [US5] RED — Write CLI score-run/activate-run RED assertions in `backend/tests/integration/test_run_publication.py`: explicit dataset/scorer/threshold/run, label-free staged assessment validation, nonzero actionable failures, rules operation without training/model/network, and failed model selection without scorer substitution (FR-009, FR-021–022, FR-025). (Depends: T046.)

- [ ] T048 [US5] GREEN — Wire score-run/activate-run in `backend/src/fraudlens/pipeline_cli.py` to the tested staged publication/activation services. Run command and failure-injection tests GREEN; record actual results and rules-only operation in `evidence/tasks/feature-002-publication.md` (FR-009, FR-021–022, FR-025). (Depends: T047.)

- [ ] T049 [US5] RED — Write independent v2 schema/model parity tests in `backend/tests/contracts/test_data_models.py` against every definition in `specs/002-data-and-risk-scoring/contracts/schemas.json`: all required/nullable/enum/pattern/length constraints, closed nested shapes, actual calendar UTC timestamps, finite numbers, >999 IDs, exact money/currency beyond v1 and semantic identity/count/scale/source consistency. Reject target-like extras/free-text leakage and malformed additive explanations. Keep `backend/tests/contracts/test_models.py` and Foundation schema unchanged (FR-003, FR-008–009, FR-019–025, SC-008). (Depends: T008, T048.)

- [ ] T050 [US5] GREEN — Implement closed public HealthV2/CaseListV2/CaseDetailV2/error projections in `backend/src/fraudlens/data_contracts.py` matching the reviewed v2 schema including numeric discriminator 2, ID and timestamp patterns, every bound/nullable field and unavailable explanation variants. Enforce cross-field semantics outside JSON Schema: matching run/dataset/transaction, source/score kind, explanation scale, displayed_count/items, total/truncated/range. Do not truncate source facts to fit public bounds; incompatibility requires reviewed mapping/contract resolution (FR-003, FR-008–009, FR-019–025). (Depends: T049.)

- [ ] T051 [US5] RED — Write dataset API/config tests in `backend/tests/integration/test_dataset_api.py`: explicit APP_MODE=dataset plus APP_SCORER=rules|model, matching completed run, health ok/unavailable with separate dataset/scorer, zero-alert 200, 503 run_unavailable, missing/malformed ID/snapshot 422, absent case 404, switched snapshot 409 stale_snapshot, generic 500, per-request consistency and restart. Probe logs/public bodies for labels/paths/credentials; assert no HTTP import/train/evaluate/activate endpoints or request-time scoring. Fixture startup/health stays independent (FR-009, FR-021–025). (Depends: T050.)

- [ ] T052 [US5] GREEN — Add explicit dataset settings/read service selection in `backend/src/fraudlens/settings.py` and `backend/src/fraudlens/main.py` using T046/T050; preserve v1 `backend/src/fraudlens/cases.py` and injected scorer behavior. Keep same read-only routes, normalized v2 error status/code mapping and one captured pointer per request; missing dataset/model never becomes a fixture response. Record API/health/error and v1 targeted regression outcomes in `evidence/tasks/feature-002-api-ui.md` (FR-021–025). (Depends: T051.)

- [ ] T053 [P] [US5] RED — Write decoder tests in `frontend/tests/dataset-contracts.test.ts` from reviewed v2 examples and backend schema parity corpus for every closed/required/nullable/pattern/length/enum/finite constraint and semantic identity/count/source/scale inconsistency. Dispatch each response by discriminator without relying on health; reject trailing newline IDs, impossible UTC dates, extra labels and mismatched snapshots. Existing v1 decoder tests remain unchanged (FR-003, FR-019–025, SC-008). (Depends: T052.)

- [ ] T054 [US5] GREEN — Add strict v2 union types/decoders in `frontend/src/contracts.ts`, preserving v1 validators and required source precision. Validate schema parity and semantic invariants, explicit unavailable explanations and finite contribution/base/remainder values; no decoder fallback between versions. Record GREEN and original contract regressions in `evidence/tasks/feature-002-api-ui.md` (FR-023–025). (Depends: T053.)

- [ ] T055 [P] [US5] RED — Write client tests in `frontend/tests/dataset-api.test.ts`: relative URLs, encoded exact snapshot query, requested case/run identity, 409/503 controlled codes/status agreement, invalid response/media type, no private server text, 5000-ms timeout across body read, cancellation/ignored abort and explicit retry. Keep `frontend/tests/api.test.ts` and `frontend/tests/api-lifecycle.test.ts` behavior intact; v1 still rejects undocumented 503 for a v1 call (FR-009, FR-021, FR-023–025). (Depends: T052.)

- [ ] T056 [US5] GREEN — Extend `frontend/src/api.ts` for discriminated v1/v2 responses and snapshot-pinned v2 details, with distinct controlled stale/unavailable messages, request identity validation and existing timer/listener cleanup. Retain v1 call signature compatibility, relative URLs and no automatic fallback/retry. Record targeted GREEN and v1 API regressions in `evidence/tasks/feature-002-api-ui.md` (FR-021, FR-023–025). (Depends: T054, T055.)

- [ ] T057 [P] [US5] RED — Write journey tests in `frontend/tests/dataset-views.test.ts`: server v2 event-time order rather than case-ID sort, snapshot carried through selection/retry, stale selection reloads list through an explicit recovery action, no mixed old detail, rules/model/IBM synthetic versus authored-fixture copy, directional money unchanged, event/as-of/scored/coverage/version fields, partial/unavailable explanation and output scale. Cover exact counts/truncation, zero/missing states, safe literal text, keyboard/focus, cancellation/stale responses and persistent v1 notice (FR-019–025, SC-007–008). (Depends: T052.)

- [ ] T058 [US5] GREEN — Migrate `frontend/src/main.ts` and `frontend/src/views.ts` together: retain list metadata/snapshot, preserve v2 server ordering and v1 case-ID sort, pin details, expose explicit stale-list refresh and current source/score/explanation wording in existing screens. Use safe text DOM methods, truthful model inference notice and no guilt claims. Retain v1 loading/empty/retry/timeout/cancellation/focus behavior; adjust `frontend/src/styles.css` only if needed. Record GREEN in `evidence/tasks/feature-002-api-ui.md` (FR-019–025). (Depends: T056, T057.)

- [ ] T059 [US5] EVIDENCE — Exercise a small controlled completed rules snapshot and model-adapter snapshot through real API/proxy/UI, run switch, restart, empty/unavailable/error and latest-100 cases; inspect all public payloads/screens for target leakage and exact source/identity/precision. Recheck the original three-case fixture journey with data/model files absent. Record actual commands/browser observations/limits in `evidence/tasks/feature-002-api-ui.md`; controlled examples are not IBM evaluation (FR-021–025, SC-007–008). (Depends: T058.)

## Phase 8: Regression, reproduction and convergence

Goal: actual runnable instructions, regressions, substantive IBM comparison, numeric repeat, independent review and reproduction. These are distinct evidence classes; none may be inferred from task text. T062 can proceed alongside later API/UI work once its listed prerequisites are ready; listed IDs remain a valid dependency order.

- [ ] T060 DOC — Replace planned placeholders with executable reviewed commands and recreation instructions in `specs/002-data-and-risk-scoring/quickstart.md`, `README.md`, `frontend/README.md` and `data/README.md`; cover fixture/dataset rules/model, eight CLI commands, mapping/protocol/lock/hash checks, private labels, local SQLite recreation/schema version, artifact trust, failure/restart/retry and missing-source pending path. Keep large evaluation output under ignored evals/results; reviewed summaries go to evidence/tasks (FR-018, FR-025–026, SC-009). (Depends: T059.)

- [ ] T061 EVIDENCE — Run full locked backend tests/Ruff, frontend tests/typecheck/build, v1/v2 schema parity and relevant integrated/browser regressions from the quickstart; retain all original Foundation assertions/fixtures/schema and replacement-scorer tests. Record actual commands/exits/counts/failures and unrun checks in `evidence/tasks/feature-002-regression.md`; do not copy historical counts or treat no tests collected/environment failure as GREEN (FR-023, FR-026, SC-008). (Depends: T060.)

- [ ] T062 EVIDENCE — Run the frozen eligible IBM protocol once with actual bounded fitting/validation, verified artifact loading, frozen selected scorer/threshold/predictions and final held-out metric join. Record full comparison, exact IDs/counts/ties/Brier/reliability/uncertainty/seen-account/resource/calibration/holdout facts in `evidence/tasks/feature-002-benchmark.md`; save large outputs locally. Source/ineligible/dependency failure stays explicitly pending/incomplete; baseline operation does not complete model delivery or SC-004. No favorable-outcome requirement or retuning after disclosure (FR-010–020, SC-003–005). (Depends: T016, T029, T036, T042, T048.)

- [ ] T063 RED — Write reproduce-command RED tests in `backend/tests/integration/test_reproduction.py` for missing source/hash/version, altered predictions/metrics, tolerance violations, semantic comparison excluding run ID/time, and consumed-holdout exploratory status. Assert intended missing reproduction behavior without treating environment/import errors as RED (FR-015, FR-018, FR-026, SC-004, SC-009). (Depends: T062.)

- [ ] T064 GREEN — Wire reproduce in `backend/src/fraudlens/pipeline_cli.py`; run reproduction tests GREEN, then repeat the frozen benchmark predictions/metrics using identical source/mapping/protocol/seed/artifacts and the predeclared tolerances. Log actual numeric differences and unresolved divergence in `evidence/tasks/feature-002-benchmark.md`; holdout reuse stays exploratory and the author's repeat is not teammate reproduction (FR-015, FR-018, FR-026, SC-004). (Depends: T063.)

- [ ] T065 REVIEW — Have another teammate inspect at least five explanations against actual facts/method/identity/scale and T029 tolerance using the predeclared label-free sampling rule; if fewer alerts, add scored transactions without manufacturing alerts. Record actual reviewer/date/sample provenance/findings in `evidence/tasks/feature-002-explanation-review.md`; remain `pending_human_review` until performed (FR-019–020, FR-026, SC-006). (Depends: T059, T062.)

- [ ] T066 REVIEW — Have another teammate reproduce the declared IBM import, trusted selected-scorer loading/scoring and evaluation report from checkout instructions without conversation history; record commands, source/mapping/protocol/artifact/lock hashes, machine, versions, elapsed time, tolerances/differences and unresolved limits in `evidence/tasks/feature-002-peer-reproduction.md`. Source absence leaves `pending_source_unavailable`; no teammate run leaves `pending_independent_reproduction`. Do not infer a separate machine or individual signoff (FR-018, FR-026, SC-009). (Depends: T060, T061, T064.)

- [ ] T067 REVIEW — Converge task/spec/plan/contracts/code/evidence and every FR/SC row in `evidence/tasks/feature-002-convergence.md`; obtain real human code/contract/evidence review, resolve regressions/deviations and distinguish unavailable Phase 2 compliance from feature delivery. Update only evidenced markers in `specs/002-data-and-risk-scoring/tasks.md` and `next_work.md` with remaining pending states and one concrete next step. No automatic commit/push; do not declare full Feature 002 acceptance while required dataset/model/review/reproduction evidence is absent (FR-026, SC-001–009). (Depends: T003, T061, T064, T065, T066.)

## Requirement coverage — planned work, tests and evidence

These rows allocate verification; they do not mark requirements satisfied. Test task IDs resolve to exact test files above. Every named evidence suffix means the future path `evidence/tasks/feature-002-<suffix>.md` (expanded literally in the validation inventory). T067 reviews every row; current-generation evidence is separately in `evidence/tasks/feature-002-task-generation.md`.

| Requirement | Implementation/gate/evidence tasks | RED test tasks | Future evidence suffixes |
|---|---|---|---|
| FR-001 | T005, T006, T007, T013, T015, T016 | T004, T009 | source-audit; import-identity |
| FR-002 | T005, T006, T007, T012, T013, T014, T016 | T004, T009, T011 | source-audit; import-identity |
| FR-003 | T007, T008, T012, T013, T050, T058 | T009, T010, T049, T053 | source-audit; import-identity; api-ui |
| FR-004 | T007, T012, T013, T014, T046 | T010, T011, T044 | import-identity; publication |
| FR-005 | T017, T020 | T018, T019 | feature-rules |
| FR-006 | T020, T025 | T018, T019 | feature-rules |
| FR-007 | T017, T024, T025 | T023 | feature-rules |
| FR-008 | T022, T024, T042, T050 | T021, T041, T049 | feature-rules; artifacts-explanations; api-ui |
| FR-009 | T014, T022, T038, T042, T045, T052 | T011, T021, T037, T041, T043, T051 | import-identity; artifacts-explanations; publication; api-ui |
| FR-010 | T027, T029, T036, T062 | T026, T035 | protocol; model-metrics; benchmark |
| FR-011 | T027, T029, T034, T062 | T026, T033 | protocol; model-metrics; benchmark |
| FR-012 | T012, T020, T022, T031, T042 | T009, T019, T021, T030, T041 | import-identity; feature-rules; model-metrics; artifacts-explanations |
| FR-013 | T028, T029, T031, T032, T036 | T026, T030, T035 | resource-pilot; protocol; model-metrics |
| FR-014 | T029, T032 | T030 | protocol; model-metrics |
| FR-015 | T029, T032, T034, T062, T064 | T030, T033, T035, T063 | protocol; model-metrics; benchmark |
| FR-016 | T034, T062, T064 | T033, T063 | model-metrics; benchmark |
| FR-017 | T028, T034, T062 | T026, T030, T033 | resource-pilot; model-metrics; benchmark |
| FR-018 | T002, T028, T031, T038, T062, T064, T066 | T037, T041, T063 | artifacts-explanations; benchmark; peer-reproduction |
| FR-019 | T024, T040, T042, T065 | T023, T039, T041, T049 | feature-rules; artifacts-explanations; explanation-review |
| FR-020 | T040, T042, T058, T065 | T039, T041, T057 | artifacts-explanations; api-ui; explanation-review |
| FR-021 | T045, T046, T048, T052, T056, T058, T059 | T043, T044, T047, T051, T055, T057 | publication; api-ui |
| FR-022 | T046, T048, T050, T058, T059 | T044, T049, T051, T057, T047 | publication; api-ui |
| FR-023 | T008, T050, T052, T054, T056, T058, T061 | T049, T051, T053, T055, T057 | contract-review; api-ui; regression |
| FR-024 | T050, T054, T058, T059 | T049, T051, T053, T057 | api-ui; regression |
| FR-025 | T024, T048, T052, T056, T058, T060 | T023, T041, T047, T051, T055, T057 | feature-rules; publication; api-ui; regression |
| FR-026 | T001, T003, T008, T060, T061, T064, T065, T066, T067 | T004, T009, T018, T021, T023, T026, T030, T033, T035, T037, T039, T041, T043, T044, T047, T049, T051, T053, T055, T057, T063 | implementation; regression; benchmark; explanation-review; peer-reproduction; convergence |

| Success criterion | Delivery/evidence tasks | RED test tasks | Required observation | Future evidence suffixes |
|---|---|---|---|---|
| SC-001 | T006, T007, T013, T014, T016 | T009, T010, T011 | 100% row accounting; exact precision/direction; stable identities; reimport and interruption; actual declared import | source-audit; import-identity |
| SC-002 | T017, T020, T024, T025 | T018, T019, T023 | Every catalog value, lookback boundaries/ties/shuffle, label-validity/history independence, held-out past facts, zero unintended future/label changes | feature-rules |
| SC-003 | T024, T025, T042, T062 | T021, T023, T041 | Hand-computed rules without ML/RAG/provider; real valid-artifact model source distinct from fixtures; both parts required | feature-rules; artifacts-explanations; benchmark |
| SC-004 | T029, T034, T062, T064 | T026, T030, T033, T063 | Eligible IBM comparison with exact FR-016 population/threshold/tie/uncertainty counts; second frozen run within prior numeric tolerance; divergence unresolved | protocol; model-metrics; benchmark |
| SC-005 | T020, T027, T029, T031, T032, T034, T062 | T019, T026, T030, T033, T035 | Observable boundaries and declared roles, train-only transforms, proxies rejected, labels outside serving, disclosure recorded and reuse exploratory | feature-rules; protocol; model-metrics; benchmark |
| SC-006 | T040, T042, T065 | T039, T041, T049 | Every published explanation valid/unavailable and method faithful; five teammate checks chosen label-free, scored non-alert supplements allowed | artifacts-explanations; explanation-review |
| SC-007 | T045, T046, T048, T052, T056, T058, T059 | T043, T044, T047, T051, T053, T055, T057 | Actual list/detail journey, failed replacement/restart old pointer, stale token, no labels, zero/missing states and exact latest-100 metadata | publication; api-ui |
| SC-008 | T008, T050, T052, T054, T056, T058, T059, T061 | T044, T049, T051, T053, T055, T057 | Unchanged v1 assertions and original three-case journey; v2 large IDs/exact money/currency, backend/schema/decoder/example consistency | contract-review; api-ui; regression |
| SC-009 | T060, T064, T066 | T063 | Another teammate's actual source import, trusted scorer load/score and reproducible report with commands/hashes/versions/hardware/time; no self-certification | peer-reproduction; convergence |

## Dependencies and execution order

The explicit per-task prerequisite lists form the detailed graph; IDs are a topological ordering. Do not start a GREEN unit before its RED evidence is established. Gates with missing prerequisites remain pending and block affected descendants; an administrative record of a missing prerequisite is not gate approval.

| Increment | Prerequisites and handoff |
|---|---|
| Setup / source-independent inspect | T001–T005; Phase 2 source lookup T003 can occur separately after T001 |
| Source audit → mapping → v2 consumer review | T006 → T007 → T008; do not merge these three reviews into one checkbox |
| US1 import | T008 → T009/T010/T011 RED → T012–T015 GREEN → actual-source T016 |
| US2 features / rules | T008 + T014 → T017 → T018/T019 → T020; T021 → T022 → T023 → T024 → T025 |
| US3 protocol / model / metrics | T020 + T024 → T026/T027; actual T016 + replay + T027 → T028 pilot → T029 freeze → T030–T036 controlled behavior |
| US4 artifacts / explanations | T036 → T037/T039 RED; T037 → T038; T038 + T039 → T040 → T041 → T042 |
| US5 publication / migration | T024 + T042 → T043/T044 → T045/T046 → T047/T048 → T049/T050 → T051/T052; frontend RED batches → decoder/client/view GREEN → T059 |
| Substantive scientific acceptance | T016 + T029 + T036 + T042 + T048 → T062 → T063/T064 numeric repeat; no final labels before frozen predictions |
| Final human / reproduction / convergence | T065 after actual benchmark and journey; T066 after instructions, regressions and numeric repeat; T067 after all required reviews/results or explicit incomplete handoff |

Independent review means each task produces an assessable change and its evidence, not that data-dependent stories have no dependencies. Controlled reviewed samples exercise component boundaries; full story acceptance additionally needs the real-source and human evidence above.

## Parallel examples (ready tasks in distinct files)

| Story | Safe batch and prerequisite | Serialize afterward |
|---|---|---|
| US1 | T009, T010, T011 after T008: parsing, identity and store tests in separate files | T012–T015 share canonical/import/store/CLI code |
| US2 | T018 and T019 after T017: timeline and feature-lineage tests | T020 replay before scorer RED/GREEN T021–T024 |
| US3 | No [P] work inside evaluation.py; after T029 the protocol owner can perform T030–T036 while a ready independent contract/document reviewer inspects T008 evidence read-only | Candidate fitting/selection/metrics all share evaluation.py and CLI |
| US4 | T037 and T039 after T036: artifact safety and explanation tests in separate files | T038 and T040 coordinate evaluation/model metadata; T041/T042 follow explanation behavior |
| US5 | T043 and T044 after T042; later T053, T055 and T057 after T052: publication/selection tests, then decoder/client/view tests | T054 → T056 → T058 serialize shared frontend types/API/state; store and CLI writes also serialize |

These are scheduling examples for later contributors, not instructions to spawn agents in this planning session. Assign actual contributors/reviewers when they accept work; role letters or AI output are not human approval.

## Incremental implementation strategy and completion evidence

1. Execute setup and source-independent inspector RED/GREEN; explicitly stop source-dependent work if no local source is supplied.
2. Review actual mapping and v2 consumer boundaries, then deliver US1 as the smallest import increment. Its controlled tests and real-source accounting are separately reviewable.
3. Deliver US2 rules as the first useful scoring increment. Other approved workstreams can use reviewed label-free boundaries without a trained model.
4. Freeze pilot budget/protocol, implement US3 behavior, then US4 safety before the actual one-time benchmark disclosure. Keep model availability separate from baseline delivery.
5. Integrate US5 completed runs and v2 API/UI with Foundation regressions. Rules browsing does not require a completed real ML experiment; the shared publication path still requires the safety behavior tested through T042.
6. Finish substantive IBM comparison, numeric repeat, five-example teammate review, independent teammate reproduction and human convergence. Source/Phase 2/review failures retain their exact pending/incomplete state. Do not reclassify a pending requirement as complete to close the feature.

Planned totals: **67 tasks** — setup/foundational 8; US1 8; US2 9; US3 11; US4 6; US5 17; final cross-cutting 8. There are 12 [P] tasks in five distinct-file RED batches. T001-T006 are complete with linked execution evidence; 61 tasks remain unchecked. Full Feature 002 acceptance is larger than the first US1/US2 increments.

