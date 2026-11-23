# Remotion product demo — 2026-11-23

## Request and scope

The original request is preserved in `prompts/development/2026-11-23-remotion-product-demo.md`. Created a separate video artifact in the already present, untracked `fraud-demo/` scaffold on branch `feature/frontend`. The nested `fraud-demo/fraud-demo/` scaffold was present on inspection and was not changed. Application code in `web/` and `backend/` was not changed.

Used `remotion-best-practices`, `remotion-create`, `remotion-markup`, `remotion-captions`, `remotion-studio`, plus the referenced composition, multi-scene, timeline, layout and captions guidance. Remotion package version: `4.0.546`; Node observed: `24.21.0`.

## Artifact

- `fraud-demo/src/Root.tsx` registers `FraudLensProductDemo` at 1920 × 1080, 30 fps, 1350 frames (45 seconds).
- `fraud-demo/src/Composition.tsx` has six timed scenes: title (5 s), transaction (7 s), model/score (9 s), RAG/source excerpts (9 s), explanation (8 s), recap (7 s). Frame-driven motion uses Remotion, not CSS animation.
- `fraud-demo/src/data/transactions.json` contains the three transactions from `data/fixtures/cases.json`, deterministic fixture-v1 scores from `docs/decisions/fixture-scoring.md`, a clearly illustrative 0.60 threshold, and two excerpts from the reviewed synthetic corpus (`sim-review.md`, `sim-missing.md`). The video does not call the model, RAG service, or provider; none of the recap counts is a model metric or a legitimacy/fraud finding.
- `fraud-demo/src/basic-captions.element.tsx` is the Remotion Basic Captions element fetched from the official published source and uses `@remotion/captions`. Captions are timed guidance without an audio narration track.
- `fraud-demo/README-demo.md` records sources, limitations and preview instructions. `fraud-demo/.gitignore` excludes the generated bundle.

## Commands and observed results

| Command/action | Result |
| --- | --- |
| `npm.cmd run dev` in `fraud-demo/` | Studio started, built and remained running at `http://localhost:3000`. Final rebuild said `Built in 238ms`. |
| `node -e ...` comparing video JSON with source fixtures and fixture-v1 score rule | `3/3 fixture records and scores match`; exit 0. |
| `npm.cmd run lint` | ESLint and TypeScript passed; exit 0. |
| `npm.cmd run build` | Remotion bundle succeeded; exit 0. |
| `npx.cmd remotion compositions src/index.ts --browser-executable='C:\Program Files\Google\Chrome\Application\chrome.exe'` | Reported `FraudLensProductDemo 30 1920x1080 1350 (45.00 sec)`; exit 0. |
| HTTP GET of `http://127.0.0.1:3000/FraudLensProductDemo` | HTTP 200. |

The `npx.cmd remotion add @remotion/captions` registry request failed with `EACCES` network access. The exact `4.0.546` package was already present in local `node_modules` and the generated lockfile; its direct dependency entry was added to `package.json` and the lockfile root, then lint and bundle passed. Initial composition listing tried to download Remotion's headless shell and failed due network restriction; explicitly selecting installed Chrome resolved the listing check. `Start-Process` browser launch was denied by the environment; a direct Chrome command was launched, but no visible-window confirmation was available to this agent.

## Limits and next step

Studio serves the composition, but no frame render, visual overflow review, full playback inspection, or exported video was performed. The skill says to render only on explicit request; this request asked for a preview, not an export. **Next step:** open the Studio URL and review each scene/caption timing visually; request specific changes or an export if needed. Do not treat this fixture walkthrough as model evaluation.
