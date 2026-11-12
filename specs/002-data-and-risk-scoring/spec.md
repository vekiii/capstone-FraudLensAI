# Feature Specification: Data Ingestion and Risk Scoring

**Feature Branch**: `initialization` (unchanged; directory: `002-data-and-risk-scoring`)
**Created**: 2026-11-12
**Status**: Revised after adversarial review; human review and technical planning pending
**Input**: Create the second feature specification following accepted foundation and
the approved data/scoring workstream in [original_idea.md](../../original_idea.md).
Revision input: the [Feature 002 adversarial review transcript](../../prompts/development/002-review.md)
and [review-remediation request](../../prompts/development/002-review-remediation-2026-11-12.md).

This feature turns a documented local IBM AML dataset into reproducible, explainable
transaction assessments and a bounded set of review cases. It is an educational
historical-analysis capability, not a production fraud finding or a real-time payment block.
No dataset has been downloaded, audited or trained on as part of writing this specification.
The authoritative Phase 2 assignment requirements document has not been located in the
repository. This specification therefore does not claim verified Phase 2 compliance.
The Feature 002 quality checklist is not that assignment document.

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
6. **Given** valid transaction facts with a missing or invalid target label, **When**
   imported, **Then** the event remains available to label-free historical context,
   its label is ineligible for supervised use, and both statuses are reported separately.
7. **Given** an interrupted import or a changed source/mapping configuration, **When**
   import is retried or selected, **Then** no incomplete import becomes active, a repeat
   of the same version is idempotent, and a changed version cannot silently overwrite it.

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
5. **Given** out-of-order rows, a lookback-boundary event or incomplete source coverage,
   **When** history is replayed, **Then** event time governs ordering, the declared window
   boundary is honored, and incomplete coverage is shown rather than called zero activity.

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
6. **Given** rule and model scores on different scales, **When** evaluated, **Then**
   both use the same predeclared validation-only operating policy with scorer-specific
   thresholds if needed. Ranking at K and threshold alerts remain separate results.
7. **Given** a previously disclosed final holdout, **When** a changed protocol is run
   against it, **Then** the new result is marked exploratory and is not presented as
   a fresh confirmatory estimate.

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
5. **Given** a model explanation computed for a different output scale or feature
   snapshot, **When** validated, **Then** it is rejected or explicitly marked unavailable;
   the displayed contributions must pass a method-appropriate faithfulness check.

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
6. **Given** a failed new scoring run, **When** an analyst opens a case, **Then** the
   previous completed snapshot remains active (or no snapshot is active if none existed);
   list and detail never mix runs, including after restart.
7. **Given** more than 100 qualifying alerts, **When** the default snapshot is shown,
   **Then** the most recent 100 are selected deterministically, displayed in chronological
   order, and the full alert count and truncation are visible.

### Edge Cases

- Source files with duplicate header names, different column order, missing required fields,
  unexpected columns, malformed records, blank timestamps, invalid labels or negative amounts.
- Empty/header-only files, invalid bytes or unsupported encodings, truncated quoted records,
  parser failure after valid rows, header case/whitespace/BOM variants and target-like extra
  columns. Unknown fields never silently become predictors.
- Equal-valued transfers in separate source rows: they may be different events; identical
  business fields alone are not permission to remove them as duplicates.
- Reimport of the same source row, repeated account tokens across banks, large identifiers
  and legitimate precision/currency values outside the old fixture contract. Filtering
  rejected rows cannot renumber later source identities.
- Paid and received amounts/currencies differ; they cannot be collapsed into one ambiguous
  amount or converted using an invented exchange rate.
- Zero, missing, malformed, nonfinite, oversized and excessive-precision numeric inputs
  must be preserved exactly when supported or rejected with a reason, never rounded or
  overflowed silently.
- Timestamp timezone absent; event time, execution time and scoring-as-of time differ.
- Equal timestamps at history/split boundaries, cold-start accounts, unseen categories,
  missing historical coverage and reproducible replay of the same scoring request.
