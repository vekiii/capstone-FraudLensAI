# T045–T051 analyst review — 2026-11-15

Scope: Feature 003 Phase 6 only, branch `feature03`, baseline/current HEAD
`fcdf528`. Initial worktree was clean. Root AGENTS.md and current next_work were
read before implementation, followed by constitution/product context, selected
tasks/spec/plan, data model, review schemas/API contracts and relevant recovery,
state, UI and provider-gate evidence. Existing Phase 5 implementation was checked;
no prior work was discarded. No dependencies, lockfiles, producer/ML contracts,
corpus source/review records or shared instructions changed.

Original request: [saved prompt](../../prompts/development/003-investigation-phase-06.md).
T045–T050 complete. T051 automated technical exercise passed, but its actual human
identity/date/confirmation requirement is **pending**, so T051 remains unchecked.
T033 remains unchecked after the earlier HTTP 400/capability failure. No T033
invocation, OpenAI access, actual .env read, Phase 7 work, commit or push here.

## Implemented behavior

An explicit review records a server-configured local actor, trimmed nonempty
1–2000-character rationale, exact saved report digest, disposition and UTC time.
Ready drafts allow escalate/close/request_more_information. Needs-information
requires its saved limitations draft and allows only request_more_information,
including amendments. Active, failed and cancelled attempts reject report review.
Generated report text, tools, schema validation and GET never authorize decisions.

POST `/api/investigation/attempts/{id}/reviews` requires UUID Idempotency-Key,
decimal If-Match, JSON and existing same-origin/Host guards. The closed request
cannot choose actor, context, provider or permissions. Stale attempt revision,
report digest or superseded review returns 409 revision_conflict. Missing
amendment note or prohibited disposition is 409 invalid_transition. Invalid text,
forged actor/unknown fields/headers return 422 invalid_request with safe messages.
Body bound is 64 KiB, enough for both legal 2000-character escaped Unicode fields.

Review row, audit event, state/revision and original public response are committed
in one short SQLite transaction. An injected failure saving the response rolls
back all four. Concurrent distinct keys have one winner; same keys replay one
accepted result. Changed target/revision/body using that key conflicts. Replay
returns the originally accepted response even after later amendments.

Corrections require the current review ID and nonempty separate correction note.
They append a linked immutable review and increment attempt revision; no prior
review is replaced. Original report/evidence rows and report-validation events
stay immutable. The public semantic_review flag is derived from separate review
events, without mutating the original report. It is not an evaluation rubric
score or a signature. Current review + supersedes ID are public; complete review
and audit history remain in the local SQLite archive, without a new history API.

The UI shows original claims/citations beside the saved decision and correction.
No decision is preselected/submitted. Amendment requires note and rationale.
Text is rendered literally. A transport failure restores normalized input and
keeps its action key; a revision conflict disables submission until explicit
refresh. Generation/context/attempt checks discard obsolete replies. Historical
report views remain read-only. Review never refreshes the source or calls a
provider; reviewed attempts cannot be retried/cancelled by existing state rules.

## Executed RED → GREEN → REFACTOR

1. Initial missing review import was an exploratory setup failure, **not RED**.
   After adding the importable boundary stub, **17 review tests failed** at its
   NotImplementedError and **9 API tests failed** on absent review route (404).
2. Implemented transaction primitive, dedicated review service, public projection
   and route: **26 passed**. First GREEN attempt exposed an incorrectly placed
   request-bound edit (NameError on create); corrected before the passing run.
3. First UI run hit Vite's literal file URL rewriting, **not RED**. Dynamic fixture
   locator fixed: **6 intended failures** on absent form/client. Implementation
   made **6 pass**. Existing test clients gained the required review method.
4. Refactored unit setup to a self-contained fixture after standalone execution
   revealed an import dependency on the integration test directory. Standalone
   review module **20 passed** after adding rollback/no-draft/immutability checks.
   An interim Ruff fixture-alias warning was fixed; no ignored lint rules added.
5. Unicode boundary: **1 API RED** (valid escaped body returned 422) and **1 UI
   RED** (native UTF-16 maxlength admitted too few Unicode characters). Body bound
   and native field capacity corrected; explicit 2000-code-point validation
   remains. Final suites include those passing boundary cases.
6. Shared guarded HTTP helper renamed mutation_action for retry/cancel/review.
   No schema version/migration or dependencies added. Existing store assertion
   now checks the named analyst_review audit event rather than an anonymous one.

