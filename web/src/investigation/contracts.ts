// Feature-local strict wire decoders. Never trust a cast as validation.
function fail(): never { throw new Error('Invalid knowledge response'); }
function record(v: unknown): v is Record<string, unknown> { return typeof v === 'object' && v !== null && !Array.isArray(v); }
function closed(v: unknown, fields: readonly string[]) {
  if (!record(v) || Object.keys(v).length !== fields.length || !fields.every(k => Object.hasOwn(v, k))) return fail();
  return v;
}
function text(v: unknown, max: number, min = 1): string { return typeof v === 'string' && [...v].length >= min && [...v].length <= max ? v : fail(); }
function choice<T extends string>(v: unknown, values: readonly T[]): T { for (const item of values) if (v === item) return item; return fail(); }
function integer(v: unknown, min: number, max: number): number { return typeof v === 'number' && Number.isInteger(v) && v >= min && v <= max ? v : fail(); }
function digest(v: unknown): string { const t = text(v, 64); return /^[a-f0-9]{64}(?![\s\S])/.test(t) ? t : fail(); }
function corpus(v: unknown): string { const t = text(v, 71); if (!t.startsWith('corpus_')) return fail(); digest(t.slice(7)); return t; }
function date(v: unknown): string { const t = text(v, 10); if (!/^\d{4}-\d{2}-\d{2}$/.test(t)) return fail(); const d = new Date(t + 'T00:00:00Z'); return Number.isFinite(d.getTime()) && d.toISOString().slice(0, 10) === t ? t : fail(); }
function instant(v: unknown): string {
  const t = text(v, 100);
  const match = /^(\d{4})-\d{2}-\d{2}[Tt](\d{2}):(\d{2}):(\d{2})(?:\.\d+)?Z(?![\s\S])/.exec(t);
  if (!match || Number(match[1]) < 1 || Number(match[2]) > 23 || Number(match[3]) > 59 || Number(match[4]) > 59) return fail();
  date(t.slice(0, 10));
  return Number.isFinite(Date.parse(t)) ? t : fail();
}
function nullable<T>(v: unknown, parse: (x: unknown) => T): T | null { return v === null ? null : parse(v); }
function array<T>(v: unknown, maximum: number, parse: (x: unknown) => T): T[] { return Array.isArray(v) && v.length <= maximum ? v.map(parse) : fail(); }
const documentFields = ['doc_id', 'title', 'origin_kind', 'source_uri', 'published_at', 'unknown_date_reason', 'retrieved_at', 'jurisdiction', 'version', 'reviewed_by', 'reviewed_at', 'reuse_terms', 'content_sha256', 'included_sections', 'applicability_notes'];
export function decodeDocument(value: unknown) {
  const v = closed(value, documentFields);
  return { doc_id: text(v.doc_id, 80), title: text(v.title, 200), origin_kind: choice(v.origin_kind, ['official', 'simulated', 'dataset_guide']), source_uri: text(v.source_uri, 1000), published_at: nullable(v.published_at, date), unknown_date_reason: nullable(v.unknown_date_reason, x => text(x, 2000)), retrieved_at: instant(v.retrieved_at), jurisdiction: text(v.jurisdiction, 200), version: text(v.version, 120), reviewed_by: text(v.reviewed_by, 80), reviewed_at: instant(v.reviewed_at), reuse_terms: text(v.reuse_terms, 2000), content_sha256: digest(v.content_sha256), included_sections: array(v.included_sections, 100, x => text(x, 200)), applicability_notes: text(v.applicability_notes, 2000) };
}
export type KnowledgeDocument = ReturnType<typeof decodeDocument>;
export function decodePassage(value: unknown) {
  const v = closed(value, ['passage_id', 'corpus_version', 'document', 'section', 'ordinal', 'text', 'content_sha256']);
  return { passage_id: digest(v.passage_id), corpus_version: corpus(v.corpus_version), document: decodeDocument(v.document), section: text(v.section, 200), ordinal: integer(v.ordinal, 0, Number.MAX_SAFE_INTEGER), text: text(v.text, 2400), content_sha256: digest(v.content_sha256) };
}
export type Passage = ReturnType<typeof decodePassage>;
export function decodeDocuments(value: unknown) {
  const v = closed(value, ['contract_version', 'corpus_version', 'documents']);
  if (v.contract_version !== 1) return fail();
  return { contract_version: 1, corpus_version: corpus(v.corpus_version), documents: array(v.documents, 100, decodeDocument) };
}
export type Documents = ReturnType<typeof decodeDocuments>;
export function decodeSearch(value: unknown) {
  const v = closed(value, ['contract_version', 'corpus_version', 'retrieval_version', 'query', 'status', 'hits']);
  if (v.contract_version !== 1) return fail();
  const version = corpus(v.corpus_version);
  const hits = array(v.hits, 5, item => {
    const hit = closed(item, ['rank', 'score', 'passage']);
    if (typeof hit.score !== 'number' || !Number.isFinite(hit.score) || hit.score < 0) return fail();
    const passage = decodePassage(hit.passage);
    if (passage.corpus_version !== version) return fail();
    return { rank: integer(hit.rank, 1, 5), score: hit.score, passage };
  });
  const status = choice(v.status, ['matched', 'no_match']);
  if (hits.some((h, i) => h.rank !== i + 1) || (status === 'no_match' && hits.length > 0) || (status === 'matched' && hits.length === 0)) return fail();
  return { contract_version: 1, corpus_version: version, retrieval_version: digest(v.retrieval_version), query: text(v.query, 500), status, hits };
}
export type Search = ReturnType<typeof decodeSearch> & { truncated?: boolean };
const safeMax = Number.MAX_SAFE_INTEGER;
function bool(v: unknown): boolean { return typeof v === 'boolean' ? v : fail(); }
function id(v: unknown, prefix: string) { const t = text(v, prefix.length + 32); return new RegExp('^' + prefix + '[a-f0-9]{32}(?![\\s\\S])').test(t) ? t : fail(); }
export type InvestigationSource = 'fixture' | 'dataset';
function caseId(v: unknown, source: InvestigationSource) {
  const pattern = source === 'dataset' ? /^C[0-9a-f]{32}(?![\s\S])/ : /^CASE-[0-9]{3}(?![\s\S])/;
  const t = text(v, 33);
  return pattern.test(t) ? t : fail();
}
const evidenceId = (v: unknown) => id(v, 'ev_');
const attemptId = (v: unknown) => id(v, 'att_');
function unique<T>(values: T[]) { return new Set(values).size === values.length ? values : fail(); }
function decodeClaim(value: unknown) {
  const v = closed(value, ['text', 'kind', 'evidence_refs', 'exact_assertions', 'quotes']);
  const refs = array(v.evidence_refs, 20, evidenceId); if (!refs.length) return fail();
  const assertion = (item: unknown) => { const a = closed(item, ['evidence_ref', 'path', 'value']); const ref = evidenceId(a.evidence_ref); if (!refs.includes(ref)) return fail(); return { evidence_ref: ref, path: text(a.path, 200), value: text(a.value, 2400) }; };
  const quote = (item: unknown) => { const q = closed(item, ['evidence_ref', 'text']); const ref = evidenceId(q.evidence_ref); if (!refs.includes(ref)) return fail(); return { evidence_ref: ref, text: text(q.text, 2400) }; };
  return { text: text(v.text, 2000), kind: choice(v.kind, ['observation', 'hypothesis', 'procedure']), evidence_refs: refs, exact_assertions: array(v.exact_assertions, 20, assertion), quotes: array(v.quotes, 20, quote) };
}
function decodeDraft(value: unknown) {
  const v = closed(value, ['outcome', 'summary', 'observed_facts', 'risk_indicators', 'alternative_explanations', 'missing_information', 'recommended_checks', 'limitations', 'citations']);
  const result = { outcome: choice(v.outcome, ['ready_for_review', 'needs_information']), summary: array(v.summary, 20, decodeClaim), observed_facts: array(v.observed_facts, 20, decodeClaim), risk_indicators: array(v.risk_indicators, 20, decodeClaim), alternative_explanations: array(v.alternative_explanations, 20, decodeClaim), missing_information: array(v.missing_information, 20, x => text(x, 2000)), recommended_checks: array(v.recommended_checks, 20, decodeClaim), limitations: array(v.limitations, 20, x => text(x, 2000)), citations: unique(array(v.citations, 100, evidenceId)) };
  const refs = new Set([result.summary, result.observed_facts, result.risk_indicators, result.alternative_explanations, result.recommended_checks].flat().flatMap(c => c.evidence_refs));
  if (refs.size !== result.citations.length || result.citations.some(ref => !refs.has(ref))) return fail();
  if (result.outcome === 'ready_for_review' && (!result.summary.length || !result.observed_facts.length || !result.citations.length)) return fail();
  if (result.outcome === 'needs_information' && !result.limitations.length) return fail();
  return result;
}
function decodeReport(value: unknown) {
  const v = closed(value, ['report_id', 'attempt_id', 'context_revision', 'created_at', 'validation', 'semantic_review', 'draft']);
  return { report_id: digest(v.report_id), attempt_id: attemptId(v.attempt_id), context_revision: digest(v.context_revision), created_at: instant(v.created_at), validation: choice(v.validation, ['schema_reference_passed']), semantic_review: choice(v.semantic_review, ['not_reviewed', 'reviewed_with_notes']), draft: decodeDraft(v.draft) };
}
function decodeReview(value: unknown) {
  const v = closed(value, ['review_id', 'report_id', 'actor', 'disposition', 'rationale', 'correction_note', 'supersedes_review_id', 'created_at']);
  return { review_id: id(v.review_id, 'rev_'), report_id: digest(v.report_id), actor: text(v.actor, 80), disposition: choice(v.disposition, ['escalate', 'close', 'request_more_information']), rationale: text(v.rationale, 2000), correction_note: nullable(v.correction_note, x => text(x, 2000)), supersedes_review_id: nullable(v.supersedes_review_id, x => id(x, 'rev_')), created_at: instant(v.created_at) };
}
function decodeFailure(value: unknown) {
  const v = closed(value, ['code', 'message', 'outcome_unknown']);
  return { code: choice(v.code, ['provider_access', 'provider_refusal', 'provider_incomplete', 'provider_failure', 'unsupported_capability', 'output_invalid', 'budget_exhausted', 'interrupted', 'stale_snapshot', 'tool_result_too_large', 'context_unavailable']), message: text(v.message, 200), outcome_unknown: bool(v.outcome_unknown) };
}
export function decodeRun(value: unknown) {
  const v = closed(value, ['contract_version', 'run_id', 'attempt_id', 'parent_attempt_id', 'case_id', 'context_revision', 'source_mode', 'snapshot_ref', 'corpus_version', 'retrieval_version', 'provider_mode', 'requested_model', 'returned_model', 'state', 'revision', 'created_at', 'updated_at', 'budget', 'trace', 'report', 'review', 'failure']);
  if (v.contract_version !== 1) return fail();
  const b = closed(v.budget, ['provider_requests', 'tool_calls', 'repairs', 'transient_retries', 'deadline']);
  const source_mode = choice(v.source_mode, ['fixture', 'dataset']);
  const result = { contract_version: 1, run_id: id(v.run_id, 'inv_'), attempt_id: attemptId(v.attempt_id), parent_attempt_id: nullable(v.parent_attempt_id, attemptId), case_id: caseId(v.case_id, source_mode), context_revision: digest(v.context_revision), source_mode, snapshot_ref: text(v.snapshot_ref, 120), corpus_version: corpus(v.corpus_version), retrieval_version: digest(v.retrieval_version), provider_mode: choice(v.provider_mode, ['test', 'openai']), requested_model: nullable(v.requested_model, x => text(x, 200)), returned_model: nullable(v.returned_model, x => text(x, 200)), state: choice(v.state, ['created', 'gathering_evidence', 'drafting', 'ready_for_review', 'needs_information', 'failed', 'cancelled', 'reviewed']), revision: integer(v.revision, 1, safeMax), created_at: instant(v.created_at), updated_at: instant(v.updated_at),
    budget: { provider_requests: integer(b.provider_requests, 0, 8), tool_calls: integer(b.tool_calls, 0, 12), repairs: integer(b.repairs, 0, 1), transient_retries: integer(b.transient_retries, 0, 1), deadline: nullable(b.deadline, instant) },
    trace: array(v.trace, 12, item => { const t = closed(item, ['sequence', 'name', 'status', 'elapsed_ms', 'evidence_refs']); return { sequence: integer(t.sequence, 1, safeMax), name: choice(t.name, ['get_case_facts', 'get_account_history', 'search_procedures']), status: choice(t.status, ['completed', 'rejected', 'failed']), elapsed_ms: integer(t.elapsed_ms, 0, safeMax), evidence_refs: array(t.evidence_refs, 100, evidenceId) }; }),
    report: nullable(v.report, decodeReport), review: nullable(v.review, decodeReview), failure: nullable(v.failure, decodeFailure) };
  if (result.report && (result.report.attempt_id !== result.attempt_id || result.report.context_revision !== result.context_revision)) return fail();
  const complete = ['ready_for_review', 'needs_information', 'reviewed'].includes(result.state);
  if (complete !== (result.report !== null) || (result.state === 'failed' && !result.failure) || (result.failure && !['failed', 'cancelled'].includes(result.state))) return fail();
  if (result.report && result.state !== 'reviewed' && result.report.draft.outcome !== result.state) return fail();
  if ((result.state === 'reviewed') !== (result.review !== null) || (result.review && result.review.report_id !== result.report?.report_id)) return fail();
  if (result.report && (result.report.semantic_review === 'reviewed_with_notes') !== (result.review !== null)) return fail();
  if (result.review && result.report?.draft.outcome === 'needs_information' && result.review.disposition !== 'request_more_information') return fail();
  return result;
}
export type Run = ReturnType<typeof decodeRun>;
export function decodeRuns(value: unknown) {
  const v = closed(value, ['contract_version', 'total_count', 'truncated', 'items']); if (v.contract_version !== 1) return fail();
  const result = { contract_version: 1, total_count: integer(v.total_count, 0, safeMax), truncated: bool(v.truncated), items: array(v.items, 20, decodeRun) };
  if (result.items.length !== Math.min(20, result.total_count) || result.truncated !== (result.total_count > 20)) return fail();
  unique(result.items.map(item => item.run_id)); return result;
}
export function decodeEvidence(value: unknown) {
  const v = closed(value, ['contract_version', 'evidence_id', 'attempt_id', 'context_revision', 'kind', 'text', 'facts', 'passage', 'history', 'returned_count', 'eligible_count', 'truncated', 'content_sha256', 'created_at']);
  if (v.contract_version !== 1) return fail();
  const result = { contract_version: 1, evidence_id: evidenceId(v.evidence_id), attempt_id: attemptId(v.attempt_id), context_revision: digest(v.context_revision), kind: choice(v.kind, ['case_fact', 'history', 'procedure']), text: text(v.text, 16000),
    facts: array(v.facts, 500, item => { const f = closed(item, ['path', 'value']); return { path: text(f.path, 200), value: text(f.value, 2400) }; }), passage: nullable(v.passage, decodePassage),
    history: nullable(v.history, item => { const h = closed(item, ['availability', 'cutoff', 'coverage', 'start', 'lookback_days', 'view_scope', 'reason']); if (h.lookback_days !== 7) return fail(); return { availability: choice(h.availability, ['available', 'unavailable']), cutoff: nullable(h.cutoff, instant), coverage: choice(h.coverage, ['full', 'incomplete', 'unavailable']), start: nullable(h.start, instant), lookback_days: 7, view_scope: choice(h.view_scope, ['authored_fixture', 'synthetic_shared_banks']), reason: nullable(h.reason, x => text(x, 2000)) }; }),
    returned_count: integer(v.returned_count, 0, safeMax), eligible_count: nullable(v.eligible_count, x => integer(x, 0, safeMax)), truncated: bool(v.truncated), content_sha256: digest(v.content_sha256), created_at: instant(v.created_at) };
  if ((result.kind === 'procedure') !== (result.passage !== null) || (result.kind === 'history') !== (result.history !== null)) return fail();
  return result;
}
export type Evidence = ReturnType<typeof decodeEvidence>;
export function decodeInvestigationError(value: unknown) {
  const v = closed(value, ['contract_version', 'error']); if (v.contract_version !== 1) return fail();
  const e = closed(v.error, ['code', 'message', 'retryable']); text(e.message, 200); bool(e.retryable);
  const code = choice(e.code, ['invalid_request', 'forbidden_scope', 'case_not_found', 'investigation_not_found', 'evidence_not_found', 'stale_snapshot', 'request_conflict', 'revision_conflict', 'invalid_transition', 'knowledge_unavailable', 'context_unavailable', 'provider_unavailable', 'store_busy', 'internal_error']);
  if (e.retryable !== (investigationStatuses[code] >= 500)) return fail(); return code;
}
export const investigationStatuses = { invalid_request: 422, forbidden_scope: 403, case_not_found: 404, investigation_not_found: 404, evidence_not_found: 404, stale_snapshot: 409, request_conflict: 409, revision_conflict: 409, invalid_transition: 409, knowledge_unavailable: 503, context_unavailable: 503, provider_unavailable: 503, store_busy: 503, internal_error: 500 };
export function decodeContextBinding(snapshot: unknown, revision: unknown) { return { snapshot_ref: text(snapshot, 120), context_revision: digest(revision) }; }
export function decodeKnowledgeError(value: unknown) {
  const v = closed(value, ['contract_version', 'error']);
  if (v.contract_version !== 1) return fail();
  const e = closed(v.error, ['code', 'message', 'retryable']);
  const code = choice(e.code, ['invalid_request', 'knowledge_unavailable', 'evidence_not_found', 'internal_error']);
  text(e.message, 200); if (typeof e.retryable !== 'boolean') return fail();
  return code;
}