- Train/validation/test missing a class; too few positive cases; fewer rows than the
  configured review budget; tied scores and an alert threshold that selects no cases.
- Corrupt or incompatible artifacts, partial/interrupted runs and stale cached assessments.
- Different source hashes or mapping versions, changed alert status across scorer versions,
  a tie crossing the K boundary and more alerts than the review display limit.
- Evaluation labels hidden in features, engineered names, IDs, explanations or UI projections.

### Normative terms and boundaries

- A **source row** has a stable physical reference assigned before filtering. Source rows
  are accounted for as event-valid or event-rejected. Event-valid rows are separately
  classified as label-eligible or label-ineligible. A missing/invalid target label does
  not by itself reject valid observable transaction facts. Only label-eligible rows
  enter supervised fitting or metric denominators.
- A **dataset/import version** binds the source content and reviewed mapping/time
  interpretation. Changing any of these creates a separately identified version.
  Case and transaction identities do not depend on target labels, raw-file hash
  changes caused only by labels, accepted-row position, scorer version or alert status.
  Stable identity across different physical source files is promised only when their
  source-row identity can be established without guessing; otherwise versions remain
  separate and any collision is reported.
- **Event time** is the source transfer time after a declared interpretation. The
  **feature as-of cutoff** for an event is immediately before its event time: only
  observable facts with strictly earlier event times may contribute. **Scored at**
  is the actual execution time. Source ordering, timestamp ties and split membership
  do not change these rules. If a source timezone cannot be interpreted defensibly,
  the import is blocked pending a documented mapping decision.
- A **history coverage state** distinguishes a measured zero from unavailable or
  incomplete prior observation. The technical plan must define exact lookback
  boundaries and how warm-up rows affect scoring and evaluation membership before
  experiments; every report records the resulting counts.
- An **evaluation population** is the declared set of label-eligible rows for a
  partition. Split boundaries are chosen on the declared event-valid view using
  observable time and criteria before labels are joined; label-ineligible rows are
  then excluded from metric denominators, with counts reported. Prior event-valid
  facts, including facts from an earlier held-out row,
  may inform a strictly later event after they become observable; labels never do.
  Application cases and the bounded display subset are not metric denominators.
- A **risk score** is a finite bounded ranking or alert value, not a probability
  unless the selected output has a declared and evaluated probability interpretation.
  Rule and model thresholds may differ numerically. Precision@K and Recall@K are
  ranking measures; threshold-generated alerts may legitimately be zero.

## Requirements *(mandatory)*

### Functional Requirements

#### Dataset provenance and canonical facts
- **FR-001**: Support locally supplied IBM AML HI-Small as the initial benchmark; record
  acquisition source, variant/release, content hash, license reference and dataset version.
  Never require credentials in Git or download the data as an application startup side effect.
- **FR-002**: Produce a data-quality report that accounts for every source row as accepted
  or rejected with reason, documents schema/field mapping, missingness, time coverage,
  per-currency counts and class prevalence with the label-eligible denominator stated.
  Structural ambiguity blocks import; rejected
  rows do not disappear from denominators. Raw data remains unchanged. Assign source-row
  references before validation. Report event validity separately from supervised-label
  eligibility: otherwise valid observable facts remain usable for label-free history
  when a label is missing or invalid, but that row is excluded from supervised fitting
  and metrics. An interrupted or failed import cannot become the active dataset.
  Unknown columns are recorded and never silently mapped into features; ambiguous,
  target-like or incompatible mappings block import pending review.
- **FR-003**: Preserve separate source/receiver bank-qualified identities, original timestamps,
  paid/received amounts and their currencies. State which amount each feature/display uses;
  preserve decimal precision and timezone assumptions. Do not infer currency conversions,
  customer demographics, devices, occupations or account ownership absent from the data.
  Parsing must not silently round, overflow, coerce nonfinite values or invent a missing
  currency/timezone. Supported zero and precision behavior must be fixed in the reviewed
  source mapping; unsupported values receive explicit row-level rejection reasons.
