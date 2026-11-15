# T039-T044 durable recovery — 2026-11-15

Scope: Phase 5 only, branch `feature03`, baseline/current HEAD `093739f`.
Initial worktree was clean. The repository is the `capstone-FraudLensAI`
subdirectory of the supplied workspace; root AGENTS.md was read there, followed
by current next_work, constitution/product context, specification, plan, tasks,
data model, API/provider/schema contracts, quickstart and state/workflow/API/UI/
provider-access/fixture evidence. No existing work was discarded.
Original request: [saved prompt](../../prompts/development/003-investigation-phase-05.md).

## Actual RED → GREEN → REFACTOR

- Initial recovery module: **8 failed** for intended missing behavior: expired
  work was reported as budget exhaustion, retry/cancel methods absent, create
  replay returned progressed rather than original state.
- Recovery API module: **5 failed**, missing retry/cancel routes (404).
- Recovery UI: first run had a fixture URL setup error, which is **not RED**.
  After correcting the literal Vite asset URL transformation: **5 intended
  failures**, missing methods/actions, no spend notice/history/refresh behavior.
- Reuse refinement: **2 failed / 1 passed**; child tools ignored copied evidence
  and create replay resolved a now-stale source. Both became GREEN.
- Backoff deadline: **1 failed**, timeout during transient backoff was incorrectly
  recorded as stale_snapshot. It now ends budget_exhausted within the original
  deadline; no second dispatch or assumed unknown outcome.
- Actual browser refresh after retry exposed two attempts being projected as
  two distinct runs. Added API assertion: **1 intended failure** (count 2 instead
  of 1), then implemented latest-attempt-per-run listing, retaining historical
  attempt GET access and the strict unique-run decoder.
- Parent access UI: **1 failed / 5 passed**, then read-only parent navigation
  implemented. Full frontend now **172 passed**.
- Refactored public views into a shared projection within one SQLite read
  snapshot. Claim/lease/deadline/start event now commit atomically. Existing
  repository audit-count test was updated to assert the new transition records
  and verify exact total rollback preservation, rather than assuming no audit.

Final backend: **653 passed**, 21.47 s; Ruff PASS. Frontend: **172 passed**,
8 files; TypeScript typecheck and Vite build PASS. Final targeted store
recheck after tightening the audit assertion: **8 passed**, 1.51 s.
No skips/xfails, dependency changes or lockfile rewrites.

## Delivered behavior

Expired or provably dead workers become failed/interrupted. Pending dispatches
become unknown, while completed/failed outcomes remain intact. Reopen/GET and
reconciliation never construct a provider or replay a request. Unknown usage is
disclosed; counts are reserved intents and are not claims of actual billing.
The worker's monotonic timeout includes transient backoff and repair; a child
gets fresh counters/deadline without resetting its parent's counters.

Retry/cancel require UUID Idempotency-Key and positive decimal If-Match, closed
JSON bodies and existing same-origin/Host guards. Replay returns the persisted
accepted response; a changed normalized payload/revision/target conflicts.
Cancel checks revision/state and atomically ends the attempt, invalidates the
lease and preserves ambiguous dispatch status. State/lease/pending-outcome
checks reject late provider results; tools/reports cannot resurrect ended work.

Retry is allowed from failed/cancelled/needs_information. It creates a child
inside the same run, retaining source identity and pinned prompt/provider/limits.
It increments the parent revision to reserve that explicit action and prevent
two distinct keys for the same saved revision from forking two children; the
parent's state, report, counters and evidence remain unchanged. Both parent and
child have linked audit events. Each later child retry uses its current revision.
Latest corpus/retrieval may be selected with reuse=false. With reuse=true their
versions must still match; source context must match in either mode. Case facts
and history are recomputed; passages resolve to their exact archived versions.
Only validated copies get fresh child evidence IDs plus parent mapping events.
When a new tool requests the same content, it uses these child IDs, still
reserving its own tool budget. No ambiguous provider continuation is reused.

UI actions are explicit. Uncertain retry/cancel transport retains the same key
for the same attempt/revision/operation/body; conflicts require explicit refresh.
Generation/context/attempt checks discard obsolete replies, including same-case
source changes. Browser navigation aborts browser requests only. The panel can
read the saved parent and keep already opened historical reports/citations when
an explicit refresh resolves a different source context. A full browser reload
does not retain that in-memory history list; immutable attempt URLs/API access
and parent navigation remain available. No cross-snapshot report mixing.

## T043: actual processes and two connections

