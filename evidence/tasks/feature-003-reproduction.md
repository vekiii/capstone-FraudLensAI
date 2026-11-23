# T066 executable handoff and teammate reproduction — 2026-11-15

**Current record: 2026-11-17** at the end of this file supersedes dated pending
statements only where concrete evidence exists. T061 audit was executed with
FAILED quality; T062–T064 are complete in their documented controlled scope.
T066 scoped human review is now complete (final decision at end); T094 independent
review remains open. Earlier pending entries are historical.

## Latest agent reproduction - 2026-11-16

[Fresh run/review evidence](feature-003-offline-review-20261116.md): backend 921
PASS, frontend 186 PASS, Ruff/typecheck/build PASS, 29 isolated actual browser/
API/proxy and 6 process observations PASS. Fixed one unit test's dependency on
an ignored historical live artifact using an independently hashed test fixture
and changed/missing negative cases. Runtime/frozen results were not changed.
Existing app port 5173 was preserved; generated harness used 5174 and cleanup
passed. No provider/environment-file access or package installations.

These are agent-executed checks, not another teammate's manual execution or
human code/contracts sign-off. The actual teammate table below stays pending;
T066 remains unchecked. T094 technical clarification proposal is ready for
human review, with historical quality failures preserved.

Status: **partial**. Documentation and independent automated regression are
complete; another teammate's actual execution and human code/contracts/evidence
review are **pending**, as is full T061. No names, signatures, dates, commands or
results below are filled in on someone else's behalf. Earlier foundation/team
reviews and T051 confirmation do not constitute this Feature 003 reproduction.

## Prepared documentation

Updated [root README](../../README.md), [frontend README](../../frontend/README.md),
[knowledge README](../../data/knowledge/README.md) and
[quickstart](../../specs/003-ai-investigation/quickstart.md): actual local settings,
CLI arguments, separate worker, safe test-provider mode, reviewed corpus archive,
demo versus frozen retrieval configuration, live execution history and pending
quality/producer gates. Removed stale claims that T033/T051/provider/report work
are unimplemented and removed non-executable evaluation command placeholders.

## Another teammate's concrete deterministic procedure

1. Agree a checkout/commit including this change after the team publishes it.
   Do not silently merge producer/ML branches. Read AGENTS.md then next_work.md.
   Record your actual identity/role, date/time, OS, checkout path, `git branch
   --show-current`, `git rev-parse HEAD`, `git status --short`, Python/uv/Node/npm
   versions. Before commit, record HEAD plus the reviewed diff because HEAD alone
   does not identify these uncommitted files. Use another teammate as runner;
   this agent's setup is not second-person reproduction.
2. Follow quickstart Setup with Python 3.14 / Node 24 and locked dependencies.
   Use existing .venv on the prepared laptop; do not reinstall routinely. On a
   fresh machine install committed locks. Do not send secrets in evidence.
3. Follow Deterministic local setup exactly: provider=test, source=fixture,
   explicit empty process key/model and a separate investigation store. Prepare
   reviewed knowledge; note returned corpus/retrieval IDs. Start backend and
   Vite in two terminals on 127.0.0.1:8000 / :5173. Leave any unrelated processes
   alone; resolve occupied ports with their owner.
4. Query health and cases directly and through proxy with Invoke-RestMethod.
   Search `supporting documentation`, inspect exact passage/version/source/
   jurisdiction/simulation limitations, then `nomatchxyz`. Note the demo 0.5
   heuristic differs from frozen evaluated baseline. Open all three cases,
   navigate back and rapidly switch selections; verify no mixed stale view.
5. Open CASE-001 investigation and explicitly create a test attempt. It stays
   queued until you run `worker --store data/processed/investigations.sqlite
   --once` in a third terminal with the **same** settings/PYTHONPATH. Inspect its
   authored test report/limitations and exact cited evidence. No OpenAI call is
   needed. Retry/cancel a diagnostic attempt explicitly; inspect saved history.
6. Review a test draft using your actual configured analyst alias and rationale;
   reopen it and append a correction. Verify the original draft/citations and
   prior review remain immutable. Use two browser sessions for stale revision
   conflict/refresh. These diagnostic review decisions are not T059 ratings.
7. Stop only your foreground backend, refresh and note the controlled error;
   restart and Retry. Check `curl.exe -i http://127.0.0.1:8000/api/cases/CASE-999`
   gives 404 and CASE-1 gives 422; repeat via :5173. Record actual envelopes.
