# Phase 8 T060–T061 regression — 2026-11-14

Original request: [Phase 8 prompt](../../prompts/development/002-phase-8-t060-t067-2026-11-14.md). Shared branch `model-implementations`, HEAD `fb32b8c8467bb5cffe6b4cbc57730b484af1b1db`; pre-existing Phase 5–7 uncommitted work was preserved. The quickstart and root/frontend/data READMEs now describe the actual fixture and dataset modes, eight CLI commands, frozen local hashes, private labels, staging/activation, recreation and exploratory reproduction. No source CSV, IBM SQLite or model artifact was changed.

## Locked environment and checks

| Actual command from repository root | Exit and observed result |
|---|---|
| `UV_CACHE_DIR=$PWD/.cache/uv uv sync --locked --group dev` | 0; resolved 48, checked 46 packages |
| `npm ci` in `frontend/` | 0; 68 packages; optional `fsevents` script warning |
| `UV_CACHE_DIR=$PWD/.cache/uv PYTHONPATH=.:backend/src uv run --locked pytest backend/tests -q --ignore=backend/tests/unit/test_pretrained_ibm_inference.py --ignore=backend/tests/unit/test_pretrained_loader.py --tb=short` | 0; **675 passed**, 2 existing warnings (Starlette deprecation, loky core detection), 53.64 s |
| `UV_CACHE_DIR=$PWD/.cache/uv PYTHONPATH=.:backend/src uv run --locked pytest backend/tests/contracts -q --tb=short` | 0; **158 passed**; unchanged v1 and reviewed v2 schema parity/validation |
| `UV_CACHE_DIR=$PWD/.cache/uv uv run --locked ruff check backend` | 0; all checks passed after removing one unused local variable in new review helper |
| `npm test -- --run` in `frontend/` | 0; **8 files, 168 passed** |
| `npm run typecheck` in `frontend/` | 0 |
| `npm run build` in `frontend/` | 0; Vite 8.3.8, 8 modules transformed |
| `git diff --check` | 0 |

The initial locked backend invocation with `PYTHONPATH=backend/src` exited 2 at collection with four `ModuleNotFoundError: backend` errors; the corrected root path above collected and passed all non-pretrained tests. An earlier `uv run --locked` without a local `UV_CACHE_DIR` exited 2 because the sandbox denied access to the default user cache. These were environment command errors, not test RED or regressions. The first Ruff run exited 1 for an unused variable in the newly added sample helper; the final run above passed.

The separate existing pretrained proposal was checked with `UV_CACHE_DIR=$PWD/.cache/uv PYTHONPATH=.:backend/src uv run --locked pytest backend/tests/unit/test_pretrained_ibm_inference.py backend/tests/unit/test_pretrained_loader.py -q --tb=short`: exit **1**, **66 known RED failures and 4 passes**. Those tests target the absent `fraudlens.pretrained` / `fraudlens.pretrained_inference` interfaces for a different external artifact. They are not newly introduced history-v1 regressions.

## Live HTTP and proxy smoke

Local socket binding needed the sandbox escalation. `APP_MODE=fixture PYTHONPATH=backend/src .venv/bin/uvicorn fraudlens.main:app --host 127.0.0.1 --port 8000` and `VITE_APP_MODE=fixture npm --prefix frontend run dev -- --host 127.0.0.1 --port 15173` started successfully (the Vite proxy targets port 8000). `curl -sS -i` to both `:8000/api/cases` and `:15173/api/cases` returned exit 0, HTTP 200 and the same `CASE-001`–`CASE-003` v1 payload; `:15173/` returned HTTP 200 with the app HTML. Servers were stopped.

With the previously controlled Phase 7 run store `/tmp/fraudlens-phase7-controlled-20261114.sqlite`, `APP_MODE=dataset APP_SCORER=model` plus `VITE_APP_MODE=dataset` started successfully. Direct `GET /api/health` returned HTTP 200, `score_source=model`, `active_run_id=run_model_control`; proxied `GET /api/cases` returned HTTP 200 with one controlled item, `snapshot_ref=run_model_control`, exact 1/1 counts and `uncalibrated_probability_estimate`. Restarting the API with `APP_SCORER=rules` against the model-active store returned proxied HTTP 503 `run_unavailable`, as contracted. All `curl` calls exited 0. These controlled data are UI/API checks, not model evaluation. The actual frozen model run's `no_alert` list remains zero.

