# T067 actual convergence assessment — 2026-11-17

Outcome: **tasks_appended**, six tasks T095–T100 in Phase16. T067 is executed;
Feature003 is **not converged or fully accepted**. T094 remains open.

User confirmed the combined file review and authorized closing T066, recording
this conversation and commit/push to feature03. Actual contributor reviewer is
Milan/milangavric2003, with implementation involvement disclosed. His scoped
review is not independent quality evaluation. Prior unspecified user/Vedran
records and all AI observations remain attributed in
[reproduction](feature-003-reproduction.md) and
[technical execution](feature-003-t066-review-20261117.md).

## Actual workflow and constraints

Applied `.agents/skills/speckit-converge/SKILL.md` after implemented tasks and T066
review. Set SPECIFY_FEATURE_DIRECTORY=specs/003-ai-investigation explicitly.
Initial direct PowerShell prerequisite invocation was blocked by execution policy
before the script ran. Used documented child-process fallback, with no machine
policy change:

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
powershell -NoProfile -ExecutionPolicy Bypass -File .specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireSpec -RequireTasks -IncludeTasks
```

Exit0 JSON selected the actual feature003 directory and research.md,
data-model.md, contracts/, quickstart.md, tasks.md. No extension file exists;
before/after hooks absent. No delegation, provider call, evaluation replay,
application change, spec/plan rewrite or producer merge during Converge.
Git publication checks are a separate user-authorized operation, not the
Converge intent source or assessment method.

Read current spec/plan/tasks and constitution as intent; supporting contracts,
source and evidence explain observed behavior. Assessed 28 FR,8 SC,19 story AC
(3+5+4+4+3),12 plan decision groups,10 constitution principles and all94 existing
task descriptions regardless of markers. Corrective T068–T093 chains assessed
by their resulting behavior, not obsolete prompts/limits. T066 closure recorded
before tasks snapshot. No new acceptance experiment was run.

The assessment inspected source boundaries and current component/test evidence;
it is not exhaustive formal verification or new proof of arbitrary prose truth.
Source AST inventory initially failed on an existing UTF-8 BOM in retrieval.py;
reran read-only with utf-8-sig. No source content changed. One draft human quote
written through a Windows shell pipe was mangled; corrected with apply_patch
before publication, preserving the actual supplied Cyrillic quote.

## Intent/code coverage inventory

| Intent | Observed source and actual evidence | Assessment |
|---|---|---|
| FR-001–004; T005–008/T062–064 | models/context/dataset.py, version2 schema/pin and accepted producer boundary;939 suite and distinct actual-producer authored smoke | Controlled adapter implemented; full integration partial F4. |
| FR-005–008; US1 AC1–3; T013–022/T052–056/T071 | knowledge/retrieval/API/UI, six reviewed sources, archived passages, full fixture browser/source checks, frozen retrieval results | Mechanics implemented; retrieval target unmet F1. |
| FR-009–012; T023–024/T057 | three closed tools, server-bound scope, history readers/outbound projection; negative/safety tests and source/privacy inspection | Bounded workflow checks pass; not universal injection/prose proof. |
| FR-013–017; US2 AC1–5; T025–033 | validation/provider/workflow, human-authority policy and prompt pinning; deterministic reference tests, old actual generation/judging, v8 raw integrity | Structural mechanics implemented; semantic quality partial F2/F7. |
| FR-018–020; US3 AC1–4; T009–010/T029–030/T039–044 | dispatch reservations, finite limits/CAS/state persistence, one repair/retry, actual killed workers and live user restart/linked retry | Current deterministic recovery passes; original live timing target remains F3. |
| FR-021; T034–038/T041–044/T049–050/T065 | strict clients/decoders, abort/generation tokens, case/context guards;186 frontend,29 browser+6 process checks; human navigation/recovery | Implemented fixture UI; same-context history wording F5. |
| FR-022–024; US4 AC1–4; T045–051 | review.py/store.append_review/immutable tables, server actor/idempotency/revision/report/predecessor guards, private projection | Human initial review→conflict→correction and read-only two-row audit prove scoped chain; no automatic disposition. |
| FR-025–028; US5 AC1–3; T052–061 | offline evaluation/judging/calibration modules, private frozen packs, post-hoc amendment, all failed outcomes preserved | Evaluation/aggregation/audit executed, quality acceptance unmet; T094 independent clarification pending. |
| T001–004/T011–012 | settings/environment/composition, lockfiles, disabled fixture behavior and safe tests | Existing setup/toggle/privacy boundaries implemented; no new installs or credentials read. |
| T066–067 | executable docs, human contributor review, attributed evidence; this actual workflow | T066 complete; T067 executed with remaining tasks. |
| T068–075 | bounded repair/cleanup, opt-in normalization and separate development-v2 protocol/records | Superseded details judged against resulting source; failed cases still retained. |
| T076–084 | timeout/quota diagnostics, calibration gating, shared strict schema and payload limits | Implemented/mock regression evidence; no old live replay or quality inference. |
| T085–093 | controlled repair, versioned human-authority policy, preserved raw responses/pins/budgets, final-v8 archive | Mechanisms implemented; failed calibration prevents quality acceptance. |
| T094 | independent rubric/control decision packet, raw archive hash/seal inspection | Partial F7, existing task retained. |

Plan decisions checked: stack/dependency boundaries; separate schema-v1 store;
short transactions/idempotency; corpus normalization/chunking/archive; frozen
BM25/glossary policy; context/producer versioning; scoped outbound tools; strict
provider continuation and size limits; request/deadline/retry/repair budgets;
worker/restart/cancellation; explicit analyst review/UI guards; evaluation and
staged integration. Decisions are implemented in their controlled scope; gaps
map below. Constitution I–X checked against scope/spec/TDD/math/claims/human
authority/reference separation/contracts/evidence/human review. No new confirmed
CRITICAL violation found; partial quality is not being represented as acceptance.

## Findings and remaining work

| ID | Type | Severity | Source | Observed evidence | Task |
|---|---|---|---|---|---|
| F1 | partial | HIGH | SC-002,FR-008/025–028 | Both frozen held-out Recall/MRR0.50; targets0.80/0.70. retrieval.py implements current policy; later opt-in variant is not fresh acceptance. | T095: separately versioned development improvement/validation plan; no exposed-holdout tuning. |
| F2 | partial | HIGH | SC-003,FR-013–017/027 | Original automated quality0/8; v8 calibration2/3 failed, quality_assessment_valid=false, passing_development_reports=null; valid IDs/schema do not establish faithful narratives. | T096 after T094: approved protocol/controls, meaningful corrections and separately authorized fresh evidence. |
| F3 | partial | HIGH | SC-006,FR-018–020/028 | Original five-case live timing/outlier failures retained, including7496.290s historical outlier. Current bounded worker tests and2 ordinary v8 cases are not five-case acceptance or proof the same defect persists. Search p95 target passed historically. | T097: reconcile remaining causes offline, prepare reviewed five-case protocol; no automatic rerun. |
| F4 | partial | HIGH | SC-007,FR-001–004/011 | dataset.py and authored producer smoke pass; no full IBM stores/trained inference/app assembly exercised. main.py and foundation browser remain fixture contracts. | T098: coordinate real stores/assembly and actual API/worker history integration; no duplication of completed T062–064 or unapproved merge. |
| F5 | partial | MEDIUM | FR-002/021,US3/AC1 | controller.show conflates non-latest parent and changed context; views.run says previous source context for same-context cancelled parent. Human controlled CASE-003 replay and exact API identities confirm. | T099: separate history/context labeling with meaningful RED/GREEN, preserving access guards and actual stale-source warnings. |
| F6 | partial | LOW | FR-001–003/028,plan versioned boundary | contracts/api.md still describes only historical producer2dd815d pin and pending approval, while code/context-v2 uses explicitly reviewed487c427 version. | T100: add current versioned addendum preserving old contract meanings. |
| F7 | partial | HIGH | T094,FR-025–028 | Proposed predicates/six controls exist; archived judge inconsistency verified. Final file review is contributor feedback, not separate independent rubric adoption. | Existing T094 retained, no duplicate task or fabricated decision. |

Counts:7 partial;0 missing/contradicts/unrequested findings;5 HIGH,1 MEDIUM,1 LOW;
0 new confirmed CRITICAL. Six new actionable task descriptions appended in
severity order, T095–T100; F7 uses existing T094. Before append, findings/counts
were shown in-session. A byte-prefix comparison against the post-T066 tasks
snapshot proves the append preserved every existing task byte. After Converge
finished, the surrounding task-status bookkeeping marks T067 executed, separately
from that append-only operation. No open quality/integration task checked complete.

## Acceptance versus execution

| Criterion | Actual current result |
|---|---|
| SC-001 | Six-source review/archive/citation mechanics verified in controlled scope; history-label finding retained, no universal narrative claim. |
| SC-002 | FAILED0.50/0.50; T095 open. |
| SC-003 | FAILED original0/8; later v8 quality unavailable; T094/T096 open. |
| SC-004 | Available deterministic safety/negative checks PASS; scoped evidence, not guarantee for arbitrary prompts. |
| SC-005 | Deterministic recovery/audit checks PASS; human contributor chain/reopen/cancel/retry/outage recovery observed. |
| SC-006 | Historical local search p95 PASS; original required live timing FAILED/unresolved; T097 open. |
| SC-007 | Fixture/contract/controlled-producer smoke PASS; full population/model/app integration UNRUN, T098 open. |
| SC-008 | Frozen outcomes, post-hoc method, usage/unknowns, reproduction and identities recorded; full release acceptance not inferred. |

Next recommended implementation is the bounded offline T099 UI-label fix, then
T100 current API documentation. Independent T094 rubric/control review can occur
in parallel as human work. T095–098 require reviewed design/access/authorization
before new experiments/integration; no live budget is granted by these tasks.
Use speckit-implement for approved tasks, then rerun Converge after remaining
work, preserving all old metrics and incomplete criteria.
