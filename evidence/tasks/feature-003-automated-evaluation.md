# T059–T061 automated evaluation implementation — 2026-11-15

**Current status: T059/T060/T061 completed under user-authorized post-hoc automated
report-judging-v2. Quality targets FAILED; this is not human validation or full
feature acceptance.** Preparation/gate text below is historical; closure follows.

Scope: [actual request](../../prompts/development/003-investigation-t059-t061.md).
Baseline aaabd8dec787d83e1b50bc2972e8182162ca6225; existing user-authorized
uncommitted judging amendment/docs preserved. AGENTS/next_work read first;
scoped speckit-implement applied, SPECIFY_FEATURE_DIRECTORY selected explicitly,
prerequisites PASS; requirements checklist 16/16, no extensions.yml hooks.

## Implemented and tested independent work

- Versioned [judge prompt](../../prompts/evaluation/report-judge-v2.md), closed
  rating schema and strict unit/kind/identity validation in offline-only
  `backend/src/fraudlens/investigation/judging.py`. No runtime imports or changes
  to frozen evaluation.py/provider/prompt/retrieval source.
- [Runner](feature-003-judge-run.py) builds 13 role/outcome packets, 48 units:
  primary eight outcomes (H02/H05 have drafts), secondary fixed five (only H02
  has a draft). Ten failed role/outcomes retained without invented claim ratings.
  Three isolated stateless Responses requests planned, no previous response or
  primary judgments in secondary input. No tools or generation rerun.
- Fresh judge freeze binds packets, amendment, prompt/schema/source/model/limits
  before dispatch. Durable separate ledger reserves/counts actual transports;
  max_retries=0 at SDK/HTTP layers, at most two attempts per packet and six total.
  Existing T058 86/104 ledger is never spent/rewritten. Saved successful judge
  outputs reused; unknown prior dispatch is refused, not silently replayed.
- Exact raw machine responses/usage and sanitized error types, actual model,
  request IDs, timestamps/durations, packet hashes and ratings saved separately
  under ignored `evals/results/feature-003/judge-v2`. No Vedran/Milan signatures.
- Conservative aggregation preserves both raw rating sets and disagreements;
  unresolved disagreements cannot pass even at 90% support. Missingness, critical
  flags and unlisted unsupported prose prevent a pass. Zero-claim support N/A,
  failed reports retained, unchanged >=7/8 and support/coverage targets.
- [Audit/aggregation command](feature-003-judge-audit.py) binds original live
  outcomes, contexts/reports/evidence, judge metadata and freeze; computes exact
  citation-ID resolution separately from semantic grades, carries original
  retrieval/live timing failures, usage-known/unknown and unknown spend, checks
  runtime modules do not import offline judge/reference evaluator.

## Actual TDD / verification

13 intended business RED assertion failures (no import/collection errors), then
13 GREEN. Additional disagreement-at-90%-support test RED then GREEN; 14 GREEN.
Actual SDK serialization over controlled MockTransport verifies three stateless
requests, store=false/no tools/no previous response/no other judge judgments,
and exact three transport reservations. Final targeted module **15 PASS**.
Those three SDK requests are synthetic test transport only, not real API calls.
Final full backend **791 PASS in 40.39s**, exit 0; Ruff and git diff --check PASS.
Original 13 live outputs, 16 generation source hashes and 10 retrieval artifacts
hash-verified unchanged; generation ledger still 86. No frontend changes; no
unnecessary browser/frontend rerun. Final small runner timing/error handling
edits verified by targeted SDK/boundary checks after the full run.

Commands from root (unique .cache parent created before pytest):

```powershell
$env:PYTHONPATH=Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-judge-run.py
# prepared_not_dispatched: 13 packets, 3 requests planned, 48 units; exit 0
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_investigation_judging.py --basetemp "$testRoot/tmp" -o "cache_dir=$testRoot/cache" -q --tb=short
.venv/Scripts/python.exe -m pytest backend/tests --basetemp "$fullRoot/tmp" -o "cache_dir=$fullRoot/cache" -q --tb=short
.venv/Scripts/python.exe -m ruff check backend evidence/tasks/feature-003-judge-run.py evidence/tasks/feature-003-judge-audit.py
```

## Execution gate / honest status

Actual judge execution **not run**, real new provider transports **0**. User
question pending: approve at most six new attempts for gpt-6-luna, including
errors/retry, for the three judge jobs only; pricing unknown. Required by the
[authorized successor protocol](../../evals/investigation/amendments/report-judging-v2.json)
judge.transport_budget=null and its explicit separate-budget limitation, plus
the [decision record](feature-003-judge-amendment.md) execution boundary. The
previous 104-attempt scope covered eight report generations/five demos, not
offline judge scoring. No actual review/model/usage result fabricated.

T059 partial (implementation/preparation done; machine ratings/comparison pending),
T060 partial (aggregator implemented; actual semantic metrics unavailable),
T061 partial (preservation/privacy audit available; final judge lineage audit
awaits actual ratings). All three checkboxes remain empty. Six failed primary
reports mean unchanged SC-003 already cannot meet seven-of-eight even if every
existing draft scores perfectly. Method is post-hoc automated, not original
prospective human validation or independent new holdout. No corpus/prompt/rank
tuning, report regeneration, producer integration, T062+, Git publication.

After explicit budget approval only, run:
`.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-judge-run.py --execute --approved-cap 6`,
then `feature-003-judge-audit.py`, inspect outputs and finish aggregate/evidence.
Do not treat this documented command as execution or as budget authorization.

