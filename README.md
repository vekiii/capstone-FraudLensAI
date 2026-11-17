# FraudLens AI

Final review update (2026-11-17): T066 human contributor review and T067 Converge
execution are complete. Six remaining tasks T095–T100 were appended; T094 stays
open. Quality, live timing and full dataset/model acceptance remain incomplete.
See [actual findings and next steps](evidence/tasks/feature-003-convergence.md).

Current Feature 003 review (2026-11-17): T062–T064 delivered the reviewed read-only
dataset adapter and controlled producer-store compatibility checks. Full IBM/model
integration remains unverified. T061 audit is complete with failed quality;
T066 human reproduction/review and T094 rubric decision remain open, followed by
T067. See the [current reproduction record](evidence/tasks/feature-003-reproduction.md).
Earlier dated results below retain their historical scope.

Coverage/calibration development v4 (2026-11-16, local): **870 backend tests PASS**;
new prompt clarifies transaction IDs and mandatory source disclosures. Judge
calibration3/3, actual development reports2/3 pass, including one recovered request
timeout. Remaining failure: invalid exact assertion followed by repair payload
49,925>48,000 bytes; preserved without rerun. This is not independent release
evaluation. [Actual results and limits](evidence/tasks/feature-003-coverage-v4.md).

Timeout/quota maintenance (2026-11-16, local follow-up): one bounded retry for
request timeout, distinct private credit/quota diagnostics, unchanged public
contracts/limits. **853 backend tests PASS**. New development-v3:3 validated drafts,
raw single-judge semantic pass0/3; a disputed state/disposition interpretation is
retained for review. [Evidence and limits](evidence/tasks/feature-003-timeout-v3.md).

Actual LLM development check (2026-11-16): three new synthetic cases with
gpt-6-luna, **2/3 development passes** under one same-model automated judge; the
remaining case failed during a 30-second request window. All outcomes retained,
17 transports total. This is not an independent release evaluation or a comparable
before/after estimate. See [results and limits](evidence/tasks/feature-003-live-development-v2.md).

Reliability maintenance (2026-11-16): new attempts use prompt v2, actionable safe
repair feedback, a final drafting request and bounded provider cleanup. An opt-in
Serbian script-normalization candidate is available; original evaluation failures
remain unchanged. **814 backend tests PASS**; no new live evaluation. See the
[executable quickstart](specs/003-ai-investigation/quickstart.md) and
[maintenance evidence](evidence/tasks/feature-003-reliability-v2.md).

Feature 003 update (2026-11-15): reviewed-source search, test-provider investigation,
evidence/report browsing, durable recovery and explicit analyst review are
implemented. [Executable quickstart](specs/003-ai-investigation/quickstart.md)
includes safe local configuration, backend/Vite/worker commands and regressions.
Its test-provider mode needs no key and makes no OpenAI calls; optional private
root .env values are overridden by process settings. Never commit credentials.

Phase 8 fixture regression: **776 backend / 186 frontend tests**, Ruff/typecheck/
build PASS; **29 automated browser + 6 process checks** PASS. See
[actual results](evidence/tasks/feature-003-regression.md).
T033 capability and T058 live execution are complete, but retrieval/live quality
and time targets failed. T059-T061 automated primary/secondary judging, aggregation and audit are now
complete under the user-approved post-hoc v2 amendment: 3 judge calls, **0/8**
quality pass. See [actual evaluation](evidence/tasks/feature-003-automated-evaluation.md).
Both planned human scoring roles were replaced; no human validation is claimed. Producer reconciliation
found a changed explanation enum and no reviewed bounded history interface;
actual producer integration remains pending. Phase 8 is a partial delivery, not
full feature acceptance. See [handoff](evidence/tasks/feature-003-phase-08-handoff.md)
and [teammate reproduction steps](evidence/tasks/feature-003-reproduction.md).
Original foundation commands/results below retain their historical scope.

Educational AML prototype. Foundation phases 1-5 are implemented: local synthetic
cases, strict contracts, replaceable scoring and list/detail UI. Phase 6 verifies
coverage and delivery. Foundation peer/human review was subsequently confirmed
by the team; see [foundation review](evidence/tasks/human-review.md). Feature 003
has separate pending evaluation/reproduction gates described above.
T019's final continuation records 16 headless Chrome scenarios plus Enter and
390px viewport checks. This is automated browser evidence, not human review.

## Prerequisites and setup
Use Git, uv, Python 3.14.x, Node 24.x and npm in Windows PowerShell.
Versions checked on 2026-11-12 in phase 6: Python 3.14.3, uv 0.10.9,
Node v24.20.0 and npm 11.19.0. Run commands from the repository root.

For a fresh checkout without dependencies, install the committed locked dependencies.
On the prepared laptop use the existing .venv directly as shown in the feature
quickstart; previous agent-driven installation attempts coincided with crashes.
```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
uv sync --locked --group dev
npm.cmd --prefix frontend ci
```
The workspace-local uv cache avoids machine-cache access restrictions. npm.cmd
avoids npm.ps1 execution-policy restrictions without changing system policy.
Initial dependency installation needs network access. Runtime startup and health
need no provider key, model, RAG corpus, dataset or external AI service.
No .env file or fixture data file is needed for health.

