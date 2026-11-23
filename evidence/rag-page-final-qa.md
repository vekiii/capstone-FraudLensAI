# Independent RAG page QA — 2026-11-23

Scope: read-only review of commit c50fc41452b257fcb1918948699f48c7e8e55da1. No application, backend, corpus, model, evaluation, or API files were changed. This report and its screenshots are the only retained outputs of this task. No provider request or new RAG evaluation was made.

## Result matrix

| Check | Result | Evidence and observation |
|---|---|---|
| BM25 versus semantic retrieval | PASS | web/src/pages/Rag.tsx:51–56 shows separate local GET and optional POST panels; backend/src/fraudlens/investigation/retrieval.py:53–57,109–116 and retrieval_semantic_v6.py:20–31,44–70 support the distinction. Neither panel attributes embeddings or a vector database to BM25. |
| Reviewed corpus and provenance | PASS | Rag.tsx:43–48 matches the six manifest documents (data/knowledge/fraudlens-aml-knowledge-v1/manifest.json), recorded six-passage publication (evidence/tasks/feature-003-phase-03-completion.md:11–36), and hash/section/chunk/archive code (backend/src/fraudlens/investigation/knowledge.py:12,68,80–101,112–125). Three simulated, one IBM guide, two historical US FinCEN sources. The page correctly limits jurisdiction. |
| Tool and API contracts | PASS | Rag.tsx:31–39 names get_case_facts, get_account_history, search_procedures, 1–500 query, at most five passages, no_match, server-bound identity. Matches specs/003-ai-investigation/contracts/tools-and-provider.md:5–21. GET and POST methods match backend/src/fraudlens/investigation/api.py:88 and semantic_api.py:86 and specs/003-ai-investigation/contracts/semantic-search-v1.md:3–12. |
| Runtime availability | PASS for wording; BLOCKED for live service verification | Rag.tsx:48 explicitly says the historic archive is absent in this checkout and does not claim a live knowledge API. Independently, Test-Path data/processed/investigations.sqlite returned False. backend/src/fraudlens/investigation/settings.py:14–22 defaults investigation and semantic retrieval off with test provider. A populated live knowledge request was not possible from this evidence. |
| Draft validation and human review | PASS | Rag.tsx:26–28,40,60–62,71–74 labels reports as drafts, validation before review, and analyst authority. Matches .specify/memory/constitution.md principles IV–VI, backend/src/fraudlens/investigation/models.py:171–181 and workflow.py:298–315. It correctly warns that valid citation IDs do not ensure faithful interpretation (specs/003-ai-investigation/evaluation.md). |
| Original multilingual BM25 metrics | PASS | Rag.tsx:65–68 displays Recall@5 0.50, MRR@5 0.50, no-answer 4/4, below target. evidence/tasks/feature-003-retrieval-results.json baseline held_out overall gives 16 answerable, four no-answer, 0.50/0.50 and four correct no-match; feature-003-evaluation.md:187–193 confirms 20 measured searches per configuration. |
| English semantic v6 metrics | PASS | Rag.tsx:65–68 displays 0.864583 Recall@5, 0.9375 MRR@5, 4/4 no-answer, 20 English questions and one provider failure counted zero. evidence/tasks/feature-003-v6-integration-judge-20261117.md:54–90 records 16 answerable/four no-answer, 19 HTTP 200 plus one HTTP 503, automated same-model reference, and numeric-gate pass. The page warns that this is not a controlled head-to-head comparison or live quality claim. |
| Report-quality outcomes | PASS for figures and text | Rag.tsx:71–74 presents 0/8 original pass with six no-report cases (feature-003-automated-evaluation.md:101–141), 3/4 locally valid v8 development with failed gate/no held-out promotion (feature-003-v8-development-20261118.md:33–50), and 2/3 final-live judge calibration with unaccepted favorable raw ratings (feature-003-final-live-v8.md:77–87). Retrieval and report results occupy distinct sections. |
| Browser response and horizontal overflow | PASS | Actual local Chrome via Playwright loaded /rag at 320, 375, 768, 1024, 1440 px. At each width document scrollWidth equaled viewport width (320/320, 375/375, 768/768, 1024/1024, 1440/1440); no JavaScript page errors. The two rag-tinted sections intentionally extend their background into side gutters; their larger scrollWidth did not cause document overflow or clip text. |
| Navigation, headings, focus and motion | PASS | One main h1, seven section headings, no duplicate page title. The pipeline anchor received keyboard Tab focus with a solid 3 px outline at all five widths. The mobile MENU button opened with Space and exposed the RAG link at 320 and 375. Reduced-motion media preference matched and existing web/src/styles/site.css:225–230 suppresses animation. |
| Visual sequence in desktop diagram | FAIL | Confirmed issue QA-1 below. |
| Failed-gate visual semantics | FAIL | Confirmed issue QA-2 below. |
| Frontend regressions | PASS | See commands and results below. |

