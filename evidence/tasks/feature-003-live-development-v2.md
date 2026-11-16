# Actual live development check v2 — 2026-11-16

Current status: preparation frozen, live dispatch not yet started. User authorized
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