8. Run the complete regression commands in quickstart and save exit codes/counts.
   Stop your own foreground demo services first. Optionally run the Phase 8
   automated browser verifier with installed Chrome/free 8000/5173/9228; label it
   automated. It creates separate .cache stores/profiles and safe absent .env.
   Pass `--result-prefix feature-003-peer-youralias-yyyymmdd` to the verifier to
   save your outputs under distinct filenames; never overwrite Phase 7
   reports or T055/T056 freeze. Do not invoke a probe/live worker/evaluation.
9. Review changed code/tests, schemas and evidence. Specifically inspect
   [producer reconciliation](feature-003-context-review.md), strict identities,
   exact money/time/score semantics, privacy, missing/empty history and remaining
   unavailable adapter. Human producer/consumer approval is separate and must
   name the actual reviewed SHA/interface/decision. Do not approve unknown
   semantics merely because a synthetic test passes.
10. Record below actual commands/exit codes, API/UI observations, issues and
    unexecuted scenarios. Send the filled record in this conversation or the
    team's normal review workflow. No external message is sent by this agent.

## Actual reproduction/review record (unfilled)

| Field | Actual evidence |
|---|---|
| Runner / reviewing teammate | pending |
| Date/time / OS / checkout path | pending |
| Branch / HEAD / clean status or reviewed diff | pending |
| Python / uv / Node / npm / browser | pending |
| Dependency commands / exits | pending |
| Corpus/retrieval IDs / exact passage comparison | pending |
| Backend / frontend / typecheck / build / Ruff / diff commands and exits | pending |
| Direct health/API and proxy / 404/422 | pending |
| Case list/detail/back / rapid selection / Retry | pending |
| Test worker / report / evidence / cancel/retry | pending |
| Explicit review / amendment / two-session conflict | pending |
| Code/contracts/evidence findings and actual decision | pending |
| Issues / unexecuted steps / evidence filenames | pending |

Phase 8 agent results are in [regression evidence](feature-003-regression.md).
T066 checkbox remains empty until actual teammate evidence plus T061 exist.
T059 human rating assignments are superseded by the user-approved automated
report-judging-v2 amendment; execution/aggregation/audit completed with failed
quality, see [actual results](feature-003-automated-evaluation.md) and
[judge decision](feature-003-judge-amendment.md). Original reports and failed
quality/time targets remain preserved in the historical
[Phase 7 handoff](feature-003-t058-t061-handoff.md).
T067/Converge and full acceptance have not been run or inferred.

## User-approved T066 review amendment and progress, 2026-11-16

User explicitly confirmed the team agreed that the user performs the human review,
including parts they helped implement. This supersedes the requirement for a
second teammate for T066 only. Record as contributor self-review, not independent
reproduction; independent quality/evaluation gates are unaffected. Historical
second-teammate instructions above describe the previous procedure.

User-reported execution (not independently executed by the agent):
- Branch: feature03; reviewed HEAD:987b64cf8717a18eafc95c2dbcbc3655c9d6898c.
- Python3.14.3; Node24.20.0; npm11.19.0; checkout D:/AIBootcamp/capstone.
- Working-tree cleanliness, uv/browser versions and exact execution time unreported.
- prepare-knowledge returned retrieval071f1a593fa17471295860bb5abc3a0064261a7e159bdf3d530494881001bccb
  and corpus_2fa1aa3379fadf2749300897ef79b9239c2ced2da311b370a8974d709b0bfaf3.
  Exact passage comparison and command exit code not yet reported.
- Vite startup failed: Port5173 is already in use. This does not establish UI success.
  Leave other processes intact; use5174 or stop an identified owned Vite terminal.
- UI, worker, review/correction/conflict, API and regression observations pending.

T066 remains unchecked; human review has started, not been completed.

## Current T066 handoff to Milan - 2026-11-16

User explicitly assigned the REST of this review to Milan. Milan has not yet
reported execution or approval. Keep T066 unchecked. Prior user self-review is
preserved and must not be attributed to Milan or relabeled independent review.
Earlier pending statements are superseded only by the concrete observations below.

Additional actual user-reported observations from this conversation:
- Search supporting documentation returned US supporting records first and IBM
  synthetic field limitations second. First result opened the Supporting
  documentation passage, authored-v1-2026-11-14, historical2007 US scope,
  FinCEN link, dates, exact short excerpt and authored-summary limitations.
  Source rendering observed; independent comparison to original website unrun.
- nomatchxyz displayed Nema dovoljno dobrog pogotka.
- Worker output and UI both ready_for_review for
  att_6f254c9544c544baad75ac473c76fec3.
- TEST provider notice present; saved evidence opens; missing decision and empty
  rationale rejected according to user. No model-quality conclusion.
- Reload preserved close review rev_1a692774fc244fc78ce007a8b8445e36,
  actor literally TVOJE_IME, timestamp2026-11-16T14:45:53.776903Z,
  rationale T066 ? provera ?uvanja odluke. Do not replace this alias with a real name.
