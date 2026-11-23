# FR-023 cross-family comparison execution — 2026-11-20

## Authorization, identity and prelaunch gate

The user approved exactly one run of canonical protocol SHA-256 `7fd4e7349b2ef4921166d008f5c3b7e147c21a6554eae5160f33948d323bac32`, seven fixed estimator fits plus train-prevalence constant, inclusion of the existing unweighted LightGBM without refit, and use of the frozen cross-family ranking rule. [Approval record](T224-stagec-cross-family-approval-2026-11-20.md) records the scope. This does not accept an application model or authorize holdout access/T230. The approved JSON was not changed.

Immediately before execution, a read-only Python gate checked project and independent canonical JSON SHA-256, exact protocol format/status, parent/diagnostic lineage, all **10 current executable hashes**, both transferred manifests and four train/validation JSONL hashes, `uv.lock`, Python 3.14.10 / LightGBM 4.7.0 / NumPy 2.5.5 / scikit-learn 1.9.1, both existing LightGBM model/result SHA-256 values and the unweighted validation probability/raw CSV hashes and recorded F1/threshold. It also confirmed that `data/eval/ibm-day-cross-family-comparison-001` and its `.incomplete` sibling did not exist. All checks passed. Free disk reported 778,240,000,000 bytes at that gate. Original T210 source/snapshot identities remain inherited, not independently reconstructed here.

The exact approved command ran **once** (exit 0), with `PYTHONPATH=backend/src .venv/bin/python -m fraudlens.training.comparison_run`, the two transferred input directories, approved protocol/hash, output `data/eval/ibm-day-cross-family-comparison-001`, root `.` and `--n-jobs 4`. There was no retry or parameter change. It wrote eight new candidate outputs (one constant plus seven fits). The existing weighted current-phase LightGBM and later unweighted diagnostic LightGBM were not fitted again. The protocol's comparison set therefore contains **ten** entries; the user's request to display “nine” corresponds to the eight new entries plus the unweighted model, but omits the protocol-linked weighted current-phase reference. Both existing references are shown below to preserve the approved protocol's full comparison set.

The supervisor published `status.json` with `state=complete`, `reason=null`, elapsed **91.4 s**, observed process-tree peak RSS **1,995,735,040 bytes**. `experiment.json` has `comparison_complete_review_pending`, eight candidate result hashes, 1,169,261 train and 482,650 validation rows, `test_features_read=false`, `test_labels_read=false`, `test_predictions_written=false`; no `fit-progress.json` remains. The report's own worker cumulative peak is 1,973,452,800 bytes. The supervisor value is the overall observed peak. macOS monitoring sums `ps` RSS for the worker and descendants every 0.1 s (KiB converted to bytes) and checks direct-worker `ru_maxrss` after exit; a shorter descendant spike can be missed. The per-candidate RSS values below are **cumulative worker peaks at candidate end**, not isolated per-fit peaks. On Windows, only the direct worker would be measured. Existing LightGBM memory/time values come from their historical runs and are not comparable as per-fit measurements.

## Read-only result verification

After completion, a separate read-only pass verified all eight result/model/score-file hashes against `experiment.json` and each candidate `result.json`; no final `fit-progress.json` existed. It read the saved validation score CSVs and **only** the transferred validation label JSONL, aligned all 482,650 IDs in row order for each of the eight new candidates and both existing LightGBM comparators, and recomputed F1, AP, precision, recall, threshold, ROC AUC, confusion matrix and P@20/50/100 with the frozen `evaluate_validation` implementation. All ten matched their saved results (floating metrics within `1e-10` relative / `1e-12` absolute; confusion and ordered IDs exactly). No test/showcase label, new test prediction, model activation or T230 was involved.

The following metrics are **validation only**. Thresholds are shown at their stored full numeric precision. `RSS` is bytes; “phase” means the historical whole-run measurement, and `—` means no estimator fit/iteration or no per-candidate measurement.

