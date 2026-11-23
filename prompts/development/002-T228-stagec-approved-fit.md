# T228 Stage C approved Mac fit — user instruction, 2026-11-20

The user explicitly approved the FR-021 candidate at `specs/002-data-and-risk-scoring/t219-training-protocol.ibm-day-60-20-20.macos-resource-review.candidate.json` with canonical SHA-256 `90b2aaa07590f771343e30f7843078f2dbd71d26679040cdafc33a5fbe5c67cf`. The user accepted the documented 0.1 s sampled-memory limitation and authorized eight defined LightGBM configurations on prepared project data using four threads.

The requested sequence was: preserve local changes; record approval separately without changing the candidate; immediately repeat read-only protocol/implementation/data/lock checks and confirm Python 3.14.10 plus locked packages; ensure both output and `.incomplete` path are absent, choosing a unique name if occupied; run the exact command below; monitor and report; retain incomplete output and diagnostics without automatic retry on failure. On success, inspect all eight validation results, selected model and threshold, artifact roundtrip, output hashes, time and memory. Test predictions may be checked for structure/integrity only. Update T228/T229 evidence, next_work and index. Do not access test/showcase labels, run T230, change methodology/ceilings, activate the model, commit or push.

```sh
PYTHONPATH=backend/src .venv/bin/python -m fraudlens.training.local_run \
  --features data/processed/t219-ibm-day-60-20-20-v1 \
  --labels data/processed/t219-ibm-day-60-20-20-labels-v1 \
  --protocol specs/002-data-and-risk-scoring/t219-training-protocol.ibm-day-60-20-20.macos-resource-review.candidate.json \
  --protocol-sha256 90b2aaa07590f771343e30f7843078f2dbd71d26679040cdafc33a5fbe5c67cf \
  --output data/eval/ibm-day-lightgbm-macos-resource-review-001 \
  --root . --n-jobs 4
```

The full original instruction and approval remain in this Codex chat. This record preserves the operational scope and exact command without claiming the attempt succeeded.
