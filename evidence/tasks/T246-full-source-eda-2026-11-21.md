# T246 — one authorized full-source label-free EDA publication

Date: 2026-11-21. [Request](../../prompts/development/002-T246-full-source-eda-execution.md). One full-source aggregation attempt, no automatic retry. This follows [preparation](T246-label-free-preparation-2026-11-21.md). T246 completed for its backend endpoint and data-delivery criteria; T243 remains undecided and T252 lacks an actual reviewer.

## Preflight and identity boundary

Reviewed [`publisher.py`](../../backend/src/fraudlens/eda/publisher.py), [runner](T246-publish-eda.py), [`_without_label`](../../backend/src/fraudlens/data/training_input.py) and FR-035–037. `_without_label` discards the canonical `is_laundering` byte token **before** `json.loads` reconstructs non-label JSON; the returned mapping has exactly the non-label source keys. No full transaction JSON parse, target aggregation, target rate, record output or label display occurs. The verifier hashes full accepted bytes opaquely for integrity but does not interpret label values. API requests load only the bounded aggregate.

Before execution, local `manifest.json` SHA-256 and `COMPLETE` both equaled `38e1cdee0e96f73abfc398ff2207c8b8fc1ed0c526a6872e56a1462e55edbb88`; accepted stat size was `3,015,200,326` bytes and rejections size zero. The output did not exist. The runner's unchanged snapshot verifier then checked every manifest-listed file size and hash before aggregation, including accepted SHA-256 `8a8315288f24a387d1bd0ec3765ac9e64a6b5ce131a634952aee1b302bd9f9ba`, source SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`, and 5,078,345 accepted/zero rejected. An identity mismatch would have stopped before parsing rows or publishing.

Preflight: `df -h .` reported 717 GiB free; `memory_pressure -Q` reported 24 GiB physical memory and 62% system-wide free. The runner enforced a 4 GiB process peak-RSS ceiling at each 100,000-row checkpoint and after the last row. Its publisher writes only after complete count/warm-up/coverage reconciliation and uses a new temporary file plus no-overwrite hard link, cleaning the temporary file in `finally`. An interrupted or failed aggregation cannot publish a partial summary. The output path is Git-ignored.

## The single full-source attempt

Command from repository root (runner has no CLI arguments):

`set -o pipefail; /usr/bin/time -l env PYTHONPATH=backend/src .venv/bin/python -u evidence/tasks/T246-publish-eda.py 2>&1 | tee evidence/tasks/T246-execution-2026-11-21.log`

The [full progress log](T246-execution-2026-11-21.txt) records all 100,000-row checkpoints and final **5,078,345/5,078,345**. The runner reported 43.058 elapsed seconds and 50,020,352-byte observed peak RSS. The published aggregate SHA-256 is **`b8900338ca375b2d632b260a794634fb19408012a1c14fc66e2f7b097a111820`**, independently confirmed by `shasum -a 256`; file size is **17,279 bytes**, below the 1,048,576-byte limit. `/usr/bin/time -l` printed 43.15 real / 42.38 user / 0.66 sys seconds, then failed its own `sysctl kern.clockrate` call under the environment. Thus the shell pipeline exited **1 despite the runner completing and publishing successfully**. The runner was **not** repeated. Its output, hash and subsequent service/API checks establish completion; the wrapper failure is retained as diagnostic, not hidden.

The linked `.txt` log is a byte-for-byte archive of the Git-ignored `.log` created by the displayed command.

## Independent aggregate and API checks

Read only the 17,279-byte aggregate, never accepted rows, to independently validate SHA-256, strict `EdaSummary` schema, synthetic origin, exact dataset/source identities, 5,078,345 source and accepted, zero rejected, 1,114,921 warm-up, 3,963,424 scoreable, and UTC coverage `2022-09-01T00:00:00Z` through `2022-09-18T16:18:00Z`. Checked 30 series, matching bucket/value lengths <=366, finite nonnegative values, denominators <=accepted count, transaction-count series with denominator and sum 5,078,345, and 24 distinct amount `(side,currency)` series (12 paid, 12 received), each with its own currency, unit and denominator. `omitted_amount_currencies` explicitly reports three paid and three received currencies beyond the bounded displayed series. `quality_counts={}` is consistent with zero rejections; this checkout has no separate full-source missing-value report.

Byte checks found none of `is_laundering`, `transaction_id`, `source_row_number`, sender/receiver account or key fields, nor canonical per-row ID prefixes in the aggregate. A real local Uvicorn server, configured with `EDA_SUMMARY_PATH` at the ignored output and `EDA_SUMMARY_SHA256` at the digest, returned **HTTP 200** for `GET /api/eda/summary` (17,278 response bytes; JSON equals the trusted aggregate). The returned JSON passed the Feature 002 `EdaSummary` JSON Schema. An unsupported query returned **HTTP 422**. Separately, in-process HTTP calls using a missing path and a modified temporary copy each returned controlled **404 `dataset_unavailable`** without local paths in the response. Original aggregate SHA-256 was checked again unchanged. The initial sandbox blocked loopback bind/connect; the local-only server and curl were run with approved sandbox escalation, then the server was stopped.

Actual local-server command: `EDA_SUMMARY_PATH=/Users/ladylazarus/Desktop/FraudLensAI-StageC/data/processed/t246-hi-small-eda-summary-v1.json EDA_SUMMARY_SHA256=b8900338ca375b2d632b260a794634fb19408012a1c14fc66e2f7b097a111820 APP_MODE=fixture .venv/bin/uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8765`. Actual request: `curl --silent --show-error --output /private/tmp/fraudlens-t246-http.json --write-out 'HTTP %{http_code} bytes=%{size_download}\n' http://127.0.0.1:8765/api/eda/summary`. A second curl used `?partition=showcase` and returned 422. The negative check used `TestClient(create_app(eda_service=EdaService(path, expected_sha)))` on a missing temporary path and a modified temporary copy; neither referenced the original file for mutation.

## Final checks and limits

- Before full run, focused synthetic publisher/aggregate/API tests: **16 passed**, one existing Starlette/httpx deprecation warning; Ruff passed after an import-order fix.
- After full run: `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests/unit/test_eda_publisher.py backend/tests/unit/test_eda.py backend/tests/integration/test_eda_api.py backend/tests/integration/test_startup.py backend/tests/integration/test_results_api.py backend/tests/contracts/test_risk_contracts.py` → **30 passed**, one existing deprecation warning.
- `.venv/bin/ruff check backend evidence/tasks/T246-publish-eda.py` and `git diff --check` → **passed**.
- Full backend regression belongs to T249; it was not run for this bounded T246 unit. No EDA UI, training, test evaluation, label parsing, showcase replay, commit or push occurred. This is local synthetic capstone data delivery, not production approval or second-person reproduction.
