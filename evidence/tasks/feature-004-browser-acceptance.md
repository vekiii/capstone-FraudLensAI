# T020 — Feature 004 browser acceptance

**Status** Pending an independent teammate walkthrough for SC-004. On 2026-11-19 the requester confirmed that the walkthrough had yet to take place. Reviewer identity, independently executed revision and tool versions, timings and observed results are pending.

## Automated walkthrough, 2026-11-19 (Europe/Belgrade)

- **Revision** `a0dfa5e6a8ccc117afe432e9c056549d41b6aec9` on `004-simulation-and-prioritization`.
- **Tools** Windows, CPython 3.14.7, uv 0.10.9, Uvicorn 0.54.0, Node 24.20.0, Vite 8.3.8 and Chrome 157.0.8103.79.
- **Settings** `review-capacity-demo` v1, digest `894136f422d013cf0d1d52820acf26e3a3a95076a4b8ab044c4e24faf4105198`, threshold `0.3`, budget `2` then `4` minutes per window, each strategy at version 1.
- **Command** `node .cache/004-phase06-browser.mjs` from the repo root, exit 0. The local verifier used an isolated Chrome profile, `uv run --locked --offline uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8000` and `node frontend/node_modules/vite/bin/vite.js frontend --config frontend/vite.config.ts --host 127.0.0.1 --port 5173 --strictPort` in fixture mode. All 16 groups passed and owned processes were stopped. [Observed checkpoint results](feature-004-phase-06-browser-results.json)

| Strategy | Reviewed at 2 → 4 minutes | Positives found | Final backlog |
| --- | --- | --- | --- |
| FIFO | `A` → `A,B` | 0 → 1 | 3 → 2 |
| Highest score | `B` → `B,C,E` | 1 → 2 | 3 → 1 |
| Weighted score per minute | `C,E` → `C,E,B` | 1 → 2 | 2 → 1 |

At budget 2, Chrome showed the hand-calculated default counts in 63 ms. At budget 4, the weighted window showed ranked `C,E,B,A` and reviewed `C,E,B`, along with source, score, weight, minutes and assumptions. Chrome downloaded the actual JSON, refreshed the app and reopened the same file. The comparison and subsequent window inspection matched the previous results in 66 ms. These are single local timings. An unavailable strategy version returned HTTP 409 and required explicit resubmission. Malformed JSON produced a readable error with no results. Cases remained the default view, with detail and back navigation working after the simulation and direct/proxy 404/422 checks passing.

## Pending independent record

The [quickstart walkthrough](../../specs/004-simulation-and-prioritization/quickstart.md#browser-walkthrough-for-sc-004) is ready for a teammate. The resulting record needs the teammate's name, tested revision and versions, scenario digest and settings, observed turnaround, the budget change and its effect on positives and backlog, the recipe rerun and the error and Cases checks.
