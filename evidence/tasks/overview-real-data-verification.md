# Overview real-data verification

Date: 2026-11-15
Verification was run on `model-implementations` from starting commit `a0b3a69`. The scoped implementation and evidence were then published to `feature/005-real-time-fraud-detection-mlops-spec` as `55f02b0a33fb9df27b17868330f0333a940651ad` and `799ebe8c08b2119dbbde02b48544d6d5a1196bc5`; the handoff and contribution ledger are recorded in a subsequent commit.
Original request: [overview-real-data-verification-2026-11-15.md](../../prompts/development/overview-real-data-verification-2026-11-15.md)

## Outcome

**Real-data dashboard integration is blocked by the missing completed publication RunStore and exact active model artifact.** The Overview correctly stays unavailable instead of substituting the source CSV, a work database, an experimental model or test fixtures. No transaction counts, fraud rate, threshold or evaluation metrics were displayed. No labels or holdout values were queried.

## 1. Available data and artifacts

| Local item | Provenance/status | Dashboard disposition |
|---|---|---|
| `data/raw/HI-Small_Trans.csv` (475,664,283 bytes) | Ignored local copy. SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040` matches the hash-pinned [Feature 002 mapping](../../data/mappings/ibm_hi_small_v1.json) and the existing [T065 source verification](feature-002-t065-source-fact-check-2026-11-15.md). The verified publisher release is IBM HI-Small v8 under CDLA-Sharing-1.0. Existing T065 evidence reports 5,078,345 valid/source rows and zero rejects. | Not a completed scoring run. No labels or source rows were read in this task. Its source count is not presented as active scored transactions. |
| `data/processed/feature-002-ibm-v8-t065-work.sqlite` (7,559,012,352 bytes) | Ignored local Feature 002 T065 source/history work store. The existing T065 record documents the exact source, mapping and time-policy hashes. | Not the dashboard publication RunStore. No private evaluation-label table was queried. |
| `data/artifacts/feature-002-runs.sqlite` | Configured default `APP_RUN_STORE` path; absent. `APP_MODE`, `APP_SCORER` and `APP_RUN_STORE` were unset before smoke setup. | No active run metadata or assessments can be reconciled. |
| `artifacts/feature-002-history-v1-20261114/` | Expected trusted frozen application artifact path from `backend/tests/unit/test_model_scoring.py`; absent in this checkout. | No verified active application model artifact is available here. |
| `artifacts/trees-20261114T100430Z-b19d39f5/` | Local ignored experiment with a manifest whose status is `exploratory_not_application_model`; model is a HistGradientBoosting experiment. Its source hash matches the CSV, but the model is explicitly not the application scorer. | Excluded from the dashboard. Its existence does not establish an active or approved run. |
| `data/artifacts/aml_lgbm_{metrics.json,model.txt,preproc.joblib}` | Ignored local AML-LGBM lineage referencing `eexzzm/IBM-Transactions-for-Anti-Money-Laundering-HI-Small-Trans`; it is separate from the Feature 002 scorer. Its metrics file does not establish the exact active application model/version and evaluation split. | Not loaded; no values from it are displayed as application performance. |

The application settings default to fixture mode and to the missing `data/artifacts/feature-002-runs.sqlite` store. The configured model artifact loader expects a different pinned manifest and model path. No compatible active run store was found among the project-owned top-level data/artifact files. Pytest-created databases and artifacts were excluded from the inventory.

## 2. Displayed values and reconciliation

Dataset-mode smoke was explicitly configured with `APP_MODE=dataset`, `APP_SCORER=model`, and `APP_RUN_STORE=data/artifacts/feature-002-runs.sqlite`.

| Check | Result |
|---|---|
| `GET http://127.0.0.1:8000/api/overview` | HTTP 503, `{"error":{"code":"run_unavailable","message":"Selected run is unavailable."}}` |
| Vite proxy `GET http://127.0.0.1:5173/api/overview` | Same HTTP 503 response |
| Overview route | HTTP 200; shows “No active dataset or model run is configured.” and retry control |
| Reload stability | Same unavailable state after page reload; no page errors |
| Desktop | 1440px viewport and document width; no horizontal overflow |
| Mobile | 390px viewport and document width; no horizontal overflow |

Because the RunStore file is absent, there are no persisted run totals, prediction counts, timestamps, identity, version or threshold to query. The dashboard displays no fabricated numbers. Confirmed-fraud count, legitimate count, label fraud rate and precision/recall/F1 remain unavailable by design without a label-safe aggregate and matching evaluation-split provenance. No private labels were opened to derive them.

Screenshots were captured with the installed Chrome/Playwright browser and visually reviewed:

- [Desktop unavailable state](overview-real-data-desktop.png)
- [Mobile unavailable state](overview-real-data-mobile.png)

