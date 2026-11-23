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

## T098 actual-publication availability check — 2026-11-18

On feature03-retrieval-v4 at038f728, actual configured producer dataset/run
paths are absent. Only local investigation/evaluation stores and cached controlled
smoke/test files were found in the reachable workspace; the three producer-shaped
smoke files exactly match historical authored-store hashes. Raw IBM CSV presence
does not establish published rules/model output. Some old cache directories are
inaccessible; no exhaustive claim about stores elsewhere. Default investigation
configuration is disabled/fixture/test; foundation case API/UI remain fixture
composition, and loopback8000 health/cases GETs were unavailable.

Actual producer run/dataset/model identities/source hashes and real API/matching
worker, bounded-history/source-switch/archive validation are **UNRUN**. T098
stays unchecked; T062–T064 completed compatibility scope remains unchanged.
Existing controlled adapter/context/API regression:44PASS7.68s,exit0; not actual
producer validation. Missing-file DatasetReader probe failed unavailable without
creating a file or fixture fallback. No live provider calls, labels, imports,
training, producer writes, report generation, commit/push/merge or contract changes.

[Full availability evidence and exact producer delivery/execution packet](feature-003-t098-20261118.md),
[machine results](feature-003-t098-20261118-results.json).
Next: obtain consistent published dataset + actual rules/model run snapshots,
producer/model/version/hash/alert identities and compatible application launch
boundary, then exercise the existing adapter/API/worker with test provider.
SC-003 report quality and SC-006 live timing remain separate unmet criteria.

### T098 private package follow-up — 2026-11-18

Actual supplied ZIP verified:15/15 payload SHA-256 values PASS; its MANIFEST
matches the published21ec67d0 identity. Model and five saved producer examples
selectively extracted to ignored cache, no deserialization/inference. ZIP has
zero SQLite stores; canonical/history dataset and actual published rules/model
run databases remain unavailable. Sample JSONs do not replace them. Per user's
explicit instruction, stop before local producer preparation and request a
choice: ready-made store transfer or new isolated import/history/scoring using
the verified CSV and transferred model, without training. No API/worker/live
provider execution or T098 completion claimed. [Evidence/options](feature-003-t098-handoff-20261118.md)
and [results](feature-003-t098-handoff-20261118-results.json).

### T098 actual local producer integration complete — 2026-11-18

User selected new isolated producer preparation from matching IBM CSV + transferred
trained model, without training/merge. Actual5,078,345 canonical events/history-v1
snapshots,3,963,424 scoreable/1,114,921 warm-up. Producer93d387e schemas unchanged
versus reviewed487c427;20 genuine model inferences/publications, native score parity
0.0 on already-exposed validation selection, separate daily-policy run,20 actual
rules assessments with unchanged no_alert/0 published cases. Full-population ML
prediction/utility and merged case UI remain separate Feature002 work.

Actual5s full-source scan interruption required an opt-in separate consumer-owned
history index (no source schema/bytes/labels change). RED7 -> full1081PASS; paired
SHA settings/read-only guards, legacy behavior/archive reads retained. Independent
all5,078,345-row oracle exactly matches10 real sender/receiver histories, including
four >50 results with exact all-eligible direction/currency totals. Real investigation
API ASGI + matching CLI worker across two actual model snapshots PASS; idempotency,
409 source-switch, archive/evidence equality and404 no-alert rules boundary PASS.
Actual missing source remains unavailable/null, not empty or fallback; archive200.
Both reports are explicit scripted TEST needs_information, not live AI quality.

Persistent ignored stores: data/processed/feature-003-t098-20261118. All five frozen
source/run/index hashes unchanged across exercise;56 protected non-backend history
artifacts unchanged, current optional-index runtime changes documented separately.
T098 checked in this actual bounded-model/full-history scope; no training/live calls,
benchmark/holdout evaluation, regrading, commit/push/merge or full feature acceptance.
[Full execution](feature-003-t098-local-20261118.md),
[IDs/hashes/checks](feature-003-t098-local-20261118-results.json),
[index design](../../specs/003-ai-investigation/history-index-v1.md).
