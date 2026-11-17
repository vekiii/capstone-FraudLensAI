# Current handoff — English-only retrieval scope approved; next design, 2026-11-17

Milan Gavrić/milangavric2003 explicitly approved moving the initial MVP procedure
retrieval to English. [Decision](specs/003-ai-investigation/retrieval-english-mvp-decision.md).
Serbian retrieval deferred; UI/report language remains separate. Current spec,
plan and evaluation addenda aligned prospectively. This unit changes docs only;
runtime/v3 pack and all previous results/thresholds retained. No new evaluation.

Branch feature03-retrieval-v3, starting clean HEADa2b35caaab5ccd46293945315c4d1dfee8d08b14.
[Prompt](prompts/development/003-english-retrieval-decision-20261117.md).
[Actual scope/checks](evidence/tasks/feature-003-english-retrieval-decision-20261117.md).
T095 OPEN, SC-002 UNMET. English-only supported-query behavior is not implemented
or accepted merely by this amendment; no automatic translation or broad UI rewrite.
Original0.50/0.50 and v3 development0.25/0.25 remain with original denominators;
old English successes are not a fresh acceptance result. No task markers changed.
Docs checks PASS:517 prior files byte-identical,100 markers unchanged,74 valid
local links, whitespace PASS. No backend/frontend tests run for this docs-only unit.

**One concrete next step:** prepare a separate T095 English-only development
design, defining analyst/worker query language, one bounded relevance/no-answer
improvement and new reviewed evaluation pack. Keep20 fresh held-out and at least4
no-answer, unchanged0.80/0.70 targets and separate run authorization. No old replay.

# Previous handoff — T095 development result below target; next design decision, 2026-11-17

On feature03-retrieval-v3 from clean cc712513d3a30286c23a9f1059aaffaa5dbae79e.
Milan Gavrić/milangavric2003 accepted the18-row development table/corpus and
authorized continuation. Review scope recorded honestly; no claim of comparison
against unseen old questions/semantic duplicate audit or held-out acceptance.

Ran one bounded development selection:18 questions x2 variants,36 local searches,
zero provider calls. B3/C3 both Recall/MRR0.25/0.25 on12 answerable;6/6 no-answer;
en0.75, sr-Latn0, sr-Cyrl0. Cutoffs8.863342357405378/9.745718240901956 are NEW
development outputs only. Baseline wins development tie; default not changed.
Old held-out0.50/0.50 and4/4 no-answer preserved; different samples, no direct
degradation claim. English-only discussed, NOT authorized/implemented.

Bookkeeping fix before real searches: pin development protocol meaning so later
held-out author/status metadata does not force replay; glossary/corpus/development
author changes still reject; full freeze pins whole final protocol. RED1/28pass,
GREEN29; final backend968 PASS56.61s/Ruff PASS. No .env/service/store interaction
outside new ignored development store; no live/fresh hold-out execution.
Integrity PASS:511 original files byte-identical;100 markers/79 links; raw seal,
source/projection/review/metric bindings and whitespace PASS. Old artifacts kept.

[Original request and discussion scope](prompts/development/003-t095-development-selection-20261117.md).
[Actual commands/decision/metrics/limits](evidence/tasks/feature-003-t095-development-selection-20261117.md).
[Per-question ranks and development metrics](evidence/tasks/feature-003-t095-development-results-20261117.json).
T095 remains OPEN, SC-002 UNMET. No further tuning of this same candidate from
these results, fresh acceptance authorization, push/merge or other feature work.

**One concrete next step:** team reviews this development failure and records a
separately versioned next retrieval design or an explicit language-scope decision.
Do not consume fresh held-out questions to tune this failure; current multilingual
requirements remain until an actual amendment. Existing review need not repeat.

# Previous handoff — T095 evaluator built; concrete development review next, 2026-11-17

Milan Gavrić/milangavric2003 explicitly approved v3 plan/implementation and a new
branch. Verified clean feature03 HEAD18e930ab4ad86e75f6f908b4a40a0a87def20e5b;
created feature03-retrieval-v3 there. Local commit permitted; no push/merge.
His statement that he had not seen old held-out questions is a user declaration.
No new question/reference review or fresh acceptance permission inferred.

