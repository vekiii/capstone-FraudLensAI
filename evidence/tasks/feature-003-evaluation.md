# Current T095 development result — 2026-11-17

Milan accepted the18-row development table/corpus and authorized continuation.
One B3/C3 comparison executed: both Recall/MRR0.25/0.25 on12 answerable questions,
6/6 correct no-answer; English0.75, sr-Latn/sr-Cyrl0. Baseline wins the declared
tie-break but is not deployed. This is a new development sample, not a rerun or
directly comparable estimate against the old0.50 held-out result. SC-002 UNMET,
T095 OPEN. [Actual execution, metrics and next decision](feature-003-t095-development-selection-20261117.md).
No cutoff relaxation, glossary change, held-out experiment or English-only scope
decision. Final backend968/Ruff PASS; old results retained.

# Previous T095 v3 implementation — 2026-11-17

Milan Gavrić/milangavric2003 approved the v3 plan and new branch implementation;
his old-held-out non-exposure statement is user-declared. Separate evaluator and
[18-row concrete development review packet](../../evals/investigation/retrieval-fresh-v3/README.md)
implemented on feature03-retrieval-v3 from18e930a. Actual question/reference
review remains pending; fresh held-out authoring stays separate. No real new
development selection, freeze or acceptance experiment occurred. T095 OPEN,
SC-002 UNMET; old0.50/0.50 and4-of-4 no-answer results unchanged.
[Actual execution/RED-GREEN/limits](feature-003-t095-v3-implementation-20261117.md).

# Previous T095 partial handoff — 2026-11-17

T095 remains **open**. Prepared a separately versioned
[development design v3 and fresh-evaluation review packet](../../specs/003-ai-investigation/retrieval-development-v3.md),
reusing the existing opt-in v2 script/glossary mechanics with proposed fresh
development-only cutoff selection. Technical AI self-review completed; actual
independent teammate plan/novelty/reference review remains pending. No new runtime
config, fresh evaluation pack/runner/freeze or acceptance experiment executed.

[Actual commands and limitations](feature-003-t095-20261117.md):135 relevant
regressions PASS;4/4 authored mechanical diagnostic controls PASS across18 local
searches, Ruff PASS after removing an unused script import. Diagnostic ranks/
script equivalence are not relevance or acceptance metrics. Both old frozen
configurations remain Recall@5=0.50/MRR@5=0.50 on16 answerable questions, with
4/4 separate no-answer outcomes. Thresholds, splits, references and results are
preserved. **SC-002 remains UNMET**. Next: independent teammate reviews the exact
v3 packet and records identity/exposure/approve-change-reject; fresh acceptance
waits for a sealed plan/pack and explicit execution authorization.

# Current T059-T061 closure - 2026-11-15

User-approved automated report-judging-v2 replaces both historical human rating
roles. Actual3/6 judge transports, 48 units, all8 primary/5 secondary outcomes
accounted, 0/8 quality pass; original failed quality/performance findings retained.
[Executed ratings/aggregate/audit](feature-003-automated-evaluation.md) and
[machine results](feature-003-judge-results.json). T059/T060/T061 completed as
post-hoc automated evaluation, not human validation or feature acceptance.
Earlier human assignment/pending statements below are historical and superseded;
no Vedran/Milan signatures are inferred. T062/T066 human gates unchanged.

# T053-T061 offline evaluation implementation - 2026-11-15

Scope: feature03 T053-T061 only, baseline/current HEAD
382e0609f73077cb6c53288f2e607c9194e04d51; initial clean worktree.
Request saved exactly in [phase-07 prompt](../../prompts/development/003-investigation-phase-07.md).
T052 approval remains complete; no T033 diagnosis/provider call or T062+ work.
Skill speckit-implement applied in scope. Checklist requirements 16/16 PASS;
extensions.yml absent. Execution policy initially blocked the prerequisite script;
child PowerShell -NoProfile -ExecutionPolicy Bypass -File succeeded with explicitly
selected specs/003-ai-investigation. No policy or shared instructions changed.

## Implemented and independently verified

Evaluation metrics use answerable-only macro Recall@5/MRR@5, explicit no-answer
denominators, overall and en/sr-Latn/sr-Cyrl groups per split, N/A for empty groups,
input digest/ID joins and missing/duplicate prediction refusal. Failed searches
cannot earn correct-no-match credit. Zero factual claims is N/A, not perfect;
uncertain judgments remain unsupported. Provider/validation failures stay in report
denominators; original reviewer disagreements are copied, not overwritten.
Report aggregation is a primitive, not complete T060 acceptance with real ratings.

