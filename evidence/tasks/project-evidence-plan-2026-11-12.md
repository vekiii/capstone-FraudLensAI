# FraudLens AI project evidence and contribution plan

Prepared 12 November 2026. Covered history: 11–12 November 2026, through
`f63bffe490358a4fba06d27b896d42c5e81bf882` on `initialization`.
All times below use Europe/Budapest, UTC+01:00 on these dates. Belgrade timestamps
in the source records have the same offset for this period.

**Three identifiable contributors have recorded project work across 19 commits.**
At this pinned baseline, Feature 001 delivered an accepted local synthetic case
demonstration and Feature 002 had a specification only. A transparent
publication-window calculation gives an
illustrative **about 11 person-hours**, with low/high assumption scenarios of
**about 7–14 person-hours** across the three contributors. These are provisional
effort estimates, not recorded working hours. The first-to-last commit span is
**29 hours 19 minutes 27 seconds**, including the overnight gap.

This report combines the completed-work ledger, individual attribution, validation
evidence, time calculation and a plan for recording subsequent work. It preserves
the distinction between implemented behavior, automated checks, participant
testimony and future requirements.

## Sources and attribution

The baseline includes all 19 distinct commits reachable from the locally available
branches and remote-tracking refs at this audit. No remote fetch was performed.
Saved development instructions and task records provide the available continuity
with earlier sessions; unsaved chats, private activity and external timesheets are
outside this record. A prompt establishes requested scope; execution evidence and
the corresponding committed changes establish what was delivered.

The [calculation snapshot](project-evidence-calculations-2026-11-12.json) contains
the full commit ledger, exact time inputs, scenario results and SHA-256 inventory
of the baseline evidence, prompts, specifications and decision records. The
[calculation script](project-evidence-calculations.py) reproduces it without
dependencies or network access. The [current request and clarification](../../prompts/development/project-evidence-plan-2026-11-12.md)
are preserved separately.

| Contributor used in this report | Recorded Git author | Attribution basis |
|---|---|---|
| Vedran Mitic, linked to the Veki account | Veki | Git identifies Veki; the named [peer execution report](peer-reproduction.md) and [human-review confirmation](human-review.md) identify Vedran. Linking the account to that participant is an attribution inference, not a full-name field in Git. |
| Isidora Popovic | Isidora Popovic | Git, explicit attribution instructions in [T012](T012.md), the [publication manifest](session-commits-2026-11-12.md), and the [browser continuation request](../../prompts/development/001-foundation-T019-browser-continuation.md) identify her work. |
| milangavric2003 | milangavric2003 | Git attributes the phase 5 changes to this account. A confirmed full name is not supplied in the saved evidence. |

The [original idea](../../original_idea.md) describes a four-member team. Following
the user's clarification, this report counts **three contributors with attributable
work** and gives the unnamed fourth member **no attributed work or estimated
hours**. Historical testimony that the team jointly reviewed setup and code remains
recorded, but it cannot supply an individual contribution or duration for that member.
The A/B/C/D labels in the plans describe responsibility streams; they are not
evidence of named assignments.

Commit attribution identifies the account responsible for the recorded changes.
The saved records describe AI-assisted implementation and verification, so these
counts do not imply that every line was manually written by the named person or
that all associated time was direct human keyboard time.

## Chronological contribution ledger

Times are Git publication timestamps, not task start/end times. Author and
committer timestamps agree in this history. The subjects below are preserved
from Git; the following sections explain the actual scope.

