# T065 fresh regression — 2026-11-15

**Completed in the available fixture/authored-contract scope. Actual producer
coverage remains pending T062–T064 and is not replaced by these results.**
Branch feature03; baseline 0829296f2824764c3773f6c8e90eb94d39843455, initially
clean. Python 3.14.3, uv 0.10.9, Node v24.20.0, npm 11.19.0, Chrome
157.0.8103.52. Existing dependencies used directly: no install/lockfile changes.

## Actual commands and outcomes

From repository root:

```powershell
$testRoot=Join-Path $PWD ('.cache/phase08-backend-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $testRoot | Out-Null
.venv/Scripts/python.exe -m pytest backend/tests --basetemp "$testRoot/temp" -o "cache_dir=$testRoot/cache" --tb=short -q
.venv/Scripts/python.exe -m ruff check backend
npm.cmd --prefix frontend run test -- --run
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend run build
$env:PYTHONPATH=Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-phase08-browser.py
```

| Check | Fresh result | Exit |
|---|---|---|
| Complete backend (no exclusions/skips/xfails added) | **776 passed**, 68.38 s | 0 |
| Ruff backend | All checks passed | 0 |
| Complete frontend | **186 passed**, 9 files | 0 |
| TypeScript | tsc --noEmit PASS | 0 |
| Production build | 12 modules; Vite 8.3.8, 275 ms | 0 |
| Automated knowledge browser/API/proxy | **10 PASS** | 0 |
| Automated review browser/API/proxy | **9 PASS** | 0 |
| Automated recovery/configuration browser/API/proxy | **10 PASS** | 0 |
| Actual killed CLI / two-connection process checks | **6 PASS** | 0 |

The full backend includes schema/Pydantic revalidation/parity, original foundation
responses, feature toggle, corpus/provider/settings errors, review/recovery,
outbound privacy and authored dataset boundaries. Newly added authored context
module separately **17 PASS**, exit 0. Before correcting its test command, an
uncreated --basetemp parent produced 17 setup errors; this was not business RED.
Existing behavior passed without artificial breakage. No new adapter RED/GREEN
is claimed; that is pending review of the actual producer port.

## Real local process/API/proxy/browser observations

[Execution manifest](feature-003-phase08-browser-results.json) binds original
and generated verifier hashes, exact commands, exit codes and separate outputs.
Verifier copies stay under ignored .cache; original verifiers and prior result
files were not rewritten. Knowledge execution uses actual six reviewed source
documents; historical replacement is clearly synthetic. Review/recovery uses
authored context and test provider. These are automated Chrome checks, never
teammate manual reproduction, analyst approval or live LLM evaluation.

| Result file | Observed scenarios |
|---|---|
| [Knowledge](feature-003-phase08-knowledge-results.json) | Direct/proxy search, no match, source/provenance, archived exact text after corpus switch; missing store and Retry; original cases, real backend restart and Retry; 404/422. |
| [Review](feature-003-phase08-review-results.json) | Safe literal injection rendering, bound citation, explicit rationale/decision, forged actor refusal, two-session stale 409, explicit refresh, immutable amendment/replay, needs-information restrictions, reopened audit. |
| [Recovery/config](feature-003-phase08-recovery-results.json) | Navigation/reopen, zero-spend GET, cancellation, linked retry, killed worker, delayed response/source switch and preserved historical citations; disabled original three cases/404/422; actual openai-mode empty-key POST gives 503 provider_unavailable; missing-model run-list gives 503 context_unavailable, browser controlled error and foundation remains 200. |
| [Processes](feature-003-phase08-process-results.json) | Four actual killed worker boundaries, released late response after cancel, two independent DB connections. |

Each browser verifier checks ports 8000/5173/9228 are free before starting and
after cleanup. All three report owned_process_cleanup PASS; only owned hidden
processes stopped, isolated Chrome profiles, no user's profile/service changed.
The isolated runtime replaces ENV_FILE with an absent .cache path before settings
load and removes/empties private key/model. Missing-key/model tests dispatch no
worker/provider. No .env contents read, no real model probe or OpenAI request.
Chrome execution used explicit sandbox process escalation for local testing.
After adding the teammate-result prefix option and knowledge post-cleanup port
assertions, a verifier-only argparse variable shadowing error occurred before
starting any subprocess. Corrected; final complete browser/process rerun passed
all 35 checks. No product failure or business RED inferred from that harness bug.
The preservation audit's first invocation also needed to unseal the stored freeze
payload before accessing fields; corrected verification passed without altering
any old sealed artifact.

## Scope and acceptance

**No remaining intentional RED failures in this full backend run.** The older
T012/T035 failures were resolved in earlier phases. Unimplemented real producer
checks are missing integration evidence, not skipped tests or claimed success.
T065 may be checked for its defined available-scope regression with this explicit
dataset limitation; T062/T063/T064 remain unchecked. No live rules/model-context
smoke or actual IBM result is claimed. No original foundation/feature 002
contracts, scorer, DB, runtime adapters or ML code changed.

[Preservation audit](feature-003-phase08-preservation-results.json) checks all 13
saved live outputs, generation code and frozen retrieval artifact hashes without
reading held-out answer text or rewriting prior audits. Retrieval/live targets
remain below target, user-deferred human quality review remains pending. This
regression cannot satisfy T059/T061 or feature-quality acceptance.
