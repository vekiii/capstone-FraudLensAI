# Feature 003 Phase 3 completion - 2026-11-14 Europe/Belgrade

Branch feature03; baseline 27ecc38, clean tree at start. Scope: finish the actual
reviewed-corpus dependency for T015/T017/T019/T021/T022. T013 review is already
recorded for all six texts by Milan Gavrić. No T023+, commit/push or deployment.
[Original request and clarification](../../prompts/development/003-investigation-phase-03-completion.md).

## Result

T013-T022 complete. Existing production loader/BM25/API/UI needed no behavior
changes. Published the reviewed six-document/six-passage corpus to the separate,
ignored `data/processed/investigations.sqlite`; exact archive equals `stage`
output and republishing returns the same identity. No producer/ML store touched.
All source text, approved review metadata, retrieval configuration and lockfiles
remain unchanged from the baseline.

- Corpus: `corpus_2fa1aa3379fadf2749300897ef79b9239c2ced2da311b370a8974d709b0bfaf3`.
- Retrieval: `071f1a593fa17471295860bb5abc3a0064261a7e159bdf3d530494881001bccb`.
- Configuration v2 still uses the untuned 0.5 demo heuristic. These selected
  smoke queries are integration checks, not retrieval-quality evaluation/tuning.

## Actual publication and local retrieval

From the repository root:

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
py -3.14 -m uv sync --locked --offline --group dev
py -3.14 -m uv run --locked --offline python -m fraudlens.investigation.cli prepare-knowledge --manifest data/knowledge/fraudlens-aml-knowledge-v1/manifest.json --store data/processed/investigations.sqlite
```

Both exit 0. `git check-ignore data/processed/investigations.sqlite` confirms the
generated archive is ignored. Exact stored corpus equals freshly validated
reviewed documents/passages. Direct search checks PASS:

| Query | First document | Observed BM25 score |
|---|---|---|
| missing occupation | sim-missing | 2.574655394264198 |
| supporting documentation | us-records | 3.1883019028243638 |
| affiliate confidentiality | us-confidentiality | 3.610943264037094 |
| nomatchxyz | explicit no_match | no hits |

## Test isolation correction: observed RED to GREEN

Once the real default store existed, the composition test expecting missing
knowledge accidentally read that store and got a normal SearchResult: KeyError
`error`, 516 passed / 4 failed. This exposed test dependence on local operator
state, not a production search defect. The module's autouse environment fixture
now sets INVESTIGATION_STORE to a fresh `tmp_path/missing.sqlite`. Assertions
unchanged; no skip/xfail, default-store removal or route placeholder.

Focused composition module: 4 passed / 3 expected T035 RED. Final full suite:
517 passed / the same 3 expected T035 failures, one existing Starlette/httpx
warning. The missing-knowledge assertion now passes while the prepared demo
store remains present. Full backend is NOT GREEN.

```powershell
$runRoot = Join-Path $PWD '.cache/003-reviewed-final-681955a506e44f10a0d7ef4144e3d16c'
py -3.14 -m uv run --locked --offline pytest backend/tests --basetemp "$runRoot/temp" -o "cache_dir=$runRoot/cache" -q
py -3.14 -m uv run --locked --offline ruff check backend
npm.cmd --prefix frontend run test -- --run
npm.cmd --prefix frontend run build
```

Observed exits: pytest 1; Ruff 0; frontend test 0 (156/6 files); build/typecheck 0
(12 modules). Three retained RED nodes are exactly those documented in
[API evidence](feature-003-api.md): future attempt error envelope, cross-origin
mutation and mutation JSON requirement, all scheduled for T035.

## Actual-source API/proxy/browser verification

Extended the existing verifier with `--reviewed`, retaining its authored-only
mode. Backend starts through the existing .venv interpreter after locked sync,
so a bare uv PATH entry is unnecessary. Preparation publishes reviewed sources
to a unique ignored .cache archive. Only that archive receives the later
authored TEST replacement used to check historical pinning; approved source
files and the default demo archive are never modified by this scenario.
Resolved paths are checked inside the unique work directory before file moves.
Cleanup handles already-exited children and fails the report on cleanup errors.

```powershell
node evidence/tasks/feature-003-knowledge-smoke.mjs
node evidence/tasks/feature-003-knowledge-smoke.mjs --reviewed
```

Final observed exits: 0 / 0. Authored-only mode: 9 observations PASS, work
`.cache/003-smoke-a18590c2-3abf-408d-ab70-06e185240d48`.
Reviewed-source mode: 10 observations PASS, work
`.cache/003-smoke-625aff23-b698-4407-a6d9-98904dd9c35e`.
[Reviewed results](feature-003-reviewed-knowledge-smoke-results.json),
[authored-only results](feature-003-knowledge-smoke-results.json).

Reviewed-mode observations include:

1. Direct HTTP and Vite proxy: six actual documents with Milan's review metadata,
   supporting-documentation search, no-match, knowledge 422/404 and original case
   404/422 responses.
2. Original CASE-001/002/003 list/detail/back with exact explanation text.
3. Actual simulated missing-facts procedure and visible SIMULATED provenance.
4. Pin reviewed corpus, publish isolated TEST replacement, then inspect exact
   old FinCEN passage; literal text equals pinned API text. Historical 2007 US
   jurisdiction and source URL are visible.
5. No-match UI, actual store unavailability and recovery via Retry.
6. Owned backend stop/restart and original case Retry recovery.
7. No uncaught browser exceptions; no cleanup error. Final port check confirmed
   no owned listeners remained on 8000/5173/9228.

Sandbox limitations were investigated rather than counted as product failures:
initial browser attempts reached API/proxy but Chrome Page.enable timed out or
WebSocket failed. Captured stderr showed GPU subprocess access denial and fatal
GPU failure; adding ordinary headless flags alone did not resolve it. One retry
then refused an occupied port 5173, preserving the existing listener. Read-only
process inspection outside the sandbox established the orphan Vite/npm chain
belonged to this run (creation 11:31:43; exact repository Vite command); only
those verified processes were stopped. Final browser runs executed with tool
escalation outside the Codex sandbox and passed. Chrome's own sandbox was not
disabled; no system policy/permissions changed. Final test processes were hidden
and isolated, and their cleanup passed.

## Limits and continuation

Runtime: Python 3.14.7, uv 0.10.9 (`py -3.14 -m uv`), Node 24.20.0,
npm 11.19.0, Chrome/157.0.8103.52. No dependency/lockfile change.
No .env needed or loaded, provider SDK/key/model/probe, report/tool/worker,
analyst disposition, dataset integration, held-out pack, quality metric or
human browser/peer reproduction claim. Full SC-001 report-citation acceptance
and full Feature 3 remain future work. T023 is the next task in Phase 4, to be
separately agreed; do not resolve T035's REDs ahead of its planned work.

Final consistency verification PASS: persistent default archive still exactly
matches reviewed stage output after both isolated smoke runs; 9+10 smoke checks
PASS without cleanup errors; T001-T022 checked, T023-T067 unchecked; 97 local
Markdown links resolve; changed Python/JSON/UTF-8 and node syntax checks PASS;
Git diff whitespace PASS. Product code, schemas, manifest/source/config and
lockfiles unchanged. HEAD remains 27ecc38; no Git publication performed.