## Browser viewport observations

| Width | Diagram | Navigation and focus | Overflow | Screenshot |
|---:|---|---|---|---|
| 320 | Branches stack at 280 px; text remains inside cards | Mobile menu opens by Space; jump anchor has visible keyboard focus | None | [320](rag-page-final-qa-screenshots/rag-qa-320.png) |
| 375 | Branches stack at 335 px | Mobile menu opens by Space; focus visible | None | [375](rag-page-final-qa-screenshots/rag-qa-375.png) |
| 768 | Two 342 px branches; tail is parallel (QA-1) | Desktop navigation and focus visible | None | [768](rag-page-final-qa-screenshots/rag-qa-768.png) |
| 1024 | Two 470 px branches; tail is parallel (QA-1) | Desktop navigation and focus visible | None | [1024](rag-page-final-qa-screenshots/rag-qa-1024.png) |
| 1440 | Two 550 px branches; tail is parallel (QA-1) | Desktop navigation and focus visible | None | [1440](rag-page-final-qa-screenshots/rag-qa-1440.png) |

Visual inspection of the full-page 320 and 1440 captures found a clear dark/lime hierarchy, readable method cards, and distinct retrieval and report-quality sections. Body and accent text use the existing high-contrast tokens. Tiny 10 px technical labels are legible at normal browser zoom but may warrant a later accessibility review; no measured contrast failure is claimed. There are no tables or chart legends on this page; metrics use labeled cards.

## Confirmed defects

### QA-1 — P1 — desktop diagram shows sequential stages as parallel

- Route/width: /rag at 768, 1024, and 1440 px.
- Screenshot: [1440](rag-page-final-qa-screenshots/rag-qa-1440.png), architecture section.
- Affected files: web/src/pages/Rag.tsx:40 and web/src/styles/site.css:361–364.
- Observation: Structured AI report draft, Validation, and Analyst review occupy three same-level columns, each with a downward arrow from the evidence assembly row. The diagram therefore reads as three parallel outputs, while the actual workflow and surrounding copy require draft → validation → analyst review.
- Minimal correction: make the tail a single ordered horizontal chain with explicit connecting arrows on desktop; retain the stacked ordered chain on mobile.
- Acceptance: at every viewport, a reader can follow one unambiguous path from evidence assembly through draft, validation, then analyst review.

### QA-2 — P2 — failed report outcomes use success-colored numbers

- Route/width: /rag at all five widths.
- Screenshot: [1440](rag-page-final-qa-screenshots/rag-qa-1440.png), end-to-end quality section.
- Affected files: web/src/pages/Rag.tsx:71–74 and web/src/styles/site.css:394–397.
- Observation: 0/8, 3/4, and 2/3 all appear in the same bright lime used for favorable highlights. The adjacent copy correctly says that the development gate and judge calibration failed, but the first visual read can imply positive results.
- Minimal correction: give the section a neutral or failure status treatment and place a short failed-gate label adjacent to each number. Preserve the brand palette and the exact recorded figures.
- Acceptance: the figures remain readable and each failed or unaccepted status is evident without reading the paragraph below.

## Verification commands and limits

- npm.cmd test -- --run, from web/: PASS, 20 files / 293 tests.
- npm.cmd run typecheck, from web/: PASS.
- npm.cmd run build, from web/: PASS. Vite emitted its existing large three.module chunk warning; no error.
- Playwright using installed local Chrome and the existing Vite server at 127.0.0.1:5173: PASS for page load, responsive width, no page errors, keyboard focus, mobile menu, and reduced-motion preference; FAIL for the two visual issues above.

Remaining uncertainty: the absent local SQLite corpus archive prevents verification of a populated knowledge API or live investigation workflow. Historical evaluation files were cross-checked; their experiments were not reproduced. No provider call, evaluation regeneration, code change, commit, or push occurred in this QA task.
