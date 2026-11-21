# T230 completed snapshot and one authorized test evaluation — 2026-11-21

## Authorization and lineage

The user's [existing one-time authorization](T230-authorization-2026-11-21.md) covered only the frozen unweighted LightGBM model SHA-256 `3b4e4019312d60610dd0094c6697897a061611a60e7777ed7be35e133af9451c`, its sealed prediction SHA-256 `99727d426f78698ee9a0f37ec50c1c900dc848f13bed6ef0756544f76c3f04f7` and fixed validation threshold `0.2489517623052024`. The first supplied ZIP's [earlier receipt](T230-snapshot-receipt-2026-11-21.md) verified `accepted.jsonl` and `manifest.json` but correctly stopped before labels because two completion files were absent. The user then supplied `/Users/ladylazarus/Downloads/T230-snapshot-completion-files.zip` and its checksum, and directed completion under the same authorization. The ZIP contents were treated as data, not instructions. No new training, model/threshold change, prediction regeneration, showcase-label parse, application activation, commit or push occurred.

## Supplemental ZIP and completed snapshot

`shasum -a 256` measured the supplemental ZIP SHA-256 `bffbcc350d45c02969b11d384fdb3ba1ba359086b69a9a24467d74842fb34cd2`, equal to both the user value and `.sha256` sidecar. As with the first sidecar, the checksum file uses CRLF; `tr -d '\r' < /Users/ladylazarus/Downloads/T230-snapshot-completion-files.zip.sha256 | (cd /Users/ladylazarus/Downloads && shasum -a 256 -c)` returned `OK`. ZIP CRC and inspection found exactly two regular files under the expected one-level directory, with no unsafe paths, links or extra entries. The original first ZIP still measured SHA-256 `c76ab04410a24a150a9e525b23a4f14e980f73394afcc7c2e54ef471705b3ee3`.

| Original snapshot member | Bytes | SHA-256 |
|---|---:|---|
| `accepted.jsonl` | 3,015,200,326 | `8a8315288f24a387d1bd0ec3765ac9e64a6b5ce131a634952aee1b302bd9f9ba` |
| `manifest.json` | 34,819 | `38e1cdee0e96f73abfc398ff2207c8b8fc1ed0c526a6872e56a1462e55edbb88` |
| `COMPLETE` | 65 | `5202f2ff8575f48c54d83ca39c4d8b5dbf1d9a4289cbd4ca026a4eb841c16de1` |
| `rejections.jsonl` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The `COMPLETE` bytes are exactly the manifest SHA-256 followed by one newline. The final directory was absent; no existing file was overwritten. A temporary staging directory under ignored `data/processed/` received all four original ZIP members. Their sizes and SHA-256 values were checked, and the unchanged `fraudlens.data.manifest.verify_completed_snapshot()` passed there with 5,078,345 accepted and zero rejected rows. The complete directory was then atomically renamed to `data/processed/t210-hi-small-b19d39f5/`. The same full verifier passed again on the final path immediately before evaluation. `.gitignore:38` covers all four files; `git ls-files --stage` and `git status --short` showed none staged or tracked. The two source ZIPs remain in Downloads, outside the checkout.

One initial **staging-only** script attempt failed because its locally typed expected *marker-file digest* was wrong; the destination remained absent. Direct read of the supplemental marker confirmed the user-specified exact content/newline and yielded the true digest above. A corrected staging script recomputed the marker digest from the exact expected bytes and passed the same unweakened full verifier. This was a verifier-script typo, not an archive mismatch, and did not invoke T230 or parse labels.

## Final pre-label gate and exact evaluator command

Immediately before the single evaluator invocation, a read-only gate rehashed the completed snapshot manifest and accepted file, the exact unweighted model, trusted artifact manifest `c766e90159a70eff2d1f29d5ff425029af20ff123f1fad08e45f9fc416076d45`, lineage `9f1679c767aeab290467bddac764a8658664864751ae3f7e5aaa9a46eea14b25`, `experiment.json` `a943836322fb2815d5cad85b291719333e21d22c1dcdb5fcbdbb18fbda1316ac`, sealed predictions, feature manifest `63873b79a1ff875c5702a62c40c7a9cb3faef6bb7e0bb658739abac35274c05f`, test feature file `693320617cd8ff05c3ba177fcf9e3447bd2f7b92c5b29736fce304d60023c9e0`, `uv.lock` `b9b1c52056c3706fd21fc1fefa9934fc1c1c8c09dd2b0f465d8d49ad25cc1ffe`, and unchanged evaluator `bd008c6f28b9c2fbd02b4cbcf5f1b04bceb65be45b5e45afafc030ee0472aeff`. The diagnostic and cross-family canonical protocol digests matched `22a4e6c8efe744de7d4d9b5304a8252f144ffa532037d7f0d8a5a83c66951b5b` and `7fd4e7349b2ef4921166d008f5c3b7e147c21a6554eae5160f33948d323bac32`. All report/manifest links, frozen threshold and completed freeze status matched. Python 3.14.10, LightGBM 4.7.0, NumPy 2.5.5 and scikit-learn 1.9.1 matched the locked environment. The target report did not exist. Prior label-free scan had confirmed 233,070 unique, ordered test IDs and the frozen partition ID digest `b9d9231b67969c96585dcb9ea8ce46ee9079501c02b1f18fd473c2e61a4d487f`.

