# Contract: Showcase website and RAG verification

**Feature:** 005 · **Tasks:** T047 to T060 · **Covers:** FR-016 to FR-020, NFR-006 to NFR-008, ML-006, ML-007 · **Status:** proposed, subject to open decisions (f) to (j) in [spec.md](../spec.md).

Brand name "FraudLens" is a placeholder. The layout and motion language follow the Topology reference site (structure and behaviour recreated; its copy, logo, imagery and code are not reused).

## 1. Scope and relationship to Feature 005

| Concern | Rule |
|---|---|
| Data | All data is the synthetic IBM-derived dataset. No real transaction data anywhere on the site or in any LLM call. |
| Model | The site describes and shows the existing pinned scikit-learn artifact. It trains nothing and adds no model family. |
| Features | The 11 `history-v1` features from the feature contract. Names and definitions are read from that contract, not retyped here. |
| Authority | A score, an alert decision and a RAG verification are all advisory. Nothing on the site or in the verifier closes, blocks or escalates an account. |
| Live source | `/live` reads the FR-010 read-only API when it exists. Until then it reads fixture and Feature 002 batch results. Every view carries a source badge: `fixture`, `batch` or `live`. |
| Integration fixture | If only the synthetic fixture artifact exists, results must be labelled "integration fixture, not a model evaluation". |
| Numbers | Every figure on the site comes from a generated file in section 12. Nothing is hard-coded. |

## 2. Site map (four routes)

| # | Route | Purpose |
|---|---|---|
| 1 | `/` | Landing: what was built, how the model works, what RAG is, what a RAG call is |
| 2 | `/data` | Dataset description, EDA, features, model and evaluation |
| 3 | `/rag` | RAG deep dive: corpus, retrieval, call, review-priority logic, evaluation, failure modes |
| 4 | `/live` | Working demo: score, explanation and RAG verification side by side |

Header nav on every page: **Overview · Data & Model · RAG · Live demo**. Footer repeats it plus contact and repository link. Out of scope: auth, accounts, CMS, write paths, i18n, blog.

## 3. Tech stack

| Layer | Choice | Why |
|---|---|---|
| Build | Vite + React 18 + TypeScript | Matches the reference's Vite bundle with a React root |
| Routing | React Router with a page-transition wrapper | Reference uses view-based transitions |
| Smooth scroll | Lenis | Reference root uses Lenis |
| Animation | GSAP 3 + ScrollTrigger + SplitText + CustomEase | Reference reveals are GSAP-style transforms with a custom ease |
| Background | three.js (r162 or later), one fixed canvas | Reference background is a fixed three.js canvas |
| Styling | CSS variables + utility classes | Reference uses atomic classes with `@sm/@md/@lg` suffixes |
| Charts | D3 or Recharts in the site palette | EDA and metrics |
| Data | Static JSON (section 12) + read-only API from FR-010 | No new write endpoints |

Hosting is decision (j). Pinned versions are recorded when chosen.

## 4. Design system

### 4.1 Colour tokens

| Token | Value | Use |
|---|---|---|
| `--bg` | `#0B0B0C` | Page background |
| `--text-light` | `#E4E2D8` | Headings, nav, key text |
| `--text-mid` | `#9B9B9B` | Body, secondary labels |
| `--text-dim` | `#5C6670` | Captions |
| `--line` | `rgba(228,226,216,0.25)` | 1 px split borders |
| `--accent` | `#C8FF4D` | Alert flag, active state, key numbers; use sparingly |
| `--danger` | `#FF5A4D` | "RAG supports alert" chip only |
| `--ok` | `#7CE3B0` | "RAG rejects alert" chip only |

The reference is near-monochrome; colour appears only on verdicts and one accent.

### 4.2 Typography

| Role | Reference font | Free substitute |
|---|---|---|
| Display + body | Lazare Grotesk (300/400) | Inter Tight or Instrument Sans |
| Accent label | Magnetik Light | Instrument Serif |
| Mono | Space Mono | Space Mono |