The Computer Use native pipe was unavailable (`failed to connect native pipe`); local headless Chrome/Playwright provided the visual checks instead.

## 3. Changes made

- `backend/src/fraudlens/data_store.py`: strengthen timestamp validation in the existing aggregate SQL. A chart bucket now requires a valid calendar date, parseable ISO timestamp, `T` separator, and UTC marker (`Z` or `+00:00`). Malformed, date-only and non-UTC offsets are reconciled under `unknown_timestamp_transactions`, not graphed.
- `backend/tests/integration/test_overview_api.py`: added focused checks for malformed/non-UTC timestamps, accepted canonical zero-offset timestamps, incomplete active pointers, inconsistent persisted transaction/alert totals, and sanitized SQLite connection errors. Existing checks already cover empty/zero-alert runs and invalid database files.
- No configuration was changed because the expected completed publication store and exact trusted model artifact are absent. No application dependencies, source mapping, thresholds, training, predictions or evaluation protocol changed.

Existing artifact safety coverage was reused: `test_manifest_and_load_checks_before_deserialization` checks missing/corrupt artifacts and incompatible manifest identity, while `test_model_activation_requires_exact_artifact_digest` rejects absent or mismatched digests. Both focused tests passed here.

## 4. Tests and verification

Commands ran from the repository root. Backend commands used `UV_CACHE_DIR=.cache/uv`, `PYTHONPATH=$PWD;$PWD/backend/src`, and workspace-local pytest cache/temp paths where shown.

| Check | Command/result | Exit |
|---|---|---:|
| Backend baseline before edits | `uv run --locked pytest backend/tests --basetemp .cache/pytest-real-overview-baseline -o cache_dir=.cache/pytest-real-overview-cache` — 733 passed, 71 failed, 4 errors, 1 skipped | 1 |
| Frontend baseline | `npm.cmd --prefix frontend run test -- --run` — 174 passed, 10 files | 0 |
| Intended RED, after correcting the corruption fixture to bypass immutable-row triggers | `uv run --locked pytest backend/tests/integration/test_overview_api.py -q --basetemp .cache/pytest-real-overview-red2 -o cache_dir=.cache/pytest-real-overview-cache` — 3 timestamp cases failed as expected, 9 passed | 1 |
| Focused GREEN, including artifact activation gates | `uv run --locked pytest backend/tests/integration/test_overview_api.py backend/tests/integration/test_run_publication.py -q --basetemp .cache/pytest-real-overview-green -o cache_dir=.cache/pytest-real-overview-cache` — 24 passed | 0 |
| Existing artifact safety tests | `uv run --locked pytest backend/tests/unit/test_model_artifacts.py::test_manifest_and_load_checks_before_deserialization backend/tests/integration/test_run_publication.py::test_model_activation_requires_exact_artifact_digest -q --basetemp .cache/pytest-real-artifact-green -o cache_dir=.cache/pytest-real-overview-cache` — 2 passed | 0 |
| Full backend after edits, no exclusions | `uv run --locked pytest backend/tests --basetemp .cache/pytest-real-overview-final -o cache_dir=.cache/pytest-real-overview-cache --tb=short` — 742 passed, 71 failed, 4 errors, 1 skipped | 1 |
| Frontend after edits | `npm.cmd --prefix frontend run test -- --run` — 174 passed, 10 files | 0 |
| Typecheck and production build | `npm.cmd --prefix frontend run build` — TypeScript and Vite build passed | 0 |
| Backend lint | `uv run --locked ruff check backend` — all checks passed | 0 |
| Whitespace | `git diff --check` — passed after the final evidence edit | 0 |

The full backend suite was not filtered. The same 71 failures and 4 errors occurred before and after this change. Final failure groups: 4 unavailable boosted-integration artifact tests; 1 Windows symlink-privilege failure in `test_model_artifacts`; 36 pretrained inference failures importing the absent `fraudlens.pretrained_inference` module and 30 pretrained loader failures importing the absent `fraudlens.pretrained` module; and 4 model-scoring errors because `artifacts/feature-002-history-v1-20261114` is missing. The suite also reported one existing Starlette/httpx deprecation warning.

## 5. Limitations and next step

- This verifies unavailable-state behavior, not real-data dashboard values.
- Existing T065 import evidence establishes the source file/version/hash and import row accounting, but its work database is not an active scored RunStore.
- The installed experimental and separate AML-LGBM model files do not identify the authorized active application scorer and cannot supply its threshold or evaluation metrics.
- Browser reload verifies stable error state only; no real active run existed for populated reload reconciliation.
- This report and its screenshots were committed on the requested Feature 005 branch. Publication status for the final ledger commit is recorded in `next_work.md` after push verification.

Concrete next step: obtain the authorized completed `data/artifacts/feature-002-runs.sqlite` store and its exact trusted model manifest/artifact, then verify active-run SQL aggregates and API/browser values read-only.
