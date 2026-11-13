# Research decisions - feature 003

Status: design research, 2026-11-13. No credentials/model probe or application code execution. Local repository evidence and primary documentation inform decisions; there is no claim of measured retrieval/report quality.

## R1 - Independent context and source contracts

**Decision**: feature 003 owns an immutable wrapper with a closed `source_payload`: original CaseDetail fixture or pinned current CaseDetailV2. Keep producer shapes unchanged; use semantic validators for cross-object equality and a dedicated HistoryReader interface. Fixture history is authored and labeled, or unavailable.

**Rationale**: Main has older v2 proposals than `origin/model-implementations` at `2dd815d85bfc9c2fc70a28baef9c142d551e57e0`. Inspecting that branch's API and schema reconciles meaning without importing its unfinished model code. Pin a review snapshot, never claim actual integration or human approval.

**Alternatives**: Direct DB access couples to private labels and migrations. A new independently simplified Transaction definition risks losing exact money/time/score semantics. Waiting for trained ML wastes available parallel work.

## R2 - Small offline retrieval and one controlled improvement

**Decision**: standard-library BM25 (`k1=1.2`, `b=0.75`) over section passages for baseline. Improved configuration uses the same body scores plus title/section term weight 2 and a reviewed Serbian-English concept glossary; original terms weight 1, added synonyms 0.5. Deduplicate terms and retain maximum per-term weight. Deterministic passage-ID tie break. Tune no-match cutoffs on 10 development questions only, then freeze both configurations and thresholds before held-out execution. Tokenizer/glossary versions are part of configuration hash.

**Rationale**: Six thematic documents do not require a vector service; lexical retrieval is inspectable, offline, inexpensive and measurable. The improvement addresses Serbian questions against English guidance without sending the corpus to an external service. An unchanged/worse result is valid evidence and must be reported.

**Exact scoring policy**: For N passages, body-token average length avgdl and document frequency df, idf(t)=ln(1+(N-df(t)+0.5)/(df(t)+0.5)). Term score is query_weight(t) * idf(t) * tf(t)*(k1+1)/(tf(t)+k1*(1-b+b*dl/avgdl)). Baseline tf and dl use body tokens only. Improved tf=body_count+2*title_section_count; dl/avgdl still use body tokens so both configurations share length normalization. Sum over deduplicated query terms with max retained query weight. Empty corpus/avgdl=0 returns unavailable, not division by zero. Unseen terms contribute zero. Scores below the development-frozen cutoff yield no_match; qualifying ties sort by passage ID.

**Alternatives**: Remote embeddings introduce another model/key/cost dependency; local embeddings add runtime/model installation to a short deadline. Neither is required to establish evidence retrieval. Do not claim BM25 scores are calibrated relevance probabilities.

## R3 - Source provenance and knowledge preparation

**Decision**: version a manifest, source terms, dates, jurisdiction, simulated status and chosen sections; hash exact UTF-8 normalized LF content without silently trimming text. Paragraph/section chunking <=2400 characters preserves section references. Splitting long paragraphs produces stable ordinal subpassages, no cross-section concatenation. Reject unreviewed or changed-hash inputs.

**Rationale**: Retrieval citations must resolve to content actually supplied, not merely a current URL. Prepare six documents before evaluating; team review includes whether reuse is permitted. Official pages cited in the original idea are candidates, not already-ingested or legally reviewed sources.

**Alternatives**: Live scraping during investigation makes sources and applicability unstable. SARSum reports do not describe IBM cases and stay outside the initial knowledge dependency.

## R4 - Provider with explicit capability gate

**Decision**: official OpenAI Python SDK, Responses API, configured model ID, strict custom functions and strict report schema; `parallel_tool_calls=false`. Model list/retrieve is only an availability check; an explicit minimal synthetic tool + report-schema probe is required to establish selected-model capability. Refusal/incomplete responses are controlled outcomes. No access/identifier inferred from project name or the informal GPT-6 Luna label.

**Rationale / primary sources**:

- [Models list](https://developers.openai.com/api/reference/resources/models/methods/list): model discovery gives basic availability, not application capability proof.
- [Function calling](https://developers.openai.com/api/docs/guides/function-calling): strict closed argument shapes and call/result continuation. Application still authorizes scope.
- [Structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs): output shape is not a guarantee of factual support; handle refusal and incomplete output.
- [Conversation state](https://developers.openai.com/api/docs/guides/conversation-state): retain required response items across tool turns. Provider-required opaque continuation items stay private; do not expose or invent a reasoning narrative.

**Alternatives**: Framework-driven agent execution hides budgets/state. A guessed model ID can fail or select an unintended model. Silent fallback would invalidate evaluation provenance. No provider request is needed to complete planning.

## R5 - Application-owned request accounting

**Decision**: SDK `max_retries=0`; per-request timeout min(30 s, remaining deadline), absolute 120-second attempt deadline; maximum 8 dispatches, output 4096 tokens/request, input 48,000 bytes and received response 2 MiB. One total transient retry (429/connection/eligible 5xx) only if budget/time remains; cap backoff at 2 s and fail rather than ignore longer Retry-After. One structured/reference repair counts as another dispatch. No retry for 401/403, invalid model/schema request or refusal. Configure only model-supported settings; do not assume temperature/seed are supported.

**Rationale**: [Official Python library](https://developers.openai.com/api/reference/python) documents automatic retry/timeout controls. Defaults are unsuitable for a bounded 120-second workflow. Account for every dispatch including unknown outcomes; no exactly-once billing guarantee is assumed.

**Alternatives**: SDK retries plus app retries silently exceed limits. Automatic replay on reopen can duplicate spend. Record unknown usage instead of fabricating token counts/cost.

## R6 - Durable local workflow, separate store

**Decision**: stdlib sqlite3, dedicated file, foreign keys, explicit short write transactions and compare-and-swap revisions. Persist unique request identity, attempt context/corpus, dispatch intent, counters, tool result and report before state changes. One CLI worker; not an in-memory FastAPI BackgroundTask. Never hold DB write locks during provider I/O. Restart marks unknown dispatch interrupted, requiring explicit linked retry.

**Rationale**: [Python 3.14 SQLite](https://docs.python.org/3.14/library/sqlite3.html) and [SQLite transactions](https://www.sqlite.org/lang_transaction.html) support explicit transaction design; SQLite has one concurrent writer. Reserve budgets before external dispatch, not after. This crash-handling policy is application design, not a provider delivery guarantee.

**Alternatives**: Sharing ML SQLite couples migrations. Remote workers/Celery add unnecessary infrastructure. In-memory workflows lose audit history. A post-request-only checkpoint falsely implies an interrupted request was never sent.

## R7 - Evaluation and acceptance

**Decision**: freeze dev/held-out packs and corpus; separate retrieval/grounding/safety metrics; require actual live reports plus independent human ratings. Deterministic identity/citation checks cannot establish semantic truth. A test provider proves workflow only. See [evaluation.md](evaluation.md).

**Alternatives**: ROUGE alone cannot detect invented financial facts. LLM-only judging is not independent human review. Tuning thresholds on held-out failures invalidates the comparison.
