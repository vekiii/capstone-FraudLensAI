# T228/T229 Stage C validation audit — 2026-11-20

Scope: read-only diagnosis of `data/eval/ibm-day-lightgbm-macos-preflight-schema-review-002` under approved FR-021 canonical SHA-256 `1ebac4f24aa198cfd1de70b96204676cb3fbd0cc07786296944c6ade0214f6be`. This audit used only saved validation scores, corresponding validation labels and validation features, the frozen selected model, report, status and source code. No fit, test/showcase label access, T230, artifact change, activation, commit or push. The original output directory remains intact; these notes are separate.

## Commands and method

Read `AGENTS.md`, `next_work.md`, the approved candidate and [completed-attempt evidence](T228-stagec-second-fit-2026-11-20.md). Inspected `evaluation.py`, `candidates.py`, `local_run.py`, the output inventory and selected model text. Ran two read-only `.venv/bin/python` heredoc analyses with `PYTHONPATH=backend/src`: (1) CSV/validation-label ID alignment, NumPy counts/quantiles, approved `choose_threshold` and `rank_lightgbm_candidates`, independent confusion-matrix arithmetic, `sklearn.metrics.average_precision_score`, explicit `(-score, transaction_id)` sort, SHA-256 checks; (2) validation feature matrix construction using the frozen artifact vocabulary and `lightgbm.Booster(model_file=...)` probability/raw-score predictions, with no `.fit` call. A third read-only model dump measured tree leaf-value ranges. All commands exited 0. No output files were created inside the experiment.

## Selected candidate: exact validation reconstruction

CSV and label JSONL IDs align row for row for **482,650** records, with **471** positive and **482,179** negative validation labels. The approved distinct-score positive-F1 rule selects exactly `1.0` (binary64 `0x1.0000000000000p+0`), so the displayed value is **not rounded**. The saved report, selected candidate ranking and independently recomputed values agree.

| Measure | Recomputed validation value |
| --- | ---: |
| TP / FP / TN / FN | 286 / 14,510 / 467,669 / 185 |
| Alerts (`score >= 1.0`) | 14,796 |
| Precision | 0.01932954852662882 |
| Recall | 0.6072186836518046 |
| F1 | 0.03746643086395494 |
| AP (independent scikit-learn check) | 0.013226874634255597 |
| Precision@20, score descending then Unicode transaction ID ascending | 0.7 (14/20) |

`experiment.json` agrees on threshold, confusion matrix, all listed metrics and selected candidate **1**. Its F1 is the largest in the eight-candidate report, so the final candidate tie rules were not needed. These are validation results only; test performance remains unmeasured.

## Other candidates and training history

Only `validation-scores.csv` for selected candidate 1 and its native model are published. The output inventory has no score CSVs, model files or evaluation histories for candidates 0 and 2–7. Their precision, recall, chosen thresholds and actual built-tree counts therefore cannot be independently recovered from the retained outputs without another fit. No fit was run for this audit. Recorded aggregate values are:

| # | Leaves | Rate | Min child | Best iteration | Built trees available | F1 | AP | P@20 | Precision / recall / threshold |
| ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- |
| 0 | 31 | 0.05 | 50 | 5 | no model retained | 0.0351520709154822 | 0.01483751573759345 | 0.60 | scores not retained |
| 1 | 31 | 0.05 | 200 | 4 | **4** in selected artifact | 0.03746643086395494 | 0.013226874634255597 | 0.70 | reproduced above; threshold exactly 1.0 |
| 2 | 31 | 0.10 | 50 | 5 | no model retained | 0.02123480686573112 | 0.008761777576228506 | 0.70 | scores not retained |
| 3 | 31 | 0.10 | 200 | 2 | no model retained | 0.020936998667645538 | 0.008877525570238142 | 0.65 | scores not retained |
| 4 | 63 | 0.05 | 50 | 4 | no model retained | 0.0247346251053075 | 0.010174739606097676 | 0.65 | scores not retained |
| 5 | 63 | 0.05 | 200 | 2 | no model retained | 0.03672021698310036 | 0.00583432202158949 | 0.75 | scores not retained |
| 6 | 63 | 0.10 | 50 | 2 | no model retained | 0.02272930648769575 | 0.009645897691599136 | 0.65 | scores not retained |
| 7 | 63 | 0.10 | 200 | 2 | no model retained | 0.02306615543789179 | 0.009750364403629596 | 0.65 | scores not retained |

