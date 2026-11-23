# Coverage and judge calibration v4 — 2026-11-16

User resumed continued work on feature03-reliability-v2. Preserve pending v3
changes and all prior reports/scores. Maintenance of FR-013–017/022–028; no public
schema, producer, model, ceiling or release-threshold change. No commit/push.

## Problem and design

V3 generated3 valid drafts, but machine coverage was5/7,3/5,3/6. Compound reference
items joined transaction identity/money with negative disclaimers; one judge also
treated needs_information as a human disposition. Raw v3 ratings stay unchanged.

1. New application prompt v3 explicitly requests transaction ID, exact money/time,
   score/source and available history facts in readable claims. Clarify that
   forbidden application envelope fields (attempt_id/report_id/state) are distinct
   from supplied transaction IDs, which belong in claim text. Require source/time/
   score/guilt/loss limitations and final human authority. New attempts pin v3;
   old attempts/retries retain their prior prompt bytes. Preserve strict validation.
2. New DEVELOPMENT references use atomic factual units. Move no-guilt/not-loss/
   non-ML/uncalibrated/synthetic/time-provenance/human-authority disclosures into
   explicit required_disclosures, gated by missingness_correct. No obligation is
   dropped: every required disclosure must pass; unsupported inventions remain
   critical failures. Keep factual support>=90%, coverage>=80%, zero critical/
   unsupported procedures and conservative flags. Changed denominators make this
   a new non-comparable protocol, not a correction to old scores.
3. Judge prompt v3 distinguishes a draft outcome from a separate human review.
   No guidance permits needs_information with empty recommended_checks. Explicit
   unsupported prose/actions remain defects. Judge semantic equivalence, not exact
   disclaimer wording, while preserving exact IDs/money/time. Source evidence alone
   is not report coverage.
4. Three authored calibration packets accompany the actual report packets in ONE
   stateless judge request: legitimate needs-information/no guidance, invented
   funds origin, and missing human-authority disclosure. Expected calibration
   judgments stay outside judge input. Raw packet ratings are bound/validated.
   All calibrations must match before primary quality scores are called reliable;
   otherwise raw scores remain but passing_development_reports is unavailable.
   Calibration packets never enter generation/retrieval or primary denominators.

## Execution boundary

Separate development-v4 inputs/references/calibrations/protocol and raw output
directory;3 fresh instances of development templates, not independent holdout.
Operator cap25 (up to8 generation requests/case+1 batch judge), same quota/access
stop policy; judge schema allows6 packets (3 actual+3 calibration), output cap8192.
No tuning between actual outcomes, no old report replays or unused-budget reuse.
Freeze source/prompt/schema/config and references before dispatch. New references
and calibrations open only after generation seals. Human review still pending.

V3 runtime files were copied and hash-verified to ignored
.cache/evidence-snapshots/timeout-v3/ before changing prompt selection. Preserve
all v2/v3 raw/summary hashes. Run RED→GREEN for calibration gate, prompt binding
and negative cases; full backend/Ruff; one bounded live development batch and audit.
No independent quality improvement/release acceptance claim from these examples.
