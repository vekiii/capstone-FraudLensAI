# Evidence-backed RAG page implementation — 2026-11-23

## Scope and sources

Updated only the /rag presentation, scoped styles, and focused page assertions. The supporting review is in [rag-page-source-audit.md](rag-page-source-audit.md). No backend, corpus, model, API, or provider behavior changed. The requested frontend-design skill was not installed in the available catalog.

## What the page now explains

1. Risk scoring, procedure retrieval, AI report drafting, and analyst authority as distinct responsibilities.
2. A responsive case/history branch and procedure-search branch joined into saved evidence, report drafting, validation, and analyst review. The three real tool identifiers, 1–500 character procedure query, five-passage bound, and explicit no_match are shown.
3. The reviewed six-English-document/six-selected-passage corpus, grouped as three simulated guides, one IBM dataset guide, and two historical US FinCEN sources. Provenance, review, hash, named-section extraction, 2,400-character chunking, versioned identities, and SQLite archiving are described.
4. Local BM25 (k1=1.2, b=0.75, cutoff, deterministic ordering) and separately enabled OpenAI semantic selection, each with its correct API method and path.
5. Structured report inputs and fields, citation validation, and the limit of syntactic checks.
6. Retrieval metrics in separate experiment panels. Original multilingual BM25 **0.50 Recall@5 / 0.50 MRR@5 / 4/4 no-answer** come from evidence/tasks/feature-003-automated-evaluation.md:140–141. Later English semantic v6 **0.864583 / 0.9375 / 4/4**, 20 questions and one provider failure counted zero come from evidence/tasks/feature-003-v6-integration-judge-20261117.md:62–84. These are explicitly labeled different evaluations.
7. Report-quality outcomes separately: original **0/8**, with six no-report cases (feature-003-automated-evaluation.md:113–141); v8 development **3/4** locally valid with failed gate and no held-out promotion (feature-003-v8-development-20261118.md:40–50); final-live judge calibration **2/3** and unaccepted raw ratings (feature-003-final-live-v8.md:75–85).
8. Limits: synthetic data, small corpus, historical jurisdiction, optional provider, citation interpretation, unaccepted report quality, and final human responsibility.

The local data/processed/investigations.sqlite archive was absent on 2026-11-23. The page distinguishes recorded publication from current runtime availability and makes no live-provider claim.

## Files

- web/src/pages/Rag.tsx: evidence-backed content and semantic section structure.
- web/src/styles/site.css: page-scoped responsive layout in existing dark/lime tokens.
- web/src/pages/pages.test.tsx: focused labels, endpoints, tool IDs, results, and removal of stale proposed-state expectation.
- evidence/rag-page-source-audit.md: authoritative source review.
- evidence/rag-page-screenshots/rag-{320,375,768,1024,1440}.png: actual Chrome screenshots.

## Verification

- RED: npm.cmd test -- --run src/pages/pages.test.tsx failed two assertions against the original placeholder page, as intended.
- GREEN: the focused test passed after implementation.
- npm.cmd test -- --run: **20 files / 293 tests passed**.
- npm.cmd run typecheck: **passed**.
- npm.cmd run build: **passed**. Vite reported an existing large three.module chunk warning; no build error.
- Real Chrome via Playwright at **320, 375, 768, 1024, 1440 px**: /rag loaded, seven section headings and navigation present, no page errors. Document width equaled viewport width at every size after fixing a 12 px mobile pseudo-element overflow. Reduced-motion media preference was active; the in-page pipeline link was present and focusable by native anchor semantics. Screenshot captures are listed above.

## Remaining limits

Browser checks inspected page structure and layout, not a running knowledge API or report workflow. The generated local corpus archive is missing, semantic retrieval defaults off, and no new RAG evaluation or provider call was made. Historical evaluation cannot establish deployed report quality. Full-page screenshots were visually reviewed at 320 and 1440 px.
