# Feature 005 T058 — site pages, data files and fallback (partial)

**Status:** PARTIAL. All four routes are implemented with contract copy. Values and feature definitions are loaded from `web/public/data/` (`metrics.json`, `eda.json`, `features.json`, `explanations_global.json`, `kb_stats.json`, `rag_eval.json`, `samples.json`); unmeasured values say “Not yet measured”. The `/live` route uses a fixture badge and every sample is labelled `ILLUSTRATIVE, not model output` both in JSON and on screen. The API probe has a bounded timeout and retains local illustrative data when the API is unavailable; even a reachable JSON API is not consumed before T055 defines the approved adapter. There are no write paths or free-text transaction inputs.

This work does not generate real metrics, RAG evaluation results or corpus statistics. T058 remains partial because T054 results and the T055 API integration are not available. No model output or measured quality claim is presented.

## Commands and observed results

| Command | Result |
|---|---|
| `npm.cmd --prefix web run test -- --run` | Exit 0; 3 files, 9 tests passed, including public JSON provenance, all 11 feature definitions, the illustrative disclaimer, and API-down behavior. |
| `npm.cmd --prefix web run typecheck` | Exit 0. |
| `npm.cmd --prefix web run build` | Exit 0; see T057 for the large entry chunk warning. |
| PowerShell `Invoke-WebRequest` for `/`, `/data`, `/rag`, `/live`, and all seven `/data/*.json` sources on `127.0.0.1:5174` | HTTP 200 for every route and source. The metrics file reported `not_yet_measured`; sample file reported `ILLUSTRATIVE, not model output`. |

Browser visual review was unavailable because the local computer-use browser host could not connect. No accessibility or performance score was measured.