- Correction escalate rev_9e1c3aaa855548cfa355144736ccdb65 at
  2026-11-16T14:50:24.622660Z, rationale T066 ? korekcija,
  correction note Provera istorije odluka. Displayed previous review
  rev_dd5a17b53e614e27bf244e04aa4dacd6, DIFFERENT from the supplied close ID.
  Intermediate review or changed selected attempt not established; chain verification
  remains unresolved. This mismatch alone is not a proven implementation bug.

Milan's remaining checks:
1. Record actual identity/role, branch/HEAD/diff, environment and commands. Read
   AGENTS.md, next_work.md, quickstart and this current handoff. Use provider=test,
   source=fixture and empty process key/model. Backend8000; frontend5174 was
   proposed after5173 was occupied; confirm actual available ports, do not kill
   unrelated processes. Use same store/config in API and worker terminals.
2. Resolve the review-chain mismatch above using the exact selected attempt and
   saved review history. If the user's local store is unavailable, say so and
   independently reproduce a fresh linked correction; do not invent old events.
3. Execute two-window stale revision conflict and refresh; prior user has not
   supplied the conflict result for this T066 run.
4. Verify cancel/retry, backend failure/restart recovery, direct/proxy404 and422,
   and remaining case navigation/rapid-selection checks.
5. Run documented backend/Ruff/frontend test/typecheck/build and diff checks;
   record real counts/exits. Inspect new dataset adapter and run controlled
   producer smoke; distinguish it from unavailable full IBM/model validation.
6. Review code/contracts/evidence, record findings, unrun cases and explicit actual
   decision in this file under Milan's own dated record. Keep user and Milan
   observations separate; his participation in implementation, if any, disclosed.

T061/quality findings and T094 remain separate open conditions. No live API batch,
regrading, merge, commit or push authorized by this handoff. Next step: Milan
records his reviewed checkout and starts remaining T066 checks. T067 remains open.

## Current T066 continuation — 2026-11-17

User explicitly identifies the current operator as **Milan**, GitHub
**milangavric2003**, and authorizes the AI to check/start local setup. Git history
shows implementation under his alias (including review/recovery/reliability), so
record **contributor self-review**, not independent reproduction. No human
completion/approval has been reported in this continuation yet.

Preserve attribution:

| Evidence owner | Established facts | Limits |
|---|---|---|
| Earlier user self-review, 2026-11-16 | Exact search, report, review/correction observations and IDs above | Historical runner identity was not explicitly established; do not retroactively assign to Milan or Vedran. Actor TVOJE_IME remains literal. |
| Milan, current user, 2026-11-17 | Identified as milangavric2003; implementation involvement supported by Git authorship; supplied report/opened procedure and explicit saved test decision, detailed observations below | Correction/conflict, T066 code-review decision and T094 approval remain pending. |
| Vedran / Git alias Veki | Git author of 987b64c adapter work and 2469aec handoff | Commit authorship is not execution/sign-off of any listed manual scenario. No new Vedran manual result supplied. |
| AI, 2026-11-17 | Fresh regression, browser/process reproduction, source/contract/archive review and local demo setup | All automated; cannot fill the human result/approval fields. |

[Detailed actual commands, issues and outcomes](feature-003-t066-review-20261117.md).
Reviewed baseline: feature03 / 2469aec0b146c5c26cb5c0eea70cb96bb9c559e3,
initially clean; subsequent reviewed diff is docs plus one verification-helper
constructor compatibility correction, with new evidence/prompt records. No
application runtime, public schema, prompt, lockfile or frozen evaluation edit.
AI environment: Windows11, Python3.14.7, Node24.20.0, npm11.19.0, uv0.10.9,
automated Chrome157.0.8103.79. These are AI-observed, not manually supplied by Milan.

Fresh AI checks: backend939 PASS/57.83s; frontend186 PASS; Ruff/typecheck/build
PASS; 29 actual browser/API/proxy plus6 process checks PASS across separately
recorded components. Prior sandbox/port failures and the recovery-helper HTTP500
failure are preserved; fixed recovery/process rerun has its own filenames.
Controlled pinned-producer smoke PASS with no source writes, label/provider
reads. Full IBM/model exercise remains unrun. T062–T064 implementation not repeated.

Current manual checklist (fill only from actual Milan observations):

- [x] Current operator identity supplied by Milan; implementation involvement
  disclosed from Git history. AI recorded baseline/environment/diff scope above.
- [x] Milan confirms combined file/evidence review including recorded checkout/
  diff/environment provenance. Commands were AI-executed; no independent human
  environment reproduction or personally run terminal commands claimed.
