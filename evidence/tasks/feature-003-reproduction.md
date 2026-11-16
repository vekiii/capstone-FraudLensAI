# T066 executable handoff and teammate reproduction — 2026-11-15

## Latest agent reproduction - 2026-11-16

[Fresh run/review evidence](feature-003-offline-review-20261116.md): backend 921
PASS, frontend 186 PASS, Ruff/typecheck/build PASS, 29 isolated actual browser/
API/proxy and 6 process observations PASS. Fixed one unit test's dependency on
an ignored historical live artifact using an independently hashed test fixture
and changed/missing negative cases. Runtime/frozen results were not changed.
Existing app port 5173 was preserved; generated harness used 5174 and cleanup
passed. No provider/environment-file access or package installations.

These are agent-executed checks, not another teammate's manual execution or
human code/contracts sign-off. The actual teammate table below stays pending;
T066 remains unchecked. T094 technical clarification proposal is ready for
human review, with historical quality failures preserved.

Status: **partial**. Documentation and independent automated regression are
complete; another teammate's actual execution and human code/contracts/evidence
review are **pending**, as is full T061. No names, signatures, dates, commands or
results below are filled in on someone else's behalf. Earlier foundation/team
reviews and T051 confirmation do not constitute this Feature 003 reproduction.

## Prepared documentation

Updated [root README](../../README.md), [frontend README](../../frontend/README.md),
[knowledge README](../../data/knowledge/README.md) and
[quickstart](../../specs/003-ai-investigation/quickstart.md): actual local settings,
CLI arguments, separate worker, safe test-provider mode, reviewed corpus archive,
demo versus frozen retrieval configuration, live execution history and pending
quality/producer gates. Removed stale claims that T033/T051/provider/report work
are unimplemented and removed non-executable evaluation command placeholders.

## Another teammate's concrete deterministic procedure

1. Agree a checkout/commit including this change after the team publishes it.
   Do not silently merge producer/ML branches. Read AGENTS.md then next_work.md.
   Record your actual identity/role, date/time, OS, checkout path, `git branch
   --show-current`, `git rev-parse HEAD`, `git status --short`, Python/uv/Node/npm
   versions. Before commit, record HEAD plus the reviewed diff because HEAD alone
   does not identify these uncommitted files. Use another teammate as runner;
   this agent's setup is not second-person reproduction.
2. Follow quickstart Setup with Python 3.14 / Node 24 and locked dependencies.
   Use existing .venv on the prepared laptop; do not reinstall routinely. On a
   fresh machine install committed locks. Do not send secrets in evidence.
3. Follow Deterministic local setup exactly: provider=test, source=fixture,
   explicit empty process key/model and a separate investigation store. Prepare
   reviewed knowledge; note returned corpus/retrieval IDs. Start backend and
   Vite in two terminals on 127.0.0.1:8000 / :5173. Leave any unrelated processes
   alone; resolve occupied ports with their owner.
4. Query health and cases directly and through proxy with Invoke-RestMethod.
   Search `supporting documentation`, inspect exact passage/version/source/
   jurisdiction/simulation limitations, then `nomatchxyz`. Note the demo 0.5
   heuristic differs from frozen evaluated baseline. Open all three cases,
   navigate back and rapidly switch selections; verify no mixed stale view.
5. Open CASE-001 investigation and explicitly create a test attempt. It stays
   queued until you run `worker --store data/processed/investigations.sqlite
   --once` in a third terminal with the **same** settings/PYTHONPATH. Inspect its
   authored test report/limitations and exact cited evidence. No OpenAI call is
   needed. Retry/cancel a diagnostic attempt explicitly; inspect saved history.
6. Review a test draft using your actual configured analyst alias and rationale;
   reopen it and append a correction. Verify the original draft/citations and
   prior review remain immutable. Use two browser sessions for stale revision
   conflict/refresh. These diagnostic review decisions are not T059 ratings.
7. Stop only your foreground backend, refresh and note the controlled error;
   restart and Retry. Check `curl.exe -i http://127.0.0.1:8000/api/cases/CASE-999`
   gives 404 and CASE-1 gives 422; repeat via :5173. Record actual envelopes.
8. Run the complete regression commands in quickstart and save exit codes/counts.
   Stop your own foreground demo services first. Optionally run the Phase 8
   automated browser verifier with installed Chrome/free 8000/5173/9228; label it
   automated. It creates separate .cache stores/profiles and safe absent .env.
   Pass `--result-prefix feature-003-peer-youralias-yyyymmdd` to the verifier to
   save your outputs under distinct filenames; never overwrite Phase 7
   reports or T055/T056 freeze. Do not invoke a probe/live worker/evaluation.
9. Review changed code/tests, schemas and evidence. Specifically inspect
   [producer reconciliation](feature-003-context-review.md), strict identities,
   exact money/time/score semantics, privacy, missing/empty history and remaining
   unavailable adapter. Human producer/consumer approval is separate and must
   name the actual reviewed SHA/interface/decision. Do not approve unknown
   semantics merely because a synthetic test passes.
10. Record below actual commands/exit codes, API/UI observations, issues and
    unexecuted scenarios. Send the filled record in this conversation or the
    team's normal review workflow. No external message is sent by this agent.

## Actual reproduction/review record (unfilled)

| Field | Actual evidence |
|---|---|
| Runner / reviewing teammate | pending |
| Date/time / OS / checkout path | pending |
| Branch / HEAD / clean status or reviewed diff | pending |
| Python / uv / Node / npm / browser | pending |
| Dependency commands / exits | pending |
| Corpus/retrieval IDs / exact passage comparison | pending |
| Backend / frontend / typecheck / build / Ruff / diff commands and exits | pending |
| Direct health/API and proxy / 404/422 | pending |
| Case list/detail/back / rapid selection / Retry | pending |
| Test worker / report / evidence / cancel/retry | pending |
| Explicit review / amendment / two-session conflict | pending |
| Code/contracts/evidence findings and actual decision | pending |
| Issues / unexecuted steps / evidence filenames | pending |

Phase 8 agent results are in [regression evidence](feature-003-regression.md).
T066 checkbox remains empty until actual teammate evidence plus T061 exist.
T059 human rating assignments are superseded by the user-approved automated
report-judging-v2 amendment; execution/aggregation/audit completed with failed
quality, see [actual results](feature-003-automated-evaluation.md) and
[judge decision](feature-003-judge-amendment.md). Original reports and failed
quality/time targets remain preserved in the historical
[Phase 7 handoff](feature-003-t058-t061-handoff.md).
T067/Converge and full acceptance have not been run or inferred.
