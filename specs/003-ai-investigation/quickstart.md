# Feature 003 validation quickstart

Status: Phase 3 T013-T022 complete. Milan Gavrić approved all six source texts and
documented reuse/applicability. Exact reviewed corpus published locally;
actual-source API/proxy/automated Chrome verification PASS. See
../../evidence/tasks/feature-003-phase-03-completion.md. Provider/worker/report
commands below remain future targets; only prepare-knowledge exists currently.
Run from repository root on `feature03` (or a reviewed descendant), preserving
the existing feature 002/ML branches. No automatic commit, push or merge.

## Setup and feature selection

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
py -3.14 -m uv sync --locked --group dev
npm.cmd --prefix frontend ci
```

Windows commands use `py -3.14 -m uv`: uv is installed under Python 3.14 even
when bare uv is absent from PATH. If bare uv works, it is equivalent for commands
below; Unix contributors use their available uv launcher. No .env is required:
settings read process environment only and do not automatically load .env.

Use existing Python 3.14 / Node 24 pins. A task adding the SDK resolves and commits
the generated lockfile once; subsequent contributors use locked installs. Unix
contributors use npm instead of npm.cmd. Record actual versions and exits, not
historical counts. If execution policy blocks repository scripts, invoke a child
PowerShell with `-NoProfile -ExecutionPolicy Bypass -File`; do not change machine policy.

## Offline first increment

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
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
py -3.14 -m uv run --locked python -m fraudlens.investigation.cli prepare-knowledge --manifest data/knowledge/fraudlens-aml-knowledge-v1/manifest.json --store data/processed/investigations.sqlite
py -3.14 -m uv run --locked python -m uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8000
```

In another terminal run `npm.cmd --prefix frontend run dev`. Search knowledge
with `missing occupation` or `supporting documentation`, inspect exact provenance,
and open CASE-001. `nomatchxyz` exercises no-match. The 0.5 cutoff remains an
untuned demo heuristic; Serbian-English glossary support is future T054 work.

Reproducible automated browser check (requires free 8000/5173/9228, installed
Chrome and prepared locked .venv; execute from an ordinary local PowerShell, or
with process escalation if the Codex sandbox blocks Chrome GPU subprocesses):

```powershell
node evidence/tasks/feature-003-knowledge-smoke.mjs --reviewed
```

It uses an isolated .cache store/profile, leaves the default archive intact,
checks actual-source historical text and original cases, and stops owned services.

## Planned investigation increment (T023+, not implemented)

Commands/journeys from here through evaluation are future validation targets.
Start investigation: creation must
return a queued attempt without a provider call. In a separate root terminal
with the same feature settings run:

```powershell
uv run --locked python -m fraudlens.investigation.cli worker --store data/processed/investigations.sqlite --once
```

Poll the returned attempt; inspect actual test-provider tool trace, labeled
fixture source, report/limitations and evidence. No open-ended chat is required.
The CLI supports --poll for explicit single-worker execution. Do not run multiple
uncoordinated workers. A queued attempt's 120-second execution deadline starts
when claimed; if the worker is not running, UI says queued, not gathering.

## Recovery and review journeys

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

## Explicit live provider gate

Configure OPENAI_API_KEY privately in the backend process without printing it or
committing an .env value. Set OPENAI_MODEL to the actual project-accessible ID,
not the project name or a guessed Luna string. The application does not load .env
unless implementation deliberately provides that capability; environment
variables are the specified interface. Set INVESTIGATION_PROVIDER=openai.

```powershell
uv run --locked python -m fraudlens.investigation.cli probe-provider --synthetic-only
```

Run only when intentionally authorizing this small live synthetic check. Capture
safe availability/tool/schema capability outcome, actual returned model/request
ID and usage or unknown. No key or model access was verified in planning. Failure
is explicit pending access/capability; no fallback. A successful probe is not
report-quality evaluation. Then repeat the investigation with real tool calls,
configured single worker, typed report validation and human inspection.

## Frozen evaluation

Follow [evaluation.md](evaluation.md). Freeze inputs, independent references,
reviewers, corpus, prompt, config and dev-selected cutoffs before held-out use.

```powershell
uv run --locked python -m fraudlens.investigation.cli evaluate-retrieval --protocol evals/investigation/protocol.json --configuration baseline
uv run --locked python -m fraudlens.investigation.cli evaluate-retrieval --protocol evals/investigation/protocol.json --configuration improved
uv run --locked python -m fraudlens.investigation.cli evaluate-reports --protocol evals/investigation/protocol.json --provider openai
uv run --locked python -m fraudlens.investigation.cli summarize-reviews --protocol evals/investigation/protocol.json --reviews evals/results/feature-003/reviews.json
```

Execution commands select split via the frozen protocol, never silently default
to held-out during development. Generation gets inputs only; offline metric
joining loads private references after frozen predictions/reports. Record both
retrieval configurations, all eight reports/failures, secondary review of at
least four, >=12 safety scenarios, 20 search latencies and five live demo runs.
Below-target results are scientifically valid but not a feature-quality pass.
No actual IBM model metrics or synthetic checks mislabeled as LLM evaluation.

## Dataset integration and regressions

First reconcile the latest feature 002 producer contract and record the actual
producer/consumer review. Verify strict history/time/currency/score meanings
against the pinned snapshot. Missing real producer/history remains unavailable,
not fake empty. Do not merge model branches just to make adapter tests import.

```powershell
uv run --locked pytest backend/tests -q
uv run --locked ruff check backend
npm.cmd --prefix frontend run test -- --run
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend run build
```

For Windows temp/cache failures, choose unique absolute paths under existing
root .cache using --basetemp and -o cache_dir; distinguish setup errors from
business RED. With feature disabled, no credentials/corpus/model installed,
exercise the original three-case list/detail/retry/404/422 journey unchanged.
Record actual API/proxy/browser observations for new and old routes, no copied
historical counts. A teammate reproduces independently; human reviews are not
inferred from a passing test. Save evidence and update next_work.md after each
implementation unit. Run Converge against actual code only after implementation.
