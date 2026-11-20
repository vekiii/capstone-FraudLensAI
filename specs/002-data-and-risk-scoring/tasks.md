# Tasks: Dataset, Machine Learning and EDA

**Inputs**: spec.md, plan.md, research.md, data-model.md, contracts/, quickstart.md
**Status**: T201–T209, T211–T218 and T220–T223 complete; T203 is closed under the explicit content-addressed local-copy exception in `protocol.md`; T210 is in progress; T219 and T224–T255 remain unchecked. Evidence: [T201](../../evidence/tasks/T201.md), [T202](../../evidence/tasks/T202.md), [T203](../../evidence/tasks/T203.md), [T204](../../evidence/tasks/T204.md), [T205](../../evidence/tasks/T205.md), [T206](../../evidence/tasks/T206.md), [T207](../../evidence/tasks/T207.md), [T208](../../evidence/tasks/T208.md), [T209](../../evidence/tasks/T209.md), [T210](../../evidence/tasks/T210.md), [T211](../../evidence/tasks/T211.md), [T212](../../evidence/tasks/T212.md), [T213](../../evidence/tasks/T213.md), [T214](../../evidence/tasks/T214.md), [T215](../../evidence/tasks/T215.md), [T216](../../evidence/tasks/T216.md), [T217](../../evidence/tasks/T217.md), [T218](../../evidence/tasks/T218.md), [T220](../../evidence/tasks/T220.md), [T221](../../evidence/tasks/T221.md), [T222](../../evidence/tasks/T222.md), [T223](../../evidence/tasks/T223.md).
**Verification**: Apply RED → GREEN → REFACTOR to critical behavior. Record actual outcomes; do not invent RED or claim synthetic checks establish model quality.
**Format**: `- [ ] Tnnn [P?] [USn] action with paths (FR-xxx; verification)`

## Stage A — Dataset and provenance

- [x] T201 [US1] Preserve the original prompt and document Feature 002 evidence/output policy in `prompts/development/`, `evidence/`, `data/README.md`, and `.gitignore` (FR-004, FR-005; diff reviewed and generated data paths verified ignored; see `evidence/tasks/T201.md`).
- [x] T202 [US1] Write synthetic duplicate-header positional-map RED tests in `backend/tests/unit/test_dataset_schema.py` for sender/receiver mapping, leading zeros and changed/malformed schema (FR-002, FR-003; test must fail for wrong mapping). See `evidence/tasks/T202.md`.
- [x] T203 [US1] Verify the selected source, source terms/license, CSV header positions/types and timezone documentation; record findings without reading record-level labels in `evidence/tasks/T203.md` and `data/README.md` (FR-001, FR-002, FR-008). Closed for the exact content-addressed local copy by the user's explicit exception in `protocol.md`; upstream Kaggle revision/acquisition date/listing terms and publisher-declared dtypes/timezone remain unknown, with local preparation only permitted.
- [x] T204 [US1] Implement raw-byte hashing, schema gate, exact-text parser and stable source-row transaction identity in `backend/src/fraudlens/data/source.py`; satisfy T202 (FR-001–003). See `evidence/tasks/T204.md`.
- [x] T205 [P] [US1] Add validation RED tests for malformed/missing values, amount, label encoding, row reconciliation and bounded reason codes in `backend/tests/unit/test_dataset_validation.py` (FR-006, FR-007, FR-013). RED evidence: `evidence/tasks/T205.md`.
- [x] T206 [US1] Implement deterministic canonical validation and rejection ledger in `backend/src/fraudlens/data/validation.py`; satisfy T205 (FR-006, FR-007, FR-013). See `evidence/tasks/T206.md`.
- [x] T207 [US1] Add interruption, checkpoint mismatch, disk exhaustion and resume RED tests in `backend/tests/unit/test_dataset_resume.py` (FR-006). See `evidence/tasks/T207.md`.
- [x] T208 [US1] Implement bounded chunk staging, verified resume, manifest and atomic completed-snapshot marker in `backend/src/fraudlens/data/pipeline.py` and `manifest.py`; satisfy T207 (FR-004–006). See `evidence/tasks/T208.md`.
- [x] T209 [US1] Benchmark representative synthetic scale/skew; decide and record memory, disk reserve, runtime, chunk and checkpoint ceilings in `protocol.md` and `evidence/tasks/T209.md` before real ingestion (FR-006). See [T209 evidence](../../evidence/tasks/T209.md).
- [ ] T210 [US1] Acquire only the verified source and create actual data card, manifest, checksums, counts, quality report and limitations in `data/README.md` and ignored `data/processed/` (FR-001–007; record exact commands/results). Local canonical preparation of the exact T203 content-addressed copy is authorized under `protocol.md`; see [T210 evidence](../../evidence/tasks/T210.md).

