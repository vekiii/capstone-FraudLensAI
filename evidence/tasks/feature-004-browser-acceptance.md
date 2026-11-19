# T020 — Feature 004 browser acceptance

**Status** Complete. The independent teammate walkthrough passed SC-004 on 2026-11-19 (Europe/Belgrade). [Quickstart](../../specs/004-simulation-and-prioritization/quickstart.md#browser-walkthrough-for-sc-004) · [Walkthrough request](../../prompts/development/004-simulation-phase-06.md#manual-walkthrough-request)

## Independent teammate walkthrough, 2026-11-19 (Europe/Belgrade)

- **Reviewer** Milan Gavrić (`milangavric2003`) confirmed he performed the walkthrough as a teammate independently of implementation. Observations are from his terminal output, browser screenshots, captured comparison response and written confirmations.
- **Revision** `3c9b3446d799eadce412d4b77a4560adcaf836ef` on `004-simulation-and-prioritization`, with a clean worktree at startup.
- **Tools** Windows, Chrome `157.0.8103.79` Stable 64-bit, Node `24.20.0`, npm `11.19.0`, Vite `8.3.8`, uv `0.10.9`, CPython `3.14.7` and Uvicorn `0.54.0`. Frontend and browser versions came from the reviewer. The backend versions were verified from the local executable and virtual environment used for startup.
- **Settings** `review-capacity-demo` v1, SHA-256 `894136f422d013cf0d1d52820acf26e3a3a95076a4b8ab044c4e24faf4105198`, threshold `0.30` (canonical `0.3`), and budgets `2` then `4` minutes per window. All three strategies were at version 1. The browser showed `bundled_synthetic / authored-v1`, `fixture / illustrative_score / illustrative-v1`, the UTC horizon, equal unit weights and whole-minute costs.

The reviewer ran these commands in separate PowerShell terminals from the repository root. The first `uv` invocation failed because it was absent from `PATH`. The local `uv.exe` and workspace cache were used to start the backend in fixture mode.

```powershell
$uvTool = '.\.cache\004-phase06-tools\uv.exe'
$env:UV_CACHE_DIR = Join-Path $PWD '.cache\uv'
$env:APP_MODE = 'fixture'
& $uvTool run --locked --offline uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8000
```

```powershell
npm.cmd --prefix frontend run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Uvicorn reported startup complete. Vite reported ready and the app loaded three fixture cases at `http://127.0.0.1:5173`.

| Strategy | Reviewed at 2 → 4 minutes | Positives found | Final backlog |
| --- | --- | --- | --- |
| FIFO | `A` → `A,B` | 0 → 1 | 3 → 2 |
| Highest score | `B` → `B,C,E` | 1 → 2 | 3 → 1 |
| Weighted score per minute | `C,E` → `C,E,B` | 1 → 2 | 2 → 1 |

At budget 2, the full table matched the hand-calculated quickstart results. At both budgets the weighted candidate rank was `C,E,B,A`. The expanded window showed the score source and assumptions. C and E both had score `0.80`, weight `1`, duration `1` minute and the same availability timestamp. The stable ID tie-break placed C first. The reviewer explained the effect of the budget change in his own words:

> Kad sam povećao budžet sa 2 na 4 minuta, svaka strategija je pronašla po jedan pozitivan slučaj više, a u zaostatku je ostalo manje slučajeva.

The reviewer downloaded `simulation-recipe-review-capacity-demo-v1.json`, refreshed the app and reopened the same file. The rerun restored threshold `0.30`, budget `4`, the same table and weighted order. The weighted strategy reviewed `C,E,B` in 4 of 4 minutes with `A` pending. Chrome DevTools showed HTTP `200 OK` and measured `10.28 ms` for the budget-4 comparison and `13.94 ms` for the recipe rerun. Both timings are HTTP request durations. Budget-2 latency and total walkthrough elapsed time were unmeasured.

The recipe picker rejected `frontend/package.json`, a JSON document with an invalid recipe structure, with the message “Recept nije ispravan. Izaberite JSON recept za simulaciju (ugovor v1).” The previous table cleared. Returning to Cases opened `CASE-001` and showed `TX-001`, score `0.75 / 1`, source `fixture` and version `fixture-v1`. The back control returned to the three-case list. The walkthrough used bundled synthetic replay data.

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