| Style | Size (px, mobile → sm → md) | Line height | Tracking |
|---|---|---|---|
| Hero H1 | 72 → 180 | 0.9 | -0.01em |
| Section H2 | 72 → 100 → 160 | 0.9 | 0 |
| Principle H3 | 54 → 64 | 0.9 | 0 |
| Lead | 24 → 32 (light) | 1.0 to 1.2 | +0.03em |
| Body | 18 → 19 | 1.4 | 0 |
| Label / nav | 14 uppercase | 1 | +0.1em |

Preload main weights and mono; every font has a fallback stack. Original fonts are licensed and are not used.

### 4.3 Spacing and grid

- Spacing scale (px): 6, 8, 12, 16, 20, 24, 30, 32, 40, 80, 96, 120, 160, 240, 350, 540.
- Breakpoints: `xsm` 480, `sm` 768, `md` 1024, `lg` 1280.
- 32-column grid (`--col: calc(100% / 32)`, helpers `w-N-32`, `offset-N-32`). Reference blocks use `11/32` widths with `2/32` and `20/32` offsets.
- Containers: `.container` (centred, max about 1400) and `.container-fluid` (full bleed).
- Dividers are 1 px animated lines. No boxed cards or shadows.

## 5. Shared components

| Component | Spec |
|---|---|
| Header | Fixed, transparent. Logo mark left, four text links right with underline-grow hover. Hidden until the hero intro ends, then fades in; a blurred background layer fades in after first scroll. Under `sm`: two-line burger opens a full-screen menu. |
| Logo | Static SVG wordmark in footer; short looping animated mark in header and About. |
| Split border | 1 px absolutely positioned line (top, right, bottom, left) that scales 0 → 1 on its axis. |
| Section title | H2 split by lines or words for reveal. |
| Numbered row/card | Mono index (`01.`), name, arrow icon that nudges right on hover. |
| Source badge | Pill: `FIXTURE`, `BATCH` or `LIVE`. Always visible on `/live` and on any figure derived from a source. |
| Verification chip | `RAG SUPPORTS`, `RAG REJECTS`, `UNCERTAIN`, `UNAVAILABLE`, `NOT RUN`. |
| Footer | Full-height end block: large wordmark, email, nav, socials, "Back to top". Revealed with a mask. |

## 6. Motion system (build first)

### 6.1 Global rules

- Lenis drives scroll and is synced with ScrollTrigger (`lenis.on('scroll', ScrollTrigger.update)` plus the GSAP ticker).
- `prefers-reduced-motion`: disable WebGL motion, scroll-story pinning and split reveals; use a 200 ms opacity fade.
- Reveals play once (`toggleActions: 'play none none none'`); only the hero and WebGL story are scrubbed.
- WebGL failure or low-power device: static gradient background, story beats become normal sections.

### 6.2 Declarative reveal API

The reference tags elements with `animate-from` (`preset`, `stagger`, `split`, `delay`, `duration`, `ease`). Recreate as `<Reveal preset="fadeUp" split="lines" stagger={0.075} />` or a data attribute plus one initialiser.

| Preset | From state | Duration | Use |
|---|---|---|---|
| `fadeUp` | `y: 40, opacity: 0` | 1.0 s | Paragraphs, labels |
| `fadeRTL` | `x: 100, opacity: 0` | 1.0 to 2.5 s | Section titles, about blocks |
| `fadeLTR` | `x: -100, opacity: 0` | 1.0 to 2.5 s | Mirror of the above |

Options: `split: 'lines' | 'words'`, `stagger` default 0.075, `delay`, `ease`. The reference's custom ease is not public; use `CustomEase.create('soft','0.65,0,0.35,1')`. Trigger start `top 85%`.

### 6.3 Signature motions