| Date | Time | Git author | Commit | Recorded change |
|---|---|---|---|---|
| 11 Nov | 16:19:45 | Veki | `b03e8e3` | initial idea |
| 11 Nov | 16:55:15 | Veki | `f86aff0` | feature 1 implementation: constitution; specification; technical plan; API and JSON; Tasks; Quickstart |
| 11 Nov | 17:08:59 | Veki | `e62c4fe` | tasks prompt generator |
| 11 Nov | 17:31:42 | Veki | `0aa7328` | T001-T005 |
| 11 Nov | 17:53:54 | Veki | `25cbd17` | add next_work.md |
| 12 Nov | 10:52:56 | Veki | `5d60252` | T006-T007 |
| 12 Nov | 11:11:43 | Veki | `56aaa10` | T008-T011 |
| 12 Nov | 15:52:45 | Isidora Popovic | `fe187a6` | test(backend): define US2 case API and fixture scorer expectations |
| 12 Nov | 15:52:46 | Isidora Popovic | `8e99ee0` | test(frontend): define US2 fetch and case inspection behaviors |
| 12 Nov | 15:52:46 | Isidora Popovic | `ff4406e` | feat(backend): serve validated synthetic cases with deterministic scoring |
| 12 Nov | 15:52:46 | Isidora Popovic | `2ff3d84` | feat(frontend): validate case API responses and request lifecycle |
| 12 Nov | 15:52:47 | Isidora Popovic | `d7c3bb7` | feat(frontend): add synthetic case inspection UI |
| 12 Nov | 15:53:35 | Isidora Popovic | `549f304` | docs(us2): record integrated verification and current acceptance limits |
| 12 Nov | 15:54:18 | Isidora Popovic | `3c786fb` | docs: record successful US2 publication |
| 12 Nov | 16:52:13 | Veki | `f17ff8f` | did T019 |
| 12 Nov | 18:54:46 | milangavric2003 | `6a99ef6` | phase-05 |
| 12 Nov | 20:48:54 | Veki | `733bff2` | T024-T027; without T025 |
| 12 Nov | 21:14:26 | Veki | `33bcf62` | T025 and T028 finish |
| 12 Nov | 21:39:12 | Veki | `f63bffe` | feature 02 created |

Isidora's seven commits were published within **1 minute 33 seconds**. They package
work already performed across multiple saved task records; that interval does not
represent the duration of the implementation. A single phase 5 commit likewise
does not mean the contributor worked for only an instant.

## Work attributable to each contributor

### Vedran Mitic and the Veki account

On **11 November**, Veki committed the approved initial product context, constitution,
foundation specification, technical plan, contracts, task breakdown and reusable
phase instructions. The setup unit T001–T005 established contributor rules,
evidence/prompt conventions, FastAPI/Python and Vite/TypeScript tooling, generated
lockfiles, local data policy and ignore rules. The runtime selection was explicitly
amended from Python 3.12/Node 22 to **Python 3.14/Node 24**, with actual installs and
checks recorded. The root handoff was added so later contributors could continue
from repository state. See [phase 1](phase-01-handoff.md) and the initial five commits.

On **12 November**, T006–T007 added strict Pydantic contracts and 93 validation
scenarios. The record preserves an actual schema discrepancy: four trailing-newline
cases failed until the user approved nine targeted regex anchor corrections.
Final contract/regression checks passed. T008–T011 then added startup/settings,
application factory, fixture-only health endpoint, run instructions and real
backend/Vite-proxy smoke checks; the backend suite reached **101 passing tests**.
See [contract evidence](T006.md), [startup evidence](T008.md), and [health smoke](T011.md).

Veki subsequently completed the remaining **T019 browser verification**, after
Isidora's earlier implementation and live-HTTP checks. The continuation added a
headless Chrome/CDP verifier, preserved two failed verifier attempts, then recorded
**16/16 browser scenarios passing**, plus keyboard and viewport checks. It added
screenshots and evidence rather than product behavior. The final browser report
timestamp is **12 November 16:43:16.409 local time**; its JSON value is
`2026-11-12T15:43:16.409Z`. This is a report timestamp, not a session duration.
See [T019 history and continuation](T019.md) and [raw browser results](T019-browser-results.json).

For **T024–T027**, Veki reviewed requirement coverage, reconciled status documents,
ran the final **310 backend / 151 frontend** regression, lint/typecheck/build and
a bounded tracked-file audit. Convergence identified the remaining peer/human
acceptance criteria and added T028. Named participant **Vedran Mitic** then supplied
actual reproduction output, corrected the local pytest temp/cache problem on rerun,
and confirmed joint team setup/code/contracts/evidence review. That testimony closed
T025 and T028 in the repository. See [phase 6](phase-06-handoff.md),
[validation](foundation-validation.md), [peer reproduction](peer-reproduction.md),
and [human review](human-review.md).

Finally, Veki committed the **feature 002 specification**: five user stories,
26 functional requirements and nine success criteria covering data ingestion,
historical features, rules/model comparison, explanations and dataset-backed case
review. This unit produced a specification and quality checklist; it did not
download data, train a model, change product code or create a technical plan/tasks.
See [specification evidence](feature-002-specification.md) and
[feature 002](../../specs/002-data-and-risk-scoring/spec.md).

### Isidora Popovic

On **12 November**, Isidora's recorded unit covered **T012–T018 and the initial
T019 verification**. It supplied the first complete synthetic case flow across
backend and frontend, following the pre-existing foundation contracts.