Lockfile creation was performed during initial setup with `uv lock` and
`npm.cmd --prefix frontend install`; those resolve dependencies and generate
uv.lock / frontend/package-lock.json. Do not repeat them for routine installs or
hand-edit lockfile hashes. Use locked installs above; intentional dependency
changes require review and genuine lockfile regeneration.

## Run in two terminals
In terminal 1, from repository root:
```powershell
uv run --locked uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8000
```
In terminal 2, from repository root:
```powershell
npm.cmd --prefix frontend run dev -- --host 127.0.0.1 --port 5173 --strictPort
```
Open http://127.0.0.1:5173 for the synthetic case inspection UI. Vite forwards relative
/api requests to http://127.0.0.1:8000. Both services bind to loopback only;
this is a local demo, with no production multi-user security or ML-ready claim.
Stop your own foreground servers with Ctrl+C.

In another PowerShell terminal check health directly and through the proxy:
```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/health'
Invoke-RestMethod -Uri 'http://127.0.0.1:5173/api/health'
```
Both must return HTTP 200 JSON `{"status":"ok","mode":"fixture"}`.
The case API is available directly and through the same proxy:
```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/cases'
Invoke-RestMethod -Uri 'http://127.0.0.1:5173/api/cases/CASE-001'
```
Unknown CASE-999 returns 404; malformed CASE-1 returns 422. Errors use the closed
`{"error":{"code":"...","message":"..."}}` envelope. See T016 evidence for actual bodies.
APP_MODE defaults to fixture and is the only supported value. If APP_MODE is set
otherwise, startup fails validation; remove it or explicitly set it to fixture.
Settings resolve data/fixtures/cases.json relative to the repository, but startup
and health do not open it. T014's three synthetic cases are stored there without scores.

## Checks and build
```powershell
uv run --locked pytest backend/tests/integration/test_startup.py
uv run --locked pytest backend/tests
uv run --locked ruff check backend
npm.cmd --prefix frontend run test -- --run
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend run build
git diff --check
```
All 310 backend tests pass (phase 6, 2026-11-12), including the unchanged 49 T012 API/scorer tests and
8 additional framework/logging checks (rerun successfully in T019).
The frontend has 151 passing tests, including all 82 original API and 19 DOM tests.
T019 typecheck/build/Ruff pass. See T012–T019 evidence for actual results and limits.
Build output frontend/dist/ is local and ignored; it is not a deployment.

The [fixture scoring rule](docs/decisions/fixture-scoring.md) rotates illustrative
constants by transaction ID and copies transaction time into scored_at. Results
are explicitly synthetic, without ML inference, calibrated probabilities or labels.

The [target quickstart](specs/001-project-foundation/quickstart.md) also describes
three-case navigation and failure-state checks. T019's real-server/browser
verification includes live HTTP and completed headless Chrome automation. See the
final T019 continuation for fault injection and limits. Phase 6 did not rerun the
browser verifier because production code is unchanged. Human review stays pending.

## Evidence and next work
See [T019 integrated verification and limits](evidence/tasks/T019.md),
[T018 UI/DOM verification](evidence/tasks/T018.md),
[T017 frontend API/validation](evidence/tasks/T017.md),
[T016 API/error verification](evidence/tasks/T016.md),
[T015 scorer/validation](evidence/tasks/T015.md),
[T014 fixtures/validation](evidence/tasks/T014.md),
[T012 backend RED](evidence/tasks/T012.md), [T013 frontend RED](evidence/tasks/T013.md),
[phase 3 handoff](evidence/tasks/phase-03-handoff.md),
[startup RED/GREEN](evidence/tasks/T008.md), [setup/smoke](evidence/tasks/T011.md)
and [next_work.md](next_work.md). Human review and independent second-member
reproduction remain pending (SC-001). Local fixture checks are not ML evaluation.

## Windows pytest temporary-directory access
If pytest reports WinError 5 during tmp_path setup or cannot write .pytest_cache,
use a fresh workspace-local temp/cache for that run (all tests still run):
```powershell
$runId = [guid]::NewGuid().ToString('N')
$pytestTemp = Join-Path $PWD ".cache/peer-pytest-$runId"
$pytestCache = Join-Path $PWD ".cache/peer-pytest-cache-$runId"
uv run --locked pytest backend/tests --basetemp "$pytestTemp" -o "cache_dir=$pytestCache"
```
Use new paths: pytest manages/removes its basetemp contents. Do not change system
permissions or remove other users' temp directories. Record the actual rerun result.

## Acceptance update - 2026-11-12
Earlier pending acceptance statements above are superseded by the team's reported
joint setup verification and code/contracts/evidence review. T025/SC-001 and T028
are complete; see evidence/tasks/peer-reproduction.md and human-review.md from the
repository root. No additional automated/browser executions claimed by this update.
