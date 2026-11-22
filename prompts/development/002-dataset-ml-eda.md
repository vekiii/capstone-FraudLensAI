# Codex Prompt — FraudLens AI | Feature 002: Dataset, Machine Learning & EDA

## 1. Your role and primary objective

You are a senior Python Machine Learning Engineer, Backend Engineer, and Specification-Driven Development architect working inside the existing **FraudLens AI** repository.

**Your task is to generate a complete, implementation-ready Spec-kit specification package for Feature 002: IBM AML Dataset Integration, Machine Learning Risk Prediction, and Exploratory Data Analysis.**

This is the first development feature after the completed project foundation.

The application already exists. Do not rebuild it.

The intended result of implementing this feature is:

1. Integrate the IBM HI-Small AML transaction dataset.
2. Create a reproducible data preparation and feature-engineering pipeline.
3. Train and evaluate a supervised ML model that identifies transactions associated with synthetic money-laundering activity.
4. Produce a risk score and interpretable prediction for eligible transactions.
5. Connect the trained model to the existing Python FastAPI backend.
6. Make predictions and model results accessible to the existing TypeScript frontend.
7. Add a separate EDA page showing dataset statistics, charts, and distributions.
8. Preserve the existing application behavior, contracts, and replaceable scoring architecture.

**IMPORTANT: This request is for SPECIFICATION GENERATION ONLY.**

Follow:

**Inspect → Specify → Clarify → Research → Plan → Define Contracts → Generate Tasks → Review**

Do not implement application code, import the full dataset, train a model, or generate real-data evaluation results in this Codex session.

The specifications must make the next implementation sessions executable without relying on this conversation.

---

## 2. Mandatory repository inspection

Before generating specifications, inspect the actual repository.

Read these files in order, when present:

1. `AGENTS.md`
2. `next_work.md`
3. `.specify/memory/constitution.md`
4. `original_idea.md`
5. `README.md`
6. `specs/001-project-foundation/spec.md`
7. `specs/001-project-foundation/plan.md`
8. `specs/001-project-foundation/tasks.md`
9. `specs/001-project-foundation/data-model.md`
10. `specs/001-project-foundation/contracts/api.md`
11. `specs/001-project-foundation/contracts/schemas.json`
12. `specs/001-project-foundation/quickstart.md`
13. Relevant existing `backend/`, `frontend/`, `data/`, and test files.

Inspect the current Git branch, working-tree changes, source structure, scoring interface, dependency configuration, and relevant evidence.

The current repository state is authoritative. Do not rely on previous Codex conversations.

If `next_work.md` is missing, report that explicitly and use the applicable task and evidence files to establish context. Do not invent its contents.

Preserve all existing foundation code and contracts.

### Existing technical stack

The foundation uses:

- Python 3.14 and FastAPI
- Pydantic and pytest
- uv with locked Python dependencies
- Vite and vanilla TypeScript
- Vitest and TypeScript type checking
- A local application architecture
- A replaceable Python scoring interface
- Existing `/api` endpoints and TypeScript API validation

Do not introduce React, Streamlit, a separate ML microservice, a graph database, or new infrastructure without an approved requirement.

Inspect existing project conventions before deciding filenames, module placement, or API structure.

### Spec-kit selection

Create a new specification package under:

`specs/002-data-and-risk-scoring/`

If this directory already exists, inspect for naming collisions and preserve existing work. Do not silently overwrite or delete previous specifications.

Explicitly select Feature 002 in the current PowerShell session:

`$env:SPECIFY_FEATURE_DIRECTORY = 'specs/002-data-and-risk-scoring'`

This selects the Spec-kit feature without changing the Git branch.

Use the Spec-kit skills and commands actually available in the repository. Do not invent unsupported commands.

---

## 3. Product and business context

FraudLens AI is an educational Anti-Money Laundering (AML) investigation and prioritization platform.

Its purpose is to help human analysts identify and review potentially suspicious financial transactions.