| Rank | Candidate | F1 | AP | P@20 | P@50 | P@100 | Precision | Recall | Threshold | Alerts | TP | FP | TN | FN |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | LightGBM unweighted diagnostic | 0.3057142857142857 | 0.2166607046990379 | 0.85 | 0.76 | 0.65 | 0.4672489082969432 | 0.22717622080679406 | 0.2489517623052024 | 229 | 107 | 122 | 482057 | 364 |
| 2 | HGB 3 | 0.2323856613102596 | 0.17559748734147484 | 0.85 | 0.72 | 0.58 | 0.2781065088757396 | 0.19957537154989385 | 0.9794289829862686 | 338 | 94 | 244 | 481935 | 377 |
| 3 | HGB 4 | 0.2259663032705649 | 0.16599437122336208 | 0.9 | 0.7 | 0.54 | 0.21189591078066913 | 0.24203821656050956 | 0.9759330438916706 | 538 | 114 | 424 | 481755 | 357 |
| 4 | HGB 5 | 0.22255192878338279 | 0.17091285915878218 | 0.8 | 0.8 | 0.55 | 0.3694581280788177 | 0.1592356687898089 | 0.9852041434619883 | 203 | 75 | 128 | 482051 | 396 |
| 5 | HGB 1 | 0.20335195530726258 | 0.15389526621017097 | 0.9 | 0.72 | 0.54 | 0.21462264150943397 | 0.1932059447983015 | 0.9703847951532942 | 424 | 91 | 333 | 481846 | 380 |
| 6 | HGB 2 | 0.1984861227922624 | 0.15175231946803708 | 0.85 | 0.7 | 0.5 | 0.16434540389972144 | 0.2505307855626327 | 0.9761433638694108 | 718 | 118 | 600 | 481579 | 353 |
| 7 | LightGBM weighted current-phase | 0.03746643086395494 | 0.013226874634255597 | 0.7 | 0.58 | 0.63 | 0.01932954852662882 | 0.6072186836518046 | 1.0 | 14796 | 286 | 14510 | 467669 | 185 |
| 8 | Decision tree | 0.029341521664960766 | 0.012890627796207543 | 0.7 | 0.6 | 0.62 | 0.014971493232362798 | 0.7303609341825902 | 0.9177223643437651 | 22977 | 344 | 22633 | 459546 | 127 |
| 9 | L2 logistic | 0.02701587956279645 | 0.01488371208099689 | 0.15 | 0.06 | 0.03 | 0.01419746396445215 | 0.2781316348195329 | 0.9207398217572055 | 9227 | 131 | 9096 | 473083 | 340 |
| 10 | Train-prevalence constant | 0.0019498220942579603 | 0.0009758624261887496 | 0.65 | 0.6 | 0.6 | 0.0009758624261887496 | 1.0 | 0.0010314207007674078 | 482650 | 471 | 482179 | 0 | 0 |

| Candidate | Fit or scoring seconds | RSS at candidate end (bytes) | Iterations | Exact score 0 / 1 | Top-score tie |
|---|---:|---:|---:|---:|---:|
| LightGBM unweighted diagnostic | 3.372021 historical fit | 1,020,608,512 historical cumulative | 140 | 0 / 0 | 1 |
| HGB 3 | 15.716221 | 1,790,820,352 | 300 | 0 / 0 | 1 |
| HGB 4 | 9.174081 | 1,860,386,816 | 200 | 0 / 0 | 1 |
| HGB 5 | 15.268207 | 1,954,299,904 | 300 | 0 / 0 | 1 |
| HGB 1 | 9.762518 | 1,645,740,032 | 200 | 0 / 0 | 1 |
| HGB 2 | 10.773950 | 1,705,574,400 | 200 | 0 / 0 | 2 |
| LightGBM weighted current-phase | 29.084 historical phase | 1,161,068,544 historical phase peak | 4 | 0 / 14,796 | 14,796 |
| Decision tree | 3.088264 | 1,106,149,376 | — | 24,180 / 0 | 22,877 |
| L2 logistic | 1.222531 | 1,527,447,552 | 68 of max 1,000 | 0 / 0 | 1 |
| Train-prevalence constant | 0.000144 scoring | 922,533,888 | — | 0 / 0 | 482,650 |

Ranking follows the approved rule: all F1 values differ, so AP/P@20/family tie-breaks did not change order. The unweighted diagnostic LightGBM ranks first **on reused validation**; that is a comparison result, not acceptance for the app. HGB 3 is the strongest newly fitted candidate. HGB 4 has P@20 0.9 versus HGB 3's 0.85, but F1 has priority. Decision tree has 24,180 exact-zero scores and a 22,877-row top-score tie; the constant has one 482,650-row tie. The historical weighted LightGBM still has 14,796 exact-one scores/tie. None was excluded post hoc. All saved scores were finite and in [0,1], and every candidate had a defined validation threshold. HGB early stopping was disabled by design and all five reached their planned 200/300 iterations. Logistic finished at 68 iterations, below its 1,000 cap. The runner did not persist per-fit warning capture, so absence of a stored convergence warning is not proof that no warning was ever emitted; no convergence warning was observed in the completed command output. No numerical fault invalidated the recorded deterministic comparison.

## Full hashes