Implemented separate offline retrieval_fresh_v3 evaluator through RED/GREEN:
reviewed development selection, immutable version-bound freeze, one-shot
authorized input-only prediction and sealed private join; errors stay in counts.
Old runtime/default search/evaluator/packs/results and services preserved.
Prepared18 AI-authored development inputs/references with readable source/rationale
table; no actual scoring or cutoff selection. Fresh held-out files absent to
preserve implementation/tuning separation. T095 stays OPEN; SC-002 UNMET.

[Original request](prompts/development/003-t095-v3-implementation-20261117.md).
[Actual execution/results/limits](evidence/tasks/feature-003-t095-v3-implementation-20261117.md).
[Concrete review packet and instructions](evals/investigation/retrieval-fresh-v3/README.md).
Final backend966 PASS78.31s; focused27 PASS; Ruff/packet checks PASS.
Real unreviewed development command
refused with expected exit2 before output/search. No .env/provider/live call or
legacy held-out text opened. Frontend/build/browser not rerun because unchanged;
no new manual acceptance claimed. Integrity results in execution evidence.
Integrity PASS:506 original files byte-identical;100 task markers unchanged;
76 local links valid; only five progress/design edits and11 scoped additions.

**One concrete next step:** Milan reviews the18 development rows and proposed
source sets/rationales in the linked packet and reports actual row-level findings
or scoped approval. Then arrange separate held-out authoring/reference review,
development selection/freeze and explicit authorization of concrete acceptance.

# Previous handoff — T095 design partial; independent review next, 2026-11-17

Scoped speckit-implement only T095 on feature03, verified expected starting
HEAD249a50baae8fa4d3b2b560777da6dae8efd2acd7; initial status/diffs clean.
Prepared [separate v3 development design/fresh-evaluation review packet](specs/003-ai-investigation/retrieval-development-v3.md),
using existing opt-in v2 mechanics and proposed fresh development-only cutoff
selection. No new runtime implementation/configuration or threshold change.

[Original request](prompts/development/003-t095-20261117.md).
[Actual execution, diagnostic rows and limitations](evidence/tasks/feature-003-t095-20261117.md).
Actual135 relevant regressions PASS12.65s;4/4 mechanical controls PASS across18
local authored searches; Ruff PASS after one unused import correction. Full
backend/frontend/browser/live acceptance NOT RUN for this design-only unit.
No private .env read, provider calls or interaction with existing services/stores;
no held-out question/reference content opened. Existing runtime/configs/glossary/
packs/manual evidence preserved. Integrity PASS:503 tracked files byte-identical,
100 task markers unchanged,49 local links resolve; diff/whitespace PASS.

T095 remains UNCHECKED: independent teammate plan/novelty/reference review pending;
fresh pack/runner/development selection/freeze and explicit acceptance execution
authorization/evidence absent. Old frozen baseline/improved Recall/MRR0.50/0.50,
16 answerable plus4 no-answer denominator and4/4 no-match retained. SC-002 UNMET;
T094,T096–T098 and original failed quality/timing/full-assembly gates unchanged.
T099/T100 completion retained. Local commit authorized; push/merge not requested.
Earlier publication blocker is historical, not the next action for this task.

**One concrete next step:** an independent teammate reviews the exact v3 packet
and records actual identity/date, prior holdout exposure and approve/change/reject.
Do not run the old freeze builder or any fresh acceptance experiment from this
handoff; obtain a concrete new freeze and separate explicit run authorization.

# Previous handoff — T099/T100 complete; T094–T098 open, 2026-11-17

Only T099/T100 implemented with scoped speckit-implement on feature03, clean
initial95b5eebe5e3a50583ffcf33b081d2c7e53755681. T099 separates historical-attempt
labels/read-only display from real source-context changes. Cancelled same-context
parents no longer claim an old source or existing report; citations/access/stale
reply guards retained. Intended RED2 failures/14 passes; GREEN/refactor16 passes.
T100 adds current context-v2/reviewed-producer API documentation while preserving
old context1/schema/example/report meanings and public HTTP envelope1.

Actual final checks:backend939 PASS60.71s; frontend193 PASS; typecheck/build/Ruff/
whitespace PASS; four schema meta-checks/both LF pins/exact producer method delta/
eight examples/derived context2 rules boundary/16 local links PASS. Initial backend
temp-parent and probe-import errors corrected in commands, separately preserved.
[Full execution evidence](evidence/tasks/feature-003-t099-t100-20261117.md).
[Original prompt](prompts/development/003-t099-t100-20261117.md).

