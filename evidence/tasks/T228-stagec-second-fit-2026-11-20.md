# T228 Stage C second approved LightGBM experiment — 2026-11-20

- Date/time: 2026-11-20, approximately 19:50–19:52 CET (Europe/Belgrade).
- Status: **one approved second attempt completed successfully**. Current-phase LightGBM training and validation selection are complete; test performance is **not measured**.
- Authorization: [exact-hash second approval](T219-stagec-second-protocol-approval-2026-11-20.md); [original development instruction](../../prompts/development/002-T228-stagec-second-approved-fit.md). This approval does not include T230, test/showcase label access or model activation.
- Working directory `/Users/ladylazarus/Desktop/FraudLensAI-StageC`; HEAD `aa1accac0ff90f2eb370618be15f145b3cc6bf2b`, dirty working tree preserved. No commit or push.
- Runtime: project `.venv` Python **3.14.10**, LightGBM **4.7.0**, scikit-learn **1.9.1**, NumPy **2.5.5**, matching the unchanged `uv.lock` SHA-256 `b9b1c52056c3706fd21fc1fefa9934fc1c1c8c09dd2b0f465d8d49ad25cc1ffe`. CPU, four worker threads, deterministic/column-wise LightGBM, seed 42, 50-round validation early stopping.
- Inputs: source identity `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`, IBM-day feature manifest SHA-256 `63873b79a1ff875c5702a62c40c7a9cb3faef6bb7e0bb658739abac35274c05f`, train/validation-only label manifest SHA-256 `5aee2e1d5f4f2ca7329fcc7b5b1ca0c808c4e8e39e84559e76a0d3e1a6add12c`. Historical source/parent manifest remain unavailable for local independent reproduction.
- Output: ignored `data/eval/ibm-day-lightgbm-macos-preflight-schema-review-002`. It and its `.incomplete` sibling were absent before launch. The first failed `data/eval/ibm-day-lightgbm-macos-resource-review-001.incomplete/status.json` was preserved, SHA-256 `ad83506e7de2dc1a03f07790b3be712e2a87bbc7c4843b7bae36289b363cc50e`.

## Immediate read-only gate and execution

The read-only verifier command below exited **0 immediately before execution**. It confirmed exact canonical SHA-256 `1ebac4f24aa198cfd1de70b96204676cb3fbd0cc07786296944c6ade0214f6be`, file-byte SHA-256 `2446c611f348c1dffe8ef0e912d08051924f66454002d9dcebeb9926aac6e017`, immediate parent, unchanged methodology, **20** bound implementation hashes, both manifests and **five** JSONL byte hashes, `uv.lock`, Git HEAD, protocol loader and research verifier. It hashes train/validation label files as bytes without parsing rows; the subsequent authorized worker reads only those train/validation labels.

```sh
PYTHONPATH=backend/src .venv/bin/python evidence/tasks/T219-stagec-review-verify.py specs/002-data-and-risk-scoring/t219-training-protocol.ibm-day-60-20-20.macos-preflight-schema-review.candidate.json --parent specs/002-data-and-risk-scoring/t219-training-protocol.ibm-day-60-20-20.macos-resource-review.candidate.json --expected-canonical 1ebac4f24aa198cfd1de70b96204676cb3fbd0cc07786296944c6ade0214f6be
```

`.venv/bin/python` printed `3.14.10 4.7.0 1.9.1 2.5.5`; lock entries for LightGBM, scikit-learn and NumPy matched, and `uv.lock` was rehashed. Both output paths were reported `ABSENT`. The approved protocol JSON was not changed; its first-candidate parent JSON was also unchanged. The exact authorized command was then run **once**:

```sh
PYTHONPATH=backend/src .venv/bin/python -m fraudlens.training.local_run \
  --features data/processed/t219-ibm-day-60-20-20-v1 \
  --labels data/processed/t219-ibm-day-60-20-20-labels-v1 \
  --protocol specs/002-data-and-risk-scoring/t219-training-protocol.ibm-day-60-20-20.macos-preflight-schema-review.candidate.json \
  --protocol-sha256 1ebac4f24aa198cfd1de70b96204676cb3fbd0cc07786296944c6ade0214f6be \
  --output data/eval/ibm-day-lightgbm-macos-preflight-schema-review-002 \
  --root . --n-jobs 4
```

Exit **0**. The supervisor published `status.json` state **`complete`**, reason null, after zero worker exit, report and resource checks; no second `.incomplete` directory remains. LightGBM printed eight nonfatal `eval_set` deprecation warnings. `experiment.json` contains exactly eight ordered candidate results with indices **0–7** and positive `best_iteration` values; independent use of the frozen `rank_lightgbm_candidates` function returns the recorded selected candidate. Train count **1,169,261** (1,206 positive), validation count **482,650** (471 positive), test prediction count **233,070**. The report records `test_labels_read=false` and `working_tree_dirty=true`.

## Validation comparison and selection

