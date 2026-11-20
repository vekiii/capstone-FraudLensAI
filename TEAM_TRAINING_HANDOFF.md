# FraudLens AI: team handoff for model training

**Prepared:** 2026-11-20, Europe/Budapest. **Branch:** `feature/002-clean-start`. **Baseline before this handoff:** `d91be2e`. This document describes the repository as checked on this workstation. A teammate must verify their own checkout and local data before claiming the same state.

## Read this first

**There is no runnable full-data training command yet.** The model functions and validation arithmetic exist, but T228 experiments have not run. The user confirmed team approval to fit the exact local CSV copy despite unknown upstream release/date; the [recorded decision](prompts/development/002-T228-input-clarification.md) is checked through a narrow prefit exception. T219 has no approved complete FR-021 training-protocol hash; verified full-source temporal features/partitions and a gated T228 runner are missing. Calling `fit_lightgbm_grid()` directly on local source data would bypass required checks. Do not mark T228 complete or report synthetic test results as model performance.

Read [AGENTS.md](AGENTS.md), [next_work.md](next_work.md), [Feature 002 tasks](specs/002-data-and-risk-scoring/tasks.md), [protocol](specs/002-data-and-risk-scoring/protocol.md), [T228 readiness evidence](evidence/tasks/T228.md), and the [local runbook](evidence/tasks/T228-local-runbook.md) before changing code or data. The current user request determines scope; the handoff does not authorize a fit.

## What is built

| Area | Current state | Main references |
|---|---|---|
| Foundation app | FastAPI plus vanilla TypeScript/Vite fixture case UI. Fixture mode needs no dataset or trained model. | [README](README.md), [backend app](backend/src/fraudlens/main.py) |
| Source and canonical data | One local IBM synthetic HI-Small CSV was hashed, parsed and snapshotted: 5,078,345 accepted rows, zero rejected. Source release and acquisition date are unknown. Generated data is ignored by Git. | [Data card](data/README.md), [T210](evidence/tasks/T210.md) |
| Chronology and labels | Frozen UTC/warm-up/split rules, count-only boundaries, five scoreable partition-ID hashes and a restricted aggregate audit. The original showcase prevalence tolerance failed; a recorded human decision keeps that split for local demo preparation and treats showcase prevalence as diagnostic. | [Protocol](specs/002-data-and-risk-scoring/protocol.md), [T218](evidence/tasks/T218.md), [T219](evidence/tasks/T219.md) |
| Features and preparation | Eleven `hi-small-temporal-v1` fields and strict-prior 24-hour feature kernel. A new synthetic-scale publisher strips labels before parsing, sorts non-label rows and verifies partition hashes; full-source publication and train/validation label access are still missing. In-memory training preparation learns categories from train only and keeps test/showcase labels sealed. | [features.py](backend/src/fraudlens/data/features.py), [training_input.py](backend/src/fraudlens/data/training_input.py), [boundaries.py](backend/src/fraudlens/training/boundaries.py) |
| Candidate models | Prevalence constant, weighted depth-5/min-leaf-500 tree, weighted L2 logistic, eight LightGBM configurations and five HistGradientBoosting comparisons are coded. Their focused tests are synthetic/mocked; no full-data fit has run. | [baselines.py](backend/src/fraudlens/training/baselines.py), [candidates.py](backend/src/fraudlens/training/candidates.py), [T221 choices](specs/002-data-and-risk-scoring/t221-model-choices.json) |
| Validation and artifacts | Fixed-score validation metrics, positive-class F1 threshold/ranking and a native LightGBM text artifact integrity boundary are coded. No real validation results or model artifact exist. | [evaluation.py](backend/src/fraudlens/training/evaluation.py), [artifacts.py](backend/src/fraudlens/scoring/artifacts.py), [T226](evidence/tasks/T226.md), [T227](evidence/tasks/T227.md) |

The last no-fit focused check for the T228 readiness review passed **114 tests, with one Windows symlink-permission skip**. The original aggregate-audit/human-decision hash check passed. Neither result measures model quality. [T228 evidence](evidence/tasks/T228.md) gives exact commands and the initial direct-script `PYTHONPATH` correction.

## Transfer the checkout and data correctly