- **FR-004**: Assign stable dataset-qualified transaction/case identities from source provenance
  and row identity, excluding target labels. Reimport is idempotent; distinct equal-valued rows
  remain distinct. Source-row identity is fixed before event/label filtering, so a rejected
  row cannot renumber later events. Reject collisions and avoid mixing different source
  hashes, releases or mapping/time-interpretation versions silently. A repeated import
  of the same version creates no additional active events or cases.

#### Historical context and repeatable scoring
- **FR-005**: Define a versioned feature catalog with meaning, required inputs, availability,
  lookback/units, currency grouping, missing-value handling and visibility scope. Include
  prior transfer counts, distinct counterparties and same-currency amount aggregates
  for available sender/receiver history; do not invent unavailable context.
  Opaque account identifiers may join history but, like transaction/case/source-row
  identifiers, MUST NOT be predictive features in the initial candidate comparison.
  The allowlist/lineage audit also excludes hashes or encodings of those identifiers,
  target copies or label-validity indicators, source-order proxies and aggregates that
  use future or full-dataset observations. Unseen categories and incomplete history
  have explicit, reproducible states.
- **FR-006**: Derive historical features from observations strictly earlier than the event's
  timestamp, excluding all tied-time events and target labels. Reconstruct identical
  context for training and scoring; record available coverage. Heldout past observations
  may update history only without labels and after their event time has passed. Replay is
  ordered by interpreted event time rather than source file order. Supervised-label
  eligibility cannot determine whether otherwise valid event facts enter history.
  A measured zero must remain distinguishable from incomplete or unavailable coverage.
- **FR-007**: Provide a versioned deterministic rule baseline with documented thresholds,
  finite bounded score, triggered reasons and cold-start behavior, usable before ML exists.
  Rules use only label-free observable current-transaction facts and permitted historical
  features; transaction, account, case, source-row and target-label identifiers cannot
  determine outcomes. Each rule has a documented condition, threshold, score or score
  contribution, reason and behavior when coverage is incomplete. The concrete small
  rule set and numeric values are frozen before evaluation. Foundation fixture constants
  and the test-only replacement scorer are not this baseline. Changing only labels or
  future events MUST NOT alter prior features or rule scores.
- **FR-008**: Return label-free, identity-consistent assessments with score source, scorer
  version, feature version, data/run reference, event/as-of context and actual scoring time.
  Distinguish risk score from calibrated probability and fixture timestamps from real execution.
  Repeated runs use the same semantic result for the same frozen inputs; execution timestamps
  may differ and are not incorrectly required to be byte-identical.
- **FR-009**: Fail explicitly for invalid inputs, out-of-range/nonfinite scores, missing/incompatible
  artifacts or mismatched transaction/run references. No silent clamping, default zero risk,
  partial import/publication or fallback to fixture/another scorer is permitted. Failed
  import/scoring attempts leave the previous completed active version intact, or no active
  version if none existed; restart and retry cannot expose mixed versions.

#### Model selection and evaluation integrity
- **FR-010**: Use chronological train/validation/test partitions, initially approximately
  70/15/15 with whole timestamp groups and recorded exact membership. Before experimentation,
  declare the benchmark view by observable criteria and determine boundaries without
  target-label eligibility; keep final test/validation class
  prevalence unchanged by resampling. A reduced training view must be documented separately.
  The manifest records event-valid, label-eligible and excluded counts, coverage/warm-up
  treatment, timestamp boundaries and any protocol amendment before fit or selection.
- **FR-011**: Verify eligibility before substantive evaluation: train and validation/test
  must contain both classes, with at least 20 positives in each outer validation and test
  partition as a capstone guardrail, not proof of statistical adequacy. Report exact counts
  and state uncertainty or evaluation limitations. If uncertainty is not quantitatively
  estimated, say so and explain why; do not imply unmeasured precision. If ineligible,
  report insufficient data and revise the protocol before fitting/selection, rather
  than cherry-picking rows or claiming success.
