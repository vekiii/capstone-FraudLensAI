# T229 second freeze: selected unweighted LightGBM — 2026-11-20

## Decision and immutable origin

The user [selected the existing model and authorized this label-free export](T229-unweighted-freeze-decision-2026-11-20.md): native LightGBM SHA-256 `3b4e4019312d60610dd0094c6697897a061611a60e7777ed7be35e133af9451c`, fixed validation threshold **`0.2489517623052024`**. This is the later five-arm diagnostic `scale_pos_weight=1` model, ranked first by the separately approved FR-023 comparison on the **already used** validation set. The diagnostic protocol canonical SHA-256 is `22a4e6c8efe744de7d4d9b5304a8252f144ffa532037d7f0d8a5a83c66951b5b`; the cross-family protocol canonical SHA-256 is `7fd4e7349b2ef4921166d008f5c3b7e147c21a6554eae5160f33948d323bac32`. The approved JSONs, old outputs, prior weighted model and its sealed predictions remained unchanged. No new fit was authorized or performed; no model was accepted for application.

## Pre-export integrity and preprocessing recovery

Read `AGENTS.md`, current `next_work.md`, the prior T229 record, diagnostic/cross-family protocol/evidence, `local_run.py`, `artifacts.py`, the transferred feature manifest, and the T230 evaluator **as code**. The evaluator's future contract requires a prediction CSV with header `transaction_id,occurred_at_utc,score`, ordered IDs matching the frozen test feature file, and a sibling `experiment.json` containing `prediction_sha256.test`, `feature_manifest_sha256`, `validation_metrics.threshold` and `protocol_sha256`. The evaluator itself was **not run**.

Before native LightGBM parsing, the new exporter checks the selected model's exact SHA-256; the diagnostic result, saved validation score CSV and threshold; the completed FR-023 experiment/status byte hashes; the approved cross-family and diagnostic protocol lineage; current executable hashes and `uv.lock`; runtime Python 3.14.10 / LightGBM 4.7.0 / NumPy 2.5.5 / scikit-learn 1.9.1; transferred feature manifest and train/validation/test feature-file hashes; and the original weighted experiment's trusted artifact manifest. The old manifest SHA-256 `9010faab6c2ae1ab395817e371970f223b3cf3e08e368f4066c98d68cc4cdbfd` is tied to the original train-only preparation and contains 16 train-only payment-currency values and 7 train-only payment-format values (including each `__UNKNOWN__` bucket), exact feature order/version and 32 ordered model columns. This **existing** vocabulary was reused verbatim; no new vocabulary discovery, scaler fit or other preprocessing fit occurred. Exact train/validation/test feature-file hashes match the original report and transferred manifest. The model has 140 trees and 32 features. A separate read-only pre-export reproduction used this vocabulary and the exact model bytes; all 482,650 validation probabilities and IDs/timestamps matched the saved diagnostic CSV **exactly** (`max_abs_diff=0.0`). No validation label read was needed for this reproduction.

## RED/GREEN and checks before export

RED: `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests/unit/test_freeze_export.py` failed collection with the intended missing module `fraudlens.training.freeze_export`. The new [exporter](../../backend/src/fraudlens/training/freeze_export.py) validates the old identities before loading, uses the original frozen vocabulary and native model, checks exact validation reproduction, writes a new trusted artifact plus provenance manifest, and exports test scores without accepting a label argument or calling `fit`. It uses the existing `resource_guard` subprocess supervisor and `.incomplete` staging; final publication requires successful worker exit and resource/report checks. Synthetic tests cover exact validation reproduction, ordered CSV roundtrip, bad validation score, nonfinite test score and wrong ID hash. Final relevant regression command:

`PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests/unit/test_freeze_export.py backend/tests/unit/test_artifacts.py backend/tests/unit/test_resource_guard.py backend/tests/unit/test_local_run.py backend/tests/unit/test_diagnostic_run.py`

Result: **50 passed**, six existing LightGBM deprecation warnings, under process-monitor access. `.venv/bin/ruff check .` passed; `git diff --check` passed. Exporter SHA-256 `38d7c1cd0e0b8040489c56e110590fe3b7dbe45d39076dfcca013be6bed02c4b`; synthetic test SHA-256 `8094490a85d75b4ebfdb5bc58e9b092ed1f13f95546aefb949a7568121aa483a`. Existing `artifacts.py` SHA-256 `bf33f0f19423ef1b7efbc88ddb430a639602cdfe6f32f5ad9619c7b702430ca3`, `local_run.py` SHA-256 `dd08e9ac04657ec628e321b0fbf94c4b4fc5242cbc55e5a8fdcae189702cca6d`, `uv.lock` SHA-256 `b9b1c52056c3706fd21fc1fefa9934fc1c1c8c09dd2b0f465d8d49ad25cc1ffe`. The export code and all relevant current code hashes are also in the new `freeze-lineage.json`.

## One completed label-free export

The target `data/eval/ibm-day-lightgbm-unweighted-freeze-001` and its `.incomplete` sibling were absent before launch. Exact command, executed once with exit 0:

```sh
PYTHONPATH=backend/src .venv/bin/python -m fraudlens.training.freeze_export \
  --features data/processed/t219-ibm-day-60-20-20-v1 \
  --labels data/processed/t219-ibm-day-60-20-20-labels-v1 \
  --output data/eval/ibm-day-lightgbm-unweighted-freeze-001 \
  --root . --n-jobs 4
```