Final regression commands/results are recorded in the final verification section.
No tests were skipped/xfail'ed to pass. The focused Unicode `-k`/`-t` RED commands
deselected unrelated cases; the complete final suites run every test.

## T051 actual API, proxy, CLI and two Chrome sessions

[Runner](feature-003-review-browser.mjs),
[isolated runtime](feature-003-review-runtime.py),
[actual results and audit IDs](feature-003-review-browser-results.json).
Chrome **157.0.8103.52**, two distinct incognito browser contexts and independent
page clients. The real FastAPI process, Vite proxy and `cli.main worker --once`
were used, with authored fixture/test-provider output. Eight observations PASS:

1. Empty selection/whitespace rationale rejected without review; actual API
   rejected forged actor (422) and wrong report (409).
2. Browser opened exact run-bound saved citation text.
3. Both sessions loaded one ready draft. First saved close (201); second's stale
   escalate returned 409 revision_conflict, with no silent refresh/overwrite.
4. Second session explicitly refreshed and saved linked escalation correction.
   HTML-like note remained literal. First request replay returned its original
   201 response after amendment; the current amended state remained unchanged.
5. Separate initial escalate and request_more_information were saved, completing
   all three initial disposition paths and their API reopen checks.
6. Authored needs-information draft allowed only request_more_information in UI;
   direct close/escalate and later close amendment returned 409.
7. Reopen/SQLite audit found **5 immutable review events**, **4 unchanged drafts**,
   five accepted review keys, original evidence/report binding and stable budgets.
8. Zero uncaught exceptions in either session. Owned-process cleanup and ports
   8000/5173/9228 checked free.

All stored decisions use **AUTOMATED TEST OPERATOR (not human approval)**.
The JSON explicitly stores human identity/date as null, status PENDING. Dates on
automated review events are actual execution timestamps, not human review dates.

Failed runs are not counted as success. Sandbox Chrome failed before UI checks
with GPU Access denied; [initial failure](feature-003-review-browser-sandbox-failure.json)
also reported a temporarily occupied cleanup port. Escalated targeted inspection
then found no remaining test listeners/processes. Cleanup now waits for owned
process ports. First escalated browser run found a harness error: worker CLI
returns a summary, not full RunView. Harness corrected to GET the saved run;
the subsequent eight-observation run passed. Chrome execution required sandbox
escalation; no approval review rejection occurred.

## Reproduction and final verification

From repository root, existing locked environment, no installation:

```powershell
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
node evidence/tasks/feature-003-review-browser.mjs
.venv/Scripts/python.exe -m pytest backend/tests --basetemp .cache/p6-final2-tmp -o cache_dir=.cache/p6-final2-cache -q --tb=short
.venv/Scripts/python.exe -m ruff check backend
npm.cmd --prefix frontend test -- --run
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend run build
git diff --check
```

Python **3.14.7**, Node **24.20.0**, npm **11.19.0**. Harness forces source fixture,
provider test, demo actor and absent ENV_FILE before configuration loading;
removes provider key/model variables. Default pytest autouse isolation also
replaces ENV_FILE. Generated stores/profiles are isolated under ignored `.cache`.
No actual model, token usage, pricing, billing or report-quality claim is made.

Final results: backend **683 passed**, 44.10 s; frontend **179 passed**, 9 files.
Ruff (backend and new Python harness), TypeScript typecheck, Vite build, browser
harness syntax and `git diff --check` PASS. Backend count includes 20 new review
unit tests and 10 new review API tests; frontend includes 7 new review tests.
Existing store audit test was updated without weakening rollback assertions.
The final browser rerun after the Unicode fix uses the same eight observations;
its latest concrete IDs/timestamps are in the linked results JSON.

## Required actual human confirmation — OPEN

- [ ] A real analyst inspects fixture citations, gaps and original draft; records
  their chosen identity, actual review date and explicit decision/rationale.
- [ ] That person verifies a linked correction and the two-session stale conflict,
  then explicitly confirms or rejects the behavior. Record actual findings and
  bound attempt/report/review IDs here; do not substitute automated test events.
- [ ] Human code/contracts/evidence review and independent teammate reproduction
  remain unclaimed. These checks are not actual-provider held-out evaluation.

Stop at T051. The next concrete action is the actual human confirmation above.
No Phase 7/evaluation-pack work is authorized by this handoff.