Only these two tasks closed. No T062–T067 repetition, T094–T098 work, live API or
evaluation; old results/thresholds and existing manual evidence/services preserved.
No new human/browser acceptance claimed. Full IBM/model/app assembly unrun;
quality/retrieval/timing and independent T094 gates remain. Local implementation
commit:c255fa8e8a93d95d5c6c7f97890e90c5ace6059c (eight reviewed files).
Normal push failed at sandbox Windows credential access; escalated push was
rejected by automatic approval review before execution. Reviewer requires explicit
approval of this payload/destination despite the branch-scoped push request.
Destination:https://github.com/vekiii/capstone-FraudLensAI, origin/feature03.
No bypass attempted; publication pending. This docs-only follow-up records the
blocker. No automatic future publication or merge.

**One concrete next step:** obtain explicit user approval to push the eight
reviewed T099/T100 files and blocker follow-up to that exact repository's feature03
branch, then retry a normal push and verify remote SHA/clean status. Independent
human T094 rubric/control decision remains the next feature gate before T096.

# Previous handoff — T066/T067 complete; six convergence tasks open, 2026-11-17

Milan/milangavric2003 completed guided manual reproduction and reviewed the
supplied code/contracts/evidence files, reporting no objections and explicitly
authorizing T066 closure plus commit/push to feature03. Contributor self-review,
not independent reproduction/quality evaluation. Baseline2469aec; original user,
Vedran and AI results remain separately attributed in the detailed records.

[Human decisions / complete chat work record](evidence/tasks/feature-003-reproduction.md).
[AI commands, regression, issues and limits](evidence/tasks/feature-003-t066-review-20261117.md).
[Actual T067 Converge inventory/findings](evidence/tasks/feature-003-convergence.md).
T066 and T067 checked as executed; NOT full feature acceptance. Converge outcome
tasks_appended, Phase16 T095–T100. T062–T064 remain complete in controlled scope.

Open: T094 independent rubric/control decision; T095 retrieval target; T096
report quality after T094; T097 required live timing validation; T098 actual full
producer/population/model assembly; T099 same-context parent label; T100 current
API context-v2/pin addendum. Old0/8 quality,0.50/0.50 retrieval, failed latency,
v8 calibration2/3 FAILED/unavailable quality and unrun full integration preserved.
No new live calls/evaluation/regrading, runtime implementation or ML merge.

Checks inherited from this unchanged runtime session:939 backend/186 frontend,
typecheck/build/Ruff PASS;29 actual browser/API/proxy+6 process checks PASS across
separate components; failures preserved. Only executable edit is the tested
recovery harness constructor forwarding fix. User now authorizes normal commit/
push of reviewed files (message style matching branch); no merge or force-push.
Final publication result is verified separately; no automatic future publication.

Publication verified: dab0fb424041aa1d4a4bbd6a89044ea8a418a981,
`T066-T067 finished; remaining Feature 003 work documented`, normal push to
origin/feature03 exit0. git ls-remote exact SHA matches HEAD; status clean after
push.25 reviewed files only, no generated stores/raw archives/environment file.
Initial sandbox index permission failure resolved with authorized escalation;
no approval-review rejection. This publication note is a docs-only follow-up.

Manual test app remains API8000/Vite5174, existing5173 preserved, no worker poll.
Owned process ledger/helper/logs and synthetic store are ignored under
.cache/t066-milan-20261117; API restarted with ledger PID27068. Do not delete the
manual review records or kill unrelated services. No actual .env/secret read.

**One concrete next step:** use speckit-implement for T099 (offline same-context
history-label RED/GREEN correction), then T100 API documentation; independent
human T094 review can proceed separately. Do not launch T095–098 experiments or
full integration without their reviewed access/protocol and explicit run scope.

# Previous handoff — T066 manual continuation / T094 decision, 2026-11-17

