# Feature Specification: Data Ingestion and Risk Scoring

**Feature Branch**: `initialization` (unchanged; directory: `002-data-and-risk-scoring`)
**Created**: 2026-11-12
**Status**: Specified; ready for clarification if requested, otherwise technical planning
**Input**: Create the second feature specification following accepted foundation and
the approved data/scoring workstream in [original_idea.md](../../original_idea.md).

This feature turns a documented local IBM AML dataset into reproducible, explainable
transaction assessments and a bounded set of review cases. It is an educational
historical-analysis capability, not a production fraud finding or a real-time payment block.
No dataset has been downloaded, audited or trained on as part of writing this specification.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Import a trustworthy, traceable dataset (Priority: P1)

As the data owner, I can import an identified IBM AML HI-Small release, inspect its
quality report and repeat the import without duplicate transactions, so every downstream
result has known provenance and understandable limitations.

**Why this priority**: Neither model quality nor an explanation is meaningful without
known data, label semantics and a reliable mapping.

**Independent Test**: Import a small reviewed source-shaped test sample containing
valid, invalid, repeated and same-account-number/different-bank records. Verify counts,
identity, precision and repeatability. This checks importer behavior, not representativeness.

**Acceptance Scenarios**:
1. **Given** a locally supplied dataset, **When** it is inspected and imported,
   **Then** its source/release/hash, license reference, observed schema, time coverage,
   class counts and accepted/rejected record counts are recorded.
2. **Given** identical account tokens in different banks and separate sender/receiver fields,
   **When** mapped, **Then** bank-qualified identities and transfer direction remain distinct.
3. **Given** an amount, currency or timestamp outside foundation's demonstration format,
   **When** normalized, **Then** the original value and precision remain recoverable,
   declared assumptions are visible, and unsupported values are rejected explicitly.
4. **Given** the same dataset and import configuration, **When** imported again,
   **Then** identities and accepted records remain stable and no duplicate cases appear.
5. **Given** unavailable data, an incompatible source schema or no eligible records,
   **When** import is requested, **Then** a controlled actionable result is recorded;
   fixture data is not substituted as though it were the requested dataset.

---

### User Story 2 - Establish a label-free historical baseline (Priority: P1)

As a contributor, I can derive prior-activity facts and calculate documented rule-based
risk scores before a trained model is ready, so integration and other workstreams continue.

**Why this priority**: Removes ML training from the critical path while establishing a
meaningful comparison baseline.

**Independent Test**: On a hand-checkable timeline, verify prior-event counts, distinct
counterparties and same-currency amounts; apply versioned rules and inspect exact scores
and reasons without exposing evaluation labels.

**Acceptance Scenarios**:
1. **Given** a transaction at time t, **When** its historical features are calculated,
   **Then** they use only allowed observations strictly earlier than t; adding a future
   event or changing labels does not change those features or rule scores.
2. **Given** multiple events with the same timestamp, **When** processed,
   **Then** they share the same earlier history; their arbitrary file order cannot leak
   observations into one another's history.
3. **Given** an account without prior activity or an unseen category,
   **When** assessed, **Then** documented cold-start/unknown handling applies without
   inventing history, converting unavailable data to confirmed low risk or failing silently.
4. **Given** documented indicators that trigger a rule,
   **When** its assessment is inspected, **Then** the reason, observed values, applicable
   boundaries and rule version are reproducible. The result identifies rules as its source.

---

### User Story 3 - Select and evaluate one explainable scoring model (Priority: P1)

As the model owner, I can compare a small bounded candidate set with the rule baseline,
select one deployable model using development evidence and evaluate it once against
a frozen future holdout, so the team can defend what it actually measured.

**Why this priority**: Provides evidence for scoring without turning the capstone into
an open-ended model research project.

**Independent Test**: Exercise split/selection/evaluation behavior using a controlled
labeled sample, then run the accepted protocol on the declared IBM benchmark view.
Behavior tests and the substantive dataset evaluation must be reported separately.

**Acceptance Scenarios**:
1. **Given** the chronological benchmark view, **When** partitions are frozen,
   **Then** approximately 70/15/15 train/validation/test boundaries, exact timestamps,
   counts, class prevalence and row membership are recorded without splitting timestamp ties.
