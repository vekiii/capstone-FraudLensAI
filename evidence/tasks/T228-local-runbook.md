# Local T228 training handout

Run from the repository root in PowerShell. **Current status: preparation checks can run; real training cannot yet start.** The T203 fitting restriction, incomplete provenance, missing approved full FR-021 protocol, and missing verified full-source feature/partition publication are active stop conditions. The current code contains model fit functions, but no gated full-source T228 runner. Calling those functions directly on the local dataset would bypass the required checks.

## 1. Set up the locked local environment

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.cache/uv')
uv sync --locked --group ml
$env:PYTHONPATH = 'backend/src'
```

The T222 lock records CPython 3.14.10, LightGBM 4.7.0 and scikit-learn 1.9.1. `uv sync` installs dependencies; it does not train a model.

## 2. Run the available no-fit checks

```powershell
uv run --locked --group ml python evidence/tasks/T219-verify-decision.py
uv run --locked --group ml pytest backend/tests/unit/test_training_protocol.py backend/tests/unit/test_training_boundaries.py backend/tests/unit/test_model_candidates.py backend/tests/unit/test_evaluation.py backend/tests/unit/test_artifacts.py -q --basetemp .cache/t228-local-check -o 'cache_dir=.cache/t228-local-check-cache'
```

The first command verifies the original restricted aggregate audit and human showcase decision. The second checks code on invented inputs; its results are **not model evaluation**. It does not establish fitting permission or source provenance.

## 3. Check the current local data status

```powershell
$m = Get-Content data/processed/t210-hi-small-b19d39f5/manifest.json -Raw | ConvertFrom-Json
[pscustomobject]@{
  accepted_count = $m.accepted_count
  provenance_complete = $m.provenance_complete
  temporal_partitioning_complete = $m.temporal_partitioning_complete
  source_release = $m.source_release
  scoreable_count = $m.scoreable_count
} | Format-List
```

Expected on this workstation: `accepted_count=5078345`, provenance and temporal partitioning `False`, release and scoreable count null. These are observed gaps, not fields to edit in the T210 manifest.

## 4. Conditions for an actual training run

Before fitting, resolve the upstream source revision/acquisition and fitting permission through a reviewed decision without rewriting the T210 history. Publish and verify the full-source chronological feature/partition output within measured resource ceilings. Complete T219's canonical protocol with all frozen identities and fields, obtain its independently recorded approval hash, and pass `verify_prefit_protocol` against freshly measured source/snapshot/boundary/partition/audit identities. A T228 runner must then bind those checks to the fit entry point and enforce the T221 3,600-second per-fit and 28,800-second eight-fit ceilings, memory/disk preflight, and train-only labels/preprocessing.

The runnable **real training command does not exist yet**. Once those conditions and a gated runner are implemented, run the eight LightGBM configurations in the declared order, evaluate **validation only** with [evaluation.py](../../backend/src/fraudlens/training/evaluation.py), retain per-candidate timings and metrics under ignored `data/eval/`, and record the selected threshold/model and limitations in [T228 evidence](T228.md). Do not use test or showcase labels for this comparison. T229 freezes predictions afterward; T230 requires separate authorization before test-label evaluation.
