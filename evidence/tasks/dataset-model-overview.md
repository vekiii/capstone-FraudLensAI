# Dataset & Model Overview dashboard

Date: 2026-11-15
Branch: `model-implementations`
Starting commit: `d9bd8a2` (`docs(evidence): record feature-002 publication ledger`)
Original request: [dataset-model-overview-2026-11-15.md](../../prompts/development/dataset-model-overview-2026-11-15.md)

## Implemented

- Added a default Overview page and accessible Overview/Cases navigation. Existing case review remains available.
- Added one read-only `GET /api/overview` endpoint. It reads only the completed active `RunStore`; SQL returns aggregate time buckets and prediction totals, never transaction records.
- Added strict backend and frontend response contracts, cancellable client requests, and loading, empty, unavailable, and controlled API-error states.
- Added four dataset KPI cards, a transaction-volume SVG chart, a predicted flagged/not-flagged trend, a prediction distribution donut, and active scorer/threshold/metric provenance panels.
- Used only the requested ink, azure and vermilion accents with neutral text and borders. No UI dependency was added.

### Changed files

- `backend/src/fraudlens/main.py`
- `backend/src/fraudlens/data_store.py`
- `backend/src/fraudlens/overview_contracts.py`
- `backend/tests/integration/test_overview_api.py`
- `frontend/src/api.ts`
- `frontend/src/contracts.ts`
- `frontend/src/main.ts`
- `frontend/src/overview-view.ts`
- `frontend/src/styles.css`
- `frontend/tests/overview-api.test.ts`
- `frontend/tests/overview-views.test.ts`
- `frontend/tests/views.test.ts` (existing case-flow test now selects Cases from the new default Overview)
- `prompts/development/dataset-model-overview-2026-11-15.md`
- `evidence/tasks/dataset-model-overview.md`
- `evidence/tasks/dataset-model-overview-desktop.png`
- `evidence/tasks/dataset-model-overview-mobile.png`
- `next_work.md`

## Data sources, formulas and provenance

The endpoint reads `active_run`, `scored_runs`, and `scored_assessments` through the existing read-only `RunStore`. The active run identity, source, scorer version, threshold, expected count, scored count and alert count come from `scored_runs`. Time-series buckets are computed in SQLite using `scored_assessments.event_time` and `alert`.

- KPI total is the active run's `scored_count`, labeled **Transactions scored**. It excludes transactions not present in that scoring run, including warm-up rows when the run excluded them; it is not represented as the full imported source count.
- `not_flagged = scored_count - total_alerts`; `flag_rate = total_alerts / scored_count`, or N/A for a zero-row run.
- Each timestamp bucket returns transaction count, flagged prediction count, and their difference. Runs with at most 10,000 expected rows use daily buckets; larger runs use SQLite `%Y-W%W` weekly buckets. Invalid/missing dates are excluded from the chart, separately counted, and included in reconciliation checks.
- Confirmed fraud, legitimate count, and confirmed-label fraud rate are always `N/A`. The public aggregate does not query `private_evaluation_labels`.
- “Flagged” and “not flagged” are model outputs at the stored run threshold; they are explicitly not confirmed classes.
- Precision, recall, F1, evaluation dataset and split are N/A because the serving run schema contains no ground-truth labels or evaluation-split provenance. The endpoint calculates no training or holdout metric.
- Model name is mapped from the stored scoring source/version (`rules`, `model-history-v1` decision tree, or boosted research candidate). Version, source and threshold are read from the active run.

Repository documentation identifies the shared frozen model as `DecisionTreeClassifier(max_depth=5, min_samples_leaf=500, class_weight='balanced', random_state=42)`, scorer version `model-history-v1`, with the frozen decision policy `no_alert`. The recorded tree test AP belongs to a period disclosed by an earlier notebook and is explicitly exploratory; development-validation figures are not test performance. These values are not injected into the endpoint. In this checkout `data/artifacts/feature-002-runs.sqlite` and the original frozen/boosted artifact directories are absent, so the actual active run could not be independently read here. The API therefore remains unavailable until a completed dataset-mode run store is configured.

## Tests and verification

Commands below ran from the repository root on Python 3.14.10 / Node 24.20.0 / npm 11.19.0. Workspace-local uv cache and pytest temp paths were used where needed.

