# Feature 005 T057 — showcase foundation and motion

**Status:** DONE for the locally authorized showcase foundation. The broader T047 RAG/provider/corpus decisions remain open; no RAG service or hosted deployment was started.

Implemented the standalone `web/` React + TypeScript + Vite app, 32-column responsive grid and design tokens, shared navigation/footer, declarative GSAP reveal presets, Lenis/ScrollTrigger synchronization and anchor scrolling, split rules, mask reveal, reduced-motion/low-power WebGL fallback, one fixed three.js canvas with pixel ratio capped at 2, scroll-story motion, and route transitions. Dependency versions and licences are listed in `web/README.md`; exact versions are locked in `web/package-lock.json`. React Router was updated to 7.18.5 after the first npm audit identified advisories in the initially pinned v6 range. Final `npm audit` reports zero vulnerabilities.

## Commands and observed results

| Command | Result |
|---|---|
| `node --version` | `v24.21.0` |
| `npm.cmd --version` | `11.19.0` |
| `npm.cmd install --package-lock-only --ignore-scripts` | Exit 0; locked exact pins. |
| `npm.cmd ci` | Exit 0; 91 packages installed; 0 vulnerabilities. |
| `npm.cmd audit --audit-level=moderate` | Exit 0; 0 vulnerabilities. |
| `npm.cmd --prefix web run test -- --run` | Exit 0; 3 files, 9 tests passed. Covers reveal presets, reduced motion, WebGL fallback, public data provenance, illustrative labels and API fallback. |
| `npm.cmd --prefix web run typecheck` | Exit 0. |
| `npm.cmd --prefix web run build` | Exit 0. Vite emitted a 860.80 kB minified entry-chunk warning (>500 kB); this size has not been optimized or presented as a performance result. |

An initial test run exposed a missing `matchMedia` setup in jsdom and an initial typecheck needed CSS/three declarations; the harness and pinned type declarations were added. The initial router pin surfaced advisories and was upgraded to the patched major with React 18-compatible peer requirements; final audit is clean.

Visual QA was not completed: the computer-use browser host was unavailable in this environment. HTTP checks returned 200 for `/`, `/data`, `/rag` and `/live`; this is route-serving verification, not a browser layout/accessibility measurement.
