# T095 English lexical coverage candidate v4

User2026-11-17 requests implementation and measured improvement, with no merge
or T095 closure until review. Work starts from68aa027 on feature03-retrieval-v4.

Candidate: opt-in English BM25 with question/function-word removal and explicit
query-content coverage. Baseline and all old configurations retain exact behavior.
Require at least half of distinct informative query terms in a passage; ignore
function words in both query and body. Unknown informative terms count against
coverage. No translations, corpus edits, LLM calls, new dependencies or labels
in runtime. Scores remain lexical relevance scores, not probabilities. English
support is disclosed; no claim of reliable natural-language identification.

Predeclared controls: stopword-only no-match; shared generic words insufficient;
specific vocabulary wins over generic prose; unknown variant fails closed; legacy
results identical. RED before implementation, then full regression.

Development diagnostics may use previously exposed development questions, labeled
as such and never an independent quality claim. No old held-out inputs/references
are opened or regraded. Acceptance requires separate fresh English pack with at
least10 development and20 held-out (at least4 no-answer), reference review,
freeze before execution, Recall@5>=.80/MRR@5>=.70 and all no-answer correct.
Agent-authored references cannot impersonate independent human approval. Keep
SC-002/T095 open unless their actual evidence exists. No lowered thresholds or
post-result deletion of failures. Current request authorizes implementation and
offline checks, not spending an unknown provider budget.

## Separately versioned v5 follow-up after v4 measurement

V4 tied selected v3 at .75/.75 and2/2 no-answer on the six exposed English
development rows. Preserve that report. V5 adds a small, explicit English suffix
normalizer (plural-s, ed/ing with doubled consonant, adverb-ly) and removes
possessive singleton tokens. Keep the .5 coverage gate and BM25 parameters.
No synonym table, question-ID routing, translations or label-dependent runtime.
Measure on the SAME development rows for engineering diagnostics only; never
claim fresh acceptance, general English stemming or semantic understanding.