2. **Given** tuning, optional calibration and threshold selection,
   **When** performed, **Then** their permitted development partitions are explicit,
   preprocessing is fitted only on permitted training observations, and final test labels
   are unavailable to selection, scoring and application delivery.
3. **Given** baseline and eligible candidates, **When** a winner is selected,
   **Then** the recorded validation ranking and tie-break rules determine one model;
   final test results cannot be used to switch winners or tune the threshold.
4. **Given** a frozen scorer and eligible test partition, **When** evaluated,
   **Then** the report includes Average Precision, fixed-budget retrieval metrics,
   threshold error counts, prevalence, denominators and comparison with the baseline.
5. **Given** insufficient classes, a model/dependency failure or no measured improvement,
   **When** results are reported, **Then** the limitation remains visible; no fixture
   performance, successful training or improvement is fabricated. A working rule baseline
   remains explicitly identifiable.

---

### User Story 4 - Understand and inspect an individual assessment (Priority: P1)

As an analyst or future investigation component, I can inspect the score, its provenance
and the actual observations behind it, so an explanation can be checked against evidence.

**Why this priority**: Explainability is a primary project requirement, not a later narrative.

**Independent Test**: For fixed examples with known rule/model contributions, verify the
assessment identity, explanation values, output scale and deterministic source references;
reject invalid, missing or mismatched results.

**Acceptance Scenarios**:
1. **Given** a scored transaction, **When** inspected, **Then** its data origin, score source,
   scorer/feature/run versions, assessment time and available historical coverage are visible.
2. **Given** a model explanation, **When** inspected, **Then** up to three strongest local
   feature contributions (or all if fewer exist), observed values, direction, method and
   explained output scale are available. They are not presented as causal proof.
3. **Given** a rule explanation, **When** inspected, **Then** the actual triggered rule
   conditions and values support the reason; a global importance chart alone is insufficient
   as the explanation of either an individual rule or model assessment.
4. **Given** unavailable model/feature artifacts, an input identity mismatch, a nonfinite
   score or an explanation referring to a different transaction/run,
   **When** scoring/delivery is attempted, **Then** the failure is explicit, not a fixture
   substitution, clipped score or invented reason.

---

### User Story 5 - Review dataset-backed cases without breaking the demo (Priority: P2)

As a demo analyst, I can inspect a bounded set of dataset-backed alerts through the
existing list/detail journey and still run the original fixture demo independently.

**Why this priority**: Makes scoring useful in the application while preserving the
foundation and allowing RAG/investigation teams to work without a trained model.

**Independent Test**: Publish a small scored batch and inspect the list/details, repeat
the same publication, and compare fixture mode before/after. Use boundary examples with
more than 999 records and non-foundation currency/precision to test compatibility.

**Acceptance Scenarios**:
1. **Given** a completed labeled-source import and a label-free scored run,
   **When** cases are made available, **Then** each case links one stable transaction and
   matching assessment; no target labels or evaluation answers are exposed.
2. **Given** a frozen alert threshold, **When** review cases are selected,
   **Then** selection depends on observable inputs/scores only, not the true labels.
   Zero alerts produces an honest empty state rather than manufactured positive cases.
3. **Given** a repeated run or another scorer version on the same transactions,
   **When** published, **Then** stable case identity is preserved, the active assessment
   version is explicit, and concurrent/mixed runs cannot produce list/detail disagreement.
4. **Given** fixture, rules or model output,
   **When** displayed, **Then** the UI distinguishes hand-authored fixtures from IBM's
   synthetic benchmark and names the actual scoring source. A model score must not retain
   the false notice that no ML inference occurred; none becomes a verified crime finding.
5. **Given** missing data/model files in fixture mode or an unavailable dataset-backed run,
   **When** started/requested, **Then** the original three-case fixture journey still works
   independently; dataset-backed mode fails explicitly rather than switching modes silently.

### Edge Cases

- Source files with duplicate header names, different column order, missing required fields,
  unexpected columns, malformed records, blank timestamps, invalid labels or negative amounts.
- Equal-valued transfers in separate source rows: they may be different events; identical
  business fields alone are not permission to remove them as duplicates.
