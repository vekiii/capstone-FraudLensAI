# English-only retrieval MVP decision — 2026-11-17

**Decision: APPROVED** by Milan Gavrić (`milangavric2003`) in this session:
“Добро, ајмо да пређемо на енглески. Можеш то записати у план или шта год.”
[Original request](../../prompts/development/003-english-retrieval-decision-20261117.md).
This supersedes the earlier multilingual retrieval scope prospectively, including
the2026-11-15 decision recorded in evaluation.md. It is a scope reduction within
the approved MVP/course, not a new technique or an acceptance waiver.

## Agreed scope

For the initial MVP, supported procedure-search queries and new retrieval
evaluation questions are **English only**, against the existing English corpus.
Serbian Latin/Cyrillic retrieval quality is deferred to a later separately scoped
version. No claim of general Serbian query support is required for this MVP.

The preceding discussion concerned retrieval language. The default Serbian UI
and generated report language remain separate, unchanged requirements. A Serbian
report may use exact English source citations; its faithfulness must still be
evaluated independently. This decision does not request an application-wide
English UI/report rewrite or introduce automatic translation.

Benefit: removes cross-language matching from the immediate retrieval work and
focuses the next experiment on relevance and explicit insufficient coverage.
Schedule impact: reduces the near-term language surface; a new English-only
design, reviewed pack and runner adaptation are still required. No delivery-date
estimate or promise of passing quality is inferred. Serbian support returns only
under a later versioned plan and evaluation.

## Evaluation and preservation

- Keep SC-002 Recall@5>=0.80, MRR@5>=0.70,20 fresh held-out questions and at least
  four no-answer questions, with all no-answer outcomes correctly insufficient.
  Keep at least10 development questions (at least30 total), reviewed references,
  baseline/candidate comparison, frozen settings and prediction/reference separation.
- The successor English-only evaluation must have new versioned identities and
  explicit language=en. For a20-question pack with four no-answer cases, the
  answerable denominator is16. Do not take only English rows from old tests and
  call that a new acceptance result or lower denominators/thresholds.
- Preserve original multilingual0.50/0.50 and v3 development0.25/0.25 results,
  inputs/references/splits/configs/cutoffs/reviews, including failed outcomes and
  their language counts. The eight old English successes and new development
  English3/4 are not independent English-only acceptance evidence.
- No fresh acceptance execution follows automatically from this scope decision.
  Prepare the concrete reviewed/frozen pack and request separate execution scope
  as already planned. T095 remains open and SC-002 unmet.

## Implementation boundary and next step

This unit records the decision and updates planning documents **only**. Existing
runtime Unicode input acceptance, optional glossary/script lookup and v3 evaluator
remain as implemented; their retained code does not prove supported Serbian
quality or implementation of the new English-only contract.

Next: specify a separate English-only retrieval development version under T095,
including baseline/candidate, no-answer handling and new pack. Define how analysts
and the investigation worker supply bounded English procedure queries, and how
unsupported query language is disclosed. Do not assume reliable language detection
or silently translate queries. Add RED/GREEN contract/negative checks before changing
runtime behavior. No new candidate, dependency, embeddings, corpus expansion,
provider use, retuning of v3 or experiment is authorized by this docs-only unit.
