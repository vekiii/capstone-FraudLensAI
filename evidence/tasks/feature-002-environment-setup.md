# Feature 002 Windows environment setup — 2026-11-15

Original request: [development environment setup prompt](../../prompts/development/002-environment-setup-2026-11-15.md). Scope was the Windows development environment and data-free checks; no original transaction database or model artifact was created, loaded, or changed.

## Version decision and starting state

`pyproject.toml` requires Python `>=3.14,<3.15`, `.python-version` says `3.14`, and the project uses `uv.lock` for runtime and dev dependencies. There is no repository `requirements.txt`, `setup.cfg`, Dockerfile, or CI workflow defining a different Python version. Windows `py -0p` found system Python 3.13.3; an existing `.venv` runs Python 3.14.10. Python 3.13.3 is outside the project range, so **3.14.10** was selected for a new isolated environment. No interpreter installation was needed in this checkout.

The boosted candidate is scikit-learn's `HistGradientBoostingClassifier` in [the comparison runner](../../backend/src/fraudlens/compare_boosted_phase5.py). The saved artifact metadata described in the handoff pins NumPy 2.5.4, scikit-learn 1.9.1 and joblib 1.6.0. The installed distributions declare Python minimums of 3.12, 3.11 and 3.10 respectively; pandas 3.1.1 declares 3.11. They accept Python 3.14.10, and the locked model-library versions match the handoff. Elena's run reported Python 3.14.7. **Actual saved-model reload and prediction parity remain unverified** because its manifest and binary are unavailable; the Python patch difference is recorded, not assumed harmless to the artifact.

The existing `.venv` was preserved. The new environment is `.cache/feature-002-env/`, covered by the repository's `.gitignore` rule `.cache/`; `git check-ignore -v .cache/feature-002-env/pyvenv.cfg` confirmed this.

## Exact setup and activation commands (PowerShell)

The following commands were executed from the repository root:

```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
$env:UV_PROJECT_ENVIRONMENT = Join-Path $PWD '.cache/feature-002-env'
$py314 = (Resolve-Path '.venv/Scripts/python.exe').Path
uv sync --locked --group dev --python $py314
uv pip install --python .cache/feature-002-env/Scripts/python.exe --no-deps 'pandas==3.1.1' 'pip==26.3'
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
& .\.cache\feature-002-env\Scripts\Activate.ps1
python --version
python -m pip check
```

The locked sync resolved 48 packages and installed 47 into the new environment, exit 0. The optional pandas and pip install added two packages, exit 0, with `--no-deps` so it did not replace locked NumPy, scikit-learn, SciPy or joblib versions. pandas and pip are **not** required by `pyproject.toml` or `uv.lock`; pandas is requested for this development environment, while project scoring reads CSV/SQLite without it. The Python used by T065/T066 must be the selected environment's executable. A later `uv sync --locked` may prune these two optional packages; rerun the explicit pinned optional install afterward if needed.

If a clean Windows machine lacks Python 3.14, install the selected patch release with `uv python install 3.14.10`, then use `uv sync --locked --group dev --python 3.14.10` with the same `UV_CACHE_DIR` and `UV_PROJECT_ENVIRONMENT` values. This fallback was **documented, not executed** here. Activation policy was changed only for the PowerShell process, not for the user or system. Explicitly invoking `.\.cache\feature-002-env\Scripts\python.exe` also works without activation.

## Installed versions and checks

| Component/check | Observed result |
|---|---|
| Python before / after | Existing `.venv`: 3.14.10; new `.cache/feature-002-env`: 3.14.10. System default: 3.13.3. |
| uv / pip | uv 0.13.8; optional pip 26.3. |
| Project model libraries | NumPy 2.5.4; SciPy 1.18.1; scikit-learn 1.9.1; joblib 1.6.0. |
| Optional requested library | pandas 3.1.1 imported successfully. |
| Dependency consistency | `.\.cache\feature-002-env\Scripts\python.exe -m pip check`: exit 0, `No broken requirements found.` |
| Boosted import | `from sklearn.ensemble import HistGradientBoostingClassifier`: passed; the comparison, training and benchmark modules imported after the Windows resource fix. |
| SQLite | Python `sqlite3` imported; SQLite 3.53.1; in-memory table creation, insert of `7`, and select returned `7`. |
| Environment isolation | `VIRTUAL_ENV` pointed to `.cache/feature-002-env`; `python` resolved to that environment after activation. |

