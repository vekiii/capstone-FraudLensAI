# Local T228 training and evaluation runbook

Run commands from the repository root in PowerShell. The source bytes and generated feature/label files live only on the original workstation unless the team separately transfers them. `data/eval/` and `data/processed/` are Git-ignored.

## Current inputs and status

- Exact local CSV SHA-256: `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`; upstream release, acquisition date and declared source timezone remain unknown.
- Research feature manifest: `63873b79a1ff875c5702a62c40c7a9cb3faef6bb7e0bb658739abac35274c05f`.
- Train/validation labels only: `5aee2e1d5f4f2ca7329fcc7b5b1ca0c808c4e8e39e84559e76a0d3e1a6add12c`.
- FR-021 candidate: `specs/002-data-and-risk-scoring/t219-training-protocol.ibm-60-20-20.candidate.json`; canonical SHA-256 without trailing newline: `f34c51bcaeec63072a29eceae987b85ff3e8d88ac106fe51e9fc16355d5b3f5f` (check the current T219 evidence if code changes regenerate it). It is a review candidate, not approved or frozen.
- No model training has been run. Current lightweight checks do not report model performance.

## Set up the locked Windows environment

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.cache/uv')
$env:PYTHONPATH = 'backend/src'
uv sync --locked --group dev --group ml
uv run --locked --group ml python --version
uv run --locked --group ml python -c "import lightgbm, sklearn; print('lightgbm', lightgbm.__version__, 'scikit-learn', sklearn.__version__)"
```

The project lock targets Python 3.14.10, LightGBM 4.7.0 and scikit-learn 1.9.1. The local runner also records NumPy, `uv.lock` SHA-256, Git revision/dirty state, configured thread count, peak Windows working set, and fit duration.

## Review and verify before training

```powershell
uv run --locked --group ml python evidence/tasks/T219-ibm-candidate.py
uv run --locked --group ml python -m fraudlens.training.local_run --help
uv run --locked --group dev --group ml pytest backend/tests/unit/test_research_split.py backend/tests/unit/test_research_labels.py backend/tests/unit/test_research_protocol.py backend/tests/unit/test_local_run.py backend/tests/unit/test_lightgbm_matrices.py backend/tests/unit/test_evaluation.py -q --basetemp .cache/pytest-ibm-training
uv run --locked --group dev --group ml ruff check backend/src backend/tests evidence/tasks/T219-ibm-split.py evidence/tasks/T219-ibm-labels.py evidence/tasks/T219-ibm-candidate.py evidence/tasks/T230-evaluate.py
```

The candidate-builder recomputes whole-day assignment and validates manifest hashes. It does not fit a model. Tests use synthetic fixtures or mocked estimators.

## Run the LightGBM experiment yourself

Review the exact candidate and digest first. If you decide to use that protocol, run all eight frozen LightGBM configurations using train-only preprocessing and class weighting, validation-based early stopping/threshold/model selection, and the configurable thread setting (default 4):

```powershell
$protocol = 'specs/002-data-and-risk-scoring/t219-training-protocol.ibm-60-20-20.candidate.json'
$protocolSha = 'f34c51bcaeec63072a29eceae987b85ff3e8d88ac106fe51e9fc16355d5b3f5f'
uv run --locked --group ml python -m fraudlens.training.local_run `
  --features data/processed/t219-ibm-day-60-20-20-v1 `
  --labels data/processed/t219-ibm-day-60-20-20-labels-v1 `
  --protocol $protocol --protocol-sha256 $protocolSha `
  --output data/eval/ibm-day-lightgbm-001 --n-jobs 4
```

This is the only full-fit command. It will refuse mismatched candidate/input hashes, bad label alignment, single-class training, or validation without positives. It writes `experiment.json`, validation metrics and scores, a native LightGBM text model plus manifest, and test predictions without test labels. It does not automatically read test labels or create test metrics. Estimate runtime on your PC before choosing `--n-jobs`; fit runtime and memory have not been measured yet. Output directory must be new.

## Evaluate test after freezing scores

Do not open test labels during model selection. When you intentionally authorize the one-time final test evaluation, the evaluator requires both the saved prediction hash and an explicit flag; it checks that the hash matches the experiment manifest before scanning labels. It writes aggregate metrics only and does not publish record-level test labels.

```powershell
$run = Get-Content data/eval/ibm-day-lightgbm-001/experiment.json -Raw | ConvertFrom-Json
uv run --locked --group ml python evidence/tasks/T230-evaluate.py `
  --predictions data/eval/ibm-day-lightgbm-001/test-predictions-sealed.csv `
  --prediction-sha256 $run.prediction_sha256.test `
  --authorize-test-evaluation I_AUTHORIZE `
  --output data/eval/ibm-day-lightgbm-001/test-evaluation.json
```

Only run that command after the predictions are frozen and the team explicitly authorizes test evaluation. Showcase labels remain unavailable. The reported test threshold comes from validation and cannot be changed using test outcomes.

## Known limits

The primary experiment covers the 1,884,981 scoreable development rows, not the warm-up context rows or later showcase. This preserves the project's existing showcase boundary and label restrictions. Only five UTC dates are available within scoreable development, so whole-day constraints yield 62.03/25.61/12.36 shares, not a close exact 60/20/20 split. Actual class counts are listed in [T219 evidence](T219.md). This exact local source's publisher revision and timezone remain unknown; UTC is the existing project assumption, not a verified publisher statement. No fit-resource numbers or model-quality results exist until you run the command.
