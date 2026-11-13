# T025 / SC-001: PARTIAL - human execution received
Date: 2026-11-12 Europe/Belgrade. Branch initialization; baseline 6a99ef6dd6b0851b472d58021cd96d887b14a286; initial tree clean.
Prompt: ../../prompts/development/001-foundation-phase-06.md. Human review pending.

User confirmed no independent second-member result. T025 remains unchecked.
Agent, second terminal or fresh venv does not count as another teammate.

## Procedure for the second teammate
1. Use your own checkout/environment. Record name/team alias, date/time, OS,
   git branch --show-current, git rev-parse HEAD and git status --short.
   Obtain agreed changes through team Git flow; preserve local work.
2. Read README. Record uv --version, node --version and npm.cmd --version.
   Use Python 3.14 and Node 24; set UV_CACHE_DIR as documented.
3. Run uv sync --locked --group dev and npm.cmd --prefix frontend ci.
   Record actual exit codes/output and uv run --locked python --version.
4. Run all README backend pytest/Ruff and frontend test/typecheck/build commands.
   Current reference is 310 backend / 151 frontend, but record your actual counts,
   warnings, failures and versions, not copied expected results.
5. Run README's exact Uvicorn and Vite commands in two terminals (loopback only).
   Check /api/health directly and through :5173: HTTP 200 fixture JSON expected.
6. Open :5173: persistent synthetic notice, exactly three cases; inspect every
   detail/source/explanation, return and rapidly change selection without stale data.
7. Stop your backend; request/retry, observe unavailable state; restart and retry.
   Verify CASE-999=404 and CASE-1=422. Empty/failing scorer cases are automated;
   do not mutate shared fixtures or add debug endpoints for this check.
8. Stop only your own servers. Append actual participant/date/commit, versions,
   every command/exit/result, issues, limits and sanitized evidence links here.
9. Submit results for human review. Resolve concrete setup issues with evidence.
   Mark T025/SC-001 complete only after successful independent reproduction.
   Partial/failed results remain partial. Expected outputs above are not executions.

## Vedran Mitic - actual report, 2026-11-12
Source: user-submitted response annotations in this conversation, not agent execution.
Participant: Vedran Mitic; team: FraudLens AI. Reported timestamp:
2026-11-12T20:51:40.0414679+01:00. Windows PowerShell, D:/AIBootcamp/capstone.
Branch initialization; commit 733bff2746a7db4f0bd8be65cd3fd6ee717ba19b;
reported git status --short empty. Existing local project environment reused;
independent clean-machine installation not established. Explicit numeric exit codes
were not supplied, so success below follows pasted output rather than invented codes.

| Check | Actual supplied result |
|---|---|
| Runtime | uv 0.10.9; Node v24.20.0; npm 11.19.0 |
| Python | py --version 3.14.7; uv run --locked python --version 3.14.3 (project) |
| uv sync --locked --group dev | 41 resolved, 40 audited; completed |
| npm.cmd --prefix frontend ci | 67 added, 68 audited; 0 vulnerabilities reported |
| uv run --locked pytest backend/tests | 235 passed, 75 setup errors, 3 warnings; NOT passed |
| uv run --locked ruff check backend | All checks passed |
| npm frontend test -- --run | 151 passed, 5 files |
| npm frontend typecheck/build | Completed; Vite 8.3.8, 8 modules, built in 171ms |
| git diff --check | No output reported |
| Servers/UI | User confirms both run; CASE-001/002/003 visible |
| Health direct/proxy | Both reported status=ok, mode=fixture; direct command paste truncated, no numeric HTTP status supplied |
| Navigation | User confirms all requested visual/detail/back/rapid-selection observations |
| Backend stop | UI reported server returned invalid response; controlled error, not exact unavailable wording |
| Restart/Retry | User confirms working again |
| 404 | curl targeted root /, returned 404 closed case_not_found envelope; NOT proof for CASE-999 |
| 422 | /api/cases/CASE-1 returned HTTP 422 and closed invalid_request envelope |

Backend errors arise in pytest tmp_path setup: PermissionError WinError 5 accessing
user temp pytest-of-Korisnik. Existing .pytest_cache also could not be written.
These are environment/fixture setup errors, not demonstrated application assertion
failures. Starlette/httpx deprecation warning also present. No permissions changed.
Backend-down Vite may return non-JSON proxy error, classified by frontend as invalid
response; retry recovery succeeded. No product change made from this observation.

### Next participant commands
Run from repo root, in the same PowerShell session:
```powershell
$runId = [guid]::NewGuid().ToString('N')
$pytestTemp = Join-Path $PWD ".cache/peer-pytest-$runId"
$pytestCache = Join-Path $PWD ".cache/peer-pytest-cache-$runId"
uv run --locked pytest backend/tests --basetemp "$pytestTemp" -o "cache_dir=$pytestCache"
$LASTEXITCODE
curl.exe -i http://127.0.0.1:8000/api/cases/CASE-999
```
New unique local directories avoid inaccessible previous temp/cache state. Pytest
controls basetemp; never point it at an existing valuable directory. No tests are
excluded and no global temp ACL/execution policy changes are requested.
Expected reference: 310 passed, exit 0; CASE-999 HTTP 404. These are pending,
not executed results. Participant should send actual summary/exit and HTTP body,
and confirm whether they are the teammate independently reproducing original setup.
T025/SC-001 remain partial; T028 broader human code/evidence review remains pending.
Final server shutdown not reported. No full reproduction success claimed.

## Successful participant rerun - 2026-11-12
Source: Vedran Mitic's subsequent supplied annotations; not agent execution.
- uv run --locked pytest backend/tests --basetemp "$pytestTemp" -o "cache_dir=$pytestCache":
  310 passed, 1 warning in 4.99s. Participant separately confirmed $LASTEXITCODE=0.
- Remaining warning is the known Starlette/httpx deprecation; no temp/cache errors
  reported in this rerun. Prior failed attempt remains historical evidence.
- curl.exe -i http://127.0.0.1:8000/api/cases/CASE-999: HTTP 404 Not Found,
  content-type application/json, body {"error":{"code":"case_not_found","message":"Case not found."}}.
  Response Date header supplied: Thu, 12 Nov 2026 20:07:52 GMT. Recorded literally;
  no assumption that it follows the initial timestamp (their order differs).
All requested technical results have now been supplied. No further test rerun is
required from this evidence alone. Actual independent second-teammate context has
not yet been confirmed; existing local checkout/environment was used. T025/SC-001
remain pending only that criterion, not backend results or CASE-999 verification.
T028 broader human code/contracts/evidence review remains pending. No application
changes or new test execution performed by agent for this documentation update.

## Team confirmation - 2026-11-12
Vedran Mitic confirmed all team members jointly checked setup. This supplements
his actual command/UI reports above and confirms human team participation beyond
an agent-only or sole-author rerun. T025/SC-001 accepted as completed on this basis.
Scope is the reported checkout 733bff2746a7db4f0bd8be65cd3fd6ee717ba19b and working
copy. No separate machines, clean installs per member, individual names/signatures
or additional commands claimed. Earlier pending entries are historical.