- Reimport of the same source row, repeated account tokens across banks, large identifiers
  and legitimate precision/currency values outside the old fixture contract.
- Paid and received amounts/currencies differ; they cannot be collapsed into one ambiguous
  amount or converted using an invented exchange rate.
- Timestamp timezone absent; event time, execution time and scoring-as-of time differ.
- Equal timestamps at history/split boundaries, cold-start accounts, unseen categories,
  missing historical coverage and reproducible replay of the same scoring request.
- Train/validation/test missing a class; too few positive cases; fewer rows than the
  configured review budget; tied scores and an alert threshold that selects no cases.
- Corrupt or incompatible artifacts, partial/interrupted runs and stale cached assessments.
- Evaluation labels hidden in features, engineered names, IDs, explanations or UI projections.

## Requirements *(mandatory)*

### Functional Requirements

#### Dataset provenance and canonical facts
- **FR-001**: Support locally supplied IBM AML HI-Small as the initial benchmark; record
  acquisition source, variant/release, content hash, license reference and dataset version.
  Never require credentials in Git or download the data as an application startup side effect.
- **FR-002**: Produce a data-quality report that accounts for every source row as accepted
  or rejected with reason, documents schema/field mapping, missingness, time coverage,
  per-currency counts and class prevalence. Structural ambiguity blocks import; rejected
  rows do not disappear from denominators. Raw data remains unchanged.
- **FR-003**: Preserve separate source/receiver bank-qualified identities, original timestamps,
  paid/received amounts and their currencies. State which amount each feature/display uses;
  preserve decimal precision and timezone assumptions. Do not infer currency conversions,
  customer demographics, devices, occupations or account ownership absent from the data.
- **FR-004**: Assign stable dataset-qualified transaction/case identities from source provenance
  and row identity, excluding target labels. Reimport is idempotent; distinct equal-valued rows
  remain distinct. Reject collisions and avoid mixing different source releases silently.

#### Historical context and repeatable scoring
- **FR-005**: Define a versioned feature catalog with meaning, required inputs, availability,
  lookback/units, currency grouping, missing-value handling and visibility scope. Include
  prior transfer counts, distinct counterparties and same-currency amount aggregates
  for available sender/receiver history; do not invent unavailable context.
  Opaque account identifiers may join history but, like transaction/case/source-row
  identifiers, MUST NOT be predictive features in the initial candidate comparison.
- **FR-006**: Derive historical features from observations strictly earlier than the event's
  timestamp, excluding all tied-time events and target labels. Reconstruct identical
  context for training and scoring; record available coverage. Heldout past observations
  may update history only without labels and after their event time has passed.
- **FR-007**: Provide a versioned deterministic rule baseline with documented thresholds,
  finite bounded score, triggered reasons and cold-start behavior, usable before ML exists.
  Changing only labels or future events MUST NOT alter its prior features or scores.
- **FR-008**: Return label-free, identity-consistent assessments with score source, scorer
  version, feature version, data/run reference, event/as-of context and actual scoring time.
  Distinguish risk score from calibrated probability and fixture timestamps from real execution.
  Repeated runs use the same semantic result for the same frozen inputs; execution timestamps
  may differ and are not incorrectly required to be byte-identical.
- **FR-009**: Fail explicitly for invalid inputs, out-of-range/nonfinite scores, missing/incompatible
  artifacts or mismatched transaction/run references. No silent clamping, default zero risk,
  partial publication or fallback to fixture/another scorer is permitted.

#### Model selection and evaluation integrity
- **FR-010**: Use chronological train/validation/test partitions, initially approximately
  70/15/15 with whole timestamp groups and recorded exact membership. Before experimentation,
  declare the benchmark view by observable criteria; keep final test/validation class
  prevalence unchanged by resampling. A reduced training view must be documented separately.
- **FR-011**: Verify eligibility before substantive evaluation: train and validation/test
  must contain both classes, with at least 20 positives in each outer validation and test
  partition as a capstone guardrail, not proof of statistical adequacy. Report exact counts
  and uncertainty limits. If ineligible, report insufficient data and revise the protocol
  before fitting/selection, rather than cherry-picking rows or claiming success.
