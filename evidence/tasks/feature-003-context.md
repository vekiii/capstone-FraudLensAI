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
