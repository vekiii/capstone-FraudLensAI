# Repair payload maintenance — 2026-11-16

User requested a commit of completed work, followed by fitting repair into the
existing byte limit. Completed timeout-v3/coverage-v4 work committed as **eedbe72**
on `feature03-reliability-v2`. Repair changes were initially left local; the user
subsequently requested commit/push on2026-11-16. Publication targets that same
branch; the pre-publication remote tip was verified at46a15ed. Git history and
the remote branch record the resulting commit identities.
Original request/design: [prompt](../../prompts/development/003-repair-v5-2026-11-16.md),
[plan](../../specs/003-ai-investigation/repair-v5.md), tasks T082–T084.

## Outcome and implementation

`compile_report_schema()` now shares one Claim definition instead of serializing
the same object five times. Expanded output equals the frozen old provider schema
exactly. Required fields, closed shapes, enum/string/list bounds remain identical.
Public/local schemas, exact fact/citation/quote checks, prompts and settings did
not change. This representation applies consistently from the initial request,
preserving tool definitions, the entire ordered private continuation, invalid
draft, encrypted items, exact evidence and provenance. No text/context truncation.

The actual SDK's JSON encoder measured the retained DEV4-742 pending repair:

| Measurement | Previous | Current |
|---|---:|---:|
| Provider report schema | 5,801 bytes | 2,024 bytes |
| Full repair request | 49,925 bytes | **46,148 bytes** |
| Configured ceiling | 48,000 bytes | 48,000 bytes |

Saved **3,777 bytes**, leaving **1,852 bytes**. This fixes the diagnosed size
failure; a different/larger history may still fail the unchanged pre-send guard.
The single repair/transient retry, 8 requests, 12 tools, 30 s/request, 120 s total,
4,096 output tokens and 2 MiB response limits remain. Lower configured ceilings
still apply. The old null assertion is still rejected: unavailable metadata is
not a scalar Fact and never becomes zero or an asserted `"null"`.

## Executed checks

PowerShell at repository root, existing locked environment; no installs:

```powershell
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_investigation_repair_v5.py -q --tb=short
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_investigation_repair_v5.py backend/tests/unit/test_investigation_openai.py -q --tb=short
$env:PYTHONPATH = 'backend/src'
.venv/Scripts/python.exe evidence/tasks/feature-003-repair-v5-check.py
.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short
.venv/Scripts/ruff.exe check backend evidence/tasks/feature-003-repair-v5-check.py evidence/tasks/feature-003-repair-v5-probe.py
git diff --check
```

- Initial test-authoring syntax error corrected before counting RED.
- **RED: 4 failed, 8 passed**, intended size regression: old schema5,801>2,500;
  standalone repair rejected before transport; both workflow accept/reject
  scenarios reached only4 transports instead of the intended repair request5.
- **GREEN: 32 passed** across the new12 and existing20 SDK checks.
- Full backend **882 passed in49.53s**. Ruff and whitespace checks PASS.
- SDK regression preserves every input/private item and uses one stable schema;
  an invalid repaired assertion still fails, without a second repair or report.
  Lower45,000-byte and larger-than48,000-byte requests fail without sending,
  including a caller attempting to supply a ceiling above48,000.
- [Offline SDK reconstruction](feature-003-repair-v5-results.json): PASS,
  six **mocked** requests, zero actual API calls. Last response is deliberately an
  incomplete diagnostic stub, not an invented corrected LLM report. Original
  invalid report remains invalid. Expanded schema equivalence PASS.

The existing SDK closed-shape test now permits only the single locally resolved
`#/$defs/Claim` reference and still traverses/checks its strict object definition.
The pre-change projection is frozen under
`backend/tests/fixtures/investigation/provider-report-inline-v1.json`.

## Separate actual-provider capability confirmation

After offline/full checks, ran exactly once:

```powershell
$env:PYTHONPATH = 'backend/src'
.venv/Scripts/python.exe evidence/tasks/feature-003-repair-v5-probe.py --execute
```

The existing synthetic-only probe passed: **2/2 actual HTTP200**, returned model
`gpt-6-luna`, tool call plus structured limited draft, store=false, SDK/transport
retries disabled. Request sizes3,930/4,273 bytes. Reported tokens1,413 input +160
output = **1,573 total**; no unknown usage in this probe; spend unknown. About4.70s.
No real/evaluation case/reference used, no judge calls, no old batch replay.
[Safe result](feature-003-repair-v5-probe-results.json). An exclusive pre-dispatch
freeze and two-transport ledger under ignored `.cache/repair-v5-synthetic-probe/`
prevent this completed probe runner being replayed. This verifies schema/tool
capability, not successful full-case repair or LLM report quality.

## Preservation and limitations

Before runtime edits, copied and verified every feature runtime source under
ignored `.cache/evidence-snapshots/coverage-v4/`; hashes match the frozen v4 source.
The offline checker verifies old protocol inputs/runners/prompts, all20 original
v2/v3 JSON hashes, the v3 snapshot and nine original v4 artifact hashes. All30
v2/v3/v4 JSON files remain unchanged across this check. Original raw output,
failure denominator, calibrated development2/3 and release failures remain.
Run historical source audits/size diagnoses at **eedbe72** or their original
verified snapshot; current provider source deliberately has a different hash.

No .env/dependency/frontend changes. Local guide updated, still below200 lines
and ignored. Secrets remain excluded from shareable files. Checklist16/16 PASS;
no pre/post implementation extension hooks exist. This scoped maintenance does
not execute T067 or replace pending human/producer review or fresh independent
evaluation. Next step: freeze a new, separately bounded development check that
exercises repaired full reports; retain every failure and do not replay DEV4-742.

Primary sources consulted: OpenAI documents
[shared schema definitions](https://developers.openai.com/api/docs/guides/structured-outputs#definitions-are-supported)
and [ordered reasoning/tool continuation](https://developers.openai.com/api/docs/guides/reasoning#keeping-reasoning-items-in-context).
Schema byte savings and preserved-history equality are local measurements.
