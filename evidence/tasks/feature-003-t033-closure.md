# T033 capability verified - 2026-11-15 Europe/Belgrade

Branch feature03, baseline/current HEAD cf218b0359cededfb2e201fd251b5361cb4c5d03.
Preexisting provider-access/next_work/prompt/instrument edits from preparation
preserved. User confirms key entered; separately approved new maximum FOUR
transport attempts, including connection failures. Original two-attempt record
is untouched. [Request/budget](../../prompts/development/003-investigation-t033-resume-2026-11-15.md).
AGENTS/next_work read first; scoped skill/prerequisites/checklist reviewed during
resume preparation, no extension hooks. No model substitution/T058/publication.

## Actual diagnosis and correction

New attempts 1 and 2 both returned HTTP 400 invalid_request_error /
invalid_json_schema for text.format.schema. First diagnostic context identified
properties/citations; compiled citations contained uniqueItems. After omitting
that keyword from provider projection, the next rejection specifically mentioned
pattern. Projection used the local exact-end negative lookahead; changed its
outbound form to portable `$`. Both changes are ONLY in compile_report_schema.
Original closed schemas/local ReportDraft validation/uniqueness/terminal-newline
rejection stay intact. Not a relaxation of application acceptance or evidence rules.

Each fix had an actual assertion RED before implementation (one failed test each),
then GREEN. Final targeted SDK/probe/diagnostics/validation **54 PASS**, exit 0.
First preparation-only diagnostic set had 25 PASS. No import/collection failure
claimed as business RED. These local checks use authored data/MockTransport and
isolated temporary .env paths; they never read the real key or call the provider.

Official documentation consulted for the strict provider schema subset:
[Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs).
The observed rejection fields, local schema inspection and subsequent successful
unchanged-model probe support this compatibility diagnosis. Raw error bodies
were intentionally not retained; no claim to recover the previous historical
HTTP 400's complete message or to know more than the captured metadata.

## Four-attempt ledger and verified outcome

| New attempt | HTTP | Request ID | Outcome |
|---|---|---|---|
| 1 | 400 | req_e1a212e784e046c7845b9e769a684529 | schema rejection, citations context |
| 2 | 400 | req_1ee6e6a438f146c1ae42d1297b928caa | schema rejection, pattern mentioned |
| 3 | 200 | req_82d8930d95754021bccf4293f01c794b | forced get_case_facts with exact empty arguments |
| 4 | 200 | req_ede28d9ab9ac46349ebc6cc6c62babac | structured needs_information draft, local schema valid |

Requested AND returned model: **gpt-6-luna**. First successful turn is tools,
second draft. Final probe status capability_probe_passed, shell exit 0, elapsed
8.188 seconds for successful two-turn probe. Two failed runs preceded it, retained
in full metadata ledger; their observed shell results were nonzero. Exactly 4/4
new attempts used, no fifth call, model-list request, SDK retry, fallback or repair.
Prior two attempts are historical, not charged against this explicitly new budget.

The probe sends only authored CASE-000/TX-000 zero-value diagnostic data, scoped
aliases, tool definitions and compiled report schema. No actual case/corpus,
evaluation reference or customer data. store=false, parallel tools disabled,
SDK max_retries=0, bounded transport/request/input/output/deadline unchanged.
Root .env was read privately after explicit user setup; key never printed,
included in browser, record or Git. .env is ignored; private exact-key scan over
all changed/untracked shareable files PASS.

Reported usage for successful turns (no guessed prices):
- Tool request: input 1093, output 16, total 1109 tokens.
- Draft request: input 1146, output 127, total 1273 tokens, including 63 reasoning
  tokens in the reported output detail; 1071 input cache-write tokens reported.
- Sum of known successful usage: input 2239, output 143, total 2382. Usage for
  rejected requests is unknown; do not call this sum total billed usage or spend.

[Safe metadata results](feature-003-t033-resume-results.json),
[bounded opt-in instrument](feature-003-t033-resume.py),
[source/schema compatibility bindings](feature-003-t033-compatibility.json).
Provider schema SHA-256:
82c812097e243153b0ffba80cec7259a6ca6afd285ee59c013c7df5e1ca9b7bb.

## Commands, regression and preservation

Actual authorized invocation (run three times within one durable capped ledger;
each network command required sandbox escalation):
```powershell
$env:PYTHONPATH=Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-t033-resume.py
```
Ledger .cache/t033-resume-20261115.json counts and saves BEFORE network I/O.
Default tests do not execute this opt-in script's main function. Three additional
diagnostic tests validate redaction, safe schema paths and four failed transports
followed by refused fifth dispatch, using entirely authored mock transport.

Full final `uv run --locked pytest backend/tests --basetemp "$runRoot/temp" -o
"cache_dir=$runRoot/cache" --tb=short`: **755 passed in 54.62s**, exit 0.
Actual unique absolute runRoot:
`.cache/t033-regression-dc8e2a005a65488aab4c137e576803cf` under project root.
Ruff PASS. No frontend changes; frontend/browser checks not repeated. Python
3.14.3, SDK OpenAI 3.51.0, existing locked dependencies; no upgrade/install here.

Retrieval freeze/code/glossary/cutoffs and original internal schemas unchanged.
Provider source is legitimately newer than original T052 inventory; the audit
accepts this source change only when bound to this successful probe record and
exact new provider-source hash. T056 results remain frozen, below retrieval targets,
not rerun or retuned. No replacement of the old model-unknown live freeze with an
invented retrospective success: T058 must freeze current verified model/settings/
prompt/compiled-schema/runner before real case generation.

T033 checked complete: actual tool+report-schema capability verified. This is NOT
report quality evaluation, live case safety acceptance or authorization for T058.
The four-attempt budget is exhausted. No T058/T059, human ratings, commit/push/
merge/deploy performed. Next step is separately scoped T058 runner/live execution
authorization with an explicit new provider-call budget.
