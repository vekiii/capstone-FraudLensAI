# T095 retrieval development design v3 — 2026-11-17

Status: **plan approved by Milan Gavrić / milangavric2003 on 2026-11-17;
18-row development reference table accepted by Milan; development selection
executed below targets; fresh acceptance execution NOT AUTHORIZED / NOT RUN**.
T095 remains partial/open. SC-002 remains unmet.

Latest actual result: [development selection evidence](../../evidence/tasks/feature-003-t095-development-selection-20261117.md).
One comparison on18 reviewed development questions: both configurations
Recall/MRR0.25/0.25,6/6 correct no-answer, baseline preselected on a tie. Actual
default unchanged. Separate held-out authoring/review/freeze/authorization absent.
No further tuning of this candidate from these results; review a new version or
an explicitly decided language-scope amendment. English-only remains discussion.

Actual decision: user explicitly confirmed this plan and authorized implementation
on a new branch from feature03. This is contributor plan approval, not a claim of
independent reference review or a declaration about prior held-out exposure.
The approved plan snapshot is available at feature03 commit18e930a; implementation
record: `evidence/tasks/feature-003-t095-v3-implementation-20261117.md`.

This is a new design/protocol proposal, not a runtime configuration or an amendment
to the historical frozen evaluation. It builds on the implemented, opt-in
[development-v2 candidate](../../data/knowledge/fraudlens-aml-knowledge-v1/retrieval-development-v2.json)
from [reliability v2](reliability-v2.md). It does not repeat T071 or silently publish
that candidate. [Evaluation evidence](../../evidence/tasks/feature-003-evaluation.md)
and [this unit's execution](../../evidence/tasks/feature-003-t095-20261117.md)
separate mechanical checks, review decisions and acceptance.

## Problem and bounded improvement

The original baseline and title/glossary improvement each measured macro
Recall@5=0.50 and MRR@5=0.50 on 16 answerable held-out questions, with 4/4 explicit
no-match outcomes on the separate no-answer denominator. These are preserved
failed results against the unchanged 0.80/0.70 targets. Published language-level
aggregates motivate a bilingual development hypothesis; they do not establish the
cause of any individual failure. Old questions/answers must not guide this work.

Propose one candidate: existing title/glossary BM25 plus explicit
`sr_cyrillic_to_latin_v1` query lookup, with a **new development-selected cutoff**.
The current v2 cutoff 0.5 is a demo heuristic, not a quality result. Reusing it or
the old frozen cutoffs as a newly validated threshold would be unjustified.
No new synonyms, stemming, embeddings, query LLM, corpus expansion, dependencies
or web access are needed for this bounded comparison. If development coverage is
inadequate, report ineligible rather than widening this candidate after exposure.

| Component | Proposed baseline B3 | Proposed candidate C3 |
|---|---|---|
| Corpus/chunks | Same reviewed six-document corpus and section IDs | Identical to B3 |
| Query tokens | NFKC, casefold, Unicode alphanumeric, deduplicate | Same, then explicit Serbian Cyrillic-to-Latin lookup |
| Term expansion | None | Existing reviewed glossary, unchanged; original weight 1, synonym 0.5, max dedup |
| Scoring | Body-only BM25, k1=1.2/b=0.75 | Body + 2*title/section tf; body-only length normalization |
| Ordering/results | Sorted term summation, passage-ID ties, <=5 | Identical ordering/bounds |
| Adequacy cutoff | Selected separately on fresh development only | Selected separately on the same fresh development only |
| Deployment | Preselected from development | No selection based on holdout |

This lookup transliterates query terms for glossary access, not corpus documents
or arbitrary language. Unknown words, inflection and mixed-topic queries remain
known limitations. BM25 scores are not relevance probabilities. A lexical match
does not establish that a complete question is answerable; no-answer controls
must include unsupported topics sharing ordinary corpus vocabulary.

## Fresh pack: retrieval-fresh-v3 (development draft authored; not frozen)

Implementation update2026-11-17: the separate offline runner and18 development
questions/reference proposals now exist. See the
[concrete review packet](../../evals/investigation/retrieval-fresh-v3/README.md).
New held-out text remains unauthored in this implementation context. Its separate
authoring/review remains pending. The concrete development table was subsequently
accepted and one development selection executed; see the latest result above.
No acceptance run occurred. The process steps below retain the approved design;
they are not acceptance completion claims.

A teammate other than the new question/reference author must review questions,
relevant-passage sets, no-answer judgments, split separation and provenance.
Record actual identities, dates, independence/conflicts, findings and decision;
AI self-review cannot fill those fields. Authors must declare prior exposure to
the original held-out content. Use a reviewer without that exposure to assess
novelty; exclude paraphrases of old tests. Any unavoidable exposure must be
disclosed and can prevent an independent acceptance claim.

Proposed separate root: `evals/investigation/retrieval-fresh-v3/`, with
`inputs/development.json`, `inputs/held-out.json`, separate private
`reference/development.json` and `reference/held-out.json`, `splits.json`,
`protocol.json`, `review.json`, and an immutable freeze. Development files are now
drafted; held-out files and the freeze remain absent. This is not a reviewed pack.
Held-out references remain inaccessible to
generation/retrieval; merely co-locating them in a combined JSON and filtering
after parsing is insufficient for this new runner.

| Split | en answerable/no-answer | sr-Latn answerable/no-answer | sr-Cyrl answerable/no-answer | Total |
|---|---|---|---|---|
| Development | 4/2 | 4/2 | 4/2 | 18 |
| Fresh held-out | 6/2 | 5/1 | 5/1 | 20 |

The extra development examples improve no-answer coverage without changing the
20-question acceptance denominator or inventing language-specific thresholds.
Translations/paraphrases of the same intent form one family and must stay in one
split. Split assignment and IDs are recorded before candidate tuning. Fresh
held-out stays sealed from the implementer until both configurations, thresholds
and development-based deployment choice are frozen. Published diagnostic controls
from this unit are development-only and excluded from both fresh splits.

Include all six documents, simple and multi-concept questions, Serbian script and
diacritic variants, and no-answer cases with lexical distractors. References name
the complete relevant passage sets and rationale, not only a desired top hit.
Reviewers must judge scope/jurisdiction/simulation limitations. Relevant passage
sets, split counts and no-answer labels may not change after seeing predictions.

## Selection, freeze and authorized experiment

1. Obtain actual teammate review of this plan and the separate pack. Unresolved
   references, leakage or scope objections block freeze. Record a new version
   if the design changes; retain superseded decisions and outputs.
2. Before implementation of the fresh runner, add intended RED tests for refusing
   missing approval/freeze, mixed split IDs, changed hashes, reference access during
   prediction, overwrite/replay, missing/duplicate predictions and result errors.
   Existing synthetic metric/legacy-policy checks remain relevant regressions.
3. Implement a **separate versioned offline runner**, not a rewrite of T055/T056.
   The existing `freeze-retrieval` path hardcodes the old 10-question pack and can
   extend its protocol; it must not be run against this proposal. Reuse pure
   cutoff/metric primitives only after verifying their inputs and version binding.
4. On the 18 fresh development questions, collect raw scores/ranks separately
   for B3/C3. For each, enumerate 0, observed positive scores and their next
   representable higher floats as cutoff candidates; retain zero false answers
   and nonzero answerable recall, then maximize recall, ties by higher cutoff.
   Record ineligible if no cutoff qualifies. Do not adjust glossary/weights after
   this one bounded comparison; any redesign needs a separate development version.
5. Preselect deployment by development Recall@5, then MRR@5, then B3 on a tie.
   Freeze corpus/manifest/document/chunker hashes, tokenizer/runtime/evaluator
   source hashes, both canonical config hashes and cutoffs, glossary, pack/split/
   reference hashes, review decisions, development predictions, deployment choice
   and environment. Record unavailable artifacts as blockers, never reconstruct
   original archives. Freeze bytes before any fresh held-out execution.
6. Present the sealed pack/configuration hashes and exact execution scope for
   explicit user authorization. Proposed budget: offline retrieval only, zero
   provider calls/spend, one run per frozen configuration over the same 20 fresh
   held-out questions (40 searches total), in a new ignored output/store. Record
   run identity, failures and no-match outcomes; refuse an existing output path.
   Interrupted/failed execution remains in evidence; rerun requires an explicit
   new decision. No live reports, timing acceptance or other tasks are included.
7. Generate from input-only files, close/seal predictions, then join private
   references offline. Never send labels or relevant IDs through search/tool
   inputs. Keep all 20 predictions per config, failures, scores/ranks/passage IDs
   and result hashes. Missing rows fail completeness rather than disappearing.

The T095 plan/implementation approval authorizes preparation and runner work,
not step 6. The runner is implemented/tested; reviewed development selection is
complete. Acceptance-pack review and freeze remain pending. These numbered steps
describe the evaluation process, not completed experiment commands.

## Metrics, decisions and completion boundary

For each answerable query, Recall@5 is relevant hits/size of its declared relevant
set; reciprocal rank is 1/first relevant rank through 5, otherwise zero. Macro
average both over all 16 answerable held-out questions. Failed searches and
answerable no-match outcomes contribute zero. The four no-answer questions have
their own denominator: report correct no-match, false answer and execution errors;
an error is never correct no-match. All four must explicitly report insufficient
coverage. Report both configurations including per-question regressions and
overall/en/sr-Latn/sr-Cyrl denominators; empty subgroups are N/A.

SC-002 remains unmet until actual authorized fresh evidence shows at least one
frozen configuration with Recall@5>=0.80, MRR@5>=0.70 and 4/4 correct no-answer.
Report target achievement separately from development-preselected deployment.
No winner selection, cutoff adjustment or relevance relabeling from held-out
results. An unsuccessful experiment remains failed; exposed questions cannot
become a fresh independent test. Passing retrieval would not establish report
faithfulness, live timing, independent T094 review or full producer assembly.

| Review item | Actual status |
|---|---|
| Scope/contract/metric/preservation technical review | AI self-review completed in this unit; see execution evidence |
| Plan decision | APPROVED by Milan Gavrić / milangavric2003,2026-11-17; contributor review |
| Concrete development reference review | ACCEPTED by Milan's subsequent table/corpus approval; no old-question semantic duplicate audit claimed |
| Fresh runner | IMPLEMENTED; synthetic RED/GREEN evidence recorded separately |
| Fresh pack |18 development proposals authored; separate held-out authoring pending |
| Actual development selection | EXECUTED ONCE, both Recall/MRR0.25/0.25; baseline tie-break; not acceptance |
| Fresh freeze and separate held-out reference review | NOT RUN / PENDING |
| User authorization for sealed fresh acceptance experiment | NOT REQUESTED; concrete freeze not yet available |
| Fresh acceptance evidence / SC-002 | NOT RUN / UNMET |

Next concrete step: team reviews the development failure and records a separately
versioned retrieval design or explicit language-scope decision. His old-held-out
non-exposure remains a user declaration, not an audited claim. Separate held-out
authoring must preserve the implementation/tuning boundary; do not tune on it.
