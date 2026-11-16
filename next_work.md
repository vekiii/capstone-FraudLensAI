# Current handoff ? coverage/calibration v4 complete, 2026-11-16

Branch feature03-reliability-v2; HEAD46a15ed plus uncommitted timeout-v3 and
coverage-v4 changes. No commit/push or .env/dependency changes. Preserve this work.
T076?T081 completed within their scoped maintenance/development checks.
Full backend870 PASS, focused17/related48 PASS, Ruff/diff PASS. Frontend unchanged.

Runtime: one bounded transient retry for request timeout; total timeout still
budget_exhausted; known credit/quota nonretryable with private safe diagnostics.
Public schemas/limits unchanged:8requests,12tools,30s/request,120s total,48k input.
New attempts pin application promptv3; old attempts/retries retain their old prompt.
Judge promptv3 distinguishes draft needs_information from an analyst disposition.
Atomic development facts + mandatory disclosures preserve all requirements and
90% support/80% coverage thresholds. Calibration failure prevents quality claims.

Live development-v4:17/25 attempts (16generation+1judge),16HTTP200+1unknown timeout.
741 valid65.404s, one timeout at29.993s RECOVERED by one retry;743 valid26.515s.
742 failed35.218s: typed null assertion on missing eligible_count Fact rejected;
repair payload reconstructed offline at49,925>48,000 bytes, no sixth HTTP sent.
Calibration3/3 PASS; actual development quality2/3. On two delivered reports:
support8/8, essential coverage19/19, procedures2/2, disclosures correct, no critical
machine flags. No independent/human or comparable before/after improvement claim.
Known79,502 tokens plus1 unknown usage, spend unknown. No quota errors observed.
Unused8 attempts NOT reusable; do NOT rerun any completed v2/v3/v4 batch.
Audit/hash PASS:20 prior v2/v3 JSON artifacts and v3 source snapshot preserved;
8 cited IDs resolve. Raw outputs remain ignored under evals/results/feature-003/.

Evidence: evidence/tasks/feature-003-coverage-v4.md, coverage-v4-results.json and
coverage-v4-repair-diagnosis.json. Detailed timeout-v3 and live-development-v2
history remains in their task evidence. V3 source snapshot before v4 selection:
.cache/evidence-snapshots/timeout-v3/ (ignored). Old source audits require their
original revision/snapshot, not current code. Local milan guide remains ignored.

Next concrete step: RED SDK regression for repair-context exhaustion, then fit
repair within48k while retaining required continuation/provenance and strict
fact validation; separately scope any NEW live check. No old failure replacement.
T062 producer/consumer review pending;T063 authored guards partial;T064 real adapter
unstarted. T066 actual teammate reproduction/human review and T067 full feature
Converge pending. Original0/8 quality, retrieval0.50/0.50 and original failed
latency/outlier remain FAILED. Independent fresh holdout/reference review pending.