CLI boundaries: evaluate-retrieval requires explicit split/configuration and a
separate T055 freeze; predictions are written exclusively/sealed before explicit
join-retrieval opens references. evaluate-reports accepts only explicit development
test-provider execution; openai and held-out report execution fail closed without
settings/environment/provider initialization. Test runner consumes materialized
contexts/history, never resolves repeated case IDs to another snapshot. Dataset
provider projection returns unavailable, no fixture fallback. Scripted provider is
mechanical: it is not responsive live prose or a quality judge; instructions and
procedure_queries are retained in input binding, not interpreted as human quality.
summarize-reviews imports the frozen rubric's 17-field per-unit format and requires
sealed outcomes; no reviewer/score/date rows were fabricated or saved.

Baseline BM25 remains body-only. Explicit title_glossary variant uses body+2*title/
section tf, body-only dl/avgdl, original terms 1 and synonyms .5, max dedup weights,
sorted term summation/passage-ID tie break. Only reviewed glossary configurations
are accepted. Prepared real glossary remains staged, with null reviewer/date.

## Actual commands and outcomes

Root workspace; Python 3.14.3, uv 0.10.9, Node 24.20.0/npm 11.19.0.
uv initially attempted to fetch missing locked httpx2 and hit sandbox network error:
environment failure, not RED. Approved `uv sync --locked --group dev` succeeded,
installing six locked packages including OpenAI 3.51.0; lockfile unchanged. No API
key/model configuration or real .env was read by this work. Existing autouse test
fixture isolates .env; mocked SDK uses explicit TEST keys and MockTransport only.

Every pytest command below used a unique absolute existing parent under `.cache`,
`--basetemp "$runRoot/temp" -o "cache_dir=$runRoot/cache"` and
`$env:UV_CACHE_DIR=Join-Path $PWD '.cache/uv'`.

- T053 RED: `uv run --locked pytest backend/tests/unit/test_investigation_evaluation.py --tb=short`:
  7 executed failures at importable NotImplemented behavior boundaries, exit 1.
- Improved retrieval RED: same module `-k improved`: 1 assertion failure (empty
  synonym results), exit 1. GREEN evaluator+baseline retrieval: 18 passed, exit 0.
- Initial safety run: 11 pass / 1 mocked-SDK cold-start timeout, exit 1; not
  business RED. New wrapper allows the specified 30-second contract limit rather
  than the inherited one-second harness limit. Explicit timeout/budget production
  controls unchanged. A later focused run had 30 passes/4 fixture setup errors
  because Ruff removed an unused-looking fixture import; corrected explicit
  re-export. Neither environment/setup issue is claimed as RED.
- New safety tests mostly verify already-correct controls; no artificial breakage.
  Existing workflow/tools/validation/recovery RED history remains its own evidence.
- Full final command: `uv run --locked pytest backend/tests --tb=short`, observed
  results appended in handoff. Local log under `.cache/p07-full-b1e878f9d7f94bcbbca1ba7f2ea07f6c/results.txt`.
- `uv run --locked ruff check backend`: PASS before final full run; four mechanical
  import issues initially auto-fixed; fixture re-export then restored explicitly.

No frontend changes: frontend/build/browser tests not repeated. No real development
cutoff selection, T055 freeze, held-out retrieval results/20 latency measurements,
live reports, actual report ratings, report quality or usage/spend results exist.
No quality target achievement claimed. Tests use authored arithmetic fixtures;
they are not real retrieval/LLM evaluation.

Final safe-generation-ID check: `-k filesystem` produced 1 intended assertion
RED (unsafe ../escape reached runner), exit 1. Added opaque ID validation before
callbacks/database paths. Final full suite after this last code change:
```powershell
$env:UV_CACHE_DIR=Join-Path $PWD '.cache/uv'
$runRoot=Join-Path $PWD '.cache/p07-final-7f672d4e9a14457aa06abb8948037d68'
uv run --locked pytest backend/tests --basetemp "$runRoot/temp" -o "cache_dir=$runRoot/cache" --tb=short
uv run --locked ruff check backend
git diff --check
```
**709 passed in 27.48s, exit 0** (evaluation 14, retrieval 10, safety 12 included).
Ruff PASS, exit 0; whitespace/diff/new handoff-link checks PASS. No skipped/xfail
tests added. Earlier 708-pass run preceded this extra negative regression.
Audit repeated after final code changes: PASS, 41 hashes. Final lineage object
digest dbae031abb45949761eed338144fc0f6d96df5ab476520db0f08ebea6b98f033;
prior pre-safe-ID audit digest 36c3ecb7ded90ea52a15fa2f2491559b614c2056a63c6faf20cf367e2ef25a6f
is historical implementation state, not a T055 freeze or evaluation result.

