# T007/T008 fixture context
Date 2026-11-14 Europe/Belgrade (work began 2026-11-13). Branch feature03; baseline 6db94af3471a9007a8a0d88cba8c7ece32886483; initial tree clean.
Prompt: ../../prompts/development/003-investigation-phase-02.md. Human review pending.

Actual RED targeted module: 6 failed at unimplemented context/history/projection
boundary, exit 1; no collection errors. GREEN targeted module exit 0, 6 passed.
All pytest runs use unique absolute .cache temp/cache locations. Exact final paths
and final regression recorded in phase-02 handoff. Original foundation cases unchanged.
Explicitly authored metadata/empty history file, default availability unavailable;
no inferred bank/timezone/dataset provenance. History injected tests exercise strict
cutoff, same-minute/focal/future exclusion, bank+account identity, 7-day window,
50-event limit, empty/unavailable/truncated and per-currency Decimal aggregates.
Projection is explicit field allowlist with context/run-scoped opaque account aliases.
No actual tool/provider calls or dataset reader implemented.

## Additional privacy/snapshot tests / final GREEN
Added frozen snapshot recomputation and explicit metadata-change identity test.
History with injected reference/source/reviewer/private-label fields initially
failed privacy assertions. Replaced raw history event copies with explicit six-field
projection; no provider implementation. Snapshot uses canonical authored fixture
contents + scorer_version + metadata; fixture snapshot is not a dataset run.
Bank/account mappings in contexts.json are explicitly authored, never inferred
from foundation account strings. Default history remains unavailable despite an
empty authored events file; tests inject available histories deliberately.

Command: `uv run --locked pytest backend/tests/unit/test_investigation_context.py --basetemp D:\AIBootcamp\capstone\.cache\003-p2-12e2e8e5b06744af9a19ab2898f583d6 -o cache_dir=D:\AIBootcamp\capstone\.cache\003-p2-cache-12e2e8e5b06744af9a19ab2898f583d6 --tb=short -q`

Exit 0.

```text
........                                                                 [100%]
8 passed in 0.35s
```

## Phase 8 T062–T064 reconciliation — 2026-11-15

Current checkout feature03 at 0829296; no producer modules imported/merged.
[Producer review packet](feature-003-context-review.md) compares pinned 2dd815d
against locally available d9bd8a2: new boosted_sequential_probability enum value,
but no reviewed bounded seven-day account-history interface. Existing label-free
whole-dataset iteration and 24h feature calculation do not establish that port.
Actual producer/affected-consumer review remains pending; no approval inferred.

New `backend/tests/integration/test_investigation_dataset_context.py` separately
executes **17 authored safeguards, PASS/exit 0**, against existing boundaries.
Well-shaped ID divergence, exact directional amount/currency/time, rules scale,
cutoff, new unreviewed method, labels, source switch, missing/empty history and
strict bank/account/window/focal filtering covered. Already-correct behavior
verified without artificial RED. Initial invocation produced 17 environment
setup errors from missing basetemp parent; corrected command created parent and
passed. Actual reviewed-adapter RED is not executed, so T063 remains partial.

T064 real adapter remains unstarted/unchecked: implementing against an unreviewed
new method/history boundary would violate its explicit condition. Foundation
context reader still fails dataset mode explicitly, without fixture fallback.
Existing authored materialized workflow tests remain valid synthetic evidence,
not actual IBM rules/model-context smoke. No production context/scorer/DB/schema
change, private-label query or trained-model claim. Actual port review is the
next condition before real adapter implementation. See
[regression](feature-003-regression.md) and [handoff](feature-003-phase-08-handoff.md).

## T062-T064 implemented after explicit agreement, 2026-11-16

Baseline feature03 1f3a09d, preserving preexisting offline-review changes. Original
request: prompts/development/003-dataset-adapter-2026-11-16.md. Governance and
feature artifacts read, feature directory explicitly selected for Spec-kit
prerequisites. Requirements checklist16/16 checked, no unchecked gate. No hooks
file. Used speckit-implement scoped only to these three tasks.