| ID | Motion | Trigger | Spec |
|---|---|---|---|
| M1 | Hero intro | Load | Headline lines rise from a mask (0.9 s, stagger 0.1), tagline fades up, footer row last; header appears after. |
| M2 | Hero exit | Scroll 0 to 1 viewport | Hero is `position: fixed`; opacity and `y` scrub to 0 and -60 px. |
| M3 | WebGL scroll story | Scroll through 150dvh spacers | Fixed, centred titles; words enter `x:-50 → 0`, opacity 0 → 1, stagger 0.08; hold; exit. Double soft text-shadow for legibility over the canvas. |
| M4 | Canvas scene | Story progress 0 to 1 | One fixed canvas, `z-index: -1`, `pointer-events: none`. A drifting point field (transactions) where a small cluster turns `--accent` and separates. Progress drives camera dolly and separation. Pixel ratio capped at 2. |
| M5 | Line draw | Enters view | `.split-border` scales 0 → 1 over 0.8 s. |
| M6 | Mask reveal frame | Enters view | Framed block reveals with CSS `mask-size` from `100% 0%` to `100% 100%` over 1.2 s. |
| M7 | Sticky section title | Desktop only | Large title stays pinned while the right-hand list scrolls. |
| M8 | Anchor scroll | Nav click | Lenis `scrollTo`, 3 s same-page, 5 s back-to-home, eased. |
| M9 | Animated arrow | Idle | Down arrow loops a 1.4 s nudge. |
| M10 | Hover | Pointer | Link underline grows left to right (0.3 s); card arrow +6 px; mark brightens. |
| M11 | Page transition | Route change | Outgoing fades and moves up 20 px (300 ms); incoming fades in (400 ms); scroll resets. |

## 7. Page 1: Landing (`/`)

### 7.1 Hero
- **Layout:** full-height fixed, bottom-aligned. H1 left (half width on `lg`), tagline offset 2/32. Footer row with split border: small caps left, "Explore ↓" right.
- **Copy:** H1 "Catch fraud at the edge of the transaction." Tagline "A model flags it. Evidence explains it." Footer "FraudLens ©2026 · Explore".
- **Motion:** M1, M2, M9; Explore uses M8.

### 7.2 WebGL scroll story
- Two beats, each a 150dvh spacer. Beat 1 "Every second, millions swipe..." Beat 2 "...a few are not who they seem." **Motion:** M3, M4.

### 7.3 About: what we built
- **Layout:** centred animated logo, small accent-font label "Why this approach", two-paragraph intro (max width 650), two offset blocks (`11/32` at offsets `2/32` and `20/32`).
- **Intro:** Fraud is rare, costly and adversarial. A score alone is a black box. We pair a pinned model with a retrieval-backed reviewer so each alert arrives with a reason, and every decision stays with a person.
- **Block 01, What we built:** A review queue: a committed transaction is captured, checked, scored against point-in-time history, and shown to an analyst with its provenance.
- **Block 02, How it works:** Change-data capture into a durable log, 24-hour history features, a pinned model artifact, an alert policy kept separate from the score, and an advisory RAG verification that must cite its sources.
- **Motion:** logo loop, `fadeUp` split lines, blocks `fadeRTL`.

### 7.4 How the model was implemented ("Principles" layout)
- **Layout:** sticky title "Model" left; three figures right (H3, lead sentence, note, small-caps caption).
- **Figures:** (1) **History**: 11 features from the prior 24 hours, excluding the transaction itself and equal-time peers; (2) **Score**: a pinned scikit-learn artifact loaded only when its digest matches the approved version; (3) **Policy**: the alert decision is a separate, versioned policy, so retuning it never changes a stored score.
- **Link:** "Dataset and model notes →" to `/data`. **Motion:** M7, `fadeUp` per figure.

### 7.5 What is RAG? ("Team" layout, centred)
- **Layout:** large centred title "RAG", three centred columns with line icons, each a name and two lines.
- **Columns:** **Retrieve** (find relevant fraud typologies and review policy passages), **Augment** (place those passages beside the alert in the prompt), **Generate** (an LLM states support, reject or uncertain and cites the passages).
- **Line:** "The model is not answering from memory. It is reading the evidence we hand it, and its citations are checked."
- **Motion:** title word split, columns `fadeUp`, stagger 0.075.

