# Current handoff - T062-T064 consumer adapter complete, 2026-11-16

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
