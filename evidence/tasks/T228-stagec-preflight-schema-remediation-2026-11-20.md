# T228 Stage C manifest-schema correction and no-fit preflight — 2026-11-20

- Time and place: 2026-11-20, Europe/Belgrade, `/Users/ladylazarus/Desktop/FraudLensAI-StageC`.
- Request: [original development instruction](../../prompts/development/002-T228-stagec-preflight-schema-remediation.md); first-attempt [diagnosis](T228-stagec-approved-fit-attempt-2026-11-20.md).
- Status: implementation and no-fit preflight verified; **new candidate pending human review; no research-data fit authorized by this revision**.
- Baseline: HEAD `aa1accac0ff90f2eb370618be15f145b3cc6bf2b`, dirty working tree preserved, no commit or push. Runtime `.venv` Python 3.14.10, LightGBM 4.7.0, scikit-learn 1.9.1, NumPy 2.5.5; unchanged `uv.lock` SHA-256 `b9b1c52056c3706fd21fc1fefa9934fc1c1c8c09dd2b0f465d8d49ad25cc1ffe`.

## Publisher/runner contract and root cause

`evidence/tasks/T219-ibm-split.py` publishes the transferred IBM-day feature manifest with exact top-level fields `format`, `source_sha256`, `parent_feature_manifest_sha256`, `method`, `target_shares`, `warmup_rows_excluded_from_partitions`, `showcase_rows_excluded_from_experiment`, `chronological`, `cutoffs_inclusive_utc_day`, `counts`, `daily_counts`, `partition_scoreable_id_sha256`, `label_values_read`, `files` and `resource_ceilings`. It **does not publish top-level `feature_version` or `feature_order`**. The transferred manifest's SHA-256 is `63873b79a1ff875c5702a62c40c7a9cb3faef6bb7e0bb658739abac35274c05f`; its three `files` entries bind train/validation/test feature bytes. Its `parent_feature_manifest_sha256` is `5ca1660eb582b68b27f58241b115eea5d69d3feb77f78f9fe46c12611b4f517a`.

`backend/src/fraudlens/data/training_input.py` writes `feature_version` and `feature_order` in the **parent** feature manifest; `backend/src/fraudlens/data/features.py` defines their values. The FR-021 candidate explicitly records the same version/order and the parent manifest hash; its research feature-manifest hash binds the repartitioned files, and the restricted label manifest links back to that research manifest. The runner verifies actual JSONL feature keys against the code's frozen order, and reads numeric/categorical values in that order. The parent manifest and historical source/snapshot are **not present on this Mac**; the parent version/order and original computation are inherited identities, not independently reconstructed here. The new candidate additionally hashes `features.py` and `training_input.py` so the locally observed definition and parent publisher code are bound, but this does not replace unavailable historical input verification.

The first attempt failed because `local_run.py` incorrectly demanded `feature_version` and `feature_order` in the research feature manifest. The correction accepts **only the exact published research/label manifest schemas and expected partition files**, verifies their byte hashes and protocol links, and requires protocol version/order to equal the imported `FEATURE_VERSION`/`FEATURE_ORDER`. Unknown manifest keys/formats, missing partitions, changed version/order, row schemas and label misalignment fail. No frozen manifest, data, protocol methodology or expected hash was adjusted; no silent default was added. The shared `_prepare_training_inputs` function performs protocol/manifest checks, train-only vocabulary discovery, train and validation matrix construction, ordered label alignment and frozen positive-count checks. Both training and `--preflight-only` use it. The preflight branch writes only `preflight.json`, never calls the grid or parses test feature rows/labels, and uses the existing subprocess resource watchdog with the protocol's unchanged ceilings. It **does hash test feature-file bytes** as part of manifest integrity verification. The guard accepts `preflight.json` as a distinct required report and publishes it atomically after success.

## RED/GREEN, regression and actual transferred-input preflight

RED: `PYTHONPATH=backend/src .venv/bin/pytest backend/tests/unit/test_local_run.py::test_ibm_day_publisher_schema_reaches_preprocessing_without_fit -q --basetemp work/pytest-manifest-red` exited **1** at the original `ValueError: source, feature or label manifest identities differ` before preprocessing. GREEN: `PYTHONPATH=backend/src .venv/bin/pytest backend/tests/unit/test_local_run.py -q --basetemp work/pytest-local-run-green` exited **0**, 5 passed at that stage. Added negative order/version/unknown-schema cases and CLI/direct preflight tests that fail if fit is called.

