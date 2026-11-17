# T095 v4/v5 implementation and measured development improvement

User requested implementation and confirmation only after measurement, then later
merge/T095 closure. New branch feature03-retrieval-v4 starts at68aa027. No merge,
commit or push. Applied scoped speckit-implement after handoff/constitution/artifact
reads and explicit SPECIFY_FEATURE_DIRECTORY=specs/003-ai-investigation prerequisite
check PASS. No extensions.yml; requirements checklist has no unchecked items.
Prompt: prompts/development/003-retrieval-v4-20261117.md.
Design before code: specs/003-ai-investigation/retrieval-development-v4.md.

V4 opt-in English BM25 removes function words and requires >=.5 informative query
term coverage; unknown words count against coverage. V5 separately adds a small
explicit suffix normalizer and removes possessive singletons. Legacy paths/configs
unchanged. No corpus edits, translations, synonyms, embeddings, new dependencies,
LLM calls or labels in runtime. English support is documented; no reliable language
detection or semantic understanding claimed. Negation and source text stay intact
in cited passages; lexical retrieval is not an entailment judgment.

Actual tests/commands using existing Python3.14 environment:
- pytest backend/tests/unit/test_retrieval_english_v4.py: RED3failed/2passed for
  absent v4 variant, then GREEN5. V5 design followed its tied measurement;
  RED1failed/5passed for absent v5, then GREEN6.
- pytest backend/tests -q --tb=short:974 PASS77.50s,exit0.
- Added explicit HTTP search/passage/no-match check afterwards. Final candidate
  tests + test_investigation_knowledge_api.py:16 PASS1.74s,exit0.
- Ruff and git diff --check PASS. No frontend change; prior193 frontend/build
  results belong to branch review, not rerun in this implementation unit.

Actual diagnostic: PYTHONPATH=backend/src, python -m
fraudlens.investigation.retrieval_v4_diagnostic, isolated new .cache stores.
First inline attempt failed cp1252 decoding before search; explicit UTF-8 runner
corrected it. No actual .env/key/provider access. Predictions materialized before
offline reference join. ONLY six previously exposed English DEVELOPMENT rows:
4answerable/2no-answer, identical sample per configuration, no dropped failures.

| Configuration | Recall@5 | MRR@5 | No-answer correct |
|---|---:|---:|---:|
| Demo baseline,cutoff.5 |1.00|1.00|0/2|
| V3 selected baseline,cutoff8.863342357405378 |.75|.75|2/2|
| V4 coverage,cutoff.5 |.75|.75|2/2|
| V5 inflection+coverage,cutoff.5 |1.00|1.00|2/2|

Preserved raw rows/configs: feature-003-retrieval-v4-development-20261117.json and
feature-003-retrieval-v5-development-20261117.json. V4 tied, not success. V5
recovers the remaining development hit without new no-answer errors. This is
exposed-development improvement ONLY; questions were visible during development.
No independent quality claim, guarantee against overfit, whole-RAG/report quality
evaluation or SC-002 acceptance. Historical multilingual results/packs unchanged.

Runtime is available opt-in through existing prepare-knowledge --retrieval with
retrieval-development-v5.json in a NEW store shared by API/worker. Quickstart
documents actual command. Existing stores/defaults not migrated or overwritten.

Concrete proposal: evals/investigation/retrieval-english-v5-proposed/ holds
10development+20held-out (8+16 answerable,2+4 no-answer). Candidate source/config
hashes recorded before proposal authoring. AI document references are NOT reviewed
gold. Requires source completeness, semantic novelty and split review, passage-ID
resolution, English-count runner adaptation and immutable freeze. NOT RUN; existing
multilingual v3 runner must not be used unchanged. A new wording alone does not
establish independence from exposed old question families in this small corpus.

T095 unchecked/SC-002 unconfirmed. User instruction authorizes offline work, not
fabricated human review or unknown provider spending. No live, merge, commit/push,
old holdout replay or lowered .80/.70/all4 no-answer targets. Next step: actual
review of this concrete proposal, English runner adaptation and freeze, then
one-shot acceptance without tuning on held-out outcomes.