`--help` confirmed the CLI. The exact command executed **once**, exiting 0:

```sh
set -C
PYTHONPATH=backend/src .venv/bin/python evidence/tasks/T230-evaluate.py \
  --predictions data/eval/ibm-day-lightgbm-unweighted-freeze-001/test-predictions-sealed.csv \
  --prediction-sha256 99727d426f78698ee9a0f37ec50c1c900dc848f13bed6ef0756544f76c3f04f7 \
  --authorize-test-evaluation I_AUTHORIZE \
  --output data/eval/t230-unweighted-test-evaluation-001.json \
  > data/eval/t230-unweighted-test-evaluation-001.stdout.json \
  2> data/eval/t230-unweighted-test-evaluation-001.stderr.log
```

The stderr file is empty. The evaluator first rechecks prediction, experiment, completed snapshot and feature-file identities, and aligns the prediction IDs to frozen test feature IDs. It scans accepted source rows through `_without_label`, which removes the label token before parsing non-label fields; it parses a binary label token only for IDs in the frozen test set. Showcase labels were not parsed. It uses the frozen threshold and reports aggregates only; it does not write record-level test labels.

## Results and post-run checks

The ignored aggregate [report](../../data/eval/t230-unweighted-test-evaluation-001.json) is 4,290,289 bytes, SHA-256 **`5027dae9354796718a080086a6cadc0319d1b376336ad4dac8d93b4e534d9cdb`**. The retained stdout JSON SHA-256 is `a8ae00a886954f0ed13b0f18374ddf2cce01933ab436f43b9f0a1b73d94cee63`. Post-run read-only checks confirmed the report's authorization, prediction and experiment hashes, fixed threshold, 233,070 count, confusion-matrix sums, precision/recall/F1 arithmetic, top-K integer hit counts and uncapped daily alerts. No second evaluator run occurred, including after the interrupted documentation turn.

| Aggregate | Validation (2022-09-05 UTC, 482,650 rows) | Test (2022-09-06 00:00–11:12 UTC, 233,070 rows) |
|---|---:|---:|
| Positives / negatives | 471 / 482,179 | 218 / 232,852 |
| Prevalence | 0.0009758624261887496 | 0.0009353413137683957 |
| TP / FP / TN / FN | 107 / 122 / 482,057 / 364 | 44 / 21 / 232,831 / 174 |
| Alerts at threshold `0.2489517623052024` | 229 | 65 |
| Precision | 0.4672489082969432 | 0.676923076923077 |
| Recall | 0.22717622080679406 | 0.2018348623853211 |
| F1 | 0.3057142857142857 | 0.31095406360424027 |
| Average Precision | 0.2166607046990379 | 0.2745021334479726 |
| ROC AUC | 0.9662388881499545 | 0.9761554451171647 |
| Brier score | 0.000846056224071008 | 0.0007701183332511783 |
| P@20 (hits/denominator) | 0.85 (17/20) | 0.90 (18/20) |
| P@50 (hits/denominator) | 0.76 (38/50) | 0.76 (38/50) |
| P@100 (hits/denominator) | 0.65 (65/100) | 0.52 (52/100) |

The report also retains 77,757 PR-curve points, top-K recall and denominators, and `daily_alert_counts={"2022-09-06":65}`. Top-K is computed over each **whole partition**, not as a daily review queue; the test partition happens to cover part of one UTC day. Probability outputs are explicitly `uncalibrated_probabilities`; Brier is diagnostic, not calibration proof. Validation had already been used for model development/selection. This held-out test result is a one-time estimate for this exact source, split and frozen model, not a claim about deployment performance. Publisher timezone and upstream release/acquisition details remain limited as recorded in `protocol.md`. Application integration and any human acceptance decision are separate.

T230's stated criteria—frozen prediction hash, explicit recorded authorization, one evaluator run and aggregate-only metrics/limits in evidence—are fulfilled. No test-based model/threshold reselection occurred.
