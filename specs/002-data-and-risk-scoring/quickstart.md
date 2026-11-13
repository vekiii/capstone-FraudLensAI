# Feature 002 validation quickstart

Phase 3 local import is available for the exact team-approved IBM v8 source and
mapping. [T016 evidence](../../evidence/tasks/feature-002-import-identity.md#t016-declared-ibm-v8-import-and-exact-replay--2026-11-13)
records the first import and immutable replay. Run these commands from the
repository root. The CSV and generated SQLite database stay local and ignored.

On macOS, prepare the locked environment and local output directory:

```sh
UV_CACHE_DIR="$PWD/.cache/uv" uv sync --locked --group dev
mkdir -p data/processed
PYTHONPATH=backend/src .venv/bin/python -m fraudlens.pipeline_cli import --source data/raw/HI-Small_Trans.csv --mapping data/mappings/ibm_hi_small_v1.json --namespace kaggle:ealtman2019/ibm-transactions-for-anti-money-laundering-aml:v8 --expected-sha256 b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040 --store data/processed/feature-002-ibm-v8.sqlite
```

On PowerShell, prepare the locked environment and run the equivalent command:

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/002-data-and-risk-scoring'
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
uv sync --locked --group dev
New-Item -ItemType Directory -Force data/processed | Out-Null
$env:PYTHONPATH = 'backend/src'
.\.venv\Scripts\python.exe -m fraudlens.pipeline_cli import --source data/raw/HI-Small_Trans.csv --mapping data/mappings/ibm_hi_small_v1.json --namespace kaggle:ealtman2019/ibm-transactions-for-anti-money-laundering-aml:v8 --expected-sha256 b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040 --store data/processed/feature-002-ibm-v8.sqlite
```

The first successful result has `status=complete`, `repeated=false`,
`source_records=5078345` and DatasetVersion
`dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802`.
Repeat the same import command against the same database: it returns
`repeated=true` and leaves the complete SQLite bytes unchanged. The measured
database was about 7.56 GB (7,559,012,352 bytes); check disk space first.
Read-only verification of that database:

```sh
.venv/bin/python evidence/tasks/feature-002-import-verify.py --source data/raw/HI-Small_Trans.csv --mapping data/mappings/ibm_hi_small_v1.json --store data/processed/feature-002-ibm-v8.sqlite
```

In PowerShell, replace `.venv/bin/python` with `.\.venv\Scripts\python.exe`.
The verifier checks the row equations, distinct D/C identities, source and
mapping hashes, SQLite schema version and `quick_check=ok`. The CLI import is
authorized only for the separately reviewed mapping, namespace and source hash;
it does not turn on general import. Read-only inspection remains available:

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/002-data-and-risk-scoring'
$env:PYTHONPATH = 'backend/src'
.\.venv\Scripts\python.exe -m fraudlens.pipeline_cli inspect --source data/raw/HI-Small_Trans.csv --mapping data/mappings/ibm_hi_small_v1.json
```

The inspect command still exits 2 with `pending_team_review`, complete
observations and `import_allowed=false` from the historical mapping flags.
Generic inspection without the bound mapping still rejects duplicate headers.
Feature building, evaluation, scoring, typed v2 delivery/decoding and consumer
integration remain planned. Use [plan.md](plan.md), [data-model.md](data-model.md)
and [contracts](contracts/api.md) for their expected behavior.

The initial 2026-11-13 [source audit](../../evidence/tasks/feature-002-source-audit.md)
contains the exact executable inspection command and results for the authorized
local file, including positional observation roles. It returns exit 2 for the
observed duplicate `Account` headers and unknown release. That historical
read-only scan predates the approved source binding; no source data is tracked.

## Preconditions

1. Read root AGENTS.md and next_work.md. In PowerShell set the feature
   selection for Spec Kit commands:

       $env:SPECIFY_FEATURE_DIRECTORY = 'specs/002-data-and-risk-scoring'

2. Use Python 3.14.x and Node 24 for the existing locked environment. The
   later Feature 002 ML stack is not installed or validated by this import.
3. Acquire the authorized IBM AML HI-Small release locally under ignored
   data/raw/ through the team's permitted process. Record source/release,
   license reference and SHA-256. Do not commit the file or credentials.
   This local session verified/adopted a hash-matched v8 reference; original
   acquisition history remains unknown; the final mapping review is recorded.
   Other checkouts require their own authorized file and hash verification.
   Before generating local files, verify the existing ignore rules for
   data/raw/, data/processed/, data/artifacts/ and evals/results/.
4. The source mapping and v2 contracts have collective final-byte approval.
   Feature catalog, rule policy and protocol are later gates. If the
   authoritative Phase 2 assignment becomes available, trace it before
   claiming compliance.

## Foundation regression available now

From the repository root, the existing fixture path can be checked
without IBM data. Record each new run's actual result separately.

    uv sync --locked --group dev
    uv run --locked pytest backend/tests
    uv run --locked ruff check backend
    cd frontend
    npm ci
    npm test -- --run
    npm run typecheck
    npm run build

Expected: current three fixture cases, strict v1 contracts, fixture health,
scorer replacement tests and frontend loading/error/empty/retry behavior
remain valid. Record actual counts, exits, runtime and any failures in
evidence/tasks/; do not copy historical counts as fresh results.

## Planned later local pipeline commands

The following interface is specified in
[data-and-scoring.md](contracts/data-and-scoring.md). `inspect` and `import`
exist now; the remaining subcommands are planned. From the repository root,
make backend/src importable:

    $env:PYTHONPATH = 'backend/src'
    $env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'

The exact source path, release ID, license reference, mapping and protocol
must come from the actual reviewed source audit. Examples use placeholders:

    uv run --locked python -m fraudlens.pipeline_cli build-features --dataset-version <completed-version> --feature-version history-v1
    uv run --locked python -m fraudlens.pipeline_cli freeze-protocol --dataset-version <completed-version> --feature-version history-v1 --config <reviewed-protocol-file>
    uv run --locked python -m fraudlens.pipeline_cli evaluate --protocol-id <frozen-protocol>
    uv run --locked python -m fraudlens.pipeline_cli score-run --dataset-version <completed-version> --scorer-version rules-v1 --protocol-id <frozen-protocol>
    uv run --locked python -m fraudlens.pipeline_cli activate-run --run-id <completed-run>
    uv run --locked python -m fraudlens.pipeline_cli reproduce --report-id <evaluation-report>

Expected checkpoints:

- Inspect reports observed schema, time span/granularity, amount/currency
  forms, label values/counts, source hash and ambiguities. It does not
  invent a mapping or activate data.
- Import accounts for every CSV record, separates event validity from
  label eligibility, preserves exact values and stable identities, and
  leaves no partial active version on failure/retry. Reimport of the
  same source/mapping has zero duplicate events.
- Features use only earlier event facts in [t−24h,t), with timestamp
  ties grouped and context-only warm-up counted. Label perturbations
  cannot change features or rule scores.
- Protocol prints exact split membership/counts and eligibility. If
  classes/positive counts fail, evaluate must not emit a substantive
  success report.
- Evaluate records frozen candidate selection, two-scorer metrics on
  identical eligible IDs, scorer-specific validation thresholds,
  test-holdout consumption and limitations. It does not assert ML
  improvement unless measured.
- Score-run produces an immutable label-free completed run. Activate-run
  changes one active pointer only after full validation. A failed new
  run leaves the old completed snapshot active.
- Reproduce compares source/mapping/artifact/protocol hashes and
  predictions/metrics under the frozen numeric tolerance; a mismatch
  is a failure to investigate, not a passing check.

## Planned analyst API check

After a completed rules or model run is selected, start the existing
FastAPI app in dataset mode with an explicit scorer. The settings/route
work is planned, not currently available:

    $env:APP_MODE = 'dataset'
    $env:APP_SCORER = 'rules'
    uv run --locked uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8000

In another PowerShell session, GET /api/health and /api/cases. A dataset
response has contract_version 2, source/scorer/run metadata, total and
displayed alert counts and a snapshot_ref. GET a case detail using that
exact snapshot query. Confirm matching transaction/run/feature identities,
directional amounts, truthful score/explanation wording and no target
labels. A switch to another active run makes an old snapshot query return
409 stale_snapshot rather than a mixed detail. No active complete run
returns 503 run_unavailable for cases; zero alerts returns a valid empty
list with total_alerts=0 and displayed_count=0.

Then reset APP_MODE to fixture and remove APP_SCORER from the environment.
The three-case v1 fixture journey must still work without any dataset
or model artifact. A dataset/model request with missing artifacts must
fail explicitly instead of switching to fixtures.

## Negative and scientific validation

The later tasks must include hand-checkable source-shaped fixtures for:
duplicate/missing/unknown headers, malformed/empty/invalid-encoding files,
partial import and retry, equal-valued distinct rows, rejected-row
identity stability, bank direction, decimal overflow/precision/currency,
label-ineligible valid facts, shuffled/tied/future timestamps, exact
lookback cutoff, warm-up/cold start, identifier/target proxies,
train-only transforms, unseen categories, missing classes/positives,
hand-computed AP/K/threshold metrics, K-boundary ties, zero alerts,
calibration status, explanation reconstruction/scale and artifact hash
mismatch. Publication tests must inject a mid-run failure and restart.

Source-shaped tests prove contract behavior, not IBM data quality or
model performance. The substantive run must use the declared acquired
source and exact frozen protocol. At least five explanations receive
independent factual/method review under SC-006; if fewer than five
alerts exist, select additional scored events by the predeclared
label-free sampling rule rather than manufacturing alerts.

## Evidence and acceptance

For every implementation unit, record task/FR/SC links, original prompt,
working revision, runtime/lock/data/artifact versions, RED failure
reason, GREEN/regression commands and actual exits, limitations and
human-review state in evidence/tasks/. The feature is not complete
until actual Foundation regressions, scientific checks, dataset
evaluation, human contract review and a second teammate's independent
reproduction are recorded. The author repeating a command does not
count as second-person reproduction.
