# T065 explanation review handoff — pending_human_review

Prepared 2026-11-14 from the frozen, exploratory T062 test scores. The actual `no_alert` model and rules runs contain zero published alerts. The label-free selection rule was fixed before inspection: choose up to five lowest SHA-256 transaction IDs among frozen test alerts, then fill from scored frozen test transactions. There were no alerts, so all five are scored transactions. No labels entered selection or the sample file.

Run from the repository root:

```sh
PYTHONPATH=backend/src .venv/bin/python backend/tests/phase8_review_sample.py --source data/processed/feature-002-ibm-v8-rules-work.sqlite --protocol evals/protocols/feature_002_v1.json --predictions evals/results/phase8/test_predictions.json --artifact-dir artifacts/feature-002-history-v1-20261114 --manifest-sha 2732691cb08daafba9d303ef6f3c8f616e03b3dc51505d3abb9772ceadd3919e --output evals/results/phase8/explanation_review.json
```

The author's run exited 0 and wrote ignored `evals/results/phase8/explanation_review.json`, containing five operational snapshots and both model/rules assessments per snapshot. The command requires the ignored frozen predictions and exact trusted artifact; the output path must be new because the script refuses overwrite. Selected IDs, in rule order: `D05cdc32fefc2bc14b78f9af568beebc5`, `D6a2f5a08dfc6682e836dacd6b5f4d604`, `Df1cedd9c73b6ef4bb6d663861efa6d9e`, `D785bf3b0961092d9069c1682cf7cd69d`, `Deb653f0394911b6ff982b2746fc2ddac`.

Another teammate should inspect all five against the recorded source facts, snapshot digest, run/model identity, units and explanation scale; for tree paths verify root-to-leaf reconstruction within the frozen 1e-8 tolerance and the explicit base/remainder; for rules verify R1–R3 conditions/arithmetic. Record reviewer identity/date, findings for each ID and any correction. Do not use private labels. The author generated the sample; no teammate review or signoff has occurred.

## Boosted full-run sample — 2026-11-14

From completed isolated `run_boosted_full_20261114_v3`, select the five alerts with highest score, breaking ties by transaction ID ascending. No private labels entered selection or this handoff. Ignored local source `evals/results/boosted-full-five-explanations.json` has SHA-256 `7d50bec8aba0b4e36c58a1a696de27ae4869fe650ba653618f04f35a9227a54f`. Each case has `history-v1` full coverage, method `boosted_sequential_probability`, explained scale `positive_class_estimate`, score kind `uncalibrated_probability_estimate`, and a partial top-three explanation. Contributions below are rounded for reading; use the JSON's full precision for the 1e-8 reconstruction check.

| Transaction / case | UTC event; operational facts | Score | Top contributions; base; remainder |
|---|---|---:|---|
| `D90fbf75213cb7bb1bdc1f3f91ec23dd5` / `C737e48e2a489a7f10bf7a71716e3bc65` | Sep 9 02:51; ACH, 48,014.36 Yuan paid and received | 0.9975916688635418 | format ACH +0.504085; currency Yuan +0.215734; paid amount +0.187014; base 0.008635664; remainder +0.082123938 |
| `D0adebff88899bbb3c98e9fb03b785df6` / `C0281c8396bb2a961e95f1b80ebeee0f7` | Sep 5 07:40; ACH, 51,805.35 Yuan paid and received; sender same-currency paid sum in prior 24h = 0 | 0.9975830657243046 | format ACH +0.750269; currency Yuan +0.135322; 24h sum 0 +0.069915; base 0.008635664; remainder +0.033440752 |
| `D6e00944c45c3f8307e5d65ef03edfd8d` / `C1b84af5218d0786128963eac213a69e9` | Sep 6 19:44; ACH, 89,709,263.78 Swiss Franc paid and received; sender 24h sum = 0 | 0.99757662559846 | paid amount +0.792379; format ACH +0.117397; 24h sum 0 +0.061620; base 0.008635664; remainder +0.017545107 |
| `D9dc186ae55ba66066b6781023bac7170` / `C906476436b96bd9e4646d10a6d09dc70` | Sep 9 13:15; ACH, 51,424.51 Yuan paid and received; sender 24h sum = 0 | 0.9973229122044224 | format ACH +0.736558; currency Yuan +0.149571; 24h sum 0 +0.061620; base 0.008635664; remainder +0.040937843 |
| `D26d712161d5bfa0d06da08cccaf5498b` / `C16b89849cf52390a3827f72899b40ca1` | Sep 9 23:36; ACH, 17,312.17 Euro paid and received; sender 24h sum = 0 | 0.9968474376592448 | format ACH +0.861192; paid amount +0.080628; 24h sum 0 +0.074746; base 0.008635664; remainder −0.028354062 |

Another teammate should record their name/date and a finding **for each row**: match case, transaction, dataset, run and snapshot digest to the saved source; compare each stated value and unit to the operational transaction/history snapshot; check method and score scale; sum full-precision base, three contributions and remainder to the saved score within 1e-8. In particular, verify that a zero 24h sum is strict-past same-currency history, that the large Swiss Franc amount is represented without unit conversion, and that the negative remainder in the fifth row is retained. These contributions are model-conditional sequential differences, not causal claims. T065 remains `pending_human_review` until another teammate performs and records the actual review.
