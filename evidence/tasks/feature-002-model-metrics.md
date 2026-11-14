# Feature 002 T030–T036 development and controlled metrics — 2026-11-14

Original request: [Phase 5 T029–T036](../../prompts/development/002-phase-5-t029-t036-2026-11-14.md). Branch `model-implementations`, review base `fb32b8c8467bb5cffe6b4cbc57730b484af1b1db`; tracked tree experiment unchanged. [Real protocol and exposure audit](feature-002-protocol.md#t029-real-history-v1-freeze--2026-11-14) precedes the successful fits. This is an **exploratory development model** on synthetic IBM AML records. The previous notebook's test results overlap the new test period; independent performance is not claimed. T062 actual held-out metric comparison remains after artifact/explanation safety.

## RED and controlled GREEN

`backend/tests/unit/test_model_selection.py` initially produced 4/4 intended RED failures at missing `fit_candidate_grid`, `select_candidate` and `select_threshold` (exit 1), then passed, expanded to 5 tests. Controlled cases exercise train-only median, scaler mean, categorical vocabulary and unknown category; supervised fit receiving train rows only; explicit failed-candidate state; finite AP/P@K selection and grid-order tie; inclusive whole-score threshold ties, no-alert and invalid input. `backend/tests/unit/test_evaluation_metrics.py` produced 4/4 intended missing-interface failures (exit 1), then passed, expanded to 5 tests. They hand-check non-interpolated AP, exact K/Recall@K, stable-ID crossing-K disclosure, confusion, prevalence, alert rate, zero alerts, Brier only for probabilities, insufficient class/invalid label, identical scorer identities, account-coverage counts and atomic holdout reuse. `backend/tests/integration/test_evaluation_pipeline.py` initially had 3/3 intended command-contract RED failures (exit 1), then 6 controlled cases pass (exit 0): missing source, exact controlled source, changed protocol rejection, ineligible source, selected/failed candidate and identity rejection before label access, report hash, first disclosure and exploratory reuse. The controlled samples are not real IBM model metrics.

The local runner uses all 11 ordered `history-v1` features. Numeric train columns use median imputation then standard scaling; current paid currency and optional payment format use train-fitted one-hot with ignored unknown categories. Each candidate fits the complete preparation and supervised model on the reduced train view only; validation predicts without fitting. Class weight is balanced, as frozen before the successful run. Six fixed candidates ran serially with seed 42 and no calibration. The source query stopped at the frozen validation boundary; test rows and test labels were not read by the fit runner. All original history snapshots remain in the source database.

## Actual validation run

Command (exit **0**):

```text
PYTHONPATH=backend/src .venv/bin/python -m fraudlens.train_phase5 --store data/processed/feature-002-ibm-v8-rules-work.sqlite --protocol evals/protocols/feature_002_v1.json --out artifacts/feature-002-history-v1-20261114
```

The prospectively amended train view has **693,230 rows / 719 positive / 692,511 negative**, from the full **2,774,357** train partition by label-free ID hash; validation remains **594,715 / 588 positive / 594,127 negative**. Full test remains **594,352 / 1,445 positive / 592,907 negative** and was not scored. The first full-train attempt failed at the frozen resource ceiling before any selection metric; its precise exceeded measurement was not logged. The amendment and exact hash are in the protocol evidence.

| Grid index | Candidate | Validation AP | Validation P@20 | Fit + validation seconds | Process peak RSS bytes |
|---:|---|---:|---:|---:|---:|
| 0 | L2 logistic C=0.1 | 0.0083995254 | 0 | 3.019 | 2,647,916,544 |
| 1 | L2 logistic C=1.0 | 0.0084249375 | 0 | 3.119 | 2,690,007,040 |
| 2 | Tree depth=3, leaf=100 | 0.0105671775 | 0 | 2.417 | 2,740,830,208 |
| 3 | Tree depth=3, leaf=500 | 0.0105671775 | 0 | 2.399 | 2,788,311,040 |
| 4 | Tree depth=5, leaf=100 | 0.0142209856 | 0 | 2.841 | 2,838,167,552 |
| 5 | Tree depth=5, leaf=500 | **0.0143070042** | 0 | 2.847 | 2,885,632,000 |

Index 5 wins by validation AP. The validation-only inclusive distinct-score F0.5 policy with at most 20 alerts selected symbolic **`no_alert`** for both the winner and `rules-v1`; zero validation alerts and F0.5=0 are honest outcomes. The combined runner took **94.885 seconds**, with final `ru_maxrss` **2,889,678,848 bytes**, below 3 GiB. Scratch peak was not measured. The selected pipeline, transform and schema metadata are in ignored local [metadata](/Users/ladylazarus/Desktop/capstone-FraudLensAI/artifacts/feature-002-history-v1-20261114/metadata.json) and [model](/Users/ladylazarus/Desktop/capstone-FraudLensAI/artifacts/feature-002-history-v1-20261114/model.joblib), **7.3 KB**, SHA-256 `fd2332d543941886eb7d0092d7a606b683d1d7c198e3763865ebc7b6a2df0838`. A reload of the just-created local file reproduced five validation predictions within absolute 1e-12. A **separate Python process** then checked the file SHA-256, selected the first actual validation snapshot read-only, reloaded the local pipeline and returned probability **0.862565385475588**, exactly matching the stored first probe (exit 0). This is not the notebook's `model.joblib` and not the future trusted application loader; T037/T038 must add pre-deserialization artifact trust checks.

The CLI `freeze-protocol` real read-only run passed, exit 0, with protocol SHA-256 `01fff67d44895b5a1aa6de6dfbb6c6c107f01c041ba7c972bf42210e2b316068`. The `evaluate` CLI was run only through controlled synthetic tests; it enforces frozen protocol hash, selected candidate, exact shared scorer IDs and optional test-ID stream digest before opening labels, records an atomic local disclosure state, computes hand-checked metrics and writes a report hash. It has not joined real test labels or produced the T062 benchmark. Previous notebook test exposure means any later same-source report remains exploratory even on its first local CLI disclosure.

## Verification and limits

| Check | Exit | Observed |
|---|---:|---|
| `PYTHONPATH=backend/src .venv/bin/python -m pytest backend/tests/unit/test_evaluation_protocol.py backend/tests/unit/test_ibm_aml_trees_experiment.py -q -p no:cacheprovider --basetemp .cache/pytest-phase5-target --tb=short` | 0 | 34 passed; one host core-count warning. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest backend/tests/unit/test_pretrained_loader.py backend/tests/unit/test_pretrained_ibm_inference.py -q -p no:cacheprovider --basetemp .cache/pytest-pretrained-known-red --tb=no` | 1 | **66 known missing-pretrained-interface failures, 4 passes**. Separate, incompatible pretrained proposal; no new regression inferred. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest backend/tests --ignore=backend/tests/unit/test_pretrained_loader.py --ignore=backend/tests/unit/test_pretrained_ibm_inference.py -q -p no:cacheprovider --basetemp .cache/pytest-phase5-regression --tb=short` | 0 | **621 passed** before the final controlled test additions. |
| Same command with `--basetemp .cache/pytest-phase5-final` after cleanup | 0 | **626 passed**, two warnings (existing Starlette/httpx and host core-count). |
| `.venv/bin/ruff check backend` | 0 | All checks passed after source/test cleanup. |
| `git diff --check` | 0 | No whitespace errors. |

The selected validation AP is low and P@20 is zero. There is no favorable-outcome requirement or bank-loss/production claim. No real test predictions, test metric comparison, calibration, uncertainty interval, independent team reproduction, push, merge or T037 work has occurred. The source SQLite was opened read-only throughout these checks; raw CSV, original notebook experiment and prior evidence were retained.

After the successful model artifact was created, the candidate helper gained explicit failure-state reporting and the CLI gained early selected-candidate/ID checks. These changes do not alter the successful candidate's transform or estimator parameters. The full IBM fit was not repeated after this controlled-path cleanup; final controlled and backend checks cover the current source.

## Additional frozen-validation ranking diagnostic — 2026-11-14

[Original request](../../prompts/development/002-validation-ranking-diagnostic-2026-11-14.md). Shared branch `model-implementations`, unchanged HEAD `fb32b8c8467bb5cffe6b4cbc57730b484af1b1db`; all pre-existing uncommitted work was preserved. This is **validation-only diagnosis**, not reselection or a new benchmark. No fit, test prediction/label access, source mutation, threshold change, commit or push occurred. The old 60/20/20 notebook had already exposed 421,212 of the frozen validation rows as its test rows, which further limits independent claims.

Inventory: `find artifacts evals -type f | sort` (exit 0) found only the selected candidate's local `model.joblib`, `metadata.json` and trusted `manifest.json`; no saved per-row validation predictions or pipelines for candidates 0–4. Their metadata contains previously computed AP/P@20, but cannot establish top-50/100 counts or tie groups. They are marked unavailable, with no refit. `shasum -a 256` (exit 0) verified protocol `01fff67d44895b5a1aa6de6dfbb6c6c107f01c041ba7c972bf42210e2b316068`, manifest `2732691cb08daafba9d303ef6f3c8f616e03b3dc51505d3abb9772ceadd3919e`, metadata `8b5a513f0346b31b4c7ff60143078567f63e041f9d86d59388b7057f00f398e2` and model `fd2332d543941886eb7d0092d7a606b683d1d7c198e3763865ebc7b6a2df0838`.

Read-only diagnostic command (exit **0**):

```sh
PYTHONPATH=backend/src .venv/bin/python backend/tests/validation_ranking_diagnostic.py --store data/processed/feature-002-ibm-v8-rules-work.sqlite --protocol evals/protocols/feature_002_v1.json --artifact-dir artifacts/feature-002-history-v1-20261114 --manifest-sha 2732691cb08daafba9d303ef6f3c8f616e03b3dc51505d3abb9772ceadd3919e --output evals/results/validation-ranking-20261114.json
```

The script verifies complete DatasetVersion/build, trusted local artifact, feature order and frozen thresholds, then scores the exact `event_time > train_end AND event_time <= validation_end` `scoreable=1` population in batches of 10,000. It verifies **594,715** ordered IDs against frozen SHA `e0f845095364e061ea505678530713a13c474a3f49fb1a981e53b6ad74e2be8c` before joining validation labels. Labels matched those IDs: **588 positive**, prevalence **0.0009887088773614253** (0.0988709%). Both scorers used the same rows. Ranking is descending score then ascending transaction ID; labels do not affect order. Selected-tree AP reproduced the saved T032 value exactly, and the T032 `select_threshold` function reproduced both frozen `no_alert` choices. Output is ignored locally at `evals/results/validation-ranking-20261114.json`, SHA-256 `8520b79e5ce4a95c83042ad4944b899ed0724246a6403d0057d582b85b0f4ef0`.

| Scorer | AP | Positive top 20 | Top 50 | Top 100 | Highest score | Rows at highest score |
|---|---:|---:|---:|---:|---:|---:|
| Frozen tree depth 5 / leaf 500 | 0.0143070042 | 0 | 0 | 1 | 0.9574739569 | 18,909 |
| R1–R3 rules | 0.0007610525 | 0 | 0 | 0 | 1.0 | 39,095 |
| Logistic L2 C=0.1 | 0.0083995254 saved | 0 saved | unavailable | unavailable | unavailable | unavailable |
| Logistic L2 C=1.0 | 0.0084249375 saved | 0 saved | unavailable | unavailable | unavailable | unavailable |
| Tree depth 3 / leaf 100 | 0.0105671775 saved | 0 saved | unavailable | unavailable | unavailable | unavailable |
| Tree depth 3 / leaf 500 | 0.0105671775 saved | 0 saved | unavailable | unavailable | unavailable | unavailable |
| Tree depth 5 / leaf 100 | 0.0142209856 saved | 0 saved | unavailable | unavailable | unavailable | unavailable |

All five unavailable candidates had saved P@20=0 in T032, so none was observed to improve the first 20 at the time of training. Their top-50/100 and tie composition cannot be reconstructed from aggregate metadata. The selected tree's top-100 has one positive, but the first 20/50 have zero.

| Scorer | Score at rank 20 | Rows above tie | Rows in tie | Positives in tie | Tie rows selected in top 20 | Positives among selected tie rows | Crosses rank 20? |
|---|---:|---:|---:|---:|---:|---:|---|
| Frozen tree | 0.9574739569 | 0 | 18,909 | 333 | 20 | 0 | Yes |
| R1–R3 | 1.0 | 0 | 39,095 | 15 | 20 | 0 | Yes |

The tree's highest group has **333/18,909 = 1.76%** positive, about 17.8 times the overall validation prevalence, yet all 18,909 share one score. ID order is deterministic but carries no claimed risk signal. The rules' highest group has 15/39,095 = 0.0384% positive, below overall prevalence. The tree has some broad enrichment; neither available scorer distinguishes the first 20 well under the declared tie order.

T032 policy considers inclusive thresholds at distinct scores, preserves complete ties and permits at most 20 alerts. The **highest** possible inclusive threshold already emits **18,909 tree** or **39,095 rules** alerts. No threshold yields 1–20 alerts for either scorer. Thus there is no feasible nonempty F0.5 candidate; symbolic `no_alert` with F0.5=0 wins and produces **zero actual validation alerts**. The top-20 table is a capacity ranking diagnostic, not the published alert list. No threshold, winner or protocol was changed.

Recommended next experiment: predeclare and evaluate a **tie-aware capacity policy on validation only** that uses the existing tree score and a deterministic, operational secondary rank within its highest-score group, with a hard 20-alert limit. Compare its precision and stability with the current ID tie order before any separate future holdout design. Merely lowering an inclusive score threshold would violate the frozen alert budget; a bare ID-based top-20 override currently has zero positives. This is a proposal for a later scope decision, not a change to the frozen model or benchmark. The absence of candidate 0–4 per-row predictions/artifacts prevents a fresh comparison of their top-50/100 and tie groups without retraining, which this request forbids.

Verification: `.venv/bin/ruff check backend/tests/validation_ranking_diagnostic.py` exit 0; a controlled four-row ranking/threshold check initially exposed an edge case for fewer than 20 rows (exit 1), then passed after using `min(20,n)` (exit 0). The real frozen validation population has more than 20 rows, so that cleanup does not change the reported measurements. `git diff --check` is recorded with the final handoff.

After that cleanup, the same diagnostic command was repeated with `--output evals/results/validation-ranking-20261114-rerun.json` (exit 0); it again reported 594,715/588 and identical scorer results. `cmp evals/results/validation-ranking-20261114.json evals/results/validation-ranking-20261114-rerun.json` exited 0: output bytes are identical. Final Ruff and `git diff --check` both exited 0.

## Predeclared validation review-queue experiment — before outcome calculation

[Original prompt](../../prompts/development/002-validation-review-queue-2026-11-14.md). Shared `model-implementations` HEAD `fb32b8c8467bb5cffe6b4cbc57730b484af1b1db`; existing uncommitted work is preserved. This section was written before running the new outcome calculation. Scope is the frozen, eligible validation partition only, with the same 594,715 ordered IDs for the selected tree and R1–R3. No candidate, threshold, model or protocol selection occurs.

Exactly one new ranking rule is fixed here: sort by each scorer's existing score descending. For equal scores, available `current_paid_amount / (sender_paid_sum_same_currency_24h / sender_paid_count_same_currency_24h)` ranks before unavailable; calculate only when the sender's prior same-currency count is at least 3 and its prior same-currency sum is strictly positive. Compare the rational values exactly by integer/Decimal arithmetic, descending, with no rounding. The history-v1 prior window is `[t−24h,t)` and excludes the current/future events. Remaining ties use transaction ID ascending. Select the first 20. Compare against existing score-descending, ID-ascending order. Do not consult validation labels until all four ordered lists are fixed and persisted. The same four ordered lists must repeat identically in a second read-only run. No other variant will be tried after seeing results.

The queue is **research only** and is separate from the frozen inclusive-threshold `no_alert` policy and published benchmark. Earlier notebook exposure includes part of this validation period; results cannot be interpreted as independent confirmation. Outcome commands/results follow below after execution.

### Executed outcome and repeat

The frozen inputs retained their prior identities: protocol SHA-256 `01fff67d44895b5a1aa6de6dfbb6c6c107f01c041ba7c972bf42210e2b316068`, trusted manifest `2732691cb08daafba9d303ef6f3c8f616e03b3dc51505d3abb9772ceadd3919e`, model `fd2332d543941886eb7d0092d7a606b683d1d7c198e3763865ebc7b6a2df0838`. The existing script was extended with the single predeclared rule and a `--selection-output` file. `_ratio` uses `Fraction(Decimal(...))` so comparison does not round; history-v1's existing same-currency count/sum have the documented `[t−24h,t)` strict-past semantics. `_queue_order` has no label argument. The script opens SQLite with `mode=ro` and `query_only=ON`, checks the frozen **594,715 validation IDs** against SHA `e0f845095364e061ea505678530713a13c474a3f49fb1a981e53b6ad74e2be8c`, computes both scorers and four ordered lists, writes the selection file with exclusive creation, and **only then** queries validation labels. Selection file modification time was `2026-11-14T14:21:50+0100`, result file time `2026-11-14T14:22:06+0100`; code order is the stronger guarantee.

First command, exit **0**:

```sh
PYTHONPATH=backend/src .venv/bin/python backend/tests/validation_ranking_diagnostic.py --store data/processed/feature-002-ibm-v8-rules-work.sqlite --protocol evals/protocols/feature_002_v1.json --artifact-dir artifacts/feature-002-history-v1-20261114 --manifest-sha 2732691cb08daafba9d303ef6f3c8f616e03b3dc51505d3abb9772ceadd3919e --selection-output evals/results/validation-review-queue-selection-20261114.json --output evals/results/validation-review-queue-result-20261114.json
```

Same command with `-repeat.json` appended to both output basenames: exit **0**. `cmp` on original/repeat selection files and on original/repeat result files: both exit **0**, byte-identical, including the same 20 IDs in the same order for each queue. Selection SHA-256 `b5495080ab0318bfd430fb80e7123bbf1d8a5ea92845b16a8ed4c6397920a7ba`; result SHA-256 `4da9c88a05d139b77687eeb9caa30b2e2406dda41b4f39960bcb71f3bf56cdff`. Both large-detail files are ignored under `evals/results/`.

| Scorer and tie order | Selected | Positive | Precision@20 | Recall@20 | Selected with available ratio |
|---|---:|---:|---:|---:|---:|
| Frozen tree; old score then ID | 20 | 0 | 0 | 0 | 0 |
| Frozen tree; new exact ratio then ID | 20 | 0 | 0 | 0 | 0 |
| R1–R3; old score then ID | 20 | 0 | 0 | 0 | 20 |
| R1–R3; new exact ratio then ID | 20 | 0 | 0 | 0 | 20 |

The old order reproduced the earlier zero-positive top 20 for both scorers. The tree's new queue is **identical** to its old queue (ordered-ID SHA `cf0686cb6292defc2259fb5056df5ffbe3682bd87970b763d285349586cd76e4`); none of its 20 selected rows had an available ratio. Because rank 20 lies in the tree's highest-score tie, an available ratio anywhere in that highest-score group would have preceded these unavailable rows; this result indicates the proposed ratio cannot distinguish that group. The rules queue **changed** order (old ordered-ID SHA `5aae2d9233fee8f87e5acf6d1adea81a66cc918a73431158743b1025a89dc8a5`, new `fd018dccea91ebf4215063851e6d2c8b074d847f59157e4725ac40af86e051ae`), but still selected zero positives.

Answers: **No**, the new order found no more positives than old ID order for either scorer. **No**, the tree found no more positives than R1–R3 with the same new secondary rule at 20 reviews; both found zero. This does not change the frozen `no_alert` policy, whose actual alert count remains zero. These 20-row queues are experimental review lists only. This single variant was prescribed before outcomes; no alternative feature, minimum count, rounding or capacity was tried after seeing results. Prior validation exposure and absence of an untouched confirmation set prohibit a performance claim.

Verification sequence: initial direct-import test invocation exited 2 at missing `_queue_order` import; corrected RED invocation collected **3 intended missing-interface failures** (exit 1). After implementation, `PYTHONPATH=.:backend/src .venv/bin/python -m pytest backend/tests/unit/test_review_queue.py -q --tb=short` exited 0 with 3 passed. Final targeted `pytest backend/tests/unit/test_review_queue.py backend/tests/unit/test_model_selection.py backend/tests/unit/test_evaluation_metrics.py -q --tb=short` exited 0 with **13 passed**. `.venv/bin/ruff check backend/tests/validation_ranking_diagnostic.py backend/tests/unit/test_review_queue.py` and `git diff --check` exited 0. Full backend regression was not rerun for this bounded diagnostic.

An additional controlled input-permutation assertion was added after the real run to verify raw row order cannot affect the declared sort. Final `PYTHONPATH=.:backend/src .venv/bin/python -m pytest backend/tests/unit/test_review_queue.py backend/tests/unit/test_model_selection.py backend/tests/unit/test_evaluation_metrics.py backend/tests/unit/test_feature_history.py -q --tb=short` exited 0 with **28 passed**; final Ruff and `git diff --check` exited 0. This assertion changed no selection code or measured output.
