# Feature 005 local development and demo quickstart

**Specification-stage document.** Commands under **WORKS TODAY** are existing project checks; no Feature 005 infrastructure or scripts exist yet. Steps marked **PLANNED** are the ordered demonstration procedure and acceptance evidence for [tasks.md](tasks.md), **not executable commands**. Do not install services or run migrations while generating this specification.

## WORKS TODAY: baseline inspection

From the repository root in PowerShell, verify Python 3.14.x, uv, Node 24.x and npm against [pyproject.toml](../../pyproject.toml) and [README.md](../../README.md). Existing locked setup, fixture API and Feature 002 batch commands are in the [root README](../../README.md) and [Feature 002 quickstart](../002-data-and-risk-scoring/quickstart.md). The currently ignored local `.cache/feature-002-env` can run data-free checks; it does not supply the original model/database. For read-only baseline inspection:

```powershell
git branch --show-current
git status --short
Get-Content pyproject.toml
Get-Content MODEL_IMPLEMENTATION_README.md
```

These commands do not prove any streaming component is running. Do not start Feature 002 scoring with substitute data.

## PLANNED: end-to-end local demonstration

| Order | Planned operator action | Required observable result / task gate |
|---|---|---|
| 1 | Confirm team scope decision, reviewed image/dependency versions, Docker Desktop/Compose capacity and ignored local secret files. | T001–T002 complete; no secrets tracked. |
| 2 | Start pinned PostgreSQL, broker, Debezium, MLflow and monitoring Compose services using the future `infra/compose/` files. | Health and versions recorded; T006–T009. No current startup command exists. |
| 3 | Apply versioned PostgreSQL migrations through the future migration entry point. | Immutable transaction/state tables, roles, indexes and checks present; T003–T004. |
| 4 | Produce a small **synthetic** transaction timeline through the future authorized producer. Include two equal-time transfers, different banks, two currencies, duplicate ID, late and invalid examples. | Stable IDs, exact decimal/currency facts and conflicts visible; T005. |
| 5 | Verify Debezium slot/publication and committed-insert envelope, then inspect `fraudlens.live-transactions.v1` by key and offset. | No uncommitted or update/delete event reaches scoring; T008–T010. |
| 6 | Start the future one-worker consumer; verify schema rejection/quarantine, durable buffer, watermark progression and 24-hour warm-up. | Equal-time peers share strict-past features; incomplete coverage stays unscored; T010–T017. |
| 7 | Stage a reviewed compatible model artifact and deployment digest; inspect feature parity before activating live inference. | Existing hash/dependency checks pass; source lineage is distinct from serving identity; T018–T020. If no approved artifact, remain in transport-only mode and do not claim a model result. |
| 8 | Let finalized events score and persist; query predictions/alert decisions with future read-only verification tooling. | Exactly one immutable prediction/decision per transaction/model/policy/generation; T021–T022. |
| 9 | Start existing FastAPI/frontend plus future live mode; open `/api/live/v1/alerts`, then a case detail. | Saved score, explanation, coverage and version identity agree with SQL; T026–T030. |
| 10 | Kill/restart worker and connector at documented crash points, replay a duplicate, then reconcile broker offsets with DB checkpoint. | No duplicate/lost visible assessment; quarantined late event requires a new generation; T023–T025. |
| 11 | Run future dbt/MLflow offline path on separately versioned, restricted synthetic confirmed labels; inspect approval/rollback audit. | No label input to live scoring; candidate cannot activate without reviewed digest; T031–T040. |
| 12 | Inspect metrics/dashboard, run latency/capacity and security checks, then perform end-to-end acceptance. | Actual measured results and limits recorded; T041–T046. |
| 13 | Stop only the Compose services started for this demo; remove generated containers/volumes **only after** preserving required evidence and with an explicit reviewed reset procedure. | No unreviewed data loss; T044. |

Future tasks must add exact, tested PowerShell/Compose/SQL commands here when their corresponding files exist. The final T046 must demonstrate SQL insert → CDC → broker → durable feature state → pinned model prediction → persisted alert → API/dashboard without invoking `pipeline_cli score-run`. An empty alert list is valid only if the chosen test case/policy makes it expected; use a reviewed synthetic policy fixture to exercise visibility without presenting it as model quality.