Executed [process runner](feature-003-recovery-process.py), using the real
`cli.main worker --once` through the [isolated harness](feature-003-recovery-runtime.py).
Four distinct Python worker processes were killed after durable markers, then
fresh repository/service instances reopened the same SQLite archive. Separate
CLI processes executed only explicitly created children. Actual IDs, report
digests, outcomes and evidence counts are in [process results](feature-003-recovery-process-results.json).

| Killed boundary | Parent requests | Unknown outcome | Rebound evidence | Child requests |
|---|---:|---|---:|---:|
| pending first dispatch | 1 | true | 0 | 4 |
| completed result before tool | 1 | false | 0 | 4 |
| first evidence saved, second dispatch pending | 2 | true | 1 | 4 |
| drafting, all results complete | 4 | false | 7 | 4 |

Each same-key concurrent retry returned the same child. Different-key retry
race produced exactly one child plus revision_conflict. Another real CLI was
paused on an authored response; two independent connections cancelled with the
same key, returning identical persisted state. Releasing the late response left
cancelled, request count 1, outcome unknown, report null and no accepted result.
**6 process/concurrency observations PASS**. This is not live provider spend proof.

## T044: actual Chrome, API and proxy

[Browser runner](feature-003-recovery-browser.mjs), Chrome **157.0.8103.52**:
**8 observations PASS**, zero uncaught browser exceptions. Exact request statuses,
IDs and old/new context hashes: [browser results](feature-003-recovery-browser-results.json).

1. Queued navigation CASE-001 → CASE-002 → CASE-001; no mixed context or spend.
2. Explicit cancel via Vite same-origin proxy; persisted cancelled state.
3. Explicit child retry; deliberately delayed accepted HTTP reply while an
   explicit refresh reads the child; old reply ignored, worker completes.
4. Kill actual CLI after evidence/pending dispatch; failed/interrupted and unknown
   outcome visible; failed navigation/reopen and retry preserve parent 2 / child 4.
5. Child opens saved parent read-only; refresh restores latest attempt.
6. Switch isolated metadata snapshot, restart API, reject pinned old list and
   retry with 409 stale_snapshot; open historical report/exact bound citation;
   new attempt for the same case has a distinct context hash.
7. Feature disabled: original three cases/list/detail/back, direct/proxy 404/422.
8. Zero uncaught browser errors. Final owned-process cleanup and ports
   8000/5173/9228 PASS.

First sandbox Chrome failed before UI steps: GPU Access denied/Page.enable
timeout; cleanup briefly left its Vite child. Its exact workspace Vite process
was inspected and stopped. The harness now launches Vite directly and waits for
owned-process shutdown. Escalated reruns exposed the genuine RunList defect above
and a harness-only venv launcher/worker PID inequality; both were corrected before
the final passing run. Earlier failed runs are not counted as success.

## Reproduction, limits and remaining gates

Executed from repository root with existing locked environment:

```powershell
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe evidence/tasks/feature-003-recovery-process.py
node evidence/tasks/feature-003-recovery-browser.mjs
```

The harness replaces ENV_FILE with an asserted-absent path **before settings
load**, forces fixture/test provider and removes provider key/model variables.
No actual .env read, OpenAI call or T033 invocation occurred. Stores, copied
source metadata and Chrome profiles are isolated under ignored `.cache`.
Process checks used an authored six-document corpus, not new human source review.
Chrome required sandbox escalation on this machine. No installation occurred.

Full backend command used a newly created `.cache/p5-final-<uuid>` directory:
`.venv/Scripts/python.exe -m pytest backend/tests --basetemp <dir>/tmp -o cache_dir=<dir>/cache -q --tb=short`.
Also executed `.venv/Scripts/python.exe -m ruff check backend`,
`npm.cmd --prefix frontend test -- --run`, `npm.cmd --prefix frontend run typecheck`,
`npm.cmd --prefix frontend run build` and `git diff --check`.
Python **3.14.7**, Node **24.20.0**, npm **11.19.0**.

Local PID ownership proves death when the OS permits inspection. Unknown/legacy
owners, inaccessible PIDs or PID reuse fall back to the bounded lease; this is
one local worker, not distributed execution. Historical state is preserved, but
exactly-once provider billing and model quality are not established. Human review
and independent reproduction remain pending. T033's HTTP 400 capability gate
remains explicitly **open/unchecked**; no model substitution or diagnosis here.
No Phase 6+, review implementation, live evaluation, commit or push.
