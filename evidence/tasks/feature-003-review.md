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

## Required actual human confirmation — recorded 2026-11-15

- [x] A real analyst inspects fixture citations, gaps and original draft; records
  their chosen identity, actual review date and explicit decision/rationale.
- [x] That person verifies a linked correction and the two-session stale conflict,
  then explicitly confirms or rejects the behavior. Record actual findings and
  bound attempt/report/review IDs here; do not substitute automated test events.
- [ ] Human code/contracts/evidence review and independent teammate reproduction
  remain unclaimed. These checks are not actual-provider held-out evaluation.

The first two items are supported by Vedran's actual observations and linked
records below, not the earlier automated operator. The third independent review/
reproduction item remains unclaimed. Historical stopping instructions are
superseded by the latest T051 correction/closure section below.

## Actual human observations — Vedran, 2026-11-15

This section supersedes the earlier claim that no human observations exist.
Vedran supplied ten annotated observations and a screenshot during the manual
T051 exercise. These are his real UI observations, not automated-operator events,
independent report-quality evaluation, code-review approval or blanket acceptance.

- Exact simulated Missingness passage opened with version, jurisdiction, corpus
  and provenance. Fact evidence preserves 1250.00 EUR; unavailable history remains
  explicitly unavailable. Test-provider/source/score limitations remain visible.
- No selected disposition: browser reports `Please select an item in the list.`
  Empty rationale: `Please fill out this field.` These are observed browser
  validation results, not a new direct API-negative test.
- Human actor Vedran saved close with rationale `Radi probe`, then reopened the
  saved result. Later saved escalation correction and request_more_information.
- Two-session exercise displayed both stale_snapshot and revision_conflict;
  user explicitly refreshed and saved a linked correction.
- Needs-information offers only request_more_information, including correction;
  Vedran explicitly confirmed both restrictions.
- Screenshot shows awkward label/textarea wrapping. This is a presentation
  observation, not evidence of lost input or a newly implemented styling fix.

### Read-only local record corroboration

Opened `data/processed/t051-manual-20261115.sqlite` using SQLite URI `mode=ro`.
Queried reports/reviews/attempts/audit_events; performed no mutations, provider
calls, environment-file reads or automated browser actions. Found three reports,
five reviews and five corresponding analyst_review events, all with actor Vedran.
The database remains ignored local data; no copy is added to Git.

| Attempt | Report | Reviews in order |
|---|---|---|
| att_3229eb6c4d28486c91c6412553695ac1 | e2716a6cf0908af8692cc198c34ceb7fadce60299acc352395024ec8db155274 | rev_9303dc2063f14a76a3671212884a21d9 (close, 11:13:44.463527Z); rev_2ea9a4e124584797b87b7bbdc2054ae4 (close correction, 11:18:06.290082Z); rev_e663891c8c064fc8ad239cff52b204db (escalate correction, 11:19:50.968802Z) |
| att_79fd6d77ceb24d8bafc63bb743bcd19f | 66d5a8244f96e51c20ddfe20b1f5f5186172da547a0f5a9f9d0fb2d94e061888 | rev_c8562bb648584e858a1c5467114bf72a (request_more_information, 11:20:52.601466Z) |
| att_6738a21d14a14e019ad89f158574efe8 | 973f475a6ced049c2c979fa6f69eda6aaa3242d9fc2a65114ad43205465f27f4 | rev_3b2711c078394a2f9d1dff32e7c221d1 (needs-information request_more_information, 11:22:58.376954Z) |

All timestamps above are UTC on 2026-11-15. The first report's review audit
revisions are 4->5->6->7, with both supersedes links intact and the same report ID.
Thus the escalation superseding rev_2ea... rather than the originally shown
rev_930... is explained by a real intermediate close correction, not a broken
chain. The three attempts are reviewed at revisions 7, 5 and 5 respectively.
The first report's stored citations match the user's initial/reopened transcript.
No before/after byte snapshot was taken here; do not infer a new full immutability
test solely from this database inspection. All three dispositions were observed,
but escalation was a correction, not a fresh initial escalation in this manual run.

### Confirmed UI finding; T051 remains open for resolution

`frontend/src/investigation/controller.ts` show() unconditionally emits
`view.recoveryError('stale_snapshot', true)` whenever `blocked` is true.
The review error handler sets blocked for revision_conflict, calls show(), then
emits the actual revision_conflict message. Therefore a revision conflict can
produce both messages without any source snapshot actually changing. This is a
code-supported explanation for the user's dual error message, not a claim that
an HTTP stale_snapshot response was observed or the server changed source data.

Concurrency protection and correction persistence have human evidence; the
additional error label is incorrect. No product code was changed and T051 is
still unchecked pending a focused RED/GREEN correction and repeat of that UI
step. No need to repeat all previous manual checks merely to restate them.
The screenshot layout may be handled separately; no CSS change is claimed.
Next concrete step: preserve/render the actual blocking error code in show()
and test revision_conflict without a false stale_snapshot warning, retaining
the genuine source-snapshot recovery behavior. T033/T052 remain open; no new
live calls, package installations, full suites, commit or push occurred here.

## T051 error-label correction and closure — 2026-11-15

User explicitly requested the fix: [original request](../../prompts/development/003-t051-conflict-label-fix-2026-11-15.md).
Earlier open-finding text is historical. Product change is limited to
`frontend/src/investigation/controller.ts`: retain the actual blocking error
code instead of a boolean, render it once, preserve it on selection/re-render,
and clear it only on successful explicit refresh. Review/retry/cancel state,
server revisions, scope and mutation authorization remain unchanged. Uncertain
transport outcomes still preserve form/key and show their nonblocking message.

### Actual RED -> GREEN

Extended review and recovery Vitest cases for revision_conflict, stale_snapshot,
request_conflict and invalid_transition. Verify one correct alert, absence of a
false stale_snapshot, disabled blocked actions, retained review input, no
automatic refresh/retry, actual-code preservation after reselecting the attempt,
and action availability after explicit refresh. Genuine stale_snapshot remains
covered; timeout/input/key and late-response tests remain intact.

```powershell
npm.cmd --prefix frontend test -- --run tests/investigation-review.test.ts tests/investigation-recovery.test.ts
# RED before product change: 8 failed / 12 passed (20 total), exit 1.
# Intended failures: false stale_snapshot or duplicate stale_snapshot alert.
# GREEN after product change: 20 passed, exit 0.
npm.cmd --prefix frontend run typecheck
# PASS, exit 0.
npm.cmd --prefix frontend test -- --run
# Final, including reselect assertions: 186 passed / 9 files, exit 0.
npm.cmd --prefix frontend run build
# Typecheck + production Vite build PASS, exit 0.
git diff --check
# PASS, exit 0.
```

Seven additional generated test cases relative to the previous 179-test suite;
no skips/xfails or weakened requirements. No new backend tests/full backend run,
provider request, package installation, real .env read, database write, automated
browser run or post-fix human-browser observation is claimed. The manual evidence
predates this small message correction; the correction has fresh DOM regression
coverage. Original human findings and automated historical evidence remain
distinct. Screenshot form wrapping is not changed by this fix.

T051 is complete for its required fixture/test-provider review behavior, based
on Vedran's real manual findings, corroborated IDs/audit and corrected UI recovery
regressions. Escalation was exercised as a linked correction; initial automated
coverage for all three dispositions remains historical and labeled as such.
No broader independent code review, reproduction or live LLM quality approval
is inferred. T033 and T052 remain unchecked. Next concrete step: independent
human review/freeze of the prepared T052 evaluation pack. No T053+ implementation,
commit or push performed.
