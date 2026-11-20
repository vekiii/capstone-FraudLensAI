# Feature Specification: Dataset, Machine Learning and EDA

**Feature directory**: `002-data-and-risk-scoring`
**Branch observed**: `feature/002-clean-start`
**Created**: 2026-11-18
**Status**: Specification package; implementation not started by this document
**Input**: User-provided Feature 002 prompt, repository instructions, constitution, and foundation contracts.

## Purpose

Enable a human analyst to inspect a transaction's synthetic AML risk assessment, understand its evidence and model provenance, and explore bounded dataset aggregates. The learning target is IBM's synthetic `Is Laundering` label. It represents a dataset label, not payment fraud, verified crime, or a final AML decision. Analysts retain all decisions; there are no account interventions or regulatory submissions.

## User Scenarios & Testing

### US1 — Verify and prepare the dataset (P1)

As a data contributor, I can reproduce a validated, versioned local transaction dataset without losing source identity or corrupting the two `Account` columns.

**Independent check**: Synthetic CSV fixtures exercise schema mapping, deterministic identity, bounded/interrupted processing, and audit manifests without using real target labels.

Acceptance scenarios:
1. Given a verified local source file, when the pipeline runs, then it records source identity, license/provenance, checksum, parser/schema version, counts, rejection reasons, and output hashes.
2. Given duplicate `Account` headers, when columns are read, then sender and receiver are mapped only by verified source position and neither value is overwritten.
3. Given malformed records or an interrupted run, when processing stops or resumes, then accepted/rejected rows reconcile with source counts and committed outputs remain verifiable.

### US2 — Produce leakage-safe features and frozen partitions (P1)

As an ML contributor, I can derive temporal features and chronological development partitions with a frozen, auditable protocol.

**Independent check**: Hand-computed tiny fixtures verify strict prior-only 24-hour features, timestamp ties, warm-up, and whole-timestamp boundaries.

Acceptance scenarios:
1. Given transactions at the same normalized instant, when features are generated, then none contributes to another's history.
2. Given a transaction at time `t`, when historical counts/sums are computed, then only events in `[t−24h, t)` contribute, grouped by bank-qualified identity and relevant currency.
3. Given the first accepted instant `t0`, when eligibility is assigned, then records in `[t0,t0+24h)` are context-only and a record at `t0+24h` is scoreable.
4. Given chronological split targets, when boundaries are selected, then complete timestamp groups stay intact and ties select the earlier boundary.

### US3 — Train and assess a reproducible AML model (P1)

As an ML contributor, I can compare a small, predeclared model set and freeze one explainable scorer without tuning on held-out labels.

**Independent check**: Synthetic fixtures validate protocol gating, preprocessing fit boundaries, ranking/threshold calculations, score bounds, and provenance; synthetic success is not model-quality evidence.

Acceptance scenarios:
1. Given a hashed frozen protocol, when model development runs, then only training labels fit preprocessing/model parameters and only validation outcomes select the model and threshold.
2. Given the test and showcase regions, when development proceeds, then record-level labels remain unread until separate authorization and frozen predictions.
3. Given a candidate result, when presented, then metric denominators, partition, threshold, data syntheticity, model and feature versions are explicit.

### US4 — Inspect an eligible transaction prediction (P1)

As an analyst, I can inspect a model risk score, review status, supporting observed features, and provenance while knowing the result is not a finding.

**Independent check**: API and UI contract checks cover valid model results, fixture fallback, ineligible warm-up records, invalid scores, identity mismatch, missing model, and unavailable service.

Acceptance scenarios:
1. Given an eligible transaction and a compatible local model, when its assessment is requested, then the response includes its identity, bounded score, status, model/feature versions and defensible explanation.
2. Given a warm-up or invalid transaction, when a prediction is requested, then no assessment is returned and a controlled eligibility/validation response is shown.
3. Given no compatible artifact, when the app starts in fixture mode, then existing fixture behavior remains available and no model download is attempted.

### US5 — Review model results (P2)

As an analyst or reviewer, I can inspect authorized aggregate development/validation metrics and their limits without seeing transaction-level labels.