- [x] Milan supplies queued/created UI evidence for the separate CASE-002 test.
  Original CASE-001 intermediate queue display remains unreported, not backfilled.
- [x] Milan supplies the ready_for_review report/TEST notice and opened procedure
  with limitations. Worker execution was AI, not Milan's manual CLI execution.
- [x] Fresh explicit test decision supplied by Milan; AI confirms attempt/report
  binding and unchanged draft/citations/budget. Actual review ID recorded below.
- [x] Linked correction preserves original report and prior review; Milan supplies
  actual correction/predecessor IDs and AI confirms both saved records unchanged.
- [x] Milan reports two-tab stale revision4 submit rejected with revision_conflict;
  first-tab reload preserves the original decision at revision5.
- [x] Following the guided refresh/correction step, Milan supplies the saved linked
  correction; API confirms revision6 and the exact original predecessor.
- [x] Explicit CASE-002 cancellation observed in Milan's before/after screenshots;
  API confirms cancelled, zero provider/tool counters and no report/review.
- [x] Explicit retry has a saved parent link; Milan's screenshot shows queued
  child/list and opened cancelled history, with exact linkage checked by AI.
- [x] Milan supplies latest CASE-003 child after guided reload/reopen, showing
  ready_for_review and exact predecessor link; cancelled parent was inspected.
- [x] User-requested controlled CASE-003 repeat: one base creation, one cancel,
  one linked retry, parent view and label comparison without extra actions.
- [x] Milan observes backend-stop error and confirms same-panel recovery after
  API restart: ready_for_review/report, unchanged4/8 requests and3/12 tools.
- [x] AI executes direct/proxy404/422 checks; actual envelopes recorded separately
  from human results, no Milan terminal execution claimed.
- [x] Milan confirms requested rapid case switching; screenshot ends at matching
  CASE-003/TX-003,18420.50 EUR,score0.1, with no reported mixed/stale case data.
- [x] Milan reviews code/contracts/evidence, records actual findings, unrun checks
  and an explicit approve/request-changes/reject decision for T066's documented
  scope, retaining failed quality/full-integration limitations.

Old-chain status: AI read-only query of the local investigation store found none
of the exact historical attempt/review IDs above. The prior D: checkout's store
is unavailable here. **Old mismatch unresolved**, no inferred intermediate event
or implementation bug. The checklist explicitly permits a fresh linked-chain
reproduction in this situation; it will not resolve the absent historical data.

Manual setup prepared by AI: http://127.0.0.1:5174, API8000,
`.cache/t066-milan-20261117/manual.sqlite`, fixture/test, no real ENV_FILE or
provider credentials, analyst alias milangavric2003. Corpus/retrieval IDs match
the reviewed versions above. AI subsequently observed a newly created attempt
`att_4c34755d3e0a4b8694ae02489bfa4b3e` queued/created with zero counters and ran
the matching worker: ready_for_review/revision4, four scripted test turns/three
tools, zero live calls. Report ID and citations are in the detailed evidence.
Milan subsequently supplied the rendered ready_for_review report and opened
procedure below, followed by the saved test decision recorded below. The earlier
API check alone did not establish his viewing or imply a saved decision.
Helper after explicit UI creation:
`.venv/Scripts/python.exe -X utf8 .cache/t066-milan-20261117/run.py worker`.
It uses the exact same configuration/store as its API. Do not invoke a live worker.

T061 task audit and T065 automated regression are completed; historical wording
"full T061 pending" conflated task execution with unmet quality acceptance.
SC-002/003/006 and full dataset/model integration remain unresolved. T094 now has
a [current decision packet](../../specs/003-ai-investigation/calibration-clarification-proposal.md)
and verified original raw v8 archive; actual independent human decision pending.
T066 stays unchecked until human evidence/review exists. T067 awaits those T066
conditions; no Converge completion or full feature acceptance is inferred.

### Milan's actual reported observation — 2026-11-17

Milan supplied the UI text for CASE-001 with the exact current context/snapshot/
corpus and report `1b55d40ce5fc4d47887d0e4cc827f4838751437824b241a9fa6e775f37b29b5a`,
attempt revision4, ready_for_review. He reports the TEST-provider notice, four
requests/three completed tools, schema/reference validation passed and semantic
review pending. The draft displays1250.00 EUR with case citation
`ev_4c2194c9160e4d6aa711a24748105933`, missing occupation/device/funds origin,
unavailable-history limitation and the human-final-authority notice.

He opened procedural citation `ev_4cb03822cfd84b828d96c03e852605a6` and supplied
its exact text/provenance: Simulated missing and conflicting facts,
authored-v1-2026-11-14, section Missingness, local:fraudlens/sim-missing,
simulated educational source, not bank policy. Returned1/eligible1, not truncated;
saved corpus matches the report. Source reviewer Milan Gavrić/date2026-11-14
is existing corpus-review metadata, not a current case approval.

