# T228 Stage C Mac receipt — 2026-11-20

## Scope and ownership

This record is Codex's receiving-side setup and no-fit review on the colleague's Mac. The earlier T219/T228 preparation and ZIP publication remain the original contributor's historical evidence. The user did not approve the FR-021 candidate, model fitting, test-label access, T230 evaluation, or task completion. No commit or push was performed.

## Repository and transfer

- New checkout: `/Users/ladylazarus/Desktop/FraudLensAI-StageC`; branch `feature/002-clean-start`; `origin` HEAD and checkout both `aa1accac0ff90f2eb370618be15f145b3cc6bf2b`. No divergence from the supplied remote commit. Initial Git status clean.
- ZIP `/Users/ladylazarus/Downloads/T228-colleague-transfer-2026-11-20.zip`: SHA-256 `a3f36444a829f44cf990a43dcdc2d70bfe906ee85327186449dfa31e32595687`, as expected; `unzip -tq` passed. Extracted separately under this Codex task's `work/transfer/`, outside Git.
- Copied only `t219-ibm-day-60-20-20-v1` and `t219-ibm-day-60-20-20-labels-v1` to `data/processed/`; seven copied files matched the extracted bytes. Both destinations were absent before copying. `.gitignore:38` ignores both directories.
- Feature manifest SHA-256 `63873b79a1ff875c5702a62c40c7a9cb3faef6bb7e0bb658739abac35274c05f`: passed. Label manifest SHA-256 `5aee2e1d5f4f2ca7329fcc7b5b1ca0c808c4e8e39e84559e76a0d3e1a6add12c`: passed. All three feature JSONL and both train/validation label JSONL hashes matched their manifests. No transaction rows or individual label values were opened for this check.
- The protocol candidate's project-defined canonical JSON SHA-256 is `f34c51bcaeec63072a29eceae987b85ff3e8d88ac106fe51e9fc16355d5b3f5f`; raw file SHA-256 is `4793819cc7df65ea37df90659149d63de6352ca5a70b23cbb50a192e62f300bf`. All 16 `reproducibility.implementation_file_sha256` values matched checkout files. This is integrity verification, not approval.

## Mac and locked environment

- MacBook Pro `Mac17,8`, Apple M5 Pro, arm64, 24 GB RAM; macOS 27.0.1 (build 26A434); approximately 729 GiB free on the Desktop volume when checked.
- Git 2.55.0; uv 0.12.15. `uv sync --locked --group dev --group ml` first failed because the sandbox denied the default home cache. The same command with `UV_CACHE_DIR` in this task's writable `work/` then succeeded and installed 47 locked packages. No `uv.lock` change; SHA-256 `b9b1c52056c3706fd21fc1fefa9934fc1c1c8c09dd2b0f465d8d49ad25cc1ffe`.
- Installed runtime: Python 3.14.7, LightGBM 4.7.0, scikit-learn 1.9.1, NumPy 2.5.5. Initial LightGBM import failed due to missing `@rpath/libomp.dylib`; `brew install libomp` installed 23.1.6, and the import then succeeded. `uv python install 3.14.10` returned `No download found for request: cpython-3.14.10-macos-aarch64-none`.
- Important compatibility blocker: `.python-version` is `3.14`, so uv selected available 3.14.7, but the candidate records 3.14.10 and `backend/src/fraudlens/scoring/artifacts.py` requires exactly 3.14.10 in `_runtime_versions()` before writing/loading a model artifact. A full fit on this runtime could reach artifact publication and then fail. No fit was attempted.

## No-fit checks

- Inspected the six test files before execution; `test_lightgbm_matrices.py` uses a stub for fitting and the others use small synthetic fixtures or fixed scores.
- `PYTHONPATH=backend/src .venv/bin/python -m fraudlens.training.local_run --help`: passed.
- `PYTHONPATH=backend/src .venv/bin/pytest backend/tests/unit/test_research_split.py backend/tests/unit/test_research_labels.py backend/tests/unit/test_research_protocol.py backend/tests/unit/test_local_run.py backend/tests/unit/test_lightgbm_matrices.py backend/tests/unit/test_evaluation.py -q --basetemp <task work/pytest-stagec-20261120>`: 43 passed in 1.61 s.
- Ruff initially failed only because the sandbox denied its default checkout cache. With `RUFF_CACHE_DIR` in task `work/`, `ruff check backend/src backend/tests evidence/tasks/T219-ibm-split.py evidence/tasks/T219-ibm-labels.py evidence/tasks/T219-ibm-candidate.py evidence/tasks/T230-evaluate.py`: passed.
- No functional test or lint failure remained. The candidate-builder `T219-ibm-candidate.py` was intentionally not run because it regenerates the candidate and needs historical inputs absent from the transfer. The full training command, T230 evaluator, full backend suite and any real-data row/label scan were not run.

## Protocol/runner review and missing inputs

- New v2 research split uses complete UTC days within 1,884,981 scoreable development rows: train 1,169,261 (62.03%), validation 482,650 (25.61%), test 233,070 (12.36%). Warm-up and showcase are excluded. The older 70/15/15 split and 3m source boundary are historical context, not the current research partitions.
- Preprocessing vocabulary and positive weight are train-only; eight LightGBM settings cross 31/63 leaves, 0.05/0.1 learning rate and 50/200 minimum child samples. Each has up to 1,000 rounds, 50-round validation binary-log-loss early stopping. Validation positive-class F1 selects thresholds and ranks current-phase candidates, with AP and precision-at-20 tie breaks. This optimizes an uncapped threshold objective; precision/recall-at-20/50/100 and daily alert counts are reported but do not impose an analyst capacity limit.
- The runner reads train/validation labels, creates test scores without test labels, and records hashes/manifest metadata. `T230-evaluate.py` is separately gated. Artifact loader validates an independently trusted manifest digest, source/protocol identities, feature/vocabulary order, runtime, path containment and model hash before loading.
- Fit protocol declares 8 GiB peak memory, 20 GiB initial and 10 GiB ending free disk, and 3,600 s per candidate / 28,800 s current phase / 54,000 s all fits. On macOS `_peak_working_set()` returns `None`; the runner records duration only after grid fitting and has no visible enforcement of the declared memory/time/disk limits. This is a prefit review issue, not a measured failure.
- Present transfer supports archive, manifest, file-hash, candidate/code-hash, CLI, synthetic tests and lint checks. It lacks the original T210 snapshot/raw source, T218 aggregate audit report and other historical local inputs; full `T219-ibm-candidate.py` regeneration/independent source-to-feature reproduction cannot run from this package. The transferred train/validation labels and feature files are sufficient inputs for a later approved runner attempt, subject to the runtime/resource issues and explicit FR-021 approval.

## Status and next step

FR-021 candidate remains pending explicit human approval; T228–T230 remain open. No model fit, test/showcase record-label access, T230 evaluation, commit or push occurred. Next: resolve the exact Python 3.14.10 runtime mismatch and macOS resource-gate behavior for review, then obtain written approval of the canonical protocol hash before any fit.