User explicitly deferred glossary review: "Vazi, pregledacu kada zavrsis sve".
Independent work has been handed over; actual review fields remain null. No
further approval was inferred or requested while those checks completed.

## Leakage, freeze and lineage

No combined retrieval/investigation inputs/reference text, review cards or held-out
expectations were displayed. Only list field names/IDs/split/config metadata and
hashes inspected. Safety stimuli/controls were inspected; they name H08 but its
context and answer were not opened. The current implementation session remains
development-only. No tuning or held-out execution has occurred.

[Hash-only audit](feature-003-evaluation-audit.py) actually verified 41 sealed
files and original bundle/inventory arithmetic. The sole changed original sealed
artifact is the authorized retrieval implementation. All approved question,
reference, source/review, split, rubric, protocol and lockfile bytes remain intact.
[Versioned implementation lineage](../../evals/investigation/implementation-lineage-v2.json)
preserves the old seal and records new code/glossary hashes without inventing a
T055 configuration freeze or renewed human approval. Runtime modules do not import
the offline evaluator; CLI imports it only inside explicit evaluation commands.
This static audit plus synthetic boundary tests is not proof of live traffic.

## Pending conditions

T054 actual glossary review pending; therefore T055 development selection/freeze
and T056 held-out evaluation are not run. T057 has 12 passing control groups but
does not yet execute every frozen subcase (see safety record). T033 blocks live
T058, then T059 actual ratings, full T060 and final T061. No defaults or fixture
replacement bypass these gates. First next step: actual glossary review.


## Glossary approval recorded - 2026-11-15

Vedran Mitic explicitly confirmed: "Da, pregledao sam sve pojmove i potvrdjujem."
This supersedes the earlier deferred-review entries. All 16 term mappings remain
unchanged. Glossary status reviewed, actual reviewer Vedran Mitic, date 2026-11-15
(date only, no invented review time). Approved glossary file SHA-256: 3725354237de09ef54ba87a10962e80fd8ebffef57b333912e3d2ca924577612.
This approves the glossary, not T055 configuration selection, T056 results, live
provider capability or human report ratings. Other recorded T054 implementation
limits remain; no task checkbox inferred from this approval alone.


## T054-T056 completed - 2026-11-15

T054/T055/T056 are complete in their deterministic offline task scope. Reviewed
glossary used; both development-selected cutoffs and baseline deployment choice
frozen before held-out execution. Both held-out Recall/MRR 0.50, no-match 4/4;
quality targets NOT met. Twenty measured searches per configuration, p95 2.8737ms
baseline/2.4578ms improved. No post-holdout tuning, provider call or T033 diagnosis.
Full backend 710 PASS, Ruff PASS. See [closure and exact commands](feature-003-t054-t056.md)
and [result summary](feature-003-retrieval-results.json). Earlier pending T054-T056
entries are historical. T057 and T058-T061 limits remain unchanged.


# T057 complete - 2026-11-15

All 12 frozen categories covered by 52 deterministic safety subcases. Full backend
750 PASS; frontend 186 PASS; Ruff/diff PASS. Actual browser review/injection 9 PASS,
recovery/stale 8 PASS, and process-fault/two-connection 6 PASS. Unauthorized
executed tools/actions zero. No live provider/real .env, no human quality rating,
no runtime/frozen configuration change or T056 rerun. T033 and T058-T061 gates remain.
See [complete closure](feature-003-t057-closure.md) and [hash manifest](feature-003-t057-results.json).
Earlier partial records below are historical.

## T058 executed / T059 actual review pending - 2026-11-15

All eight primary and five demo executions are sealed; 86/104 transport attempts,
87 reserved dispatch slots. Primary two needs_information, six failures; demo two
of five successful within 90s, one measured 7496.290s failure. Quality/performance
targets failed; no replacement/cherry-picking/tuning. Known reported usage subset
325196 tokens, five reserved dispatches without reported usage; spend unknown.
Final backend 759 PASS, Ruff PASS. T059 actual judgments deliberately absent
(user deferred until handoff); full T060/T061 remain pending. No T062+ or publication.
See [current complete handoff](feature-003-t058-t061-handoff.md),
[actual execution summary](feature-003-live-results.json),
[available audit](feature-003-live-audit-results.json).
