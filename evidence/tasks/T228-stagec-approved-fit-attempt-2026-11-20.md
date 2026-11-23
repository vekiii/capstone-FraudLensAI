# T228 Stage C approved fit attempt — 2026-11-20

- Date/time: 2026-11-20 19:34–19:35 CET (Europe/Belgrade).
- Status: **blocked before fitting; experiment incomplete**. No candidate model fit or validation comparison occurred.
- Authorization: [exact-hash approval](T219-stagec-protocol-approval-2026-11-20.md); [original development instruction](../../prompts/development/002-T228-stagec-approved-fit.md).
- Working directory: `/Users/ladylazarus/Desktop/FraudLensAI-StageC`; branch `feature/002-clean-start`, HEAD `aa1accac0ff90f2eb370618be15f145b3cc6bf2b`, existing local changes preserved. No commit or push.
- Runtime: project `.venv` Python 3.14.10; LightGBM 4.7.0, scikit-learn 1.9.1, NumPy 2.5.5, matching `uv.lock` entries. Lock SHA-256 `b9b1c52056c3706fd21fc1fefa9934fc1c1c8c09dd2b0f465d8d49ad25cc1ffe`.
- Approved candidate canonical SHA-256 `90b2aaa07590f771343e30f7843078f2dbd71d26679040cdafc33a5fbe5c67cf`; file-byte SHA-256 `fcdd833474f6fdf47b1bbbabfd003e2f9081e99c3506f229977d35f9a83085f7`. Candidate file unchanged.

## Preflight and actual command

`PYTHONPATH=backend/src .venv/bin/python evidence/tasks/T219-stagec-review-verify.py specs/002-data-and-risk-scoring/t219-training-protocol.ibm-day-60-20-20.macos-resource-review.candidate.json --expected-canonical 90b2aaa07590f771343e30f7843078f2dbd71d26679040cdafc33a5fbe5c67cf` exited **0** immediately before the attempt. It rehashed 18 implementation files, both manifests, 3 feature and 2 train/validation label JSONL files, `uv.lock`, and verified candidate lineage/methodology/protocol. Feature manifest SHA-256: `63873b79a1ff875c5702a62c40c7a9cb3faef6bb7e0bb658739abac35274c05f`; label manifest SHA-256: `5aee2e1d5f4f2ca7329fcc7b5b1ca0c808c4e8e39e84559e76a0d3e1a6add12c`. The verification hashes restricted label files as bytes and does not parse label rows.

The runtime version check printed `3.14.10 4.7.0 1.9.1 2.5.5`. A supplemental `.venv/bin/python -m pip --version` failed with `No module named pip`; this environment is managed by uv and that check is not a training prerequisite. A subsequent read-only lock inspection confirmed all three package versions and the lock hash. Both `data/eval/ibm-day-lightgbm-macos-resource-review-001` and its `.incomplete` sibling were absent, so the approved output name was used.

Executed once, with `PYTHONPATH=backend/src`, four threads, and no edits to grid/thresholds/limits:

```sh
PYTHONPATH=backend/src .venv/bin/python -m fraudlens.training.local_run \
  --features data/processed/t219-ibm-day-60-20-20-v1 \
  --labels data/processed/t219-ibm-day-60-20-20-labels-v1 \
  --protocol specs/002-data-and-risk-scoring/t219-training-protocol.ibm-day-60-20-20.macos-resource-review.candidate.json \
  --protocol-sha256 90b2aaa07590f771343e30f7843078f2dbd71d26679040cdafc33a5fbe5c67cf \
  --output data/eval/ibm-day-lightgbm-macos-resource-review-001 \
  --root . --n-jobs 4
```

Exit code **1**. Worker traceback ended at `backend/src/fraudlens/training/local_run.py:201` with `ValueError: source, feature or label manifest identities differ`; supervisor then raised `ResourceLimitError: worker exited with code 1`. This occurred before `_discover_vocab`, label-row reading, matrix construction or `fit_lightgbm_matrix_grid`. No fit started; the command was **not retried**.

## Read-only root-cause diagnosis and output state

Inspection of manifest top-level keys shows the transferred feature manifest has the correct `source_sha256` but **does not contain `feature_version` or `feature_order`** (both `.get(...)` return `None`). The runner at `local_run.py:201–202` requires those fields to equal `FEATURE_VERSION='hi-small-temporal-v1'` and the frozen 11-field `FEATURE_ORDER`, so its combined identity condition fails. The label manifest's source and feature-manifest link match. The protocol verifier accepted the real manifest structure and all hashes; its checks did not cover this extra runner expectation. No manifest, runner, candidate or expected hash was changed after the failure.

The guard retained only `data/eval/ibm-day-lightgbm-macos-resource-review-001.incomplete/status.json`:

```json
{"elapsed_seconds": 1.121, "peak_observed_rss_bytes": 150044672, "reason": "worker exited with code 1", "state": "incomplete"}
```

The requested final output path is absent. No `experiment.json`, model artifact, validation scores or sealed test predictions exist; therefore there are no candidate metrics or output hashes to report. The 150,044,672 bytes are the guard's observed prefit process-tree RSS, not a trained-model memory measurement. No test/showcase labels or T230 were accessed. RED/GREEN does not apply to this execution-only attempt; prior synthetic checks are in the [candidate review](T219-stagec-macos-resource-review-2026-11-20.md).

**Next step:** reconcile the runner's feature-manifest schema expectation with the frozen input contract, then prepare a new candidate binding any code change and obtain a new exact-hash approval before another research-data fit. This approval and this attempt do not authorize an automatic retry.
