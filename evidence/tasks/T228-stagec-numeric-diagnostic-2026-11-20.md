# T228/T229 Stage C numerical diagnosis and next experiment proposal — 2026-11-20

Status: **read-only post-hoc validation diagnosis and unapproved proposal**. Parent: [frozen validation audit](T228-stagec-validation-audit-2026-11-20.md), [completed experiment](T228-stagec-second-fit-2026-11-20.md), approved FR-021 canonical SHA-256 `1ebac4f24aa198cfd1de70b96204676cb3fbd0cc07786296944c6ade0214f6be`. Runtime: project `.venv`, Python 3.14.10, installed LightGBM 4.7.0. No fit, T230, test/showcase label read, output mutation, protocol/code edit, activation, commit or push. Only train features, saved validation features/labels, and the selected native model were read. The original source snapshot and training evaluation history remain unavailable.

## Procedure and references

Read `AGENTS.md`, `next_work.md`, approved candidate, prior audit, `backend/src/fraudlens/training/candidates.py`, `local_run.py`, `evaluation.py`, and `data/features.py`. Used read-only `PYTHONPATH=backend/src .venv/bin/python - <<'PY'` diagnostics to load the frozen LightGBM `Booster`, build the validation matrix with the frozen vocabulary, predict raw/probability scores at each retained tree count, check validation-label/ID alignment, calculate AP and deterministic P@20, inspect `dump_model()` leaves, and stream only train **feature** rows for numeric ranges. A second command reconstructed the first four unweighted clipped validation binary-logloss values. Inspected installed `lightgbm.sklearn.LGBMClassifier.fit`/`predict_proba` source and the model text. All analyses exited 0. No estimator `.fit` was called and no analysis output was written inside the frozen experiment.