### 7.6 What is a RAG call? (full-width framed block)
- **Layout:** bordered frame; left a five-step list, right a JSON panel that cross-fades (200 ms) as steps are hovered or scrolled.
- **Steps:** (1) **Build query** from the assessment's features, score, coverage and explanation; (2) **Embed** the query; (3) **Retrieve** top candidates by hybrid search and rerank; (4) **Prompt** with the alert descriptors and retrieved passages; (5) **Validate** the structured verdict and its citations.
- **Motion:** M5, M6. Link to `/rag`.

### 7.7 Results strip ("Supported by" layout)
- Three large numbers between two split borders, read from `metrics.json` and `rag_eval.json`: **PR-AUC**, **recall at fixed alert capacity**, **RAG overturn rate** (with interval). A value that has not been measured shows "Not yet measured". Fixture-artifact values show the integration-fixture label. Accuracy is never shown.
- **Motion:** M6, count-up 1.2 s.

### 7.8 Pipeline grid ("Portfolio" layout)
- 2 columns (4 on `md`) inside a frame, eight numbered tiles `01.` to `08.` with a monochrome mark (via `mask-image`) and top-right arrow: PostgreSQL, Debezium, Kafka-compatible broker, Python worker, scikit-learn, FastAPI, MLflow, Prometheus and Grafana.
- **Motion:** M5 on four borders, M6 on grid, M10 on cards.

### 7.9 Explore ("Public goods" layout)
- Four full-width rows: `01.` Data & EDA, `02.` Model, `03.` RAG, `04.` Live demo; icon, name, right-aligned "Open →". **Motion:** `fadeUp` 1.2 s, M10.

### 7.10 Footer
- M6 mask reveal, then staggered fade of wordmark, nav, email, socials. "Back to top" uses M8.

## 8. Page 2: Data, EDA and model (`/data`)

One long page with a sticky in-page index (desktop).

| Block | Content | Visual |
|---|---|---|
| 8.1 Dataset card | Synthetic IBM-derived transactions: source, size, period, field groups, label definition, licence, limitations (synthetic, no real-world calibration). | Key-value table between split borders |
| 8.2 Class balance | Positive rate from `eda.json`; why accuracy misleads at this rate. | Bar chart, log-scale option |
| 8.3 Amount and time | Amount distribution by label (log x), hourly pattern, currency mix. | Histogram and line |
| 8.4 Features | The 11 `history-v1` features with plain-language definitions from the feature contract; label relationship per feature. | Table and ranked bar |
| 8.5 Point-in-time rules | Prior 24 hours only; self and equal-time peers excluded; warm-up and unavailable coverage; late events held then quarantined (FR-005 to FR-007). | Timeline diagram |
| 8.6 Evaluation protocol | Fixed windows, delayed confirmed labels, capacity metrics (ML-004). State exposure and uncertainty. | Protocol table |
| 8.7 Metrics | PR curve, confusion matrix at the policy threshold, recall at capacity, bootstrap intervals. | Three small charts |
| 8.8 Explanation | The stored explanation per assessment (method named in the serving contract) and how it feeds the RAG query. | Global bars and one local example |

**Motion:** each block `fadeUp`; charts animate once (axes draw with M5, bars grow 0.8 s); static under reduced motion.

## 9. Page 3: RAG (`/rag`)

| Block | Content |
|---|---|
| 9.1 Why RAG here | Analysts need reasons. RAG grounds an advisory verdict in reviewed documents. It verifies and explains; it does not decide. |
| 9.2 Knowledge base | Doc types (typologies, review policies, synthetic case write-ups, glossary), counts, version, licence and reviewer. |
| 9.3 Chunking and embedding | Chunk size and overlap, metadata, embedding model, vector store (decision (g)). |
| 9.4 Retrieval | Hybrid keyword + dense, top 8, rerank to 4, metadata filter; funnel diagram. |
| 9.5 The RAG call | Walk-through with the real record from section 11.4; collapsible panels. |
| 9.6 Review-priority logic | Table below. |
| 9.7 Evaluation | hit@k, citation correctness, verdict agreement, overturn rate with intervals, latency, cost per call. |
| 9.8 Failure modes | Empty retrieval, contradictory evidence, injection attempts, stale corpus, provider outage; each with its guard (section 11.6). |

