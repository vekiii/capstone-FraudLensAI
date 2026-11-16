# Feature 003 validation quickstart

2026-11-16 maintenance: [reliability v2](reliability-v2.md)
defines prompt/repair/deadline checks and an opt-in script-normalization
candidate. Backend regression: 814 PASS. This is a post-evaluation revision;
original frozen quality/time failures below are preserved, not re-evaluated.
The isolated new check is `.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-reliability-smoke.py`.
Use `--retrieval data/knowledge/fraudlens-aml-knowledge-v1/retrieval-development-v2.json`
with prepare-knowledge and a separate store to explicitly try the candidate.

Status (2026-11-15): reviewed six-document search, fixture investigation, durable
worker/recovery and analyst review are implemented; T051 human confirmation and
T033 synthetic provider capability check are complete. T054–T058 were executed,
including the saved live batch. T059-T061 automated report-judging-v2 execution, aggregation and audit are complete
(3 judge transports, 0/8 quality pass); no human validation is claimed. Retrieval/live quality and timing targets were not met.
User defers those reviews/findings; Phase 8 does not erase or rerun them.
T062 producer reconciliation is prepared; actual producer/consumer approval and
real dataset adapter/history are pending. See
[current handoff](../../evidence/tasks/feature-003-phase-08-handoff.md),
[T033 closure](../../evidence/tasks/feature-003-t033-closure.md) and
[live results](../../evidence/tasks/feature-003-t058-t061-handoff.md).
Run from repository root on `feature03` (or a reviewed descendant), preserving
the existing feature 002/ML branches. No automatic commit, push or merge.

## Setup and feature selection

