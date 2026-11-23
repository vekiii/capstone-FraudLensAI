# FraudLensAI — Align AML Dataset Splitting and Local LightGBM Training With IBM Research

## Objective

Revise the existing Feature 002 AML data preparation and model-training implementation using the methodology documented in IBM Research's published AML experiments.

**Research references:**
- https://arxiv.org/abs/2306.11586
- https://github.com/IBM/Multi-GNN
- https://github.com/IBM/Multi-GNN/blob/main/data_loading.py
- https://github.com/IBM/Multi-GNN/blob/main/format_kaggle_files.py

Relevant research: Appendix E.1, "AML Data Split", in *Provably Powerful Graph Neural Networks for Directed Multigraphs*.

**My goal:** Prepare the IBM HI-Small dataset for binary money-laundering classification, split it using a research-supported methodology, and implement a reproducible LightGBM pipeline that I will run locally on my Windows PC.

The goal is a working ML experiment, not additional approval bureaucracy.

## 1. Adopt IBM's Temporal Split

IBM uses approximately:

- 60% training
- 20% validation
- 20% testing

The split is chronological, using transaction timestamps.

The IBM implementation selects chronological day boundaries to approximate the desired proportions by transaction count.

Implement or reuse this methodology.

Requirements:

- Use the existing `HI-Small_Trans.csv`.
- Predict the binary target `Is Laundering`.
- Parse timestamps consistently and sort chronologically.
- Preserve original transaction identifiers.
- Break timestamp ties deterministically.
- Prefer complete-day cutoffs where practical, as IBM does.
- Choose cutoffs based on timestamp and transaction counts, not on labels.
- Ensure train, validation and test partitions are mutually exclusive.
- Ensure every transaction belongs to exactly one partition.
- Preserve strict chronological ordering between partitions.
- Record cutoff timestamps, partition counts, row IDs, positive counts, negative counts and prevalence.

Do not use random stratified splitting for the primary research experiment.

If the existing frozen partition already implements this methodology correctly, reuse it instead of recomputing it unnecessarily.

If the frozen partition differs materially, create a clearly versioned replacement and regenerate dependent manifests and hashes. Do not overwrite the old historical evidence.

## 2. Correct FR-018 — Remove Arbitrary Class Requirements

The existing project requires:

- At least 20 positive transactions in every partition.
- A prevalence ratio between 0.75 and 1.25.

These requirements are not part of the referenced IBM AML temporal-splitting methodology.

Revise FR-018 and all connected acceptance tests, validators, specifications, protocols and task dependencies.

New requirements:

- Do not require a fixed minimum of 20 positives in each partition.
- Do not require matching positive-class prevalence across partitions.
- Report the actual class distribution.
- Treat unusual class distributions as diagnostics, not automatic split failures.
- Never duplicate, synthesize, move or relabel transactions to satisfy class-balance targets.
- Never inspect labels to optimize the chronological cutoffs.

**Important:** Retain genuine ML validity requirements.

Training must not proceed if the training partition contains only one class.

If validation or test has no positive examples, explain that the affected positive-class evaluation metrics are undefined or uninformative. Do not fabricate a result or silently alter the split.

If the split is unsuitable for meaningful evaluation, report the limitation and suggest an explicitly documented alternative experiment.

## 3. Maintain Data-Leakage Protection

Use a realistic transaction-prediction setup.

- Fit preprocessing transformations using training data only.
- Apply those transformations to validation and test.
- Fit class weighting using training labels only.
- Use validation data for hyperparameter tuning and decision-threshold selection.
- Evaluate on test only after model selection.
- Never train on test labels.
- Never use test metrics to choose hyperparameters or thresholds.
- Do not use target-derived features or information unavailable at prediction time.

For account-history or graph-derived features, use only information available before the transaction being scored. Do not calculate features from the entire dataset and then split afterward.

IBM's GNN graph snapshots are useful methodological context, but our immediate objective is a tabular LightGBM baseline, not reimplementation of Multi-GNN.

## 4. Update FR-021 Training Protocol

Revise:

`specs/002-data-and-risk-scoring/t219-training-protocol.candidate.json`