| Unit | Delivered behavior | Primary evidence |
|---|---|---|
| T012 | Backend case API/scorer expectations: 43 API and 6 scorer tests, with intended missing-behavior RED | [T012](T012.md) |
| T013 | Frontend API/DOM expectations: 82 API and 19 DOM tests, with RED | [T013](T013.md) |
| T014 | Three label-free synthetic transactions/cases, strict loader and 68 fixture-validation tests | [T014](T014.md) |
| T015 | Replaceable scorer protocol, deterministic fixture scorer, input/output/identity safeguards and 65 additional tests | [T015](T015.md) |
| T016 | List/detail routes, injected case service, safe 404/422/500 envelopes and 8 additional error tests; backend reached 291 passing | [T016](T016.md) |
| T017 | Runtime frontend decoding, typed fetch boundary, timeout/cancellation and controlled errors; 14 lifecycle and 32 contract checks | [T017](T017.md) |
| T018 | Serbian Latin list/detail/back UI, persistent synthetic notice, safe text, retry and stale-response protection; 4 UI lifecycle checks; frontend reached 151 passing | [T018](T018.md) |
| Initial T019 | 291/151 regression, real API/proxy/schema checks, response capture, real proxy outage/recovery and honest browser-access limitations | [T019](T019.md), [HTTP responses](T019-responses.json) |

The unit added **190 backend scenarios** beyond the earlier 101, and **151 frontend
scenarios**. These are test-case counts, not measures of effort. T018 also records
a real keyboard-focus defect exposed by a lifecycle test and corrected before the
final green frontend run.

The [publication manifest](session-commits-2026-11-12.md) explains the seven-commit
grouping, explicit attribution to Isidora and successful publication of the six
implementation/verification commits. At that handoff, browser acceptance remained
**0/16 executed** because browser-control access had failed. The later Veki
continuation closed this shared T019 gap; credit for the initial implementation
and HTTP checks remains with Isidora.

### milangavric2003

On **12 November**, commit `6a99ef6` delivered **T020–T023**, the independent
contribution-boundary unit. It added **19 scorer-substitution/failure scenarios**
using a test-only rules scorer, and ran them plus the full backend suite:
**310 passed**, with Ruff passing. The new checks passed on their first execution
because T015/T016 already supported the required injection and validation; phase 5
did not require a production refactor or establish a new RED cycle.

The same unit documented replaceable boundaries, contract-review rules, A/B/C/D
responsibility streams and future feature dependencies. It created the foundation
development-prompt index and verified linked evidence. Production code, wire
contracts, shipped fixtures and dependencies remained unchanged. See
[T020/T021](T020.md), [phase 5](phase-05-handoff.md), and
[foundation decisions](../../docs/decisions/foundation.md).

The phase 5 request was subsequently reformatted at its author's request and is
explicitly labeled an **edited instruction record**, rather than a verbatim
transcript. Local setup before phase 5 is mentioned there but has no duration or
separate commit and is not assigned extra hours in this calculation.

## Validation and acceptance evidence

| Milestone | Recorded result | Interpretation |
|---|---|---|
| Initial scaffolding | Backend zero tests, pytest exit 5; frontend zero tests, exit 1; builds/config checks succeeded | Mechanical setup was verified; absent tests were not a passing behavior suite. |
| Contracts/startup | 93 contract tests, then 101 total backend tests passing | Strict validation and startup boundary established. |
| Case/API/UI implementation | 291 backend + 151 frontend = **442** passing | Synthetic behavior and contracts, not predictive model evaluation. |
| T019 live checks | 37 JSON responses and 4 HTML/source assets checked; actual proxy outage 502 and recovery 200 | Integration evidence separate from pytest/Vitest counts. |
| T019 browser continuation | **16 numbered scenarios + 2 extra checks = 18 report entries**, all passing | Headless real-browser automation with documented fault injection; no manual accessibility certification. |
| Phase 5 substitution | 19 added checks; backend total rises from 291 to **310** | Test-only rules adapter proves replaceability, not production AML rules quality. |
| Phase 6 final regression | **310 backend + 151 frontend = 461** passing; Ruff, typecheck and build pass | Latest recorded complete automated foundation run. Repeated runs are not added together. |
| Vedran reproduction | Initially 235 passes + 75 setup errors; rerun **310 passed, exit 0**; frontend 151 passed; CASE-999 404 supplied | Temp/cache setup problem resolved without dropping tests. |
| Human acceptance | T025/SC-001 and T028 completed through recorded joint team confirmation | Named reporter Vedran; no individual signatures, durations or separate-machine installations established. |
| Feature 002 | Specification/checklist reviewed by agent; human feature review pending | No acquired-data audit, training, comparative ML results or implementation claimed. |

