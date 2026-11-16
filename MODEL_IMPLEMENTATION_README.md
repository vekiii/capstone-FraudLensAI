# FraudLens AI model implementation

The main **local** Feature 002 model path is the pinned `HistGradientBoosting` scorer, `model-history-v1-boosted-candidate`. It was fitted, checked on development validation and exercised through an isolated full application run. The frozen decision tree remains the shared active run and the original benchmark/T066 comparison path until the outstanding gates are met. The boosted model is not an independently confirmed prospective result. See the [quickstart](specs/002-data-and-risk-scoring/quickstart.md#main-local-model-path-histgradientboosting) for required same-hash local inputs, scoring, activation and API commands.

The contributor's local completed v3 run can be inspected without repeating scoring: `run_boosted_full_20261114_v3` in ignored `evals/results/boosted-full-20261114-v3.sqlite` contains 3,963,424 scored transactions and 166 threshold alerts. For a new checkout, transfer the reviewed boosted artifact and complete source/history SQLite through the authorized team channel, verify all hashes **before** deserialization, then use a fresh isolated run store and ID. Missing source, protocol or artifact files and mismatched manifest bytes now have specific CLI errors. The shared active run must not be changed by this workflow.

For local operation with a daily review capacity of 20, the [versioned `boosted_utc_daily_top20_v1` policy](specs/002-data-and-risk-scoring/contracts/data-and-scoring.md) derives a **new isolated completed run** from a same-hash completed boosted score archive. It preserves all 3,963,424 assessments and their numerical scores/explanations, records source-store hash and source run ID, and publishes only the top 20 scores per UTC date, breaking ties by transaction ID. The original v3 remains the 166-alert reference. The derived run has 159 published cases and records 166 threshold-eligible and seven excluded by capacity; the API list and detail use the same selected snapshot. The [quickstart](specs/002-data-and-risk-scoring/quickstart.md#isolated-daily-top-20-publication-from-verified-scores) gives the exact derivation, activation and browser commands. This is a technical local policy result; the team's independent-period and shared-activation decisions remain open.

## Source and data flow

The source is the IBM AML `HI-Small_Trans.csv` transaction table, recorded as 5,078,345 transactions with source SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`. The imported dataset version is `dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802`. Import and feature building store normalized transactions, private evaluation labels, and `history-v1` snapshots in a local SQLite database. The historical feature replay uses the project's approved mapping and time policy; the source timestamps themselves do not establish a source timezone. See the [source audit](evidence/tasks/feature-002-source-audit.md), [import implementation](backend/src/fraudlens/data_import.py), and [feature builder](backend/src/fraudlens/feature_history.py).

Snapshots use a preceding 24-hour window with a full day of warm-up. At a given event timestamp, transactions at that same timestamp are excluded from one another's history; the current event is added only after its snapshot is emitted. Incomplete history is not scored. Of 5,078,345 snapshots, 1,114,921 were warm-up/unscoreable and **3,963,424 were scoreable** in the recorded full run. The full-run source SQLite is a local, ignored artifact, not part of Git.

The [frozen evaluation protocol](evals/protocols/feature_002_v1.json) specifies a chronological 70/15/15 split by complete timestamp groups:

| Partition | Scoreable rows | Positive AML labels | Period in the recorded protocol | Use |
|---|---:|---:|---|---|
| Train | 2,774,357 | 2,822 | 2 Sep 2022 00:00 through 8 Sep 07:21 UTC | Fit preprocessing and candidate models |
| Validation | 594,715 | 588 | 8 Sep 07:22 through 9 Sep 09:31 UTC | Select and compare candidates/thresholds |
| Test | 594,352 | 1,445 | 9 Sep 09:32 through 18 Sep 16:18 UTC | Frozen-tree exploratory benchmark only |

For the recorded fits, the protocol selects a **label-free quarter of train IDs**: the first eight bytes of `SHA256(transaction_id)`, interpreted as an unsigned big-endian integer, modulo 4 equals 0. This yielded **693,230 training rows with 719 positives**. All earlier transactions still contribute to history features. Validation and test membership are unchanged. The train reduction followed an earlier full-train resource-ceiling failure and is recorded in the [protocol evidence](evidence/tasks/feature-002-protocol.md). Private labels are used offline for training/evaluation, never as model inputs or application scoring features.

### Ordered model inputs

The [training loader](backend/src/fraudlens/train_phase5.py) and [feature catalog](backend/src/fraudlens/feature_history.py) define exactly **11 ordered features**:

| Feature | Meaning |
|---|---|
| `sender_out_count_24h` | Sender's outgoing transaction count in prior 24 hours |
| `sender_distinct_receivers_24h` | Distinct bank-qualified receivers for that sender |
| `sender_paid_count_same_currency_24h` | Sender's prior paid count in the current paid currency |
| `sender_paid_sum_same_currency_24h` | Sender's prior paid sum in the current paid currency |
| `receiver_in_count_24h` | Receiver's incoming transaction count in prior 24 hours |
| `receiver_distinct_senders_24h` | Distinct bank-qualified senders for that receiver |
| `receiver_received_count_same_currency_24h` | Receiver's prior received count in the current received currency |
| `receiver_received_sum_same_currency_24h` | Receiver's prior received sum in the current received currency |
| `current_paid_amount` | Current transaction's paid amount, in its paid currency |
| `current_paid_currency` | Current paid-currency category |
| `current_payment_format` | Current payment-format category |

The first nine are numeric and the last two are categorical. Money features retain their named currency; the model does not convert them to a common currency. The learned preprocessing is fit on train only: median imputation and standard scaling for numeric columns, one-hot encoding with unknown categories ignored for categorical columns. The boosted pipeline requests dense transformed output. The score is the pipeline's positive-class `predict_proba` output and is published as an **uncalibrated probability estimate**, not an established real-world AML probability.

## Models and fit settings

| Path | Training and selection | Parameters and identity |
|---|---|---|
| Rules reference | Deterministic R1–R3 score, with no learned fit | [Rule logic](backend/src/fraudlens/train_phase5.py) and [rule scorer](backend/src/fraudlens/rule_scoring.py) |
| Shared frozen model | Six prespecified logistic/tree candidates fitted serially on reduced train; selected on full validation by average precision, then precision@20 and grid order for ties | Winner: `DecisionTreeClassifier(max_depth=5, min_samples_leaf=500, class_weight='balanced', random_state=42)`; scorer version `model-history-v1`; [fit and selection code](backend/src/fraudlens/evaluation.py) |
| Boosted research candidate | One declared fit with the same rows, ordered inputs and learned preprocessing; compared on already inspected validation. A second same-recipe fit produced the saved candidate artifact | `HistGradientBoostingClassifier(max_iter=150, max_leaf_nodes=15, min_samples_leaf=100, learning_rate=0.1, class_weight='balanced', early_stopping=False, random_state=42)` with two threadpool threads; scorer version `model-history-v1-boosted-candidate`; [fit runner](backend/src/fraudlens/compare_boosted_phase5.py) |

Both model pipelines are serialized as local `model.joblib` with `metadata.json` and `manifest.json`. The boosted artifact also saves `validation_scores.npy`. The [trusted loader](backend/src/fraudlens/model_scoring.py) checks the expected manifest hash, model and metadata hashes, dataset/protocol/feature/scorer versions, ordered features, dependency versions and model class before loading the local binary; it rejects uploaded artifacts. This is a local provenance gate, not permission to load unreviewed joblib files. The recorded boosted manifest SHA-256 is `013c7ebe5ab5a5270a7b66af200060d3499c31eb2598c06a038ca887fd9320a6`; the ignored path is `artifacts/feature-002-boosted-validation-20261114/`. The recorded fit used Python 3.14.7, NumPy 2.5.4, scikit-learn 1.9.1 and joblib 1.6.0. See the [boosted validation record](evidence/tasks/feature-002-boosted-validation.md) for complete artifact digests, commands and resource measurements.

## Recorded evaluation results

On the **594,715-row validation partition**, using descending score and ascending transaction ID to break ranking ties:

| Scorer | Average precision | Positives in top 20 | Precision@20 | Validation alert threshold | Simulated alerts / positives |
|---|---:|---:|---:|---|---:|
| R1–R3 rules | 0.0007610525 | 0 | 0 | `no_alert` | 0 / 0 |
| Refit/frozen tree | 0.0143070042 | 0 | 0 | `no_alert` | 0 / 0 |
| HistGradientBoosting candidate | **0.1721290265** | **19** | **0.95** | **0.9936687168275105** | **20 / 19** |

The boosted threshold was chosen on validation with the existing inclusive, whole-score-tie, at-most-20-alert F0.5 policy. Its rank-20 score had no boundary tie. The refit tree's validation scores matched the frozen tree exactly. After the second boosted fit was saved, a separate process reloaded it and reproduced all 594,715 saved validation scores exactly, including AP and 19/20. These are **development validation findings**, not a newly held-out test result. The old notebook's 60/20/20 test period had already exposed 421,212 rows of this validation set. The **95%** figure means 19 labeled positives among the 20 highest-ranked validation transactions; it is not the positive rate of the later 166 alerts.

The separate [frozen-tree test benchmark](evidence/tasks/feature-002-benchmark.md) scored 594,352 rows: tree AP `0.0307344403263558`, rules AP `0.0018670818306353214`, zero positives in either top 20, and zero published alerts at their frozen `no_alert` thresholds. That test period had also been exposed by the earlier notebook, so it is exploratory. The boosted candidate has **no recorded independent test metric** on a previously unseen compatible period.

## Application integration and full technical run

The [scoring CLI](backend/src/fraudlens/pipeline_cli.py) reads scoreable `history-v1` snapshots from the source store, verifies a pinned local artifact for model runs, validates each assessment against the v2 scoring contract, and writes a separate immutable run store. For boosted scoring it processes bounded batches of 128; the [model scorer](backend/src/fraudlens/model_scoring.py) batches prediction and explanation counterfactuals. A run is activated only after completion. The [FastAPI application](backend/src/fraudlens/main.py) reads an active run through `RunStore` for `/api/health`, `/api/cases`, and case detail; the frontend displays the run, score and explanation. Dataset mode is selected through application settings, while the foundation fixture mode remains separate.

The boosted explanation method is `boosted_sequential_probability`: start with train-median numeric and missing-category baseline values, introduce the 11 observed raw features in frozen order, and record each change in the positive-class estimate. The public explanation shows the three largest absolute contributions, plus a base value and remainder for omitted terms. Its full-precision components must reconstruct the saved score within `1e-8`. Contributions depend on that feature order and baseline; they are **not causal effects**. See [explanation code](backend/src/fraudlens/explanations.py).

Elena's [completed isolated full-run evidence](evidence/tasks/feature-002-boosted-validation.md#completed-v3-result-and-isolated-application-check) records `run_boosted_full_20261114_v3` as `completed`: **3,963,424 scoreable assessments and 166 alerts** at the frozen boosted threshold. The 1,114,921 warm-up snapshots were excluded. This run used the original local source, but its alert labels were **not measured**; no 166-alert precision or recall is known. The run was activated only in its own ignored run store. The shared active model run remained the frozen tree with `no_alert` and zero alerts.

The v3 isolated API returned 166 total alerts, 100 shown by its bounded list response, and 100 checked details with saved-score/explanation reconstruction. A browser list/detail check displayed the boosted scorer, score and explanation. A partial alert-list index was added after the first full-store list query was too slow. The full run is an **end-to-end technical check**, not independent model acceptance. On two complete UTC days the fixed threshold generated **24 alerts on 2 September and 23 on 9 September**, above the team's 20-review daily capacity. The separately versioned local top-20 policy publishes 20 on each of those days and remains subject to team review before shared activation.

## Current status and what remains

- **Implemented:** history features, frozen tree/rule evaluation, separate boosted fitting and trusted local artifact path, explanation generation, batch full-run scoring, isolated run publication, API and browser display.
- **Measured on development validation:** boosted AP `0.1721290265`, 19 positive in top 20, 20 simulated alerts with 19 positive. **Measured on full source without labels:** 3,963,424 scores and 166 alerts. These numbers answer different questions.
- **Pending:** T065 teammate review of five boosted explanations, T066 second-person reproduction, team review of the implemented daily policy, and a previously unseen compatible 24-hour UTC acceptance check requiring at least five positives among at most 20 alerts. T067 final review and any decision to use the boosted model in the shared run remain open.
- **This checkout's blocker:** the original SQLite history store, boosted model/manifest, explanation JSON, frozen prediction reports and approved same-hash protocol are unavailable or mismatched locally. The Windows Python/SQLite development environment is ready for data-free work, but artifact reload, T065 fact checks and T066 reproduction cannot be claimed here. See [T065](evidence/tasks/feature-002-explanation-review.md), [T066](evidence/tasks/feature-002-peer-reproduction.md), and [environment setup](evidence/tasks/feature-002-environment-setup.md).

The source table is synthetic; its AML label indicates the dataset's money-laundering class, not proof of real-world financial crime. Human analysts retain final case decisions. No model merge, deployment, or release approval follows from the technical run or the evidence-access agreement.