Python's built-in `sqlite3` is sufficient for the T066 run-status query. The external `sqlite3` executable is absent, but the [quickstart](../../specs/002-data-and-risk-scoring/quickstart.md) now includes a PowerShell command that opens the actual peer run store with `mode=ro` and `PRAGMA query_only=ON`, then runs the same parameterized status query. This does not create a database when the expected store is absent. The external CLI was therefore not installed.

## Windows portability repair and tests

The first data-free pytest attempt could not collect `test_boosted_validation.py`: `ModuleNotFoundError: No module named 'resource'`. Three project modules imported Unix-only `resource`. [process_metrics.py](../../backend/src/fraudlens/process_metrics.py) now reads Windows peak working-set bytes through `GetProcessMemoryInfo` while preserving the existing Unix `resource.getrusage` behavior. The comparison runner, training script and benchmark use the helper for their existing resource measurements; model fitting, feature inputs, thresholds, predictions and evaluation arithmetic were not changed. On this machine the helper returned a positive integer (176,836,608 bytes) and all three modules imported. Ruff passed for all four touched Python files.

An initial broader smoke attempt against artifact-dependent and temporary-file tests produced **4 failed, 10 passed, 12 errors**; a representative boosted failure required the missing `artifacts/feature-002-boosted-validation-20261114/manifest.json`, and pytest's default cache/temp location produced Windows file errors. No project-model result can be inferred from that attempt. The repeat used an ignored temp path and excluded tests requiring the absent artifact:

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/002-data-and-risk-scoring'
$env:PYTHONPATH = 'backend/src'
$env:TEMP = Join-Path $PWD '.cache/feature002-temp'
$env:TMP = $env:TEMP
.\.cache\feature-002-env\Scripts\python.exe -m pytest backend/tests/unit/test_boosted_validation.py backend/tests/unit/test_explanations.py backend/tests/unit/test_model_selection.py backend/tests/unit/test_evaluation_metrics.py -q --tb=line -p no:cacheprovider --basetemp .cache/feature002-pytest-smoke-20261115b
```

Exit **0, 21 passed** in 6.99 seconds. A further synthetic store/loader run with the same environment and a separate ignored `--basetemp` gave **11 passed, 1 failed**. The remaining failure is `test_escaped_path_upload_and_incompatible_manifest_reject`: Windows returned `WinError 1314` when the test tried to create a directory symlink without the required privilege. The test was not skipped or weakened. Its other 11 checks, including run publication tests, passed. Full regression and artifact-dependent tests were not claimed as passing. No IBM source or model output was used in these checks.

## Errors, fixes, and remaining blockers

- An initial `uv python list --only-installed` using uv's default cache failed to acquire a user-profile cache lock. Setting `UV_CACHE_DIR` to the repository's ignored `.cache/uv` resolved package operations.
- The package-index connection failed in the ordinary sandbox, and offline resolution showed pandas was not cached. Approved network access resolved pandas 3.1.1 and pip 26.3 and installed them in the isolated environment.
- `python -m pip` initially failed because uv environments do not include pip by default; the optional pinned pip install supplied it for the requested `pip check`.
- Windows lacks the Unix `resource` module; the process-memory helper repair above removed the import failure without changing model behavior.
- One existing symlink security test requires Windows symlink privilege; it remains failed on this host. This is separate from the environment's package and SQLite checks.

**Environment status: READY for local, data-free Feature 002 work.** T065 and T066 remain **BLOCKED**: the original history-v1 SQLite database, exact boosted model/preprocessing binary and manifest/metadata, explanation JSON, frozen predictions/reports, and correct pinned protocol/time-policy are still unavailable or mismatched. The project protocol on disk previously hashed to `e8073b9c664f241418566eb87b4a3797e9798aeb2d306d035bbd2c8676e38074`, while T066 requires `01fff67d44895b5a1aa6de6dfbb6c6c107f01c041ba7c972bf42210e2b316068`. Neither task was resumed; the original candidate artifact was not loaded, refitted, scored, or deployed. The data-free unit tests did fit small synthetic candidates.

One concrete next step: obtain the authorized same-hash database, artifacts and protocol from Elena, verify their hashes and compatibility, then resume the blocked T065/T066 procedures in the isolated environment.
