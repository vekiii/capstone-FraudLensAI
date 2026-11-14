# Phase 4 offline fixture journey, 2026-11-15 Europe/Belgrade

Branch feature03, baseline fece114. Scope T031-T038 except live T033.
[Original request](../../prompts/development/003-investigation-phase-04-resume.md).
T023-T030 code already existed; stale handoff/task markers reconciled against code,
tests, previous evidence and retained pytest failure caches. No dependency install.

## Real local journey (T038)

Command: `node evidence/tasks/feature-003-fixture-journey.mjs --reviewed`.
Chrome required process escalation as the sandbox previously blocked its GPU
subprocesses. Browser sandbox stays enabled. Fresh isolated .cache store/profile,
six unchanged human-reviewed corpus texts, no keys/models/evaluation references,
explicit test provider. Default local archive and source/review hashes untouched.

[Machine-readable results](feature-003-fixture-journey-results.json): **9 checks
PASS**, Chrome 157.0.8103.52. Separate real FastAPI/Vite/CLI processes, not TestClient
or mocked browser responses. Opening the report panel does not enqueue; explicit
start returns 202/created with zero provider calls. An explicit worker --once makes
four authored provider requests and executes get_case_facts, get_account_history,
search_procedures; all three completed, actual evidence saved. Ready report has
schema/reference validation passed and semantic review pending. Exact cited text,
source URI/jurisdiction and fixture numbers are inspected through browser/API.
Reload reads the same report without further dispatch. Invalid citation uses one
repair then fails output_invalid with report=null. Separate no-match scenario
produces a needs_information report. Original three-case browsing and API/proxy
404/422 pass with feature disabled and missing corpus/key/model. No uncaught browser
exceptions. Owned processes stopped; ports 8000/5173/9228 free afterward.

Initial browser checks exposed a real proxy integration defect: the string Vite
proxy configuration rewrites Host (installed Vite code confirms changeOrigin=true),
so browser Origin and backend Host disagreed and POST correctly returned 403.
Changed proxy to explicit target/changeOrigin=false, preserving same-origin guards.
The next run passed seven workflow checks but failed in the harness's reload race:
it saw the previous DOM before navigation finished. Awaiting Page.loadEventFired
fixed the harness; final complete run PASS. This was not a product-crash claim.

## Regression and limits

Final backend command: `.venv/Scripts/python.exe -m pytest backend/tests --basetemp
<unique-existing-cache-parent>/tmp -o cache_dir=<same-parent>/cache -q --tb=short`.
**629 PASS**, no expected future REDs left in this phase. `.venv/Scripts/ruff.exe
check backend`: PASS. `npm.cmd --prefix frontend test -- --run`: **166 PASS**;
typecheck/build PASS. Initial frontend regression 165 PASS/1 FAIL exposed the new
panel's automatic request in old browsing; report panel now opens explicitly via
Prikaži AI istragu. Assertions were preserved. Focused UI RED/GREEN and API evidence
are in [UI](feature-003-ui.md) and [API](feature-003-api.md).

Runtime Python 3.14.7, OpenAI 3.51.0, httpx2/httpcore2 2.16.0, Node 24.20.0,
npm 11.19.0. SDK was installed manually by the user before this work. No uv sync/add,
pip install, key read, live provider call or model/ML execution in this session.
No claim of LLM quality, current dataset integration, human report approval or
second-person reproduction. T033 pending; no Phase 5-8 implementation, commit/push.
