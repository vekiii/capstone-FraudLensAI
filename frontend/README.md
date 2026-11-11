# Frontend development environment

Minimal vanilla TypeScript/Vite scaffold for T004 (FR-001). Project name only;
case UI, API client and behavior tests belong to later tasks.

Required runtime: Node 24.x. Verified runtime: Node v24.20.0, npm 11.19.0.
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
There are no behavior tests yet; an empty test run is not a passing suite.
No passWithNoTests option is set. Generated dist/ stays out of Git.