## Stage B — Historical features and frozen partitions

- [x] T211 [US2] Write synthetic RED tests for strict prior-only features, timestamp ties, UTC-equivalent spellings, exact 24-hour lower edge, currency grouping, bank-qualified identity and warm-up boundary in `backend/tests/unit/test_temporal_features.py` (FR-008–014). See [T211 RED evidence](../../evidence/tasks/T211.md).
- [x] T212 [US2] Verify timezone policy and freeze the exact current/history feature order and category unknown handling in `protocol.md` before feature experiments (FR-008, FR-011–015). See [T212 evidence](../../evidence/tasks/T212.md).
- [x] T213 [US2] Implement UTC normalization and two-phase timestamp-group feature processing in `backend/src/fraudlens/data/features.py`; satisfy T211/T212 (FR-008–015). See [T213 synthetic GREEN evidence](../../evidence/tasks/T213.md); full-source sort/publication remains gated.
- [x] T214 [US2] Write RED tests for `[t0,t0+24h)` warm-up and whole-timestamp partition boundaries/tie breaks in `backend/tests/unit/test_partitions.py` (FR-010, FR-016, FR-017). See [T214 RED evidence](../../evidence/tasks/T214.md).
- [x] T215 [US2] Implement warm-up accounting, nearest-3m source-record development/showcase boundary and 70/15/15 scoreable development split in `backend/src/fraudlens/data/partitions.py`; satisfy T214 (FR-010, FR-016, FR-017). See [T215 synthetic GREEN evidence](../../evidence/tasks/T215.md); real-scale sorting/publication remains gated.
- [x] T216 [US2] Write access-control RED tests for allowed aggregate audit shapes and refused record-level/showcase subrange queries in `backend/tests/unit/test_label_access.py` (FR-018–020). See [T216 RED evidence](../../evidence/tasks/T216.md); GREEN is pending T217.
- [x] T217 [US2] Implement restricted label audit interface and append-only purpose/query/time/result log in `backend/src/fraudlens/training/label_access.py`; satisfy T216 (FR-018–020). See [T217 synthetic GREEN evidence](../../evidence/tasks/T217.md); real aggregate audit remains T218.
- [x] T218 [US2] After count-only boundaries freeze, run the permitted aggregate class audit; record partition counts/prevalence and stop on failed tolerance in `evidence/tasks/T218.md` (FR-018, FR-019). See [T218 evidence](../../evidence/tasks/T218.md): showcase prevalence failed the original frozen tolerance; a later user decision retains the split and makes the showcase ratio diagnostic for this exact local copy. The original audit remains failed.
- [ ] T219 [US2] Freeze dataset/protocol/partition hashes and exact protocol fields in `specs/002-data-and-risk-scoring/protocol.md`; verify every mismatch is a stop condition (FR-021). Partial: source, boundaries and five scoreable partition-ID hashes frozen; the post-audit decision is checked against the original aggregate report and decision record. T221 choices are frozen separately; the full training-protocol hash, fitting-level provenance resolution and full-source feature-capacity review remain pending. See [T219 evidence](../../evidence/tasks/T219.md).

## Stage C — Machine learning

