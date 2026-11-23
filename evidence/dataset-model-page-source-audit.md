# Dataset and model page source audit — 2026-11-23

Scope: read-only review for `/eda` and `/data` on `feature/frontend`. No source rows, protected record-level test labels, model fit, or evaluation command were opened or run. Values below come from approved existing aggregate records and the implemented contracts. These records describe one exact local IBM HI-Small copy; the currently running fixture server may not have its EDA summary or model artifacts configured.

## Source and provenance

| Fact | Confirmed value | Authority |
| --- | --- | --- |
| Dataset | IBM Transactions for Anti-Money Laundering, `HI-Small_Trans.csv`, synthetic AML transactions; `Is Laundering` is a simulator label, not a legal finding | `original_idea.md` §3.1; `specs/002-data-and-risk-scoring/spec.md` |
| Distribution | User-reported local Kaggle download of the IBM dataset; IBM data terms identified as CDLA-Sharing-1.0 | `specs/002-data-and-risk-scoring/protocol.md` T203 decision |
| Exact local source | 475,664,283 bytes; SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040` | Same protocol; `evidence/tasks/T230-snapshot-completion-and-evaluation-2026-11-21.md` |
| Upstream revision, acquisition date, publisher timezone | Unknown. Source naive minute timestamps use a documented project UTC assumption. | `specs/002-data-and-risk-scoring/protocol.md` §§T203/T212 |
| Full-source EDA summary | SHA-256 `b8900338ca375b2d632b260a794634fb19408012a1c14fc66e2f7b097a111820`; bounded 17,279-byte report, 30 series | `evidence/tasks/T246-full-source-eda-2026-11-21.md`; Feature 002 API contract |
| Source / accepted / rejected | 5,078,345 / 5,078,345 / 0 | T246 aggregate evidence |
| Warm-up / scoreable full source | 1,114,921 / 3,963,424 | T246 aggregate evidence |
| Full-source UTC coverage | 2022-09-01 00:00 through 2022-09-18 16:18 | T246 aggregate evidence; timezone is project assumption |
| Quality and currency bounds | `quality_counts={}` with zero rejects; 12 paid and 12 received currency amount series shown, three currencies omitted on each side | T246 aggregate evidence. No separate full-source missing-value report in this checkout. |

The `/eda` API returns only this independently hash-pinned, label-free aggregate when configured. It has category and UTC transaction-count series and currency-separated paid/received amount totals by UTC bucket. The bounded contract does **not** contain amount histograms, median transaction amounts, label balance, or individual records. Do not describe its amount-by-time totals as a transaction-amount distribution. The local fixture server returns controlled 404 when no pinned summary is configured. Sources: `specs/002-data-and-risk-scoring/contracts/api.md`, `backend/src/fraudlens/eda/service.py`, `web/src/scoring/contracts.ts`.

## Preparation, features, and frozen research split

The canonical pipeline validates the source header/positions, including two distinct `Account` columns, preserves decimal amount text, rejects invalid rows, and constructs label-free events. The feature kernel in `backend/src/fraudlens/data/features.py` defines eight historical features and three current-event features. It uses a strict prior `[t−24h,t)` window; equal-instant peers never contribute to one another. Current model inputs are `current_amount_paid_log1p`, `current_payment_currency`, and `current_payment_format`. The older `web/public/data/features.json` calls the amount feature `current_paid_amount` and is **not** an accurate final-model feature catalog. The selected model uses nine numeric inputs plus train-only one-hot vocabularies for currency and payment format, producing 32 matrix columns; missing inputs are rejected, not imputed. Sources: `features.py`, `backend/src/fraudlens/training/local_run.py`, `evidence/tasks/T229-unweighted-freeze-export-2026-11-20.md`.

The original T218 scoreable development train/validation/test split (1,319,586 / 282,681 / 282,714) is **historical**. The executed FR-021 research split uses complete UTC days with approximate 60/20/20 targets; only five development dates make exact shares impossible. Warm-up and showcase are outside model fit and selection. Frozen scoreable development is 1,884,981 rows, partitioned as follows. Sources: `specs/002-data-and-risk-scoring/protocol.md` research-split addendum and approved T219 protocol, canonical SHA-256 `1ebac4f24aa198cfd1de70b96204676cb3fbd0cc07786296944c6ade0214f6be`.

| Partition | UTC coverage | Rows | Positive | Negative | Prevalence |
| --- | --- | ---: | ---: | ---: | ---: |
| Train | 2022-09-02 through 2022-09-04 | 1,169,261 | 1,206 | 1,168,055 | 0.103142% |
| Validation | 2022-09-05 | 482,650 | 471 | 482,179 | 0.097586% |
| Test | 2022-09-06 00:00 through 11:12 | 233,070 | 218 | 232,852 | 0.093534% |

These are 62.03%, 25.61%, and 12.36% of **scoreable development**, not of the full 5,078,345-row source. Train labels fit the model, validation outcomes select model/threshold, and the one authorized test evaluation followed frozen predictions. The later 2,078,443-row showcase is excluded from this research evaluation; its prevalence exception is documented, not an unbiased holdout.

## Selected model and authorized evaluation

The final local capstone model is the **unweighted LightGBM GBDT** from the five-arm numerical diagnostic, subsequently ranked first in the approved cross-family **validation** comparison and explicitly accepted for opt-in local model mode. It was not refitted at export. It uses 1,169,261 training rows, 11 source feature fields expanded to 32 model columns, 140 trees (best iteration; 190 total rounds), 31 leaves, learning rate 0.05, minimum child samples 200, `scale_pos_weight=1`, deterministic CPU, seed 42, and validation binary-logloss early stopping. No class resampling or weighting was used for this final model. Threshold `0.2489517623052024` maximized positive-class F1 on validation. Native model SHA-256 `3b4e4019312d60610dd0094c6697897a061611a60e7777ed7be35e133af9451c`; independently trusted manifest SHA-256 `c766e90159a70eff2d1f29d5ff425029af20ff123f1fad08e45f9fc416076d45`. Sources: `evidence/tasks/T228-stagec-numeric-diagnostic-execution-2026-11-20.md`, `T224-stagec-cross-family-execution-2026-11-20.md`, `T229-unweighted-freeze-export-2026-11-20.md`, `T231-stage-d-acceptance-2026-11-21.md`.

The approved aggregate T230 test report SHA-256 is `5027dae9354796718a080086a6cadc0319d1b376336ad4dac8d93b4e534d9cdb`; its lineage binds the above model, sealed prediction SHA-256 `99727d426f78698ee9a0f37ec50c1c900dc848f13bed6ef0756544f76c3f04f7`, and unchanged threshold. The two columns below use the **same frozen model**. Source: `evidence/tasks/T230-snapshot-completion-and-evaluation-2026-11-21.md`.

| Aggregate at fixed threshold | Validation | Test |
| --- | ---: | ---: |
| TP / FP / TN / FN | 107 / 122 / 482,057 / 364 | 44 / 21 / 232,831 / 174 |
| Alerts | 229 | 65 |
| Precision / recall / F1 | 0.467249 / 0.227176 / 0.305714 | 0.676923 / 0.201835 / 0.310954 |
| Average precision / ROC AUC / Brier | 0.216661 / 0.966239 / 0.000846056 | 0.274502 / 0.976155 / 0.000770118 |
| P@20 / P@50 / P@100 | 17/20 / 38/50 / 65/100 | 18/20 / 38/50 / 52/100 |

P@K applies to each whole partition. The test covers only part of 2022-09-06, so its 65 alerts do not establish full-day analyst volume. The model outputs uncalibrated scores; Brier is diagnostic, not calibration proof. A high ROC AUC does not imply high recall at this threshold. Validation was reused in selection and diagnosis. This synthetic, single-source result is not a real-world performance claim. The model is approved for local capstone opt-in use, not production.

## Page conflicts and presentation decisions

- `web/src/pages/Data.tsx` currently says a scikit-learn artifact is pinned and no evaluation result exists. Both statements are stale for the selected native LightGBM and approved aggregate T230 report. Its `metrics.json`/`eda.json` placeholders describe a separate Feature 005 showcase; leave those shared files intact and replace only `/data` presentation.
- `web/src/scoring/views.ts` currently renders a second navigation block inside `SiteFrame`. Use the shared shell navigation, plus one contextual link to `/data`.
- No approved aggregate in the inspected contract supports label prevalence on `/eda`, amount histograms, ROC/PR curves on `/data`, full-source missing-value rates, exact upstream release/date/timezone, or deployment efficacy. Keep these unavailable or explain limits.
