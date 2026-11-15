# Feature 003 validation quickstart

Status (2026-11-15): Phase 4 offline T023-T032/T034-T038 complete; Phase 3 reviewed
corpus preserved. Provider SDK adapter, worker, run API and report UI implemented;
actual fixture browser/API/proxy/worker journey PASS. T033 was attempted separately:
ConnectError then HTTP 400 / unsupported_capability; two-attempt budget exhausted.
Capability gate and Phase 5+ remain pending. See
../../evidence/tasks/feature-003-provider-access.md and
../../evidence/tasks/feature-003-fixture-journey.md.
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
.venv/Scripts/python.exe -m fraudlens.investigation.cli prepare-knowledge --manifest data/knowledge/fraudlens-aml-knowledge-v1/manifest.json --store data/processed/investigations.sqlite
.venv/Scripts/python.exe -m uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8000
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
durable worker attempt. Retry/cancel/review controls belong to later phases.

Reproduce the complete isolated offline journey with free 8000/5173/9228 and Chrome:
`node evidence/tasks/feature-003-fixture-journey.mjs --reviewed`.

## Planned recovery and review journeys (Phase 5+, not implemented)

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

Configure OPENAI_API_KEY privately in root .env or the backend process without
printing or committing it. Set OPENAI_MODEL to the explicitly intended ID; the
configured `gpt-6-luna` was attempted on 2026-11-15 but its required capabilities
remain unverified after HTTP 400. Process values override .env. Set
INVESTIGATION_PROVIDER=openai for a real worker; the opt-in probe uses the real
adapter independently of the ordinary test-provider/feature-enabled defaults.

```powershell
.venv/Scripts/python.exe -m fraudlens.investigation.cli probe-provider --synthetic-only
```

The current two-attempt authorization is exhausted; do not rerun under that budget.
Run only with a new explicit authorization for this small live check. Capture
safe availability/tool/schema capability outcome, actual returned model/request
ID and usage or unknown. No key or model access was verified in planning. Failure
is explicit pending access/capability; no fallback. A successful probe is not
report-quality evaluation. Any later real investigation/worker/report evaluation
requires its separately agreed scope; T033 alone does not authorize it.

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