Branch feature03, reviewed baseline2469aec0b146c5c26cb5c0eea70cb96bb9c559e3,
initially clean. Current user identifies as Milan / milangavric2003; Git history
shows investigation/recovery/review implementation involvement, so contributor
self-review, not independence. Milan supplied current TEST report/procedural
evidence and saved the initial diagnostic decision; no T066 sign-off yet. Preserve earlier unspecified
user observations and Vedran/Veki authorship separately.

[Actual AI checks, findings and commands](evidence/tasks/feature-003-t066-review-20261117.md):
backend939 PASS57.83s, frontend186/typecheck/build/Ruff PASS; 29 browser/API/proxy
and6 process checks PASS across separate components. Failed sandbox/port/helper
attempts retained. Fixed only recovery verification helper's old constructor
signature; application runtime/contracts/prompts/locks unchanged. Controlled
producer smoke PASS in a distinct new output, no source DB writes/labels/provider.
T062–T064 implementation remains complete in documented scope; no full IBM/model
validation, new evaluation, live API, commit/push/merge.

Old user review-chain IDs absent from this local store; previous D: store is
unavailable. Mismatch unresolved; fresh manual chain is allowed by checklist,
not reconstruction of missing events. AI prepared manual fixture/test app on
http://127.0.0.1:5174 with API8000, absent ENV_FILE, empty key/model, analyst
milangavric2003 and separate .cache/t066-milan-20261117/manual.sqlite. Existing
5173 preserved. Owned hidden service PIDs/logs/run.py are in that cache directory;
AI setup is not a human check. Matching worker helper is `run.py worker`. AI
subsequently observed newly created att_4c34755d3e0a4b8694ae02489bfa4b3e and
ran that test worker: ready_for_review/revision4, four scripted turns/three tools,
zero live calls and no human review. Exact report/citation IDs in evidence.
Milan subsequently supplied ready_for_review/TEST/report/limitations and opened
the simulated Missingness procedure with exact version/corpus metadata. AI GET
confirmed cited procedure binding and revision4/review=null before the decision.
Milan now reports request_more_information review rev_40f8c34cf0464ced9ef449bb941e42db,
actor milangavric2003, UTC2026-11-17T00:50:57.922620Z, rationale
"T066 — test čuvanja odluke; nedostaju dodatni podaci." AI GET confirms reviewed/
revision5, supersedes=null, same report/draft/citations/budget. Milan now supplies
first-tab reload preserving that decision and second-tab revision4 error exactly
"revision_conflict. Osvežite sačuvano stanje pre nove radnje." AI GET confirms
original review/revision5/draft/budget unchanged. Milan now supplies linked close
correction rev_b30f69e52fc74628b112ebe27d7a2e0f at UTC2026-11-17T00:59:09.046218Z,
superseding rev_40f8c34cf0464ced9ef449bb941e42db. AI GET confirms revision6;
read-only SQLite confirms both reviews, initial review unchanged, original draft/
citations/budget retained. Fresh chain/conflict/reopen checks observed; old absent
chain remains unresolved. Milan supplies CASE-002 before/after queue/cancel
screenshots: created/waiting→cancelled,0 requests/tools. AI GET matches timestamp/
context to att_01d1d0cf537d4b18a8714f7f81cd0c5c, cancelled/revision2, no report/
review. Milan next supplies queued-child/cancelled-history screenshot. API/audit
confirm child att_69a521e11cf74702a40969eff93dea4f → immediate cancelled parent
att_b68477162299435589cf83417014b6b2 in same run/context. That parent is a separate
base created01:02:38Z, not original cancelled att_01d1d0...; original retained.
Exact IDs/limits in evidence. AI verifies only linked child queued, runs matching
test worker once →ready_for_review. Human child-reopen/recovery/navigation and
actual code/contracts/evidence sign-off remain pending. Source metadata
"reviewed by Milan" is prior corpus review, not current case/T066 approval.

[Current human checklist and attribution](evidence/tasks/feature-003-reproduction.md).
T061 audit is executed with FAILED quality; historical "full T061 pending" is
not a new execution dependency. T066 remains open pending real manual findings
and explicit code/contracts/evidence decision. T067/converge NOT RUN, as requested
until T066 conditions are met. Tasks completed do not imply acceptance criteria.

