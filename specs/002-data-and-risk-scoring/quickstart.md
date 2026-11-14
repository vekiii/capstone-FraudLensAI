# Feature 002 validation quickstart

Feature 002 has a working local IBM import, history-v1 features, frozen model,
offline evaluation and read-only v2 UI. [T016 evidence](../../evidence/tasks/feature-002-import-identity.md#t016-declared-ibm-v8-import-and-exact-replay--2026-11-13)
records the first import and immutable replay. Run commands from the repository
root. The CSV, SQLite, model and large evaluation outputs stay local and ignored.

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

## Implemented local feature build

Run this against a **working copy** of the completed import, with enough disk
space for the additional snapshots. Inputs are the SQLite store containing a
complete, provenance-compatible DatasetVersion, its exact `dv_` ID, and the
frozen `history-v1` catalog. The following command was executed on the IBM v8
working copy in [Phase 4 evidence](../../evidence/tasks/feature-002-feature-rules.md#t025-actual-source-replay-and-repeatability):

```sh
cp data/processed/feature-002-ibm-v8.sqlite data/processed/feature-002-ibm-v8-rules-work.sqlite
PYTHONPATH=backend/src .venv/bin/python -m fraudlens.pipeline_cli build-features --store data/processed/feature-002-ibm-v8-rules-work.sqlite --dataset-version dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802 --feature-version history-v1
```

Make the working copy once after the import completes; this needs roughly
another 7.56 GB before feature-build growth. Do not copy over an existing
work store or modify the archived import. On PowerShell, use `Copy-Item`.

The first successful build returns JSON with `status=complete`,
`feature_version=history-v1`, `snapshot_count=5078345` and `repeated=false`.
The same command on that completed working copy returns `repeated=true` and
the same count. The first 24 hours are context-only; snapshots exist for those
events but their coverage is `incomplete` and they are not scoreable. Building
features does not create a scored run or publish v2 API responses.

## Read-only inspection

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/002-data-and-risk-scoring'
$env:PYTHONPATH = 'backend/src'
.\.venv\Scripts\python.exe -m fraudlens.pipeline_cli inspect --source data/raw/HI-Small_Trans.csv --mapping data/mappings/ibm_hi_small_v1.json
```

The historical pre-approval inspect run exited 2 with `pending_team_review`.
The approved mapping and source binding now allow import of the exact reviewed
release. Generic inspection without the bound mapping still rejects duplicate
headers. See [plan.md](plan.md), [data-model.md](data-model.md) and
[contracts](contracts/api.md) for the current behavior.

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
   locked Feature 002 ML stack is installed with the command above.
3. Acquire the authorized IBM AML HI-Small release locally under ignored
   data/raw/ through the team's permitted process. Record source/release,
   license reference and SHA-256. Do not commit the file or credentials.
   This local session verified/adopted a hash-matched v8 reference; original
   acquisition history remains unknown; the final mapping review is recorded.
   Other checkouts require their own authorized file and hash verification.
   Before generating local files, verify the existing ignore rules for
   data/raw/, data/processed/, data/artifacts/ and evals/results/.
4. The source mapping and v2 contracts have collective final-byte approval.
   The feature catalog, rule policy and evaluation protocol are frozen. If the
   authoritative Phase 2 assignment becomes available, trace it before
   claiming compliance.

## Locked regression

From the repository root, the existing fixture path can be checked
without IBM data. Record each new run's actual result separately.

    UV_CACHE_DIR="$PWD/.cache/uv" uv sync --locked --group dev
    UV_CACHE_DIR="$PWD/.cache/uv" PYTHONPATH=.:backend/src uv run --locked pytest backend/tests --ignore=backend/tests/unit/test_pretrained_loader.py --ignore=backend/tests/unit/test_pretrained_ibm_inference.py
    UV_CACHE_DIR="$PWD/.cache/uv" uv run --locked ruff check backend
    cd frontend
    npm ci
    npm test -- --run
    npm run typecheck
    npm run build

The excluded pretrained suites are a separate known RED proposal for an
incompatible external model; run and report them separately. Backend tests cover
the unchanged v1 schema and reviewed v2 schema parity. Record actual results in
`evidence/tasks/feature-002-regression.md`.

## Current fixture and dataset servers

Fixture v1 needs no IBM database or model file. Run these in separate terminals:

```sh
APP_MODE=fixture PYTHONPATH=backend/src .venv/bin/uvicorn fraudlens.main:app --host 127.0.0.1 --port 8000
VITE_APP_MODE=fixture npm --prefix frontend run dev -- --host 127.0.0.1
```

Open `http://127.0.0.1:5173/`; the fixture list has `CASE-001`–`CASE-003`.
For v2, score and activate a completed run first, then restart the servers with
`APP_MODE=dataset APP_SCORER=rules` or `APP_SCORER=model`,
`APP_RUN_STORE=data/artifacts/feature-002-runs.sqlite`, and
`VITE_APP_MODE=dataset`. Dataset `GET /api/cases` is 200 with 0/0 counts when
the frozen `no_alert` run is active, 503 when no matching completed run exists.
Copy the list's `snapshot_ref` into `GET /api/cases/{case_id}?snapshot=...`;
an old reference returns 409 `stale_snapshot`. HTTP never scores or activates.

```sh
APP_MODE=dataset APP_SCORER=rules APP_RUN_STORE=data/artifacts/feature-002-runs.sqlite PYTHONPATH=backend/src .venv/bin/uvicorn fraudlens.main:app --host 127.0.0.1 --port 8000
VITE_APP_MODE=dataset npm --prefix frontend run dev -- --host 127.0.0.1
```

PowerShell uses `$env:APP_MODE`, `$env:APP_SCORER`, `$env:APP_RUN_STORE`,
`$env:VITE_APP_MODE` and `$env:PYTHONPATH='backend/src'` before starting each
process. Stop the old foreground servers with Ctrl+C before switching modes.

## Obtain the local model before scoring

The trusted `artifacts/feature-002-history-v1-20261114/` directory is ignored
and **is not present in a clean checkout**. Its selected model, train-fitted
preparation, metadata and manifest must be obtained through an authorized
team-local transfer. Verify the transferred files against the frozen hashes
below, then use only that directory for exact T062 reproduction. The ignored
`evals/results/phase8/test_predictions.json`, `test_report.json` and
`holdout_ledger.json` are also required by `reproduce`; transfer these through
an approved private channel or make an independent first benchmark with the
same frozen artifact. Keep private labels and record-level results out of Git.

For an independent *new* local fit from the authorized CSV and complete feature
work store, first run `freeze-protocol` below, then use a fresh ignored output
directory under the repository's `artifacts/` root:

```sh
PYTHONPATH=backend/src .venv/bin/python -m fraudlens.train_phase5 --store data/processed/feature-002-ibm-v8-rules-work.sqlite --protocol evals/protocols/feature_002_v1.json --out artifacts/feature-002-history-v1-peer
PYTHONPATH=backend/src .venv/bin/python -c 'from pathlib import Path; from fraudlens.model_scoring import create_manifest; print(create_manifest(Path("artifacts/feature-002-history-v1-peer"), Path("evals/protocols/feature_002_v1.json")))'
```

The fit uses only frozen train/validation membership and saves the chosen
pipeline, input preparation, ordered features, thresholds and reload probe.
Record the returned manifest hash and the metadata/model hashes. A new fit may
produce different bytes or a different manifest hash; it does **not** silently
replace the frozen selected artifact or its reference predictions. Verify its
provenance and predictions explicitly before using it for a separate comparison.
The full clean-checkout path and an independent fit have not been run on a
second machine; T066 remains open for Isidora's actual reproduction record.

## Frozen local inputs and eight CLI commands

The authorized CSV must be acquired separately. If it is absent, leave the
source-dependent steps pending. For the transferred frozen artifact, before any
model deserialization, confirm
SHA-256 of the source `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`,
mapping `a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57`,
protocol `01fff67d44895b5a1aa6de6dfbb6c6c107f01c041ba7c972bf42210e2b316068`,
manifest `2732691cb08daafba9d303ef6f3c8f616e03b3dc51505d3abb9772ceadd3919e`,
and model `fd2332d543941886eb7d0092d7a606b683d1d7c198e3763865ebc7b6a2df0838`.
The trusted loader independently verifies origin, root containment, versions and
hashes before joblib; uploads are rejected. Use `shasum -a 256` on macOS or
`Get-FileHash -Algorithm SHA256` on PowerShell. Check local ignore rules with
`git check-ignore` for `data/raw/`, `data/processed/`, `data/artifacts/`,
`artifacts/` and `evals/results/` before adding files.

The eight `fraudlens.pipeline_cli` subcommands are `inspect`, `import`,
`build-features`, `freeze-protocol`, `evaluate`, `score-run`, `activate-run`, and
`reproduce`. Define the shell function below before the examples. On Windows,
invoke each subcommand after `.\.venv\Scripts\python.exe -m
fraudlens.pipeline_cli` with `$env:PYTHONPATH='backend/src'`.

```sh
fl() { PYTHONPATH=backend/src .venv/bin/python -m fraudlens.pipeline_cli "$@"; }

# 1. Inspect is read-only; historical pending flags can return exit 2.
fl inspect --source data/raw/HI-Small_Trans.csv --mapping data/mappings/ibm_hi_small_v1.json

# 2. Import into a NEW local store; same-source replay returns repeated=true.
fl import --source data/raw/HI-Small_Trans.csv --mapping data/mappings/ibm_hi_small_v1.json --namespace kaggle:ealtman2019/ibm-transactions-for-anti-money-laundering-aml:v8 --expected-sha256 b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040 --store data/processed/feature-002-ibm-v8.sqlite

# 3. Build features on a completed working store, never on the archived import.
fl build-features --store data/processed/feature-002-ibm-v8-rules-work.sqlite --dataset-version dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802 --feature-version history-v1

# 4. Audit the frozen source/split read-only.
fl freeze-protocol --store data/processed/feature-002-ibm-v8-rules-work.sqlite --dataset-version dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802 --config evals/protocols/feature_002_v1.json

# 5. Join private labels only after frozen test predictions exist.
fl evaluate --protocol evals/protocols/feature_002_v1.json --predictions evals/results/phase8/test_predictions.json --labels evals/results/phase8/test_labels.json --ledger evals/results/phase8/holdout_ledger.json --report evals/results/phase8/test_report.json

# 6. Score into a separate local store with a fresh run ID; this does not activate.
fl score-run --source-store data/processed/feature-002-ibm-v8-rules-work.sqlite --run-store data/artifacts/feature-002-runs.sqlite --dataset-version dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802 --protocol artifacts/feature-002-history-v1-20261114/metadata.json --run-id run_rules_001 --scorer rules --threshold no_alert

# 7. Activate only the completed matching run.
fl activate-run --run-store data/artifacts/feature-002-runs.sqlite --run-id run_rules_001 --scorer rules

# 8. Repeat frozen predictions/metrics after the first report exists.
fl reproduce --source-store data/processed/feature-002-ibm-v8-rules-work.sqlite --protocol evals/protocols/feature_002_v1.json --artifact-dir artifacts/feature-002-history-v1-20261114 --manifest-sha 2732691cb08daafba9d303ef6f3c8f616e03b3dc51505d3abb9772ceadd3919e --predictions evals/results/phase8/test_predictions.json --report evals/results/phase8/test_report.json --ledger evals/results/phase8/holdout_ledger.json --out-dir evals/results/phase8/reproduce
```

For a model `score-run`, use `--scorer model`, `--run-id run_model_001`, and add
`--artifact-dir artifacts/feature-002-history-v1-20261114 --manifest-sha 2732691cb08daafba9d303ef6f3c8f616e03b3dc51505d3abb9772ceadd3919e`.
Use the same manifest SHA with model `activate-run`. The score-run protocol
argument is the frozen development `metadata.json` containing both validation
thresholds and the protocol hash. Both selected thresholds are `no_alert`; a
failed/incomplete staging run leaves the old active snapshot available. Use a
new run ID for a retry; completed rows are immutable.

For the first offline benchmark, save predictions before opening labels:

```sh
mkdir -p evals/results/phase8
PYTHONPATH=backend/src .venv/bin/python -m fraudlens.benchmark_phase8 predict --source data/processed/feature-002-ibm-v8-rules-work.sqlite --protocol evals/protocols/feature_002_v1.json --artifact-dir artifacts/feature-002-history-v1-20261114 --manifest-sha 2732691cb08daafba9d303ef6f3c8f616e03b3dc51505d3abb9772ceadd3919e --output evals/results/phase8/test_predictions.json
PYTHONPATH=backend/src .venv/bin/python -m fraudlens.benchmark_phase8 labels --source data/processed/feature-002-ibm-v8-rules-work.sqlite --protocol evals/protocols/feature_002_v1.json --predictions evals/results/phase8/test_predictions.json --output evals/results/phase8/test_labels.json
```

The model was already fit on train and selected on validation in Phase 5; do
not retrain merely to score the test. Top-20 ranking is separate from the
published `no_alert` list. The old 60/20/20 notebook exposed every new test
row, so this benchmark and all repeats are exploratory. Large output remains
ignored under `evals/results/`; only sanitized summaries enter evidence.

For a teammate, reproduce the import, feature build and selected-scorer loading
from an authorized same-hash CSV in their own checkout. Record machine, versions,
source/mapping/protocol/artifact hashes, actual commands/exits/timing and numeric
differences. The author's own `reproduce` run is not second-person verification.
The frozen IBM benchmark found model AP `0.0307344403263558` versus R1–R3 AP
`0.0018670818306353214`; both had zero positives in top 20 and zero published
alerts under `no_alert`. Validation ranking and the exploratory amount-ratio
tie experiment are documented separately in
[`feature-002-model-metrics.md`](../../evidence/tasks/feature-002-model-metrics.md).
The direct browser journey was checked in Phase 7; Phase 8 added live API/Vite
proxy checks, without a fresh direct browser pass.