- **FR-012**: Keep test labels/references separate from operational data, model inputs,
  historical features, explanations and application/investigation payloads. Training labels
  are used only for supervised fitting; development/test labels only for their declared
  evaluation roles. Preprocessing, category handling and any training resampling must not
  learn from future partitions.
- **FR-013**: Freeze the protocol before experiments: candidate set, feature allowlist,
  training/search budget, seed, development subpartitions, selection metric/tie-break,
  review budget K and threshold procedure. The default primary metric is Average Precision
  (AP); distinguish it from other precision-recall area definitions. Select at most one
  simple linear and one tree-based candidate; a bounded AutoML search is optional and
  replaces manual candidate search rather than adding an open-ended third research track.
- **FR-014**: Select one explainable model using validation AP, then Precision@K for an AP tie,
  then simpler/faster inference for a remaining tie. Declare numeric tie tolerance before
  runs. Tune any threshold on validation only. If calibration is attempted, use a declared
  separate chronological development segment or other leakage-safe development procedure;
  do not calibrate and judge calibration quality on the same fitted examples.
- **FR-015**: Freeze the selected model, transformations, feature schema, threshold and
  calibration status before final test scoring; holdout outcomes cannot alter selection.
  Any later changed protocol is a new experiment and cannot treat a consumed holdout as unseen.
- **FR-016**: Produce a comparison report for the baseline and selected model on the same
  eligible population: AP, Precision@K, Recall@K, confusion counts, precision/recall at
  the frozen threshold, total/positive counts, prevalence and alert rate. Cap K at available
  rows and record the actual denominator; resolve score ties by stable transaction identity.
  Report Brier score/reliability diagnostics for probability-output models with their actual
  calibration status; do not label an arbitrary rule score a probability.
- **FR-017**: Report actual dataset/hardware/time/resource conditions, versions and evaluation
  limits, including any lack of improvement and seen/unseen account coverage in each partition.
  A temporal split is not a claim of independent unseen-account performance.
  No accuracy-only success claim, claimed bank-loss
  savings or production generalization from the synthetic benchmark. Functional acceptance
  requires an honest baseline/model comparison, not a promised absolute AP value.
  A failed model run remains incomplete model delivery, even if baseline integration works.
- **FR-018**: Save enough versioned metadata and trusted local artifacts to reproduce transforms,
  fit, scoring, selection and reported metrics. Small definitions/reviewed evidence go in Git;
  downloaded data, model binaries and large generated outputs remain local/ignored with
  hashes and recreation instructions. Do not load arbitrary user-uploaded model artifacts.

#### Explanation and application integration
- **FR-019**: Provide per-assessment explanations derived deterministically from actual
  rule triggers or model-local contributions. Include observed feature values, direction,
  method and output scale, plus dataset/feature/assessment references. Explain up to three
  strongest contributions, or fewer when fewer exist; global importance alone is insufficient.
- **FR-020**: Keep factual observations, model contribution and uncertainty distinct.
  Explain whether contributions refer to raw model output or calibrated output, without
  claiming a decomposition of a different scale. Missing context/explanation must be
  marked unavailable; never fabricate it with an LLM or infer guilt/causation.
- **FR-021**: Publish an explicitly selected, completed scored run into the existing case
  browsing journey using replaceable data/scoring boundaries. Provide one review case per
  threshold-triggering transaction, stable across reruns, with no target labels. Persisted
  results must be restart-reproducible and tied to their exact feature/scorer/run metadata.
- **FR-022**: Bound the default application review snapshot to at most 100 alerts, ordered
  by event time then stable transaction identity. Report total alert count, displayed count,
  selected time range and truncation; do not imply this display subset is the evaluation
  population. Risk/resource optimization and full-scale interactive browsing are later work.
- **FR-023**: Preserve the accepted fixture journey, validation/error behavior and truthful
  provenance notices. Plan explicit versioning/migration for changes to fixed three-digit
  IDs, amount/currency representation, provenance/explanations and data-mode assumptions.
  Producer and affected consumers must review new contracts before implementation; migrate
  affected validation/decoding/tests together, without silently widening foundation v1.
