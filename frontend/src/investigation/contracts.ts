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
export function decodeKnowledgeError(value: unknown) {
  const v = closed(value, ['contract_version', 'error']);
  if (v.contract_version !== 1) return fail();
  const e = closed(v.error, ['code', 'message', 'retryable']);
  const code = choice(e.code, ['invalid_request', 'knowledge_unavailable', 'evidence_not_found', 'internal_error']);
  text(e.message, 200); if (typeof e.retryable !== 'boolean') return fail();
  return code;
}
