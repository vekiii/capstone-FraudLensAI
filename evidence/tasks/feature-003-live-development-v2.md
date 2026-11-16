# Actual live development check v2 — 2026-11-16

Current status: **live development run and automated assessment completed**.
Preparation history follows, then actual results. User authorized
publication then actual LLM quality checks; [original request](../../prompts/development/003-live-development-v2-2026-11-16.md).
[Protocol/design](../../specs/003-ai-investigation/live-development-v2.md).

## Publication and preparation

Created feature03-reliability-v2 from local feature03 cd98ea0, committed maintenance
as **7ed606c91c0bdc8b44c7318d1ad1d87e8d1bc31e**, pushed to origin with upstream.
Local feature03 remains cd98ea021a38b362b5766c4e23a1e55ec0ad0dcd. No force/merge.
Git writes required sandbox escalation; authorized operations succeeded, no
automatic-review rejection. Staged18-file secret/exclusion check PASS; private
.env, ignored milan guide, local/generated artifacts were excluded.

New development inputs/expectations/protocol under evals/investigation/development-v2.
Assistant-authored; independent human review pending. No old holdout read/replay.
Cases: new exact-money EUR with incomplete multi-currency history; new GBP with
unavailable history; new USD with explicitly controlled no-guidance retrieval.
The third uses a high cutoff only to produce controlled no-match, not to claim
quality of that retrieval configuration. Runtime remains the published v2 source.

Existing strict limits unchanged. Operator chose max25 total transports under
user's general authorization (not a user-quoted numerical approval):8/case and
one stateless same-model batch judge. Reservation persists before I/O and counts
connection errors. No automatic case/judge replay after ambiguous prior dispatch.
Freeze binds source/prompt/schema/settings, new inputs/reference hashes, corpus,
candidate/control configs and SDK3.51.0. Actual key excluded from serialization.
Generator never parses reference.json; judge opens it only after all3 outcomes
are exclusively sealed. Same-model single judge is not independent human validation.

## Executed preparation checks

Initial transport-cap RED: **7 failures**, intended unimplemented reservation,
not import errors. GREEN7. Added durable/replay/reference guards and actual SDK
serialization over MockTransport; final targeted **34 PASS** (19 runner +15 judge).
Mocked generation/judge calls are authored transports, never actual API calls.
First ad-hoc input authoring used unsupported coverage spelling partial; schema
rejected before any dispatch/file publication. Authored builder corrected it to
the existing contract value incomplete; no schema/contract weakening.

