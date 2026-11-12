# Frontend development environment

Vanilla TypeScript/Vite frontend with T017's typed API boundary and T018's complete
synthetic case inspection UI. No framework or runtime dependency is required.

Required runtime: Node 24.x. Latest verified runtime: Node v24.21.0, npm 11.19.0.
The user approved this change from Node 22 on 2026-11-11. Global runtime
installations and execution policies were not changed. Use npm.cmd in PowerShell.

From repository root:
```powershell
node --version
npm.cmd --version
npm.cmd --prefix frontend ci
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend run build
npm.cmd --prefix frontend run test -- --run
npm.cmd --prefix frontend run dev
```

package-lock.json was updated with npm after changing the Node engine to >=24 <25
and resolving @types/node@24. Use locked installs afterward. Complete resolved
versions and integrity hashes are in package-lock.json; initial execution history
and the runtime-change verification are in evidence/tasks/phase-01-handoff.md.

Vite binds to 127.0.0.1:5173 with strictPort and proxies /api to
http://127.0.0.1:8000. Vitest uses jsdom. Backend absence does not block setup.
T017 makes all 82 original API tests GREEN and adds 46 lifecycle/contract checks.
T018 makes all 19 original DOM tests GREEN and adds four UI lifecycle checks.
The full suite has 151 passed, 0 failed; typecheck/build pass.
See ../evidence/tasks/T018.md and T017.md for actual results and limitations.
No passWithNoTests option is set. Generated dist/ stays out of Git.

## Case UI

main.ts exports mountCaseApp(root, optionalClient), returning a disposal function.
It owns explicit UI states and request generations; views.ts safely creates DOM
nodes and styles.css provides responsive desktop/mobile layout. The case selector
remains available during detail loading/error. Back restores its selected button's
focus. Each navigation/retry invalidates and aborts earlier requests; only the
current generation can render, including when a client ignores cancellation.
The synthetic notice is persistent. Scores appear as raw 0–1 illustrative values,
with source/version/time/explanation. Loading, empty, error and not-found states
are accessible; recoverable errors offer explicit retry. No raw exceptions or
invented case data are displayed. T019 confirms real backend/proxy HTTP and reruns
all checks; interactive browser/console and visual layout checks remain unexecuted
because browser access failed. See ../evidence/tasks/T019.md.

## API boundary

`src/api.ts` exports `getCases(options?: RequestOptions): Promise<CaseList>` and
`getCase(caseId: string, options?: RequestOptions): Promise<CaseDetail>`.
`RequestOptions.signal` accepts an AbortSignal. Requests use relative /api URLs,
with a fixed 5000 ms deadline covering headers and body reading. Timeout and
caller cancellation abort transport and reject promptly, including transports
that ignore abort. Timers and caller listeners are removed when requests settle.

Errors are `ApiError` instances with a typed `code` and optional HTTP `status`:
case_not_found, invalid_request, internal_error, invalid_response, network_error,
timeout or cancelled. Messages are controlled Serbian text; server/transport
messages are never forwarded. Views can ignore cancelled requests and expose
explicit retry for failures. There are no automatic retries or fabricated data.

`src/contracts.ts` exports canonical Transaction, RiskAssessment, CaseSummary,
CaseDetail, CaseList, Health, ErrorBody and ErrorEnvelope types and their decoders
(ErrorBody is validated within decodeErrorEnvelope). Decoders accept unknown,
check closed nested objects, required fields, patterns, Unicode lengths, finite
score bounds, UTC calendar timestamps and transaction identity. getCase also
checks the returned case ID. Invalid input throws ContractValidationError,
translated at the request boundary into ApiError with code invalid_response.
Empty items remain a successful empty collection. There are no new dependencies.

Focused checks from the repository root:
```powershell
npm.cmd --prefix frontend run test -- --run tests/api.test.ts tests/api-lifecycle.test.ts tests/contracts.test.ts
npm.cmd --prefix frontend run typecheck
```