Foundation has **T001–T028 marked complete and accepted in its synthetic-demo
scope**. The repository records acceptance of joint setup verification; it does
not establish four independent clean-machine reproductions. Manual browser,
screen-reader, real-phone and physically disconnected-machine checks are not
claimed. The known Starlette/httpx deprecation warning remains recorded.

Historical pending entries must be read in sequence: the final T019 continuation
supersedes its earlier browser gap, and the final team confirmation supersedes
the earlier T025/T028 pending statements. Some older handoff prose still says
only feature 001 exists; the newer feature 002 specification and Git history
establish the current state. These historical files are preserved.

## Approximate time calculation

### Recorded time facts

| Measurement | Observed value | What it establishes |
|---|---|---|
| First publication | 11 Nov 16:19:45 | First recorded commit, not project start |
| Last publication in this snapshot | 12 Nov 21:39:12 | Latest included commit |
| Calendar span | **29 h 19 min 27 sec** | Includes the overnight gap and idle time |
| 11 Nov first-to-last publication window | 16:19:45–17:53:54 = **1 h 34 min 9 sec** | Day's publication window |
| 12 Nov first-to-last publication window | 10:52:56–21:39:12 = **10 h 46 min 16 sec** | Day's publication window |
| Sum of both daily windows | **12 h 20 min 25 sec** | Calendar windows; not measured person-hours |
| Unique recorded Git authors | **3** | Identifiable contribution accounts |

Neither multiplying the calendar span by three nor reading first/last commits
per author gives actual labor. In particular, Isidora's work was batched and the
phase 5 author has only one commit. No start/stop time log is available.

### Assumptions used for the estimate

To make a reproducible provisional estimate from the available record:

1. Order commits by committer timestamp and exclude overnight gaps.
2. Assign each gap between consecutive same-day publications **once**, to the
   author of the later commit. Saved task records support the successive work
   units, but do not prove that work began immediately after the earlier commit.
3. Apply assumed activity shares of **50%, 75% and 100%** to those windows.
   These fractions allow different amounts of idle time; they are analyst-chosen
   assumptions, not measured activity or statistical confidence limits.
4. Add **30, 45 or 60 minutes**, respectively, before each day's first publication,
   assigned to that first author, Veki. The existence of pre-publication work is
   clear from the delivered artifacts; its duration is assumed.
5. Do not add extra hours for repeated evidence entries, unnamed reviewers,
   overnight time, unmeasured earlier setup, or writing this report.

For contributor *p*, let **G** be assigned same-day gap hours and **D** the number
of first daily publications. The scenarios are:

`low = 0.50 × G + 0.50 × D`

`central = 0.75 × G + 0.75 × D`

`high = 1.00 × G + 1.00 × D`

For example, the gap from 12 November **11:11:43 to 15:52:45** is assigned to
Isidora's first publication, followed by her 93-second commit batch. Her total
assigned window is **4 h 42 min 35 sec**. This is a publication proxy; she could
have worked partly outside that window or taken breaks within it. Likewise,
the **16:52:13–18:54:46** gap is assigned to the phase 5 author, not established
as their actual session start/end.

| Contributor | Commits | Assigned same-day gaps | First daily publications | Low scenario | Central scenario | High scenario |
|---|---:|---:|---:|---:|---:|---:|
| Vedran / Veki | 11 | 5 h 35 min 17 sec | 2 | 3.79 h | 5.69 h | 7.59 h |
| Isidora Popovic | 7 | 4 h 42 min 35 sec | 0 | 2.35 h | 3.53 h | 4.71 h |
| milangavric2003 | 1 | 2 h 2 min 33 sec | 0 | 1.02 h | 1.53 h | 2.04 h |
| **Total across 3 contributors** | **19** | **12 h 20 min 25 sec** | **2** | **7.17 h** | **10.76 h** | **14.34 h** |

Practical rounded wording: **approximately 11 person-hours estimated through the
publication-window model, with 7–14 hours across the chosen assumptions**.
The central allocation is roughly **5 h 41 min for Vedran/Veki, 3 h 32 min for
Isidora, and 1 h 32 min for milangavric2003**. Total estimated effort and each
person's allocation remain unconfirmed by participants.

