# Frontend development environment

Vanilla TypeScript/Vite frontend with strict fixture v1 and dataset v2 decoders,
snapshot-pinned detail requests and the case inspection UI. No framework or
runtime dependency is required.

Required runtime: Node 24.x. Phase 6 verified runtime (2026-11-12): Node v24.20.0, npm 11.19.0.
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
The earlier Foundation suite had 151 passes; current run results are recorded in
`../evidence/tasks/feature-002-regression.md`. See `T018.md` and `T017.md` for
Foundation behavior and limits.
No passWithNoTests option is set. Generated dist/ stays out of Git.

## Case UI

main.ts exports mountCaseApp(root, optionalClient), returning a disposal function.
It owns explicit UI states and request generations; views.ts safely creates DOM
nodes and styles.css provides responsive desktop/mobile layout. The case selector
remains available during detail loading/error. Back restores its selected button's
focus. Each navigation/retry invalidates and aborts earlier requests; only the
current generation can render, including when a client ignores cancellation.
The appropriate fixture or synthetic IBM notice is persistent. Scores appear as raw 0–1 values,
with source/version/time/explanation. Loading, empty, error and not-found states
are accessible; recoverable errors offer explicit retry. No raw exceptions or
invented case data are displayed. T019 confirms real backend/proxy HTTP and reruns
all checks; its final continuation records successful headless Chrome, console,
Enter and 390px viewport checks. Manual review and peer reproduction are pending.
Phase 7 browser verification exercised rules/model/empty/unavailable/stale v2
states and the v1 journey, including operation while the model file was absent.
See `../evidence/tasks/feature-002-api-ui.md`.

For v1 use `VITE_APP_MODE=fixture`; for v2 use `VITE_APP_MODE=dataset` with a
matching backend `APP_MODE=dataset APP_SCORER=rules|model` and an activated run.
Vite proxies relative `/api` requests to 127.0.0.1:8000. The v2 list preserves
server latest-100 ordering, carries its `snapshot_ref` to detail and exposes an
explicit refresh after 409. Exact paid/received amount and currency, source,
coverage time and explanation or unavailable state are shown without labels.

## API boundary

`src/api.ts` exports `getCases(options?: RequestOptions): Promise<CaseList>` and
`getCase(caseId: string, options?: RequestOptions): Promise<CaseDetail>`.
`RequestOptions.signal` accepts an AbortSignal. Requests use relative /api URLs,
with a fixed 5000 ms deadline covering headers and body reading. Timeout and
caller cancellation abort transport and reject promptly, including transports
that ignore abort. Timers and caller listeners are removed when requests settle.

Errors are `ApiError` instances with a typed `code` and optional HTTP `status`:
case_not_found, invalid_request, internal_error, invalid_response, network_error,
timeout or cancelled; v2 also handles `stale_snapshot` and `run_unavailable`.
Messages are controlled Serbian text; server/transport
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

## Acceptance update - 2026-11-12
Earlier pending acceptance statements above are superseded by the team's reported
joint setup verification and code/contracts/evidence review. T025/SC-001 and T028
are complete; see evidence/tasks/peer-reproduction.md and human-review.md from the
repository root. No additional automated/browser executions claimed by this update.