T094: raw ignored v8 archive now available, all10 original artifact hashes and
raw payload seal verified read-only. CAL8-B unsupported/critical=true but
missingness=true confirmed directly; frozen expectation false, calibration2/3
FAILED and quality unavailable preserved. [Human decision packet](specs/003-ai-investigation/calibration-clarification-proposal.md)
asks approve/change/reject three-predicate rubric plus six controls for a new
version only; independent reviewer/decision pending, no rerun budget inferred.
Old0/8 quality, retrieval0.50/0.50 and timing failures remain. No gate waiver.

History-label finding confirmed by requested minimal CASE-003 replay: one base
att_363daf9e442841ff8221068119c346d3 → child att_550de71019924ae4a76fe2b5d5c91816,
same run/case/context/snapshot/corpus/retrieval; Milan's parent-view screenshot
still says "prethodni kontekst izvora". Extra CASE-002 cancellation is not needed
to reproduce it. Binding correct; wording defect tracked for T067/FR-021/FR-002,
no task append/runtime fix yet. AI then verifies only CASE-003 child queued and
runs matching test worker once →ready_for_review, no live call/evaluation.

Milan now supplies guided CASE-003 reopen screenshot: ready_for_review and exact
parent att_363daf... confirmed. This covers saved-child reopen; no extra CASE-002
reopen observation invented. AI has deliberately stopped manual API8000 for
recovery test: exact helper command matched PIDs20672/26052, initial Stop-Process
failed (health remained200), then verified .NET Kill succeeded (curl exit7).
Frontend5174 remains200, Vite26472 and existing5173 preserved. Store untouched.

Milan supplies expected outage screenshot: invalid_response/refresh guidance,
saved ready item retained, creation disabled. AI restarts same helper/store/config
hidden PID27068 (ledger updated); direct/proxy health200 and saved child/parent/
CASE-001 correction states/counters retained. API is now UP. No worker/live call.
Fresh AI direct/proxy CASE-999404/CASE-1422 checks also pass; distinct from human.

Milan explicitly confirms restored same-panel ready_for_review/report and4/8
requests,3/12 tools in text; no screenshot required/claimed. Manual recovery unit
complete, preserving separate AI API/404/422 results and human observations.

Milan confirms rapid switching; screenshot ends correct CASE-003/TX-003,
18420.50 EUR/score0.1, no mixed case data reported. Panel collapsed in screenshot;
do not claim unseen report inspection. Guided manual UI units now recorded.
Remaining human checkout/diff/environment inspection and code/contracts/evidence
review have a four-group packet at end of reproduction.md; no sign-off inferred.

Milan replies "pregledao sam, deluje u redu" to linked review.py submit/store.py
append_review review step: actual group1 code inspected, no objection reported.
No broader approval or separate API-contract/environment/diff review inferred.

Milan confirms group2 dataset.py/accepted-boundary review "okej je, dalje", no
objections, and requests more files per step. Batch remaining review; do not
keep splitting it into tiny file groups. T066 final decision still unreported.

**One concrete next step:** Milan reviews combined UI controller/views, API
contract, recovery helper diff, working status/diff, reproduction/technical
evidence and T061/v8 quality limits. Packet at reproduction.md end. Report actual
reviewed scope/environment, explicit scoped T066 decision/findings/unreviewed
parts; optional T094 feedback separately, not inferred independent approval.
Once T066 conditions met run feature003 Converge; preserve open T094 and failed
quality/full-integration criteria. No new live/evaluation/commit/push/merge.

# Previous handoff - Milan owns remaining T066 review, 2026-11-16

User explicitly handed remaining T066 review to Milan. T066 and T067 stay open;
Milan execution/approval is not yet reported. User already observed successful
source search/passage opening, no-match, test worker/UI ready_for_review, evidence
opening, required decision/rationale validation and persisted close decision.
Saved alias is literally TVOJE_IME. Correction saved, but its predecessor ID differs
from the prior supplied review; intermediate event/attempt selection unconfirmed.

[Exact IDs, observations and Milan checklist](evidence/tasks/feature-003-reproduction.md)
are in the final Current T066 handoff section. Preserve attribution: user results
are self-review, not Milan's execution or independent reproduction. Remaining:
review-chain mismatch, two-window conflict, cancel/retry/recovery, API404/422,
navigation, regression and code/contracts/evidence review. Full IBM/model checks
and quality/T061/T094 gates remain unresolved; no automatic live run/merge/push.