Before this document was written, `git status` was clean, but this branch had **nine local commits ahead of** `origin/feature/002-clean-start` (`9292c1f` through `d91be2e`). A documentation commit adds to that count. A fresh clone of the remote branch will **not** contain those commits until the owner pushes them or transfers an approved Git bundle. The owner can review `git log --oneline origin/feature/002-clean-start..HEAD` and `git status --short --branch` first. If the team approves publishing this branch, the owner can run `git push origin feature/002-clean-start`; no push was performed as part of this handoff.

`data/raw/`, `data/processed/`, `data/artifacts/` and `data/eval/` are ignored. A Git clone does not include the local CSV, 3 GB canonical JSONL, boundary/audit reports, or any future model/evaluation output. Obtain source bytes through the team's authorized channel and verify **both** 475,664,283 bytes and SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040` before using them. The selected upstream release/date and the Kaggle listing terms were not established; do not assume permission to redistribute the local copy. Recreate or transfer processed outputs only under a reviewed data-sharing decision, then verify their committed hash identities in the protocol. Never commit source rows, labels, large outputs or secrets.

## On a teammate's Windows machine: setup and safe checks

Use PowerShell from the repository root. Install Git, `uv`, Python 3.14 and Node 24/npm if the fixture UI is needed. The ML lock was checked with CPython **3.14.10**, LightGBM **4.7.0** and scikit-learn **1.9.1** on the original workstation; another machine must record its actual versions.

```powershell
git status --short --branch
git log -1 --oneline
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.cache/uv')
uv sync --locked --group dev --group ml
$env:PYTHONPATH = 'backend/src'
uv run --locked --group ml python evidence/tasks/T219-verify-decision.py
uv run --locked --group dev --group ml pytest backend/tests/unit/test_training_protocol.py backend/tests/unit/test_training_boundaries.py backend/tests/unit/test_model_candidates.py backend/tests/unit/test_evaluation.py backend/tests/unit/test_artifacts.py -q --basetemp .cache/team-handoff-pytest -o 'cache_dir=.cache/team-handoff-pytest-cache'
uv run --locked --group dev --group ml ruff check backend/src backend/tests
```

The T219 decision script needs its ignored local aggregate report; on a clean clone without that report, it will fail because the input is absent. That is a missing local input, not permission to fabricate one. The focused tests use synthetic values and mocks and do not run a real-data fit. Use a fresh workspace-local `--basetemp` path for each repeat because pytest may remove its old temporary directory. Record exact commands, outcomes and warnings in the new machine's evidence; do not copy the original workstation's success claim.

To inspect a local T210 manifest **without opening record labels**:

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

On the original workstation this showed `5078345`, `False`, `False`, null and null. Those fields describe the historical T210 snapshot; do not edit them to pass a gate. If the teammate only wants to run the fixture app, follow [README.md](README.md); its startup is independent of training.

## Steps required before a real T228 training command exists