- **FR-012**: Keep test labels/references separate from operational data, model inputs,
  historical features, explanations and application/investigation payloads. Training labels
  are used only for supervised fitting; development/test labels only for their declared
  evaluation roles. Preprocessing, category handling and any training resampling must not
  learn from future partitions. Every learned imputer, encoder, scaler, selector or
  statistic is fitted only on its declared training role; unknown categories have a
  frozen handling rule. The evaluator may join held-out labels only to already frozen
  predictions for metrics, never pass them to scoring or selection.
- **FR-013**: Freeze the protocol before experiments: candidate set, feature allowlist,
  training/search budget, seed, development subpartitions, selection metric/tie-break,
  review budget K and threshold procedure. Record a role table for each partition and
  subpartition: fitting, transforms, selection, calibration fit/check, threshold choice
  and final metric computation. The default primary metric is Average Precision
  (AP); distinguish it from other precision-recall area definitions. Select at most one
  simple linear and one tree-based candidate; a bounded AutoML search is optional and
  replaces manual candidate search rather than adding an open-ended third research track.
- **FR-014**: Select one explainable model using validation AP, then Precision@K for an AP tie,
  then simpler/faster inference for a remaining tie. Declare numeric tie tolerance before
  runs. A deterministic operating-point objective and tie policy must be frozen before
  validation. Apply the same policy separately to rules and model on their own validation
  scores; numeric thresholds need not match. Threshold-generated alerts are separate
  from top-K ranking metrics and need no minimum count. Zero alerts are valid when no
  event meets the frozen policy. Tune any threshold on validation only. If calibration
  is attempted, use a declared
  separate chronological development segment or other leakage-safe development procedure;
  do not calibrate and judge calibration quality on the same fitted examples.
- **FR-015**: Freeze the selected model, transformations, feature schema, threshold and
  calibration status before final test scoring; holdout outcomes cannot alter selection.
  Any later changed protocol is a new experiment and cannot treat a consumed holdout as
  unseen. Once holdout labels/results are disclosed, reuse of that holdout is exploratory
  and cannot support a fresh confirmatory estimate.
- **FR-016**: Produce a comparison report for the baseline and selected model on the same
  eligible population: AP, Precision@K, Recall@K, confusion counts, precision/recall at
  each scorer's frozen threshold, total/positive counts, prevalence and alert rate. Cap
  K at available rows and record the actual denominator; Recall@K divides by all
  positives in the eligible partition, not only alerted positives. Resolve score ties
  by stable transaction identity and report any tie crossing the K boundary, including
  that ID order supplies reproducibility rather than predictive discrimination.
  Report Brier score and feasible reliability diagnostics for probability-output models
  with their actual calibration status; Brier alone does not prove calibration and an
  arbitrary rule score is not a probability.
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
  hashes and recreation instructions. Before loading a local artifact, verify its
  recorded hash and expected feature/transform/scorer compatibility; reject a mismatch
  without fallback. Do not load arbitrary user-uploaded model artifacts.

#### Explanation and application integration
- **FR-019**: Provide per-assessment explanations derived deterministically from actual
  rule triggers or model-local contributions. Include observed feature values, direction,
  method and output scale, plus dataset/feature/assessment references. Bind each
  explanation to the exact transaction, run, scorer and feature snapshot. Explain up
  to three strongest contributions, or fewer when fewer exist; global importance alone
  is insufficient. A method-appropriate check must establish that the contributions
  came from the declared model input and output scale. If an additive reconstruction
  is claimed, include the base/remainder terms and verify it within a predeclared
  tolerance; otherwise label the displayed top contributions as partial.
- **FR-020**: Keep factual observations, model contribution and uncertainty distinct.
  Explain whether contributions refer to raw model output or calibrated output, without
  claiming a decomposition of a different scale. Missing context/explanation must be
  marked unavailable; never fabricate it with an LLM or infer guilt/causation.
