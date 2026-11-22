# Stage C second approved FR-021 fit — user instruction, 2026-11-20

The user explicitly approved canonical SHA-256 `1ebac4f24aa198cfd1de70b96204676cb3fbd0cc07786296944c6ade0214f6be` for `specs/002-data-and-risk-scoring/t219-training-protocol.ibm-day-60-20-20.macos-preflight-schema-review.candidate.json`. The user accepted 0.1 s memory sampling and unavailable historical source/parent-manifest reproduction, and authorized **one second attempt** at eight LightGBM configurations with four threads, unchanged method and ceilings. The user required separate approval evidence; immediately preceding read-only candidate/implementation/data/lock/runtime verification; a free output and `.incomplete` path; exact command execution, monitoring and no parallel copy or automatic retry; on success, validation results, selected configuration and rationale, artifact reload, output digests, time/memory and structural/integrity-only test-prediction checks. T228/T229 evidence, next_work and index must reflect actual results. The user explicitly excluded test/showcase label access, T230, app activation, commit and push.

Exact authorized command:

```sh
PYTHONPATH=backend/src .venv/bin/python -m fraudlens.training.local_run \
  --features data/processed/t219-ibm-day-60-20-20-v1 \
  --labels data/processed/t219-ibm-day-60-20-20-labels-v1 \
  --protocol specs/002-data-and-risk-scoring/t219-training-protocol.ibm-day-60-20-20.macos-preflight-schema-review.candidate.json \
  --protocol-sha256 1ebac4f24aa198cfd1de70b96204676cb3fbd0cc07786296944c6ade0214f6be \
  --output data/eval/ibm-day-lightgbm-macos-preflight-schema-review-002 \
  --root . --n-jobs 4
```

The full original instruction and approval remain in this Codex chat. This prompt record preserves operational scope; observed results are in separate evidence.
