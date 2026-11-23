# V6: bounded semantic answerability, not another lexical threshold

User2026-11-17 requests a robust RAG candidate and explicitly authorizes up to30
OpenAI calls on educational/public material, no automatic retries. No merge yet.

Implement an explicit async semantic retrieval port. Candidate generation for the
current tiny corpus uses all passages up to20, not lexical top-k that can discard
paraphrases. Fail closed above20 or48k request bytes; no silent context clipping.
Output at most5 source IDs with verbatim supporting quotes, or insufficient.
Deterministic validation rejects extra fields, unknown/duplicate IDs, missing/
altered quotes, inconsistent verdicts. Text remains untrusted; no tools/network
actions instructed by sources. Model judges meaning, never supplies permissions.

Question-specific facts require source-specific evidence; related general policy
does not answer a request for actual customer facts, exact legal quantities or
current obligations. General advice can answer a procedural question or a grounded
negative question. Preserve jurisdiction/date and missingness. No ID routing,
keyword denylist, invented translations, glossary or query-specific prompts.

Runtime boundary must remain explicit: do NOT hide extra provider calls inside
existing deterministic search/tools or bypass investigation dispatch budgets.
Provide async port and bounded experiment runner first; application activation
requires budget-accounted integration, separately tested. Legacy paths unchanged.

Tests before implementation: correct source/citation, insufficient, unknown ID,
quote corruption, duplicate IDs, malformed/refusal/oversize and strict budgets.
Freeze code/prompt/corpus before one-shot diagnostics:24 exposed robustness rows
plus6 additional author-controlled probes. Labels joined only AFTER raw responses.
No tuning after these results. Agent references are not independent gold; keep
T095/SC-002 open until reviewed fresh acceptance and runtime integration exist.