- **FR-021**: Publish an explicitly selected, completed scored run into the existing case
  browsing journey using replaceable data/scoring boundaries. Provide one review case per
  threshold-triggering transaction, stable across reruns, with no target labels. Persisted
  results must be restart-reproducible and tied to their exact feature/scorer/run metadata.
  An alert disappearing in a later active run disappears from that run's list, while its
  stable case identity remains reserved for that transaction if it alerts again. Readers
  see one complete active run at a time, including across restart. The case list carries
  a snapshot/run reference; a later detail request either resolves against that same
  snapshot or reports that the selection is stale. It never silently substitutes a
  detail from a newly active run.
- **FR-022**: Bound the default application review snapshot to at most 100 alerts, ordered
  by event time then stable transaction identity. Report total alert count, displayed count,
  selected time range and truncation. When more than 100 alerts qualify, select the most
  recent 100 by descending event time and ascending stable transaction identity for ties,
  then display that selection
  in ascending event-time/identity order. The tie convention is deterministic and not a
  claim of risk ranking. Do not imply this display subset is the evaluation population.
  Risk/resource optimization and full-scale interactive browsing are later work.
- **FR-023**: Preserve the accepted fixture journey, validation/error behavior and truthful
  provenance notices. Plan explicit versioning/migration for changes to fixed three-digit
  IDs, amount/currency representation, provenance/explanations and data-mode assumptions.
  Producer and affected consumers must review new contracts before implementation; migrate
  affected validation/decoding/tests together, without silently widening foundation v1.
  The new contract distinguishes dataset source from scorer source, binds list/detail to
  one active run, and keeps target labels out of public payloads. Existing fixture
  payloads remain valid under their declared contract version.
- **FR-024**: Clearly identify hand-authored fixture data versus the IBM synthetic dataset and
  actual fixture/rules/model scoring in the existing UI. Display model reasons and required
  provenance without adding a fifth product screen or implying verified criminal activity.
- **FR-025**: Development and demonstration remain possible without an LLM key, RAG, network
  access at scoring time or completed model training. Rules and fixture modes are explicit
  separate choices; a selected model mode does not silently fall back when the model is absent.
  Configuration and health output identify the selected dataset/run and scoring source
  without treating dataset identity as interchangeable with scorer identity.
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
  Event-valid/label-eligible counts reconcile separately. Interrupted import, changed
  mapping and malformed-file tests expose zero incomplete active datasets.
- **SC-002**: On hand-checkable timelines, every declared historical feature agrees with
  its definition; future-event changes, tied-time ordering and label perturbations produce
  zero unintended changes to earlier features/rule scores. Tests also cover shuffled
  source order, a held-out past fact, exact lookback boundaries, incomplete coverage
  and a valid event whose label becomes invalid.
- **SC-003**: A reproducible rule assessment is available without ML/RAG/provider access and
  identifies its real triggers; a model scoring run with valid artifacts produces a separately
  identified model assessment instead of reusing illustrative fixture constants.
  Hand-computed trigger, non-trigger and cold-start examples agree with the frozen rule
  policy; identifier-only and label-only changes do not change the score.
- **SC-004**: A recorded eligible IBM benchmark run compares baseline and one selected model
  with all FR-016 measures and exact class/selection counts. A second run with identical
  frozen inputs/seed reproduces predictions and metrics within a predeclared numeric tolerance;
  otherwise the difference and its cause are reported as unresolved, not silently accepted.
  The report shows the same evaluated row IDs for both scorers, each frozen threshold and
  alert count, K-boundary ties, and either justified uncertainty estimates or an explicit
  not-quantified limitation. A zero-alert scorer is reported honestly.
- **SC-005**: All declared chronological boundaries, fit/selection/calibration roles and
  leakage checks pass before a final evaluation is accepted; no final holdout label or
  reference answer influences fitting, winner/threshold selection or public case content.
  Observable event facts remain available for their permitted scoring/history roles.
  The manifest records the first holdout disclosure; later reuse is marked exploratory.
  Tests reject target/identifier proxies and prove learned transforms fit only permitted
  training rows, with deterministic handling of unseen categories.