1. **Preserve the exact-copy fitting decision.** The user confirmed team approval for fitting source SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040` despite unknown upstream revision/acquisition. Keep its recorded decision bytes and hash bound in the final protocol. Preserve the original T210 manifest and audit facts; do not label unknown provenance as known.
2. **Finish T210/T219 preparation.** Build a bounded, reproducible chronological full-source feature/partition publication from the verified snapshot. The small `training_input.py` core has a default 10,000-row ceiling and is not full-source capacity evidence. Check counts and five frozen scoreable-ID hashes. Measure resource use and keep label access separated. Complete a canonical FR-021 protocol containing the source/snapshot/boundary/audit/partition hashes, exact feature/partition/model/threshold/resource/label rules and showcase role. Independently record its approved SHA-256. `t221-model-choices.json` SHA-256 `3ee00698879c428a6a4ca46bff6564da6e68c48363daf0ba9b5dba4da3b59f5e` is **only the model-choice digest**.
3. **Implement and check the T228 runner.** It must call `verify_prefit_protocol()` with independently measured inputs **before** any `fit`, refuse missing/mismatched approval or provenance, load only train/validation labels, use train-fitted preprocessing, verify feature order and partition identity, and enforce the frozen runtime/memory/disk ceilings. Add RED then GREEN checks for the gating and output boundary. It must emit generated results only to ignored `data/eval/` and record commands, versions, timings, actual model comparisons, limitations and review in [T228 evidence](evidence/tasks/T228.md).
4. **Run the approved current phase.** CPU only; seed 42; eight LightGBM combinations of `num_leaves={31,63}`, `learning_rate={0.05,0.1}`, `min_child_samples={50,200}`, at most 1,000 estimators and 50-round validation log-loss early stopping. Use train negative/positive ratio for positive weight; no downsampling. The declared ceilings are 3,600 seconds per fit, 28,800 seconds for eight fits, 8 GiB peak working set, at least 20 GiB free disk before training and at least 10 GiB afterward. Measure physical cores and log `n_jobs=max(1, physical_core_count-1)`. Stop and record a limit breach.
5. **Select using validation only.** Choose each threshold by positive-class F1 over distinct scores; ties prefer higher precision, then higher threshold. Rank LightGBM candidates by validation F1, Average Precision, Precision@20, then the frozen simplicity/order tie rules in [protocol.md](specs/002-data-and-risk-scoring/protocol.md). Report denominators, PR-AUC/AP, ROC AUC, Brier, confusion and daily unsuppressed alert counts. Do not use test/showcase record labels, adjust frozen features from validation results, or activate the later cross-family rule without its separate reviewed decision.
6. **Freeze and evaluate later.** T229 freezes model/preprocessing/threshold and development-test predictions without reading test labels. T230 test-label evaluation needs **separate explicit authorization**. Showcase is for a local demo; its recorded post-audit exception means it is not an unbiased performance holdout. T233/T234 later connect a verified local artifact to the API; fixture mode remains independent.

The eventual local command must be supplied by the **implemented, reviewed runner** and recorded in T228 evidence. Do not substitute a direct Python call to the candidate functions or a guessed script name. Plan for an eight-fit upper bound of eight CPU fit-hours **plus** feature preparation, evaluation and integration. Actual time on the teammate's machine is unknown until preflight and measurement.

## How to use Codex on the teammate's machine

Open the transferred checkout as Codex's workspace, with the intended branch checked out and the required local data available only through approved means. Codex uses the same local files and shell as its workspace. Give it this initial task:

> Read AGENTS.md, next_work.md, TEAM_TRAINING_HANDOFF.md, Feature 002 spec/plan/tasks/protocol, and T210/T219/T221/T228 evidence. Verify the checkout and local data identities and the recorded exact-copy fitting decision. Finish full-source feature publication and the complete FR-021 protocol with an independently approved hash, then implement a gated T228 runner with RED/GREEN checks. Keep T228 open and do not fit or read test/showcase record labels while any gate is incomplete. Record exact commands, observed outcomes and remaining blockers in evidence and update next_work.md. Do not invent source provenance.

Once the team has actually approved and recorded the full protocol hash, the full-source output is verified, and the gated runner exists, give Codex a separate execution request:

> Re-read AGENTS.md and next_work.md. Verify the approved FR-021 protocol hash against independently measured source/snapshot/boundary/partition/audit identities and confirm fitting permission, full-source feature publication, hardware/disk preflight and T221 ceilings. If any check fails, stop before fit and report the specific mismatch. If all pass, run only the current eight LightGBM train/validation candidates through the gated T228 runner, monitor limits, write generated output under ignored data/eval/, and record actual metrics, versions, timings, limitations and human review status in T228 evidence. Do not access test/showcase record labels or claim T228 complete until all required work is done.

The exact-copy fitting decision is recorded; the complete FR-021 protocol approval hash and full-source engineering gates remain outstanding. Codex may implement, inspect and run local commands after those gates pass. Long fits should be monitored on the local machine; a stopped Codex session is not evidence that training completed. Keep the generated report and artifact hashes so another team member can reproduce or review the run.

## Handoff references

- [Constitution](.specify/memory/constitution.md), [approved product context](original_idea.md), [Feature 002 specification](specs/002-data-and-risk-scoring/spec.md), [plan](specs/002-data-and-risk-scoring/plan.md), [tasks](specs/002-data-and-risk-scoring/tasks.md)
- [T203 local-copy scope](evidence/tasks/T203.md), [T210 ingestion](evidence/tasks/T210.md), [T218 audit and decision](evidence/tasks/T218.md), [T219 protocol gate](evidence/tasks/T219.md), [T221 model choices](evidence/tasks/T221.md), [T222 locked ML compatibility](evidence/tasks/T222.md)
- [T223 preprocessing/baselines](evidence/tasks/T223.md), [T224 candidates](evidence/tasks/T224.md), [T226 validation](evidence/tasks/T226.md), [T227 artifacts](evidence/tasks/T227.md), [T228 readiness](evidence/tasks/T228.md)
