# EDA real-data final verification — BLOCKED

**Date:** 2026-11-23
**Scope:** Locate the approved T246 aggregate, verify it, and only then configure the existing backend and inspect `/eda` and `/dataset-overview` with the real response. The Phase 1 artifact gate did not pass. Phases 2 and 3 were not attempted.

## Artifact provenance and availability

The authoritative aggregate is the Git-ignored `t246-hi-small-eda-summary-v1.json` published from the verified T210 snapshot. [T246 execution evidence](tasks/T246-full-source-eda-2026-11-21.md) records **17,279 bytes** and independent SHA-256 **`b8900338ca375b2d632b260a794634fb19408012a1c14fc66e2f7b097a111820`**. The same digest is pinned in the [EDA API contract](../specs/002-data-and-risk-scoring/contracts/api.md). T246 records a successful 200 response in fixture mode when that exact file and digest were supplied. [T247](tasks/T247.md) records a historical real Safari check. Those are prior observations in another checkout, not a current artifact or current browser result.

**Current artifact:** unavailable. The exact filename is absent at the documented ignored output path under `data/processed/`, at the checked local Downloads and Documents filename locations, and from a recursive exact-filename search of the project `data/processed/` and its `sita-capstone` parent folder. The historical T246 server path is on a different Mac checkout and is not an accessible Windows artifact location here. [The local integration record](tasks/capstone-mvp-integration.md) also notes the aggregate was absent from its integration checkout. No approved alternate artifact location was found in the reviewed T210/T246/T247/T249 evidence or contract.

| Gate | Expected | Observed | Status |
|---|---|---|---|
| Authoritative digest | `b8900338ca375b2d632b260a794634fb19408012a1c14fc66e2f7b097a111820` | Present in T246 evidence and API contract | **PASS** |
| Approved aggregate bytes | Exact T246 file, 17,279 bytes | No file at checked approved local/documented locations | **BLOCKED** |
| Independent current SHA-256 | Match authoritative digest | Cannot hash absent file | **NOT RUN** |
| Existing loader schema/source check | Strict `EdaSummary`, approved source SHA `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040` | Cannot call [EdaService](../backend/src/fraudlens/eda/service.py) with absent artifact | **NOT RUN** |
| Current backend | 200 populated summary | Health 200; EDA 404 | **BLOCKED** |

The T210 raw CSV and snapshot files are present according to [readiness investigation](eda-backend-readiness.md), but they are **not** the approved T246 aggregate and cannot be substituted for it. No raw rows, labels, or model partitions were opened. No archive was extracted or scanned for a replacement.

## Configuration and real-data QA disposition

The established [local startup procedure](../README.md) runs Uvicorn from the repository root and Vite on port 5173. [Settings](../backend/src/fraudlens/settings.py) support `EDA_SUMMARY_PATH` and `EDA_SUMMARY_SHA256` in fixture mode; [the route](../backend/src/fraudlens/main.py) returns `dataset_unavailable` when the loader cannot obtain a trusted summary. Configuration would require setting those two variables to the independently verified approved aggregate and its digest in the backend process's startup environment, then restarting the local backend. **No backend was restarted, and no configuration was changed**, because the artifact gate failed.

No real-data Playwright session or screenshot was produced. The five requested viewports (320, 375, 768, 1024, 1440 px), route equivalence, real values, UTC coverage, categories/currencies, tables, denominators, overflow, SHA readability, and absence of row/label exposure remain **NOT VERIFIED against the current backend**. [Earlier final QA](dataset-model-final-qa.md) used an intercepted synthetic contract response and does not satisfy this task's real-data requirement.

## Commands executed and results

- Exact-path `Test-Path -LiteralPath ... -PathType Leaf` for the documented processed output and local Downloads/Documents filenames: **false** for each.
- `Get-ChildItem -LiteralPath data/processed -Filter t246-hi-small-eda-summary-v1.json -Recurse -File` and an exact-filename recursive search of the `sita-capstone` parent: **no result**.
- `curl.exe` to the current local backend: `/api/health` **200**, `/api/eda/summary` **404**.
- Read `AGENTS.md`, `next_work.md`, the constitution, [readiness report](eda-backend-readiness.md), T210/T246/T247 evidence, contract, settings/service, and [frontend QA](dataset-model-final-qa.md). No test suite or build was run because no code was changed and the artifact gate stopped the workflow.

## Required authorized action

Provide or locate the **already approved T246 aggregate bytes** from the documented source holder through an authorized transfer to an ignored local path. Then independently compare SHA-256 to the recorded digest and use the existing strict loader to verify schema/source identity. Only after those checks pass may the backend be restarted with the two EDA variables and the real browser QA run. If the approved artifact cannot be obtained, this task remains blocked; any new full-source publication requires a separate decision and is outside this task.

**Final disposition: BLOCKED.** No dataset regeneration, backend/API/model/frontend change, network interception, commit, or push was performed. The pre-existing unrelated untracked files were left untouched.