- **SC-006**: Every published assessment has matching event/run identities and a supported
  explanation or explicit unavailable state. At least five selected-case explanations are
  independently checked against their actual facts/method by a teammate, not chosen using labels.
  If fewer than five alert cases exist, use additional scored transactions selected by a
  predeclared label-free sampling rule; do not manufacture alerts just to meet review count.
  Method-specific checks confirm the declared output scale, any claimed additive
  reconstruction and its tolerance, and reject an explanation from a different
  feature snapshot, scorer or run.
- **SC-007**: An analyst can inspect a bounded dataset-backed snapshot, match list/detail
  results and identify data/scoring provenance; no public payload, explanation or screen exposes
  a target label. Empty and missing-artifact scenarios give the specified controlled outcomes.
  Failure during a replacement run leaves the previous complete snapshot visible; switching
  active runs cannot silently serve a detail from a different run. More than 100 alerts
  yield the declared most-recent selection and exact total/display/truncation fields.
- **SC-008**: The original three-case fixture journey and relevant foundation negative,
  scoring-replacement and UI checks still pass. Large-identity/precision/currency boundary
  tests demonstrate that the planned dataset contract does not truncate valid source values.
  Versioned backend schema, frontend decoder, API examples and tests agree on fixtures
  and dataset-backed responses without loosening Foundation v1 validation.
- **SC-009**: Another teammate can reproduce import, selected scorer loading/scoring and the
  evaluation report from the recorded protocol and locally acquired source version without
  conversation history; actual commands, source/artifact hashes, dependency versions,
  hardware, elapsed time, protocol amendments and outstanding limits are recorded.

## Implementation handoff for the technical plan and task authors

The following is a concrete handoff, not a claim that these files, functions, tests or
the IBM source schema already exist. The plan must finalize interfaces, local storage
mechanics, numeric policies and source mapping after inspecting the authorized local
dataset. The later tasks.md must split the work into reviewable RED/GREEN units and
trace each task to the FR/SC IDs below. Do not copy these sketches into production
without contract review, implementation and tests.

### Required code boundaries and data flow

| Planned boundary | Required behavior and likely code location | Contract/check to deliver |
|---|---|---|
| Source inspection and import | A local importer under backend/src/fraudlens reads an explicitly selected source, records source/hash/mapping, assigns physical row references before filtering, parses event facts and labels separately, and stages a complete import. | DatasetVersion, ImportReport, CanonicalTransaction and private label store; FR-001–004, SC-001. |
| Historical features | A pure feature builder takes event-valid facts and a frozen feature catalog; it replays timestamp groups in event-time order and emits one snapshot per event before adding that group's facts to history. | HistoricalFeatureSnapshot with coverage/as-of/feature version; FR-005–006, SC-002. |
| Rules baseline | A separate RuleScorer reads only canonical current facts and permitted historical snapshots; it returns a bounded score and actual fired conditions under a frozen rule version. | Label-free RiskAssessment and rule explanation; FR-007–009, SC-003. |
| Split and protocol | An offline evaluation module freezes observable benchmark view, whole-timestamp partitions, row/label roles, feature allowlist, candidate budget, seed, tie tolerance, K and threshold objective before fitting. | SplitManifest and EvaluationProtocol; FR-010–015, SC-004–005. |
| Model training and inference | A bounded candidate trainer fits learned transforms on permitted training rows only, selects on validation, freezes one model and supports unknown categories without refitting. A model adapter scores the same canonical request type as rules. | Trusted ScorerArtifact, frozen predictions and calibration status; FR-012–018. |
| Metrics and explanations | An evaluator joins labels only to frozen predictions; it computes the declared AP, K metrics, threshold metrics and denominators for rules/model on identical eligible rows. Explanation generation binds exact input and output scale. | EvaluationReport and method-checked Explanation; FR-016–020, SC-004–006. |
| Run publication and read API | A local run store stages results, validates identity/artifact references, marks a run complete, then selects one active snapshot. Case list/detail read the same selected run or report a stale selection. | ScoredRun, ReviewCaseSnapshot and versioned API contracts; FR-009, FR-021–023, SC-007–008. |
| Frontend | Existing case list/detail and API decoder support declared fixture and dataset contracts, distinguish data source from scorer source, show coverage/score meaning/reasons and exact truncation metadata. | Contract/UI regression checks; FR-023–025, SC-007–008. |