**Next step:** Milan records actual reviewed branch/HEAD/diff/environment, then
executes remaining checklist with test provider and matching API/worker store.
Frontend5174 was proposed because5173 occupied; confirm ports on his machine.

# Previous handoff - user T066 review started, 2026-11-16

Team explicitly approved user-led contributor self-review for T066, replacing
second-teammate execution only; no independent-review claim or quality gate waiver.
User reports feature03 HEAD987b64c, Python3.14.3/Node24.20.0/npm11.19.0 and successful
knowledge publication with recorded corpus/retrieval IDs. Vite startup failed:
5173 occupied. UI/worker/API/regression/human findings remain pending; T066 unchecked.
Details: evidence/tasks/feature-003-reproduction.md (superseding amendment at end).
Next concrete step: launch owned frontend on5174 and continue manual case/search
checks using that port, with backend8000 and explicit test-provider settings.

# Previous handoff - T062-T064 consumer adapter complete, 2026-11-16

Branch feature03, baseline1f3a09d. User explicitly confirmed producer/investigation
agreement on behalf of the team and assigned feature003 history implementation to
this contributor. Actual reviewed producer487c427ea50e169f5e36898420d659f05ead2c60;
no merge of ML branch. Agreement and execution:
[accepted boundary](specs/003-ai-investigation/dataset-adapter-agreement-v2.md),
[review](evidence/tasks/feature-003-context-review.md),
[RED/GREEN/evidence](evidence/tasks/feature-003-context.md).

T062/T063/T064 checked. Read-only adapter now resolves completed active published
rules/model contexts and bounded seven-day bank+account history. Direction/currency
exact totals, eligible counts, truncation, missing-vs-empty, strict time/focal
filtering, source switch and label exclusion tested. New context2/new producer pin
explicitly support reviewed boosted method; historical context1/pin unchanged.
API/worker use INVESTIGATION_DATASET_RUN_STORE, INVESTIGATION_DATASET_STORE and
INVESTIGATION_DATASET_SCORE_SOURCE with INVESTIGATION_SOURCE=dataset; see quickstart.

Actual checks: backend936 PASS135.61s; final35 boundary tests PASS (includes three
further cases and dataset HTTP/archive checks after full collection), Ruff and
whitespace PASS. Actual pinned producer DatasetStore/RunStore smoke PASS for both
rules/model-shaped publications, source bytes unchanged, zero provider/label reads.
Smoke uses authored records/assessments, not actual IBM population or trained ML
inference. Full producer import/run stores absent: full dataset/model validation
still unrun, no SC-007/full acceptance claim. Frontend source untouched; prior186/
build/browser results historical. Existing offline-review work preserved.

Final HTTP RED found absent dataset case503 instead of404; adapter now raises
existing CaseNotFoundError. Final dataset+existing investigation API regression:
44 PASS5.06s, Ruff/final diff check PASS. Full936 collection predates this small
exception correction; no claim of another full run.

T066 teammate reproduction/human code review, T094 independent quality/rubric
clarification and T067 full Converge remain open. Old failed quality/retrieval/
latency outcomes and historical protocols/results unchanged. Colleague document's
unavailable9454bfc reviewed SHA correction is explicitly deferred by user until
feature003 is finished; adapter is pinned to available487c427 instead.

**One concrete next step:** a real teammate follows T066 in
[evidence/tasks/feature-003-reproduction.md](evidence/tasks/feature-003-reproduction.md),
records their actual identity/commands/observations and reviews the new adapter
boundary. When producer stores become available, additionally run the documented
API/worker dataset check with actual selected run; controlled smoke is not that
validation. No automatic live batch, regrading, commit, push or ML merge.

# Previous handoff - offline reproduction/review complete; human gates pending, 2026-11-16

Branch feature03, baseline 1f3a09d. User requested available fixture reproduction,
code/contracts review and evaluation clarification while waiting for producer
agreement. Fresh agent checks: backend 921 PASS, frontend 186 PASS, Ruff,
typecheck/build/whitespace PASS; actual isolated browser/API/proxy 29 PASS and
process 6 PASS, zero provider calls. No actual .env reads or package installs.

