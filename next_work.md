# Current handoff - repair serialization v5 complete, 2026-11-16

Branch feature03-reliability-v2. Completed timeout-v3/coverage-v4 committed at
eedbe72 per user request. Repair-v5 code/evidence included with this handoff;
user explicitly requested commit/push on2026-11-16. Remote tip before publication
verified at46a15ed. Use Git history/upstream to verify publication status.
No .env/dependency/frontend changes.

T082-T084 scoped maintenance complete. Provider schema shares one Claim definition
instead of five copies:5,801 to2,024 bytes. Expanded schema EXACTLY equals previous
provider projection. Original local/semantic/fact validation unchanged, including
rejection of the unavailable eligible_count string "null" assertion.
Entire ordered context/tools/evidence/provenance/invalid draft/private continuation
preserved. No truncation or mid-conversation schema switching. Existing limits
unchanged:8requests,12tools,30s/request,120s total,48k input,4096 output tokens,
2MiB response, one repair and one transient retry. Lower ceilings still apply;
larger histories can still fail before sending.

RED4fail/8pass; focused32 PASS; full backend882 PASS in49.53s; Ruff/diff PASS.
Exact offline SDK replay of retained DEV4-742:49,925 to46,148 bytes,1,852 spare.
Six mocked requests, zero actual calls; final diagnostic stub incomplete, no
corrected live report claimed. Prior protocols/source snapshots/hashes checked;
all30 old v2/v3/v4 JSON files unchanged. Pre-change v4 runtime now preserved at
.cache/evidence-snapshots/coverage-v4/ (ignored). Run old audits at eedbe72 or their
original verified snapshot; current provider hash intentionally differs.

Separate synthetic-only capability probe:2/2 actual HTTP200 gpt-6-luna, schema
and tool accepted;1,573 reported tokens, unknown0, spend unknown. No case/reference
or judge used. .cache/repair-v5-synthetic-probe/ contains exclusive freeze/ledger;
DO NOT replay completed runner. No new live quality batch performed.
Evidence: evidence/tasks/feature-003-repair-v5.md, repair-v5-results.json and
repair-v5-probe-results.json. Local milan guide remains ignored,182 lines.

Prior development-v4 remains calibrated2/3,17/25 transports16HTTP200+1unknown;
741 timeout RECOVERED65.404s,743 valid26.515s,742 failure35.218s retained. Earlier
v2/v3/live-v1 raw outcomes and failed original targets unchanged. Do NOT replay
completed batches or treat unused transport allowances as a new budget.

Next concrete step: freeze a fresh separately bounded development check exercising
full-report repair after v5; keep failures in denominator, no replacement of742.
T062 producer/consumer review pending;T063 authored guards partial;T064 actual
dataset adapter unstarted. T066 real teammate reproduction/human review and T067
full feature Converge pending. Original0/8 quality, retrieval0.50/0.50 and failed
latency/outlier remain FAILED. Independent fresh holdout/reference review pending.