The model will learn from the IBM synthetic dataset's binary target:

`Is Laundering`

Interpretation:

- `0` — transaction not labeled as laundering in the synthetic dataset
- `1` — transaction labeled as laundering in the synthetic dataset

**Do not confuse the AML laundering label with a general payment-fraud label.**

For the user interface, use terms such as:

- AML risk score
- Suspicious activity
- Potentially suspicious transaction
- Requires review

Do not present model predictions as confirmed crimes, verified fraud, or final AML decisions.

Human analysts retain final authority.

There must be no automatic account blocking, financial intervention, or regulatory submission.

All real-data performance claims must explicitly identify this as an evaluation on synthetic data.

---

## 4. Dataset source and ingestion requirements

### 4.1 Dataset

Use the following source:

**IBM Transactions for Anti-Money Laundering — HI-Small**

Dataset URL:

https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml

Target file:

`HI-Small_Trans.csv`

IBM documentation:

https://github.com/IBM/AML-Data

The actual CSV schema must be verified during implementation.

Expected fields include:

- `Timestamp`
- `From Bank`
- `Account` (sender)
- `To Bank`
- `Account` (receiver)
- `Amount Received`
- `Receiving Currency`
- `Amount Paid`
- `Payment Currency`
- `Payment Format`
- `Is Laundering`

**Important:** The CSV contains two fields named `Account`. The ingestion specification must define an unambiguous mapping for sender and receiver accounts based on verified source positions.

Do not assume both refer to the same account or silently allow a CSV library to overwrite either field.

Bank identifiers and account identifiers must preserve their exact identity, including leading zeros where applicable.

Canonical account identity must combine bank and account, rather than assuming account identifiers are globally unique.

### 4.2 Previously reported reference figures

The following figures were supplied in the project input and are reference values only:

- Source records: 5,078,345
- First-24-hour warm-up records: 1,114,921
- Previously reported rejected records: 0
- Previously reported SHA-256: `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`

These figures are **not verified results from this specification session**.

Create tasks requiring implementation to independently check:

- Actual downloaded source and version
- File size and checksum
- Source schema and types
- Total row count
- Rejected/malformed rows
- Missing values
- Timestamp range
- Label encoding and distribution
- Duplicate and ambiguous identities
- Currency and payment-format values
- Warm-up and scoreable counts

Generate a data-card specification identifying source, license, provenance, limitations, and reproducibility information.

IBM distinguishes the repository license from the dataset license, which is documented as CDLA-Sharing-1.0. Require verification in the data card.

### 4.3 Data storage and processing

Plan a reproducible local pipeline suitable for approximately five million transactions.

Consider streaming or chunked CSV processing and a simple reproducible processed-data format.

Do not require SQLite merely because a previous implementation may have used it.

The plan must explicitly address:

- Memory and disk ceilings
- Deterministic processing
- Stable record identifiers
- Processing interruption and recovery
- Input validation
- Dataset versioning
- Incremental verification
- Data integrity and duplicate handling
- Separation of raw, processed, and evaluation artifacts

Do not load millions of rows into the frontend.

Keep raw datasets, processed datasets, trained artifacts, credentials, and generated evaluation outputs out of Git unless a small reviewed fixture is specifically intended for version control.

The existing foundation must continue to run without requiring the downloaded dataset or trained model.

---

## 5. Time normalization, warm-up, and historical features

### 5.1 Timestamp policy

Define an explicit UTC normalization policy.

The source timestamp format and source timezone must be investigated and documented. Do not claim the source specifies a timezone unless verified.

If a timezone assumption is necessary, make it explicit.

Equivalent timestamps that represent the same UTC instant must form one group.

All timestamp ties must have deterministic processing order.

A group of transactions occurring at the same normalized instant cannot contribute to one another's historical features.

### 5.2 First-24-hour warm-up

The first 24 hours of source data provide historical context.

These records must not receive production-style model predictions or alerts because a complete previous 24-hour history is unavailable.

Report the following separately:

