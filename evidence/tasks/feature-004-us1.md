# Feature 004 US1 RED tasks T005-T007 - 2026-11-18 Europe/Belgrade

**Update: T008-T011 implemented and verified later on 2026-11-18. All prior
intentional RED tests now GREEN; see execution closure at the end. Original
RED observations below remain historical, not current product state.**

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

## T008-T011 implementation and actual GREEN closure - 2026-11-18

Authorization: [received follow-up](../../prompts/development/004-simulation-us1-green.md).
Initial branch 004-simulation-and-prioritization, HEAD
c53a164b20dcaaf413bab93ad3dd01acad0c4673, initially clean. AGENTS then next_work
read first; scoped speckit-implement applies T008-T011 only. Explicit feature
selection/prerequisites PASS; checklist16/16 unchanged, extensions.yml absent.

T008: pure label-free engine uses Fraction for scores/weights/minutes and actual
UTC instants for availability/ID tie-break. Each strategy owns independent
reviewed set/budget per window, scans past oversized work and admits late
arrivals to final backlog. Inputs are validated without mutation. No private
outcome access/import. Actual targeted GREEN: **9 PASS**, exit0.

T009: closed strict recipe/catalog/comparison models and read-only APIRouter,
minimal factory registration. Request type/version errors422, unavailable
scenario/hash/strategy409, sanitized service failures500 with no partial output.
Recipe threshold echoed canonically; catalog metadata unchanged. Outcome access
occurs only after ALL three strategies select; counts distinguish threshold/
backlog misses, unknown coverage, empty zero counts and wholly unlabeled null.
No per-alert labels, Cases/scorer mutation, database or Feature02 access.
Actual targeted GREEN: **26 PASS**, exit0.

T010: raw unknown-client responses decoded through closed objects/nested field
validation, strict decimal/UTC/identity/integer/assumption/strategy/count checks;
plain text DOM rendering, source/score/assumptions and ordered results table.
Real relative GET/POST client has a5-second abort timeout; initial controls use
catalog defaults. No budget/threshold editing or recipe download/reopen added.
Mount disposal/abort and generation guards avoid publishing after navigation.
Default app entry remains Cases; navigation switches/disposes either view.
Minimal table/mobile overflow styles; no framework/dependency/config changes.
UTC comparison uses six-digit string keys, receipt threshold equality uses text
normalization instead of floating-point rounding. Actual **8 simulation tests
PASS**; full frontend **159 PASS**, typecheck/build PASS, all exit0.

T011: [actual automated browser verifier](feature-004-us1-browser.mjs) runs normal
uvicorn and Vite quickstart entry points on loopback, then real Chrome157.0.8103.79
with isolated ignored profile. No response injection or fake client. Two real
direct/proxy default comparisons verified exact recipe/scenario digest and all
hand-counted values. Browser normal navigation shows A / B / C,E and found0/1/1,
threshold misses1/1/1, backlog misses2/1/1, negatives1/0/1, backlog3/3/2.
Cases default/list/detail/back and404/422 remained correct after navigation.
No uncaught browser exceptions. **7 grouped checks PASS**, final observed browser
comparison66ms (one smoke observation, not a performance benchmark). Results:
[browser result](feature-004-us1-browser-results.json). All owned hidden processes
stopped; ports8000/5173/9228 free before/after; no personal Chrome profile changed.
Browser required approved sandbox process escalation. This is automated evidence,
not human clicking, peer reproduction or product acceptance review.

### Commands and final regression

From D:\AIBootcamp\capstone, existing Python3.14.3/uv0.10.9/Node24.20.0/npm11.19.0:

```powershell
$env:SPECIFY_FEATURE_DIRECTORY='specs/004-simulation-and-prioritization'
$env:UV_CACHE_DIR=Join-Path $PWD '.cache/uv'
$t=Join-Path $PWD ('.cache/004-us1-verified-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $t | Out-Null
uv run --locked pytest backend/tests --basetemp "$t/tmp" -o "cache_dir=$t/cache" -q --tb=short
uv run --locked ruff check backend
npm.cmd --prefix frontend run test -- --run
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend run build
node evidence/tasks/feature-004-us1-browser.mjs
git diff --check
```

Full backend **401 passed in4.16s**, exit0, one existing Starlette/httpx warning.
Full frontend **159 tests /6 files PASS**, exit0; typecheck and build exit0.
Ruff PASS after local import/format/lambda-to-def cleanup; diff PASS. Existing RED
tests/assertions unchanged, no skips/xfails or requirements weakened. Minimal
stubs replaced with behavior; no additional artificial RED required. Initial
large frontend patch was rejected before mutation due to duplicate target edit;
corrected single-file update, then all checks passed. No behavioral failure was
masked or claimed as successful execution.

No residual intentional RED. Bundled facts/outcomes/hash and trusted catalog
unchanged, source privacy boundary preserved. No lockfile/dependency/shared
instruction or Cases contract/fixture/scorer changes; only minimal app/navigation
composition. No providers/datasets/ML/Feature02/Feature05, Git publication or
subagents. Human review/reproduction still pending. T008-T011 may be checked for
this bundled US1 delivery; T012+ remain unstarted. Next separately scoped work:
Phase4 T012-T014 (capacity/threshold controls and stale-result extensions).