These scenario endpoints are not lower/upper bounds on actual work. Work could
have started earlier, overlapped, included longer breaks or taken place outside
Git. AI execution time and direct human effort cannot be separated from these
records. Do not use the estimate as a timesheet, a ranking of productivity, or
an equal division of effort. Per-person timing confirmation would replace this
proxy rather than be added on top of it.

## Plan for subsequent evidence collection

This plan improves contribution and time records within the existing project
workflow. It does not start feature 002 implementation or assign future A/B/C/D
ownership to people without agreement.

| When | Responsible participant | Evidence to record | Completion condition |
|---|---|---|---|
| Before the next work unit | Person actually taking the unit | Name/alias, feature/task, current commit, intended scope, local start timestamp and timezone; preserve received prompt | Named unit and baseline are identifiable before changes |
| During implementation | Implementer | Code/contract/fixture changes, actual RED/GREEN where applicable, commands, exits, runtime/lock/data versions and relevant failure/recovery | Results distinguish behavior failures, harness issues and environment failures |
| At session end or a break | Same participant | End timestamp, breaks, direct human minutes and elapsed AI/tool minutes when distinguishable, shared participants, remaining work | Approximate duration is participant-confirmed rather than inferred from commits |
| Before publication | Commit author | Task-to-commit mapping and an explicit note when commits batch earlier work; attribution of any shared work | Commit grouping cannot be mistaken for session duration |
| During peer verification | Actual peer | Name, checkout, environment reused/new, commands/exits/results and verification time | Joint review, fresh environment and separate-machine reproduction remain distinct |
| At human review | Actual reviewers | Individual names, date, revision, findings, disposition and optional time spent | Collective testimony can be traced without inventing individual sign-off |
| After each coherent unit | Implementer | Updated task evidence and root next_work.md with actual progress, blockers and one next step | Next contributor can continue from repository state |
| Before final project submission | Team | Reconcile named contributions, participant-confirmed durations, validation results and remaining scope against Git | Actual times replace estimates; shared sessions count once per participating person |

Use the existing [task template](../templates/task.md), supplemented by:

```text
Participant / alias:
Feature and task:
Baseline / resulting commits:
Session start and end with timezone:
Break minutes:
Approximate direct human minutes:
Elapsed AI/tool minutes, if distinguishable:
Shared participants and each person's active duration:
Delivered artifacts and actual verification:
Reviewer / review result:
Unrun checks and next step:
Participant confirmed on:
```

For a shared 30-minute session attended throughout by three named people, record
**30 elapsed minutes and 1.5 person-hours**, with each person's participation
confirmed. Do not multiply the time by the planned four-person team size.

For feature 002, first review the existing specification and prepare its technical
plan. Later task evidence should identify the actual data release/hash/license,
mapping and contract migration, temporal splits, past-only history, baseline/model
versions, holdout controls and measured evaluation results when those activities
are authorized and actually executed. Foundation fixture tests cannot substitute
for those future model/data results. Human feature review remains pending.

## Audit verification and limits

The documentation audit used `git log --all`, commit path histories, branch/ref
inventory, saved evidence/prompts, foundation tasks and current feature 002
artifacts. The initial working tree was clean. No existing code, contracts,
dependencies, task acceptance markers or historical evidence were rewritten.
Application suites and browsers were not rerun for this documentation-only task;
all application results above identify historical executions.

Reproduce the contribution snapshot from the repository root:

```powershell
python evidence/tasks/project-evidence-calculations.py --output evidence/tasks/project-evidence-calculations-2026-11-12.json
```

The script defaults to the pinned baseline, so later commits do not silently enter
this historical estimate. It reports any locally available commits outside that
baseline separately. The source inventory excludes this newly written report,
its request, the script and calculation output because they are not part of the
historical work being estimated. No commit or push is performed by this audit.

Audit checks executed with system Python **3.13.3**, without installing packages:

- Calculation command above: **exit 0**; 19 commits, three authors, 69 inventoried
  source files and no locally available ref commits outside the pinned baseline.
- Dependency-free `python -` document check: **exit 0**; all 19 ledger rows match
  Git dates/authors/revisions, scenario totals match an independent calculation,
  43 local links resolve, UTF-8/fences/whitespace and helper syntax pass, and
  historical test additions reconcile to 310 backend / 151 frontend.
- `git diff --check` and untracked-file whitespace checks: **pass**. Git's
  no-index difference status was distinguished from whitespace diagnostics.
- Git reports an inaccessible user-global ignore file; repository status and
  the intended changed/new paths remain readable. No global configuration changed.

