# Isolated boosted UTC daily-cap publication — 2026-11-16

## Authorization and frozen inputs

The user directed implementation of the proposed policy for a **new isolated
run**, while keeping `run_boosted_full_20261114_v3` (166 threshold alerts)
as an immutable reference and shared activation as a later team decision.
Before implementation, `git fetch origin` exited 0 and local/remote
`model-implementations` both resolved to
`d9bd8a2e3629a2d3939fc5507583f310428c53ac`; all previous uncommitted
code/evidence and team commits were preserved. Read current `AGENTS.md`,
`next_work.md`, quickstart, proposal, T065–T067 evidence and contracts.

The pinned source v3 store SHA-256 is
`732eefa75ad46c80404c34301ae6d72be87d4eb61f0d618457f7c760224dce06`,
boosted manifest
`013c7ebe5ab5a5270a7b66af200060d3499c31eb2598c06a038ca887fd9320a6`,
protocol `01fff67d44895b5a1aa6de6dfbb6c6c107f01c041ba7c972bf42210e2b316068`.
The source has `completed|3963424|3963424|166`. The full development-only
selection digest was already fixed as
`9ad3106f5fbce59b43af1ff0b06db7dc06b4b9cbb66959628699323dc741b466`.
No previously unseen compatible 24-hour source was found in `data/raw/`,
`data/processed/` or `evals/results/`: only the original IBM v8 CSV and
derived stores are present. No new labels were read.

## Contract and implementation

The user-authorized isolated policy is `boosted_utc_daily_top20_v1`. From
scores at or above frozen threshold `0.9936687168275105`, group by the UTC
date of the approved synthetic time coordinate, sort score descending then
stable transaction ID ascending, and publish at most 20 per day. The new
derived run keeps **all** saved assessments, scores and explanation values;
only the run ID and final alert flags change. Its immutable `run_policies`
record includes source run ID, exact source-store SHA-256, selection digest,
threshold-eligible count and capacity-excluded count. The source run remains
untouched. `RunStore.complete` checks final row and alert counts, and the
API list/detail query the same `alert=1` set. Legacy v2 list responses remain
unchanged; policy runs add optional policy and eligible/excluded counts, with
frontend parsing and display. A completed policy row is immutable.

