# Isolated IBM HI-Small tree notebook reproduction — 2026-11-14

## Authority and scope

- Original request: `prompts/development/002-ibm-tree-notebook-reproduction-2026-11-14.txt`.
- User-supplied reference: `reference/ibm-aml-with-trees.ipynb`, copied byte-for-byte from the supplied Downloads file; SHA-256 `468c298be1a4d9f405f3d2b673014eacd4d704fd85b8e44cc43a72415c15923e`.
- Branch: `model-implementations`; starting HEAD `c30a6ac`. The initial implementation request made no commit or push; this later publication request produced `cab42fd` (reference notebook and original request) and `6f7bcb7` (isolated implementation, tests, and artifact ignore rule). No pre-existing tracked file or `evals/protocols/feature_002_v1.json` was changed. Existing untracked protocol drafts were preserved. No push was requested or made.
- This is an **exploratory offline notebook reproduction**. It is not the approved Feature 002 `history-v1` scorer or a replacement for original T029–T036.

## Implemented

New `backend/src/ibm_aml_trees/` package streams the exact duplicate-header IBM CSV, preserves bank/account strings until coding, saves raw row index, stable-sorts timestamps, and computes the notebook's 9 basic and 20 vectorized history features over the full sorted file. It then makes a whole-timestamp temporal 60/20/20 split, optionally samples only training rows at a common effective fraction, fits HistGradientBoosting for seeds 0–2 with validation-only max-F1 thresholds, and reports test F1, precision, recall, average precision (PR-AUC), confusion counts and 1,000-resample row-bootstrap 95% intervals per seed. The basic-feature ablation and optional delayed-alert rule are reported separately. A development-only grouped stratified split is available with an explicit time-leakage warning.

Completed run outputs are ignored under `artifacts/<run_id>/`: native joblib models, manifest with ordered features, categories, thresholds, split reports, versions, source hash and metrics, plus a scoring wrapper. Joblib loading is limited to a caller-designated trusted local run and verifies the recorded model hash. The scorer ignores labels and returns estimates in new-row input order. Its output has not been calibrated or integrated into FraudLens case assessment.

## Executed checks and results

| Command/check | Observed result |
| --- | --- |
| Initial five focused tests with stub interfaces | 5 failed at the intended missing feature/split/sampling behavior (RED); valid collection. |
| `.venv/Scripts/python.exe -m pytest backend/tests/unit/test_ibm_aml_trees_experiment.py -q -p no:cacheprovider --basetemp artifacts/pytest-tree-20261114-c --tb=short` | 9 passed, exit 0. Covers hand-computed ties/self-transfer history, future/label invariance, temporal and grouped split boundaries, train-only sampling, stable CSV read, bootstrap, manifest round-trip and reloaded scoring. |
| `.venv/Scripts/python.exe -m pytest backend/tests --ignore=backend/tests/unit/test_pretrained_loader.py --ignore=backend/tests/unit/test_pretrained_ibm_inference.py -q -p no:cacheprovider --basetemp artifacts/pytest-tree-regressions-20261114 --tb=short` | 608 passed, 1 existing Starlette/httpx warning, exit 0. The two intentionally RED pretrained suites were excluded. |
| `.venv/Scripts/ruff.exe check backend/src/ibm_aml_trees backend/tests/unit/test_ibm_aml_trees_experiment.py` | All checks passed, exit 0. |
| Source and six model SHA-256 values checked against `manifest.json`; `git check-ignore -v` on raw CSV and model binary | All matched; both paths ignored. |
| `.venv/Scripts/python.exe -m ibm_aml_trees.train --data data/raw/HI-Small_Trans.csv --out artifacts --retro` with `PYTHONPATH=backend/src` | Completed, exit 0, 765.22 seconds. Run `trees-20261114T100430Z-b19d39f5`; source SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`. |
| `.venv/Scripts/python.exe -m ibm_aml_trees.evaluate --run artifacts/trees-20261114T100430Z-b19d39f5` | Completed, exit 0; read the saved manifest, no new label access. |

Full-data split, with `split_mode=temporal`, `train_frac=1.0`: train 3,046,861 rows / 2,297 positives (0.075389%); validation 1,015,920 / 1,083 (0.106603%); test 1,015,564 / 1,797 (0.176946%). All 5,078,345 rows contributed to feature history before splitting. Whole-minute split boundaries prevent train/validation/test timestamp overlap. Stage times: load 58.34 s; features 14.99 s; basic fit/evaluate 229.04 s; history fit/evaluate 461.73 s. A read-only process snapshot during the run showed 1.73 GB working set; it was not a peak-memory measurement.

| Test variant (three-seed mean) | F1 | Precision | Recall | PR-AUC |
| --- | ---: | ---: | ---: | ---: |
| 9 basic features only | 0.2389 | 0.2271 | 0.2523 | 0.1185 |
| Basic + 20 history features, model alone | 0.6519 | 0.8683 | 0.5222 | 0.6294 |
| Delayed alerts, **not real-time**, applied to history model | 0.7182 | 0.8199 | 0.6398 | n/a: binary follow-up rule, not a new ranking score |

Per-seed history model F1: 0.6606, 0.6502, 0.6449; PR-AUC: 0.6409, 0.6188, 0.6285. Their 1,000-resample F1 intervals are respectively [0.6405, 0.6801], [0.6301, 0.6704], [0.6245, 0.6671]; PR-AUC intervals [0.6182, 0.6627], [0.5944, 0.6432], [0.6056, 0.6525]. Per-seed basic and delayed-alert counts and intervals are preserved in the local manifest. Intervals hold each fitted model and validation threshold fixed; they do not cover retraining variance. No confidence interval for the three-seed mean was estimated.

## Differences, limitations and review

- The notebook's direct row-count 60/20/20 cuts can divide equal timestamps. This implementation moves boundaries to whole timestamp groups to meet the requested no-time-overlap check. Natural class rates were reported; none were equalized.
- The notebook uses pandas and, in its lean extension, PyArrow. Neither is installed in the locked local environment. A streaming Python CSV reader and NumPy arrays achieved a completed full run without changing `pyproject.toml` or `uv.lock`. The manifest records pandas as `null`.
- The reference uses unqualified account strings and treats earlier same-minute rows as available history. Those choices are reproduced here, but they differ from FraudLens's bank-qualified, strict-earlier-timestamp `history-v1` contract. This artifact must not be represented as compatible application inference.
- The supplied task covers HI-Small; LI-Small, HI-Medium, charts and pattern-file analysis from the notebook were not reproduced. Retroactive flagging uses validation-chosen window/low-score settings separately for each seed; earlier alerts are delayed until a later model alert.
- A post-run code cleanup replaced an unnecessary average-precision calculation inside retro tuning with its algebraically identical F1 count and marked delayed-alert PR-AUC as not applicable. The ignored manifest's representation was corrected without refitting, changing thresholds or re-reading labels. The full-data run was not repeated after that cleanup; the nine focused tests passed on final source.
- Human review and a team decision are required before any proposal to alter the approved Feature 002 protocol or connect this model to the product. Existing T029–T036 remain open. The original add-only implementation request left root `next_work.md` untouched; this later publication request updates it with the commit ledger. Next step: review the experimental feature identity/time semantics and decide whether a separate versioned application contract is warranted.
