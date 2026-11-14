# Phase 3 UI evidence
2026-11-14 Europe/Belgrade. Branch feature03; baseline 83b587bcc17f8ad703ea67ca593b3785d7fc4391. Existing phase-02 handoff/next_work changes preserved.
Prompt: ../../prompts/development/003-investigation-phase-03.md. Human source review pending.

T020 RED: 4 executed tests failed, two missing client/decoder and two absent-form
assertions. Importable boundary, not collection failure. T021 initial GREEN 4 passed;
full frontend suite 155 passed (151 prior + 4 new), typecheck and build exit 0.
Knowledge navigation composed minimally; original exported mountCaseApp unchanged.
Literal rendering, provenance, safe errors/retry, encoding, abort and stale
search/passage suppression tested. Additional final checks recorded below.
T021 remains partial as actual reviewed corpus/API delivery dependency is pending.
No provider/model or frontend case-v2 decoding migration performed.

## Final verification - 2026-11-14 Europe/Belgrade

Added malformed-date/version/nullable/size regression: 1 actual assertion failure
and 4 passes, exit 1; strict timestamp handling fixed (calendar date, 24:00,
terminal newline). Targeted test command then returned 5 passed, exit 0.
Caller cancellation additionally verified with a pending fetch: promise rejects
with controlled cancelled code and internal fetch signal is aborted.

Final commands from repository root, Node 24.20.0/npm 11.19.0:
```powershell
npm.cmd --prefix frontend run test -- --run
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend run build
```
Observed **156 passed in 6 files**, exit 0; typecheck exit 0; Vite 8.3.8 build
12 modules, exit 0. Existing 151 tests retained. No lockfile change.
Actual automated headless Chrome/proxy/UI observations are in
[knowledge evidence](feature-003-knowledge.md) and the linked smoke JSON.
T020 complete by test-task type; T021 code independently verified but delivery
remains partial because actual reviewed source corpus is unavailable.

## Actual-source dependency closed - 2026-11-14

T021 complete: reviewed sources published, UI exercised through actual API/proxy
and Chrome. Exact historical FinCEN passage/jurisdiction/URL, simulated missing
facts, no-match, missing-store Retry and original three-case/restart journeys
PASS. Frontend 156 tests PASS, typecheck/build PASS; no product UI code change.
See [completion evidence](feature-003-phase-03-completion.md) and
[reviewed results](feature-003-reviewed-knowledge-smoke-results.json). This is
automated browser verification, not human clicking, peer reproduction or live
report-quality evaluation. Earlier pending dependency statements are historical.