- Source records
- Rejected records
- Warm-up/context records
- Scoreable records

Define and test the exact temporal boundary and inclusivity rules.

### 5.3 Required historical features

The initial model must use the following eight historical features:

1. `sender_out_count_24h`
2. `sender_distinct_receivers_24h`
3. `sender_paid_count_same_currency_24h`
4. `sender_paid_sum_same_currency_24h`
5. `receiver_in_count_24h`
6. `receiver_distinct_senders_24h`
7. `receiver_received_count_same_currency_24h`
8. `receiver_received_sum_same_currency_24h`

Every feature must use only transactions that occurred **strictly earlier than the current transaction and within its preceding 24 hours**.

A transaction must never contribute to its own historical features.

Same-timestamp transactions cannot contribute to each other's history.

Define precisely:

- Feature type
- Formula or aggregation rule
- Time-window boundaries
- Account identity
- Currency grouping
- Missing-value handling
- Expected behavior for empty history
- Deterministic feature order

Do not aggregate amounts from different currencies without a documented conversion policy.

### 5.4 Current-transaction features

Evaluate a small, justified set of current-transaction fields, such as:

- Amount paid
- Payment currency
- Payment format

Research the appropriate representation of categorical variables and numerical values.

Choose exact initial fields during specification and record them in the feature contract before experiments.

Exclude:

- `Is Laundering`
- Future transaction information
- Future transaction aggregates
- Analyst conclusions
- Future case outcomes
- Any post-transaction investigation data

No new features may be added opportunistically after inspecting validation or test performance.

---

## 6. Chronological dataset partitioning

Define partition rules before observing model outcomes.

### 6.1 Development versus showcase

The dataset must have two major contiguous chronological regions:

**Development region:** approximately the first 3,000,000 source records.

**Showcase region:** all later source records, reserved for future time-ordered replay.

Choose the boundary using the cumulative source-record count at whole normalized timestamp groups.

Select the boundary closest to 3,000,000 records.

If two boundaries are equally close, select the earlier boundary.

Do not split one timestamp group across partitions.

Do not describe the three million development source records as three million trainable examples, because the development region also includes warm-up context.

### 6.2 Train / validation / test

Within the development region, partition scoreable records chronologically:

- 70% training
- 15% validation
- 15% testing

Use cumulative scoreable counts and whole-timestamp boundaries.

Choose boundaries closest to cumulative 70% and 85% targets. Resolve exact ties in favor of the earlier timestamp boundary.

Every partition must be nonempty.

Do not use random row-level splitting, stratification, or post-hoc boundary adjustments based on label outcomes.

### 6.3 Class-distribution audit

The dataset is heavily imbalanced.

Balanced partitions means reasonably comparable natural positive-class prevalence, not equal positive and negative counts.

Freeze the following acceptance rule before aggregate label access:

- Train, validation, test, and showcase must each contain at least 20 positive scoreable records.
- Each partition's positive prevalence must be between 0.75 and 1.25 times the overall development scoreable prevalence, inclusive.

Determine timestamp boundaries from timestamps and counts alone.

Only afterward perform the authorized aggregate audit.

If the acceptance rule fails:

1. Stop the progression toward training.
2. Report exact counts and prevalences.
3. Document no more than three nearby whole-timestamp boundary alternatives.
4. Require a human decision before changing the protocol.

Do not automatically choose an alternative, rebalance partitions, widen tolerance, or move records.

Training-only class weighting or negative downsampling may be specified after partition membership is frozen.

Never change the natural class distribution of validation, test, or showcase.

---

## 7. Label-access restrictions and frozen protocol

### 7.1 Label isolation

The target `Is Laundering` must not be available to the runtime scoring adapter, public transaction APIs, UI transaction details, investigation tools, or model-input features.

For the initial split audit, allow only:

- Development aggregate counts and positive counts by UTC day.
- Development partition-level aggregate counts.
- One partition-wide showcase aggregate covering source rows, scoreable rows, and positives.