The current laptop already has SDK 3.51.0 installed manually. Do not repeat uv
installation through the agent: earlier attempts coincided with system crashes.
Use its existing .venv directly for commands below. The setup block is for a fresh
checkout with dependencies not yet prepared; it is not required on this laptop.

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
py -3.14 -m uv sync --locked --group dev
npm.cmd --prefix frontend ci
```

Windows commands use `py -3.14 -m uv`: uv is installed under Python 3.14 even
when bare uv is absent from PATH. If bare uv works, it is equivalent for commands
below; Unix contributors use their available uv launcher. Investigation settings
now optionally read repository-root .env, independent of cwd; process values take
precedence, including empty values. Single-line KEY=value literals support optional
export, quotes and comments, with no interpolation/escape/shell expansion. Invalid
or unreadable files fail safely. Foundation APP_MODE still reads process environment.

Use existing Python 3.14 / Node 24 pins and committed generated lockfiles. Unix
contributors use npm instead of npm.cmd. Record actual versions and exits, not
historical counts. If execution policy blocks repository scripts, invoke a child
PowerShell with `-NoProfile -ExecutionPolicy Bypass -File`; do not change machine policy.

## Deterministic local setup (no provider calls)

The six-document corpus now includes actual provenance/reuse/human-review
metadata. Each checkout must prepare its own ignored local archive. Corpus
preparation never scrapes at runtime or imports evaluation reference files.
Use the reviewed committed manifest and these implemented commands:

```powershell
$env:INVESTIGATION_ENABLED = 'true'
$env:INVESTIGATION_PROVIDER = 'test'
$env:INVESTIGATION_SOURCE = 'fixture'
$env:INVESTIGATION_STORE = 'data/processed/investigations.sqlite'
$env:INVESTIGATION_ANALYST = 'local-demo-analyst'
$env:OPENAI_API_KEY = ''
$env:OPENAI_MODEL = ''
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe -m fraudlens.investigation.cli prepare-knowledge --manifest data/knowledge/fraudlens-aml-knowledge-v1/manifest.json --store data/processed/investigations.sqlite
.venv/Scripts/python.exe -m uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8000
```

These explicit empty process values override any private .env credentials. The
test provider creates authored diagnostic reports without OpenAI calls. In each
worker terminal repeat the same environment block before executing a worker.
Use your own chosen INVESTIGATION_ANALYST only for actions you actually perform.

In another terminal run `npm.cmd --prefix frontend run dev -- --host 127.0.0.1 --port 5173 --strictPort`.
Open http://127.0.0.1:5173. Search knowledge
with `missing occupation` or `supporting documentation`, inspect exact provenance,
and open CASE-001. `nomatchxyz` exercises no-match. Default preparation uses the
committed 0.5 demo heuristic, distinct from evaluated frozen configurations.
Title/glossary retrieval is implemented, reviewed and evaluated separately;
it is not silently enabled by this demo command. Frozen deployment selection
was baseline, cutoff 6.773881319338023, from development only; its held-out
Recall/MRR 0.50 remain below target. See
[T054–T056 evidence](../../evidence/tasks/feature-003-t054-t056.md).

Reproducible automated browser check (requires free 8000/5173/9228, installed
Chrome and prepared locked .venv; execute from an ordinary local PowerShell, or
with process escalation if the Codex sandbox blocks Chrome GPU subprocesses):

```powershell
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-phase08-browser.py
```

It uses isolated .cache stores/profiles and an absent ENV_FILE, checks reviewed
source historical text, review/recovery, missing key/model and original cases,
then stops only owned services. Results go to separate Phase 8 evidence files;
prior reports and verifier results are preserved. All actions are automated test
operator actions, not human review. Do not run it while your own services occupy
8000/5173/9228; stop only your own foreground demo first.

## Implemented offline investigation (Phase 4)

Open a case, click Prikaži AI istragu, then Pokreni novu istragu. Creation returns
a queued attempt without a provider call. In a separate root terminal
with the same feature settings run:

```powershell
.venv/Scripts/python.exe -m fraudlens.investigation.cli worker --store data/processed/investigations.sqlite --once
```

Poll the returned attempt; inspect actual test-provider tool trace, labeled
fixture source, report/limitations and evidence. No open-ended chat is required.
The CLI supports --poll for explicit single-worker execution. Do not run multiple
uncoordinated workers. A queued attempt's 120-second execution deadline starts
when claimed; if the worker is not running, UI says queued, not gathering.

For an explicit continuous single worker use --poll instead of --once; Ctrl+C
stops it. Backend-only INVESTIGATION_TEST_SCENARIO defaults to grounded; optional
authored needs_information/invalid_citation/refusal/incomplete scenarios are pinned
when a new attempt is created. They are diagnostics, not model quality evidence.
Report list returns at most 20 saved runs. UI polls at most 120 times, then offers
read-only refresh. Navigate away to stop browser polling; this does not cancel the
durable worker attempt. Phase 5 now provides explicit retry/cancel controls;
Phase 6 also provides explicit review and linked correction forms.

Reproduce the isolated journeys with the Phase 8 verifier above; it retains prior
phase-specific results and isolates contributor .env settings.

## Implemented offline recovery (Phase 5)

The report panel offers Otkaži pokušaj for created/gathering/drafting and
Pokreni novi pokušaj for failed/cancelled/needs_information. Retry may spend
again; prior unknown outcome is disclosed. A checkbox chooses compatible
revalidated evidence reuse. Retry creates a linked child; old counters/report
are preserved. The previous-attempt button reads saved history, with no dispatch.
Conflicts require Osveži sačuvano stanje; no automatic retry. A refreshed source
context is used only for new work; already opened historical reports and exact
citations remain inspectable in the panel. Historical attempt API access persists
across reload; the panel's in-memory historical list lasts for its mount.

Reproduce actual killed CLI processes, independent connections and released late
cancelled response, then real Chrome/API/proxy navigation and snapshot switching:

```powershell
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-phase08-browser.py
```

The verifier includes both browser and process checks, uses isolated ignored
stores/authored corpus and replaces ENV_FILE
with an absent path before settings load. They never load the real .env or call
OpenAI. Browser needs free 8000/5173/9228 and installed Chrome; sandbox GPU denial
may require running from an ordinary local terminal. Results/limits are recorded
in `evidence/tasks/feature-003-recovery.md`. Test provider results are workflow
evidence, not model-quality or billing evaluation. No hidden automatic recovery
of an interrupted dispatch occurs.

## Implemented review journey (Phase 6; T051 confirmed)

With a fixture/test run ready for review, inspect its citations and choose an
explicit decision; no decision is preselected. Enter 1–2000 characters of trimmed
rationale and select Sačuvaj odluku. Actor comes from INVESTIGATION_ANALYST on the
backend. Configure an actual operator's chosen identity only when that person
performs the review; an automated test identity is not their signature.
Needs-information offers only request_more_information and requires its saved
limitations draft. Failed/cancelled/active attempts have no review form.

Reopen the saved decision to see actor, UTC date, rationale and unchanged AI
claims/citations. A correction requires an explicit decision, rationale and
correction note. It appends a new review with a supersedes link. Prior events
remain in the local SQLite audit; the panel displays the current review and link.
No generated prose is modified. A disposition is not an evaluation rubric score.

Open the same draft in two browser sessions. After the first saves, the stale
second receives revision_conflict and must explicitly refresh before submitting
a linked correction. An uncertain transport outcome preserves the same key and
form input for repeating that exact request; no automatic submission occurs.

Reproduce the automated two-context Chrome/API/proxy/CLI check:

```powershell
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-phase08-browser.py
```

This harness always forces fixture/test mode, an absent ENV_FILE and the actor
AUTOMATED TEST OPERATOR (not human approval). It creates an isolated ignored
archive, never reads the real .env, calls OpenAI or runs T033. Ports 8000/5173/9228
must be free; Chrome sandbox restrictions may require an ordinary local terminal.
See evidence/tasks/feature-003-review.md for actual human findings, the corrected
error label and T051 closure. Automated actions cannot stand in for T059 quality
ratings or T066 another teammate's reproduction/code review.

## Recovery and review checks

1. Force a controlled provider timeout in a test script. Confirm failed state,
   exact counters, saved evidence and controlled error, not a completed report.
2. Stop the worker after dispatch intent but before outcome. Restart; the old
   attempt is interrupted with outcome_unknown, and GET consumes no tokens.
   Explicit retry creates a child; old evidence is copied only after binding checks.
3. Cancel while waiting; late result cannot change the cancelled attempt. Reuse
   the same request key; no duplicate attempt. Reuse it with a different body;
   request_conflict. Revisions reject stale cancel/review writes.
4. Open citations and record rationale/disposition. Reopen and verify actor/time,
   original draft, separate correction and immutable audit trail. Needs-information
   allows only request_more_information on a saved limitations draft.
5. Switch selected case while an old response is in flight. No mixed report.
   Fixture responses remain unchanged; saved old dataset reports remain historical,
   while new reads/retries against changed active snapshots reject stale_snapshot.

## Live provider history and explicit execution boundary

Private root .env supports OPENAI_API_KEY and OPENAI_MODEL; process values win.
Never print or commit credentials. The gpt-6-luna T033 tool/structured-output
probe completed under its separate four-attempt authorization. The subsequent
T058 batch completed 13 saved executions with 86/104 actual transport attempts.
Its unused budget is not a reason to rerun cases or improve outputs. Do not
invoke probe-provider, the live runner, an openai worker or UI creation with
live-provider settings as part of deterministic reproduction. Any new live run
requires a separately scoped request/budget; no fallback model is selected.

## Frozen evaluation

Follow [evaluation.md](evaluation.md). Both frozen retrieval configurations have
already run on all 20 held-out questions. Do not rerun freeze/tuning or rewrite
their exclusive outputs. Historical exact executable commands, including required
--split/--store/--freeze/--output arguments, are in
[T054–T056 evidence](../../evidence/tasks/feature-003-t054-t056.md). They are
execution history, not routine setup commands. Runtime retrieval never opens
references. Saved live reports/failures are under ignored
evals/results/feature-003/live-v1; they are local evidence, not Git-delivered data.

The user replaced both planned human scoring roles with automated LLM-as-judge
on 2026-11-15. Primary covers all eight outcomes; secondary uses an isolated
context on unchanged H02/H03/H04/H06/H08. See the
[successor protocol](../../evals/investigation/amendments/report-judging-v2.json)
and [decision record](../../evidence/tasks/feature-003-judge-amendment.md).
Original review cards/templates are historical source material, not current
assignments to Vedran/Milan. Actual gpt-6-luna primary/secondary machine scores
and audit now exist in separate judge-v2 outputs; see
[actual closure](../../evidence/tasks/feature-003-automated-evaluation.md).
Do not rerun the completed judge batch: 3/6 approved transports used, 0/8 pass.
The old human importer must not disguise machine identities as human signatures.
Preserve all failed cases, raw disagreements and existing outputs; no new generation.

## Dataset integration and regressions

First reconcile the latest feature 002 producer contract and record the actual
producer/consumer review. Verify strict history/time/currency/score meanings
against the pinned snapshot. Missing real producer/history remains unavailable,
not fake empty. Do not merge model branches just to make adapter tests import.

```powershell
$testRoot = Join-Path $PWD ('.cache/regression-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $testRoot | Out-Null
.venv/Scripts/python.exe -m pytest backend/tests --basetemp "$testRoot/temp" -o "cache_dir=$testRoot/cache" -q
.venv/Scripts/python.exe -m ruff check backend
npm.cmd --prefix frontend run test -- --run
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend run build
```

For Windows temp/cache failures, choose unique absolute paths under existing
root .cache using --basetemp and -o cache_dir; distinguish setup errors from
business RED. With feature disabled, no credentials/corpus/model installed,
exercise the original three-case list/detail/retry/404/422 journey unchanged.
Fresh Phase 8 results and their scope are in
[regression evidence](../../evidence/tasks/feature-003-regression.md). Source SHA,
schema change and bounded history review packet are in
[context review](../../evidence/tasks/feature-003-context-review.md). There is no
actual dataset adapter enabled in this checkout; dataset mode fails explicitly.

Another teammate follows the concrete
[reproduction protocol](../../evidence/tasks/feature-003-reproduction.md), records
their own commands/observations and performs code/contracts/evidence review.
T066 stays partial until actual evidence and T061 exist. T067 Converge is not
part of this execution; it does not automatically accept pending quality gates.