## Actual execution and closure — 2026-11-15

User explicitly replied **“Odobravam najviše 6 pokušaja”** to the three-job
gpt-6-luna judge request; approval appended to the original task prompt. Started
with no judge ledger. Executed runner `--execute --approved-cap 6`, exit 0.
Actual **3/6 transports**, all HTTP 200/completed; **no retries** or further calls.
Requested/returned model gpt-6-luna on all three independent stateless requests:
primary H02 17 units, primary H05 14, secondary H02 17. Same model as generator,
separate contexts without primary output; no claim of independent human evidence.
Other six primary/four secondary outcomes are preserved failures without report,
not invented claim ratings. All eight primary/five secondary outcomes accounted.

Actual judge usage reported for all three requests: **25,159 input + 5,923 output
= 31,082 total tokens**. Unknown judge-usage dispatches: **0**. Spend unknown;
no pricing lookup/estimate invented. Generation usage remains a separate known
subset of 325,196 tokens with five reserved slots without reported usage, and
old generation transport ledger remains 86. Judge cost/latency not conflated with
the five original demo executions. Unused judge budget is not spent on rerating.

### T059 ratings and disagreement

Both raw sets and response metadata preserved in ignored judge-v2, exclusive
sealed result files. Automated evaluator identities are openai/gpt-6-luna,
actual timestamps/durations/request IDs retained, never Vedran/Milan signatures.
H02 unit judgments agree; report-level additional_issues differs: primary flags
the unsubstantiated statement about procedure search returning no results;
secondary lists no additional issue. Both rate missingness_correct=false and
critical_error=false. Original ratings retained unchanged; disagreement recorded
**unresolved**, conservatively keep the primary issue and deny report pass. No
third-call adjudication, erased disagreement or model-authority resolution.

### T060 measured results

| Primary | Supported factual units | Essential coverage | Missingness | Pass |
|---|---|---|---|---|
| H02 | 4/4 (100%) | 11/13 (84.62%) | incorrect/incomplete by both judges; additional-issue disagreement retained | FAIL |
| H05 | 5/5 (100%) | 6/9 (66.67%) | incorrect/incomplete | FAIL |
| H01/H03/H04/H06/H07/H08 | N/A, no report | N/A, no report | failed generation retained | FAIL |

Overall **0/8 pass**, target >=7/8 FAILED. Support on nine rated observational
units is 9/9; essential coverage on 22 applicable units is 17/22 (77.27%). These
denominators cover the two existing drafts only, not eight successful reports.
Zero unsupported critical claims identified in those drafts by the judges; six
absent reports do not become semantically successful. Procedural units **0**,
applicability **N/A**, not 100%. All **6/6** cited evidence identities resolve to
the exact saved evidence set; ID validity is distinct from the judge's semantic
and missingness assessment. Full prose was also scored via report-level flags.

Existing T056 baseline/improved held-out Recall@5/MRR@5 **0.50/0.50** each remain
below target; no-match **4/4**, timing p95 **2.8737/2.4578 ms**, no re-evaluation.
Original five-demo live success-within-90 **2/5**, target >=4/5 FAILED; terminal
by120 **false**, includes **7496.290 s** outlier unchanged. No performance repair,
report regeneration, new holdout, model switch or threshold/prompt tuning.

### T061 audit and lineage

Executed `.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-judge-audit.py`,
exit 0. [Audited machine summary](feature-003-judge-results.json) records actual
metrics, raw-rating disagreement, per-role output hashes, retrieved metric-file
hashes, exact generation summary binding, usage and explicit failed quality.
Ignored `judge-v2/audited-summary.json` is sealed/exclusive. Its aggregate equals
runner summary for every rating/report/disagreement/result field. All judge
artifact seals verified; freeze binds actual prompt/schema/packets/model/source.
All **13 original live outputs**, **16 generation source hashes**, **10 retrieval
artifacts** verified unchanged. Base frozen protocol/rubric/splits remain bound by
the successor's original hashes; amendment decision is preserved without editing
its historical authorized_not_executed status. Execution state lives in this
closure and actual judge freeze/results, not retroactively rewritten protocol.

Offline references were deliberately opened only after generation to construct
judge packets and expectations; no generator rerun used them. Exposure is now
explicit, not a fresh prospective holdout. Runtime source AST/import checks
including main confirm no runtime judge/reference evaluator imports. Raw answers
are not copied into development prompt or runtime corpus. Original corpus
provenance/approved source reviews unchanged. T057 safety and current regression
remain distinct workflow/security evidence, not human report-quality evaluation
or ML/data accuracy. No human case disposition, source/producer approval or
T066 teammate reproduction is inferred from these machine scores.

T059/T060/T061 can now be checked as **executed automated evaluation/aggregation/
audit with FAILED quality**, under the expressly approved replacement method.
This does not close T062/T063/T064 producer work, T066 human reproduction or T067.
No new provider requests needed. Next project condition remains producing and
affected-consuming teammates' actual context/history decision (T062).

Final closure verification: full backend **791 passed in 48.65 s**, exit 0;
Ruff and diff checks PASS. Application prompt/rank/cutoff/provider sources remain
unchanged; no frontend changes or dependency/lockfile modifications. Separate
judge records are not included in the historical generation-only zero-new-call
preservation script's scope; actual new judge calls are three as recorded above.