Found and corrected one unit-test reproducibility issue: preparation test needed
an ignored old live audit.json. It now uses its own independently hashed fixture
and changed/missing negative cases, retaining real hash enforcement. Runtime,
contracts, prompts, lockfiles and historical results unchanged. Sandbox Chrome
failed; an escalated attempt found existing port 5173 occupied. Preserved that
service and ran generated harness on 5174; owned cleanup PASS. Failed attempts
and successful isolated outputs have distinct evidence filenames.

[Actual commands/results/technical findings](evidence/tasks/feature-003-offline-review-20261116.md).
[T094 clarification proposal](specs/003-ai-investigation/calibration-clarification-proposal.md)
separates complete disclosures, no invented missing values and no contradictions.
Frozen CAL8-B/v8 labels/ratings stay unchanged, failed calibration and unknown
quality preserved. Ignored raw v8 judge archive absent locally; detailed claim
detection is documented prior evidence, not reverified raw judge rationale.

T066 remains unchecked: agent execution is not another teammate's reproduction
or human code/contracts approval. T094 partial/open pending real human review
of proposed semantics/controls. T062 producer agreement/T064 actual adapter remain
pending. No live rerun, historical regrading, commit/push or full acceptance.

**One concrete next step:** a real teammate follows the T066 procedure in
evidence/tasks/feature-003-reproduction.md and records actual identity/observations/
review decision; T094's separate clarification packet can be reviewed in parallel.
Do not dispatch new API batches from this handoff. Earlier handoffs are historical.

# Previous handoff - reliability fixes merged into feature03, 2026-11-16

ACTIVE BRANCH feature03. User explicitly authorized merge and push after joint
review. Clean worktree/remote refs rechecked; git merge --ff-only moved feature03
from cd98ea021a38b362b5766c4e23a1e55ec0ad0dcd to reliability tip
920296436643e2c25ca27fc19441ecedf7e078c6, no conflicts. Resulting tree exactly
matches tested reliability tree. This handoff/evidence update is a docs-only
follow-up commit; publishing origin/feature03 requested. Verify Git remote for
final publication identity. Reliability branch retained; no force push/deletion.

Next concrete feature03 step: T062 reconcile the current feature002 producer/
history contract with our pinned context contract and obtain actual producing/
affected-consuming review before adapter work. Do not infer approval from merge.
T063 actual adapter RED beyond authored guards remains partial,T064 real adapter
unstarted,T066 teammate reproduction/human review,T067 full Converge pending.
T094 rubric/control disagreement review also pending; no automatic new API batch.

Merged runtime: bounded timeout retry/quota handling, fixed safe repair guidance,
shared schema within48k, opt-in script normalization, mandatory exact human final
notice on new attempts (promptv4/private policy). One repair then controlled fail;
original raw responses, immutable reports and old binding/retry semantics retained.
No frontend/public schema/dependency/.env changes. Local ignored guide199 lines.

Verification inherited from IDENTICAL merged tree: backend919 PASS69.01s,
frontend186/typecheck/build PASS,Ruff/diff PASS; no repeated full suite needed for
fast-forward with no code reconciliation. Post-merge offline integrity audit
rechecked. Evidence/tasks/feature-003-merge-readiness.md records actual merge and
remaining limits. No new provider calls or historical result edits during merge.

Final live check:18HTTP200 gpt-6-luna;3 valid reports in46.789/26.687/38.841s.
Ordinary assertion-scope repair and controlled notice-omission recovery succeeded
at38,925/35,580bytes. Known101,617 tokens,unknown0,spend unknown. Caps unchanged.
QUALITY STILL UNCONFIRMED: calibration2/3 FAILED on missingness interpretation;
fabricated-funds critical allegation WAS detected. Raw favorable ratings not
accepted:quality_assessment_valid=false,passing_development_reports=null. No
regrading, changed control labels or judge rerun. Full feature not accepted.

Final evidence/tasks/feature-003-final-live-v8.md and final-live-v8-results.json.
44 prior artifacts preserved,10 new hashes,13 cited IDs resolve; actual runtime/
prompt/policy/config bindings audited. Ignored raw development-v8 results remain.
Never replay completed builders/batches or reuse unused7 transports. All original
0/8 quality,retrieval0.50/0.50 and failed latency/outlier results remain FAILED.
Fresh independent quality/reference review still required for acceptance.