- [x] T220 [US3] Write RED tests proving training preprocessing fits only train data and test/showcase labels remain unread in `backend/tests/unit/test_training_boundaries.py` (FR-020–025). See [T220 RED evidence](../../evidence/tasks/T220.md); GREEN completed under [T223](../../evidence/tasks/T223.md).
- [x] T221 [US3] Resolve and freeze exact candidate grid, class strategy, threshold objective, feature admission policy and budget before any fit; record human decision in protocol/evidence (FR-021, FR-023–026). See [T221 evidence](../../evidence/tasks/T221.md); the complete FR-021 prefit protocol hash and provenance gate remain T219 work.
- [x] T222 [US3] Verify scikit-learn, LightGBM and Python 3.14 lock compatibility and artifact format/security options; record actual versions and decision in `evidence/tasks/T222.md` (FR-030). See [T222 synthetic compatibility and artifact decision](../../evidence/tasks/T222.md); full-source fit and loader remain gated.
- [x] T223 [US3] Implement train-only preparation and prevalence, depth-5/min-leaf-500 tree and L2 logistic baselines in `backend/src/fraudlens/training/`; satisfy T220 on synthetic data before any real-source fit (FR-020, FR-023, FR-025). See [T223 evidence](../../evidence/tasks/T223.md). The user explicitly requested this implementation order on 2026-11-20.
- [ ] T224 [US3] Implement the eight frozen LightGBM configurations and five frozen HistGradientBoosting comparisons in `backend/src/fraudlens/training/`; freeze a cross-family final-selection rule before using comparison results to change the selected model (FR-023, FR-024).
- [ ] T225 [US3] Write RED tests for positive-class F1 selection, AP/P@k/recall/denominators, threshold and model-ranking ties, alert counts, NaN/inf and bounded score in `backend/tests/unit/test_evaluation.py` (FR-022, FR-024, FR-026, FR-027).
- [ ] T226 [US3] Implement validation evaluation and threshold selection without daily alert suppression in `backend/src/fraudlens/training/evaluation.py`; satisfy T225 (FR-024, FR-026, FR-027).
- [ ] T227 [US3] Implement artifact writer/metadata/hash/version validation in `backend/src/fraudlens/scoring/artifacts.py`; ensure no untrusted deserialization (FR-021, FR-030).
- [ ] T228 [US3] Run authorized train/validation experiments and record actual comparisons, limitations and review in `evidence/tasks/T228.md` plus ignored `data/eval/` (FR-022–029).
- [ ] T229 [US3] Freeze model and development-test predictions without reading test labels; record their hashes in `evidence/tasks/T229.md` (FR-020, FR-021, FR-028).
- [ ] T230 [US3] Only after separate explicit authorization, evaluate the frozen test predictions and record authorization/results/limits in `evidence/tasks/T230.md`; otherwise keep test metrics unavailable (FR-020, FR-027, FR-028).

## Stage D — Backend prediction integration

- [ ] T231 [US4] Write synthetic API RED tests for model success, warm-up ineligibility, absent/incompatible artifact, transaction mismatch, malformed score and fixture fallback in `backend/tests/contracts/test_risk_contracts.py` and `backend/tests/integration/test_risk_api.py` (FR-030–034).
- [ ] T232 [US4] Add versioned closed schemas and Pydantic models in `contracts/schemas.json` and `backend/src/fraudlens/contracts.py`; preserve Foundation v1 compatibility (FR-031–034).
- [ ] T233 [US4] Implement trusted local artifact loader and model adapter for the existing `Scorer` boundary in `backend/src/fraudlens/scoring/model_scorer.py` (FR-030–032).
- [ ] T234 [US4] Add explicit opt-in model settings and controlled eligibility/unavailable error mapping in `backend/src/fraudlens/settings.py` and `main.py`; fixture startup remains artifact-free (FR-030–034).
- [ ] T235 [US4] Implement read-only eligible transaction risk endpoint in `backend/src/fraudlens/main.py`; satisfy T231 and exclude target labels (FR-031–034).
- [ ] T236 [US4] Run existing Foundation backend regression checks and record actual commands/outcomes in `evidence/tasks/T236.md` (FR-032).

## Stage E — Frontend prediction/results integration

- [ ] T237 [US4] Write decoder RED tests for closed prediction/results payloads, label leakage and malformed/unavailable states in `frontend/tests/contracts.test.ts` (FR-033, FR-034).
- [ ] T238 [US4] Implement typed decoders and API calls in `frontend/src/contracts.ts` and `frontend/src/api.ts`; decode unknown values without unsafe casts (FR-033, FR-034).
- [ ] T239 [US4] Render score, non-final review state, source, synthetic-data notice, model/feature versions and explanation in `frontend/src/views.ts` and `main.ts` (FR-033).
- [ ] T240 [US4] Render model metrics with partition, denominator, calibration status and authorization limitations in `frontend/src/views.ts` (FR-027, FR-028, FR-033).
- [ ] T241 [US4] Verify safe text rendering, no target labels, and explicit loading/error/retry UI states in `frontend/tests/` (FR-033, FR-034).
- [ ] T242 [US4] Run locked frontend tests, typecheck and build; record exact outcomes in `evidence/tasks/T242.md` (FR-033).

## Stage F — Dedicated EDA page (approval gated)

- [ ] T243 [US6] Record the fourth-screen proposal, benefit and schedule impact, and obtain explicit team approval in `docs/decisions/feature-002-eda.md`; otherwise defer EDA UI tasks (FR-038).
- [ ] T244 [US6] Write aggregate correctness, bounded size, denominator and currency-separation RED tests in `backend/tests/unit/test_eda.py` (FR-035–037).
- [ ] T245 [US6] Implement label-free Python EDA aggregates and closed models in `backend/src/fraudlens/eda/` and `contracts.py` (FR-035, FR-036).
- [ ] T246 [US6] Implement bounded EDA summary endpoint and contract examples in `backend/src/fraudlens/main.py` and `contracts/api.md` (FR-035–037).
- [ ] T247 [US6] Add accessible EDA route/navigation and bounded aggregate charts with explicit units/denominators in `frontend/src/`; requires T243 approval (FR-035, FR-037, FR-038).
- [ ] T248 [US6] Add EDA decoder and loading/empty/unavailable/malformed/retry checks in `frontend/tests/` (FR-036, FR-037).
- [ ] T249 [US6] Run full Foundation plus Feature 002 regression checks and record exact outcomes in `evidence/tasks/T249.md` (FR-032, FR-037).