An initial combined regression in the normal restricted sandbox produced 8 passed, 7 failed because macOS `ps` returned `Operation not permitted` to the watchdog; this was an environment permission failure, not a code behavior result. The same full focused command with approved process inspection exited **0**, **84 passed in 1.92 s**:

```sh
PYTHONPATH=backend/src .venv/bin/pytest backend/tests/unit/test_local_run.py backend/tests/unit/test_resource_guard.py backend/tests/unit/test_research_split.py backend/tests/unit/test_research_labels.py backend/tests/unit/test_research_protocol.py backend/tests/unit/test_lightgbm_matrices.py backend/tests/unit/test_evaluation.py backend/tests/unit/test_artifacts.py -q --basetemp work/pytest-stagec-schema-final-002
```

The `--preflight-only` command below used the previously approved candidate solely as an input contract. An initial successful run used `work/stagec-preflight-schema-001` (11.65 s, 917,962,752-byte peak). Review found that its report field `test_features_read: false` was imprecise: the guard hashes test feature-file bytes but does not parse test rows. That initial no-fit output remains intact. After changing the report to distinguish byte hashing from row parsing, the command was repeated once under the distinct `work/stagec-preflight-schema-002` name; both its final and `.incomplete` paths were absent before launch. macOS process inspection was permitted so the existing 20 GiB initial disk, 10 GiB continuing reserve, 8 GiB sampled memory and monotonic time limits applied. The new candidate binds the second report.

```sh
PYTHONPATH=backend/src .venv/bin/python -m fraudlens.training.local_run \
  --features data/processed/t219-ibm-day-60-20-20-v1 \
  --labels data/processed/t219-ibm-day-60-20-20-labels-v1 \
  --protocol specs/002-data-and-risk-scoring/t219-training-protocol.ibm-day-60-20-20.macos-resource-review.candidate.json \
  --protocol-sha256 90b2aaa07590f771343e30f7843078f2dbd71d26679040cdafc33a5fbe5c67cf \
  --output work/stagec-preflight-schema-002 --root . --n-jobs 4 --preflight-only
```

Exit **0**. Actual checks completed: candidate/protocol and transferred manifest/file hashes, exact manifest schemas, train-only category vocabulary (16 currency and 7 format values including unknown buckets), 1,169,261 train and 482,650 validation feature rows, matrices `(1169261, 32)` and `(482650, 32)`, ordered train/validation label alignment, 1,206 train and 471 validation positives matching frozen manifests, and one-class/zero-positive refusal conditions. Worker preparation took **10.926 s**; supervisor completed in **11.532 s** with observed process-tree peak RSS **918,028,288 bytes**. The resulting `work/stagec-preflight-schema-002/preflight.json` SHA-256 is `c6947b347fa6db43abb9eceebe6db013b9fd2d9f8d75bfbd348dda14f13c5c35`; `status.json` SHA-256 is `be932f47a7d16237e6999133517760a9467892a695dcd53b0c91493597cff37d`, state `complete`. That state means **preflight complete**, not experiment complete. The directory contains only those two reports. No estimator.fit, model, experiment.json, validation scores or test predictions; test feature-file bytes were hashed, test feature rows were not parsed, and no test/showcase labels were accessed.

Ruff on backend sources/tests and relevant evidence scripts exited **0** (`All checks passed!`). `git diff --check` exited **0**. A small synthetic LightGBM fit/artifact roundtrip was among the 84 tests; it used synthetic arrays only and is compatibility evidence, not real-data evaluation.

## New candidate and independent verification

[New pending-review candidate](../../specs/002-data-and-risk-scoring/t219-training-protocol.ibm-day-60-20-20.macos-preflight-schema-review.candidate.json):

