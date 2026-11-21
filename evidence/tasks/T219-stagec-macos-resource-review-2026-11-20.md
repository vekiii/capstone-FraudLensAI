# T219 Stage C Mac revised FR-021 candidate — 2026-11-20

- Status: **candidate pending explicit human review**. No protocol approval or research-data fit.
- Original request: [development prompt](../../prompts/development/002-T219-stagec-macos-resource-review.md). Prior receiving-side [receipt](T228-stagec-mac-receipt-2026-11-20.md) and [resource remediation](T228-stagec-mac-resource-remediation-2026-11-20.md) were read.
- Baseline: branch `feature/002-clean-start`, HEAD `aa1accac0ff90f2eb370618be15f145b3cc6bf2b`, dirty working tree. Existing local edits were preserved; no commit or push.
- Runtime: macOS 27.0.1 arm64, project `.venv` Python 3.14.10, LightGBM 4.7.0, scikit-learn 1.9.1, NumPy 2.5.5, uv 0.12.15, libomp 23.1.6; `uv.lock` SHA-256 `b9b1c52056c3706fd21fc1fefa9934fc1c1c8c09dd2b0f465d8d49ad25cc1ffe`.

## Code review against HEAD

`git diff HEAD -- backend/src/fraudlens/training/candidates.py backend/src/fraudlens/training/local_run.py` and inspection of the new guard showed that `candidates.py` changes only the array-grid loop to call an optional `on_candidate_start(index)` before each unchanged `_fit_lightgbm` call. The `LIGHTGBM_GRID` product still has eight entries in the same order: leaves 31/63, rates 0.05/0.1, minimum child samples 50/200. The underlying fit still uses seed 42, `scale_pos_weight` from train labels only, CPU deterministic/column-wise mode, 1,000 maximum rounds, validation `binary_logloss`, and 50-round early stopping. The train-only categorical vocabulary, unknown bucket, numeric conversion, label alignment, validation threshold/metric ranking and tie rules are unchanged in `local_run.py`/`evaluation.py`. The runner reads train and validation labels only; it reads test features and writes test predictions without reading test labels. No split, feature, grid or selection rule changed.

The previous guard had a **material publication gap**: a worker could write `experiment.json` and sealed predictions, then exit nonzero or fail a final limit, leaving final-named files alongside `status.json: incomplete`. A new RED test reproduced this: `PYTHONPATH=backend/src .venv/bin/pytest backend/tests/unit/test_resource_guard.py::test_worker_failure_cannot_mark_partial_output_complete -q --basetemp work/pytest-quarantine-red` exited 1 because `experiment.json` still existed. Cleanup of final-named files made the targeted GREEN pass. Review then identified supervisor termination between worker output and cleanup as a remaining risk. The guard now works in a sibling `<output>.incomplete` directory, publishes `status.json: complete` only after worker zero exit, report, final disk and memory checks, and atomically renames that directory to the requested output path. Failure leaves no requested output directory, retains an `incomplete` status in staging and removes final-named report/prediction/artifact outputs. The read-only future consumer must use the requested final directory, not the `.incomplete` directory. `--_worker` remains an internal CLI entrypoint; direct manual invocation of that hidden flag bypasses the supervisor and is outside the reviewed command.

The atomic-publication RED case (`PYTHONPATH=backend/src .venv/bin/pytest backend/tests/unit/test_resource_guard.py::test_insufficient_initial_disk_refuses_to_start -q --basetemp work/pytest-atomic-red`) exited 1 because the expected `.incomplete/status.json` did not exist. The controlled-process GREEN run with `--basetemp work/pytest-atomic-green` passed 9 tests. A no-fit mock case additionally confirmed markers `0..7` precede the unchanged grid order. A reviewed test generated only NumPy arrays inside a subprocess and fitted one small synthetic LightGBM candidate, then wrote and read a native artifact on Python 3.14.10; `--basetemp work/pytest-synthetic-fit` passed 1 test. This is compatibility evidence, not model evaluation or a real-data fit.

## Candidate and exact hashes

New candidate: [t219-training-protocol.ibm-day-60-20-20.macos-resource-review.candidate.json](../../specs/002-data-and-risk-scoring/t219-training-protocol.ibm-day-60-20-20.macos-resource-review.candidate.json).

- **Canonical JSON SHA-256:** `90b2aaa07590f771343e30f7843078f2dbd71d26679040cdafc33a5fbe5c67cf`.
- **File-byte SHA-256:** `fcdd833474f6fdf47b1bbbabfd003e2f9081e99c3506f229977d35f9a83085f7`.
- Parent IBM-day candidate canonical SHA-256 `f34c51bcaeec63072a29eceae987b85ff3e8d88ac106fe51e9fc16355d5b3f5f`, file SHA-256 `4793819cc7df65ea37df90659149d63de6352ca5a70b23cbb50a192e62f300bf`; original file unchanged.
- Same `fraudlens-fr021-training-protocol-v2` format and `candidate_pending_explicit_human_review` status. The 60/20/20 whole-UTC-day method, all counts/boundaries, feature order, label rules, eight-candidate grid, metrics, selection and tie rules, and numeric `resource_ceilings` are byte-equivalent JSON values to the parent.

