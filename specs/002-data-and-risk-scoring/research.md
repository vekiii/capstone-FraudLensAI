# Research Notes: Dataset, Machine Learning and EDA

**Status**: Desk research and design proposals only. No dataset downloaded, real labels inspected, model trained, or application dependency changed during specification work.

**Later decision:** The 2026-11-20 [T221 model-choice decision](protocol.md#t221-model-choice-decision--frozen-choices-fitting-stopped) supersedes the AP-first/F0.5 and at-most-five-candidate proposals below. The earlier research text is retained as its original design rationale.

## Dataset, provenance and license

IBM's AML-Data README states the repository is Apache-2.0 while the data itself is CDLA-Sharing-1.0, and describes the generated transactions as synthetic from a virtual-world model, not anonymized real individuals ([IBM AML-Data README](https://github.com/IBM/AML-Data/blob/main/README.md)). The NeurIPS Datasets and Benchmarks paper describes six AML datasets with different sizes/illicit ratios and reports public synthetic statistics ([paper](https://papers.nips.cc/paper_files/paper/2023/file/5f38404edff6f3f642d6fa5892479c42-Paper-Datasets_and_Benchmarks.pdf)). Published figures do not replace verification of the exact Kaggle file/revision acquired. Prompt figures (including checksum/record counts) remain unverified references.

**Proposal**: Data card records Kaggle dataset/revision ([HI-Small distribution](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml)) and IBM documentation, acquisition time, license text and source URL, file hash/size, exact schema/header positions, row count, quality and label audit outputs, processing revision, limitations, and reproducibility command. Verify Kaggle terms as well as IBM documentation at acquisition; do not infer data redistribution rights from repository code license.

## Large-file processing

Approximately five million rows rules out assuming a whole-file in-memory dataframe, especially after eight temporal features and high-cardinality accounts. Candidate approaches: Python CSV chunks + external merge sort; a columnar engine with streaming scan/sort; or an embedded analytical engine. Chunk CSV parsing is simple but global sorting and temporal windows require spill-to-disk coordination. Columnar formats reduce repeated parse costs but need measured disk/RSS and dependency support. DuckDB is a candidate for bounded local execution, but adds a dependency and its behavior/compatibility must be validated; it is not mandated.

**Recommendation**: benchmark a single bounded local pipeline against a deterministic synthetic workload. Use checksummed staged chunks and a Parquet snapshot if compatible. Process whole timestamp groups in a chronological pass with a rolling expiry queue/map; do not use global account aggregates that include future events. Record measured RSS, disk peak, runtime and checkpoint behavior before approving ceilings. Do not hard-code resource claims from desk research.

## Timestamp and historical windows

Source timestamp timezone and precision are unresolved until the exact documentation/file is inspected. Normalize explicit-offset values to UTC. If source values are naive and documentation does not assign a zone, make the chosen UTC assumption visible in the data card/protocol. Use `[t−24h,t)` to satisfy “strictly earlier and within preceding 24h”; lower edge included, current instant excluded. Compute each same-instant group's features before applying any member to rolling state. IDs and ordering use stable source row identity, not locale-dependent sorting.

Accounts must be keyed by exact `(bank, account)` text, avoiding global account-number assumptions and leading-zero loss. Sender sums use paid amount + payment currency; receiver sums use received amount + receiving currency. No currency conversion is proposed.

## Feature representation and categorical data

Historical counts/sums are deterministic numeric fields, zero for no history. Monetary amounts should be parsed as decimal text or integer minor units only after source precision is verified; float conversion can introduce boundary/aggregation errors. Current `Amount Paid` has cross-currency scale differences; proposed `log1p` reduces scale but does not make currencies economically comparable. Include payment currency and payment format categorically, with unknown-category handling explicitly defined. This remains a proposal pending the feature contract.

The requested +10% relative validation AP admission rule is not established evidence. It requires team approval before feature experiments and a frozen baseline/feature candidate definition; validation comparisons must be prespecified and must not affect held-out test.

## Model candidates and imbalance

The bounded experiments in the prompt fit the educational MVP: prevalence baseline, shallow decision tree, L2 logistic regression, and at most five scikit-learn `HistGradientBoosting` configurations. Use AP as primary because rare positives make accuracy uninformative; report Precision/Recall@k, ROC AUC and confusion counts with denominators. The IBM paper is domain provenance, not evidence that any proposed model performs well here.

Scikit-learn's model persistence guidance warns that pickle/joblib can execute code and that cross-version loading is unsupported; it discusses ONNX and `skops.io` tradeoffs ([model persistence guide](https://scikit-learn.org/stable/model_persistence.html)). Therefore artifact format depends on estimator support, local Python 3.14 compatibility, and locked dependency versions. Proposal: same locked train/runtime stack and an inspectable/safe format where feasible; never load untrusted artifacts. Do not claim library compatibility until checked against the repository lockfile and interpreter.

Class imbalance options are restricted to none, supported class weighting, or deterministic training-only negative downsampling. Preserve natural validation/test/showcase class prevalence. Do not assume oversampling improves temporal generalization.

## Evaluation, threshold, explainability

Select models only on validation AP, then P@20, then a written deterministic simplicity tie-break. Freeze threshold via an agreed validation objective (recommend F0.5 with tie handling declared); do not assume 0.5 or cap daily alerts. Brier score does not establish calibration on its own; label uncalibrated unless calibration is assessed. Explain selected feature values and valid model contributions only; contribution is not causality. Do not fabricate SHAP values.

Separate training/validation, frozen prediction creation, explicitly authorized test label access and future showcase. A test result is not available before separate authorization, and no test metric may influence model or threshold choices.

## Artifact and runtime boundary

Training is an explicit local command. Runtime loads only a local frozen artifact whose checksum, metadata, feature order, model version and dependency compatibility pass. Missing artifacts preserve fixture mode. Do not train/download models at app startup. Include source/protocol hashes and training code revision in metadata. Avoid unsafe generic deserialization of untrusted files.

## EDA and charts

Python computes bounded aggregates. Browser receives small typed summaries and chart series only. Proposed charts: rows by UTC date (without labels), currency-separated amount distributions, payment-format/currency counts, quality/rejection summary, and data coverage. All charts include unit, denominator and accessible text summary. Do not show target rates or individual ground truth in public EDA. Native SVG/HTML/CSS or a small accessible chart implementation is preferred unless requirements justify a new dependency.

## Source/schema uncertainty

Prompt expects duplicate `Account` headers and lists likely field names. This is a hypothesis until the exact source revision is acquired and its CSV schema inspected. Implementation must fail closed on altered order/count/header; source positional mapping must be documented in the data card and covered by a synthetic duplicate-header fixture.