Scoped speckit-implement, explicitly selected feature003, prerequisites PASS;
requirements checklist16/16, no extensions.yml hooks. Existing Python3.14.7 and
locked dependencies reused, no installation. Commands actually executed:

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
powershell -NoProfile -ExecutionPolicy Bypass -File .specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-live-development-inputs.py
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_investigation_live_development_v2.py -q --tb=short --basetemp=.cache/live-development-v2/red-tmp -o cache_dir=.cache/live-development-v2/red-cache
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_investigation_live_development_v2.py backend/tests/unit/test_investigation_judging.py -q --tb=short --basetemp=.cache/live-development-v2/green3-tmp -o cache_dir=.cache/live-development-v2/green3-cache
.venv/Scripts/python.exe -m ruff check backend evidence/tasks/feature-003-live-development-v2.py evidence/tasks/feature-003-live-development-inputs.py
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-live-development-v2.py
```

Ruff/diff PASS. Prepare returned frozen_not_dispatched,3cases,max25. No application,
producer, frontend or old evaluation artifacts changed in this follow-up.
Full backend regression **833 PASS in42.44s**, exit0 (814+19 runner checks):
`.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short --basetemp=.cache/live-development-v2/full-tmp -o cache_dir=.cache/live-development-v2/full-cache`.
No live outcome, usage, quality rating or spend is inferred from preparation.

## Actual execution and results

Setup/protocol committed/pushed as **103c3c0**, then executed exactly once:

```powershell
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-live-development-v2.py --execute
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-live-development-audit.py
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-reliability-diagnose.py
```

Runner exit0 means completed execution/aggregation, not all cases passed. Actual
**17/25 transport attempts:16 generation +1 judge**. **16 HTTP200**,1 generation
attempt without response headers. No model switch, case rerun or extra judge;
all3 original outcomes retained. Returned model gpt-6-luna on all16 completed
provider responses. No runtime/prompt/retrieval/expectation changes between cases.

| Case | Actual result | Seconds | Requests/tools | Automated support | Essential coverage | Development pass |
|---|---|---:|---|---|---|---|
| DEV2-701 incomplete multi-currency history | failed,budget_exhausted; no report |37.971|5/4|N/A|N/A|FAIL|
| DEV2-702 unavailable history | needs_information |21.054|5/4|4/4|4/5 (80%)|PASS|
| DEV2-703 controlled no guidance | needs_information |21.051|6/5|4/4|5/6 (83.33%)|PASS|

All three used zero repairs. **2/3** yielded validated drafts within90s; all three
terminated within120s. This is descriptive on this development sample, not the
separate five-case release criterion. First case's fifth dispatch had no headers
for29.987s and unknown provider outcome/usage. Together with the fixed30s request
limit,5<8 requests and37.971<120 total, this is consistent with per-request timeout,
not exhausting8 dispatches/120s. Underlying provider/network cause is unknown;
the recorded public code remains budget_exhausted. Do not assume it cost zero.

Single stateless same-model judge completed and rated all units of both existing
reports. Generation failure remains failed with no invented claim ratings.
On those TWO reports only: **8/8 observational units supported**, **9/11 essential
units present**, **1/1 procedure applicable**. No-guidance case has zero procedural
units (applicability N/A, not100%). Both drafts had correct missingness and no
critical unsupported claim/additional issue according to this machine judge.
Missing E01 coverage: explicit statement that transfer is not bank loss; on703
also explicit focal transaction ID. These compound predeclared requirements were
not relaxed after scoring. Same-model judgment is not independent correctness.

Usage reported for16 completed responses: **56,917 input +7,354 output =64,271
known tokens**, plus1 attempt with unknown usage; actual spend unknown. Judge
cost/latency not counted as a case-generation latency. No pricing invented.

## Actual post-run audit and boundaries

Audit PASS, exit0. [Safe machine results](feature-003-live-development-v2-results.json)
include exact hashes, denominators, timing/usage/status counts. Nine raw/metadata
artifacts sealed and hash-bound under ignored evals/results/feature-003/development-v2.
All source/protocol hashes still match pre-dispatch freeze; all3 context/input/
corpus/retrieval bindings and report validation rechecked. **8 cited IDs resolve**
to the exact saved evidence; zero unknown IDs. Same-model raw judge response/rating
and packets preserved; no raw outputs/SQLite/opaque reasoning/key committed.

Original baseline42-file check PASS: only the expected three runtime maintenance
sources differ from cd98ea0, other39 original files unchanged, including old
protocol/holdout/reference/summary artifacts. Old raw execution archives still
absent here; no fresh old-raw-integrity claim. Local .env unchanged. Git publication
checked private-key absence and excluded local/generated files before staging.

The DEV2-702 language metadata says sr-Cyrl but its authored instruction/query hints
are Latin Serbian, as on the other cases. No live Cyrillic/cross-language quality
claim follows; offline script-equivalence checks remain separate. This metadata
limitation is disclosed without rewriting the frozen inputs.

Original0/8 quality,0.50 retrieval and failed original demo/outlier remain unchanged.
New2/3 is **not a comparable before/after improvement estimate**: different
development cases and a single automated primary judge, no independent reference
review/secondary judge/human validation. Producer integration and T066/T067 remain
pending. Do not spend unused8 attempts or rerun the completed batch to replace the
failed case. Next concrete work: diagnose the30s no-header timeout with offline
regressions before planning any separately bounded new live revision.
