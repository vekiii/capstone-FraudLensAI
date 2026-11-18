# Feature 004 US1 RED tasks T005-T007 - 2026-11-18 Europe/Belgrade

**T005/T006/T007 complete as test-authoring/executed RED tasks only. T008-T011
unstarted. No new behavior GREEN/refactor or complete Phase 3 delivery claimed.**

Branch 004-simulation-and-prioritization; baseline HEAD
9ebcea82fc7f2010a7287ea14cded42b99ad74f7; initially clean. AGENTS then next_work
read first. [Exact original request](../../prompts/development/004-simulation-phase-03.md).
Read feature specification/plan/research/data-model/quickstart/contract, existing
models/catalog, fixture and phase2 evidence, actual factory and frontend patterns.
Scoped speckit-implement applied, SPECIFY_FEATURE_DIRECTORY explicitly selected;
prerequisites PASS, checklist16/16 unchanged, extensions.yml absent (no hooks).
Python3.14.3, uv0.10.9, Node24.20.0, npm11.19.0. Existing locks/dependencies used;
no new install, model/provider/network service, agents or browser execution.

## Chosen future boundaries (not implemented)

- `simulation.replay.replay(scenario, score_threshold, budget_minutes_per_window)`
  receives validated label-free Scenario only; future result is strategy records
  in fifo/highest_score/weighted_score_per_minute order, each with windows and
  pending_alert_ids. Importable stub returns an empty list, not valid results;
  no sorting, validation, budget, outcome calculation or replay behavior added.
- Actual FastAPI factory/routes unchanged. Tests use real TestClient requests;
  no test routes or fake HTTP success. Future T009 trusted catalog dependency
  can read `app.state.simulation_catalog`; current factory simply tolerates this
  test-set attribute. Temporary Catalog is actual phase2 implementation. Fault
  tests patch existing Catalog.metadata/resolve to raise private messages; recipe
  creation precedes the resolve patch, preventing invalid test setup.
- `frontend/src/simulation.ts` exports SimulationClient with raw unknown-returning
  listScenarios(options)/compare(recipe,options) and mountSimulation(root,client)
  returning a disposal function. Stub only returns a no-op disposer. No fetch,
  decoder, DOM rendering or main navigation. Future T010 builds this standalone
  view and registers navigation; tests call mount as view entry, not a fake main.
  DOM selectors: select with scenario-ID values; data-simulation-run button;
  data-simulation-results; per-result data-strategy-id, data-reviewed-alerts,
  data-positives-found, data-backlog; readable failures use role=alert. These are
  documented test seams, not a new framework/architecture. Fake client returns
  raw authored public-wire examples; it neither validates nor renders for SUT.

## Coverage and final executed results

| Module | Collected/executed | Passed | Failed | Errors | Exit |
|---|---:|---:|---:|---:|---:|
| test_simulation_replay.py | 9 | 1 | 8 | 0 | 1 |
| test_simulation_api.py | 26 | 1 | 25 | 0 | 1 |
| simulation.test.ts | 8 | 0 | 8 | 0 | 1 |
| Existing simulation contracts + startup | 64 | 64 | 0 | 0 | 0 |
| Existing frontend api.test.ts | 82 | 82 | 0 | 0 | 0 |

**41 intentional failing tests remain**: 33 backend and 8 frontend. Not a full
suite GREEN claim. The two passing new tests retain already-correct horizon-end
validation and original Cases 404/422 behavior; not artificially broken for RED.

T005 traces FR-002-004/006 and SC-001/002: hand-calculated three-alert/A-E examples,
inclusive threshold, 60-digit weight difference beyond float/default Decimal
precision, availability/ID ties, exact window arrival/no early review, exclusive
horizon-end input validation, independent window budget resets, skip oversized,
carry-over that fits a later window, late final-backlog order, used minutes,
ranked/reviewed order and uniqueness. Outcomes never passed to replay. Expected
orders are literals, not calculated using the future algorithm/formula.

T006 traces FR-001/005-009: closed catalog/comparison shapes, sorted temporary
catalog ID/version, actual bundled digest/defaults/canonical recipe threshold,
three strategy order/default counts/ranked/reviewed/pending IDs; per-alert
privacy, Cases before/after equality, 14 strict bad-payload cases plus missing
field/malformed JSON, four unavailable-version cases, sanitized GET/POST service
failures with no partial comparison/private text. Present RED is real HTTP404
because no routes exist, never a mocked HTTP status. Cases preservation checks
precede the intentional final response-status assertion.

T007 traces FR-001/005/008/009: view entry, selection, synthetic/time/score source
and assumptions, catalog defaults first recipe, three ordered result rows and
literal selections/counts, malformed catalog/comparison, catalog and comparison
transport failures with readable safe error/no comparison. Current mount does
not call the catalog or render errors; assertions fail as intended. No skip,
xfail, importorskip, fake rendering, recipe reopen/edit/stale lifecycle work.

## Actual execution history and commands

Sequential T005 -> T006 -> T007. Initial T005 7 failed/1 passed. T006 first had a
decorator SyntaxError; corrected before recording business RED (not RED proof).
T006 then 24 failed/1 passed. T007 8 failed. Added explicit fitting carry-over
and POST service-failure checks, tightened window shape/ranked IDs, formatted new
Python tests and reran affected final modules. Final counts above reflect these
last changes, with no collection/environment errors. No production changes to
make tests GREEN.

[Machine-readable final commands/results/failing test IDs](feature-004-us1-red-results.json)
records every exact argv, exit/count and concrete pytest node ID/Vitest test name.
Working directory D:\AIBootcamp\capstone; UV_CACHE_DIR=.cache/uv. Final raw
logs/JUnit/Vitest JSON under ignored
`.cache/004-us1-d42950aa7a9c42ba9ea20ade027e3992/`.
Each backend module gets unique absolute --basetemp and -o cache_dir paths with
existing parent, plus --junitxml. Final frontend uses --reporter=json and separate
--outputFile. All commands are the requested target modules, no suite exclusions.

`uv run --locked ruff check backend`: PASS/exit0.
`npm.cmd --prefix frontend run typecheck`: PASS/exit0 (extra check confirms TS
test/boundary validity). `git diff --check`: PASS. One existing Starlette/httpx
deprecation warning in API/startup regression. No dependency/lock upgrade.

## Preservation and continuation

Phase2 fixture/models/catalog and fingerprint
`894136f422d013cf0d1d52820acf26e3a3a95076a4b8ab044c4e24faf4105198`
unchanged; no Cases/app/main/schema, frontend main or shared instruction change.
Only T005-T007 test-task markers changed. Full backend/frontend suite, new
behavior GREEN, browser/application demo T011, runtime replay/API/UI, ML/Feature02
adapter/Feature05 work NOT RUN/NOT STARTED, outside explicit scope. Human review
and teammate reproduction pending, no generated approval/signature. No commit,
push, branch switch, pull, merge, reset/stash/clean or deploy.

Next separately authorized implementation: T008 replay, then T009 API and T010
frontend; T011 walkthrough follows actual GREEN, never inferred from RED work.