Milan asks whether TEST/evidence are correct and what they mean; this is an
observation/question, **not acceptance or a semantic-quality rating**. AI GET
independently confirms exact procedural evidence/corpus binding and current
state ready_for_review/revision4/review=null. No mutation/provider dispatch in
that verification. The original queue display remains unreported by Milan.

### Milan's saved initial test decision — 2026-11-17

Milan reports: actor `milangavric2003`, timestamp
`2026-11-17T00:50:57.922620Z`, disposition `request_more_information`, review
`rev_40f8c34cf0464ced9ef449bb941e42db`, rationale exactly:
`T066 — test čuvanja odluke; nedostaju dodatni podaci.`
UI explicitly labels this a local decision record, not LLM-quality scoring or an
independent evaluator signature. This is an actual diagnostic case disposition,
not T066 completion, T094 approval or feature acceptance.

AI GET independently confirms the same review, original report binding, state
reviewed/revision5, correction_note=null and supersedes_review_id=null. Comparing
saved pre-review and post-review API snapshots confirms exact original report
draft/citations and budget unchanged; revision4→5. All review writes were Milan's
UI action. AI only read/compared existing state; no provider call or mutation.

### Milan's actual stale-tab conflict / first-tab reload — 2026-11-17

Milan supplied both rendered tabs after trying the diagnostic close decision:
first tab after reload remains reviewed/revision5 with
`rev_40f8c34cf0464ced9ef449bb941e42db`, request_more_information and unchanged
rationale. The second tab remains ready_for_review/revision4 and displays exactly:
`revision_conflict. Osvežite sačuvano stanje pre nove radnje.`
This is actual human-observed stale-write rejection and persistence after reload.
AI separately GETs the attempt: revision5/original review unchanged, original draft
and budget equal the pre-review snapshot. AI did not submit the rejected write
or any correction. No correction/refresh outcome is inferred yet. The old D:
review-chain mismatch remains unresolved; this fresh chain is separate evidence.

### Milan's saved linked correction — 2026-11-17

Following the explicit refresh/correction instructions, Milan supplies:
actor milangavric2003, UTC2026-11-17T00:59:09.046218Z, disposition close,
review `rev_b30f69e52fc74628b112ebe27d7a2e0f`, rationale exactly
`T066 — test povezane korekcije odluke.`, correction note exactly
`Provera istorije; prethodna odluka mora ostati sačuvana.`
The UI links to `rev_40f8c34cf0464ced9ef449bb941e42db` and states the predecessor
is retained. No separate intermediate refresh screenshot is claimed.

AI read-only API confirms reviewed/revision6, current correction and exact
supersedes link. A SQLite mode=ro query finds exactly these two review rows for
this attempt, ordered initial→correction; the entire initial review equals the
previously saved initial-review API snapshot. Original report draft/citations
and budget equal the pre-review snapshot. Both writes were Milan's UI actions;
AI performed only GET/comparison/read-only audit. Fresh chain verified. Old
unavailable D: chain remains unresolved; no historical reconstruction inferred.
T066 overall review and T094 approval remain open.

### Milan's queued/cancelled screenshots — 2026-11-17

Milan attaches two conversation screenshots, before/after explicit cancellation,
and reports that the first clearly waits for the worker although he did not
notice the literal created word. AI visual inspection sees `created` beside
`2026-11-17T01:00:55.100987Z`, plus `Posao je sačuvan i čeka worker.` and the
cancel button. Second screenshot shows `cancelled` in the saved-attempt item and
state, with explicit retry/reuse controls. Both show TEST provider and0/8 requests,
0/12 tools, same context/snapshot/corpus. Screenshots remain conversation
attachments; no repo screenshot file is claimed. Crop does not show the case ID;
API binding identifies CASE-002 by the exact timestamp/context.

AI GET separately confirms CASE-002/run inv_f9ca77a1c71b4f119d17b47bb93596fc,
attempt `att_01d1d0cf537d4b18a8714f7f81cd0c5c`, cancelled/revision2,
created_at2026-11-17T01:00:55.100987Z, updated_at2026-11-17T01:01:37.996952Z,
zero requests/tools, null report/review. Queue/cancel UI actions are Milan's;
AI did not run a worker or mutate this attempt. Original CASE-001 review chain
remains separate. Retry has not yet been observed.

### Milan's retry/history screenshot and exact API lineage — 2026-11-17

Milan supplies a screenshot with two saved run entries: latest created at
2026-11-17T01:03:31.271014Z and original cancelled at01:00:55.100987Z. The open
history panel shows cancelled, TEST,0 requests/tools and matching context/corpus.
Screenshot alone does not identify which cancelled attempt is open or establish
parent IDs; AI checks the actual saved lineage before accepting the retry check.