- **FR-024**: Clearly identify hand-authored fixture data versus the IBM synthetic dataset and
  actual fixture/rules/model scoring in the existing UI. Display model reasons and required
  provenance without adding a fifth product screen or implying verified criminal activity.
- **FR-025**: Development and demonstration remain possible without an LLM key, RAG, network
  access at scoring time or completed model training. Rules and fixture modes are explicit
  separate choices; a selected model mode does not silently fall back when the model is absent.
- **FR-026**: Develop critical import, leakage, feature, scorer and delivery behavior test-first.
  Record original prompts and actual RED/GREEN, regression, scientific evaluation and human
  review separately. Freeze and verify shared contracts before other workstreams integrate.

### Key Entities *(include if feature involves data)*

- **DatasetVersion / ImportReport**: Source/release/hash/license, observation scope, row
  accounting, schema mapping, rejection reasons, timeframe/currency coverage and class
  summaries. Class counts belong to data/evaluation reporting, not analyst scoring payloads.
- **CanonicalTransaction**: Stable source event identity, bank-qualified parties, original
  and normalized time assumptions, paid/received amounts and currencies, payment format
  and source-row reference. No target label in the operational projection.
- **HistoricalFeatureSnapshot / FeatureDefinition**: Label-free features at an event's
  historical cutoff, units/currency, missing/coverage state and provenance/version.
- **SplitManifest / EvaluationProtocol**: Exact chronological membership and roles, sampling
  declaration, eligible class counts, candidate/metric/threshold/budget/seed configuration
  and freeze state. Private labels are joined only inside permitted fit/evaluation procedures.
- **ScorerArtifact**: Rule/model identity, trusted artifact hashes, input feature schema,
  transform/model versions, selection evidence and calibration status.
- **RiskAssessment / Explanation**: Transaction/run identity, finite risk score, source,
  timestamps and method-backed observed reasons/contributions, never the target label.
- **ScoredRun / ReviewCaseSnapshot**: Completed label-free batch, threshold and stable
  case identities, selected snapshot bounds and metadata, separate from the full evaluation.
- **EvaluationReport**: Reproducible metrics/denominators and limitations for frozen scorers,
  baseline comparisons and actual execution evidence; no unsupported improvement claim.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The data owner can reproduce a declared import and account for 100% of source
  rows as accepted/rejected; a repeat creates zero duplicate event/case identities. Controlled
  checks preserve equal-valued distinct rows, bank distinctions, amount precision and currencies.
- **SC-002**: On hand-checkable timelines, every declared historical feature agrees with
  its definition; future-event changes, tied-time ordering and label perturbations produce
  zero unintended changes to earlier features/rule scores.
- **SC-003**: A reproducible rule assessment is available without ML/RAG/provider access and
  identifies its real triggers; a model scoring run with valid artifacts produces a separately
  identified model assessment instead of reusing illustrative fixture constants.
- **SC-004**: A recorded eligible IBM benchmark run compares baseline and one selected model
  with all FR-016 measures and exact class/selection counts. A second run with identical
  frozen inputs/seed reproduces predictions and metrics within a predeclared numeric tolerance;
  otherwise the difference and its cause are reported as unresolved, not silently accepted.
- **SC-005**: All declared chronological boundaries, fit/selection/calibration roles and
  leakage checks pass before a final evaluation is accepted; no final holdout label or
  reference answer influences fitting, winner/threshold selection or public case content.
  Observable event facts remain available for their permitted scoring/history roles.
- **SC-006**: Every published assessment has matching event/run identities and a supported
  explanation or explicit unavailable state. At least five selected-case explanations are
  independently checked against their actual facts/method by a teammate, not chosen using labels.
  If fewer than five alert cases exist, use additional scored transactions selected by a
  predeclared label-free sampling rule; do not manufacture alerts just to meet review count.
- **SC-007**: An analyst can inspect a bounded dataset-backed snapshot, match list/detail
  results and identify data/scoring provenance; no public payload, explanation or screen exposes
  a target label. Empty and missing-artifact scenarios give the specified controlled outcomes.
- **SC-008**: The original three-case fixture journey and relevant foundation negative,
  scoring-replacement and UI checks still pass. Large-identity/precision/currency boundary
  tests demonstrate that the planned dataset contract does not truncate valid source values.
