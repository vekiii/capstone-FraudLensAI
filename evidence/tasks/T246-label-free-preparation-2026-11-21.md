# T246 — verified T210 label-free EDA publication preparation

Date: 2026-11-21. [Original request](../../prompts/development/002-T246-label-free-snapshot-preparation.md). Status: **preparation and synthetic checks complete; no full-source pass or live EDA summary**. T246 remains open.

## Mechanism and authority

[`training_input._without_label`](../../backend/src/fraudlens/data/training_input.py) is the existing canonical accepted-row boundary. It requires exactly one byte marker `,"is_laundering":`, splits the raw bytes at that marker, discards the token up to the following field comma, and only then calls `json.loads` on the reconstructed **non-label** JSON. It rejects a missing marker and any non-label field set other than `_SOURCE_KEYS`. The canonical snapshot writer uses sorted-key JSON, placing the field before the permitted source fields. This is the same stripping boundary used by the earlier label-free feature publisher; the T230 evaluator separately used it before its explicitly authorized test-label access. The new EDA publisher reuses this boundary. It never calls `json.loads` on an entire accepted transaction or reads a label value from the returned mapping.

FR-015/019/020/036 prohibit label flow into runtime/public EDA, showcase subrange/record label inspection and label-derived rates. The permitted path hashes the accepted file's bytes for integrity—hashing necessarily processes every byte, including the opaque label token—but never interprets, counts, compares, emits or aggregates the token as a value. This distinction is why the existing verified T210 snapshot can be used without a separately supplied label-free copy. The API request path still reads only the small precomputed summary, never accepted rows.

## Read-only local receipt in this preparation

Read `manifest.json` and `COMPLETE` only; checked `accepted.jsonl` **stat size only**. Manifest SHA-256 and COMPLETE marker both equal `38e1cdee0e96f73abfc398ff2207c8b8fc1ed0c526a6872e56a1462e55edbb88`. It records source SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`, source/accepted/rejected `5,078,345/5,078,345/0`, accepted SHA-256 `8a8315288f24a387d1bd0ec3765ac9e64a6b5ce131a634952aee1b302bd9f9ba`, and accepted size `3,015,200,326` bytes; local stat matches. This is a **partial receipt**, not a new full-file hash verification. Historical T210/T230 evidence records full verification. T210 manifest has `warmup_count=null`; frozen independent T218 evidence supplies the expected 1,114,921 warm-up rows and UTC boundary.

## Prepared offline procedure (not executed on the full source)

1. [`publisher.py`](../../backend/src/fraudlens/eda/publisher.py) first compares the small manifest bytes with the independently pinned T210 digest, then calls unchanged `verify_completed_snapshot` to check COMPLETE, counts, accepted/rejections sizes and byte hashes. It requires the exact source hash, accepted hash/size and zero rejections. A mismatch stops before publication.
2. It opens the verified accepted stream only after the gate. Each line passes through `_without_label` **before JSON parsing**, then must have the expected source SHA, canonical transaction ID and consecutive source-row number. UTC timestamps are checked against the frozen warm-up end. Only the non-label mapping enters `aggregate_eda`.
3. The aggregate must reconcile all 5,078,345 accepted rows, 1,114,921 warm-up and 3,963,424 scoreable rows, source/accepted/rejected totals, and UTC coverage `2022-09-01T00:00:00Z` through `2022-09-18T16:18:00Z`. It keeps paid/received amount sums separate by currency, declares per-series denominators and any omitted amount currencies, and has no transaction IDs, accounts or target fields in output. The bounded summary is written to a new ignored path only after success and receives its own SHA-256; it is never overwritten.
4. The prepared [runner](T246-publish-eda.py) is an **unexecuted future command**: `PYTHONPATH=backend/src .venv/bin/python evidence/tasks/T246-publish-eda.py`. Before running, confirm sufficient resources and that `data/processed/t246-hi-small-eda-summary-v1.json` does not exist. The runner uses the pinned T210 snapshot and constants. Independently hash the resulting file, inspect only its aggregate counts/series metadata, set `EDA_SUMMARY_PATH` and `EDA_SUMMARY_SHA256` to the exact output/digest, and prove an actual 200 response from `GET /api/eda/summary`. If any gate fails, leave T246 open and do not point the API at the file.

## Synthetic RED/GREEN and limits

[`test_eda_publisher.py`](../../backend/tests/unit/test_eda_publisher.py) creates tiny synthetic completed snapshots. It uses **invalid JSON label tokens** that would make whole-row `json.loads` fail, then proves the resulting EDA summary equals one built from different label tokens. It checks absence of label text in output, manifest/accepted hash refusals, warm-up/coverage refusals, new-output-only publication, output digest and loading through `EdaService`. Initial run: **4 expected RED failures**, all at missing `fraudlens.eda.publisher`. Subsequent focused run: **15 passed** across publisher, aggregate and API tests; one existing Starlette/httpx warning. No real source or label token was read by these tests.

The prepared publisher has **not** been executed on the full T210 snapshot. Consequently the accepted-file SHA has not been rechecked in this task, actual EDA counts/distributions and runtime/resource use are unobserved, and a live API 200 is unproven. The old quality report is absent from this checkout; the summary currently records verified rejection counts and accepted-row category/time/amount aggregates, not a claimed missing-value report. T243 approval and T252 human review remain pending. No showcase replay, training, T230 repeat, commit or push occurred.

Final focused checks from the repository root:

- `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests/unit/test_eda_publisher.py backend/tests/unit/test_eda.py backend/tests/integration/test_eda_api.py` → **15 passed**, one existing Starlette/httpx deprecation warning.
- `.venv/bin/ruff check backend/src/fraudlens/eda backend/tests/unit/test_eda_publisher.py evidence/tasks/T246-publish-eda.py` → **All checks passed**.
- `git diff --check` → **passed** (no output).
