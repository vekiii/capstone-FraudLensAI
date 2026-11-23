# Dataset and model pages: visual and responsive audit

**Date:** 2026-11-23
**Reviewed commit:** `1ac73c11de3436e2a9c37daa2b4cb5bf3caaaa26` (`feature/frontend`)
**Scope:** `/eda`, `/dataset-overview`, `/data`, `SiteFrame`, and relevant CSS. This is a read-only audit; no frontend, API, dependency, test, or model change was made.

## Method and limits

- Read `AGENTS.md`, `next_work.md`, the constitution, Feature 002 EDA requirements FR-035–038, API contract, and relevant page, frame, CSS, and UI test sources. No `frontend-design` skill is installed in the available skill catalog or repository skill files.
- Used **Playwright 1.61.1** with locally installed **Chrome 158.0.8127.36** against `http://127.0.0.1:5173`. Playwright set and confirmed actual CSS viewports of **320, 375, 768, 1024, and 1440 px**. Screenshots use full-page capture and reduced motion. This avoids Chrome CLI's 504 px minimum-layout-viewport screenshot artifact observed in an earlier informal review.
- Inspected `/data`, the locally served `/eda` unavailable state, and browser-intercepted populated EDA responses on `/eda` and `/dataset-overview` at every requested width. The populated mock is the **two-row synthetic contract fixture** from `web/tests/eda-ui.test.ts`, with bank, UTC-count, paid-USD, and received-EUR series. It verifies rendering and responsiveness, **not** full-source values or the live loaded state.
- Also captured mocked empty, pending/loading, HTTP 500, and malformed-response states at 320 px. The local `/api/eda/summary` was unavailable (404); its hash-pinned full-source summary was absent. Populated live-data rendering and data-dependent chart density remain unverified.
- Browser probes measured `window.innerWidth`, `document.documentElement.scrollWidth`, table container widths, heading/navigation counts, keyboard Tab focus outlines, menu opening with Enter, and horizontal table scrolling. No automated accessibility certification or full contrast audit was run.

## Confirmed defects

### V01 — P1: populated EDA overflows the page horizontally

- **Routes / viewports:** `/eda` and `/dataset-overview` at 320, 375, and 768 px, with the populated contract mock.
- **Screenshots:** [320 px EDA](dataset-model-visual-audit/eda-mock-320.png), [375 px EDA](dataset-model-visual-audit/eda-mock-375.png), [768 px EDA](dataset-model-visual-audit/eda-mock-768.png). The alias screenshots show the same behavior.
- **Affected files/components:** `web/src/scoring/views.ts`, `fields()` / `createEdaView()` source SHA field; `web/src/styles/site.css` `.fields > div`, `.fields dd` and narrow-screen rules.
- **Observed:** The unbroken 64-character `source_sha256` expands the `.fields` grid. Browser-measured document widths were **628 px at 320 px**, **628 px at 375 px**, and **846 px at 768 px**. The 320 px source-hash definition term/value extended to x=628; at 768 px the hash text exceeded its grid cell. The unavailable state and `/data` had no document-level overflow at those widths. At 1024 and 1440 px, populated EDA stayed within the viewport.
- **Recommended minimal fix:** Constrain `.fields` grid children with `min-width: 0` and wrap long field values with `overflow-wrap: anywhere` (or an equivalent scoped rule). Keep the hash visible and copyable.
- **Expected acceptance criteria:** With a 64-character source SHA and populated EDA, `document.documentElement.scrollWidth <= window.innerWidth` at all five requested widths; the full hash remains readable without clipping; internal series tables can still scroll within their own containers.

### V02 — P2: alias route has no active navigation indication

