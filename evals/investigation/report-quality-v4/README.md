# Report-quality v4: authored software controls

Team accepted the corrected protocol on 2026-11-17. This pack implements T096;
it is not a real-provider calibration result, generated-report evaluation or SC-003
acceptance. The original v8 failures, ratings and labels remain historical.

- `inputs/controls.json`: six public materialized report/evidence envelopes.
- `reference/expectations.json`: private exact control judgments.
- `reference/authored-ratings.json`: hand-authored software-test responses, **never
  model outputs**. Do not pass these to a model or use them as live calibration.
- `rating-schema.json`: closed v4 rating schema, matching the code.
- `manifest.json`: LF-normalized SHA-256 of those files, the implementation and
  canonical `prompts/evaluation/report-judge-v4.md`.

Only `project_packet` output may enter a future judge context. It drops references,
reviewer notes, outcome flags and extra nested metadata; supplies the identical
neutral field inventory; hashes the exact public role/report/evidence/unit content.
Never send this README, manifest, private directory or development prompts to judges.

Verify the authored software controls without credentials or network:

```powershell
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe -m fraudlens.investigation.judging_v4 --verify-controls evals/investigation/report-quality-v4
.venv/Scripts/python.exe -m pytest backend/tests/test_judging_v4.py -q
```

Expected verifier fields: `software_controls_pass=true`,
`model_quality_evaluated=false`. The six-control gate verifies test mechanics only.
Future real ratings must be assessed separately under the approved validation path.

Offline aggregation of a separately frozen and authorized future run:

```powershell
.venv/Scripts/python.exe -m fraudlens.investigation.judging_v4 --input evals/results/feature-003/NEW-RUN/envelope.json --output evals/results/feature-003/NEW-RUN/quality-v4.json
```

This command has no provider integration or network code and never overwrites an
existing output. The future envelope must already contain actual saved ratings,
not the authored responses here. No such run was performed for T096.
See [offline contract](../../../specs/003-ai-investigation/contracts/report-quality-v4.md)
and [reviewed validation path](../../../specs/003-ai-investigation/report-quality-v4-validation.md).
