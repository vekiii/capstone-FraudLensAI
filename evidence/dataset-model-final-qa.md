# Dataset and model pages: targeted correction and final QA

**Date:** 2026-11-23
**Base commit:** `1ac73c11de3436e2a9c37daa2b4cb5bf3caaaa26`
**Scope:** confirmed P0/P1 findings in `/eda`, `/dataset-overview`, and `/data` from the [visual audit](dataset-model-visual-audit.md) and [source verification](dataset-model-verification.md).

## Disposition

The audits confirmed one P1 defect and no P0 defect or dataset/model figure mismatch. V01, populated EDA horizontal overflow, is fixed. V02, V03, and S01-S03 are P2 findings or suggestions and remain unchanged under this task's scope. No unverifiable issue was converted into an implementation change.

| Finding | Before | Correction | After |
|---|---|---|---|
| V01, long source SHA expands the EDA page | Playwright document widths for `/eda` with a populated contract response: 628 px at a 320 px viewport, 628 at 375, and 846 at 768. The initial overflow assertion exited 1 as expected. | In `web/src/styles/site.css`, constrain only `.eda-dashboard .fields` children with `min-width: 0` and allow definition values to wrap with `overflow-wrap: anywhere`. | `/eda` and `/dataset-overview` both have document width equal to viewport at 320, 375, 768, 1024, and 1440 px. The full 64-character hash remains in the DOM and its field box stays in the viewport. |

## Exact files changed

- `web/src/styles/site.css`: two scoped CSS declarations for V01.
- `evidence/dataset-model-final-qa.md`: this execution record.
- `evidence/dataset-model-final-qa/eda-{320,375,768,1024,1440}.png`: post-fix Playwright captures of the populated EDA route.
- `next_work.md`: current handoff, results, and next step.
- The already completed `evidence/dataset-model-visual-audit.md`, `evidence/dataset-model-verification.md`, and `evidence/dataset-model-visual-audit/*.png` are included as the Task 1/2 inputs and before-fix evidence for this correction. Only Markdown trailing whitespace was cleaned from the two reports during Task 3.

## Browser verification

Playwright 1.61.1 launched local Chrome 158 against the running Vite site at `http://127.0.0.1:5173`. For both EDA routes, the browser intercepted only `GET /api/eda/summary` with a two-row, four-series synthetic contract fixture matching the structure in `web/tests/eda-ui.test.ts`; its bank label was `Bank A`. This is a rendering fixture, not a live full-source aggregate. `/data` loaded without interception. At each width, the probe awaited the page and fonts, measured `document.documentElement.scrollWidth` and `window.innerWidth`, checked a single `h1`, and checked the SHA field's visibility and exact text on EDA routes. It exited 0.

| Viewport | `/eda` document | Alias document | `/data` document | EDA screenshot |
|---:|---:|---:|---:|---|
| 320 px | 320 px | 320 px | 320 px | [320](dataset-model-final-qa/eda-320.png) |
| 375 px | 375 px | 375 px | 375 px | [375](dataset-model-final-qa/eda-375.png) |
| 768 px | 768 px | 768 px | 768 px | [768](dataset-model-final-qa/eda-768.png) |
| 1024 px | 1024 px | 1024 px | 1024 px | [1024](dataset-model-final-qa/eda-1024.png) |
| 1440 px | 1440 px | 1440 px | 1440 px | [1440](dataset-model-final-qa/eda-1440.png) |

The `/data` tables retained internal horizontal scrolling at 320, 375, and 768 px. The browser probe found one `h1` on each route. Task 1's [before screenshot at 320 px](dataset-model-visual-audit/eda-mock-320.png) shows the SHA pushing the page; the [after screenshot](dataset-model-final-qa/eda-320.png) shows it wrapping within the EDA field. No browser check of a real full-source populated response was possible because the configured fixture backend returns 404 `dataset_unavailable` for `/api/eda/summary`.

## Commands and results

| Check | Result |
|---|---|
| Pre-fix Playwright overflow assertion on populated `/eda`, widths 320/375/768/1024/1440 | **Expected RED, exit 1.** Document widths 628/628/846/1024/1440 px. |
| Post-fix Playwright responsive probe on `/eda`, `/dataset-overview`, `/data` at all five widths | **PASS, exit 0.** Fifteen route/width combinations; no document overflow; complete SHA field on both EDA routes. |
| `npm.cmd test -- --run` from `web/` | **PASS:** 293 tests in 20 files. |
| `npm.cmd run build` from `web/` | **PASS:** `tsc --noEmit` and Vite production build. The existing large three.js chunk warning remains. |
| `git diff --quiet HEAD -- web/src/model-evidence.ts web/src/pages/Data.tsx web/src/scoring/views.ts web/src/scoring/contracts.ts backend/src/fraudlens/eda specs/002-data-and-risk-scoring/contracts/api.md` | **PASS:** no changes to model evidence, page claims, EDA contract/view, backend EDA, or API contract. |
| `git diff --check` | **PASS.** |

The first PowerShell `npm` invocation did not start tests or build because local execution policy blocks `npm.ps1`; rerunning through `npm.cmd` produced the passing results above. Task 2 independently checked all displayed frozen figures against the authoritative aggregate records and ran EDA/temporal backend tests. With no value, denominator, model, or API code changed in Task 3, that source consistency remains applicable. No model training, evaluation, artifact edit, dataset read, or API behavior change occurred.

## Remaining issues and limitations

- P2 V02/V03 and suggestions S01-S03 remain as recorded in the visual audit; none blocks the verified P1 fix.
- The configured local backend is in fixture mode and does not serve a hash-pinned full-source EDA summary. A live populated-data browser review remains blocked; the browser result above covers the contract fixture and responsive behavior.
- Task 2 records a separate approximate percentage inconsistency in the research protocol prose. The `/data` page uses the correct exact counts and calculated shares; protocol prose is outside this correction scope.

**Disposition:** V01 is fixed and verified. ML artifacts, approved evaluation figures, EDA API contracts, and backend behavior remain unchanged.