- **Canonical SHA-256:** `1ebac4f24aa198cfd1de70b96204676cb3fbd0cc07786296944c6ade0214f6be`.
- **File-byte SHA-256:** `2446c611f348c1dffe8ef0e912d08051924f66454002d9dcebeb9926aac6e017`.
- Parent approved-first-attempt candidate: canonical `90b2aaa07590f771343e30f7843078f2dbd71d26679040cdafc33a5fbe5c67cf`, file bytes `fcdd833474f6fdf47b1bbbabfd003e2f9081e99c3506f229977d35f9a83085f7`; still unchanged. The first `.incomplete/status.json` remains byte-identical, SHA-256 `ad83506e7de2dc1a03f07790b3be712e2a87bbc7c4843b7bae36289b363cc50e`.
- Exactly five top-level metadata/binding fields changed: `candidate_lineage`, `model_fitting_scope`, `receiving_mac_identity_scope`, `reproducibility`, `resource_configuration`. The research method, source/manifest identities, counts/splits, feature order/version, grid, seed, class weights, early stopping, thresholds, selection/ties and all numeric ceilings remain equal to the parent. Status is `candidate_pending_explicit_human_review`.
- Changed/bound implementation SHA-256 values:

| File | Previous candidate | New candidate |
| --- | --- | --- |
| `backend/src/fraudlens/training/local_run.py` | `af12111b93f6bfabb5748ace7308b02906b6f61fc44482194e6d8a79da89bce3` | `dd08e9ac04657ec628e321b0fbf94c4b4fc5242cbc55e5a8fdcae189702cca6d` |
| `backend/src/fraudlens/training/resource_guard.py` | `6384c100d9c2b12e5d6c73fe23a8a578f8981003a88ef1fcbf237564243fc0f3` | `df5f9ad8683c8647590ca2f9f5c9e24f4aa939c171e40a43cccf25a595a30b4b` |
| `backend/tests/unit/test_local_run.py` | `de3ebf52426af741cf3dfc5b86f0c008a900bb6ee1f9b100c54a5239db06c4eb` | `01e712a6d04eac8bc5423460901962dde743f22e974d292ba2a42403057270a1` |
| `backend/tests/unit/test_resource_guard.py` | `cd8868d24fcc4a3798308ce6442829f0abc38fc89de4cb8b0bfda3a8403426f2` | `3a15d0ab132e82c537b106c8d5bd5a6a1ead4394303a880fcc8dd8d279e9af98` |
| `backend/src/fraudlens/data/features.py` | not listed | `bfc410497d813bcd81f92e5333a26f49b09a85547bcf28ed75240bef5b9c7b87` |
| `backend/src/fraudlens/data/training_input.py` | not listed | `28dae762e163378b930fe76eed414b2ef9a484bba3e0fef7b1512f9fa4f1a109` |

The unchanged IBM-day split publisher remains bound in both candidates. The new mapping has **20** files. The inherited historical `candidate_builder_sha256` was not regenerated; `T219-ibm-candidate.py` was not run because its inputs are absent here.

Read-only verification command:

```sh
PYTHONPATH=backend/src .venv/bin/python evidence/tasks/T219-stagec-review-verify.py specs/002-data-and-risk-scoring/t219-training-protocol.ibm-day-60-20-20.macos-preflight-schema-review.candidate.json --parent specs/002-data-and-risk-scoring/t219-training-protocol.ibm-day-60-20-20.macos-resource-review.candidate.json --expected-canonical 1ebac4f24aa198cfd1de70b96204676cb3fbd0cc07786296944c6ade0214f6be
```

Exit **0**: canonical/file hash, immediate-parent lineage, unchanged method, both manifest links, three feature and two train/validation label file hashes, all 20 implementation files, lock, HEAD, `_load_protocol` and `verify_research_protocol` passed. A second calculation using only Python standard-library `json.dumps(..., ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(',', ':'))` and `hashlib.sha256` independently produced the same canonical/file digests; it also confirmed the previous candidate's digests and pending status. This candidate does **not** inherit the earlier approval.

## Remaining limits and next step

Original source CSV, T210 snapshot/manifest and T218 historical reports are absent, so those inherited claims cannot be independently reproduced on this Mac. Preflight does not establish model performance or guarantee a later fit will finish. Existing 0.1 s memory polling can miss brief descendant spikes; Windows descendant memory is not fully monitored. The prior `.incomplete` result is retained. No T230, test/showcase label access, real-data estimator fit, commit or push occurred. T228–T230 remain open.

**One next step:** human reviewers decide whether to approve the exact new canonical SHA-256 before a separately authorized second fit attempt.