Do not allow showcase per-day, sub-range, or record-level label inspection.

Define a label-access audit log recording:

- Purpose
- Requested query shape
- Timestamp
- Returned row count
- Allowed/refused result
- Relevant execution reference

Train and validation record-level labels may be used only for authorized training/model-selection purposes.

Development-test and showcase record-level labels remain unread until frozen predictions exist and a separate explicit instruction authorizes the relevant evaluation.

### 7.2 Frozen protocol

Before fitting any real-data model, require a frozen and hashed protocol containing:

- Dataset identity and checksum
- Timestamp normalization rules
- Warm-up definition
- Historical feature rules
- Exact chronological boundaries
- Partition counts and allowed prevalence statistics
- Stable per-partition scoreable ID hashes
- Feature schema and feature version
- Random seed 42
- Deterministic tie-handling rules
- Preprocessing rules
- Training-only imbalance strategy
- Candidate model configuration
- Evaluation metrics
- Threshold selection objective
- Resource limits
- Label-access restrictions
- Showcase role: `demo_only_record_labels_unread`

Provenance, count, split, identity, label-access, or protocol-hash mismatches must be treated as explicit stop conditions.

---

## 8. Machine learning model requirements

### 8.1 Prediction objective

Implementing this feature must eventually produce a supervised binary AML risk prediction.

For each eligible transaction, the selected model returns a bounded risk score between 0 and 1.

A model output must not be described as a calibrated probability until calibration has actually been evaluated and documented.

The user interface may display a threshold-based status such as "Review recommended" or "Below review threshold", without implying a confirmed label or analyst decision.

### 8.2 Required baselines

Specify three baseline approaches:

**Baseline A — Constant prevalence**

Use the training partition's positive-class prevalence as the constant score.

**Baseline B — Decision tree**

Use an interpretable decision tree with:

- Maximum depth: 5
- Minimum leaf size: 500

**Baseline C — Logistic regression**

Use L2-regularized logistic regression.

Preprocessing must be fitted exclusively on training data.

### 8.3 Primary candidate model

Specify a bounded `HistGradientBoosting` model-selection experiment using scikit-learn.

Requirements:

- Random seed 42
- At most five gradient-boosting candidate fits
- A candidate configuration declared before fitting
- Model selection using validation data only
- Reproducible training
- Memory and execution-budget limits

Rank candidates by:

1. Validation Average Precision
2. Validation Precision@20
3. Simplicity using a documented deterministic tie rule

Compare the selected candidate with the baselines.

Choose one understandable, reproducible model for application integration.

Do not introduce neural networks, GNNs, transformers, large AutoML searches, or external inference providers.

### 8.4 Class imbalance

Consider only declared training-time options:

- No class adjustment
- Appropriate class weighting
- Deterministic negative downsampling retaining every training positive

If downsampling is considered, the specifications must predeclare candidate ratios, stable ID-based selection, and seed.

Do not oversample or downsample validation, test, or showcase.

New feature admission requires a prespecified improvement margin. Record a proposed minimum of +10% relative validation AP improvement over the frozen baseline, with maintained interpretability and documented analyst use.

This improvement margin requires team approval before feature experiments.

### 8.5 Explainability

Design an explanation contract that reports only defensible model and transaction information.

Possible explanatory content includes:

- Observed transaction amount and currency
- Historical transaction frequency
- Number of recent counterparties
- Relevant historical amount aggregates
- Model feature importance or contribution, where technically valid
- Model version and feature version

Do not fabricate SHAP values or explanations.

A model explanation is not proof that a transaction constitutes money laundering.

---

## 9. Model evaluation

Plan the following metrics:

- Average Precision — primary ranking metric
- ROC AUC
- Precision@20, Precision@50, Precision@100
- Recall@20, Recall@50, Recall@100
- Precision-recall curve data
- Brier score, labeled uncalibrated unless calibration is performed
- Confusion matrix at the selected threshold
- False-positive and false-negative counts
- Positive prevalence and denominators
- Actual alert counts per UTC day

