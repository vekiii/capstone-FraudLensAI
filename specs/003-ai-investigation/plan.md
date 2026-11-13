# Implementation Plan: Evidence-backed AI Investigation

**Branch**: `feature03` | **Date**: 2026-11-13 | **Spec**: [spec.md](spec.md)

**Input**: `specs/003-ai-investigation/spec.md`; all runtime behavior below is planned, not implemented.

## Summary

Deliver curated knowledge search, a bounded tool-using investigation, immutable evidence-backed reports and explicit human disposition. Work from authored fixtures before dataset/model integration. Add feature-local modules and a separate SQLite store; preserve foundation response contracts and do not import unfinished ML code. The first useful increment is US1 search/source inspection; the complete investigation MVP includes US2-US4, and US5 evaluation is mandatory for release.

## Technical Context

**Language/Version**: Existing Python >=3.14,<3.15 and Node >=24,<25; vanilla TypeScript/Vite.

**Primary Dependencies**: Existing FastAPI/Pydantic/Uvicorn; add the official OpenAI Python SDK at implementation-time resolution and commit generated uv.lock. No dependency installation in this planning task. Standard-library SQLite, hashing, Unicode/tokenization and BM25 calculations; no vector database or workflow framework.

**Storage**: Separate ignored `data/processed/investigations.sqlite`, schema version 1, parameterized queries, foreign keys, short explicit write transactions, optimistic revisions and unique request identities. Reviewed corpus sources/config are tracked only where reuse terms permit; exact run evidence and generated indices remain local. No writes to feature 002's store.

**Testing**: Existing pytest/jsonschema/Ruff and Vitest/jsdom/typecheck/build. RED -> GREEN -> REFACTOR for contracts, tool access, retrieval, budgets, state, review and UI races; no artificial RED for directories/locked installs. Runtime provider tests opt-in and excluded from default unit suite.

**Target Platform**: Windows/macOS local demonstration, loopback backend/proxy; one explicit CLI worker process, one active attempt globally. No background distributed workers, public hosting or enterprise auth.

**Project Type**: Existing web application plus local corpus/evaluation/worker CLI.

**Performance Goals**: SC-006: 20-query local search p95 <=2 s; >=4/5 ordinary live cases produce a validated/needs-information result <=90 s; every attempt visibly ends <=120 s.

**Constraints**: At most 8 dispatched provider requests, 12 tool executions, 5 passages/search, 50 history events/result, 1 transient retry and 1 output repair per attempt; all share 120 s. Per-request timeout <=min(30 s, remaining deadline), max output tokens 4096, serialized input <=48,000 UTF-8 bytes, total transport response <=2 MiB. Disable SDK automatic retries. If the selected model cannot meet required tool/schema controls, stop at an explicit capability gate. No silent model substitution.

**Scale/Scope**: At least six reviewed thematic documents, <=200 initial passages, one local analyst identity and one active attempt; 30 retrieval questions, 12 report scenarios, >=12 safety scenarios. Queries 1-500 trimmed Unicode characters. Corpus passages <=2400 characters and tool-result bodies <=16,000 UTF-8 bytes; oversize individual facts cause controlled failure, never silent alteration.

## Constitution Check

Pre-research and post-design assessments both pass at design level; actual acceptance remains pending.

| Principle | Design evidence / enforcement |
|---|---|
| I scope | Existing four screens, synthetic data, no excluded product techniques. |
| II specification | Spec -> this design/contracts -> tasks -> implementation. |
| III TDD | Separate intended RED and GREEN tasks with negative/regression evidence. |
| IV purposeful AI | Model chooses permitted evidence queries and synthesizes; math, scope, persistence and disposition deterministic. |
| V verifiable claims | Typed evidence/citations, exact-value checks, human semantic review. |
| VI human authority | Separate explicit reviewed disposition, never tool access to decisions. |
| VII independent evaluation | Private reference pack; runtime cannot open it; frozen development/held-out partitions. |
| VIII parallel development | Fixture context + proposed dataset boundary, separately reviewed before real integration. |
| IX reproducibility | Hashed versions, bounded trace, no credentials, explicit unknown outcomes. |
| X minimum complexity | SQLite + one worker + standard-library retrieval; no framework/graph/vector service. |

External gates are not design violations: actual provider/model access, corpus selection/human review and current feature 002 contract review. They block the related live tasks, not fixture development. No exceptions to constitution requested.

## Project Structure

### Documentation (this feature)