## Stage G — Gated evaluation and future showcase

- [ ] T250 [US5] Add denied test/showcase record, daily, and subrange label query tests in `backend/tests/unit/test_label_access.py` (FR-019, FR-020, FR-028, FR-034).
- [ ] T251 [US5] Implement aggregate results API with partition visibility controlled by explicit evaluation authorization in `backend/src/fraudlens/training/results.py` and `main.py` (FR-027, FR-028, FR-034).
- [ ] T252 [US5] Complete human review/reproduction of protocol, data card, metrics and limitations; record scope and actual reviewers in `evidence/tasks/feature-002-review.md` (FR-004, FR-021, FR-028).
- [ ] T253 [US5] Specify showcase preceding-24-hour context and event-order contract in `specs/002-data-and-risk-scoring/showcase.md`, without implementing replay (FR-039).
- [ ] T254 [US5] If replay receives separate approval, add synthetic context/order/threshold/no-label/>20-alert tests in `backend/tests/` (FR-039).
- [ ] T255 [US5] Only after separate scope approval, implement later chronological replay and record actual review; do not gate initial data/prediction/EDA delivery on it (FR-039).

## Dependencies and delivery order

T202 precedes T204; T205 precedes T206; T207 precedes T208; T209 precedes T210. Stage B depends on verified Stage A; T211 precedes T213; T214 precedes T215; T216 precedes T217; T218 follows frozen boundaries and access control; T219 follows audit/hash checks. Stage C depends on T219 and decisions T221/T222; T220 precedes training; T228 precedes T229; T230 requires separate authorization. Stage D T231 precedes T232–T235. Stage E depends on backend contracts/API. Stage F's route/UI requires T243 approval. Stage G T251 depends on authorization tests and frozen results; T255 is separately gated/deferred.

The first implementation focus is synthetic validation plus independently verified source ingestion. Build the smallest complete data-to-prediction workflow before optional chart refinement or replay. T240 may be developed against the versioned contract and synthetic responses, but its live results integration depends on T251; model results are unavailable until their permitted evidence exists.

## Requirement traceability index

| Requirement | Implementation tasks |
|---|---|
| FR-001 | T203, T204, T208, T210 |
| FR-002 | T202, T203, T204 |
| FR-003 | T202, T204 |
| FR-004 | T201, T208, T210, T252 |
| FR-005 | T201, T208, T234 |
| FR-006 | T205, T207, T208, T209 |
| FR-007 | T205, T206 |
| FR-008 | T203, T211, T212, T213 |
| FR-009 | T211, T213, T214, T215 |
| FR-010 | T211, T214, T215 |
| FR-011 | T211, T212, T213 |
| FR-012 | T211, T212, T213 |
| FR-013 | T205, T206, T211, T212 |
| FR-014 | T212, T221 |
| FR-015 | T212, T216, T231, T235, T241 |
| FR-016 | T214, T215 |
| FR-017 | T214, T215 |
| FR-018 | T216, T217, T218 |
| FR-019 | T216, T217, T218, T250 |
| FR-020 | T216, T217, T220, T229, T230, T250 |
| FR-021 | T219, T221, T227, T229 |
| FR-022 | T225, T226, T228 |
| FR-023 | T220, T221, T223, T224 |
| FR-024 | T224, T226, T228 |
| FR-025 | T220, T221, T223 |
| FR-026 | T221, T225, T226 |
| FR-027 | T225, T226, T228, T230, T240, T251 |
| FR-028 | T229, T230, T240, T250, T251 |
| FR-029 | T228, T239 |
| FR-030 | T222, T227, T231, T233, T234 |
| FR-031 | T231, T232, T235 |
| FR-032 | T232, T233, T236 |
| FR-033 | T237, T238, T239, T240, T241, T242 |
| FR-034 | T216, T231, T237, T241, T250 |
| FR-035 | T244, T245, T246, T247 |
| FR-036 | T244, T245, T248 |
| FR-037 | T244, T246, T247, T248, T249 |
| FR-038 | T243, T247 |
| FR-039 | T253, T254, T255 |