The project interpreter was not changed. Participant confirmation of actual
working durations and of the Veki-to-Vedran account mapping remains outstanding;
the estimate and that mapping are qualified accordingly above.

## Publication addendum — this documentation session, 12 November 2026

This addendum records work **after** the pinned `f63bffe` baseline. The 19-commit
ledger, 69-file inventory and 7.17–14.34 provisional person-hour scenarios above
remain a historical snapshot; they are not recalculated to imply measured time
for this session. The [publication request](../../prompts/development/002-publication-request-2026-11-12.md)
explicitly authorizes these commits and the push, superseding earlier request
records that limited the documentation work to uncommitted drafts.

Git records **Isidora Popovic** as the author of each new commit. This attributes
the published changes to her account, not exclusive manual authorship or a
measured working duration. The saved request, document evidence and actual diffs
support the work descriptions below. No additional contributor or hours are
assigned without evidence.

| Commit | Subject | Work recorded in this session |
|---|---|---|
| `6b69ae2` | `docs(evidence): document historical contributions and time estimate` | Added this consolidated historical evidence report, a pinned reproducible 19-commit calculation and JSON source inventory, the original evidence request/clarification, and a link from evidence/README.md. It separates three identifiable contributors and provisional publication-window hours from measured time. |
| `5eb0d10` | `docs(feature-002): strengthen risk-scoring specification after review` | Preserved the adversarial-review transcript and remediation request; revised Feature 002 spec, quality checklist and specification evidence for label-independent history, temporal and threshold safeguards, faithful scoring/explanations, atomic publication, and Foundation compatibility. Human and Phase 2 gates remain open. |
| `7957844` | `docs(feature-002): add technical plan and Codex work prompts` | Added the detailed architecture/implementation plan, 14 research decisions, data model, v2 API and offline scoring contracts with JSON Schema, validation quickstart, eight staged Codex prompts, original planning request, planning evidence and updated next_work.md. These are proposed design artifacts; no IBM data or Feature 002 code was executed. |
| This ledger commit | `docs(evidence): record session publication ledger` | Adds this post-baseline commit ledger, preserves the explicit publication request and updates the root handoff. Its hash is resolved by `git log` after commit creation; a commit cannot embed its own hash without changing that hash. |

After the ledger commit, the branch contains **23 commits total** (the pinned 19
plus these four), with the same **three distinct Git author accounts**. The
three newly completed commits have publication timestamps 23:50:15, 23:51:05
and 23:52:15 Europe/Budapest, respectively. Those times are Git timestamps,
not work-session start/end or labor measurements. This addendum does not add
an estimated duration for this session. No product source, lockfile, dataset
or model artifact is included in these four documentation commits. Application
tests were not rerun; the reported document/JSON/link checks are in the
[Feature 002 planning evidence](feature-002-technical-plan.md) and earlier
specification evidence. Remote push status must be verified from Git refs.


## Collective T007/T008 approval follow-up ? 13 November 2026

This follow-up records work after the historical 19-commit baseline and the 2026-11-12 publication addendum. It does not recalculate or revise that historical 7.17?14.34 person-hour estimate. The original request and approval clarification are preserved in [the development prompt](../../prompts/development/002-collective-approval-publication-2026-11-13.md).

The user stated that the team works jointly on the project and that one member's approval represents team approval, then explicitly approved T007/T008. The team decision was recorded as collective approval conveyed by the user. This closes the two review gates without assigning individual reviewer names. Import remains disabled because no import command exists.

| Participant/attribution | Date | Work | Time record |
|---|---|---|---|
| User, conveying collective team approval | 13 Nov 2026 | Approved T007 source mapping and T008 contract review under the team's collective-approval convention. | No human working duration supplied. |
| Codex-assisted repository work; configured Git author is Isidora Popovic | 13 Nov 2026 | Reconciled the handoff and review requirements; updated mapping, task status, contract status, review evidence and handoff; prepared this attribution/commit record. | Retrospective estimate: about **0.3 hours (roughly 15?25 minutes)** of active AI-assisted work, not clocked. This is not a human timesheet or person-hour attribution. |

The approval/status unit was published in **three descriptive commits** on `002-data-and-risk-scoring`:

