# Reportv6/output8192 + computed history bounds, 2026-11-18

User explicitly requested implementation of both corrections. Work on feature03
frombb46ba4, preserving prior dirty v8 development/proposal/handoff changes.
No commit/push/merge or live requests. Actual counter remains150/279.

## Behavior

New report_prompt=v6 opts into code-derived history bounds. max_output_tokens8192
requires explicit OpenAI semanticv8/reportv6;4096 remains default/legacy maximum.
SDK provider has explicit output_token_cap8192 from PERSISTED binding in both
application and metered evaluation factories. Omitted/default provider cap4096
still rejects8192 before HTTP. New explicit settings permit any selected integer
limit up to8192; >8192 rejected. Evaluation runner transmits frozen output limit,
with omitted field4096. New freezes must specify max_output_tokens8192/reportv6.
No.env activation or automatic switch. Legacy v4/v5 prompt bytes remain unchanged.
Request45/selector30/total120,8request/12tools/48KB/2MiB limits unchanged.

Reportv6 attempts pin history_bounds_version1; ToolExecutor computes
window_start_inclusive from actual returned history start and
window_end_exclusive from actual cutoff floored to UTC minute. For09:18:43Z,
exclusive end09:18:00Z. These are public evidence text AND exact facts; existing
history envelope, raw cutoff and actual filters unchanged. Unavailable histories
have null bounds. Old attempts omit fields. Prompt copies computed values rather
than inferring cutoff rounding. Retry preserves pin/prompt/output limit and
revalidates reuse with the matching history reader. Defaults remain v4/4096.

## Verification

RED5 intended tests failed for missing profile/cap/bound behaviors. GREEN7 tests
cover settings/old defaults, actual SDK wire8192 and default-cap rejection,
application/evaluation factory use of saved limits despite changed settings,
available/unavailable tool evidence, legacy projection and retry evidence reuse.
74 targeted regression PASS8.65s. Full backend **1157 PASS98.24s**, final code.
Ruff backend source/tests/modified runner and git diff --check PASS.
Initial style lint corrected; one early available-history test attempted retry
from ready_for_review (invalid transition by design), then used needs_information
to correctly exercise retry/reuse. This was test setup, not weakened transition.
Prerequisites PASS with feature003 explicitly selected,16/16 checklist, no hooks.
No frontend checks (unchanged), API/model capability probe, runtime live quality,
new model report or higher-token performance claim.

Prior execution freeze covers72files. Exact bytes archived and hash-verified at
ignored development/executed-source-snapshot; changed tracked files recovered
fromHEAD and tested newline encodings against ORIGINAL SHA, no guess accepted.
Archive matches all72 original hashes; old observations/ratings/freeze are not
rewritten. Current runtime hashes differ and are explicitly versioned; do not
claim old freeze identity/current live acceptance. Transferred databases untouched.

Commands: python -m pytest backend/tests/unit/test_report_v6_bounds.py plus existing
openai/tools/semantic_profile_v8/acceptance_harness tests; full
`.venv/Scripts/python.exe -m pytest backend/tests -q --basetemp=.cache/report-v6-full-tmp -o cache_dir=.cache/report-v6-full-cache`.
[Machine hashes/results](feature-003-report-v6-output-bounds-20261118-results.json).
[Design](../../specs/003-ai-investigation/report-v6-output-bounds.md).

## Handoff

Corrections implemented; T101/T102 remain open. A larger token budget cannot
promise completion, semantic truth or90s timing. New report/source/binding runtime
requires fresh reviewed development inputs and new freeze before dispatch. The
previous failed cycle remains stopped; a further live cycle is a separate decision
under its approved stop rule, not automatic use of leftover129 requests. No
new budget or calibration/report-quality acceptance inferred from software tests.
