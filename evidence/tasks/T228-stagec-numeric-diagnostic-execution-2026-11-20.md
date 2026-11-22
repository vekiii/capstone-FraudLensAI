# T228 Stage C: approved five-arm numerical diagnostic — 2026-11-20

## Authorization, gate and execution

The [separate approval](T228-stagec-numeric-diagnostic-approval-2026-11-20.md) authorized exactly one train/validation-only five-arm execution under canonical protocol SHA-256 `22a4e6c8efe744de7d4d9b5304a8252f144ffa532037d7f0d8a5a83c66951b5b`. The approved JSON was not changed. No additional fit or automatic retry occurred.

Immediately before launch, a read-only `.venv/bin/python` check recomputed the canonical and file-byte hashes of the diagnostic candidate, ran `verify_diagnostic_protocol`, checked the parent canonical/file identity and its frozen research-protocol linkage, rehashed all **10 current diagnostic implementation files**, both transferred manifests and their five JSONL files (test **feature bytes hashed only**, not parsed), `uv.lock`, and confirmed Python 3.14.10 / LightGBM 4.7.0 / NumPy 2.5.5 / scikit-learn 1.9.1. The runner rechecks the four train/validation JSONL hashes before fitting. The prelaunch output and `.incomplete` names were both absent; free disk was 778,240,000,000 bytes, above the 20 GiB minimum. All gate checks passed. The first read-only helper print attempt ended after all file/runtime checks because it looked for the parent's implementation map at the wrong JSON nesting level; the corrected helper passed before launch. This was a helper error, not a protocol or file mismatch. No expected hash was modified.

The current diagnostic `resource_guard.py` SHA-256 is `15ee63a8aeefcb29d7141eedef17847e96fdb973a467f9dbbe1cb48d42ec1736`; the parent experiment's **historical** bound value remains `df5f9ad8683c8647590ca2f9f5c9e24f4aa939c171e40a43cccf25a595a30b4b`. The new candidate binds the current value, not the old execution code. All ten current hashes are listed in the immutable diagnostic candidate and in [preparation evidence](T228-stagec-numeric-diagnostic-preparation-2026-11-20.md).

Exact command, executed once from the project root with process-listing permission for the resource monitor:

```sh
PYTHONPATH=backend/src .venv/bin/python -m fraudlens.training.diagnostic_run \
  --features data/processed/t219-ibm-day-60-20-20-v1 \
  --labels data/processed/t219-ibm-day-60-20-20-labels-v1 \
  --protocol specs/002-data-and-risk-scoring/t228-lightgbm-numeric-diagnostic.ibm-day-60-20-20.candidate.json \
  --protocol-sha256 22a4e6c8efe744de7d4d9b5304a8252f144ffa532037d7f0d8a5a83c66951b5b \
  --parent-protocol specs/002-data-and-risk-scoring/t219-training-protocol.ibm-day-60-20-20.macos-preflight-schema-review.candidate.json \
  --output data/eval/ibm-day-lightgbm-numeric-diagnostic-001 \
  --root . --n-jobs 4
```

Exit code **0**. `data/eval/ibm-day-lightgbm-numeric-diagnostic-001/status.json` says `complete`; `.incomplete` is absent. All five ordered arms have `result.json`, native `model.txt`, validation probability CSV and validation raw CSV. Train matrix `(1,169,261, 32)`, validation matrix `(482,650, 32)`; train positives 1,206 and validation positives 471. Supervisor elapsed **58.761 s**, observed process-tree peak RSS **1,154,203,648 bytes** (1,100.734 MiB). This is sampled monitoring, with the approved short-spike limitation. Per-arm memory below is **cumulative worker peak at the end of each arm**, not isolated arm peak. Five `eval_set` deprecation warnings arose from installed LightGBM 4.7.0; no fit was interrupted.

## Validation results using probabilities

All thresholds and metrics follow the existing validation F1 and transaction-ID tie rules. Values are diagnostic validation results, not independent generalization evidence. `P@20/50/100` means deterministic precision at each rank cutoff. `0/1` counts are probabilities exactly equal to zero/one in binary64.

| Arm | Best / rounds | AP | F1 | Precision | Recall | P@20 / 50 / 100 | Threshold | Alerts | Exact 0 / 1 | Raw range | Top probability tie | Fit s | Cumulative RSS MiB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Control | 4 / 54 | 0.0132268746 | 0.0374664309 | 0.0193295485 | 0.6072186837 | .70 / .58 / .63 | 1.0 | 14,796 | 22,105 / 14,796 | −737,765.6388 … 16,101,669.3498 | 14,796 | 1.067057 | 917.563 |
| `scale_pos_weight=1` | 140 / 190 | 0.2166607047 | 0.3057142857 | 0.4672489083 | 0.2271762208 | .85 / .76 / .65 | 0.2489517623052024 | 229 | 0 / 0 | −29.8333 … 12.0565 | 1 | 3.372021 | 973.328 |
| `boost_from_average=false` | 1000 / 1000 | 0.1686430121 | 0.2291666667 | 0.2519083969 | 0.2101910828 | .85 / .76 / .56 | 0.9837731903895447 | 393 | 0 / 0 | −20.8159 … 8.7517 | 1 | 17.843318 | 1072.047 |
| `lambda_l2=1` | 2 / 52 | 0.0008961166 | 0.0058737151 | 0.0038167939 | 0.0127388535 | .00 / .00 / .00 | 0.9999999999979794 | 1,572 | 56,515 / 0 | −3672.5671 … 29.4024 | 2 | 1.001024 | 1100.734 |
| `max_delta_step=1` | 1 / 51 | 0.0010191584 | 0.0020362416 | 0.0010191584 | 1.0 | .65 / .60 / .60 | 0.0010842454337775874 | 462,146 | 0 / 0 | −6.925786 … −6.825786 | 462,146 | 0.791771 | 1100.734 |