- **Route / viewport:** `/dataset-overview` at 1024 and 1440 px; the same shared navigation state applies at the other widths when the menu is opened.
- **Screenshot:** [alias at 1440 px](dataset-model-visual-audit/alias-mock-1440.png), compared with [/eda at 1440 px](dataset-model-visual-audit/eda-mock-1440.png).
- **Affected file/component:** `web/src/components/SiteFrame.tsx`, navigation active-state calculation for the `/eda` link.
- **Observed:** Both URLs render the same `Dataset overview` page and populated EDA content. Browser inspection found one active header link (`Dataset overview`) on `/eda` and **zero** active header links on `/dataset-overview`. No duplicate page header or nested navigation was found: each route had one `h1`, one shared header nav, and no nav inside `main`.
- **Recommended minimal fix:** Treat `/dataset-overview` as an alias of `/eda` in the shared active-link calculation.
- **Expected acceptance criteria:** The `Dataset overview` nav item has the same visible active styling and current-page semantics on both URLs; no second nav or heading is introduced.

### V03 — P2: the EDA hero link leaves its arrow on a separate line

- **Route / viewport:** `/eda` and `/dataset-overview` at 320 px, in all captured EDA states.
- **Screenshot:** [320 px empty state](dataset-model-visual-audit/eda-empty-320.png) and [320 px error state](dataset-model-visual-audit/eda-error-320.png).
- **Affected files/components:** `web/src/scoring/views.ts`, hero method link; `web/src/styles/site.css`, `.evidence-link`.
- **Observed:** `Metod, podjela i rezultati modela →` wraps so the arrow occupies a line by itself and the underline spans the full available width. The link remains functional, but its direction cue is visually detached from the label.
- **Recommended minimal fix:** Keep the arrow attached to the final word with a nonbreaking span or equivalent wrap rule, while allowing the preceding words to wrap.
- **Expected acceptance criteria:** At 320 and 375 px, the arrow appears beside the last word, the link stays inside the viewport, and its focus indicator remains visible.

## Design suggestions, not established defects

### S01 — P2: indicate that model tables scroll sideways

- **Route / viewport:** `/data` at 320 and 375 px.
- **Screenshot:** [320 px full page](dataset-model-visual-audit/data-320.png), [375 px full page](dataset-model-visual-audit/data-375.png).
- **Affected files/components:** `web/src/pages/Data.tsx`, `.evidence-table-scroll` tables; `web/src/styles/site.css`.
- **Observed:** The tables are intentionally contained and scrollable, with **no document-level overflow**. At 320 px, the first table container measured 280 px wide with 650 px of content; a Playwright scroll reached the remaining 370 px. No visible cue tells a touch user that later columns exist. This is a discoverability suggestion, not a broken scroll interaction.
- **Recommended minimal fix:** Add a short, visually quiet “Scroll table to see more columns” cue at narrow widths, or a subtle edge fade that does not obscure values.
- **Expected acceptance criteria:** Users can discover the hidden columns at 320/375 px; tables remain keyboard and touch scrollable; the document itself stays within the viewport.

### S02 — P2: make bar segments identifiable without relying on position or color

- **Routes / viewports:** `/data` split bar and populated `/eda` quality bar at all widths.
- **Screenshots:** [data at 1440 px](dataset-model-visual-audit/data-1440.png), [populated EDA at 1440 px](dataset-model-visual-audit/eda-mock-1440.png).
- **Affected files/components:** `web/src/pages/Data.tsx` split bar; `web/src/scoring/views.ts` quality bar; `web/src/styles/site.css` segment colors.
- **Observed:** Both bars have accessible labels, and surrounding tables/text provide counts. The colored segments themselves have no nearby visible legend. A reader must infer their order from the surrounding content. This is a visual interpretation improvement; no missing accessible name was found.
- **Recommended minimal fix:** Add compact labels or a small legend next to each bar, using the same names as the associated counts.
- **Expected acceptance criteria:** Each segment can be identified visually and by assistive technology without color alone; values and denominators remain unchanged.

### S03 — P2: choose one language convention for the paired pages