Accuracy can appear only with a clear warning explaining the rare-positive class problem.

Do not invent any metric values.

### Threshold selection

The decision threshold must be selected using validation data alone.

Specify a clear objective, such as maximizing validation F0.5.

Do not assume a universal 0.5 threshold.

Do not enforce a fixed daily 20-alert maximum.

Precision@20 is an evaluation metric, not an operational alert cap.

The plan must allow:

- Zero alerts on a given day
- More than 20 alerts on a given day
- Explicit daily alert volume reporting
- Pagination without silently suppressing alerts

Testing and showcase data must never be used to select the model, features, threshold, or alert policy.

### Evaluation authorization

Separate the following milestones:

1. Training and validation experiments
2. Model and threshold selection
3. Frozen predictions
4. Explicitly authorized development-test evaluation
5. Future showcase replay

If test evaluation has not been authorized, the application may display real validation metrics but must not claim test performance.

---

## 10. Integration with the existing FastAPI backend

The application already contains a replaceable scoring interface.

The new trained model must integrate behind that boundary rather than requiring a separate scoring microservice.

Inspect:

- `backend/src/fraudlens/scoring.py`
- `backend/src/fraudlens/contracts.py`
- `backend/src/fraudlens/cases.py`
- `backend/src/fraudlens/main.py`

These are existing foundation paths; verify their current contents before designing changes.

Plan an implementation that supports the existing scorer contract while clearly distinguishing:

- Fixture scoring
- Rules-based scoring
- Trained-model scoring

Preserve the accepted `RiskAssessment` semantics, including bounded scores, transaction identity, source, scorer version, scoring timestamp, and explanation.

If the foundation's three-digit synthetic transaction ID contract cannot represent IBM transaction identifiers, specify a versioned extension or separate real-data transaction contract. Do not silently widen or break the foundation schema.

Model training must be an explicit offline operation, not something automatically performed during API startup.

Model artifacts must include provenance and version checks.

Provide a safe fallback: the existing fixture application must still run when the dataset or trained model is unavailable.

### Planned API contracts

Design necessary read-only API contracts, without assuming they already exist, for:

- Dataset metadata and available statistics
- Transaction predictions
- Paginated scored transaction records
- Model metadata and version
- Authorized model evaluation summaries
- EDA chart data

Choose final endpoint paths in the API design after reviewing existing routes.

Do not create unbounded endpoints that return millions of raw rows.

Keep existing API error conventions and validation behavior.

Do not expose target labels through scoring APIs.

Define how the frontend distinguishes genuine model scores from illustrative fixture scores.

---

## 11. TypeScript frontend integration

The frontend is already implemented using Vite and vanilla TypeScript.

Do not rebuild the UI or migrate frameworks.

Inspect the existing:

- `frontend/src/main.ts`
- `frontend/src/api.ts`
- `frontend/src/contracts.ts`
- `frontend/src/views.ts`
- `frontend/src/styles.css`
- Relevant frontend tests and routing/navigation logic

Plan the smallest compatible extension.

### 11.1 Prediction display

The application must eventually show transactions scored by the selected ML model.

A transaction detail should support:

- Transaction identifier
- Timestamp
- Sender and receiver identities
- Amount and currency
- Payment format
- AML risk score
- Review-threshold status
- Scoring source
- Model version
- Explanation or relevant observed features

Existing list/detail behavior should remain functional.

Never show the ground-truth `Is Laundering` label as if it were a runtime prediction.

Never display fixture outputs as real model predictions.

### 11.2 Model results

Plan a simple model-performance section showing verified and authorized evaluation data, such as:

- Selected model
- Model version
- Feature version
- Evaluation partition
- Average Precision
- Precision and Recall
- Precision-recall curve
- Threshold used
- Alert volume
- Comparison with baseline approaches

For unavailable results, show a clear unavailable or not-yet-evaluated state.

Do not hardcode sample performance values in a way that could be mistaken for measured results.

