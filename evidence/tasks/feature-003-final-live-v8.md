# Final live check and merge preparation — 2026-11-16

User authorized continued work and commits, expressly requiring waiting before
merge into feature03. Runtime baseline1936d23; no application/prompt/config edits.
Design: [final-live-check.md](../../specs/003-ai-investigation/final-live-check.md).
Original request: [prompt](../../prompts/development/003-final-live-check-2026-11-16.md).

Three fresh authored template cases: two ordinary quality cases (incomplete
mixed-currency history/guidance and unavailable history/no-match), plus one
separate controlled missing-notice candidate. Preserve original real model output
and SDK history; remove the exact notice from an authored candidate only. Normal
strict validation must reject it and the next real LLM draft must restore it.
This is controlled application recovery, not a natural model-mistake claim.

Ordinary denominator2 including failures. Separate diagnostic rating. Same-model
single stateless judge with3 opaque calibration packets; expected labels remain
outside generation/judge input. Preserve support90%/coverage80%/zero critical/all
disclosures; no independent/human evaluation or full acceptance claim.

New development-v8 pack, ignored raw directory and durable ledger. Max25 actual
transports,8/case,1judge; existing8requests/12tools/1repair/1retry/30s/120s/48k/4096/
2MiB generation limits. Judge60s/8192tokens/200k input. Quota/rate/access stops
further dispatch. No tuning between outcomes or replay of completed batches.

Preparation: scoped speckit-implement, feature003 selected, checklist16/16 PASS,
no extension hooks. RED1 intended missing omission-fault behavior/4 passed,
GREEN8 harness tests. Full backend **919 passed69.01s**; frontend **186 passed**;
typecheck/build/Ruff/diff PASS. Existing environment/locks; no installs. Frozen
inputs/references/source/prompts/config and44 previous artifact hashes verified.

```powershell
.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short
.venv/Scripts/ruff.exe check backend evidence/tasks/feature-003-final-live-v8.py evidence/tasks/feature-003-final-live-v8-inputs.py
# frontend working directory:
npm.cmd test -- --run
npm.cmd run build
# repository root:
$env:PYTHONPATH = 'backend/src'
.venv/Scripts/python.exe evidence/tasks/feature-003-final-live-v8-inputs.py
.venv/Scripts/python.exe evidence/tasks/feature-003-final-live-v8.py
```

Builder/freeze commands above record completed preparation; never overwrite or
replay a completed execution. Next step after preparation commit is one --execute,
then --audit and a merge-readiness review without merging. Live outcomes pending
at preparation; final evidence appended after the single execution.
