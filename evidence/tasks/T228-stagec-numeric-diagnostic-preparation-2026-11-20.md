# T228 Stage C: preparation of the five-arm numeric diagnostic — 2026-11-20

## Scope and decision

The user accepted preparation of exactly five predefined one-factor arms, but did not authorize fits on project data. This work adds a separate train/validation-only diagnostic runner and a **pending human review** protocol. No project fit, T230, test/showcase label access, model activation, commit or push occurred. The original FR-021 protocols, finished experiment, model and frozen test predictions were left unchanged.

The prerequisite numerical analysis is [T228-stagec-numeric-diagnostic-2026-11-20.md](T228-stagec-numeric-diagnostic-2026-11-20.md). Its selected configuration is `num_leaves=31`, `learning_rate=0.05`, `min_child_samples=200`. Control reproduces all existing training settings. The other arms change only: `scale_pos_weight=1`, `boost_from_average=false`, `reg_lambda=1` (native `lambda_l2`), or `max_delta_step=1` (native aliases `max_tree_output` and `max_leaf_output`). The installed LightGBM 4.7.0 exposes these parameters; a synthetic model-text check confirmed `lambda_l2`, `max_delta_step` and `boost_from_average`. Official references: [parameter names and aliases](https://lightgbm.readthedocs.io/en/stable/Parameters.html), [Python classifier](https://lightgbm.readthedocs.io/en/stable/pythonapi/lightgbm.LGBMClassifier.html).

## Implementation and measurements

`backend/src/fraudlens/training/diagnostic_run.py` verifies exact protocol/code/lock/runtime hashes and prior experiment identity before reading only train/validation features and labels. The transferred manifests and underlying train/validation JSONL files are checked against frozen hashes; parent feature version/order and class counts are checked. It uses the existing train-only vocabulary and matrix parser. Five arms run in fixed order under the existing subprocess resource supervisor, with four threads, seed 42, validation binary logloss early stopping after 50 non-improving rounds, and unchanged 1000-round limit. It records effective sklearn/native parameters, fit options, native model, complete observed validation logloss history, best iteration, total rounds, validation probability/raw CSV with IDs and timestamps, probability metrics and F1-rule threshold/confusion matrix, separate raw ranking diagnostics, ties, saturation, leaf extrema/Hessians, time, memory and file hashes. Weighted training outputs are not described as calibrated population probabilities. No test predictions are generated.

`backend/src/fraudlens/training/resource_guard.py` recognizes `diagnostic.json` as the final report and removes a partial top-level report on failure. The report is written only after all five arms; the supervisor publishes a final-named directory only on success. On interruption, `.incomplete` preserves partial arm files and failure status. Limits inherited without increases: 20 GiB free disk before start, 10 GiB reserve during/final, 8 GiB observed process-tree RSS, 3600 s per arm, 28800 s phase, 54000 s total. Polling is 0.1 s, so short macOS memory spikes can be missed. Windows monitoring observes only the direct worker. These are monitoring limits, not an instantaneous hard memory cap.

Comparison is fixed in advance: check control reproduction against frozen validation result, then compare raw-margin extrema/saturation, validation metrics and alert count against control. No automatic application winner. Validation has already served selection and diagnosis; further validation outcomes are not independent generalization evidence.

## RED/GREEN and checks

- RED: `PYTHONPATH=backend/src .venv/bin/python -m pytest backend/tests/unit/test_diagnostic_run.py -q` failed at collection because `fraudlens.training.diagnostic_run` did not exist.
- GREEN: the new synthetic five-arm test passed; it checks exact one-factor changes, native aliases, all arm outputs, probability/raw score files, model reload and control compatibility. Negative tests reject altered arm plans and invalid matrices; supervisor tests cover completion and partial failure. No project data was fitted.
- Final regression command: `PYTHONPATH=backend/src .venv/bin/python -m pytest backend/tests/unit/test_diagnostic_run.py backend/tests/unit/test_resource_guard.py backend/tests/unit/test_local_run.py backend/tests/unit/test_lightgbm_matrices.py backend/tests/unit/test_evaluation.py backend/tests/unit/test_research_protocol.py -q` → **58 passed, 6 LightGBM eval_set deprecation warnings**. In the default sandbox eight process-supervisor cases initially stopped because `ps` was denied (`Operation not permitted`); the identical test command passed with read-only process listing enabled. The warning does not change this run's fit semantics.
- `.venv/bin/ruff check backend/src/fraudlens/training/diagnostic_run.py backend/src/fraudlens/training/resource_guard.py backend/tests/unit/test_diagnostic_run.py` → passed.
- `git diff --check` → passed.
- Read-only `verify_diagnostic_protocol` on the new candidate → `pending_human_review`; it checked parent and implementation hashes, locked runtime, prior report/model and input identities. This was no-fit validation, not a real-data preflight or training run.

## New candidate identity

Path: `specs/002-data-and-risk-scoring/t228-lightgbm-numeric-diagnostic.ibm-day-60-20-20.candidate.json`.

Canonical SHA-256 (project canonical JSON): `22a4e6c8efe744de7d4d9b5304a8252f144ffa532037d7f0d8a5a83c66951b5b`.

File-byte SHA-256: `082ada367c4255d6ed59d615ba3362d5099c6443c38258cf4d18690ccc144d24`.

Parent canonical SHA-256: `1ebac4f24aa198cfd1de70b96204676cb3fbd0cc07786296944c6ade0214f6be`; parent file-byte SHA-256: `2446c611f348c1dffe8ef0e912d08051924f66454002d9dcebeb9926aac6e017`. New protocol binds the prior experiment/model SHA-256 and inherited source/manifest/file identities; the original T210 snapshot and parent source remain unavailable locally and were not independently reproduced. Git HEAD `aa1accac0ff90f2eb370618be15f145b3cc6bf2b` has local changes.

Runtime: Python 3.14.10, LightGBM 4.7.0, NumPy 2.5.5, scikit-learn 1.9.1. `uv.lock` SHA-256: `b9b1c52056c3706fd21fc1fefa9934fc1c1c8c09dd2b0f465d8d49ad25cc1ffe`.

Execution file SHA-256 values (all full values are in the JSON): `diagnostic_run.py` `bdb66b93cae40b8fe3864da9262db855ca21ed6ac7c844f4825337b2beb6275c`; `resource_guard.py` `15ee63a8aeefcb29d7141eedef17847e96fdb973a467f9dbbe1cb48d42ec1736`; `local_run.py` `dd08e9ac04657ec628e321b0fbf94c4b4fc5242cbc55e5a8fdcae189702cca6d`; `evaluation.py` `b488999e083db8fe05f55bdcd4d7bcf2076765a7d2a36b284beb39bc4991d774`; `protocol.py` `072e4ed3dd64cbbb9f8c635cefa5bd99cc4f7f9a07efcb10bdaf2a77e10cc24b`; `candidates.py` `bec506b6431a50c26e3610c78d46d18fe4ed76ed96e92f4827cdc1b043009132`; `boundaries.py` `a16020b8022b3be0a00979320327f24e6d9a4665586b733bbd0db7a89dddf4af`; `features.py` `bfc410497d813bcd81f92e5333a26f49b09a85547bcf28ed75240bef5b9c7b87`; `manifest.py` `5c061ec3c28a218c274e10e5ce8bc5985b1c524e230e7988d4fee4fed73774f2`; `scoring/artifacts.py` `bf33f0f19423ef1b7efbc88ddb430a639602cdfe6f32f5ad9619c7b702430ca3`.

Preservation check: prior `experiment.json` `7dda36e76957169525ff8ca3c52a514ed04141f0e559b1fbb0c27471f1b3a81c`; model `d978b27599f38cc22a1ce1aa525cc9e9b5fd4335412ed7dca63db9d477325914`; frozen test predictions `cc63b5d3cfbfd4ce9a2fc13794e5e0e8c48758565128938abfc5e31fe844048f`.

**Next step:** human review of this exact candidate hash; only a separate approval would permit the five project-data fits. The proposed command is documented in `next_work.md` and is not executed here.
