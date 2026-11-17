# TypeScript web migration finalization

Date: 2026-11-17
Branch: `feature/005-real-time-fraud-detection-mlops-spec`
Reviewed commit: `3da2510` (`feat(web): consolidate app in React TypeScript`)

## Scope and changes

The final application remains the single React/TypeScript/Vite app in `web/`;
Python/FastAPI, ML services, API contracts, and source data were not changed.
The six routes are `/`, `/data`, `/rag`, `/live`, `/cases`, and
`/dataset-overview`. Header/footer navigation uses React Router links. Case and
dataset pages preserve the typed v1/v2 API decoders, cancellation and snapshot
handling, and explicit loading/empty/error/retry states. The dataset overview
preserves loading, error, retry and successful aggregate states. The live page
keeps its explicit fixture label and API availability status. Existing tests
cover those API/UI contracts.

Each route page is loaded with React `lazy` and has a route-scoped Suspense
loading status, so the shared navigation remains mounted during page loads.
GSAP, ScrollTrigger, Lenis and Three.js are asynchronously imported from effects;
WebGL/motion setup retains reduced-motion, low-power, initialization-failure and
cleanup paths. Three.js classes are selected by named exports to retain build
tree-shaking. Native scrolling and visible page content remain available if
optional animation chunks fail.

Updated the current Foundation plan and data tracking guide from the removed
`frontend/` package-lock path to `web/`. Historical task records and original
prompts retain their original paths as historical evidence.

## Bundle comparison

Vite baseline recorded in the migration evidence: `index` **893.52 kB** minified
(single eager application chunk). Final build: `index` **191.34 kB** minified
(gzip 63.40 kB), a **78.6% smaller initial entry chunk**. Route page chunks are
2.69–11.38 kB; GSAP and ScrollTrigger are separate 70.35 kB and 42.83 kB
chunks. The Three.js chunk remains **742.80 kB** minified (gzip 187.70 kB) and
Vite continues to warn that this asynchronous chunk exceeds 500 kB. The build
is split; total emitted JavaScript is not claimed to be smaller. Animation and
WebGL chunks load after route rendering/device checks and remain an optimization
and performance-review risk.

## Validation

| Command/check | Result |
|---|---|
| `npm.cmd --prefix web run test -- --run` | PASS: 12 files, 163 tests. |
| `npm.cmd --prefix web run build` | PASS: strict `tsc --noEmit` and Vite production build. Bundle sizes above; Three.js chunk warning remains. |
| `$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'; $env:PYTHONPATH = '.'; uv run --locked pytest backend/tests/integration/test_overview_api.py backend/tests/integration/test_dataset_api.py backend/tests/integration/test_cases.py -q` | PASS: 60 tests; one existing Starlette/httpx deprecation warning. |
| Scan `web/` for `.js`, `.jsx`, `.mjs`, `.cjs` files and TypeScript `any` annotations | PASS: no application JavaScript files or `any` annotations. (`index.html` remains the minimal app entry.) |
| Browser review | NOT RUN: browser access host was unavailable; no responsive visual acceptance is claimed. |

No Python or ML files were changed. `.audit-tmp/` was left untouched. No push
was performed.

## Remaining risks and next step

The Three.js chunk remains large and the motion/WebGL presentation has not had
interactive desktop/mobile review. Once browser access is available, review all
six routes at desktop and mobile widths, including keyboard navigation and
reduced-motion fallback.