The `--labels` directory argument is used **only to verify its frozen manifest SHA-256** through the protocol contract; the exporter never opens label row files. The worker report says `fit_called=false`, `test_labels_read=false`, `showcase_labels_read=false`. No test metric was calculated. Supervisor `status.json` is `complete`, reason `null`, elapsed **6.321 s**, observed peak process-tree RSS **676,200,448 bytes**. macOS RSS is sampled at 0.1-second intervals and may miss a shorter descendant spike; the same 20 GiB initial disk, 10 GiB reserve, 8 GiB observed RSS and time ceilings were inherited. There is no remaining `.incomplete` sibling.

The new artifact writer copied the **exact** model bytes into `artifacts/selected-unweighted-lightgbm/model.txt`; the trusted `manifest.json` binds model SHA/size, feature version/order, 32 matrix columns, frozen train-only vocabularies, source, approved cross-family protocol, runtime version, seed and fixed validation threshold. The companion `freeze-lineage.json` binds the diagnostic and cross-family protocols, original vocabulary manifest, original and new model hashes, validation result and score hashes, transferred data/test partition identities, `uv.lock`, full export-code hashes, runtime, threshold and prediction SHA. The new `experiment.json` binds the trusted manifest, lineage, prediction SHA and threshold in the T230 evaluator's expected locations. These are **separate new output files**; no prior model, experiment or prediction was overwritten.

## Independent post-export verification and full hashes

After publication, a read-only pass authenticated the new artifact with `read_verified_artifact` using the independently recorded manifest digest, confirmed its bytes equal the original diagnostic model, created a **fresh** native LightGBM Booster and reproduced all saved validation probabilities exactly using the frozen vocabularies. The model still has 140 trees/32 features, and its manifest and experiment threshold remain exactly `0.2489517623052024`. It streamed the new test CSV alongside the **test feature file only** and checked all **233,070** rows, unique IDs, exact feature-file order and timestamps, finite scores in `[0,1]`, and the frozen test partition ID SHA-256 `b9d9231b67969c96585dcb9ea8ce46ee9079501c02b1f18fd473c2e61a4d487f`. Observed test-score range was `9.305900253928908e-13` to `0.9999974605522108`. The CSV and `experiment.json` satisfy the evaluator's static input contract; evaluator execution and test-label access remain unauthorized. The historical weighted test-prediction hash was rechecked unchanged.

| New output under `data/eval/ibm-day-lightgbm-unweighted-freeze-001/` | Full SHA-256 |
|---|---|
| `artifacts/selected-unweighted-lightgbm/model.txt` | `3b4e4019312d60610dd0094c6697897a061611a60e7777ed7be35e133af9451c` |
| `artifacts/selected-unweighted-lightgbm/manifest.json` | `c766e90159a70eff2d1f29d5ff425029af20ff123f1fad08e45f9fc416076d45` |
| `freeze-lineage.json` | `9f1679c767aeab290467bddac764a8658664864751ae3f7e5aaa9a46eea14b25` |
| `test-predictions-sealed.csv` | `99727d426f78698ee9a0f37ec50c1c900dc848f13bed6ef0756544f76c3f04f7` |
| `experiment.json` | `a943836322fb2815d5cad85b291719333e21d22c1dcdb5fcbdbb18fbda1316ac` |
| `status.json` | `c90cde7b7cfcaa6c258f467c06cef807993215d0562be10a776d586bf3ee436f` |

The old weighted model/prediction hashes remain `d978b27599f38cc22a1ce1aa525cc9e9b5fd4335412ed7dca63db9d477325914` / `cc63b5d3cfbfd4ce9a2fc13794e5e0e8c48758565128938abfc5e31fe844048f`. The new freeze does not change the historical result or its selected threshold `1.0`.

## Later T230 transfer requirements; **not authorization to run**

On the original workstation, first verify its existing T210 accepted snapshot at `data/processed/t210-hi-small-b19d39f5/` with the expected manifest SHA-256 `38e1cdee0e96f73abfc398ff2207c8b8fc1ed0c526a6872e56a1462e55edbb88` and completed marker. Transfer byte-for-byte the **new** `data/eval/ibm-day-lightgbm-unweighted-freeze-001/` directory, especially `test-predictions-sealed.csv` and its sibling `experiment.json`; keep the artifact and `freeze-lineage.json` for provenance. Ensure the transferred `data/processed/t219-ibm-day-60-20-20-v1/manifest.json` (SHA-256 `63873b79a1ff875c5702a62c40c7a9cb3faef6bb7e0bb658739abac35274c05f`) and `test.jsonl` (SHA-256 `693320617cd8ff05c3ba177fcf9e3447bd2f7b92c5b29736fce304d60023c9e0`) are present at their expected paths; they are needed by the existing evaluator to verify prediction IDs. Provide this decision/evidence and the approved diagnostic/cross-family protocol files for audit, plus the checkout with `evidence/tasks/T230-evaluate.py` SHA-256 `bd008c6f28b9c2fbd02b4cbcf5f1b04bceb65be45b5e45afafc030ee0472aeff` and compatible locked runtime. Preserve the source and prediction hashes after transfer. **Only a later separate explicit T230 authorization** may permit that evaluator to read test labels or calculate aggregate test metrics. No showcase labels or application activation is part of this transfer.
