# Current handoff — branch pushed; live development v2 frozen, 2026-11-16

User now explicitly authorized new branch push then actual LLM quality checks.
Created feature03-reliability-v2 from feature03, pushed maintenance7ed606c to origin.
feature03 remains cd98ea0. New protocol: specs/003-ai-investigation/live-development-v2.md.
T073 prepared/frozen3 NEW synthetic development inputs and separate expectations,
durable cap25 (8/case+1judge), no unknown-dispatch replay. Actual live calls so far0.
34 targeted/mock checks PASS; full backend833 PASS; Ruff/diff PASS.
Next: execute bounded development-v2 once, then one offline batch judge; preserve
all results. This user authorization supersedes the earlier no-live boundary below.
Evidence: evidence/tasks/feature-003-live-development-v2.md. No runtime tuning
between cases; no independent holdout/human/release claims. Pending T074/T075.

## Completed maintenance context

User authorized option1 diagnosis/fixes and short guide in milan. T068–T072 complete:
safe allowlisted repair reasons, prompt v2 for new attempts, last request/repair
restricted to drafting, bounded async provider cleanup, opt-in Cyrillic glossary
lookup and separate unvalidated development config. Original config/prompt/results
unchanged. .env unchanged; no new API calls, installs, model switch or Git publication.

Executed RED→GREEN; full backend814 PASS (791+23), Ruff/diff PASS. Isolated actual
local HTTP/CLI test-provider journey8/8 PASS. No browser/manual UI/frontend rerun.
Local ignored guide: milan/feature03-provere-v2.md,144 lines. Evidence:
evidence/tasks/feature-003-reliability-v2.md and baseline manifest. Original runtime
at cd98ea021a38b362b5766c4e23a1e55ec0ad0dcd; old frozen-source audits must use it,
not the changed development checkout. Of42 baseline files only3 expected runtime
sources changed, other39 match. Ignored raw live-v1/judge-v2/retrieval-v1 archives
ABSENT here: no fresh raw-integrity/exact old-rejection/outlier-cause claim.

Original quality0/8, retrieval0.50/0.50, demo2/5-within90 and7496.290s outlier remain
FAILED. No old batch replay/unused-budget reuse. New independent quality estimates
need a NEW versioned protocol/fresh holdout. T062 producer review, T063 partial
authored guards, T064 real adapter, T066 actual teammate reproduction/human review
and T067 final feature Converge remain pending. V2 focused review is not T067.
Next: review v2 and scope/freeze a bounded development-only live test on new
synthetic input before fresh independent evaluation. Producer integration is a
separate pending team dependency. No additional live execution authorized here.

## Historical handoff — 2026-11-15 (superseded current next step)

User-authorized post-hoc report-judging-v2 replaces BOTH human rating roles.
User approved max6 new gpt-6-luna judge attempts; actual3/6, all200, no retries.
All8 primary/5 secondary outcomes accounted; 48 rated units across3 independent
stateless requests (H02/H05 primary, H02 secondary). Ten failed role/outcomes
retained without invented claims. Raw outputs/disagreement immutable; same-model
agreement is not independent human validation. No Vedran/Milan signatures.
Conservative quality0/8 pass (target7/8): six generation failures; H02/H05 gaps.
H02 support4/4, coverage11/13; H05 support5/5, coverage6/9; missingness false.
One unresolved additional-issue disagreement retained, no automatic pass.
Judge31,082 tokens known, no unknown judge usage; spend unknown. Generation
ledger remains86, original13 live outcomes/16 source/10 retrieval hashes unchanged.
T056 retrieval0.50/0.50 and live demo2/5-within90/outlier7496.290s remain FAILED.
T059/T060/T061 checked for executed automated evaluation/audit, not acceptance.
791 backend/15 targeted PASS, Ruff/diff PASS; no runtime/producer changes.
Evidence: evidence/tasks/feature-003-automated-evaluation.md and
feature-003-judge-results.json. Ignored raw/sealed outputs: judge-v2/ under
evals/results/feature-003/. Do NOT rerun completed batch or reuse unused budget.

T065 fixture regression complete. T062 source reconciliation partial; actual
producer/affected-consumer review pending (user awaiting ML/data teammates).
T063 authored guards partial; real T064 adapter unstarted pending that interface.
T066 docs complete, actual teammate reproduction/human code review still pending.
T067 unstarted. No generation rerun, tuning, model switch, Git publication.
Next: receive actual producer/consumer decision on the prepared SHA-pinned
context/history review packet: evidence/tasks/feature-003-context-review.md.
Earlier detailed history remains in task evidence and prior Git handoffs.