These are **validation** metrics. `experiment.json` records F1, AP and Precision@20 for each candidate, but precision, recall and chosen threshold **only for the selected candidate**. No score files or artifacts exist for the other seven candidates, so their missing cells cannot be reconstructed without another fit; they are deliberately left unavailable.

| # | Leaves | Rate | Min child | Best iteration | F1 | Precision | Recall | AP | P@20 | Threshold |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 31 | 0.05 | 50 | 5 | 0.035152 | unavailable | unavailable | 0.014838 | 0.60 | unavailable |
| **1** | **31** | **0.05** | **200** | **4** | **0.037466** | **0.019330** | **0.607219** | **0.013227** | **0.70** | **1.0** |
| 2 | 31 | 0.10 | 50 | 5 | 0.021235 | unavailable | unavailable | 0.008762 | 0.70 | unavailable |
| 3 | 31 | 0.10 | 200 | 2 | 0.020937 | unavailable | unavailable | 0.008878 | 0.65 | unavailable |
| 4 | 63 | 0.05 | 50 | 4 | 0.024735 | unavailable | unavailable | 0.010175 | 0.65 | unavailable |
| 5 | 63 | 0.05 | 200 | 2 | 0.036720 | unavailable | unavailable | 0.005834 | 0.75 | unavailable |
| 6 | 63 | 0.10 | 50 | 2 | 0.022729 | unavailable | unavailable | 0.009646 | 0.65 | unavailable |
| 7 | 63 | 0.10 | 200 | 2 | 0.023066 | unavailable | unavailable | 0.009750 | 0.65 | unavailable |

Candidate **1** was selected because its validation positive-class F1 **0.03746643086395494** is the highest among all eight; no ranking tie-break was needed. Its exact validation precision is `0.01932954852662882`, recall `0.6072186836518046`, AP `0.013226874634255597`, P@20 `0.7`, and threshold `1.0` under the protocol's positive-F1 threshold objective and precision/higher-threshold tie rule. The selected native artifact contains **4 trees**, matching `best_iteration=4`. These numbers make no claim about test performance.

## Output integrity, native reload and resources

Read-only post-run inspection exited **0**. `read_verified_artifact` authenticated the selected manifest against the digest in `experiment.json`, checked source/protocol/version/ordered features and model bytes, then a fresh `lightgbm.Booster(model_str=...)` parsed the native text. It reported four trees and 32 features and produced a finite `[0,1]` score on a synthetic all-zero row. This is an artifact reload check, not a new fit or evaluation.

| Output file | Full SHA-256 |
| --- | --- |
| `artifacts/selected-lightgbm/model.txt` | `d978b27599f38cc22a1ce1aa525cc9e9b5fd4335412ed7dca63db9d477325914` |
| `artifacts/selected-lightgbm/manifest.json` | `9010faab6c2ae1ab395817e371970f223b3cf3e08e368f4066c98d68cc4cdbfd` |
| `experiment.json` | `7dda36e76957169525ff8ca3c52a514ed04141f0e559b1fbb0c27471f1b3a81c` |
| `test-predictions-sealed.csv` | `cc63b5d3cfbfd4ce9a2fc13794e5e0e8c48758565128938abfc5e31fe844048f` |
| `validation-scores.csv` | `3adf4e730c5afdc5567274bf00dbaa3f4a1e033976a83b5087ff5b781d9c0a63` |
| `status.json` | `9b7b45eb3d54fd1bf6ae5b7da57a4db9cee6dbde3e9eeecaa54ae7ac35b28ee0` |

The test prediction digest matches `experiment.json`. Structural-only checks found exactly **233,070** unique IDs in the frozen partition order; their SHA-256 is `b9d9231b67969c96585dcb9ea8ce46ee9079501c02b1f18fd473c2e61a4d487f`, matching the protocol. CSV header is `transaction_id,occurred_at_utc,score`; every timestamp is timezone-aware and chronological and every score is finite in `[0,1]`. No test/showcase labels were opened or joined, and **no test metrics were calculated**.

Worker `experiment.json` records **28.39 s** total, **9.589 s** for the eight fits, and **1,161,052,160 bytes** direct-process peak. The supervisor records **29.084 s** total and **1,161,068,544 bytes** observed process-tree peak RSS, below the unchanged 8 GiB ceiling; disk/time checks passed. The 0.1 s sampling limit remains. No additional training, T230, model activation, commit or push occurred.

## Limitations and continuation

The per-candidate precision, recall and thresholds for seven candidates were not retained by this runner. They cannot be filled from the published outputs without rerunning those fits, which this one-attempt approval does not permit. Original source/parent-feature manifest and T218 historical reports remain unavailable for independent source-to-feature reproduction on this Mac. Validation metrics are **not** test metrics. T230 requires separate explicit authorization; the frozen test prediction digest above is available for that later gate. T228/T229 evidence is updated, while task checklist review remains separate.

**One concrete next step:** human reviewers inspect this completed validation experiment and frozen-output hashes, then decide separately whether to authorize T230 against the exact test-prediction SHA-256. Do not run T230 from this approval.
