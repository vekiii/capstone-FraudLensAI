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

## Final observed outcomes

Preparation committed as **dd140af** before actual dispatch. Executed ONCE:

```powershell
$env:PYTHONPATH = 'backend/src'
.venv/Scripts/python.exe evidence/tasks/feature-003-final-live-v8.py --execute
.venv/Scripts/python.exe evidence/tasks/feature-003-final-live-v8.py --audit
```

**18/25 actual transports:17 generation+1 judge, all HTTP200 gpt-6-luna**.
Known86,241 input+15,376 output = **101,617 tokens**, unknown usage0, spend unknown.
No timeout, quota/access error, transient retry or stopped/not-executed case.
All attempts finished within90/120s, all final reports include the exact notice.

| Case / role | Outcome | Seconds | Requests / tools / repairs |
|---|---|---:|---|
| DEV8-781 ordinary | ready_for_review | 46.789 | 6 / 4 / 1 |
| DEV8-782 ordinary/no guidance | needs_information | 26.687 | 5 / 4 / 0 |
| DEV8-783 controlled omission | needs_information | 38.841 | 6 / 4 / 1 |

Ordinary781 naturally needed one `assertion_scope_mismatch` repair; actual repair
input38,925bytes, then a valid report. Ordinary782 had no repair and included the
human-authority notice. Controlled783 rejected the deliberately missing notice
with `human_authority_notice_required`, sent one real35,580-byte repair, then
validated the next actual LLM report. This proves the intended runtime recovery
within48,000 bytes. Raw drafts/continuation were preserved; no fabricated claim of
a natural omission. The controlled case remains excluded from primary quality.

## Quality gate did NOT pass

The judge's **raw** ratings favored both ordinary reports (support6/6, coverage
19/19, procedural1/1 with other N/A, no critical flags) and the diagnostic final
report (support3/3, coverage7/7, procedure2/2). These are retained raw observations,
**not accepted quality scores**: calibration matched **2/3**, so
`quality_assessment_valid=false`, `passing_development_reports=null` and
`controlled_report_quality_pass=null` as required by the frozen method.

CAL8-B contains an intentionally fabricated source-of-funds allegation. The judge
correctly marked its claim unsupported/critical, but marked missingness_correct
true because the limitations separately disclose the unknown fields. The expected
control label was false. This disagreement alone fails the strict calibration
gate; it does not show that the critical allegation was missed. Raw interpretation
and expected label are retained. Do not change expected labels, thresholds or
rerun the judge to obtain a pass. Resolving this rubric/control ambiguity and
independent quality validation remain explicit follow-up work on feature03.

Thus the final technical check succeeded; **LLM semantic quality remains
unconfirmed**. No independent/human review or improvement/release claim.

## Integrity and merge preparation

[Audited result](feature-003-final-live-v8-results.json): integrity **PASS**, distinct
from the failed calibration gate. Runtime/prompt/policy/config/input identities
verified against actual bindings; all44 previous artifacts preserved. Ten new
raw/metadata hashes,13 cited evidence IDs resolve. Source unchanged throughout;
single schema, repair tool_choice=none, exact invalid candidate rejection,
original private-item hashes and existing caps verified. No further API calls.
Unused7 transports are not a reusable allowance. No historical outcome regraded.

[Merge review](feature-003-merge-readiness.md): focused agent review found no
blocking code defect; current feature03 is an ancestor and non-mutating merge
preview is conflict-free. Backend919/frontend186/typecheck/build/Ruff PASS.
No fresh browser/process journeys; earlier results distinguished. Public schemas,
frontend, dependencies and producer adapter unchanged. Full acceptance/human/
producer/reproduction/convergence and original failed targets remain pending.

Completed evidence and handoff committed as a separate logical unit, per user
authorization. **WAIT before actual merge**. Joint review may accept scoped fixes
back into ongoing feature03 work while retaining unresolved quality tasks. No
automatic additional prompt revisions, evaluation batches or actual merge here.
