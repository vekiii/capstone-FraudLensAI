# English retrieval scope amendment — 2026-11-17

Milan explicitly approved the move to English after the proposed retrieval-only
scope explanation. [Request](../../prompts/development/003-english-retrieval-decision-20261117.md).
[Recorded decision](../../specs/003-ai-investigation/retrieval-english-mvp-decision.md).

Started clean feature03-retrieval-v3 at
a2b35caaab5ccd46293945315c4d1dfee8d08b14. Read AGENTS.md then current next_work.md,
relevant specification/plan/evaluation/design/tasks/governance/evidence. Checked
branch/HEAD/diff. No runtime implementation, tests added, provider/evaluation run,
package install, real .env read, application service or original-store interaction.

Updated the current spec assumption and planning/evaluation addenda, linking a
prospective language-scope decision; old multilingual policy remains explicitly
historical. Serbian UI/report requirements remain separate. SC-002 thresholds,
20 fresh held-out questions/no-answer denominator and independent reviewed
evaluation stay mandatory. Old multilingual/fresh-v3 packs/results remain intact;
English-only is decided, not implemented or proven to pass. T095 remains open.

Verification for this documentation-only change: whitespace, local links,
unchanged task markers and baseline byte-preservation audit. No RED required
and no backend/frontend suite rerun; previous968 PASS is historical, not a new
test execution. Actual audit PASS:517 of525 initial tracked files byte-identical;
only eight intended documentation edits and three new decision/prompt/evidence
files. All100 task markers unchanged,74 local links resolve, whitespace/diff PASS.
Application code, JSON packs/reviews/configs, locks and all prior measured results
remain byte-identical. Audit: `.cache/t095-english-decision-20261117/integrity.json`.

Next concrete step: prepare a separate English-only T095 development design with
explicit analyst/worker search-language contract, bounded candidate and fresh
reviewed development/held-out pack. No automatic retuning or acceptance run.