**9.6 Review-priority suggestion (advisory only):**

| Assessment state | RAG verification | Suggested display |
|---|---|---|
| Alert selected by policy | Supports | Raise review priority |
| Alert selected by policy | Rejects | Keep in queue, mark "RAG disagrees"; never auto-clear |
| Alert selected by policy | Uncertain or unavailable | Normal priority, show state |
| Not alerted | Not run | No verification (saves cost) |
| Warm-up or unavailable coverage | Not run | Show the coverage message; do not score as zero |

**Motion:** funnel draws step by step on scroll (SVG stroke-dashoffset); code panels fade between tabs.

## 10. Page 4: Live demo (`/live`)

Three-column frame under a split-border header, with a persistent **source badge** (`FIXTURE`, `BATCH`, `LIVE`) and the line "All data is synthetic."

1. **Left, picker:** 20 to 30 pre-selected assessments (alerted, not alerted, warm-up, rejected-by-RAG, verifier-unavailable) plus "random". Numbered rows like the grid tiles. No user-typed input.
2. **Centre, pipeline stage:** nodes Transaction → Features and score → RAG verification → Review view, joined by lines; a pulse travels along them on run (1.2 s per hop). Each node expands: coverage and score with explanation; retrieved passages with similarity; verdict, rationale and citations; the review-priority suggestion.
3. **Right, evidence drawer:** full text of each cited passage, the exact prompt (collapsible), version identifiers (model digest, feature and alert-policy version, corpus, embedding model, LLM), latency per stage.

**States:** idle, running (skeleton shimmer), success, API error (clear message and retry; falls back to precomputed results with the badge changed), verification unavailable, RAG not run (explain why).

**Page footer:** aggregate table of review volume with and without RAG priority marks (alerts, supported, rejected, uncertain, unavailable). **Motion:** M5 borders, pulse along lines, count-up numbers, passages stagger 0.075 s.

## 11. RAG verification contract

### 11.1 Knowledge base
- Content: fraud typologies, review policies and synthetic case write-ups authored or licensed for this project (decision (i)). No confidential or real policy text.
- Each document has `doc_id`, `type`, `title`, `source`, `licence`, `version`, `reviewed_by`, `reviewed_on`.
- The corpus is not the transaction table. The synthetic transaction fields give a model little to reason over on their own, so evidence comes from the typologies and policies.

### 11.2 Chunking and index
- 300 to 500 token chunks, about 15% overlap, metadata inherited from the document.
- Build is deterministic for a pinned corpus version, chunker version and embedding model; the build records a `kb_version` and content hash.
- Retrieval: hybrid keyword and dense search, top 8, rerank to 4, optional metadata filter.

### 11.3 Trigger and query
- **Trigger:** a separate verifier process (its own database role) polls committed `alert_decisions` of the active generation where `alert` is true, coverage is full, and no `verification_runs` row exists for the active verification config. It works in `(event_time, transaction_id)` order and reads only committed rows, so it runs after FR-009 commits and never inside the worker's transaction.
- **Query text** is built only from structured descriptors of the persisted feature snapshot, score, coverage and explanation (ML-006). Example shape: "Alert on a {payment format} transaction; {descriptor from feature A}; {descriptor from feature B}; coverage full." Descriptors map feature values to bands defined in the feature contract. No target or confirmed-label field and no free text from any source enters the query or prompt.
- **Prompt rule:** "Use only the provided passages. If they are insufficient, answer uncertain. Cite passage ids."
- Output is forced into a structured schema, validated, and retried once on parse failure.

### 11.4 Verification record