| # | Commit | Subject | Scope |
|---|---|---|---|
| 1 | `dab61f3` | `docs(feature-002): record collective T007/T008 approval` | Recorded the team decision, closed T007/T008, and aligned mapping, contract and handoff statuses. |
| 2 | `ae98c63` | `docs(evidence): attribute collective approval and effort` | Preserved the original request and added this contribution/time addendum. |
| 3 | This ledger commit; resolve its hash with `git log -1` | `docs(evidence): finalize approval publication ledger` | Reconciles all three commit IDs/subjects in the master report and handoff. A commit cannot contain its own hash without changing that hash. |

Thus this follow-up contributes **three commits**, authored in Git under the configured Isidora Popovic identity. The recorded attribution distinguishes that configured identity from Codex-assisted drafting and the user's team decision. Git timestamps are publication times, not measures of working duration. The approximate AI-assisted effort above is retrospective and unmetered; human hours remain unknown.

No application tests were run for this documentation and evidence update. `git diff --check` passed before publication.


## Feature 002 Phase 3?4 implementation update ? 13 November 2026

This addendum records four commits published after the collective T007/T008 approval ledger. Git attributes all four commits to **Elena Kalajd?i?**. This is commit attribution; it does not claim exclusive manual authorship or prove that all work was performed without AI assistance. The task evidence, original prompts, and current `next_work.md` provide the supporting work record.

| Commit time (Europe/Budapest) | Git author | Commit | Description of work |
|---|---|---|---|
| 10:41 | Elena Kalajd?i? | `b5f7521` ? `feat(feature-002): complete and verify local dataset import` | Completed the canonical data models, streaming importer, stable D/C identities, versioned SQLite store and local import CLI; added RED/GREEN coverage for T009?T016; recorded the final mapping/team review; imported and reconciled the declared IBM v8 dataset. The evidence reports 5,078,345 event-valid and label-eligible records, 5,177 positives, 5,073,168 negatives, and an identical same-version replay. |
| 11:20:52 | Elena Kalajd?i? | `5530608` ? `fix(feature-002): finalize phase 3 import verification and docs` | Added source-stream hash/size checks before import completion, failure/replacement regressions, completed Phase 3 cleanup and quickstart updates. The full backend suite recorded 465 passing; the IBM import/replay and read-only database reconciliation are documented in `feature-002-import-identity.md`. |
| 14:23:37 | Elena Kalajd?i? | `0f5ad9a` ? `feat(feature-002): complete feature replay and rules baseline` | Completed the `history-v1` feature catalog/replay, exact-decimal `rules-v1` baseline, SQLite feature snapshots, and tests/evidence for T017?T025. The full IBM work-copy replay recorded 5,078,345 snapshots: 3,963,424 full and 1,114,921 warm-up/incomplete; the rules-only Phase 4 review passed its documented checks. |
| 14:35:38 | Elena Kalajd?i? | `27ac7d4` ? `fix(feature-002): protect concurrent feature snapshot builds` | Fixed a reproducible concurrent-build race that could erase completed snapshots. Added in-process and separate-CLI regressions, using a database/version-scoped OS lock. Targeted tests recorded 21 passing; full backend recorded 575 passing, with Ruff passing. |

### Duration estimate and limits

The four **committer timestamps** span **3 hours 54 minutes 38 seconds** (10:41:00?14:35:38). This is a publication window, not continuous work time. No participant supplied session start/end, breaks, or actual hours, so measured working time is **not available**.

For a rough comparison with the historical report, applying its same publication-window assumptions to the three same-day gaps gives **about 2.46 low / 3.68 central / 4.91 high provisional person-hours** for this single Git author. These are assumption-based proxies, not timesheets, confidence bounds, or confirmed effort. The estimates should be replaced if Elena supplies actual active-time details. The IBM import's recorded 1,315.29-second runtime is machine execution time and is not added as a separate person's labor estimate.

This update does not alter the pinned historical 19-commit calculation or its JSON snapshot. T009?T025 are recorded complete. T026, chronological split/protocol RED tests, is the next open task. Independent teammate reproduction, trained-model evaluation, and authoritative Phase 2 compliance remain outstanding.

## Feature 002 Phase 5 and pretrained-model contribution ledger - 13 November 2026

This ledger extends the prior contribution snapshot through the Phase 5 final review. Feature 002 baseline: `27ac7d4`. Git attributes the fourteen commits below to **Isidora Popovic**. This is commit-account attribution, not proof of exclusive manual authorship or measured work duration. User-reported team decisions are distinguished from Git commit attribution.