---

## 12. Dedicated Exploratory Data Analysis page

Plan a **separate navigable EDA page** within the existing TypeScript application.

Working title:

**Dataset Explorer — AML Transaction Analysis**

This page is for understanding the dataset, not for making final AML decisions.

The EDA page should provide a useful visual overview without requiring the user to inspect millions of raw records.

### 12.1 Dataset overview cards

Include:

- Total source transactions
- Valid and rejected transaction counts
- Warm-up/context transaction count
- Scoreable transaction count
- Date range
- Unique sender and receiver accounts
- Number of banks
- Number of payment currencies
- Number of payment formats
- Permitted aggregate laundering-label counts and prevalence

All values must come from verified source-derived aggregates.

Display the dataset version, source, and relevant scope of each statistic.

### 12.2 Charts and visualizations

Plan these visualizations:

**A. Transaction volume over time**

A daily transaction-count line chart.

Optionally include hourly volume if the aggregation is reasonably bounded.

**B. Payment method distribution**

A bar chart showing the number of transactions for each payment format.

**C. Transaction currency distribution**

A chart showing transaction counts by payment currency.

**D. Transaction amount distribution**

A histogram or percentile-oriented visualization.

Amounts from different currencies must be separated or explicitly normalized under an approved conversion rule.

**E. AML class imbalance**

A clearly labeled view of the permitted development-data aggregate class distribution.

Do not expose unauthorized test or showcase label detail.

**F. Data quality overview**

Show missing-value counts, rejected-record counts, and relevant schema-validation outcomes.

**G. Chronological partition overview**

Show source and scoreable record counts by partition and the associated time ranges.

Only display label statistics where the frozen access policy permits them.

**H. Model performance overview**

Show verified, authorized validation results and model comparisons. This can link to the prediction or model-results section rather than duplicating all content.

### 12.3 Technical expectations

- EDA aggregation runs in Python.
- TypeScript renders precomputed or bounded aggregate results.
- The browser must not download or process the full CSV.
- APIs return explicitly typed and validated results.
- Graph data must have clear units and labels.
- Counts and percentages must use correct denominators.
- Empty, unavailable, loading, malformed-response, and retry states must be covered.
- All charts should be accessible and readable.
- Avoid unnecessary visualization dependencies.
- Do not create misleading cross-currency monetary totals.
- Exclude raw target labels and transaction-level ground truth from the UI.

### 12.4 Project scope checkpoint

The approved project plan originally defined four principal screens.

A new dedicated EDA page may increase the UI scope.

Record this requested addition, its benefit, estimated implementation impact, and whether team approval is required under the constitution.

Include its specification and tasks, but do not represent an unrecorded team approval as already obtained.

---

## 13. Future time-ordered showcase

The later contiguous showcase partition is reserved for a future live demonstration.

Include its design and dependencies in the specification, but do not make full replay implementation a prerequisite for delivering the first useful dataset, prediction, and EDA workflows.

The planned showcase must:

- Replay transactions in normalized chronological order.
- Use the frozen model and approved score threshold.
- Display model outputs without showcase ground-truth labels.
- Preserve strict historical feature calculations.
- Support a controllable presentation speed without changing event order.
- Display alerts without artificial daily suppression.

When showcase replay begins, preload the immediately preceding 24 hours of development transaction facts as historical context.

Do not substitute the dataset's original first-day warm-up for this context.

The original warm-up may be shown separately as a labeled historical prelude, but must not receive predictions or alerts.

---

## 14. Required Spec-kit artifacts

Generate a complete Feature 002 package.

Expected structure:

`specs/002-data-and-risk-scoring/`

### `spec.md`

Include:

- Feature purpose and business problem
- Scope and exclusions
- User stories and priorities
- Dataset ingestion requirements
- Data-quality requirements
- Historical feature requirements
- Chronological partition requirements
- Label-isolation requirements
- Machine learning requirements
- Evaluation requirements
- Prediction API requirements
- TypeScript integration requirements
- Dedicated EDA page requirements
- Showcase requirements and deferred scope
- Edge cases
- Testable acceptance criteria
- Measurable success criteria
- Explicit dependencies on the foundation