API confirms child `att_69a521e11cf74702a40969eff93dea4f`, created/revision1,
belongs to run `inv_3a815875c0bd47938e44308bdcff2afd` and explicitly points to
`att_b68477162299435589cf83417014b6b2`. That immediate parent is a separate base
attempt created at01:02:38.768507Z, cancelled/revision3 after retry reservation,
same run/case/context/snapshot/corpus and0 requests/tools. It is **not** original
cancelled `att_01d1d0cf537d4b18a8714f7f81cd0c5c`, which remains unchanged in its
own run. Read-only audit confirms parent cancel/retry_child and child retry/binding
events; no missing intermediate attempt is invented. Two list entries count runs,
not parent/child attempts. Exact linkage is AI-verified; screenshot is Milan's UI
observation. Intermediate extra base creation/cancel UI steps were not separately
reported and are not attributed as human observations.

Found a UI wording issue for T067 follow-up: the opened parent is labeled
`Istorijski izveštaj — vezan za prethodni kontekst izvora.` even when parent and
child share the exact context. `controller.ts:show` passes historical=true for
parents absent from the latest-attempt list; `views.ts` treats that flag as a
previous-source-context claim. This overstates a source change; API binding is
correct and no mixed evidence observed. Record for Converge under FR-021/FR-002;
no runtime fix or acceptance waiver in this manual-review step.

After confirming exactly one queued child in the isolated manual store, AI runs
the matching `run.py worker` once: exit0, child ready_for_review. This is AI test
worker execution, not Milan's CLI run or live LLM. No human child-reopen result
yet. First audit-print attempt hit Windows console UnicodeEncodeError; inspection
was repeated with ASCII-safe JSON output; no stored data changed.

### User clarification / controlled repeat requested — 2026-11-17

Milan now reports that he cancelled an additional attempt between the previously
guided steps and requests a repeat before treating the history wording as a
Converge defect. This is consistent with the previously observed extra base/
cancelled-parent lineage; his clarification does not itself name the extra ID.
Preserve the exact API lineage and prior screenshots, rather than rewriting the
retry as having the first cancelled attempt as parent.

The earlier history wording observation and code mapping remain recorded as a
candidate for verification, **not an appended Converge task or final defect
decision**. Extra cancellation explains the additional attempt; it does not by
itself establish a source-context change. Per user request, compare wording and
exact context IDs on a fresh minimal chain before deciding follow-up. No change
to runtime or completed task markers. CASE-002 child ready_for_review is currently
AI-confirmed only; its human reopen observation remains pending.

AI read-only baseline: CASE-003 has zero saved runs. Use it for the controlled
repeat without clearing any previous attempts. No worker/new run dispatched by
AI. First unit is one explicit base creation followed by exactly one cancellation;
stop before retry and record its identity. Later unit is the lower retry control
and parent read with the same context, followed by wording comparison.

### Controlled CASE-003 base identified — 2026-11-17

Milan supplies a cancelled screenshot with exactly one saved investigation,
created timestamp2026-11-17T01:09:32.722442Z, TEST,0/8 requests,0/12 tools,
context a57c1235dbafc97a4f13a41fb3ba53ca5f58e3b6f833049764264e4b02cbed86
and the lower retry button. This is the human observation for the controlled
base cancellation; no linked retry/history result is claimed yet.

AI GET confirms CASE-003 has exactly one run inv_bb544c097ede4a23b19557e1a2fe2a46,
base attempt `att_363daf9e442841ff8221068119c346d3`, parent=null,
cancelled/revision2, same timestamp/context and zero requests/tools. No worker
or mutation performed by AI. This exact ID must be the next child's parent;
preserve it as the controlled comparison point for the history label.

### Controlled repeat result — 2026-11-17

Milan's next screenshot shows one saved run with latest child created at
2026-11-17T01:10:49.836445Z and the opened cancelled predecessor, again labeled
`Istorijski izveštaj — vezan za prethodni kontekst izvora.` TEST counters remain0.
AI GET confirms child `att_550de71019924ae4a76fe2b5d5c91816` points exactly to
pinned base `att_363daf9e442841ff8221068119c346d3`; there is one CASE-003 run,
not an extra independent investigation. Parent cancelled, child created; run,
case, context_revision, snapshot, corpus and retrieval identities all match.
Thus the previous-context wording is reproduced on the minimal controlled chain,
independent of the earlier additional cancellation. This is a confirmed display
wording defect for T067/FR-021/FR-002, not a data-binding or cancellation failure.
No runtime fix/task append or human acceptance inferred here.