**Independent check**: Closed response schemas and authorization tests reject test/showcase label access and show unavailable metrics as unavailable, not zero.

### US6 — Explore dataset aggregates (P2)

As an analyst, I can use a dedicated EDA page to understand source coverage, data quality, categorical distributions, and currency-separated amount distributions.

**Independent check**: API/UI tests verify correct denominators, bounded response sizes, no transaction-level data or target labels, and empty/unavailable/retry states.

## Scope

### In scope

- Local, reproducible ingestion and validation of IBM Transactions for AML `HI-Small_Trans.csv`.
- A data card and manifest; streaming/bounded preparation; canonical transaction identity.
- Strict-prior 24-hour historical features, warm-up exclusion, chronological development/showcase regions and frozen train/validation/test splits.
- A small, declared baseline comparison and bounded scikit-learn `HistGradientBoosting` candidate experiment.
- A local replaceable FastAPI scorer, read-only prediction/results contracts, and TypeScript presentation.
- A separate EDA page using bounded, server-computed aggregate results.
- A later, gated chronological showcase design; full replay is not required for the first useful data-to-prediction and EDA workflow.

### Excluded

Real customer data or claims of real-world model efficacy; general payment-fraud classification; LLM/RAG features; graph databases, GNNs, transformers, broad AutoML; external ML services; automatic actions or regulatory submissions; model training at app startup; browser-side full-dataset processing; test/showcase tuning; live replay as a prerequisite; deployment or multi-user security claims.

## Functional Requirements

### Source and preparation

