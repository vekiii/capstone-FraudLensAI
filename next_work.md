# Current handoff - human-authority protocol v7 complete, 2026-11-16

Branch feature03-reliability-v2. Completed v6 evaluation published as af8fe4b.
User explicitly requested commit/push of completed T088-T090 correction on
2026-11-16; correction and this handoff are included in that publication.
Pre-publication HEAD/upstream af8fe4b; use Git to verify resulting tip.
No .env/dependency/frontend/public schema edits.

New attempts pin application prompt v4 and private
report_policy=human_authority_notice_v1. Every draft outcome requires one exact
separate limitations item, defined in investigation/report_policy.py:
Konačnu odluku donosi ljudski analitičar; AI nacrt ne izvršava radnje.
Missing item raises fixed human_authority_notice_required, one bounded repair
with tool_choice=none, then output_invalid if omitted again. No auto-appending,
raw-response edits or semantic safety inference. Other source/fact/schema checks
and all8/12/1/1/30s/120s/48k limits unchanged. Unknown policy fails before I/O.
Legacy bindings lacking policy and retry descendants keep old validation/prompt;
new retry inherits the new policy. Reports and private continuation stay immutable.
Authored test provider includes notice; semantic_review stays not_reviewed.

RED9fail/1pass, GREEN18 new/82 related PASS; full backend911 PASS70.09s, Ruff/diff
PASS. One old positive mock updated to include notice; no production gate weakened.
SDK+mock continuation/repair checks passed. ZERO actual API calls in this unit;
new prompt/policy full-report model quality remains UNVERIFIED. Checklist16/16;
no pre/post extension hooks. Local ignored milan guide updated,199 lines.

Evidence evidence/tasks/feature-003-human-authority-v7.md and
human-authority-v7-results.json; design specs/003-ai-investigation/human-authority-v7.md.
Offline check verifies32 prior+10 v6 artifact hashes, original v6 audit,13 cited
IDs and unchanged old report IDs. Original762 missing notice is rejected ONLY
under new policy for diagnostic purposes; old score remains1/2, not regraded.
Pre-change19 runtime files saved/hash verified under ignored
.cache/evidence-snapshots/live-repair-v6/. Run historical source audits at af8fe4b
or their original verified snapshot, not changed runtime. New offline helper:
evidence/tasks/feature-003-human-authority-v7-check.py (no API, old outputs intact).

Next concrete step: freeze new prompt-v4/policy-aware development inputs and a
separately bounded live check for full reports/notice omission recovery. Preserve
all old outcomes and calibration/semantic criteria. No completed batch replay or
reuse of old unused budgets. No new live batch has been prepared/executed yet.

Historical v6 actual17/25 HTTP200,3 valid needs_information in27.194/26.171/43.954s;
ordinary quality1/2 due missing human authority in762; controlled repair37,169bytes
valid and separately rated PASS; calibration3/3. Known86,684 tokens/unknown0/spend
unknown. All original failures unchanged. T062 review pending,T063 authored guards
partial,T064 dataset adapter unstarted,T066 teammate/human reproduction-review and
T067 full Converge pending. Original0/8 quality,retrieval0.50/0.50 and failed
latency/outlier stay FAILED. Independent fresh holdout/reference review pending.