Use traceable functional requirement identifiers such as `FR-001`, `FR-002`, etc.

### `plan.md`

Include:

- Existing architecture and integration points
- Proposed data flow
- Streaming or bounded processing approach
- Dataset and model artifact lifecycle
- Feature-engineering architecture
- Model development and evaluation architecture
- API and TypeScript integration
- EDA aggregation and visualization architecture
- Resource limitations
- Error handling
- Testing and verification strategy
- Explicit unresolved decisions
- Constitution compliance review

Include a clear architecture diagram:

`IBM CSV → Validation → Chronological Processing → Historical Features → Frozen Splits → Model Training → Validation → Frozen Model → FastAPI Scorer → TypeScript UI`

The EDA pipeline should branch from verified source and authorized aggregate data, rather than consuming evaluation labels through the scoring API.

### `research.md`

Document decisions and alternatives for:

- Large-file processing
- Processed-data storage
- Historical 24-hour aggregates
- Model candidates
- Class imbalance
- Scikit-learn compatibility with the locked environment
- Model artifact serialization and versioning
- Evaluation metrics
- Explainability
- Frontend charting approach
- Training/runtime separation
- Data provenance and licensing

Mark proposals as proposals rather than completed experiments.

### `data-model.md`

Define:

- Raw IBM transaction
- Canonical transaction
- Bank-qualified account identity
- Historical feature vector
- Dataset manifest
- Chronological partition
- Frozen training protocol
- Model metadata
- Prediction result
- Evaluation summary
- EDA summary
- EDA chart series

Specify field names, types, constraints, units, identity rules, and label visibility.

### `contracts/`

Create only the necessary versioned contracts, such as:

- `api.md`
- `schemas.json`
- Relevant feature/prediction contract documentation

Match actual foundation conventions.

Document successful responses, errors, validation behavior, examples, and backward-compatibility constraints.

No unapproved breaking changes.

### `quickstart.md`

Provide planned Windows PowerShell instructions for:

- Installing locked dependencies
- Placing or acquiring the dataset
- Verifying provenance
- Running ingestion
- Generating historical features
- Running the split audit
- Freezing the protocol
- Training and validating candidate models
- Generating authorized predictions
- Starting the existing backend/frontend
- Accessing model predictions
- Accessing the EDA page
- Running tests and checks

Clearly distinguish commands that exist today from commands that implementation tasks must create.

Do not invent successful execution output.

### `tasks.md`

Generate small, sequential, actionable implementation tasks with unique IDs, file paths, dependencies, requirement traceability, and verification expectations.

All newly generated implementation tasks must initially remain unchecked.

Organize the tasks into coherent delivery stages:

**Stage A — Dataset and provenance**

Source verification, data card, schema mapping, safe local processing, data validation, and synthetic tests.

**Stage B — Historical features and frozen partitions**

Strict-prior historical features, UTC normalization, warm-up, chronological split, aggregate label audit, access controls, and frozen protocol.

**Stage C — Machine learning**

Baseline models, bounded model search, training-only preprocessing, validation, model selection, threshold selection, model metadata, and interpretable predictions.

**Stage D — Backend prediction integration**

Model artifact loading, scorer adapter, real-data transaction contract, read-only prediction API, compatibility tests, and fixture fallback.

**Stage E — Frontend prediction/results integration**

Typed API consumption, risk-score presentation, model provenance, performance display, and UI error states.

**Stage F — Dedicated EDA page**

Aggregate computations, EDA API contracts, TypeScript navigation, charts, dataset statistics, data-quality views, and tests.

**Stage G — Gated evaluation and future showcase**

Frozen predictions, separately authorized test evaluation, showcase context, future chronological replay, and relevant verification.

Prioritize the smallest complete data-to-prediction workflow before optional visualization improvements or replay enhancements.

