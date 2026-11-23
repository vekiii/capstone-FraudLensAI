# Report evaluation method amendment v2 — 2026-11-15

Decision source: [actual user annotation](../../prompts/development/003-investigation-judge-amendment.md).
Baseline HEAD aaabd8dec787d83e1b50bc2972e8182162ca6225, worktree initially clean.
Read AGENTS.md then current next_work.md, constitution and feature evaluation
requirements. No implementation skill invoked: this unit changes specifications
and evaluation protocol only, not runtime behavior or evaluation execution.

## Actual decision and reason

The user explicitly chooses LLM-as-judge instead of both planned human rating
roles because manual unit/evidence review is difficult to carry out. Benefit:
remove the requirement that Vedran and Milan manually rate all prepared units.
Schedule impact: prepare a versioned judge prompt/output contract and isolated
primary/secondary execution, then aggregate; actual additional duration/cost is
unknown. No signatures or confirmation from Milan/the entire team are invented.

This changes the assessment method **after** retrieval and live report outputs
were exposed. It is a post-hoc evaluation amendment, not the original frozen
human-rubric result and not independent new held-out evidence. It must be labeled
automated in every summary. The same model/family can reproduce generator errors;
second-pass agreement is consistency evidence, not human validation or proof of
statistical independence. Original failed quality/time findings remain failed.
Six primary attempts failed without a report; even perfect scores on the two
remaining drafts cannot meet the unchanged seven-of-eight report target. Task
execution may later finish with a failed quality outcome; the method change
does not convert the feature into accepted quality.

## Approved replacement scope

- Primary: automated ratings on all 8 original primary outcomes, retaining failed
  reports in denominator and rating only actual existing claims.
- Secondary: automated ratings on unchanged preselected H02/H03/H04/H06/H08.
  Run in a fresh isolated context without primary judgments/reasons or prior chat.
  Record actual model/provider/settings, prompt/input/output hashes, date, usage
  or unknown and any retry/error. Same-model use must be disclosed.
- Preserve both raw sets before comparison. Disagreements must be recorded;
  unresolved uncertainty/disagreement cannot be promoted to supported/present.
  Any adjudication needs a separately recorded evidence-based rationale, never
  overwrite the original sets or claim a model has human authority.
- Keep existing support/coverage/critical-error/applicability definitions, fixed
  subset and >=7/8, >=90%, >=80%, zero critical unsupported claim targets. Empty
  claim denominator stays N/A. No replacement reports, new samples or tuning.
- Judge sees frozen reports/evidence and offline rubric/expectations, not secrets
  or private laundering labels. Reference access is solely post-generation
  scoring, never runtime investigation/retrieval/report generation.

## Preserved boundaries

FR-022/023 explicit human case disposition and immutable analyst audit unchanged.
Source/glossary/reference-pack approval, T062 producing/consuming review, T066
actual teammate reproduction/human code review and shared constitution unchanged.
No autonomous product agent or account action is added. This is an offline
evaluation-method change expressly requested by the user.

Original protocol.json, reference rubric, splits, T055 freeze, T058 live freeze,
reports, primary/secondary human templates and earlier evidence remain untouched.
The successor protocol is
[report-judging-v2.json](../../evals/investigation/amendments/report-judging-v2.json),
binding their hashes and referencing this decision. Historical human-review text
in old evidence/templates describes the superseded method, not a current gate.
The existing summarize-reviews/import_reviews implementation is not silently
repurposed to label machine identities as human reviews.

## Execution state

**Judge execution not run. T059 remains unchecked until actual machine ratings
and recorded comparison exist under v2.** T060/T061 must aggregate/audit under
the amended method, without claiming original human-validation acceptance.
No new provider call or paid attempt is authorized by interpreting the old
86/104 ledger as an available judge budget. A production judge run needs actual
model/settings/prompt binding and a separately authorized transport cap. No
judgments, score improvements, reviewer dates or model identity fabricated here.

Validation: documentation/protocol consistency and original-file hash preservation;
business RED/GREEN and application regression not applicable to this docs-only
change. See protocol verification result after execution below.

Validation executed, exit 0: successor JSON hashes match original protocol,
rubric and splits; all 13 frozen outcome byte hashes match; original three
artifacts equal HEAD after LF normalization; thresholds/subset unchanged;
T059 remains unchecked and judge.executed=false. UTF-8, JSON, local Markdown
links and shareable-secret-pattern scan PASS; git diff --check PASS.
Existing hash-only Phase 8 preservation check also PASS: 13 outcomes, 16 live
generation source hashes, 10 retrieval artifacts; ledger remains 86 attempts.
No application tests rerun for documentation-only changes; no runtime, importer,
model/API, reference rubric or frozen generation changes. No commit/push.