Probability ROC AUC in the same order: `0.7412328888670372`, `0.9662388881499545`, `0.9559772621728444`, `0.10695609297230048`, `0.521261813558865`.

## Separate post-hoc raw-score ranking diagnostics

Raw scores are margins, not probabilities. No new threshold or official replacement result is defined on raw margins. AP/ROC AUC and P@k below are **diagnostic ranking** values with the same transaction-ID tie rule.

| Arm | Raw AP | Raw ROC AUC | Raw P@20 / 50 / 100 | Top raw-score tie |
|---|---:|---:|---:|---:|
| Control | 0.020062480640418316 | 0.7425293896172651 | .55 / .40 / .23 | 1,718 |
| `scale_pos_weight=1` | 0.21666070469903778 | 0.9662388881499545 | .85 / .76 / .65 | 1 |
| `boost_from_average=false` | 0.1686430121336035 | 0.9559772621728444 | .85 / .76 / .56 | 1 |
| `lambda_l2=1` | 0.0007941948886434297 | 0.09710350891220727 | .00 / .00 / .00 | 2 |
| `max_delta_step=1` | 0.001019158447763261 | 0.5212618135588651 | .65 / .60 / .60 | 462,146 |

The `max_delta_step=1` P@k values are dominated by a 462,146-way top tie and transaction-ID ordering, so they should not be read as useful ranking performance. The unweighted and no-average arms have no exact 0/1 probabilities and unique top scores. `lambda_l2=1` reduces positive saturation but has very poor ranking and remains heavily negative saturated. The no-average arm reached the 1000-round cap without early stopping; this is a cap observation, not proof of convergence. These one-factor observations support a strong role for class weighting and initialization in control saturation, but do not isolate every interaction or establish deployment performance. The probability outputs from weighted arms are not calibrated population probabilities.

## Integrity and control reproduction

For each arm, `result.json` SHA-256 matches `diagnostic.json`, and model/probability/raw CSV hashes match each result. All five native models reloaded with `lightgbm.Booster`; tree counts match the results, and reloaded probability/raw predictions on 32 validation rows match saved scores. Every probability and raw CSV has the same 482,650 ordered IDs. Probability metrics, threshold, confusion matrix and alert counts were recomputed from **all** saved validation scores and aligned validation labels; raw AP/ROC AUC were also recomputed. All matched the stored results.

Control reproduces the prior experiment exactly: best iteration 4, threshold 1.0, 14,796 alerts, zero difference in AP/F1/precision/recall/ROC AUC. Its model SHA-256 `d978b27599f38cc22a1ce1aa525cc9e9b5fd4335412ed7dca63db9d477325914` equals the frozen selected model; its complete validation probability CSV SHA-256 `3adf4e730c5afdc5567274bf00dbaa3f4a1e033976a83b5087ff5b781d9c0a63` equals the prior `validation-scores.csv` byte for byte. Thus the comparison has a reproduced control.

Output hashes, SHA-256:

| File | SHA-256 |
|---|---|
| `diagnostic.json` | `d936379c1089eb8979aa040c0385eec96591abbf6164437a66ec75a86627dc61` |
| `status.json` | `1258227157e1da37027456ade723787bfed42cb6bfadf8a233b0d263d2600d08` |
| Control `result.json` | `ef424690b4c870db4d0335689899a787e8cea978d95e792bc3119302fef36fa4` |
| Unweighted `result.json` | `4d671b97714d816aa28386e1ecf9aa264d324726a51c0a89440bb06218eaf95d` |
| No-average `result.json` | `57a768c9550bbcde1087ec2763dd58ee84f51904679e37da6fe6c9bb45df855f` |
| L2 `result.json` | `33355449ac0076f83a9ab3b89a8d2a08a56dfb0bfd7bf2bc2286ac0e1ff344a9` |
| Delta-step `result.json` | `33b95d2b4f2199f502ad272d35fb65ad948acb5330dfbaaf5f7684ad75e5cef6` |
| Control model | `d978b27599f38cc22a1ce1aa525cc9e9b5fd4335412ed7dca63db9d477325914` |
| Unweighted model | `3b4e4019312d60610dd0094c6697897a061611a60e7777ed7be35e133af9451c` |
| No-average model | `b55dd2fc41f4a34cf96d2c26a7ef43b864603c06ab8db54f51ca0276d66f4ea5` |
| L2 model | `5fe77f185d67e546137809c9d49c3407088dd5df9335591f96b60fd4442f3a30` |
| Delta-step model | `34e5ce01474a948f0819d2dc9e652a22f92e241396dcf1e2c97e8b389205acda` |

All ten probability/raw CSV SHA-256 values are recorded in the corresponding arm `result.json`; the control probability hash above was independently checked against the historical CSV. The frozen prior `experiment.json`, native model and test predictions remain byte-identical to hashes in [preparation evidence](T228-stagec-numeric-diagnostic-preparation-2026-11-20.md). No new test prediction file exists in the diagnostic output; no test/showcase labels were accessed, no T230, activation, commit or push occurred.

**Smallest recommended next change for review:** carry forward only `scale_pos_weight=1` as a proposed new training candidate with all other settings fixed, and plan a separately authorized independent holdout assessment before any application decision. This is a proposal, not automatic model selection or an authorization to generate predictions or run T230. Reused validation cannot establish generalization, and the original source/T210 snapshot remains unavailable locally for independent preparation reproduction.
