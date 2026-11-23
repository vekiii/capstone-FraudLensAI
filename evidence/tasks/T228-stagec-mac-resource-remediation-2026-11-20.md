# T228 Stage C Mac Python and resource remediation — 2026-11-20

- Scope: technical preparation only; FR-021 candidate remains unapproved; T228–T230 open.
- Baseline: `aa1accac0ff90f2eb370618be15f145b3cc6bf2b`, with pre-existing local changes in `next_work.md`, `evidence/README.md`, and the untracked Mac receipt. They were preserved.
- Prompt: [original request record](../../prompts/development/002-T228-stagec-mac-resource-remediation.md). Specification, plan, tasks and constitution were read; current candidate was inspected but not edited.
- Runtime: macOS 27.0.1 Apple M5 Pro arm64, uv 0.12.15, Python 3.14.10 in this project's `.venv`, LightGBM 4.7.0, scikit-learn 1.9.1, NumPy 2.5.5; `uv.lock` SHA-256 remains `b9b1c52056c3706fd21fc1fefa9934fc1c1c8c09dd2b0f465d8d49ad25cc1ffe`.

## Python diagnosis and installation

`UV_CACHE_DIR=work/uv-cache uv python list --all-versions | rg '3\.14\.(10|7)'` listed installed 3.14.7 and a 3.14.7 free-threaded download, but no 3.14.10. `UV_CACHE_DIR=work/uv-cache uv python install 3.14.10 --install-dir work/python --verbose` exited 2 immediately: `No download found for request: cpython-3.14.10-macos-aarch64-none`. This is uv 0.12.15's available-build catalog, not evidence that CPython 3.14.10 does not exist. [Python.org's release](https://www.python.org/downloads/release/python-31410/) is dated 2026-10-25. The [python-build-standalone release](https://github.com/astral-sh/python-build-standalone/releases/tag/20261110) has `cpython-3.14.10+20261110-aarch64-apple-darwin-install_only.tar.gz`; GitHub release API reported SHA-256 `42031ed5f0d38777335252c8c77d64708c8010dd67c128246bdec25000672666`, size 27,109,898 bytes.

Sandbox network was a separate issue: ordinary `curl -I` exited 6 (`Could not resolve host: github.com`), while the elevated official-source probe reached Python.org with HTTP 200. The first `uv sync --locked --group dev --group ml --python work/python-3.14.10/python/bin/python3.14` recreated `.venv` then failed to fetch NumPy because sandbox DNS was denied. The approved network rerun succeeded: 47 locked packages installed, Python 3.14.10 and the expected ML versions imported. The downloaded archive was checked against the published SHA-256 and extracted under ignored `work/python-3.14.10/`; no system Python or other virtual environment changed. `.python-version` remains `3.14`, so a future unspecific environment rebuild could choose another patch version; use explicit `--python work/python-3.14.10/python/bin/python3.14` for this checkout.

## Prior gap and code change

- `backend/src/fraudlens/training/local_run.py`: `_peak_working_set()` returned `None` outside Windows; `run_training()` called `fit_lightgbm_matrix_grid()` with no disk, memory or elapsed limit and recorded aggregate fit time only after return. Output `experiment.json` was written only at the end, with no explicit interrupted state.
- `backend/src/fraudlens/training/candidates.py`: `fit_lightgbm_matrix_grid()` iterated all eight `_fit_lightgbm` calls without a start hook, so an outer watchdog could not distinguish one active fit from the rest.
- `backend/src/fraudlens/scoring/artifacts.py`: `_runtime_versions()` already requires exactly 3.14.10 and LightGBM 4.7.0; its writer produces native model bytes and versioned metadata. It was not changed.

New `resource_guard.py` starts the CLI worker in its own POSIX process group (Windows process group plus `taskkill /T /F`), polls the process tree RSS via macOS `ps` RSS in KiB converted to bytes, and stops it on a breach. It checks initial free disk on the output volume before starting, then a 10 GiB reserve throughout and at completion. The current candidate's exact fit ceilings are 20 GiB initial disk, 10 GiB ending reserve, 8 GiB memory, 3,600 s for one fit, 28,800 s current phase, and 54,000 s all fits. Per-candidate start markers are atomic; the watchdog checks their monotonic time while `_fit_lightgbm` is active. It also checks overall elapsed time, which conservatively includes input preparation and output. On macOS `resource.getrusage(...).ru_maxrss` is bytes; the worker records its exact direct-process peak, and the parent checks the direct child peak after exit in addition to sampled tree RSS. An atomic `status.json` remains `incomplete` on a limit, worker failure or missing report, with the reason and observed peak; it becomes `complete` only after zero exit, final reserve and `experiment.json`. The output path refuses overwrite. Windows remains importable and retains worker working-set measurement/termination; current LightGBM uses threads, not subprocess workers.

The watchdog samples every 0.1 s. Thus active sustained excess is stopped, and the direct macOS worker's brief peak is detected at exit, but a brief peak in a descendant between samples can be missed; this is **not a hard instantaneous memory cap**. A worker that deliberately escapes its process group is outside the stop mechanism. Windows memory polling covers the direct worker, not arbitrary future descendants. The shell `ps` access is required on macOS: the restricted Codex sandbox denies it, so the guard fails closed before starting a worker there; an elevated synthetic test confirmed `ps` works on this Mac. These limits need human review before any authorized fit.

## RED, GREEN and checks

All commands below ran from the repository root; no full dataset or model fit was used.

- RED: `PYTHONPATH=backend/src .venv/bin/pytest backend/tests/unit/test_resource_guard.py -q --basetemp work/pytest-resource-red` exited 2 during collection with intended `ModuleNotFoundError: fraudlens.training.resource_guard`.
- First GREEN in restricted sandbox: eight tests, six passed and two failed because `ps` was denied (`PermissionError: Operation not permitted`), not a behavior assertion. Elevated `PYTHONPATH=backend/src .venv/bin/pytest backend/tests/unit/test_resource_guard.py backend/tests/unit/test_local_run.py backend/tests/unit/test_lightgbm_matrices.py -q --basetemp work/pytest-resource-green-escalated` passed 8 tests.
- Final elevated no-fit regression: `PYTHONPATH=backend/src .venv/bin/pytest backend/tests/unit/test_resource_guard.py backend/tests/unit/test_research_split.py backend/tests/unit/test_research_labels.py backend/tests/unit/test_research_protocol.py backend/tests/unit/test_local_run.py backend/tests/unit/test_lightgbm_matrices.py backend/tests/unit/test_evaluation.py backend/tests/unit/test_artifacts.py -q --basetemp work/pytest-stagec-final`: 72 passed. After adding partial-output, current-phase and total-fit timeout cases and a Windows handle cleanup fix, the same command with `--basetemp work/pytest-stagec-final-3` passed **75 tests** in 1.11 s.
- `RUFF_CACHE_DIR=work/ruff-cache .venv/bin/ruff check backend/src backend/tests evidence/tasks/T219-ibm-split.py evidence/tasks/T219-ibm-labels.py evidence/tasks/T219-ibm-candidate.py evidence/tasks/T230-evaluate.py`: passed after one import-order correction in the new test. `git diff --check`: passed.
- `PYTHONPATH=backend/src .venv/bin/python -m fraudlens.training.local_run --help`: passed. Direct `_load_protocol` check recomputed canonical SHA-256 `f34c51bcaeec63072a29eceae987b85ff3e8d88ac106fe51e9fc16355d5b3f5f` and printed the above fit ceilings. `test_artifacts.py` exercised the exact-version writer/reader path with invented model bytes on Python 3.14.10; no LightGBM model was fitted.
- Full backend suite: not run, because existing baseline tests fit estimators and the user prohibited any fit. `T219-ibm-candidate.py`, `T230-evaluate.py`, eight candidates, real-data fit and record-level test/showcase label access: not run.

## Protocol integrity and next step

The candidate JSON raw SHA-256 remains `4793819cc7df65ea37df90659149d63de6352ca5a70b23cbb50a192e62f300bf`; canonical digest remains `f34c51bcaeec63072a29eceae987b85ff3e8d88ac106fe51e9fc16355d5b3f5f`. Its implementation hash mapping still contains the **old** runner/candidate values and does not cover the new guard. No candidate hash was edited and no protocol approval is claimed.

| Implementation file | Candidate's old SHA-256 | Current SHA-256 |
| --- | --- | --- |
| `backend/src/fraudlens/training/local_run.py` | `5b30fdc25c591053c7a2080e413778ce9be455cff75dfb272e8a6463cac8988e` | `d8ae1fa2ca010d4cab625c00d4c72adcd263fcec46e0300246bf55de23b2003b` |
| `backend/src/fraudlens/training/candidates.py` | `b741a19ab93aad99413c2359ea2f04981c5eb2688f548e74dd87af32780f224c` | `bec506b6431a50c26e3610c78d46d18fe4ed76ed96e92f4827cdc1b043009132` |
| `backend/src/fraudlens/training/resource_guard.py` | absent | `b2ca33d608540548712ddf2e185d68d19a5da4dba61d104158011f56a0dcad34` |

Next step: prepare a new FR-021 protocol candidate that hashes the changed runner, candidate loop and new resource guard, records the sampled-memory limitation, then submit that exact new digest for human review before any fit.

Human review: pending. Second-person reproduction of this change: pending.
