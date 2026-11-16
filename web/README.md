# FraudLens showcase

Local-only showcase work for Feature 005 T057 and the data-independent part of T058. Start it with `npm.cmd --prefix web run dev`; Vite binds to `127.0.0.1:5174` (`--strictPort`). Four local routes are `/`, `/data`, `/rag` and `/live`.

The site only consumes JSON files under `public/data/`. Metric, EDA, explanation, corpus and RAG evaluation values are explicitly `Not yet measured`. The live route uses illustrative examples, each labelled `ILLUSTRATIVE, not model output`, and retains that fallback when the read-only API is unavailable. A reachable API is not consumed until T055 supplies an approved adapter. No external LLM or real data call is made.

## Dependencies and licences

Exact direct versions are pinned in `package.json` and `package-lock.json`.

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

Typography uses local system fallback stacks naming Inter Tight, Instrument Sans and Space Mono. No font files or remote font requests are included. GSAP SplitText is not used.

## Checks

```powershell
npm.cmd --prefix web run test -- --run
npm.cmd --prefix web run typecheck
npm.cmd --prefix web run build
```
