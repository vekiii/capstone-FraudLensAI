# FraudLens AI: team handoff for model training

**Updated:** 2026-11-20, Europe/Budapest. **Branch:** `feature/002-clean-start`. This document describes the repository as checked on this workstation. A teammate must verify their own checkout and local data before claiming the same state.

## Read this first

**The local LightGBM runner is implemented; no model fit has run.** The IBM-style, whole-UTC-day research partition and restricted train/validation labels are generated under ignored `data/processed/`. The new candidate [t219-training-protocol.ibm-60-20-20.candidate.json](specs/002-data-and-risk-scoring/t219-training-protocol.ibm-60-20-20.candidate.json) has canonical SHA-256 `f34c51bcaeec63072a29eceae987b85ff3e8d88ac106fe51e9fc16355d5b3f5f`; it remains pending review and is not frozen. The original T218 boundary and 70/15/15 data remain historical. The exact upstream source release/date/timezone are still unknown. No fit, test-label read or test metrics occurred. See the [T228 runbook](evidence/tasks/T228-local-runbook.md) for exact commands and the explicitly gated final-test evaluation.

Read [AGENTS.md](AGENTS.md), [next_work.md](next_work.md), [Feature 002 tasks](specs/002-data-and-risk-scoring/tasks.md), [protocol](specs/002-data-and-risk-scoring/protocol.md), [T228 readiness evidence](evidence/tasks/T228.md), and the [local runbook](evidence/tasks/T228-local-runbook.md) before changing code or data. The current user request determines scope; the handoff does not authorize a fit.

## What is built

The current research split is based on complete UTC days of scoreable development. Train, validation and test counts, proportions, class counts and cutoffs are summarized in the latest [handoff](next_work.md) and [T219 evidence](evidence/tasks/T219.md). The new FR-021 candidate is distinct from the historical v1 candidate; use only the linked IBM-day candidate and hash in the local runbook.

| Area | Current state | Main references |
|---|---|---|
| Foundation app | FastAPI plus vanilla TypeScript/Vite fixture case UI. Fixture mode needs no dataset or trained model. | [README](README.md), [backend app](backend/src/fraudlens/main.py) |
| Source and canonical data | One local IBM synthetic HI-Small CSV was hashed, parsed and snapshotted: 5,078,345 accepted rows, zero rejected. Source release and acquisition date are unknown. Generated data is ignored by Git. | [Data card](data/README.md), [T210](evidence/tasks/T210.md) |
| Chronology and labels | Frozen UTC/warm-up/split rules, count-only boundaries, five scoreable partition-ID hashes and a restricted aggregate audit. The original showcase prevalence tolerance failed; a recorded human decision keeps that split for local demo preparation and treats showcase prevalence as diagnostic. | [Protocol](specs/002-data-and-risk-scoring/protocol.md), [T218](evidence/tasks/T218.md), [T219](evidence/tasks/T219.md) |
| Features and preparation | Eleven `hi-small-temporal-v1` fields and strict-prior 24-hour feature kernel. Full-source label-free publication passed with manifest SHA-256 `5ca1660eb582b68b27f58241b115eea5d69d3feb77f78f9fe46c12611b4f517a`; separate train/validation-only labels passed with manifest SHA-256 `3f1e8b49387457f4d1701060272ef23df81237aab552d43ed2bcd34e0ed8e54b`. In-memory training preparation learns categories from train only and keeps test/showcase labels sealed. | [T210 evidence](evidence/tasks/T210.md), [training_input.py](backend/src/fraudlens/data/training_input.py), [label_input.py](backend/src/fraudlens/training/label_input.py) |
| Candidate models | Prevalence constant, weighted depth-5/min-leaf-500 tree, weighted L2 logistic, eight LightGBM configurations and five HistGradientBoosting comparisons are coded. Their focused tests are synthetic/mocked; no full-data fit has run. | [baselines.py](backend/src/fraudlens/training/baselines.py), [candidates.py](backend/src/fraudlens/training/candidates.py), [T221 choices](specs/002-data-and-risk-scoring/t221-model-choices.json) |
| Validation and artifacts | Fixed-score validation metrics, positive-class F1 threshold/ranking and a native LightGBM text artifact integrity boundary are coded. No real validation results or model artifact exist. | [evaluation.py](backend/src/fraudlens/training/evaluation.py), [artifacts.py](backend/src/fraudlens/scoring/artifacts.py), [T226](evidence/tasks/T226.md), [T227](evidence/tasks/T227.md) |

