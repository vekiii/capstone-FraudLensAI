# Feature 003 Phase 3 handoff - 2026-11-14 Europe/Belgrade

Later source-review update (2026-11-14): Milan Gavrić explicitly approved all six
texts and documented reuse/applicability without changes. T013 is now complete;
manifest status reviewed and production stage validation PASS. No actual corpus
publish/runtime recheck performed. T015/T017/T019/T021/T022 remain partial.
See [current approval evidence](feature-003-corpus-review.md) and root next_work.md.
The original implementation handoff below is historical; its pending-review and
manifest-only statements are superseded by that evidence. T023+ remains untouched.

Scope: T013-T022 only. Phase is **partial**; T023+ not started.
Branch `feature03`, baseline/current HEAD
`83b587bcc17f8ad703ea67ca593b3785d7fc4391`; no commit/push/merge/deploy.
Preexisting edits to phase-02 handoff and next_work were preserved.
Original [rendered request and clarifications](../../prompts/development/003-investigation-phase-03.md).
Applicable speckit-implement skill used within explicit scope; selected feature
via SPECIFY_FEATURE_DIRECTORY. Requirements checklist 16/16; no extensions.yml
before or after implementation, thus no hooks dispatched. Checklists unchanged.

## Status by task type

| Task | Status | Actual result / remaining condition |
|---|---|---|
| T013 | Partial | Six candidate texts and hashed provenance manifest prepared; user inspected only manifest. Actual source/reuse review pending. |
| T014 | Complete | Executed loader RED, final 17 unit tests pass with authored data. |
| T015 | Partial | Loader/CLI/archive implemented and independently tested; real six-document publish blocked by T013. |
| T016 | Complete | Executed BM25 RED; final 10 tests pass, including process determinism. |
| T017 | Partial | Offline baseline implemented/tested; delivery depends on actual T015 corpus. |
| T018 | Complete | Executed 9 route assertion RED failures, final 9 API tests pass. |
| T019 | Partial | Knowledge routes/composition and T012 knowledge errors implemented; actual-source dependency remains. |
| T020 | Complete | Executed frontend RED, final 5 focused tests pass. |
| T021 | Partial | Strict client/views/controller/navigation implemented; actual-source dependency remains. |
| T022 | Partial | Real HTTP/proxy/automated Chrome scenarios pass with authored TEST corpus; real reviewed corpus recheck pending. |

No T013-T022 task is wholly unstarted. Delivery tasks remain unchecked until
their actual dependency is met; synthetic reviewer metadata is not approval.

## Delivered behavior

Offline preparation validates review metadata, dates, normalized content hashes,
closed manifest/entry fields and resolved path boundaries. Exact section passages
are bounded to 2400 characters/200 per corpus, with stable version/content/chunker
identities and immutable historical text/provenance in separate SQLite storage.
No runtime document ingest, download or reference/development-prompt access.

BM25 is body-only k1=1.2/b=0.75, NFKC/casefold Unicode tokens, deduplicated sorted
query terms, stable passage-ID tie break, top five. Archived config IDs pin
retrieval. User requested a logical initial threshold: configuration version 2
uses **0.5 demo heuristic**, not development/held-out evaluated. T055 quality
selection remains future work. No glossary/title weighting or embedding service.

Readonly `/api/knowledge/documents`, `/search`, `/passages/{id}` use closed
existing contracts and safe feature errors. Optional omitted versions select
latest archived version; returned identity pins subsequent UI requests. Feature
disabled/missing corpus preserves startup and original case browser. Separate
X-Results-Truncated header preserves closed SearchResult JSON.

Knowledge UI displays literal exact passage text and provenance, simulation,
jurisdiction and historical limitations, no-match/unavailable, Retry; cancels or
ignores obsolete responses. Original case flow/decoders preserved.

## Actual verification

Python 3.14.3; uv 0.10.9; Node 24.20.0; npm 11.19.0;
Chrome/157.0.8103.52. Existing locked environment reused, no dependency changes.

| Check | Observed | Exit |
|---|---|---|
| Full backend | 517 passed, 3 deliberate T035 failures, 1 existing warning | 1 |
| Focused knowledge/retrieval/API rerun | 36 passed (17/10/9), 1 existing warning | 0 |
| Ruff backend | PASS | 0 |
| Full frontend | 156 passed / 6 files | 0 |
| Typecheck / build | PASS / PASS (12 modules) | 0 / 0 |
| Real API/proxy/automated headless browser | 9 observations PASS with authored TEST corpus | 0 |
| Actual staged corpus CLI validation | Controlled refusal, no store created | 2 (expected) |
| Six normalized candidate source hashes | Match; review fields null | 0 |
| Diff whitespace / 28 new-file UTF-8/link checks | PASS | 0 |

Full backend is NOT GREEN. Exact remaining node IDs and causes are in
[API evidence](feature-003-api.md): investigation attempt envelope and two future
POST mutation guards. They stay RED until T035; no placeholders/skip/xfail added.

Detailed commands/RED/GREEN/environment errors/limits:
[knowledge](feature-003-knowledge.md), [UI](feature-003-ui.md),
[corpus review](feature-003-corpus-review.md),
[automated browser results](feature-003-knowledge-smoke-results.json).
The browser verifier started hidden loopback services with isolated Chrome profile
and stopped only owned process trees; no cleanup errors reported. This is not
human clicking, peer review, model evaluation, or full SC-001 acceptance.

## First remaining condition and concrete continuation

**Actual human review of the six texts** and their provenance/reuse/applicability
notes, with actual reviewer/date/decision/corrections recorded in corpus-review
evidence. User explicitly confirmed only the manifest was inspected. Manifest
remains staged, all actual reviewed_by/reviewed_at null, real corpus never published.
The review record links every text and gives the review checklist.

After actual approval, record truthful metadata, revalidate all hashes, set
reviewed state and publish via prepare-knowledge; repeat actual-source T022 smoke.
Do not infer approval from this handoff or from test-only reviewer fields.

CLI must run with backend package path (documented quickstart):
```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
```
While review is pending, the reproducible authored-only smoke command is
`node evidence/tasks/feature-003-knowledge-smoke.mjs`; it refuses occupied ports
8000/5173/9228 and requires the recorded local Chrome executable. Generated stores
and browser profiles stay under ignored unique `.cache` directories.

No provider SDK/key/probe, report, tools, worker, analyst disposition or evaluation
implementation added. Source/producer/provider reviews outside this slice remain
pending. Do not begin Phase 4 from this partial handoff.
