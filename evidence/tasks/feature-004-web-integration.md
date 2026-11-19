# Feature 04 React integration

- Date: 2026-11-19.
- Local branch: `integration/004-simulation-web` from Feature 05 at `1401889`.
- Feature 04 source: `45a375f`.
- [Original request](../../prompts/development/004-simulation-web-integration.md).

## Scope

The React router and site navigation expose `/simulation`. The React page mounts and disposes the verified Feature 04 view and uses the site's theme. The existing API router, synthetic scenario and relevant tests are carried over from Feature 04. Frontend and backend run from the same checkout.

## Observed checks

- `npm.cmd --prefix web run test -- --run`: 205 passed. `npm.cmd --prefix web run build`: typecheck and production build passed, with a warning for the Three.js chunk size.
- Targeted pytest via `uv run --locked --offline python -m pytest`: 160 passed across simulation contracts, replay, simulation API, Cases, dataset API and Overview API. `ruff check backend` passed.
- HTTP on the normal FastAPI entry point returned the bundled catalog and expected budget-4 review orders, `A,B`, `B,C,E` and `C,E,B`. Cases returned three fixture rows. The Vite proxy returned the same simulation catalog.
- Headless Chrome opened the React site, followed its Simulation navigation link, ran the default and four-minute budgets, and checked the expected selection changes. It then followed Cases and confirmed the simulation view unmounted and `CASE-001` was visible. The existing imported frontend tests also cover recipe download, reopen and invalid files.
- The full backend suite reported 830 passed, 24 skipped, 72 failed and 4 errors. The failures were outside the simulation tests, including unimplemented Feature 05 security and pretrained-model behavior, missing local model artifacts and Windows symlink permissions. Full backend acceptance remains pending on the shared base.

The Feature 02 score adapter and the Feature 03 React integration are separate work. No commit, push or merge to `main` was performed.