Version-matched official references: [LightGBM 4.7.0 parameters](https://lightgbm.readthedocs.io/en/stable/Parameters.html) (`scale_pos_weight`, `boost_from_average`, `max_delta_step`, `lambda_l2`); [LightGBM 4.7.0 classifier API](https://lightgbm.readthedocs.io/en/stable/pythonapi/lightgbm.LGBMClassifier.html) (`sample_weight`, `predict_proba`); [v4.7.0 binary objective implementation](https://github.com/lightgbm-org/LightGBM/blob/v4.7.0/src/objective/binary_objective.hpp) (label weights, unweighted initial class prevalence, sigmoid); [v4.7.0 leaf-output formula](https://github.com/lightgbm-org/LightGBM/blob/v4.7.0/src/treelearner/feature_histogram.hpp) (`-gradient/(Hessian+lambda_l2)` and optional output cap); [v4.7.0 binary-logloss implementation](https://github.com/lightgbm-org/LightGBM/blob/v4.7.0/src/metric/binary_metric.hpp) (per-row loss capped by `-log(kEpsilon)`); [early-stopping documentation](https://lightgbm.readthedocs.io/en/stable/pythonapi/lightgbm.early_stopping.html).

## Confirmed model setup and initial score

The selected native model has `objective=binary sigmoid:1`, `boost_from_average=1`, `scale_pos_weight` displayed in native text as `968.536`, `is_unbalance=0`, `learning_rate=0.05`, `num_leaves=31`, `min_data_in_leaf=200`, `min_sum_hessian_in_leaf=0.001`, `lambda_l1=0`, `lambda_l2=0`, `max_delta_step=0`, 4 threads, deterministic CPU and 4 exported trees. The report gives the full Python weight `1,168,055 / 1,206 = 968.5364842454395`; native text rounds parameter display. The fit call has **no** `sample_weight`, `class_weight`, `init_score`, `eval_sample_weight`, or `eval_class_weight`; the separate histogram-gradient code's `sample_weight` does not apply to this LightGBM run. Installed wrapper source confirms only explicit/class weights would populate dataset weights; the selected fit supplied neither.

Train prevalence is `1,206 / 1,169,261 = 0.0010314207007674078`. With `boost_from_average=1` and no per-row weights, the v4.7.0 binary objective starts from the **unweighted** train prevalence, giving initial probability `0.0010314207007674078` and raw logit `-6.87578615301562`. The positive-class weight enters gradient/Hessian calculations after this initialization; it does not turn the starting probability into 0.5. If applied to the prior as a hypothetical sample weight, the weighted prevalence would be 0.5, but that is **not** the initialization implemented here. The first exported tree includes this initial score in its leaf outputs, so the model file alone does not expose a separate zero-tree prediction.

## Tree-by-tree numerical behavior

Read-only predictions on all 482,650 frozen validation feature rows:

| Retained trees | Raw margin minimum | Raw margin maximum | Largest new-tree absolute shift | Exact probability 0 | Exact probability 1 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | -6.925837776062751 | 39.489066649872846 | baseline/tree 0 | 0 | 13,735 |
| 2 | -174565.99401238462 | 38.30341129791052 | 174,559.06817460855 | 13,192 | 12,279 |
| 3 | -199645.6591434974 | 196825.7778419071 | 347,244.2107292479 | 21,317 | 2,969 |
| 4 | -737765.638804412 | 16101669.349779349 | 16,101,631.32680808 | 22,105 | 14,796 |

The first tree already creates probability 1.0 for many rows; huge signed raw moves begin at tree 2 and the largest positive move appears at tree 4. Extremal leaves and their stored training-row/Hessian aggregates:

| Tree | Minimum leaf output (count; Hessian sum) | Maximum leaf output (count; Hessian sum) |
| ---: | --- | --- |
| 0 | -6.925837776062751 (2,498; 2.573831426445394) | 39.489066649872846 (33,938; 785.6398687150795) |
| 1 | -174559.06817460855 (6,875; 0.0019603684969672587) | 4.99812318174008 (2,643; 7.41958680394165) |
| 2 | -199667.82505769035 (6,113; 0.0014997412572452969) | 347244.2107292479 (6,323; 0.001673524850048124) |
| 3 | -563239.3157323048 (13,533; 0.0011794275051525407) | 16101631.32680808 (39,514; 0.0012655414028230954) |

The tiny Hessian sums are just above the configured 0.001 leaf floor. With zero L2 and no output cap, the official leaf formula permits very large updates. This is direct evidence of the **proximate numerical mechanism** for the large raw scores. The current artifact does not establish which upstream factor (class weighting, low prior, feature distribution, or their interaction) caused those particular gradients/Hessians; that requires a controlled refit. LightGBM's official parameter documentation also warns that `scale_pos_weight` can worsen probability estimates.

## Input and preprocessing checks

The runner uses nine nonnegative numeric features and train-only one-hot vocabularies for currency/format, producing a 32-column `float64` matrix. It does not standardize numeric magnitudes. Streaming all **1,169,261 train feature rows** found zero nonfinite and zero negative numeric values. The validation matrix has zero nonfinite and zero negative numeric cells. For every numeric field, the validation minimum/maximum lies inside the train minimum/maximum; no validation numeric value exceeds the train range. Numeric values can nevertheless be large: train `sender_paid_sum_same_currency_24h` maximum `1,012,952,828,108.63`, train `receiver_received_sum_same_currency_24h` maximum `1,013,023,564,923.9`; validation maxima for both are `147,741,507,365.13`. Train count-feature maxima are 26,368 sender and 538 receiver; validation maxima are 18,663 sender and 80 receiver. `current_amount_paid_log1p` is bounded between about `1e-6` and 27.16 on train, 25.67 on validation. These checks exclude NaN/inf, negatives and validation out-of-range values as an observed explanation; they do not prove that feature scale or tree binning has no effect.

## Post-hoc raw-score ranking, not an approved result

Among the **14,796** rows whose stored probability is exactly 1.0, the frozen model has **118 distinct raw margins**, spanning `36.983166293975835` to `16101669.349779349`; the entire validation set has 378 distinct raw margins. Thus probability saturation discards real ordering information. With the same `(-score, transaction_id)` Unicode-codepoint tie rule, **raw-score validation AP is `0.020062480640418316` and raw-score P@20 is `0.55` (11/20)**. For comparison, frozen probability AP is `0.013226874634255597` and P@20 `0.70` (14/20). The largest raw margin is itself shared by **1,718** rows, including 56 positives, so raw P@20 still depends strongly on ID ordering. All raw top-20 rows belong to the probability-1.0 group. These post-hoc numbers are diagnostic only: they do **not** replace the approved selection, threshold, `experiment.json`, model or test predictions.

## Class weighting, logloss and short best iterations

The positive-class weight changes training gradients/Hessians, while the validation call supplies no evaluation weights. Early stopping uses **unweighted validation `binary_logloss`**, first metric only, patience 50, not validation F1/AP/P@20. The final candidate ranking uses F1 from probability scores at each candidate's best logloss iteration. The saved best iterations are 5, 4, 5, 2, 4, 2, 2, 2; only candidate 1's selected four-tree model is retained. These facts make an early best iteration plausible without making short training itself a defect.

For the selected exported model's first four trees, a read-only reconstruction of LightGBM's **clipped** unweighted validation binary-logloss formula gives approximately `4.5759720`, `3.4236194`, `2.5965820`, `2.5613563`. The official metric caps a misclassified probability loss at about `-log(1e-15) = 34.54`; it cannot reflect the full cost of margins in the millions. As a separate diagnostic, a numerically stable **unclipped** logistic loss on raw margins rises to about `437,732.92` by tree 4. This contrast is expected from the metric definition, not evidence of an implementation bug. The four reconstructed values are **not** a saved early-stopping history: the original run retained neither `evals_result_` nor total rounds, so the later trajectory and exact stopping trigger cannot be established without a new fit.

## Proposed small controlled experiment — pending separate review and approval

Use **only the existing train/validation**, same frozen input bytes and feature order, train-only vocabulary, candidate-1 tree shape (31 leaves, 0.05 learning rate, 200 minimum child samples), seed 42, CPU/four threads, 1,000 round cap, validation binary-logloss callback with patience 50, same 8 GiB/time/disk resource guard and fresh distinct output directory. Fit exactly these **five predeclared arms**, one parameter change at a time; this is a diagnostic study, not a repeat of the eight-candidate approved run or a new approved model-selection result:

| Arm | Change from selected configuration | Hypothesis tested | Held fixed |
| --- | --- | --- | --- |
| A | None (`scale_pos_weight=968.5364842454395`, `boost_from_average=true`, `lambda_l2=0`, `max_delta_step=0`) | Reproduces observed saturation with full history and per-arm artifacts. | All shared settings above. |
| B | `scale_pos_weight=1` | Removes the large positive gradient/Hessian multiplier; tests whether weighting is necessary for giant leaves/saturation. | A except weight. |
| C | `boost_from_average=false` | Starts raw margin at 0 instead of about -6.876; tests sensitivity to prior initialization under the same class weight. | A except initialization. |
| D | `lambda_l2=1` | Adds a denominator to leaf updates; tests whether tiny Hessian with no L2 is the proximate driver. | A except L2. |
| E | `max_delta_step=1` | Explicitly caps an individual learned leaf update (0.05 after learning rate); checks whether bounding updates prevents saturation even with current weighting. | A except leaf-output cap. |

For **every arm**, persist ordered validation probability and raw-score CSVs (same IDs), full threshold/confusion/precision/recall/F1/AP/P@20 metrics under a predeclared common rule, raw-score diagnostic AP/P@20 separately, `best_iteration`, **total rounds trained**, per-round validation binary-logloss history and callback result, full fit parameters and native model, per-tree leaf extrema/Hessian summaries, counts at exact 0/1, score quantiles, distinct-score counts, largest and top-20 boundary tie sizes, and resource measurements/hashes. Keep artifacts from unsuccessful arms marked incomplete. Compare saturation and ranking at the selected best iteration and at predeclared early checkpoints, without tuning arms after viewing validation outcomes. Freeze the comparison plan and new protocol/hash for human review **before** any fit; prior approval covers only the original eight-candidate experiment and does not authorize this study. Do not produce test predictions or read test/showcase labels.

**Interpretation limit:** validation already served early stopping, model selection and this diagnosis. Future train/validation outcomes are **not independent evidence of generalization**. No result from the proposed study may silently replace the frozen model or its official metrics.

**One next step:** review the five-arm design and decide whether to authorize a separately hashed diagnostic protocol; no fit is authorized by this record.