The Phase 7 [browser evidence](feature-002-api-ui.md) contains direct UI checks for fixture, latest-100, restart, switch, empty and unavailable states. A fresh Phase 8 browser check was attempted, but the computer-use inventory returned `Browsers: Error: Local browser use is disabled in Work settings`. The native Safari surface was on an unrelated ChatGPT permission dialog, so it could not provide a reliable app check. Phase 8 therefore has HTTP/proxy and automated UI evidence, with **fresh browser inspection unrun due to the Work setting**.

The read-only `freeze-protocol` quickstart command returned exit 0 with `status=frozen`, eligible partitions and the recorded protocol hash. The new `reproduce` quickstart command returned exit 0 with zero semantic differences; see [benchmark](feature-002-benchmark.md). Import and feature build were already executed on the authorized source in earlier phases; they were not repeated because the existing complete IBM store and archived import were preserved. A clean second checkout/source acquisition is T066, pending another teammate.

## Publication gate rerun — 2026-11-14

The publication request is preserved in [the original prompt](../../prompts/development/002-feature-002-publication-2026-11-14.md). Before staging, local `model-implementations` HEAD and `origin/model-implementations` were both `fb32b8c8467bb5cffe6b4cbc57730b484af1b1db`. `git fetch origin` exited 0 (only `origin/feature03` advanced); `git rev-list --left-right --count origin/model-implementations...HEAD` returned `0 0`, so no existing local-only commit needed preservation or reconciliation. All pre-existing Feature 002 modifications stayed in place. No IBM source, SQLite, frozen model or published benchmark was changed for this handoff.

| Actual publication command | Exit / observed result |
|---|---|
| `UV_CACHE_DIR=$PWD/.cache/uv uv sync --locked --group dev` | 0; resolved 48, checked 46 packages |
| `UV_CACHE_DIR=$PWD/.cache/uv PYTHONPATH=.:backend/src uv run --locked pytest backend/tests/unit/test_model_selection.py backend/tests/unit/test_model_artifacts.py backend/tests/unit/test_model_scoring.py backend/tests/unit/test_explanations.py backend/tests/integration/test_dataset_api.py backend/tests/integration/test_run_publication.py backend/tests/integration/test_reproduction.py backend/tests/integration/test_model_validation_snapshot.py` | 0; **40 passed**, 1 Starlette warning, 52.52 s |
| `UV_CACHE_DIR=$PWD/.cache/uv PYTHONPATH=.:backend/src uv run --locked pytest backend/tests --ignore=backend/tests/unit/test_pretrained_loader.py --ignore=backend/tests/unit/test_pretrained_ibm_inference.py` | 0; **679 passed**, 2 existing Starlette/loky warnings, 45.63 s |
| `UV_CACHE_DIR=$PWD/.cache/uv PYTHONPATH=.:backend/src uv run --locked pytest backend/tests/contracts -q` | 0; **158 passed**, including v1/v2 schema parity |
| `UV_CACHE_DIR=$PWD/.cache/uv uv run --locked ruff check backend` | 0; all checks passed |
| `npm test -- --run` in `frontend/` | 0; **168 passed in 8 files** |
| `npm run typecheck` in `frontend/` | 0 |
| `npm run build` in `frontend/` | 0; Vite 8.3.8, 8 modules transformed |
| `git diff --check` | 0 |
| `UV_CACHE_DIR=$PWD/.cache/uv PYTHONPATH=.:backend/src uv run --locked pytest backend/tests/unit/test_pretrained_loader.py backend/tests/unit/test_pretrained_ibm_inference.py -q` | 1; **66 known RED failures, 4 passes**; missing `fraudlens.pretrained`/`fraudlens.pretrained_inference` for the separate publisher-model proposal, not a new history-v1 regression |

Local hashes rechecked with `shasum -a 256` (exit 0): frozen protocol `01fff67d44895b5a1aa6de6dfbb6c6c107f01c041ba7c972bf42210e2b316068`, trusted manifest `2732691cb08daafba9d303ef6f3c8f616e03b3dc51505d3abb9772ceadd3919e`, metadata `8b5a513f0346b31b4c7ff60143078567f63e041f9d86d59388b7057f00f398e2`, model `fd2332d543941886eb7d0092d7a606b683d1d7c198e3763865ebc7b6a2df0838`. `git check-ignore -v` (exit 0) confirmed ignored source CSV, processed SQLite, model binary, test predictions and private labels. The quickstart now documents both an approved transfer of this exact frozen artifact and a separately identified fresh train/validation fit; the latter has not been reproduced on a second machine. Direct browser checks belong to Phase 7; Phase 8 has live API/Vite proxy checks, and fresh browser inspection remains unrun due to the Work setting.
