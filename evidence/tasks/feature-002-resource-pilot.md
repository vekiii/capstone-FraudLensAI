# Feature 002 T028 dependency and resource pilot

- Date: 2026-11-13, Europe/Budapest.
- Branch: `model-implementations`.
- Starting HEAD: `a2857cdfce02b9d60b2b8c3c276a2500081cbad5`.
- Outcome: **T028 complete.** The approved minimum Python 3.14 ML stack was locked and installed; the bounded actual-source import/history pilot completed under enforced resource limits. No model fit, comparison, or holdout evaluation ran.
- Prompt: [T028 request](../../prompts/development/002-t028-resource-pilot-2026-11-13.md).
- Authority: Feature 002 `tasks.md` T028; `research.md` Decisions 12 and 14; existing source/mapping approval and T016 import evidence.

## Environment and dependencies

| Item | Observed |
|---|---|
| Platform | Windows 11 x64, build 10.0.26300; CPython 3.14.10, 64-bit; `uv 0.13.8` (`3d97a6aad`, Windows x86-64). CPU model query was denied by local WMI permissions and is not reported. |
| RAM / disk at verification | 16,806,150,144 bytes total RAM; 4,408,696,832 bytes available. Workspace volume: 510,712,082,432 bytes total, 78,396,260,352 bytes free. These are capacity readings, not pilot consumption. |
| Dataset | `data/raw/HI-Small_Trans.csv`, 475,664,283 bytes; SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`, matching the source-bound v8 reference. The source hash matched before and after the pilot. |
| Mapping | Normalized CRLF-to-LF SHA-256 `a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57`, matching the collective approval record. Windows raw bytes have CRLF; this does not change normalized M. |
| Direct ML dependencies | `numpy 2.5.4`, `scipy 1.18.1`, `scikit-learn 1.9.1`. All imported successfully from the locked `.venv` on this CPython 3.14.10 / Windows x86-64 host. |
| New locked transitives | `cloudpickle 3.1.2`, `joblib 1.6.0`, `narwhals 2.28.0`, `threadpoolctl 3.8.0`. No previously locked package version changed. |
| Booster candidates | The authoritative T031 grid is scikit-learn L2 logistic regression and decision trees (at most six fits); LightGBM, XGBoost and CatBoost are not approved candidates and were not added or installed. Current PyPI files advertise Windows-compatible wheel tags for LightGBM 4.7.0, XGBoost 3.4.1 and CatBoost 1.2.10, but these are distribution metadata checks only, not local import/runtime tests: [LightGBM](https://pypi.org/project/lightgbm/), [XGBoost](https://pypi.org/project/xgboost/), [CatBoost](https://pypi.org/project/catboost/). |

The repository’s referenced `evidence/tasks/feature-002-model-reference.md` is absent in this checkout. No IEEE-CIS implementation or feature was copied; the current Feature 002 task grid remained authoritative. The locally approved minimum stack is scikit-learn with NumPy and SciPy, which T031 requires for the planned candidates and metrics.

`pyproject.toml` now declares `numpy>=2.5.4,<3`, `scipy>=1.18.1,<2`, and `scikit-learn>=1.9.1,<2`; exact platform-resolved versions are in `uv.lock`. Lock comparison against starting HEAD found no upgrades to existing package versions. `uv add` emitted an upstream invalid-specifier normalization warning (`>=3.5,` to `>=3.5`); resolution, lock validation and locked sync succeeded.

## Bounded actual-source pilot

The runner streamed the first **100,000 consecutive CSV records** into a new, ignored pilot-only prefix, then used the production canonical row parser, `DatasetStore` batch ingestion and `history-v1` feature builder. The prefix was canonicalized through Python’s CSV reader/writer, retaining the source field values and row order; its digest and pilot-only DatasetVersion do not claim to be the full source’s identity. The approved full-source SHA-256 was independently checked before and after. The new store was isolated at `data/processed/t028-resource-pilot-20261113/` and removed after measurement.

The process guard ran inside the Python worker. It sampled Windows `GetProcessMemoryInfo` peak working set and pilot-directory size every 0.2 seconds, terminating the process if it exceeded **3 GiB peak working set**, **4 GiB temporary disk**, or **30 minutes**. The cumulative Windows peak-working-set counter preserves the process maximum between samples. All limits passed.

The initial measurement wrappers were discarded: one PowerShell launch split the script path at a space, and an early memory-guard draft omitted `ctypes.wintypes`; neither produced accepted pilot measurements. A completed run using a wrapper that watched the Windows launcher also failed to report the Python worker's peak memory. The final in-process guard and streaming runner below correct those measurement issues; only that guarded run is used for the stated results.

| Measurement | Actual result |
|---|---:|
| Pilot source records | 100,000 consecutive records; prefix 9,995,297 bytes, SHA-256 `32685058bb0497d3a0bb88b9031ef81dcf6bf105967097a682cac93aee871f39` |
| Import accounting | 100,000 valid, 0 rejected; 100,000 label-eligible, 0 ineligible; aggregate 5 positive / 99,995 negative. Reconciliation equations passed. No row labels were printed or joined to predictions. |
| Feature build | `history-v1` produced 100,000 snapshots; 0 scoreable because these first records are within the specified 24-hour warm-up. No evaluation split was created. |
| Elapsed time | 145.315 seconds, measured from prefix extraction through feature build completion. |
| Peak working set | 285,134,848 bytes (about 272 MiB), measured by the in-process Windows guard. |
| Peak pilot disk | 262,063,538 bytes (prefix, SQLite database and active journal). |
| Final pilot files before cleanup | SQLite store 250,650,624 bytes; prefix 9,995,297 bytes; feature-lock file 1 byte; total 260,645,922 bytes. |
| Model artifact | None; 0 model fits were run. |
| Guard result | Passed: 145.315 s < 1,800 s; 285,134,848 B < 3,221,225,472 B; 262,063,538 B < 4,294,967,296 B. |

### Estimates and fit-budget recommendation

The existing T016 evidence reports 5,078,345 source records. A simple row-linear extrapolation from this pilot (factor 50.78345) estimates about **7,380 seconds / 2.05 hours** for the import-plus-history workload and about **12.73 GB** for a store with the same per-row footprint. These are estimates only; the first 100,000 records are all warm-up, the prefix is canonicalized, and SQLite/filesystem/cache costs may not scale linearly. The pilot did not measure a full-size feature store or any candidate fit. Memory is not extrapolated.

Before the first model search, use these conservative stop ceilings as T029 inputs: one candidate fit at a time, no more than **six fits** from the approved grid, seed **42**, **30 minutes per fit / 3 hours total**, **3 GiB process peak working set**, and **4 GiB fit scratch/artifact space**. They are prospective guardrails, not demonstrated fit capacity. If a fit reaches a ceiling, stop and record it; do not switch runtimes or silently relax the limit. Any training-view reduction must be declared in T029 while preserving the full chronological history, validation and test roles. The all-warm-up pilot and absence of a model fit leave full training feasibility unverified.

## Preservation, cleanup, commands and checks

No `data/processed/` database or `data/artifacts/` file existed in this checkout before the pilot. The new pilot prefix and SQLite store were created under a unique ignored path, measured, then deleted; `data/processed/` is absent after cleanup. `data/artifacts/` remains absent. The original raw CSV SHA-256 is unchanged, and no earlier imported store or feature artifact was available here to overwrite. The unrelated modified contribution report was preserved.

| Command/check | Exit | Result |
|---|---:|---|
| `uv add --no-sync 'scikit-learn>=1.9.1,<2' 'numpy>=2.5.4,<3' 'scipy>=1.18.1,<2'` | 2 on first sandboxed attempt | PyPI connection denied by sandbox (`os error 10013`); no successful package resolution from that attempt. Retried with the same approved package set and network access; resolution succeeded and installed the seven new packages. |
| `uv lock --check` | 0 | 48 packages resolved; lock is current. |
| `uv sync --locked --group dev` | 0 | 47 packages checked; no lock drift. |
| `.venv\Scripts\python.exe -c "import sys,platform,numpy,scipy,sklearn; ..."` | 0 | CPython 3.14.10 / Windows 11 x64; NumPy 2.5.4, SciPy 1.18.1 and scikit-learn 1.9.1 import successfully. |
| `.venv\Scripts\python.exe .cache\t028-pilot-guarded-runner.py` | 0 | `status=complete`; measurements above; no fits or holdout access. Runner and outputs were local/ignored; pilot data was cleaned up. |
| `pytest -q backend/tests/unit/test_data_import.py backend/tests/unit/test_feature_history.py backend/tests/unit/test_evaluation_protocol.py backend/tests/integration/test_data_store.py -p no:cacheprovider --basetemp .cache/t028-regression` | 1 | 99 passed, 6 failed. All six are existing CLI binding assertions comparing raw mapping SHA to a CRLF checkout; the authorized import boundary hashes normalized LF bytes. This is the previously documented Windows `core.autocrlf=true` issue, not a dependency or pilot failure. |
| Same regression set with the six named CLI-binding cases deselected | 0 | 99 passed, 6 deselected. |
| `.venv\Scripts\ruff.exe check backend` | 0 | All checks passed. |
| `git diff --check` | 0 | No whitespace errors. |
| SHA-256 before/after and ignored-path checks | 0 | Source remained `b19d39f5…c5b040`; normalized mapping M remained `a816260a…9093e57`; pilot path absent after cleanup. |

No holdout labels, full model fit, candidate comparison, validation selection or metric evaluation occurred. T029 protocol freeze is the next task; this evidence supplies measured resource ceilings and explicitly distinguishes estimates from measurements.