Overall `experiment.json`: `f72108083e2b789a106e13a772f8528256add0d5147ab69e6d2dab1e26a6ee62`; `status.json`: `a833e842ccd2d08fc60f06410601b27ce963e3da3d5f1dd647156f19d1c22036`.

| New candidate | Model/state SHA-256 | Result JSON SHA-256 | Validation CSV SHA-256 |
|---|---|---|---|
| Prevalence constant | `aabfc3c664d08c95e18ef7e8f82d2cc92c7e0d1104cf3e78db8f7cef6416a2f6` | `f136e02bcf8922d7398cebd3af8274069c1087f83efcce9047e1d0625a89fcf9` | `93f7ad4ee16942ebe413a5ff110bf923a450dbc35ce00a1167dbb03fc459dde9` |
| Decision tree | `fa4b1e862509eafe03cb35f0f45f2cc8be5624d2a14361e0080d01c0a7213b76` | `bd07102984b411a27c353d919d2872de6b8990a9cf57c41ed5fa69da204b50ac` | `8f9c853332f999d7664d0309f09fa52a68e0f7e6cd64f6df3210a85c882c0bc1` |
| L2 logistic | `5becf61f5699c06105be3977f660698775973f3764054a9e1d616a7c4312d6f8` | `7bbffae6910fd09db1c5f36091dd5f10b225c9457d83698257c695fc51f307ad` | `94a9d008f53436a55da658fe8613fcd5d309ceac9d4d3175b76e4e46e1124a77` |
| HGB 1 | `ac9ba3904eb36627419db52dc665b7b3bc69c91a8088b60ea834890d0fab853b` | `f207e38b65724fa771aaf6dd0efb53c96728730848b10322e20edf6bf0d0755e` | `e247ebc21fbca6f624fb18a68cf64ccf33ea53a8555513526b54fb26a58d2ea1` |
| HGB 2 | `7a570581e6e94d821e6aab1e3e1072001bb83bd1d66a1b64d06f22dc65f9207a` | `0a7c962d82c3a1a124538048e8526a6dca1103ca595bfa0636b4d428ea93f439` | `fa85ed34d3e838219277e90b43679b9dfcc5fcd231a02db23896395e41f6f31f` |
| HGB 3 | `eed2c958dd3058ef5f7bad022ec0d1ea925ada7d05ead36795ee494bbb5835de` | `5f025670f3780a5b0a42662e26dedb4ea7fd71ddb0dd2e9c7fa262e0e656923b` | `57328b1a05526180f1ea3e8e3b6a892a0ae148d448a891fa087f09f56478e62f` |
| HGB 4 | `616212a3dc6bb51ff29f479b1120a07c9e7d33da0f41d362dc1036f2afcd5514` | `53079f294f9baf901c26d435213dab696f3564cee653db0579ff54bf7017dce9` | `25683de44b1d2705252ddaf70444330e7a5cbaf7926e1d7d541466404672b305` |
| HGB 5 | `a6a53c2a01d939fb28fc9eafbc73fa9869b9211cc6de491076435924fd3494cb` | `40d242f26501477a2eb946edeb3af3fd52501446873a42a472790bb550b6a655` | `f824e7720271725ea5edf8697f5dd9bc2cc204549c349444b6140b9b58e825b5` |

Existing weighted model/result/validation CSV: `d978b27599f38cc22a1ce1aa525cc9e9b5fd4335412ed7dca63db9d477325914`, `7dda36e76957169525ff8ca3c52a514ed04141f0e559b1fbb0c27471f1b3a81c`, `3adf4e730c5afdc5567274bf00dbaa3f4a1e033976a83b5087ff5b781d9c0a63`. Existing unweighted model/result/probability CSV/raw CSV: `3b4e4019312d60610dd0094c6697897a061611a60e7777ed7be35e133af9451c`, `4d671b97714d816aa28386e1ecf9aa264d324726a51c0a89440bb06218eaf95d`, `7be1cf1d844832c9c1e4cfdf0eb922775ba654db7d756c744e886ebe17ef0bce`, `908303e01e27b43184ba9d8fdd5290b5d17399191086202c0c0cdd15bc34f625`.

## Decision boundary and next step

The approved rule has been **applied for validation ranking**, but the result has not been accepted for the application. The unweighted model's diagnostic origin and repeated use of validation are material limits. No new test prediction was generated. No model was activated. The next concrete step is a human review of the full ranked validation comparison and exact unweighted model hash, including whether to freeze that model and its `0.2489517623052024` threshold in a new trusted artifact. Only a separate future authorization may export new frozen test predictions without labels; T230 remains separate and requires the matching historical snapshot, which is absent here.