| Commit time (Europe/Budapest) | Git author | Commit | Work recorded |
|---|---|---|---|
| 16:05:55 | Isidora Popovic | `fe310c1` - `test(ml): add RED chronological evaluation protocol tests` | Added synthetic T026 tests for temporal whole-timestamp partitions, warmup, label eligibility, class coverage, deterministic membership and invalid provenance. |
| 16:15:00 | Isidora Popovic | `a2857cd` - `feat(ml): implement immutable temporal evaluation protocol` | Implemented T027 immutable split manifests and explicit eligibility; recorded controlled test results. |
| 17:27:44 | Isidora Popovic | `d606fb7` - `chore(ml): record locked dependencies and resource pilot` | Recorded the locked Python 3.14 ML stack and bounded 100,000-row import/history pilot, measured resource use and prospective fit ceilings. |
| 18:22:05 | Isidora Popovic | `b8643a4` - `docs(ml): prepare pretrained model integration branch` | Recorded the proposed inference-only direction and conflicts with original training tasks. |
| 18:34:27 | Isidora Popovic | `87b6980` - `docs(ml): assess pretrained model artifacts and input compatibility` | Compared pretrained candidates and documented data, feature-schema, licensing and compatibility findings. |
| 18:38:36 | Isidora Popovic | `13472f9` - `docs(ml): define gated pretrained inference architecture` | Defined the proposed local inference boundary, artifact manifest and fail-closed compatibility behavior. |
| 19:21:00 | Isidora Popovic | `c872375` - `docs(ml): switch pretrained candidate to IBM AML LightGBM` | Corrected the proposed candidate to IBM AML LightGBM while retaining scope and technical gates. |
| 20:21:47 | Isidora Popovic | `81b3b9a` - `test(ml): add RED IBM pretrained inference tests` | Added synthetic RED tests for IBM transaction input and inference contracts. |
| 21:02:46 | Isidora Popovic | `79987df` - `test(ml): align pretrained loader RED tests with IBM model` | Aligned loader RED tests to the pinned model schema and artifact requirements. |
| 21:14:13 | Isidora Popovic | `f426cec` - `test(ml): add RED IBM pretrained inference tests` | Extended inference tests against observed model metadata; missing-adapter failures remained intentional RED. |
| 21:16:56 | Isidora Popovic | `92bdd79` - `docs(ml): record blocked IBM pretrained inference gate` | Recorded graph provenance, mapping and manifest blockers to production loading. |
| 21:20:13 | Isidora Popovic | `429d6ec` - `docs(ml): record pretrained inference verification gate` | Recorded that no real inference or independent performance evaluation could be claimed. |
| 21:24:13 | Isidora Popovic | `07cce92` - `fix(data): preserve approved mapping bytes on Windows` | Pinned LF checkout for the unchanged mapping content; subsequent backend regressions passed. |
| 21:28:14 | Isidora Popovic | `570b344` - `docs(ml): finalize IBM pretrained inference handoff` | Finalized state, blockers, tests, artifact provenance and next technical gate. |

A subsequent evidence/checklist reconciliation commit is recorded as `docs(ml): reconcile pretrained model gate evidence`; the Git log provides its exact ID and timestamp. This ledger update is itself committed in the subject that contains this section; a commit cannot embed its own hash without changing it.

### Attribution and effort limits

The fourteen listed commit timestamps span 5 hours, 22 minutes and 19 seconds. This is a publication window, not continuous work. No participant supplied a start/end log or breaks, so actual working time is unknown and no person-hours are inferred. The user reported collective team approval for the proposed pretrained direction; technical artifact/input compatibility remains unresolved. Original T029-T036 remain open, and pretrained inference was not implemented or evaluated.

### Follow-up documentation commits - 13 November 2026

The evidence and handoff commits published after `570b344` are:

| Commit time (Europe/Budapest) | Git author | Commit | Work recorded |
|---|---|---|---|
| 22:01:41 | Isidora Popovic | `ddf5ceb` - `docs(ml): reconcile pretrained model gate evidence` | Reconciled artifact, security, feature, test and evaluation gate evidence; updated the pretrained checklist without completing original training tasks. |
| 22:01:54 | Isidora Popovic | `24a44c2` - `docs: record phase 5 contribution handoff` | Updated `next_work.md` with the final state, blockers and next action. |
| 13 Nov 2026; exact time in Git history | Isidora Popovic | This commit - `docs(evidence): record phase 5 contribution ledger` | Added the commit-by-commit Phase 5 attribution ledger and clarified publication-time limits. Its hash is in Git history because a commit cannot contain its own hash. |

All Git authorship above records the configured Git identity. It does not claim that Git timestamps measure active work or that the named author alone performed every human decision.
