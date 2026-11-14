# Phase 3 knowledge/retrieval evidence
2026-11-14 Europe/Belgrade. Branch feature03; baseline 83b587bcc17f8ad703ea67ca593b3785d7fc4391. Existing phase-02 handoff/next_work changes preserved.
Prompt: ../../prompts/development/003-investigation-phase-03.md. Human source review pending.

T014 RED: 11 executed failures on importable loader/archive boundary (NotImplementedError),
exit 1. Initial GREEN 10 passed / 1 failed: Windows symlink privilege unavailable and
fallback test used nonexistent path. Corrected fallback to actual forbidden project
reference namespace; no production relaxation or test skip. T014/T016 combined GREEN
20 passed (11 loader + 9 retrieval). T016 RED previously 9 executed failures on
missing BM25 behavior, exit 1. No collection failures.
Synthetic test reviewer metadata is authored testing data, not approval of T013 corpus.
Six real candidate docs/manifest remain staged and were NOT published. User inspected
manifest only, explicitly confirmed no source-text review. Thus T013/T015 as a whole
remain partial. T017 code is verified on test corpus, dependency on real publish pending.
User requested logical demo cutoff: 0.5 heuristic, configuration_version 2, expressly
unvalidated; no development/held-out pack opened or tuning performed.
Truncation is reported internally and through X-Results-Truncated HTTP header to
preserve closed SearchResult JSON shape; UI discloses capped results. No schema edit.
Historical text/provenance retained in immutable SQLite archive, not reread from source
on GET. Generated test stores/temp/cache under unique absolute root .cache paths.

## Final validation, 2026-11-14 Europe/Belgrade

Runtime: Python 3.14.3, uv 0.10.9, Node 24.20.0, npm 11.19.0;
Chrome/157.0.8103.52. No dependency or lockfile changes. Existing installed locked
environment reused. Commands below ran from repository root. No provider/key,
evaluation input/reference pack, glossary improvement or model evaluation used.

Additional executed RED checks:
- Resolved document-root escape: one intended assertion failure, then guard GREEN.
  A first fixture attempt failed from missing copied files; fixture repaired before
  the actual business RED. Windows symlink creation itself is unavailable; a
  monkeypatched resolved directory verifies this boundary without claiming OS
  symlink/junction integration coverage.
- `uv run --locked pytest backend/tests/unit/test_investigation_retrieval.py -k hash_seeds`
  with unique absolute temp/cache: first attempt lacked parent temp directory
  (environment error, not RED). Corrected attempt: 1 assertion failure, exit 1,
  different serialized scores across PYTHONHASHSEED 1-4. Sorted normalized query
  terms before summation; the same four-process regression now passes.
- `uv run --locked pytest backend/tests/unit/test_investigation_knowledge.py -k structure`
  with unique absolute temp/cache: 4 failures, exit 1. Invalid root/entry handling,
  boolean manifest version and path-shaped corpus identity now rejected before
  document reads. Corpus identity also binds manifest corpus_id.

Final backend command/environment (actual run identifier):
```powershell
$env:UV_CACHE_DIR=Join-Path $PWD '.cache/uv'
$runRoot=Join-Path $PWD '.cache/003-final-regression-bc44c59946b541988fd86188b0f72fba'
uv run --locked pytest backend/tests --basetemp "$runRoot/temp" -o "cache_dir=$runRoot/cache"
uv run --locked ruff check backend
```
Observed: **517 passed, 3 failed, 1 warning, exit 1**; Ruff PASS, exit 0.
Full suite is NOT GREEN. Final targeted modules within that run: knowledge 17,
retrieval 10, knowledge API 9 all pass. Exact deliberate failures are recorded in
[API evidence](feature-003-api.md). Existing Starlette/httpx deprecation warning
retained. No skip/xfail or placeholder route added. Earlier 512/3 and 513/3 runs
preceded final manifest/determinism regressions; 517/3 supersedes their counts.

Actual unreviewed-corpus CLI safety check:
```powershell
$env:PYTHONPATH=Join-Path $PWD 'backend/src'
uv run --locked python -m fraudlens.investigation.cli prepare-knowledge --manifest data/knowledge/fraudlens-aml-knowledge-v1/manifest.json --store "$reviewStore" --stage-only
```
`$reviewStore` was a unique absolute `.cache/003-cli-<UUID>/unreviewed-must-not-exist.sqlite`.
Observed controlled message, exit 2, store does not exist. Initial invocation
without PYTHONPATH failed module discovery (exit 1), not a validation success;
quickstart now includes the required backend/src path. All six normalized source
SHA-256 values verified directly; review fields null and staged status preserved.

## T022 real API/proxy/automated browser execution

Actual command: `$env:UV_CACHE_DIR=Join-Path $PWD '.cache/uv'` then
`node evidence/tasks/feature-003-knowledge-smoke.mjs` (exit 0). Repeated after final
loader/retrieval changes, also exit 0. Local loopback 8000/5173, isolated headless
Chrome profile/9228, hidden owned child processes; cleanup reported no error.
The verifier uses the documented uvicorn/Vite commands, checks ports are free
before starting, and stops only its own process trees. No public hosting.

[Executable verifier](feature-003-knowledge-smoke.mjs),
[authored-only preparation](feature-003-knowledge-smoke-prepare.py), and
[final observed results](feature-003-knowledge-smoke-results.json).

Nine observations passed:
1. Actual knowledge search and case 404/422 through direct backend.
2. Same calls through Vite proxy.
3. All three original case list/detail/back journeys, including exact explanations.
4. Publish changed TEST corpus while UI pins old version; selected historical
   passage text exactly equals old API text, with simulation/version provenance.
5. Explicit no-match rendered.
6. Actually missing test store gives unavailable UI, no fabricated hits.
7. Restore store and Retry: new test corpus is shown.
8. Stop/restart owned backend: original case Retry recovers.
9. No uncaught browser exceptions.

This is automated browser evidence, not human clicking or peer review. Corpus is
six wholly authored TEST documents with synthetic reviewer fields, never the six
real candidates. T022 and dependent delivery tasks remain partial pending T013
and real-corpus publish/recheck. No actual-source ingest, human corpus acceptance,
live LLM evaluation or full SC-001 report/citation acceptance is claimed.

Final focused rerun after extending path-exclusion assertions (no production
changes after the full backend run):
```powershell
$runRoot=Join-Path $PWD '.cache/003-targeted-0cfd6619d755468496ef25c50c9500c0'
uv run --locked pytest backend/tests/unit/test_investigation_knowledge.py backend/tests/unit/test_investigation_retrieval.py backend/tests/integration/test_investigation_knowledge_api.py --basetemp "$runRoot/temp" -o "cache_dir=$runRoot/cache"
uv run --locked ruff check backend
```
36 passed (17/10/9), 1 existing warning, exit 0; Ruff exit 0. Explicit assertions
reject evaluation inputs, reference and development-prompt namespaces before file
reads. This focused result does not replace or conceal the three full-suite REDs.
Final `git diff --check` exit 0; 28 new UTF-8 files checked for trailing whitespace
and evidence-local link targets. Existing source schemas, fixtures, lockfiles,
feature 002 and shared .agents/.specify instructions remain unchanged.
