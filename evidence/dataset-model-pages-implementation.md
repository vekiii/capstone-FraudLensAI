# Evidence-backed dataset and model pages — implementation record

Date: 2026-11-23. Branch: `feature/frontend`. Scope: the user-provided six-phase page request and subsequent explicit local-commit instruction. This is frontend and documentation work only. No model fit, data preparation, protected record-level label access, evaluator run, backend behavior change, or push occurred. The repository did not expose the attachment's named `frontend-design` skill in this session; the existing `evidence/frontend-design-audit.md` and FraudLens tokens guided presentation. The available Computer Use skill required `node_repl`, which is absent from the enabled tool list, so desktop/mobile screenshot inspection was unavailable; responsive behavior was reviewed from CSS and DOM tests, not visually verified.

## Source findings and page division

The [source audit](../dataset-model-page-source-audit.md) identifies the exact local synthetic IBM HI-Small source SHA-256, T246 label-free EDA summary, final day-based research split, accepted unweighted LightGBM, and one authorized T230 aggregate test report. `/eda` and `/dataset-overview` remain aliases of a single live, bounded EDA dashboard. `/data` is a separate research explanation using approved, static aggregate evidence; it does not claim the current server is in model mode. The old Feature 005 showcase JSON remains unchanged for other pages.

## Source-to-UI mapping

| Displayed information | UI location | Authoritative source |
| --- | --- | --- |
| Dataset name, synthetic origin, unknown upstream release/acquisition/timezone and project UTC convention | `/data` source section; `/eda` loaded-state note | `original_idea.md` §3; `specs/002-data-and-risk-scoring/protocol.md` T203/T212; T246 evidence |
| Exact local CSV SHA-256 `b19d39f5…` | `/data` identity disclosure; `/eda` runtime summary source identity | Frozen protocol and T246 independently pinned API summary |
| 5,078,345 accepted, zero rejected, 1,114,921 warm-up, 3,963,424 scoreable, full-source UTC coverage | `/eda` cards and source/quality details; `/data` source explanation for accepted/rejected | `evidence/tasks/T246-full-source-eda-2026-11-21.md`; `/api/eda/summary` runtime data. `/data` is pinned to the recorded copy. |
| EDA quality counts, category/time series, currency-side amount totals, 12+12 visible and omitted counts | `/eda` tables, bars, disclosures and limits | Same runtime API; `specs/002-data-and-risk-scoring/contracts/api.md` bounds. No client-side record aggregation. |
| Eleven exact feature names, 24-hour strict-prior rule, train-only categorical vocabulary, 32 matrix columns | `/data` pipeline/feature/model sections | `backend/src/fraudlens/data/features.py`; `backend/src/fraudlens/training/local_run.py`; `evidence/tasks/T229-unweighted-freeze-export-2026-11-20.md` |
| Final train/validation/test row and class counts, UTC day coverage, 62.03/25.61/12.36 shares | `/data` split bar and table | Approved FR-021 protocol and `specs/002-data-and-risk-scoring/protocol.md` research split; denominator 1,884,981 scoreable development rows. Historical T218 70/15/15 figures are excluded. |
| Final model family/configuration, unweighted policy, threshold, native SHA-256 | `/data` selected-model section | T228 diagnostic, T224 comparison, T229 freeze, T231 local-application acceptance |
| Validation and test confusion cells, alerts, precision/recall/F1, AP, ROC AUC, Brier and whole-partition P@20/50/100 | `/data` metric bars, comparison table and confusion cards | `evidence/tasks/T230-snapshot-completion-and-evaluation-2026-11-21.md`, report SHA-256 `5027dae9354796718a080086a6cadc0319d1b376336ad4dac8d93b4e534d9cdb`; same model and threshold for both partitions. UI source values are centralized in `web/src/model-evidence.ts`. |

The split table percentages and displayed metric percentages are deterministic formatting of the sourced row counts and exact metric values. The metric bars use a 0–100% scale and have a numeric table equivalent. The EDA quality bar uses API counts and has an explicit accessible label. Each EDA series retains its unit, transaction denominator, caption, table values, and a decorative bar hidden from assistive technology. Amounts remain separate by currency and paid/received side; shown totals are not individual-amount histograms or cross-currency sums. Currency omissions and possible partial UTC buckets are disclosed.

## Files and behavior

- `web/src/pages/Data.tsx`: replaced outdated showcase placeholders with six evidence-backed sections: source, preparation, frozen split, selected model, authorized evaluation, and limits. Adds links to `/eda`.
- `web/src/model-evidence.ts`: centralized approved aggregate-only model and split values plus final eleven-feature catalog. No record-level labels or source rows.
- `web/src/scoring/views.ts`: retained existing closed API data path and loading/empty/unavailable/error/retry handling; added summary cards, quality breakdown, readable number formatting, more precise amount labeling, limits and a link to `/data`. Removed duplicate site navigation inside `SiteFrame`.
- `web/src/styles/site.css`: layout and responsive styles for both pages using existing tokens; tables scroll horizontally when needed.
- `web/src/pages/pages.test.tsx`, `web/tests/eda-ui.test.ts`, `web/tests/model-evidence.test.tsx`: adjusted legacy showcase assertions; checked route alias, single navigation, exact feature order, aggregate arithmetic, rendering and existing EDA state behavior.
- `evidence/dataset-model-page-source-audit.md` and this record: source and execution evidence.

## Verification observations

1. Initial full frontend run after implementation: **286 passed / 4 failed**. The failures were prior test expectations requiring the old EDA title/home subnavigation and a `/data` “Not yet measured” placeholder. They directly concerned the requested presentation change; assertions were updated to the new behavior.
2. Focused page suite after updates: **10 passed / 10** across the EDA UI, showcase page, and new model-evidence files. React SSR `useLayoutEffect` and asynchronous `act` warnings appeared in test output; tests exited 0.
3. Full frontend `npm.cmd --prefix web run test -- --run --reporter=dot`: **293 passed / 293**, 20 test files, exit 0. The same React test warnings appeared. This includes existing scoring, investigation, simulation, RAG, API and EDA contract cases.
4. `npm.cmd --prefix web run build`: TypeScript typecheck and Vite build passed, exit 0. Existing three.js chunk-size warning remained; no build failure.
5. `git diff --check`: passed with a Git LF/CRLF notice on `Data.tsx`; no whitespace error. Only the listed frontend files and two evidence files were intended for staging. Unrelated pre-existing ZIPs and `~/` were excluded.

The ignored local T230 aggregate report and T246 EDA summary were absent in this checkout, so source-to-display checks use the reviewed, committed aggregate evidence and arithmetic checks; no frozen report hash was revalidated locally. The current fixture-mode server has no configured EDA summary, so its `/eda` loaded state was verified by synthetic contract/UI tests rather than a current live 200 response. Browser screenshots at desktop/mobile widths were not obtained because the available Windows Computer Use integration lacks its required `node_repl` tool in this session. This is the remaining visual-review limitation, not a failed functional check.

## Pending human review

Review the updated `/data` narrative against the frozen report and inspect `/data` and `/eda` at desktop/mobile sizes in a browser. The pages make no production or real-world efficacy claim. Historical Feature 005 showcase JSON remains stale by design and outside this request; its content on other routes was not relabeled as measured.