| Area | Parent candidate | Revised candidate |
| --- | --- | --- |
| Methodology and ceilings | IBM-day v2; 8 GiB, 20/10 GiB, 3,600/28,800/54,000 s | Identical values |
| Implementation binding | 16 files, older runner/candidate hashes, no guard | 18 locally rehashed files, including guard and synthetic guard test |
| Runtime and checkout | Python 3.14.10 declared; prior source-workstation revision | Observed Mac versions, `uv.lock` hash, HEAD `aa1accac…`, dirty tree |
| Resource execution | Ceilings declared; runner did not enforce them | 0.1 s sampled process-tree RSS, macOS byte units and direct-worker peak, disk/time checks, process-group stop, atomic staged publication; short descendant spike and Windows descendant limits explicit |
| Provenance | Historical identities inherited | Parent canonical/file hashes and explicit locally rehashed versus unavailable historical inputs |
| Status | Pending human review | Pending human review |

Changed/new implementation hashes in the revised candidate:

| File | Parent mapping | Revised mapping |
| --- | --- | --- |
| `backend/src/fraudlens/training/local_run.py` | `5b30fdc25c591053c7a2080e413778ce9be455cff75dfb272e8a6463cac8988e` | `af12111b93f6bfabb5748ace7308b02906b6f61fc44482194e6d8a79da89bce3` |
| `backend/src/fraudlens/training/candidates.py` | `b741a19ab93aad99413c2359ea2f04981c5eb2688f548e74dd87af32780f224c` | `bec506b6431a50c26e3610c78d46d18fe4ed76ed96e92f4827cdc1b043009132` |
| `backend/src/fraudlens/training/resource_guard.py` | absent | `6384c100d9c2b12e5d6c73fe23a8a578f8981003a88ef1fcbf237564243fc0f3` |
| `backend/tests/unit/test_resource_guard.py` | absent | `cd8868d24fcc4a3798308ce6442829f0abc38fc89de4cb8b0bfda3a8403426f2` |

The historical `candidate_builder_sha256` remains an inherited identity; `T219-ibm-candidate.py` was not executed here because its historical inputs are absent. No hash in the parent candidate was changed.

## Read-only verification and regression

`PYTHONPATH=backend/src .venv/bin/python evidence/tasks/T219-stagec-review-verify.py specs/002-data-and-risk-scoring/t219-training-protocol.ibm-day-60-20-20.macos-resource-review.candidate.json --expected-canonical 90b2aaa07590f771343e30f7843078f2dbd71d26679040cdafc33a5fbe5c67cf` exited 0. It independently recomputed canonical SHA-256 and file-byte SHA-256, rehashed the transferred feature manifest (`63873b79a1ff875c5702a62c40c7a9cb3faef6bb7e0bb658739abac35274c05f`) plus its 3 JSONL files, the restricted label manifest (`5aee2e1d5f4f2ca7329fcc7b5b1ca0c808c4e8e39e84559e76a0d3e1a6add12c`) plus its 2 train/validation JSONL files, confirmed the label-to-feature manifest link, all 18 implementation hashes, `uv.lock`, the parent lineage, unchanged methodology, `_load_protocol`, and `verify_research_protocol`. The script hashes label-file bytes but never parses record label values. The original source CSV, T210 snapshot and T218 historical reports are absent here; their inherited identifiers were **not independently reproduced on this Mac**.

`PYTHONPATH=backend/src .venv/bin/pytest backend/tests/unit/test_resource_guard.py backend/tests/unit/test_research_split.py backend/tests/unit/test_research_labels.py backend/tests/unit/test_research_protocol.py backend/tests/unit/test_local_run.py backend/tests/unit/test_lightgbm_matrices.py backend/tests/unit/test_evaluation.py backend/tests/unit/test_artifacts.py -q --basetemp work/pytest-stagec-review-final` passed **77 tests** in 1.85 s, including one small synthetic fit. `RUFF_CACHE_DIR=work/ruff-cache .venv/bin/ruff check backend/src backend/tests evidence/tasks/T219-ibm-split.py evidence/tasks/T219-ibm-labels.py evidence/tasks/T219-ibm-candidate.py evidence/tasks/T230-evaluate.py` and Ruff on the new read-only verifier passed. `git diff --check` passed. Full backend suite was not run because it contains additional estimator fits not needed for this review; eight research candidates, real-data fit, test/showcase record-label access and T230 were not run.

## What approval would permit, and limits

Only after explicit approval of the **new canonical digest**, the documented Mac command below would verify the candidate and transferred manifests, read train/validation features and labels, fit the eight frozen LightGBM configurations in order under the declared guard, select threshold and model from validation, write native artifact/validation report and sealed test predictions without reading test labels. The experiment would appear at the requested final output path only on successful completion. T230 would still require separate authorization.

Command prepared as text, **not executed**:

```sh
PYTHONPATH=backend/src .venv/bin/python -m fraudlens.training.local_run \
  --features data/processed/t219-ibm-day-60-20-20-v1 \
  --labels data/processed/t219-ibm-day-60-20-20-labels-v1 \
  --protocol specs/002-data-and-risk-scoring/t219-training-protocol.ibm-day-60-20-20.macos-resource-review.candidate.json \
  --protocol-sha256 90b2aaa07590f771343e30f7843078f2dbd71d26679040cdafc33a5fbe5c67cf \
  --output data/eval/ibm-day-lightgbm-macos-resource-review-001 \
  --root . --n-jobs 4
```

Residual limits: 0.1 s RSS polling can miss brief descendant spikes; macOS direct-child `ru_maxrss` catches its own peak only after exit, not necessarily during the fit; Windows measures only the direct worker's memory. The historical source, snapshot and aggregate evidence were not transferred, so source-to-feature reproduction remains unavailable here. No actual research fit duration, memory use or model performance has been observed. Human review and second-person reproduction of this revision are pending. T228–T230 remain open.

**One next step:** human reviewers decide whether to approve this exact new canonical digest and its stated resource-monitoring limitations before any research-data fit.