After that capture and checking that only this child is queued, AI runs matching
test worker once: exit0, child ready_for_review. Human ready/reopen confirmation
is still pending; no live API or new quality evaluation.

### Human reopened child / controlled API outage — 2026-11-17

Milan supplies the guided reload/reopen screenshot: latest child timestamp
2026-11-17T01:10:49.836445Z, ready_for_review and exact predecessor
att_363daf9e442841ff8221068119c346d3, with parent-opening control. Human retry/
saved-child reopen is confirmed on CASE-003; no separate CASE-002 reopen image
is claimed or required to repeat the same behavior.

Next recovery unit: AI identifies only manual API Python processes by exact
`.cache/t066-milan-20261117/run.py api` command (launcher20672/child26052).
First Stop-Process attempt reports NullReferenceException and API health remains
200; it did not stop the service. Revalidated those commands and used .NET
Process.Kill on only those two PIDs. Direct8000 health now fails connection with
curl exit7; frontend5174 root remains200. API is deliberately DOWN pending human
error observation; no store deletion, worker or provider dispatch. Existing5173
and manual Vite26472 are preserved. Actual browser error/restart result pending.

### Human outage error / AI restart — 2026-11-17

Milan supplies the CASE-003 screenshot after explicit refresh with API down:
`Istraga nije spremna ili odgovor nije ispravan (invalid_response). Osvežite stanje.`
The previous ready_for_review list item is retained; create is disabled and
explicit saved-state refresh remains available. This confirms human-observed
controlled error, not browser recovery yet.

AI restarts the identical absent-ENV_FILE/fixture/test helper and manual store,
hidden launcher PID27068; process ledger updated, separate api-restarted logs.
Direct8000/proxy5174 health200. GET confirms child ready_for_review/revision4/
four scripted turns/three tools, cancelled parent revision3/zero counters, and
CASE-001 reviewed/revision6 with original linked correction retained. No new
worker/provider dispatch or attempt; persisted states survive API restart.

AI also executes direct/proxy foundation error GETs: CASE-999404 and CASE-1422
on each port, recording actual envelopes in the detailed technical evidence.
These are AI checks, not Milan's terminal execution.

### Milan's explicit recovery confirmation — 2026-11-17

Milan explicitly confirms the requested restored ready_for_review/report and
unchanged4/8 requests,3/12 tools, offering a screenshot if necessary. Record as
human text confirmation; no screenshot was supplied/required and no image
artifact is claimed. Along with his actual outage screenshot and AI API checks,
this completes the manual backend stop/error/restart/explicit-refresh recovery
unit. No human code-review/sign-off or T094 approval inferred.

### Human rapid-navigation confirmation — 2026-11-17

Milan confirms the requested quick switching leaves the correct final selection
and supplies CASE-003/TX-003 screenshot:18420.50 EUR,score0.1/fixture, correct
synthetic parties/time. No mixed/stale case data reported. The investigation panel
is collapsed in this image; no unseen report/citation inspection is claimed from
the screenshot. Earlier report/reopen checks and automated race checks are separate.

## Remaining human code/contracts/evidence review packet

Current reviewed baseline remains feature03/2469aec0b146c5c26cb5c0eea70cb96bb9c559e3.
AI rechecked branch/HEAD and diff. Runtime source/public schemas/application
prompts/locks have no edits in this session; changed executable is the three-line
optional-constructor forwarding fix in recovery verification helper. Documentation
and new evidence/prompt records are uncommitted. Milan still needs to inspect the
checkout/diff and report what he actually reviewed; AI checks are not that review.

Review in small groups; note actual findings or unresolved questions for each:

| Group | Sources to inspect | Concrete review questions |
|---|---|---|
| 1. Decisions/audit | [review.py](../../backend/src/fraudlens/investigation/review.py), [store.py](../../backend/src/fraudlens/investigation/store.py) append_review and immutable triggers, [API contract](../../specs/003-ai-investigation/contracts/api.md) Phase6 | Are actor/report/revision/latest predecessor checked before save? Does a correction append rather than overwrite? Can review dispatch a provider or automatic account action? Compare the actual two-review chain/conflict above. |
| 2. Context/privacy | [accepted boundary](../../specs/003-ai-investigation/dataset-adapter-agreement-v2.md), [dataset.py](../../backend/src/fraudlens/investigation/dataset.py), [tools.py](../../backend/src/fraudlens/investigation/tools.py) | Check read-only bounded source access, bank+account/time/direction/currency scope, unavailable versus empty, allowlisted data and no private labels. Keep completed controlled adapter scope separate from unrun full IBM/model integration. |
| 3. UI/reproduction | [controller.ts](../../frontend/src/investigation/controller.ts), [views.ts](../../frontend/src/investigation/views.ts), [technical evidence](feature-003-t066-review-20261117.md), current human observations above | Check case/context/revision guards, recovery/helper correction and actual AI versus human attribution. Record confirmed same-context historical-label defect for later Converge. |
| 4. Quality/scope | [T061 closure](feature-003-automated-evaluation.md), [v8 results](feature-003-final-live-v8-results.json), [clarification proposal](../../specs/003-ai-investigation/calibration-clarification-proposal.md) | Executed audits are not achieved quality targets. Retain0/8 quality,0.50/0.50 retrieval, latency failures, failed v8 calibration/unavailable quality and full integration limit. T094 independent rubric decision remains separate. |

