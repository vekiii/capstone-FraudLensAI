"""Fixed local validation diagnostics; no raw rejected input enters feedback."""

from fraudlens.investigation.report_policy import HUMAN_AUTHORITY_NOTICE

REPAIR_HINTS = {
    'schema_invalid': 'Return the complete ReportDraft JSON shape; include every required key and no extra keys. Use unique references and obey outcome-specific required sections.',
    'unknown_or_duplicate_evidence_reference': 'Use only evidence IDs returned by tools in this attempt. Remove duplicate evidence_refs.',
    'observation_required': 'Every observed_facts claim must have kind observation.',
    'procedure_required': 'Every recommended_checks claim must have kind procedure and cite applicable procedure evidence.',
    'hypothesis_required': 'Every alternative_explanations claim must have kind hypothesis and cite its case/history premises.',
    'claim_evidence_kind_mismatch': 'Observations cite case_fact/history; procedures cite procedure evidence; hypotheses cite case/history premises. Guidance is not a case fact.',
    'assertion_scope_mismatch': 'Each exact_assertions evidence_ref must also occur in that claim evidence_refs.',
    'exact_assertion_mismatch': 'Copy each exact_assertions path and value verbatim from facts in the cited evidence. Do not invent fields or alter exact source strings.',
    'exact_quote_mismatch': 'Copy each quote verbatim from the cited evidence text and include its evidence_ref in that claim evidence_refs.',
    'citation_set_mismatch': 'The citations must equal the deduplicated set of evidence_refs used across all claims, without unused or missing IDs.',
    'source_limitations_required': 'Include truthful source/history/score limitations from the supplied context and evidence.',
    'human_authority_notice_required': 'Include this exact separate limitations item in either outcome: '
        + HUMAN_AUTHORITY_NOTICE + ' Keep all other truthful limitations; this is not a claim or a recommended action.',
}


def repair_reason(error):
    """Exception text is used only for an exact allowlist lookup, never forwarded."""
    code = str(error)
    return code if code in REPAIR_HINTS else 'schema_invalid'
