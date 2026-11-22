# FraudLens AI web application

`web/` is the repository's only web application. It combines the case and
dataset dashboard with the Feature 005 showcase in one React 18, TypeScript and
Vite app. Application code and components use `.ts` or `.tsx`; `index.html` is
only the CSP-protected entry point. Styling lives in CSS. Python/FastAPI and ML
services stay in `backend/`.

## Routes

| Route | Purpose |
|---|---|
| `/` | Showcase overview and current evidence status |
| `/data` | Dataset, features and evaluation limits |
| `/rag` | Advisory RAG design and status |
| `/live` | Clearly labelled illustrative sample states and API availability |
| `/cases` | Fixture v1 or published dataset v2 case browser |
| `/dataset-overview` | Read-only aggregates from the active dataset/model run |

Case and overview API values are decoded from `unknown` using the existing
closed TypeScript contracts before rendering. Set `VITE_APP_MODE=dataset` when
starting Vite to request dataset v2; fixture mode is the default. The client
keeps snapshot identity for dataset detail requests and handles stale snapshots
as an explicit recovery state. The showcase's illustrative files remain
labelled and separate from measured API output.

## Start locally

Install the locked dependencies with `npm.cmd --prefix web ci`. Start FastAPI
from the repository root in one terminal:

```powershell
uv run --locked uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8000
```

Start the web application in another terminal:

```powershell
npm.cmd --prefix web run dev
```

Vite binds to `127.0.0.1:5173` and proxies `/api` requests to FastAPI on port
8000. Open `http://127.0.0.1:5173/`.

For a published dataset run, set `APP_MODE=dataset`, `APP_SCORER`,
`APP_RUN_STORE`, and `VITE_APP_MODE=dataset` in the server environments. The
backend remains read-only for browser requests; scoring and activation are not
performed by the web application.

## Typecheck, tests and build

TypeScript uses `strict`, `noUnusedLocals` and `noUnusedParameters`; typechecking
covers application source, tests and Vite configuration.

```powershell
npm.cmd --prefix web run test -- --run
npm.cmd --prefix web run typecheck
npm.cmd --prefix web run build
```

All direct dependency versions and licences are recorded below and locked in
`package-lock.json`.

## Dependencies and licences

| Package | Version | Licence |
|---|---:|---|
| React / React DOM | 18.3.1 | MIT |
| React Router DOM | 7.18.5 | MIT |
| Vite | 8.3.8 | MIT |
| `@vitejs/plugin-react` | 6.3.0 | MIT |
| GSAP | 3.15.1 | GSAP Standard “no charge” licence |
| Lenis | 1.3.27 | MIT |
| three.js | 0.187.0 | MIT |
| TypeScript | 7.0.2 | Apache-2.0 |
| Vitest | 5.1.0 | MIT |
| jsdom | 31.0.0 | MIT |
| `@types/react` / `@types/react-dom` | 18.3.28 / 18.3.7 | MIT |
| `@types/three` | 0.187.0 | MIT |
| `@types/node` | 24.19.2 | MIT |

Typography uses local system fallback stacks; there are no remote font requests.
GSAP SplitText is not used. The showcase makes no external LLM calls or real
data requests.
