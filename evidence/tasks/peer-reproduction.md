# T025 / SC-001: PENDING
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