```json
{
  "verification_id": "ver_000123",
  "generation": 7,
  "transaction_id": "tx_000456",
  "case_id": "case_000789",
  "config_id": "vcfg_001",
  "status": "completed",
  "verdict": "support",
  "rationale": "Activity pattern matches the described rapid fan-out typology.",
  "citations": ["kb_typology_017", "kb_policy_004"],
  "retrieved": [{"id": "kb_typology_017", "rank": 1, "score": 0.71}],
  "versions": {"kb": "kb-2026-11-a", "embedding": "pinned-id", "llm": "pinned-id", "prompt": "p1"},
  "latency_ms": {"retrieve": 120, "llm": 940},
  "created_at": "2026-11-16T10:00:00Z"
}
```

- `status`: `completed`, `skipped` (not alerted or coverage not full) or `unavailable` (timeout, provider error, repeated parse failure).
- `verdict`: `support`, `reject` or `uncertain`; absent unless `status` is `completed`.
- No confidence number is stored. LLM self-reported confidence is not calibrated, so the contract does not expose one.
- **Citation rule:** every id in `citations` must appear in `retrieved`. Otherwise the server drops the unknown ids and sets `verdict` to `uncertain`. A `support` or `reject` with no valid citation is also downgraded.
- **Idempotency:** one record per `(generation, transaction_id, config_id)`; a rerun returns the existing record. Approving a new verification config (new corpus, embedding model, LLM or prompt version) creates a new record and leaves the earlier one readable. Verifications are not copied across generations, because their inputs differ.

### 11.5 Storage and API exposure
- Stored in `verification_configs` and `verification_runs` (see the data-model addendum), keyed by `(generation, transaction_id, config_id)`; never written into prediction or alert-decision rows and never read by dbt marts or any feature or training path.
- Exposed as additive fields on `GET /api/live/v1/alerts/{case_id}` (`verification`, `review_priority_suggestion`). `GET /api/live/v1/alerts` carries only `verification.verdict` and `verification.status`. List ordering and the generation-bound cursor stay exactly as in `live-alert-api.md`, and a stale generation still returns the controlled 409. `live-alert-api.md` is updated in T055.
- The site and dashboard have no endpoint that triggers a verification from the browser.

### 11.6 Failure and security rules (NFR-007, NFR-008)

| Risk | Guard |
|---|---|
| Provider outage or slow response | Timeout and one bounded retry; record `status: unavailable`; assessments keep persisting; UI shows "verification unavailable". |
| Empty or weak retrieval | Minimum similarity cut; below it the verdict is `uncertain`. |
| Contradictory evidence | Prompt requires `uncertain` when passages conflict. |
| Prompt injection | Corpus is reviewed; query uses structured descriptors only; no user or free-text fields reach the prompt. |
| Stale corpus | Verification record carries `kb_version`; site shows the version; rebuild is a reviewed change. |
| Data leaving the host | Only synthetic data may be sent; blocked by default until decision (h). |
| Secrets | LLM key held by the verifier role only, never in the browser bundle; separate credential and database role (`verifier`) from producer, connector, worker, label curator, registry operator and the read-only API role. |
| Metrics | Export verification latency, cost, empty-retrieval rate, parse-failure rate, unavailable rate and downgrade count. |

### 11.7 Evaluation (ML-007)
1. Hand-label 50 to 100 alert descriptors with the passages that should be retrieved (labels authored by the team, recorded as such).
2. Report hit@4, MRR, citation correctness and verdict agreement with the labelled expectation. Report agreement with confirmed investigation outcomes only where FR-013 labels exist.
3. Report **overturn rate** (RAG rejecting an alert) and, where labels exist, how many overturned alerts were confirmed fraud. The question for any headline: does verification reduce review effort without discouraging review of true fraud?
4. Show intervals or small-sample warnings. Make no claim about real-world predictive quality.

## 12. Generated data files