The code fits with binary log loss on the validation set, `n_estimators=1000`, and `lgb.early_stopping(50, first_metric_only=True, verbose=False)`. The selected model export explicitly uses `num_iteration=model.best_iteration_`, hence its four stored trees do **not** establish how many rounds were actually trained. The model text contains `[early_stopping_round: 0]` and `[first_metric_only: 0]`; these serialized parameter defaults do not preserve the Python callback configuration or an evaluation history. Neither `experiment.json` nor the model stores `evals_result_` or total rounds trained. Thus best iterations 2–5 are verified as recorded, selected exported trees are verified as four, and full training histories/tree counts for other candidates are unavailable. The report's 9.589 seconds for eight fits and 29.084 seconds supervisor duration are observations; short duration alone is not proof of a faulty fit.

## Score saturation and Precision@20 ties

The selected scores have **100 distinct binary64 values**; none is NaN or infinite. Exactly **22,105** are 0 and **14,796** are 1. The 1.0 group contains **286 positives** and occupies the entire top 20, as well as every alert at the selected threshold. Next score groups are `0.9999999999999998` (127 rows), `0.9999999999999982` (413), `0.999999999999998` (8), `0.9999999999999973` (2) and `0.9999999999999956` (295). Min/mean/max are `0.0` / `0.11737657646074244` / `1.0`.

| Quantile | Score |
| ---: | ---: |
| 0%, 0.1%, 1% | 0.0 |
| 5% | 6.8546717017216374e-133 |
| 10% | 3.167190796993911e-05 |
| 25%, 50% | 5.9369814934958295e-05 |
| 75% | 0.0004635449034174054 |
| 90% | 0.999998317072981 |
| 95% | 0.999999985676084 |
| 99%, 99.9%, 100% | 1.0 |

The exact approved ordering `(-score, transaction_id)` yields 14 positives among the first 20. Since all those 20 are tied by score within a **14,796-row** group, the model scores alone do not order them. Arbitrary choices within this tied group could produce P@20 anywhere from 0 to 1; the reported 0.7 is deterministic under the protocol's ID rule but is strongly dependent on that rule and should not be read as fine-grained model discrimination.

`local_run.py` calls `model.predict_proba(validation, num_iteration=model.best_iteration_)[:, 1]` and writes each float with `.17g`; it does not apply a second sigmoid or clipping. Reloading the frozen four-tree LightGBM model and predicting the **same 482,650 validation feature rows** gives exactly equal binary64 probabilities to those parsed from the saved CSV (`max abs difference 0`, mismatch count 0). Native raw margins passed through `scipy.special.expit` also match exactly (`max abs difference 0`); applying a further sigmoid to probabilities does not (max difference 0.5). The saved model has `objective=binary sigmoid:1`, and native raw margins span approximately `-737765.64` to `16101669.35`; margins for saved 1.0 scores start at `36.983166293975835`. Thus the exact 0/1 probabilities reflect numerical saturation of very large native margins, not CSV rounding, a second sigmoid or explicit clipping. Dumped tree leaf-value absolute maxima rise from about 39.49 in tree 0 to 174,559.07, 347,244.21 and 16,101,631.33 in trees 1–3. This is a concrete model-output diagnostic, not proof of a specific training-code defect.

The train-only class weight in the report is `1,168,055 / 1,206 = 968.5364842454395`; the fitting code passes that ratio as `scale_pos_weight`. The saved model text reports rounded `[scale_pos_weight: 968.536]`, along with binary objective, 0.05 learning rate, 31 leaves, 200 minimum child samples, four threads, seed 42, deterministic CPU and column-wise training. The text's decimal formatting does not show the full fit-time Python float. No validation-label-derived weight was found.

## Frozen-output integrity and conclusion

Read-only SHA-256 rechecks match the completed-attempt evidence: selected `model.txt` `d978b27599f38cc22a1ce1aa525cc9e9b5fd4335412ed7dca63db9d477325914`; artifact `manifest.json` `9010faab6c2ae1ab395817e371970f223b3cf3e08e368f4066c98d68cc4cdbfd`; `experiment.json` `7dda36e76957169525ff8ca3c52a514ed04141f0e559b1fbb0c27471f1b3a81c`; validation CSV `3adf4e730c5afdc5567274bf00dbaa3f4a1e033976a83b5087ff5b781d9c0a63`; sealed test predictions `cc63b5d3cfbfd4ce9a2fc13794e5e0e8c48758565128938abfc5e31fe844048f`; `status.json` `9b7b45eb3d54fd1bf6ae5b7da57a4db9cee6dbde3e9eeecaa54ae7ac35b28ee0`. The test-prediction file was **hashed only**, not joined with labels or evaluated.

**Conclusion:** selected validation metrics, ranking, threshold and saved probabilities are internally consistent; no concrete metric or score-serialization implementation error was found. The concrete limitation is extreme probability saturation and a 14,796-way top-score tie, making P@20 mostly an ID tie-break statistic. Candidate-specific precision/recall/thresholds and training histories for the other seven were not retained. **Next step:** human review of this tie/saturation diagnostic before any separate decision about T230 or a future protocol revision; preserve the frozen run unchanged.
