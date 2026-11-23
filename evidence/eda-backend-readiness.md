# EDA backend readiness investigation

**Date:** 2026-11-23
**Scope:** read-only investigation of the current local `GET /api/eda/summary` 404. No source data, protected labels, individual rows, model artifacts, code, or configuration were changed.

## Finding and confidence

The current backend cannot serve a **configured, trusted EDA summary**. Its API returns HTTP 404 `dataset_unavailable`, and the documented T246 aggregate is absent at `data/processed/t246-hi-small-eda-summary-v1.json` in this checkout. The investigating PowerShell process has neither `EDA_SUMMARY_PATH` nor `EDA_SUMMARY_SHA256` set. The running server reports `mode=fixture`, which is the intentional default; **fixture mode alone does not disable EDA**. A prior T246 run proved that the same endpoint returns 200 in fixture mode when the two EDA variables point to a verified summary.

The exact `EdaUnavailable` branch in the already running server is **not observable from its safe HTTP response**. This investigation did not inspect that process's inherited environment. It could have no EDA variables, an inaccessible path, a wrong digest, or another invalid artifact. The absent documented local summary is a confirmed missing prerequisite; the unset variables are confirmed for this shell only. No backend code change is indicated by the evidence.

## Route and loading trace

1. [Vite proxy](../web/vite.config.ts) forwards `/api` from port 5173 to the local FastAPI server on port 8000.
2. [Settings](../backend/src/fraudlens/settings.py) default `APP_MODE` to `fixture` and read `EDA_SUMMARY_PATH` and `EDA_SUMMARY_SHA256` independently. The EDA path has no default.
3. [Application construction](../backend/src/fraudlens/main.py) creates `EdaService` with those settings. Model mode is a separate opt-in and is not required for EDA.
4. `GET /api/eda/summary` rejects **any** query string with 422 before loading. Otherwise it calls `EdaService.load()`. It catches `EdaUnavailable` and returns the fixed, path-free 404 `dataset_unavailable` response.
5. [Service](../backend/src/fraudlens/eda/service.py) requires a path and lowercase 64-hex independent digest; refuses symlinks, missing/non-file paths and files over 1 MiB; reads the bounded bytes; checks their SHA-256 **before** strict JSON validation; and requires embedded `source_sha256` to equal `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`. File/parse/validation errors also become `EdaUnavailable`. The endpoint does not scan a raw CSV, accepted rows, or generate aggregates on request.
6. The [API contract](../specs/002-data-and-risk-scoring/contracts/api.md) requires a previously generated, independently hash-pinned, bounded, label-free aggregate. Its one recorded T246 summary digest is `b8900338ca375b2d632b260a794634fb19408012a1c14fc66e2f7b097a111820`.

## Current environment and dependencies

| Check | Observed result | Limit |
|---|---|---|
| `GET http://127.0.0.1:8000/api/health` | 200 `{"status":"ok","mode":"fixture"}` | Confirms running mode, not EDA artifact settings. |
| `GET http://127.0.0.1:8000/api/eda/summary` | 404 `{"error":{"code":"dataset_unavailable","message":"EDA summary is unavailable."}}` | Deliberately does not disclose the failing validation branch. |
| Same route with `?partition=test` | 422 `invalid_request` | Confirms query rejection before EDA loading. |
| Investigating shell `APP_MODE` | Unset | Server process environment was not inspected. |
| Investigating shell `EDA_SUMMARY_PATH`, `EDA_SUMMARY_SHA256` | Both unset | Server process environment was not inspected. |
| Documented T246 summary path | Absent | No local approved aggregate bytes to hash or serve at that path. |
| `data/processed/t210-hi-small-b19d39f5/manifest.json` | Present, 34,819 bytes; SHA-256 `38e1cdee0e96f73abfc398ff2207c8b8fc1ed0c526a6872e56a1462e55edbb88` | Small metadata only was read. |
| T210 `COMPLETE` marker | Present; equals the manifest digest | Does not substitute for full snapshot verification. |
| T210 `accepted.jsonl` | Present; size 3,015,200,326 bytes, matching manifest | Contents and actual accepted-file digest were **not** read or rehashed in this task. Manifest records digest `8a8315288f24a387d1bd0ec3765ac9e64a6b5ce131a634952aee1b302bd9f9ba`. |
| T210 `rejections.jsonl` | Present; zero bytes | Contents were not read. |
| T210 manifest identity | Source SHA `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`; 5,078,345 source/accepted, zero rejected | Manifest claims match [T210 evidence](tasks/T210.md) and [T246 evidence](tasks/T246-full-source-eda-2026-11-21.md); full current file integrity was not checked. |
| `data/raw/HI-Small_Trans.csv` | Present; size 475,664,283 bytes | Not needed by the runtime endpoint. Contents/digest not checked. |