| File | Used by | Content |
|---|---|---|
| `metrics.json` | `/`, `/data` | PR-AUC, recall at capacity, confusion matrix, policy version, artifact label (real or integration fixture) |
| `eda.json` | `/data` | Binned distributions, label rates, correlations |
| `features.json` | `/data` | The 11 features with definitions, copied from the feature contract |
| `explanations_global.json` | `/data` | Aggregate explanation contributions |
| `kb_stats.json` | `/rag` | Document counts by type, chunk size, `kb_version` |
| `rag_eval.json` | `/`, `/rag`, `/live` | Retrieval and verdict metrics with intervals |
| `samples.json` | `/live` | Demo assessments with precomputed verification, each with a source label |

Files are produced by notebooks or CLI steps and carry a generation timestamp and source version. Precomputed samples are the fallback when the API is unavailable.

## 13. Repository structure and build order

```
/web
  /src
    /motion      lenis.ts, reveal.ts, scrollStory.ts, splitBorder.ts, maskReveal.ts
    /webgl       scene.ts, points.ts, shaders/
    /components  Header, Footer, Section, SourceBadge, VerificationChip, NumberedRow
    /pages       Landing, Data, Rag, Live
    /styles      tokens.css, grid.css, type.css
  /public/data   metrics.json, eda.json, features.json, ...
/src/rag         kb_build, index, query_builder, verifier, validator
/notebooks       eda, rag_eval
```

Build order (task numbers match Phase 7 in `../tasks.md`):
1. Scope decision (T047), then corpus, tests and index build (T048 to T050).
2. Verification contract tests, verifier, failure isolation (T051 to T053).
3. RAG evaluation set and report (T054).
4. API fields and dashboard evidence panel (T055, T056).
5. Site foundation and motion (T057); this can run in parallel with Phases 2 to 6 once T047 is recorded.
6. Site pages, generated files and fallback (T058).
7. Observability, permissions, quality pass, then acceptance (T059, T060).

## 14. Acceptance checklist

**Behaviour (AC-07)**
- [ ] A verification links to exactly one assessment and never changes its score or alert decision.
- [ ] Every cited id was retrieved; invalid citations downgrade to `uncertain`.
- [ ] With the provider down, assessments still persist and the UI shows "verification unavailable".
- [ ] Verification is not run for non-alerted or non-full-coverage assessments.
- [ ] No target or label field and no free text reaches a query or prompt.

**Site (AC-08)**
- [ ] Four routes render; every number comes from a generated file.
- [ ] Source badge visible on `/live`; works from precomputed data with the API down.
- [ ] "Synthetic data" and "integration fixture" labels appear where applicable.
- [ ] Accuracy is never a headline metric; unmeasured values show "Not yet measured".

**Visual and motion**
- [ ] 32-column grid with the specified offsets.
- [ ] Hero fixed and exits on scroll; WebGL beats scrub smoothly.
- [ ] Split borders draw and framed blocks mask-reveal once.
- [ ] Sticky title pins on desktop only; anchor scroll long and eased; route transitions work.

**Quality (NFR-006)**
- [ ] Mobile Lighthouse performance 85 or higher (proposed target), one canvas, pixel ratio capped.
- [ ] Reduced-motion and keyboard paths work; text contrast meets AA.
- [ ] WebGL failure falls back to a static gradient.

## 15. Risks and gates

| Item | Risk | Default |
|---|---|---|
| Team approval | RAG and site are out-of-course scope | No implementation before decision (f) is recorded with benefit and schedule impact |
| Model availability | Original artifact blocked | Use the labelled integration fixture; never present it as an evaluation |
| Provider and data handling | External LLM call | Blocked until decision (h); synthetic data only |
| Corpus provenance | Licensing or invented authority | Review owner and licence recorded per document (decision (i)) |
| Overstated results | Synthetic data | Persistent footnote; no real-world claims |
| LLM cost and latency | Slow demo or spend | Run only for alerted, full-coverage assessments; cache by version set |
| Font licensing | Legal | Free substitutes in section 4.2 |
| Site placement | Duplicate dashboards | Decision (j) before T055 |

If a gate fails, stop the dependent task and record the blocker; do not relax validation.