Human review record: group1 finding supplied below; remaining inspected paths/
checkout/diff/environment and final decision **pending**. No approval inferred from successful
UI checks or source-review metadata. A T066 scoped review may explicitly carry
remaining defects into Converge; it cannot assert full feature acceptance.

### Milan's group1 source review finding — 2026-11-17

After receiving links to review.py submit and store.py append_review and the
revision/predecessor/append-only review questions, Milan states:
`pregledao sam, deluje u redu`. Record as actual human inspection of the supplied
group1 code with no objection reported. No separate claim that he read the API
contract, checked environment/diff, approved other groups or signed off T066.
This is contributor self-review, not independent quality validation. AI did not
write a disposition or infer broader acceptance from this response.

### Milan's group2 review / batching preference — 2026-11-17

Milan replies `okej je, dalje` to dataset.py and accepted adapter agreement with
the specific read-only/label exclusion, bank+account/time/directional-currency and
controlled-versus-full-integration review questions. Record as group2 review with
no objections reported. He requests more files per remaining step; batch the
rest into one review packet. This response does not approve unreviewed UI/API/
evidence/diff or close T066/T094.

### Batched remaining review

Review together: frontend controller.ts/views.ts, investigation API contract
(request identity, Phase5/6, public projection), changed recovery-runtime helper,
current working diff/status, this reproduction record, technical evidence and
T061/v8 results. Use the four-group table above for paths/questions. Confirm
actual reviewed checkout/environment against the recorded baseline; note parts
not personally reviewed. Check actor/revision/citation guards, safe text/stale
responses, explicit recovery, immutable drafts and accurate AI/Milan/prior-user/
Vedran attribution. Preserve the confirmed history-label finding and old absent
store limitation for Converge; tests do not establish full quality/integration.

After actual inspection record one explicit **T066 scoped** decision: approve,
request changes or reject, with findings/unreviewed parts. This concerns
reproduction/code/contracts/evidence review, not achievement of SC-002/003/006 or
full IBM/model acceptance. Group1/2 code review results remain recorded above;
do not infer additional reading from their short responses.

Separately, T094 decision remains pending independent human review. Its proposal
asks whether a future version should require disclosure completeness AND no
invented missing values AND no contradictions, with all six controls reviewed.
Milan is a contributor, so any current feedback is contributor feedback unless
the team explicitly changes the independent-review requirement. No such change
is requested/inferred here; no new version implementation or live run authorized.

**One next step:** Milan reviews the combined packet and reports actual reviewed
scope, T066 decision/findings/unreviewed parts, plus any separate T094 feedback.
Only after T066 conditions are confirmed run feature003 Converge; T094 may remain
open and must be carried honestly without quality/integration acceptance claims.


### Final scoped T066 decision and publication authorization — 2026-11-17

Milan states: `Добро, прегледао сам ове фајлове што си рекао, делују ми ок.`
He asks to close T066 if complete, document this conversation and push to the
branch, then identify remaining Feature003 tasks. With group1/2 reviews and
actual manual observations, this completes his no-objection contributor review
of the combined UI/code/API/helper/evidence packet in its documented limited
scope. AI verifies executed T061/T065 and amended T066 conditions against the
recorded evidence and marks T066 complete. No independent reproduction or
personally run Git/version commands are attributed to Milan.

Reviewed baseline feature03/2469aec0b146c5c26cb5c0eea70cb96bb9c559e3 plus the
recorded uncommitted docs/evidence/helper diff. Known history-label defect stays
for Converge. Old unavailable D: chain, failed retrieval/report/latency targets,
unrun full IBM/model integration and independent T094 condition remain explicit.
No full feature acceptance or independent rubric adoption inferred from this
contributor review. No additional findings reported by Milan.

Current user expressly authorizes commit/push of this reviewed work to feature03,
superseding earlier no-automatic-publication instruction for this work only.
No merge/force-push, new evaluation/provider budget or further implementation.
Next: actual feature003 Converge, record remaining tasks and publish reviewed
handoff/evidence. Publication outcome will be verified separately.