- **SC-009**: Another teammate can reproduce import, selected scorer loading/scoring and the
  evaluation report from the recorded protocol and locally acquired source version without
  conversation history; actual findings and outstanding limits are recorded.

## Assumptions

### Scope and practical defaults
- Feature 001 is accepted. Its current contracts are references, not automatically sufficient
  for IBM data; no source code, contract migration, dataset import or model training is
  implemented by this specification. Technical choices and executable interfaces belong to
  the next plan/contracts/tasks, not this document.
- Initial source: local `HI-Small_Trans.csv` from the declared IBM AML release. No raw file
  was present under data/ at specification time; observed schema, exact counts, available
  timestamp granularity and label distribution must be verified during the first data audit.
- The initial experiment uses a clearly declared synthetic pooled multi-bank view.
  This is not a claim that one real institution can see all other banks' customer activity.
- Historical scoring is performed after each source transfer record is available. Rolling
  activity uses strictly earlier timestamps. An initial one-day lookback is the default for
  activity counts/counterparties/amount aggregates, with a declared coverage/warm-up interval.
  Current-transfer facts may be used; future values and label-dependent patterns may not.
- Default outer split is approximately 70/15/15 by chronological observation order with ties
  kept together; actual proportions can vary. Choosing 80/10/10 or a smaller fixed observation
  window requires a recorded pre-experiment protocol amendment and eligibility recheck.
  Do not manufacture a balanced test set or choose a window because its resulting metrics look better.
- Default review budget K is 20 per evaluation partition, capped at its available rows; the
  threshold is chosen for at most 20 validation alerts with a deterministic tie policy.
  If tied scores make an exact threshold count impossible, record the lower achievable count
  and the resulting threshold. This is a capstone capacity assumption, not a bank policy.
  Recall denominator is all positives in the eligible partition, including unalerted events.
- Training and optional AutoML are timeboxed in the technical plan before experiments.
  Start with rules, then a small explainable candidate comparison; no GNN, transformer,
  graph database, new agents or distributed/streaming infrastructure is required.
- Local single-user operation and the team's existing approved runtime agreement remain.
  Any necessary dependency/runtime incompatibility is reported and resolved explicitly,
  without silently changing the team's runtime agreement.

### Explicit exclusions
- No LLM decision-making or generated investigation narratives, RAG ingestion/retrieval,
  analyst case-disposition workflow, regulatory filing, account blocking, learning-to-defer,
  cost/resource optimization, drift-monitoring service or Simulation Lab implementation.
- No live bank integrations, real personal/customer data, production authentication,
  public hosting, automatic retraining or model registry platform.
- Only the list/detail provenance and explanations needed for this feature are in scope;
  evaluation output is a reproducible report, not a new dashboard project.
- No absolute promise of predictive improvement, prevented loss or production readiness.
  Unsupported benchmark performance must be reported honestly, not hidden by redefining labels.

### Dependencies and readiness
- Requires locally acquired licensed source data, adequate eligible class counts, permitted
  local compute and compatible dependencies before substantive training/evaluation.
- Requires reviewed dataset-backed transaction/assessment contracts and consumer migration
  before application integration; fixture compatibility stays covered by regression.
- RAG, investigation and simulation contributors may work from reviewed label-free examples
  and stable boundaries while ML experiments run. They do not need training data or test labels.
- Candidate algorithms, exact artifact layout, command interfaces, processing strategy,
  numeric tolerances and detailed schema/versioning are planning decisions. These are not
  unresolved product choices and must be fixed before their corresponding implementation runs.

### Source references
- [Approved project idea](../../original_idea.md), especially data/scoring and evaluation scope.
- [Foundation contracts](../001-project-foundation/contracts/api.md) and
  [existing replacement/compatibility decisions](../../docs/decisions/foundation.md).
- [IBM dataset repository](https://github.com/IBM/AML-Data) and
  [Kaggle distribution](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml).
- [Dataset authors' paper](https://arxiv.org/html/2306.16424v2).
  Published descriptions support the initial source choice; they do not replace inspecting
  the actual acquired release or establish this project's measured performance.

