# Human-authority notice v7 maintenance

User requested publishing completed v6 then continuing T088. Published af8fe4b;
v6 ordinary quality1/2 remains frozen (762 omitted human final authority).
This is scoped FR-013–020/022–028 maintenance, not a new evaluation batch.

## Design

New attempts pin application prompt v4 and private binding
`report_policy=human_authority_notice_v1`. In every outcome require one separate
limitations item exactly:

> Konačnu odluku donosi ljudski analitičar; AI nacrt ne izvršava radnje.

This is a versioned protocol literal for a known application rule. The validator
checks exact whole-item membership, not keywords or semantic inference. Equivalent
paraphrases still require repair under this protocol. Do not auto-append a notice,
rewrite a provider response, or treat it as evidence that other prose is safe.
Semantic support, contradictions, unauthorized-action language and all required
disclosures still need unchanged machine/human evaluation. Semantic status stays
not_reviewed after local validation. No new public schema/report fields.

The original schema/fact/citation/quote/limited-source checks run unchanged. For
the new policy, a missing literal raises allowlisted
`human_authority_notice_required`; fixed repair guidance requests the literal in
limitations. Existing single-repair/8request/12tool/30s/120s/48k limits apply.
If the second draft omits it, fail output_invalid with no saved report. Unknown
policy fails before dispatch. Old bindings lacking policy keep old behavior;
retry inherits its parent's policy and exact prompt. Saved reports are immutable.
The authored test provider emits the same notice; no claim of model evaluation.

Add RED/GREEN no-guidance acceptance/repair/failure, both outcomes, exact-item
negative cases, preserved raw drafts/SDK continuation, legacy/new retry pinning,
unknown policy, lower budgets and unchanged numerical validation. Preserve a
hash-verified pre-change runtime snapshot and old result hashes before edits.
Full backend/Ruff plus offline old-artifact audit. No live calls or score changes
in this unit; a fresh model evaluation requires a separately frozen new protocol.