The critical feature replay must have this order. A same-time group is scored
against one earlier-history state; only afterward may its facts update later
history. This sketch deliberately excludes labels from the history interface:

    for group in events_grouped_by_interpreted_time:
        snapshots = [features(history_before_group, event) for event in group]
        emit(snapshots)
        history_before_group.add_observable_facts(group)

The publication boundary must have this externally visible behavior:

    candidate = stage_complete_run(scored_events, metadata)
    validate_all_references_scores_and_artifacts(candidate)
    mark_completed(candidate)
    select_active_snapshot(candidate)

If any preceding step fails, the candidate is not active. The plan chooses the
smallest local atomic selection mechanism; no distributed service is required.

The scoring request and assessment contracts must expose at least these concepts.
Field names and types are finalized in the versioned contracts, not assumed from
an uninspected IBM file:

    ScoreRequest:
        canonical_transaction
        historical_feature_snapshot
        dataset_version
        run_id
        scorer_version
        feature_as_of_cutoff

    AssessmentV2:
        transaction_id
        run_id
        dataset_version
        score_source
        score_and_declared_scale
        scorer_version
        feature_version
        event_time
        feature_as_of_cutoff
        actual_scored_at
        explanation_or_explicit_unavailable_state

    CaseListV2:
        active_run_id
        snapshot_reference
        total_alerts
        displayed_alerts
        selected_time_range
        truncated
        items

Dataset source and scorer source are separate fields. The Foundation fixture
payload remains valid under its v1 contract. The v2 design must specify how a
list snapshot reference is supplied to detail lookup and what stale-selection
error is returned if the snapshot is unavailable. The shared API description,
backend models, frontend decoders, examples and negative tests must change
together; weakening closed-object, identity or score checks is not a migration.

### Label-role contract

| Stage | Permitted target-label access | Public/operational output |
|---|---|---|
| Import audit | Read for validity and class accounting only; do not use it to decide event-fact validity. | Event facts and label-eligibility status are separate; labels remain private. |
| History, rules, model scoring, explanations, case/UI | None. | No target, target copy, label-validity feature or evaluation answer. |
| Supervised fitting | Training labels for training-eligible rows only. | Fitted model and manifest, not labels in the scorer request. |
| Validation selection, threshold and optional calibration | Only the declared development labels for their frozen roles. | Selected protocol/scorer/threshold, not test feedback. |
| Final evaluation | Join test labels to frozen predictions after selection and score generation. | Private metrics report; holdout marked consumed on disclosure. |

### Work packages to convert into tasks.md

1. **Source audit and mapping decision (FR-001–004, SC-001):** obtain the authorized
   local source outside Git; record exact observed headers, encoding, date resolution,
   amount formats, labels, file size, license and hash. Freeze a reviewed mapping,
   unknown-column policy, decimal/time interpretation and import version rule.
   Do not invent schema fields before this evidence exists.
2. **Versioned contracts (FR-003–004, FR-008, FR-019–025, SC-007–008):** define
   canonical and public v2 shapes, score scale, stable IDs, snapshot reference,
   stale-selection/error envelope and explicit data/scorer configuration. Review
   producing and consuming owners, then update schema, backend/frontend validators
   and examples together while preserving v1 fixtures.
3. **Importer and identity (FR-001–004, FR-009, SC-001):** test duplicate/ambiguous
   headers, unreviewed columns, malformed/empty files, encodings, precision/overflow,
   bank/direction, identical distinct events, label-ineligible valid events,
   rejected-row stability, interruption, reimport and changed versions.
4. **Feature replay (FR-005–006, SC-002):** test shuffled input, strictly earlier
   history, tied timestamps, exact lookback boundary, warm-up state, same-currency
   aggregation, held-out prior facts and label/future invariance.