The T246 aggregate was previously generated and verified on another local checkout, then served successfully by Uvicorn with `APP_MODE=fixture`, `EDA_SUMMARY_PATH` and `EDA_SUMMARY_SHA256`; see [T246 execution](tasks/T246-full-source-eda-2026-11-21.md). That historical success does not establish that the aggregate is present or configured on this Windows checkout.

## Supported activation path and missing prerequisites

**Preferred if the approved T246 aggregate can be obtained through an authorized team transfer:** place that exact aggregate in an ignored local path; independently verify its SHA-256 equals the T246 digest above; set `EDA_SUMMARY_PATH` to its absolute path and `EDA_SUMMARY_SHA256` to the independently verified digest **in the same PowerShell session that starts a new backend process**; keep `APP_MODE=fixture` if model mode is not otherwise required; then start the existing Uvicorn app and request the endpoint. A successful service load also verifies the embedded source identity and strict schema. Do not point the service at a file that fails any check. No contract or backend change is needed for this path.

**If the trusted aggregate cannot be restored:** the repository has an offline [publisher](../backend/src/fraudlens/eda/publisher.py) and the exact T210 [runner](tasks/T246-publish-eda.py). Its required inputs are the complete, independently verified T210 snapshot (manifest, `COMPLETE`, accepted and rejections files, pinned source/accepted identities), a new ignored output path, and a separately authorized full-source pass. It verifies snapshot byte hashes before streaming non-label facts and refuses to overwrite an existing output. The runner imports POSIX `resource`, which is unavailable in the checked Windows Python environment, so the recorded runner command cannot be assumed to work here unchanged. A supported POSIX environment or a separately reviewed Windows invocation of the existing publisher is needed. **No publication was run in this investigation.** The original raw CSV alone is insufficient for the runtime API.

### Safe verification commands (PowerShell, repository root)

These read only configuration status, small metadata, or the bounded aggregate. They do not parse protected rows:

```powershell
Test-Path -LiteralPath 'data/processed/t246-hi-small-eda-summary-v1.json' -PathType Leaf
(Get-FileHash -LiteralPath 'data/processed/t210-hi-small-b19d39f5/manifest.json' -Algorithm SHA256).Hash
(Get-Content -LiteralPath 'data/processed/t210-hi-small-b19d39f5/COMPLETE' -Raw).Trim()
curl.exe -sS -i http://127.0.0.1:8000/api/health
curl.exe -sS -i http://127.0.0.1:8000/api/eda/summary
```

Once an authorized aggregate is present, check its digest **before** configuring a new server:

```powershell
$summaryPath = (Resolve-Path -LiteralPath 'data/processed/t246-hi-small-eda-summary-v1.json').Path
(Get-FileHash -LiteralPath $summaryPath -Algorithm SHA256).Hash.ToLowerInvariant()
# Compare the result independently with b8900338ca375b2d632b260a794634fb19408012a1c14fc66e2f7b097a111820.
# Only after a match, in the terminal that will start Uvicorn:
$env:EDA_SUMMARY_PATH = $summaryPath
$env:EDA_SUMMARY_SHA256 = 'b8900338ca375b2d632b260a794634fb19408012a1c14fc66e2f7b097a111820'
$env:APP_MODE = 'fixture'
uv run --locked uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8000
```

The final command is a **procedure, not a command executed here**. It requires stopping the current port-8000 server first. For a browser check, the existing Vite proxy then forwards `/eda` and `/dataset-overview` to the newly configured backend.

## Minimal next steps and browser-test readiness

1. Locate or obtain the already approved T246 **aggregate only**, through the team's authorized local transfer. Verify its digest independently; do not download, replace, or read raw data to solve a runtime configuration gap.
2. Restart the local backend with both EDA variables set and confirm 200, expected dataset/source identity, and bounded aggregate schema. Keep the current fixture mode if desired.
3. Then perform a real populated `/eda` and `/dataset-overview` browser check. A browser can already render a synthetic contract response via interception, as documented in [final frontend QA](dataset-model-final-qa.md), but that does **not** verify current full-source values. A real populated EDA browser test cannot run against the current 404 backend without supplying the approved summary and restarting with configuration. This changes environment inputs, not backend behavior.

No tests, publisher, source verifier, model training, evaluation, commit, or push were run in this investigation. The only HTTP calls were health, EDA summary, and a rejected EDA query. No protected records were opened.