Each task should be independently reviewable and contain concrete completion criteria.

---

## 15. Testing and acceptance requirements

Specify a RED → GREEN → REFACTOR workflow for critical business behavior.

Separate:

1. Synthetic unit and contract tests
2. Real-dataset provenance verification
3. Authorized model-development experiments
4. Separately authorized holdout evaluation
5. Frontend integration tests
6. Human review and reproducibility checks

Include explicit negative tests for:

- Missing or malformed CSV
- Duplicate `Account` header mapping
- Invalid bank/account identities
- Unknown currencies and payment formats
- Invalid amounts
- Missing or invalid timestamps
- Equivalent timestamp spellings
- Same-timestamp and future leakage
- Incorrect 24-hour boundaries
- Warm-up records receiving predictions
- Timestamp groups split across partitions
- Unstable transaction IDs
- Partition-hash mismatch
- Too few positive examples
- Class prevalence outside tolerance
- Unauthorized record-level label requests
- Unauthorized showcase sub-partition queries
- Cross-currency aggregation errors
- Interrupted processing
- Resource-limit exhaustion
- Missing or incompatible model artifact
- Out-of-range or nonfinite scores
- Model/transaction identity mismatch
- UI accidentally showing target labels
- Invalid API payloads
- EDA empty/unavailable states
- More than 20 alerts on a day without suppression
- Missing immediately preceding historical context for showcase

Require actual execution evidence before marking implementation tasks complete.

Synthetic test success is not proof of trained-model quality.

Do not claim model evaluation until the relevant real evaluation has actually executed.

---

## 16. Scope and implementation controls

This specification-generation session must not:

- Implement pipeline or application code
- Install or upgrade dependencies
- Download the full Kaggle dataset
- Read actual record-level labels
- Train models
- Create model artifacts
- Generate fabricated metric values
- Modify foundation fixture data
- Break existing APIs
- Replace the existing TypeScript application
- Introduce unrelated infrastructure
- Implement RAG, AI investigation workflows, or simulation features
- Automatically expand scope into future project features
- Mark implementation tasks completed
- Invent RED/GREEN evidence
- Change the Git branch
- Commit, push, merge, or deploy

Preserve existing uncommitted changes.

Do not reset, stash, clean, or delete work to obtain a clean checkout.

Do not silently weaken requirements because a planned implementation may be difficult.

Where a necessary technical choice is genuinely unresolved, record:

- The decision required
- Available options
- Recommended option and rationale
- Impact on implementation
- Whether explicit approval is required

Especially identify unresolved choices around current-transaction features, candidate model grid, resource ceilings, threshold objective, model-artifact format, EDA scope approval, and the proposed +10% feature-admission rule.

Do not invent consensus or approval.

---

## 17. Deliverables and final report

Generate the Feature 002 specifications in the repository following the current Spec-kit conventions.

Before finishing, review the new files for:

- Contradictions
- Missing requirements
- Untestable acceptance criteria
- Incompatible foundation contracts
- Unclear chronology or leakage restrictions
- Label-access violations
- Missing negative cases
- Implementation tasks without dependencies
- Unnecessary complexity
- Scope expansion beyond this feature

Run only appropriate read-only or specification-validation checks.

Do not run implementation tests merely to claim new functionality exists.

Your final Codex response must contain:

1. Files created or updated
2. Key architectural decisions
3. Proposed dataset-processing approach
4. Model-development and evaluation approach
5. Backend/frontend integration approach
6. Planned EDA page functionality
7. Implementation-stage task breakdown
8. Open decisions or approval gates
9. Checks actually run and their observed results
10. Checks not run and why
11. Exact first implementation task recommended

**STOP after completing and reviewing the specification package.**

Do not begin implementation automatically.

The goal is an implementation-ready, controlled Feature 002 specification that another Codex session can execute incrementally, starting with verified dataset ingestion and ending with trustworthy AML risk predictions, integration into the existing web application, and a dedicated EDA page.