Update the corresponding specification and implementation.

The protocol should include:

- Temporal 60/20/20 splitting methodology.
- Exact source dataset identification and hash.
- Partition identifiers and cutoff timestamps.
- Feature definitions.
- Binary classification target.
- Fixed random seed.
- LightGBM model configuration.
- Training-only class weighting.
- Training-only preprocessing.
- Validation-based model selection.
- Relevant evaluation metrics.
- Actual dependency versions and training configuration.

Record the local code revision and resource configuration for reproducibility.

Do not make CPU core count, thread count or unverified Kaggle revision metadata arbitrary blockers to basic local experimentation.

Preserve existing verified provenance. Report unknown source metadata as unknown rather than inventing it.

Do not silently approve or freeze a new protocol hash. Produce the updated candidate and provide its verification information.

## 5. Update FR-027 — Model Evaluation

Implement the following outputs:

- Confusion matrix
- Precision
- Recall
- F1 score
- Precision-recall curve data
- PR-AUC / average precision
- ROC-AUC where defined
- Actual positive-class prevalence
- Positive and negative denominators
- Selected decision threshold

Show these metrics separately for validation and test.

Handle undefined metrics correctly when a partition lacks examples of a required class.

Do not use accuracy as the primary performance measure because AML data is highly imbalanced.

If reporting Brier score, clearly state whether probabilities have been calibrated. Do not label an uncalibrated probability score as calibrated.

## 6. Prepare LightGBM for Local Windows Training

Use the existing project architecture.

Do not implement a GNN at this stage.

Implement a practical LightGBM binary classification training pipeline.

Requirements:

- Python-based training.
- Local Windows execution through VS Code.
- Reuse existing preprocessing and feature artifacts wherever valid.
- Avoid unnecessary full-dataset copies.
- Use memory-conscious data loading.
- Allow configurable CPU thread count.
- Use deterministic seeds where supported.
- Use training-only class weighting or `scale_pos_weight` to address class imbalance.
- Use validation for early stopping and model selection.
- Save the model and reproducibility metadata.
- Export prediction scores and evaluation outputs for future TypeScript web-app integration.

Do not run the full model-fitting process automatically.

I will execute training myself on my PC.

You may run lightweight tests and structural checks, but do not start expensive training jobs.

## 7. Reconcile Existing Feature 002 Artifacts

Inspect the existing work associated with:

- T203
- T210
- T219
- T228
- FR-018
- FR-021
- FR-027

Determine what already works.

Reuse valid code, source hashes, partition manifests, feature-generation logic and other artifacts.

Update obsolete acceptance criteria consistently rather than adding new compensating checks.

Preserve previous audit reports as historical records. Produce new results where necessary.

Do not replace the existing architecture with a new framework.

## 8. Required Tests

Provide lightweight tests for:

1. Correct chronological partition order.
2. No overlapping transaction IDs.
3. Complete assignment of eligible rows.
4. Deterministic splitting.
5. Accurate reported class counts and prevalence.
6. Absence of label-based split optimization.
7. Train-only preprocessing.
8. No future-information leakage in derived features.
9. Correct handling of undefined evaluation metrics.
10. Compatibility between the training scripts and prepared input artifacts.

Avoid introducing minimum-positive-count or prevalence-ratio gates.

## 9. Final Deliverables

Implement the necessary changes in the repository and then provide:

1. Files modified and why.
2. Updated FR-018, FR-021 and FR-027 requirements.
3. Actual train/validation/test transaction counts.
4. Actual positive and negative counts for every partition.
5. Exact chronological cutoff timestamps.
6. Whether the old frozen split was reused or replaced.
7. Updated protocol candidate and hash.
8. Results of lightweight verification tests.
9. Commands to install dependencies and run training locally.
10. Commands to evaluate the saved model.

The commands must match the actual implemented files. Do not invent script paths.

**Success criterion:** I have verified, leakage-safe, chronologically partitioned AML data and a working local LightGBM training and evaluation workflow.

Prioritize finishing a usable ML pipeline. Do not create new approval checkpoints beyond genuinely necessary integrity or safety checks.