The last no-fit focused check for the T228 readiness review passed **114 tests, with one Windows symlink-permission skip**. The original aggregate-audit/human-decision hash check passed. Neither result measures model quality. [T228 evidence](evidence/tasks/T228.md) gives exact commands and the initial direct-script `PYTHONPATH` correction.

## Transfer the checkout and data correctly

This branch has local commits that may be ahead of `origin/feature/002-clean-start`. A fresh clone of the remote branch will **not** contain those commits until the owner pushes them or transfers an approved Git bundle. The owner can review `git log --oneline origin/feature/002-clean-start..HEAD` and `git status --short --branch` first. No push was performed as part of this handoff.

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

## What remains before a fit

1. Review the v2 [IBM-day FR-021 candidate](specs/002-data-and-risk-scoring/t219-training-protocol.ibm-60-20-20.candidate.json) and its canonical SHA-256 in the latest [T219 evidence](evidence/tasks/T219.md). The candidate is not approved/frozen. Unknown upstream release, acquisition date and publisher timezone stay recorded as unknown.
2. Run the no-fit test/lint commands in the [T228 runbook](evidence/tasks/T228-local-runbook.md). The current workstation's latest focused check recorded there is 36 passed before the last small edits; a final recheck is still pending.
3. After review, the operator can execute the exact eight-candidate LightGBM training command in the runbook. It writes only under ignored `data/eval/`, fits preprocessing/class weight on train, selects by validation, writes native text plus JSON artifact metadata, logs actual versions/thread count/resources, exports validation metrics and test predictions, and reads no test labels. No full fit was started for this handoff.
4. Test evaluation is separate: `evidence/tasks/T230-evaluate.py` verifies the frozen prediction SHA-256 and requires `--authorize-test-evaluation I_AUTHORIZE`; it emits aggregate metrics only. Showcase record labels remain unread.
5. Report actual wall time/memory only after local execution. The eight candidate fits can take a while; no full-fit benchmark exists. `--n-jobs` is configurable (default 4), and CPU core count is logged for context without blocking the run.

## How to use Codex on a teammate's machine

Transfer the code branch and the authorized local source/prepared inputs through the team's approved channel. Git does not contain ignored source/features/labels. Re-read `AGENTS.md`, `next_work.md`, this handoff, Feature 002 artifacts and latest T219/T228 evidence. Verify the local manifests against candidate hashes before invoking the runner. Synthetic tests are not model results. Ask Codex to run the no-fit checks first; request a full fit separately when the team is ready, then inspect `experiment.json` and keep test evaluation closed until the prediction hash is frozen.

## Handoff references

- [Constitution](.specify/memory/constitution.md), [approved product context](original_idea.md), [Feature 002 specification](specs/002-data-and-risk-scoring/spec.md), [plan](specs/002-data-and-risk-scoring/plan.md), [tasks](specs/002-data-and-risk-scoring/tasks.md)
- [T203 local-copy scope](evidence/tasks/T203.md), [T210 ingestion](evidence/tasks/T210.md), [T218 audit and decision](evidence/tasks/T218.md), [T219 protocol gate](evidence/tasks/T219.md), [T221 model choices](evidence/tasks/T221.md), [T222 locked ML compatibility](evidence/tasks/T222.md)
- [T223 preprocessing/baselines](evidence/tasks/T223.md), [T224 candidates](evidence/tasks/T224.md), [T226 validation](evidence/tasks/T226.md), [T227 artifacts](evidence/tasks/T227.md), [T228 implementation and runbook](evidence/tasks/T228.md)