- **Routes / viewports:** `/data` and `/eda`/`/dataset-overview`, all widths.
- **Screenshots:** [data at 1024 px](dataset-model-visual-audit/data-1024.png), [EDA at 1024 px](dataset-model-visual-audit/eda-mock-1024.png).
- **Affected files/components:** `web/src/pages/Data.tsx` (`lang="en"`); `web/src/scoring/views.ts` (Bosnian/Serbian/Croatian page copy); `web/src/components/SiteFrame.tsx` (English shared navigation).
- **Observed:** Navigation between the paired pages switches language. This may be intentional for the capstone audience; no reviewed specification establishes a single-language requirement, so it is **not classified as a defect**.
- **Recommended minimal fix:** Decide the intended page language with the team, then align the paired page labels and navigation or make the language switch explicit.
- **Expected acceptance criteria:** The chosen language convention is documented and applied consistently to headings, links, charts, and state messages.

## Checks with no confirmed defect

| Check | Observed result |
|---|---|
| `/data` document overflow | None at 320, 375, 768, 1024, or 1440 px. Internal feature/split/metric tables scroll at narrow widths. |
| Live EDA unavailable state | Rendered at all five widths without document overflow; clear message and retry button. |
| Mocked EDA empty/loading/error/malformed states | Rendered at 320 px with distinct messages. Loading set `aria-busy="true"`; HTTP error and malformed responses provided retry. |
| Route alias | `/eda` and `/dataset-overview` both rendered the same EDA page and mock data. Active-nav difference is V02. |
| Heading/navigation duplication | One `h1` and one shared header nav per route; no nested nav inside `main`. |
| Keyboard and focus | Tab reached the wordmark and next control; a visible outline was observed. At 320 px, Enter opened `MENU +`, `aria-expanded` changed to `true`, and the nav became visible. |
| Typography, spacing, palette | Desktop and narrow layouts retained the dark/lime palette, readable section hierarchy, stacked cards, and aligned metric cards. No other verified overlap or clipping was found in the captured states. |

## Screenshot index

All screenshots are browser-generated PNGs in [`evidence/dataset-model-visual-audit/`](dataset-model-visual-audit/). `eda-mock` and `alias-mock` contain the two-row intercepted contract fixture; `eda-live` contains the local 404 unavailable state.

| Viewport | `/data` | `/eda` live | `/eda` populated mock | `/dataset-overview` populated mock |
|---:|---|---|---|---|
| 320 | [data](dataset-model-visual-audit/data-320.png) | [live](dataset-model-visual-audit/eda-live-320.png) | [mock](dataset-model-visual-audit/eda-mock-320.png) | [alias](dataset-model-visual-audit/alias-mock-320.png) |
| 375 | [data](dataset-model-visual-audit/data-375.png) | [live](dataset-model-visual-audit/eda-live-375.png) | [mock](dataset-model-visual-audit/eda-mock-375.png) | [alias](dataset-model-visual-audit/alias-mock-375.png) |
| 768 | [data](dataset-model-visual-audit/data-768.png) | [live](dataset-model-visual-audit/eda-live-768.png) | [mock](dataset-model-visual-audit/eda-mock-768.png) | [alias](dataset-model-visual-audit/alias-mock-768.png) |
| 1024 | [data](dataset-model-visual-audit/data-1024.png) | [live](dataset-model-visual-audit/eda-live-1024.png) | [mock](dataset-model-visual-audit/eda-mock-1024.png) | [alias](dataset-model-visual-audit/alias-mock-1024.png) |
| 1440 | [data](dataset-model-visual-audit/data-1440.png) | [live](dataset-model-visual-audit/eda-live-1440.png) | [mock](dataset-model-visual-audit/eda-mock-1440.png) | [alias](dataset-model-visual-audit/alias-mock-1440.png) |

Additional 320 px state captures: [empty](dataset-model-visual-audit/eda-empty-320.png), [loading](dataset-model-visual-audit/eda-loading-320.png), [HTTP error](dataset-model-visual-audit/eda-error-320.png), [malformed response](dataset-model-visual-audit/eda-malformed-320.png).