- The expected source field names are `Timestamp`, `From Bank`, two `Account` columns, `To Bank`, `Amount Received`, `Receiving Currency`, `Amount Paid`, `Payment Currency`, `Payment Format`, and `Is Laundering`. Expected positional mapping is zero-based: `From Bank` + first `Account` at indices 1/2 form sender identity; `To Bank` + second `Account` at indices 3/4 form receiver identity. This is an unverified source hypothesis, not a claim about the acquired CSV: implementation MUST compare the exact header sequence with the selected IBM source documentation/file before using these positions and stop if it differs.
- **FR-001**: The pipeline MUST identify the source and release, preserve the original bytes, and compute SHA-256 before parsing. Prompt-supplied reference figures are unverified only: 5,078,345 source rows, 1,114,921 first-24-hour warm-up rows, 0 rejected rows, and SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`. These MUST be independently checked against the acquired source. For the exact local copy, the user-directed [T203 exception](protocol.md#t203-local-copy-decision-and-t210-scope) permits a content-addressed local revision in lieu of an unavailable Kaggle release number for local canonical preparation only; upstream release remains explicitly unknown.
- **FR-002**: The importer MUST verify the actual CSV header, column count/order, types, duplicate header behavior, and source documentation. It MUST map the two `Account` fields by verified position to sender and receiver; duplicate names MUST never overwrite values.
- **FR-003**: Canonical identity MUST preserve exact bank/account text, including leading zeroes, and combine bank plus account. CSV values MUST initially be read as text; no numeric coercion of identifiers is permitted.
- **FR-004**: A reproducible manifest/data card MUST record source, acquisition date/method, license, source and processed checksums, parser/schema version, row counts, rejection/missing counts, timestamp and value ranges, categorical values, label encoding/distribution in restricted audit output, processing configuration, and limitations. Under the explicit T203 local-copy exception, the acquisition date and upstream release are recorded as unknown rather than invented; restricted label distribution and temporal counts remain deferred until the authorized partition/audit tasks.
- **FR-005**: Raw data, processed data, model artifacts, credentials, and generated evaluations MUST remain outside Git except reviewed small synthetic fixtures. The foundation MUST continue running without any of them.
- **FR-006**: Preparation MUST be deterministic, bounded-memory, restartable at verified checkpoints, and report source/accepted/rejected/warm-up/scoreable rows separately. Corruption, count mismatch, checksum mismatch, or resource exhaustion MUST stop downstream modeling.
- **FR-007**: Invalid rows MUST be rejected with a bounded reason code and source-row reference. Invalid timestamp, bank/account, amount, unsupported label, malformed encoding, or ambiguous schema MUST not be silently repaired.

### Time and features

- **FR-008**: Every timestamp MUST normalize to UTC at a precision that preserves source ordering. Explicit offsets denote instants and normalize to one UTC value. A timezone-naive source value is provisionally interpreted as UTC only after source documentation is checked and the assumption is recorded; contradictory evidence blocks ingestion pending decision.
- **FR-009**: Transactions MUST be ordered by normalized instant, then stable source-row identity for reproducible processing. All equal-instant rows form an indivisible group for features and partitions.
- **FR-010**: The warm-up interval is `[t0,t0+24h)`, where `t0` is the earliest valid normalized source instant. These rows provide history only and MUST not receive prediction/alert outputs. At exactly `t0+24h`, scoring is eligible.
- **FR-011**: Historical features MUST include, in this fixed order: `sender_out_count_24h`, `sender_distinct_receivers_24h`, `sender_paid_count_same_currency_24h`, `sender_paid_sum_same_currency_24h`, `receiver_in_count_24h`, `receiver_distinct_senders_24h`, `receiver_received_count_same_currency_24h`, `receiver_received_sum_same_currency_24h`.
- **FR-012**: Each feature MUST use prior transactions only in `[t−24h,t)`, excluding the current event and all same-instant events. Sender/receiver identity is bank-qualified. Paid features group by `Payment Currency`; received features group by `Receiving Currency`. Empty-history counts and sums equal zero. Monetary sums MUST not combine currencies.
- **FR-013**: Feature definitions MUST specify decimal precision, null handling, categorical unknown handling, deterministic order, and stable feature version. Unknown or missing required inputs MUST be rejected or mapped by an explicitly versioned policy, never silently guessed.
- **FR-014**: Before experiments, freeze a small current-transaction feature set. Recommendation for review: amount paid as a numeric log-transformed value plus categorical payment currency and payment format, with declared unknown-category handling. Do not add features based on validation/test outcomes.
- **FR-015**: `Is Laundering`, future transactions, post-transaction investigation data, and analyst conclusions MUST be excluded from prediction inputs and runtime/public transaction contracts.

### Partitions and label governance

- **FR-016**: The cumulative source-record boundary nearest 3,000,000 rows MUST divide development from showcase at a whole normalized timestamp group; exact-distance ties choose the earlier boundary. Development includes warm-up rows; do not call it 3,000,000 trainable rows.
- **FR-017**: Scoreable development records MUST be split chronologically 70/15/15 into train/validation/test using cumulative scoreable counts, whole timestamp groups, nearest boundaries and earlier-boundary tie breaks. Partitions MUST be nonempty. No random/stratified split or label-driven boundary adjustment is allowed.
- **FR-018**: Before aggregate label access, freeze the audit rule: train, validation, test and showcase each have at least 20 positive scoreable records; each partition's prevalence is within inclusive 0.75–1.25× overall development scoreable prevalence. Determine boundaries from timestamps/counts only. A failed audit stops training and requires a human decision; at most three nearby boundary alternatives may be reported, without automatic selection or tolerance changes. **2026-11-19 user-directed, post-audit exception for this exact content-addressed local copy:** retain the original frozen chronological boundaries and original failed audit; treat the showcase prevalence ratio as a reported diagnostic with no pass/fail cap for subsequent local demo preparation. The ≥20-positive rule and 0.75–1.25× rule for train/validation/test remain. Do not claim the original audit passed, use showcase labels to move boundaries or choose a model, or describe showcase as an unbiased performance holdout. This exception must be bound to the exact source, boundary and aggregate-audit hashes in the later frozen protocol; any different source/split requires a new predeclared audit rule and human review.
- **FR-019**: Initial label audit access is limited to development aggregate positives/counts by UTC day and partition totals, plus one showcase-wide total (source, scoreable, positives). Showcase daily, subrange, and record-level labels are forbidden. All allowed/refused query shapes MUST be audited.
- **FR-020**: Training/validation record labels may be used only for approved model training/selection. Test/showcase record labels remain unread until predictions are frozen and a separate instruction authorizes the exact evaluation.
- **FR-021**: Before fitting, hash a frozen protocol containing dataset/checksum, time and warm-up rules, features/version, boundaries/counts, allowed prevalence and any explicitly documented post-audit exception with its original audit hash, partition scoreable-ID hashes, seed 42, tie rules, preprocessing, imbalance option, candidate grid, metrics, threshold objective, resource ceilings, label rules, and showcase role `demo_only_record_labels_unread`. Any hash/provenance mismatch is a stop condition.

### Modeling and evaluation

- **FR-022**: The objective is a binary prediction of the synthetic AML label. Return finite scores in `[0,1]`; call them risk scores unless probability calibration is explicitly evaluated and documented.
- **FR-023**: Compare training-prevalence constant, decision tree (max depth 5, minimum leaf 500), L2 logistic regression, five predeclared `HistGradientBoosting` fits, and eight predeclared LightGBM fits. Implement the LightGBM path first. Exact settings are frozen in [T221 model choices](t221-model-choices.json). Seed 42 applies wherever supported. Preprocessing fits on training only. The user reported team approval of this expanded comparison on 2026-11-20 in [the decision record](../../prompts/development/002-T221-team-decision.md).
- **FR-024**: Select one model across the declared families using validation positive-class F1 at its selected validation threshold, then Average Precision, then Precision@20, then the fixed simplicity/order tie-break in the [T221 model choices](t221-model-choices.json). Compare the selected model to every baseline. Do not tune using test or showcase. This supersedes the original AP-first ranking under the 2026-11-20 reported team decision.
- **FR-025**: Declare class strategy before fitting: no adjustment, supported class weighting, or deterministic ID-based negative downsampling retaining every positive. If downsampling is used, freeze ratios, seed, and ID-based rule. Validation/test/showcase retain natural prevalence.
- **FR-026**: Select each candidate's threshold by maximizing validation positive-class F1 over its distinct validation scores; ties choose higher precision, then the higher threshold. Freeze the selected model and threshold before any authorized test evaluation. There is no universal 0.5 default and no daily alert cap. Report actual alert counts by UTC day; permit zero or more than 20 alerts.
- **FR-027**: Evaluation reports Average Precision, ROC AUC, Precision/Recall@20/50/100, PR curve data, Brier score (uncalibrated unless calibrated), confusion matrix at selected threshold, FP/FN counts, prevalence, denominators and daily alert counts. Accuracy, if shown, carries a rare-positive caveat. No metric value may be fabricated.
- **FR-028**: Test evaluation requires an explicit separate authorization after predictions are frozen. Until then, only authorized train/validation development results may be shown; the UI MUST NOT imply test performance.
- **FR-029**: Explanations MUST state observed transaction facts and defensible feature values/contributions only. Feature contribution is not causation or proof of laundering. Do not generate SHAP or other explanations unless the chosen model/method supports them and they are actually computed.

### Backend and frontend

- **FR-030**: Model loading MUST be local, explicit, version-compatible and fail closed. No download, training, or artifact execution from untrusted sources at startup. Missing/incompatible artifacts MUST not break fixture mode.
- **FR-031**: Add versioned, validated read-only contracts for eligible transaction assessment and permitted aggregate model results. Prediction identity MUST match the requested transaction. Out-of-range/nonfinite values and malformed model outputs MUST become controlled errors, never zero-risk assessments.
- **FR-032**: Keep existing foundation endpoints and payloads backward compatible. Adapt model scoring behind the existing replaceable Python `Scorer`; preserve explicit source (`fixture`, `rules`, `model`) and provenance distinction.
- **FR-033**: Frontend MUST validate all external JSON as `unknown`, show AML risk score and a non-final review status, identify synthetic data/model/version/feature version, and render loading, empty, ineligible, unavailable, invalid, and retry states. Do not render target labels or transaction-level ground truth.
- **FR-034**: Prediction/results endpoints MUST never expose record-level training, test, or showcase labels or unauthorized metric subsets. Authorization here is the explicit local workflow gate; the MVP does not claim user authentication.

### EDA and showcase

- **FR-035**: Provide a separate EDA route/page with source/version overview, UTC coverage, row and quality counts, bank/currency/payment-format distributions, and bounded time/count/amount distributions. Amount summaries are separated by currency and state units/denominators.
- **FR-036**: EDA aggregation MUST run in Python and return bounded precomputed summaries. Browser MUST NOT fetch or process full CSV, record-level labels, or individual transactions. Public EDA excludes target labels and label-derived rates; label audit remains restricted.
- **FR-037**: Charts MUST have accessible labels, units, denominators, and empty/unavailable/loading/malformed/retry states. Avoid a new visualization dependency unless documented need and compatibility justify it.
- **FR-038**: The requested dedicated EDA page adds UI scope beyond the constitution's four-screen MVP. Specify it, but mark implementation conditional on recorded team approval including benefit and schedule impact; do not claim approval exists.
- **FR-039**: The future showcase replays chronologically using the frozen model/threshold and strict historical features, without ground truth and without daily suppression. Preload the immediately preceding 24 hours of development facts as context. Original warm-up remains unscored. Replay is deferred and not a prerequisite to initial data, prediction, or EDA delivery.

## Success Criteria

- **SC-001**: A second contributor can reproduce the manifest and processed hashes from the same source/version/configuration, with source/accepted/rejected/warm-up/scoreable counts reconciling exactly.
- **SC-002**: Synthetic temporal tests cover lower/upper 24-hour boundaries, same-instant exclusion, UTC-equivalent spellings, warm-up boundary, stable identity, and timestamp-group split invariants with exact expected results.
- **SC-003**: Before any model fit, protocol and partition hashes validate; any mismatch or insufficient-positive audit blocks fitting.
- **SC-004**: Every generated prediction has a matching transaction ID, finite bounded score, model/feature version, eligibility, and source; invalid artifacts/outputs produce controlled unavailable/error states.
- **SC-005**: No public API or UI response contains raw target labels or record-level ground truth; negative access tests demonstrate rejection.
- **SC-006**: Existing fixture application setup and behavior remain possible without dataset/model files; compatibility checks confirm existing contracts.
- **SC-007**: EDA responses are pre-aggregated and bounded; monetary charts never mix currencies and all counts/percentages state denominators.
- **SC-008**: Actual execution evidence separates synthetic tests, source verification, authorized development, separately authorized test evaluation, frontend integration and human review; no unsupported model-quality claim is made.

## Edge Cases

Duplicate/missing headers; either duplicate `Account` mapping changed; identifier whitespace/leading zeros; invalid bank/account; unknown category; invalid/nonfinite/negative amount; invalid/missing timestamp; equivalent offset instants; timestamp ties crossing prospective boundaries; boundary exactly 24 hours; interruption, disk exhaustion, checksum/count/protocol mismatch; no positive examples or prevalence outside tolerance; unknown model category; missing/incompatible/tampered artifact; identity mismatch; NaN/inf/out-of-range score; fixture startup with absent files; unauthorized record-label or showcase subrange request; currency-mixed aggregation; empty/unavailable EDA; and more than 20 daily alerts without suppression.

## Dependencies and Assumptions

- Feature 001 foundation: Python 3.14/FastAPI/Pydantic, fixture `Scorer` protocol, closed API validation, vanilla TypeScript/Vite and safe display patterns.
- Dataset source and licensing terms must be verified at acquisition; repository license does not establish data license.
- Naive timestamps are provisionally treated as UTC only after verification; a contrary source statement blocks the pipeline until decided.
- Local educational, single-user workflow; no authentication or secure multi-user hosting claim.
- Feature admission, threshold objective and fit resource ceilings are recorded in [T221 choices](t221-model-choices.json). Full-source feature-generation ceilings, serialization format, implementation dependency versions and EDA schedule impact remain unresolved before their affected implementation; the complete FR-021 protocol still needs approval before fitting.
- The proposed +10% relative validation AP feature-admission margin and EDA page require team approval before those experiments/UI implementation.