5. **Rules scorer (FR-007–009, SC-003):** freeze a small observable rule table and
   score aggregation in the plan; hand-calculate trigger/non-trigger/cold-start
   examples and verify source/version/reasons and identifier invariance.
6. **Evaluation protocol (FR-010–015, SC-004–005):** freeze the split/role manifest,
   positive-count eligibility, feature lineage audit, transform-fit permissions,
   candidate budget, selection/tie policy, per-scorer operating point and holdout
   consumption rule before model experiments.
7. **Model and metrics (FR-012–018, SC-004–005):** fit the bounded candidates,
   compare on identical eligible rows, test AP and K/threshold calculations by hand,
   record boundary ties, zero alerts, calibration roles and uncertainty limitations.
   Report no substantive model result if the source is unavailable or ineligible.
8. **Artifacts and explanations (FR-018–020, SC-006):** verify local artifact hash
   and feature compatibility before load; reject corruption. Test rule reasons,
   model contribution direction/scale/fidelity and run/feature mismatches.
9. **Completed-run publication (FR-009, FR-021–022, SC-007):** failure-inject during
   staging/scoring/selection; verify previous active snapshot or honest empty state,
   restart consistency, stable case identity, zero alerts and deterministic latest-100
   selection with correct counts and time range.
10. **Application integration and reproduction (FR-023–026, SC-007–009):** migrate
    API/UI together, run Foundation fixture and negative regressions, and record
    commands, actual results, dependency/data hashes, machine/time limits and an
    independent teammate reproduction. Do not mark these checks passed until run.

### Decisions the plan must freeze before corresponding code or experiments

- Actual source schema, permitted aliases/unknown columns, label encoding, source-row
  reference, decimal range/zero policy, timezone interpretation and import identity.
- Exact one-day window inclusion, timestamp precision, warm-up representation and
  eligibility effect; the score request and feature catalog must agree.
- Concrete rule indicators, thresholds, score aggregation and missing-history policy;
  a fixture constant is not an empirical rule baseline.
- Observable benchmark view and split boundaries, positive eligibility, every
  training/validation/calibration/test role, candidate/seed/budget and feature lineage.
- Per-scorer validation threshold objective, tie handling, numeric tolerances,
  probability/calibration claim and metric implementation/positive label.
- Trusted local artifact format/hash validation, run snapshot selection, persistence
  and restart procedure, plus a feasible local resource/timebox based on measurements.

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
  validation-only operating policy and each scorer's resulting threshold are fixed before
  final evaluation. The policy must define an objective, alert cap and tie treatment;
  merely choosing an arbitrary threshold that yields at most 20 is insufficient.
  If tied scores make an exact count impossible, record the achievable count and threshold.
  Zero alerts remain valid when the frozen policy finds no qualifying events. This is a
  capstone capacity assumption, not a bank policy.
- The 70/15/15 partition, 20-positive eligibility guardrail, K=20 review budget and
  100-alert display limit are explicit project design defaults, not claims that an
  unavailable Phase 2 rubric mandates those numbers. Record any justified amendment
  before the corresponding experiment or publication.
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
- The actual Phase 2 assignment requirements have not been found. Phase 2 compliance and a
  traceability percentage remain unassessed until that source is identified; the quality
  checklist and Feature 001 handoff cannot substitute for it.

### Source references
- [Feature 002 review transcript](../../prompts/development/002-review.md), including
  corrected second-level findings, scientific/data-engineering risks and Foundation
  compatibility findings. Earlier proposed defects are not assumed confirmed when the
  later independent review narrowed or rejected them.
- [Approved project idea](../../original_idea.md), especially data/scoring and evaluation scope.
- [Foundation contracts](../001-project-foundation/contracts/api.md) and
  [existing replacement/compatibility decisions](../../docs/decisions/foundation.md).
- [IBM dataset repository](https://github.com/IBM/AML-Data) and
  [Kaggle distribution](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml).
- [Dataset authors' paper](https://arxiv.org/html/2306.16424v2).
  Published descriptions support the initial source choice; they do not replace inspecting
  the actual acquired release or establish this project's measured performance.

