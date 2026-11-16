# Current handoff - live repair v6 complete, 2026-11-16

Branch feature03-reliability-v2. User authorized one new three-case evaluation,
now complete, and explicitly requested commit/push on2026-11-16. T085-T087 complete;
development-v6 pack, runner, tests, evidence and this handoff are included in that
publication. Pre-publication HEAD/upstream4262193; verify Git for resulting tip.
No runtime, prompt,
.env, frontend or dependency changes. Preserve all work and old results.

Design specs/003-ai-investigation/live-repair-v6.md. Two ordinary quality cases,
one separately labeled controlled application-candidate fault. Wrapper preserves
original actual draft/private continuation and injects one invalid authored
candidate for local validation only. This is not a natural model mistake.
RED6 intended failures; GREEN11 new/42 related PASS; full backend893 PASS61.61s;
Ruff/diff PASS. Requirements checklist16/16; no extension hooks.

Actual17/25 transports:16generation+1same-model judge, allHTTP200 gpt-6-luna.
Known86,684 tokens (73,054input+13,630output), unknown0, spend unknown. No timeout,
quota/access error or transient retry. All3 valid needs_information <90/120s:
761 ordinary27.194s,5requests/4tools/0repair;
762 ordinary26.171s,5requests/4tools/0repair;
763 controlled43.954s,6requests/4tools/1repair.

Controlled intended exact_assertion_mismatch observed; one REAL repair transport
37,169<48,000 bytes, valid real LLM report and separate machine quality PASS.
All limits and full continuation retained. Controlled case excluded from primary
quality denominator. Ordinary quality1/2:761PASS,762FAIL missing explicit human
final authority. Both ordinary factual6/6 and essential19/19; procedure1/1, other
N/A; no critical machine flags.762 covers other disclosures but omits human
final authority; raw result retained unchanged. Narrow calibration3/3 PASS;
no independent/human validation or comparable before/after/release claim.

Audit PASS: runtime/protocol/source/prompt/config hashes unchanged; all32 prior
artifact hashes preserved,10 new raw/metadata hashes,13 cited IDs resolve. Actual
injected candidate still fails local validation; original private items bound.
Evidence evidence/tasks/feature-003-live-repair-v6.md and live-repair-v6-results.json.
Raw outputs ignored evals/results/feature-003/development-v6/. DO NOT replay any
completed batch/builder or reuse unused8 transports. Safe offline --audit only.
Local milan guide updated, ignored,193 lines. No further API calls needed for v6.

Next concrete step: T088 authored RED reproduction of missing human-authority
statement in no-guidance drafts, then separately design/version a correction
preserving original model outputs, report immutability and semantic requirements.
Do not weaken the disclosure or regrade DEV6-762 to pass. Not implemented yet.

Prior v5 byte fix and synthetic2/2 capability remain published4262193; v4 quality
2/3 and all original failed targets intact. T062 producer/consumer review pending;
T063 authored guards partial;T064 actual dataset adapter unstarted. T066 actual
teammate reproduction/human review and T067 full Converge pending. Original0/8
quality, retrieval0.50/0.50 and failed latency/outlier remain FAILED. Fresh
independent holdout/reference review still required for acceptance.