T062: actual user-conveyed team confirmation and available producer SHA recorded
in [review](feature-003-context-review.md). The feature003-owned history adapter
uses the existing producer SQLite layout without a merge or database changes.
Version1/old producer pin unchanged. New dataset context2 and explicit outbound
context_contract_version2 select the separately reviewed producer snapshot.
Public run/report envelopes remain version1. Dependencies/lockfiles unchanged.

T063 RED: `.venv/Scripts/python.exe -m pytest
backend/tests/integration/test_investigation_dataset_adapter.py -q` exited1:
12 failures, all missing fraudlens.investigation.dataset, the intended absent
consumer implementation. Then implemented DatasetReader, delegation/wiring and
versioned validation. Expanded tests cover real configured service/API/archive
and tools, boosted projection, fixed read-only SQL and source switching.

Final GREEN:

| Actual command | Result |
|---|---|
| `.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short` | 936 PASS,135.61s,exit0 |
| `.venv/Scripts/python.exe -m pytest backend/tests/integration/test_investigation_dataset_adapter.py backend/tests/integration/test_investigation_dataset_context.py -q --tb=short` | 35 PASS,2.55s,exit0 after three further source-switch cases and expanded HTTP checks |
| `.venv/Scripts/ruff.exe check backend` | PASS,exit0 after final test edits |
| `git diff --check` | PASS,exit0 before documentation completion; repeated at handoff |
| `.venv/Scripts/python.exe backend/tests/support/producer_dataset_smoke.py` | PASS,exit0, actual pinned producer export and published stores |

The full suite collected936 before the three added cases; all18 new adapter tests
plus17 historical safeguards passed in the final targeted35. No claim of a second
full939-test run. Python3.14.3, Ruff0.17.4, Node24.20.0. No frontend source changes;
earlier frontend186/build/browser results are historical, not rerun for this unit.

T064: CaseContextReader/HistoryReader delegate dataset mode to the new feature-local
dataset.py; InvestigationService builds it from explicitly configured paths/source.
Missing stores never create files or fall back to fixtures. Completed active run,
source dataset and identities must match. Exact decimal strings/raw time/source
currency names remain intact; explanation source/scale/reconstruction checked.
History excludes same-minute/future/focal/foreign-bank records, returns maximum50
movements and sums all eligible movements with Decimal by direction/currency.
Raw identities become run-scoped aliases in provider evidence; private table
reads are denied and no labels enter the explicit operational projection.

Producer compatibility evidence:
[feature-003-dataset-producer-smoke-20261116.json](feature-003-dataset-producer-smoke-20261116.json).
Actual producer DatasetStore/RunStore from487c427 creates controlled canonical
records and completed active rules/model-shaped publications. Both read back
exactly equal to producer detail_active; history and provider projection PASS;
source hashes before/after equal, zero provider calls/label reads. Model values
are authored; this is NOT trained inference, model evaluation or full IBM smoke.
The producer code is exported only to ignored .cache, never merged/imported into
the running feature03 package. New code does not modify scorer/database schemas.

T062/T063/T064 consumer implementation and available compatibility checks complete.
Actual IBM import/run stores and trained model artifacts are absent locally, so
full real-population validation remains unrun and required before claiming full
dataset/model acceptance under T067/SC-007. No historical evaluation, protocol,
ratings or failed quality outcomes were rewritten. No real .env read, network,
training, package install, commit, push or ML merge in this unit.

Final HTTP follow-up: expanded the configured-service test to require404 for a
valid but absent dataset case. RED:503 instead of404 (1failed,17deselected).
Adapter now raises the existing CaseNotFoundError, preserving the public API
envelope. Final command adds test_investigation_api.py to the two dataset files:
**44 PASS,5.06s,exit0**. Ruff and final git diff --check PASS. This focused run
is after the small404 exception correction; the936 full-suite result predates it.