`spec.md`, `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, `tasks.md`, `evaluation.md`, `checklists/requirements.md`; `contracts/api.md`, `contracts/tools-and-provider.md`, `contracts/schemas.json`, pinned `contracts/producer-v2.snapshot.json` and `contracts/examples/*.json`.

### Source Code (repository root; planned paths)

```text
backend/src/fraudlens/investigation/
  __init__.py  models.py  settings.py  context.py  knowledge.py  retrieval.py
  store.py  tools.py  provider.py  validation.py  workflow.py  review.py
  api.py  cli.py  evaluation.py
backend/tests/contracts/test_investigation_contracts.py
backend/tests/unit/test_investigation_*.py
backend/tests/integration/test_investigation_*.py
frontend/src/investigation/{contracts,api,views,controller}.ts
frontend/tests/investigation-*.test.ts
data/knowledge/fraudlens-aml-knowledge-v1/{manifest.json,documents/,glossary.json}
data/fixtures/investigation/{contexts.json,history.json,provider-scripts.json}
prompts/application/investigation-v1.md
evals/investigation/{inputs/,reference/,splits.json,protocol.json}
evals/results/feature-003/                 # ignored
data/processed/investigations.sqlite       # ignored
evidence/tasks/feature-003-*.md
```

**Structure Decision**: Keep feature modules isolated. Only final composition modifies `backend/src/fraudlens/main.py` and `frontend/src/main.ts`/`views.ts`; coordinate these edits with feature 002. New investigation routes use their own error handling so existing 404 behavior is not reused incorrectly. Do not widen `APP_MODE` or feature 002 contracts. New feature settings are separate from existing fixture Settings.

## Phase 0: Research decisions

See [research.md](research.md). Decisions: local BM25 baseline; one frozen title-weight/bilingual-glossary improvement; immutable corpus versions; official SDK Responses with configurable model and strict tools/report; separate durable store and explicit worker; no hidden retries. Source/model capability checks are opt-in future tasks, never claimed executed in planning.

## Phase 1: Design and contracts

See [data-model.md](data-model.md), [API](contracts/api.md), [tools/provider](contracts/tools-and-provider.md), [schemas](contracts/schemas.json), [evaluation](evaluation.md), [quickstart](quickstart.md).

### Flow and failure boundaries

1. Knowledge preparation validates hashes/metadata, chunks by section with a 2400-character ceiling and no overlap across sections, then publishes an immutable corpus version. Query normalization is NFKC + casefold, Latin/Cyrillic handling through a versioned reviewed glossary, Unicode alphanumeric tokens, no hidden network embedding calls.
2. POST creates a case/snapshot-bound run from an authorized context adapter, copies the immutable context, pins corpus/retrieval/prompt/provider settings and reserves a request identity. No provider call in HTTP creation or polling.
3. Explicit local worker claims one queued run with transactional compare-and-swap. Tools use server-bound scope. Tool outcomes and authorized evidence become durable; no model-generated SQL or cross-case IDs are accepted.
4. Reserve provider budget and persist dispatch intent before each request. Update outcome after return. All request/retry/repair time counts toward the attempt's single deadline. On restart interrupted dispatch is outcome_unknown and attempt fails as interrupted; GET never replays it. Explicit retry creates a linked attempt with fresh limits and disclosed possible prior spend, reusing only saved valid evidence with matching context/corpus.
5. Model requests tools in sequence, then submits structured report. Validate schema, source identity, required evidence types, structured exact-value assertions and exact source quotes. Numbers hidden in prose cannot be reliably proven by schema; semantic support is explicitly unchecked until human evaluation. Unsupported drafts cannot be accepted through unknown citations or changed structured facts.
6. Persist a valid ready-for-review report or limitations draft/needs-information. No unsupported draft is published as ready. Explicit review transaction records actor/rationale/disposition/report revision; stale writes conflict. Cancelled/failed attempts cannot resume from late replies.

### Parallel ownership / current producer reconciliation

Baseline is main `0fbe313`; selected producer contract was inspected at `2dd815d`. A documentation-only snapshot of that producer schema is pinned here so fixture adapter tests use current meanings without merging ML. Feature 003 context embeds the producer's CaseDetailV2 unchanged or the existing foundation CaseDetail for fixture mode; context metadata explains unavailable fixture history/time provenance instead of fabricating v2 fields.

Dataset equality checks include context case_id = payload case_id, transaction ID agreement, context snapshot_ref = payload snapshot_ref = assessment run_id, and context dataset_version = payload/assessment dataset_version. Time assumptions, raw minutes, source-supported currency/amount precision and explanation scale remain unchanged. Tools query no private labels. Producer history is a separate interface whose accepted behavior is strict pre-cutoff bank+account history; no adapter is labeled real until reviewed and exercised against the actual producer.

Freeze context API with producing/consuming teammates before real integration. Do not wait for trained-model accuracy to develop fixtures or a truthful rules-backed context. If producer advances, record new SHA/schema diff and re-review affected consumers; do not silently replace this pinned snapshot.

### Delivery stages / ordering

- Setup/foundation: settings, closed schemas, fixture adapters, minimal transaction store and corpus inputs.
- US1: source preparation/search/inspection and knowledge UI; first independent MVP.
- US2: bounded tools, test provider, report validation, worker and report UI. Live provider adapter follows opt-in probe; credentials do not block offline slice.
- US3: explicit restart/retry/cancel/stale-snapshot recovery and persistence evidence.
- US4: human review and correction UI with optimistic revisions.
- US5: frozen retrieval/report/safety packs, baseline/improved evaluation, actual-provider human scoring and measured demonstration.
- Integration/convergence: dataset adapter review/live integration when producer exists; full foundation regressions, quickstart reproduction and actual acceptance. No automatic completion of ML gates.

## Complexity Tracking

No constitution violations or additional services. A separate SQLite file avoids shared schema migrations. One worker is the smallest durable execution mechanism here; a queue service and framework are rejected as unnecessary. Lexical retrieval keeps baseline offline and transparent; embeddings remain a separately justified later choice if this bounded comparison is insufficient, not an implicit task.