| Check | Command/result | Exit |
|---|---|---:|
| Frontend baseline before code changes | `npm.cmd --prefix frontend run test -- --run` — 169 passed, 8 files | 0 |
| Backend baseline invocation | `uv run --locked pytest backend/tests` — collection failed on 6 `ModuleNotFoundError: backend` imports; no tests ran | 1 |
| Backend baseline with repo `PYTHONPATH` | `uv run --locked pytest backend/tests` — 527 passed, 40 failed, 1 skipped, 236 errors in 61.51s; Windows temp access plus existing absent-artifact/pretrained-proposal failures | 1 |
| Intentional frontend RED | `npm.cmd --prefix frontend run test -- --run tests/overview-api.test.ts tests/overview-views.test.ts` — 4 expected failures because Overview API/mount behavior was not implemented | 1 |
| Focused backend GREEN | `uv run --locked pytest backend/tests/integration/test_overview_api.py -q --basetemp <workspace-local-temp> -o cache_dir=<workspace-local-cache>` — 5 passed in final applicable regression | 0 |
| Applicable backend regression | `uv run --locked pytest backend/tests --basetemp <workspace-local-temp> -o cache_dir=<workspace-local-cache> --ignore=backend/tests/unit/test_pretrained_ibm_inference.py --ignore=backend/tests/unit/test_pretrained_loader.py --ignore=backend/tests/unit/test_model_scoring.py --deselect=backend/tests/unit/test_boosted_integration.py::test_trusted_boosted_reload_and_explanation --deselect=backend/tests/unit/test_boosted_integration.py::test_boosted_explanation_batches_counterfactual_predictions --deselect=backend/tests/unit/test_boosted_integration.py::test_boosted_assess_batch_matches_individual_scoring --deselect=backend/tests/unit/test_boosted_integration.py::test_wrong_boosted_version_rejected_before_deserialization --deselect=backend/tests/unit/test_model_artifacts.py::test_escaped_path_upload_and_incompatible_manifest_reject` — 729 passed, 1 skipped, 5 deselected (730 selected) | 0 |
| Frontend regression | `npm.cmd --prefix frontend run test -- --run` — 174 passed, 10 files | 0 |
| Type check and production build | `npm.cmd --prefix frontend run build` — `tsc --noEmit` and Vite production build passed | 0 |
| Backend lint | `uv run --locked ruff check backend` — all checks passed | 0 |
| Whitespace | `git diff --check` — passed (Git emitted only existing LF-to-CRLF working-copy notices) | 0 |

The broad backend suite remains non-green for out-of-scope pretrained proposal tests and missing local model artifacts. The final applicable regression excluded those artifact-dependent suites and the Windows symlink-privilege test; the new Overview tests were included and passed. The frontend package has no lint script, so no frontend lint command exists.

### API and visual smoke checks

An isolated SQLite run was generated under ignored `.cache/` using the existing synthetic `phase7_samples.entry` helper (three scored rows, two thresholded predictions). It is test data, not a production value or model evaluation.

- FastAPI `http://127.0.0.1:8000/api/overview`: HTTP 200, 3 scored, 2 flagged, 1 not flagged, two daily periods, metrics null.
- Vite proxy `http://127.0.0.1:5173/api/overview`: same aggregate; `/api/cases` returned 2 alerts; `/` returned HTTP 200 with title `FraudLens AI`.
- Desktop screenshot: [dataset-model-overview-desktop.png](dataset-model-overview-desktop.png), emulated 1440px viewport; `innerWidth=1440`, document width 1440.
- Mobile screenshot: [dataset-model-overview-mobile.png](dataset-model-overview-mobile.png), emulated 390px viewport; `innerWidth=390`, document/body width 390. Visual check showed all panels, navigation and cards without horizontal overflow.
- Windows computer-use native bridge was unavailable (`failed to connect native pipe`); installed Chrome headless plus DevTools viewport emulation was used for screenshots and width checks instead.

## Issues found and fixes

- Updated the existing entry-point UI tests to select Cases now that Overview is the default page.
- Fixed an aggregate reconciliation test bug, then verified missing timestamps remain counted but are omitted from timeline buckets.
- Corrected the loading accessibility assertion to inspect `.page-content`, where `aria-busy` is applied.
- Initial Chrome `--window-size=390` screenshots used a 504px CSS viewport and clipped content. DevTools mobile emulation exposed this; the dataset identity now wraps, the mobile header stacks, and the final 390px document width equals the viewport.
- The machine's default uv cache and pytest temp directory are access-restricted. Local workspace cache/temp paths allowed the applicable suite to run.

## Remaining limitations / next work

- This checkout has no active publication run store. Fixture mode correctly returns a controlled unavailable state; actual counts/model identity become visible when an approved completed dataset-mode run store is configured.
- The dashboard reports the active **scored population**, not all imported transactions. Confirmed label counts and precision/recall/F1 remain N/A by design because no label-safe aggregate or evaluation split is attached to the serving run.
- A full live-data smoke test against the missing trusted active run and its artifact was not possible. No model was trained, threshold or mapping changed, and no private/holdout metric was calculated.
- No commit or push was made.

Concrete next step: configure an authorized completed dataset-mode run store in this checkout, then verify the displayed run identity, threshold and aggregates against that store.