The exact CLI command and new store/run ID are in the [quickstart](../../specs/002-data-and-risk-scoring/quickstart.md#isolated-daily-top-20-publication-from-verified-scores).
The process is one worker and reads the source run store in read-only mode.
The original v3 is retained for 166-alert reference comparison.

## RED/GREEN and regression

`PYTHONPATH=backend/src .venv/bin/python -m pytest backend/tests/integration/test_daily_cap_publication.py -q --tb=short`
first exited 1 with two intended `ModuleNotFoundError` failures for the
missing publication module. After implementing the derived-run path, the
targeted integration suite exited 0 with two passes: 22 candidates on one
day reduce to 20 with stable score/ID tie handling; another day has exactly
20; later days have below-threshold/no-alert rows; API count/list/detail and
404 for excluded cases agree; wrong manifest/hash fail before target creation.
The earlier pure selection suite covers exact UTC midnight and non-UTC times.

Full backend `PYTHONPATH=backend/src .venv/bin/python -m pytest backend/tests -q`
exited 0 with **744 passed, two existing dependency/host warnings** after a
contract parity correction. An earlier broad run exited 1 with **1 failure,
743 passes** because new optional Pydantic fields serialized as null in a
legacy v2 list. The `CaseListV2` serializer now omits fields not set, preserving
the exact old shape; targeted schema/model and publication tests then passed
14/14. Frontend `npm --prefix frontend test -- --run` exited 0 with **170
passed**. `npm --prefix frontend run build` (including typecheck) exited 0;
Ruff passed. Final diff checks and actual full-run/API/UI results are recorded
in the completion addendum below.

## Completion addendum: actual derived run and application

The exact `derive-daily-cap-run` command linked above exited **0** and returned
`status=completed`, `scored_count=3963424`, `threshold_eligible_count=166`,
`capacity_excluded_count=7`, `total_alerts=159`, source v3 store SHA-256
`732eefa75ad46c80404c34301ae6d72be87d4eb61f0d618457f7c760224dce06`
and selection SHA-256
`9ad3106f5fbce59b43af1ff0b06db7dc06b4b9cbb66959628699323dc741b466`.
The one-worker process created its target at 21:28:06 CET and last modified it
at 21:44:31 CET, approximately **16 minutes 25 seconds** of file activity;
the actual CLI exit was 0. While quiet, PID 26529 remained `Rs`, accrued CPU
time and grew the target store; it was not restarted. The source v3 was never
written. The completed, subsequently isolated-activated target is
`evals/results/boosted-daily20-20261116-v1.sqlite`, SHA-256
`5b7f834c877cc71aa3dbe90174b5bcd2bf7556dc4dc5a42bd48e7c9150973a70`.

Read-only SQLite returned `completed|3963424|3963424|159`; an independent
`COUNT(*)/SUM(alert)` over `scored_assessments` returned `3963424/159`.
`run_policies` returned the declared policy ID, v3 run ID/store hash, selection
digest and `166/7`. `PRAGMA quick_check` returned `ok`. The new store contains
the partial `alert_listing` index and all three policy immutability triggers,
including the regular writable-open insert trigger. `activate-run` exited 0
with `status=active` **only in this target store**; read-only `active_run`
points to the new run. Shared activation was not touched.

Final alert counts by UTC date are: Sep 1 **0 warm-up**, Sep 2 **20**,
Sep 3 **11**, Sep 4 **9**, Sep 5 **13**, Sep 6 **18**, Sep 7 **18**,
Sep 8 **16**, Sep 9 **20**, Sep 10 **14**, Sep 11 **2**, Sep 12 **5**,
Sep 13 **3**, Sep 14 **0**, Sep 15 **3**, Sep 16 **4**, Sep 17 **3**,
Sep 18 **0 partial source edge**. These sum to **159**. The only changes from
v3 are Sep 2 **24→20** (four excluded) and Sep 9 **23→20** (three excluded).
There is no unexpected deviation from the predeclared read-only diagnostic.
Sep 1 and Sep 18 are not used as complete-capacity evidence; Sep 14 is a full
UTC day with zero alerts.

The actual isolated API `GET /api/cases` returned HTTP 200, 159 total, 100
displayed, `truncated=true`, policy ID and `166/7`. All **100** listed case
details returned HTTP 200 with the same snapshot ID and list score; each
matched the corresponding v3 saved score and complete explanation exactly,
and full-precision base + displayed contributions + remainder reconstructed
its score within `1e-8`. All seven excluded threshold candidates returned
HTTP 404 as case details. A real local Vite/FastAPI browser pass showed
`Ukupno upozorenja: 159; prikazano: 100` and `iznad praga: 166; izostavljeno: 7`.
Opening `C111ebf9aa63b53588db7f7207375d88c` displayed run
`run_boosted_daily20_20261116_v1`, scorer
`model-history-v1-boosted-candidate`, score `0.9968118733390847`, method
`boosted_sequential_probability`, base `0.008635663555714459`, remainder
`0.018812791098467885` and the saved three feature contributions. API and
browser startup commands are in the quickstart; both servers were stopped
after verification.

Final regression after the last code/test change: backend
`PYTHONPATH=backend/src .venv/bin/python -m pytest backend/tests -q` exited 0
with **744 passed, two existing host/dependency warnings** in 54.67 s;
frontend `npm --prefix frontend test -- --run` exited 0 with **170 passed**.
`npm --prefix frontend run build` (including `tsc --noEmit`) exited 0;
`.venv/bin/ruff check backend/src backend/tests evidence/tasks/feature-002-build-private-handoff.py evidence/tasks/feature-002-daily-capacity-check.py`
exited 0; `git diff --check` exited 0. The original v3 remains the
166-alert reference; no new model fitting or full prediction pass occurred.
The private package's copied handoff instructions were synchronized after
these findings. Its 15 listed payload hashes were rechecked with zero
mismatches; final `evals/results/team-handoff-20261116/MANIFEST.json`
SHA-256 is `21ec67d094488c691715c9764dd3be554b43eddbd679e5fe37031c24a0fdf65d`.

## Open review gates

This local technical implementation does not close T065 teammate review,
T066 independent reproduction, T067 team code/contract/evidence review or
independent usefulness. The fresh unseen 24-hour criterion remains at least
five hits among at most 20 alerts under a policy and period frozen before
label access. The team must separately decide whether and when to activate
the policy run in the shared store.
