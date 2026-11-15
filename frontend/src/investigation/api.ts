import { decodeDocuments, decodeKnowledgeError, decodePassage, decodeSearch } from './contracts';

import { decodeRun, decodeRuns, decodeEvidence, decodeInvestigationError, investigationStatuses, decodeContextBinding } from './contracts';
import type { Run } from './contracts';

export class KnowledgeError extends Error {
  constructor(readonly code: string) { super('Pretraga nije spremna ili zahtev nije uspeo.'); }
}
async function request<T>(url: string, decode: (value: unknown, response: Response) => T, signal?: AbortSignal, options?: RequestInit, success = 200, investigation = false): Promise<T> {
  if (signal?.aborted) throw new KnowledgeError('cancelled');
  const controller = new AbortController();
  let rejectStop: (error: Error) => void = () => {};
  const stop = new Promise<never>((_, reject) => { rejectStop = reject; });
  const cancel = () => { rejectStop(new KnowledgeError('cancelled')); controller.abort(); };
  signal?.addEventListener('abort', cancel, { once: true });
  const timeout = setTimeout(() => { rejectStop(new KnowledgeError('timeout')); controller.abort(); }, 5000);
  const receive = async () => {
    const response = await fetch(url, { ...options, signal: controller.signal });
    if (response.headers.get('content-type')?.split(';')[0].trim() !== 'application/json') throw new KnowledgeError('invalid_response');
    const value: unknown = await response.json();
    if (response.status !== success) {
      const code = investigation ? decodeInvestigationError(value) : decodeKnowledgeError(value);
      const statuses = investigationStatuses;
      if (response.status !== statuses[code]) throw new KnowledgeError('invalid_response');
      throw new KnowledgeError(code);
    }
    return decode(value, response);
  };
  try { return await Promise.race([receive(), stop]); }
  catch (error) { throw error instanceof KnowledgeError ? error : new KnowledgeError('invalid_response'); }
  finally { clearTimeout(timeout); signal?.removeEventListener('abort', cancel); }
}
export function getDocuments(signal?: AbortSignal) { return request('/api/knowledge/documents', decodeDocuments, signal); }
export function searchKnowledge(query: string, corpus: string, retrieval?: string, signal?: AbortSignal) {
  const params = new URLSearchParams({ q: query, corpus });
  if (retrieval) params.set('retrieval', retrieval);
  return request('/api/knowledge/search?' + params, (value, response) => {
    const result = decodeSearch(value);
    if (result.corpus_version !== corpus || result.query !== query.trim() || (retrieval && result.retrieval_version !== retrieval)) throw new KnowledgeError('invalid_response');
    return { ...result, truncated: response.headers.get('x-results-truncated') === 'true' };
  }, signal);
}
export function getPassage(id: string, corpus: string, signal?: AbortSignal) {
  return request(`/api/knowledge/passages/${encodeURIComponent(id)}?${new URLSearchParams({ corpus })}`, value => {
    const result = decodePassage(value);
    if (result.passage_id !== id || result.corpus_version !== corpus) throw new KnowledgeError('invalid_response');
    return result;
  }, signal);
}
export const knowledgeClient = { documents: getDocuments, search: searchKnowledge, passage: getPassage };

export function listInvestigations(caseId: string, signal?: AbortSignal) {
  return request('/api/investigation/runs?' + new URLSearchParams({ case_id: caseId }), (value, response) => {
    const result = decodeRuns(value);
    const binding = decodeContextBinding(response.headers.get('x-investigation-snapshot'), response.headers.get('x-investigation-context'));
    if (result.items.some(run => run.case_id !== caseId || run.context_revision !== binding.context_revision || run.snapshot_ref !== binding.snapshot_ref)) throw new KnowledgeError('invalid_response');
    return { ...result, ...binding };
  }, signal, undefined, 200, true);
}
export function createInvestigation(caseId: string, snapshot: string, revision: string, key: string, signal?: AbortSignal) {
  return request('/api/investigation/runs', value => {
    const result = decodeRun(value);
    if (result.case_id !== caseId || result.snapshot_ref !== snapshot || result.context_revision !== revision) throw new KnowledgeError('invalid_response');
    return result;
  }, signal, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Idempotency-Key': key }, body: JSON.stringify({ case_id: caseId, source_mode: 'fixture', snapshot_ref: snapshot }) }, 202, true);
}
export function getInvestigation(id: string, caseId: string, revision: string, signal?: AbortSignal) {
  return request('/api/investigation/attempts/' + encodeURIComponent(id), value => {
    const result = decodeRun(value);
    if (result.attempt_id !== id || result.case_id !== caseId || result.context_revision !== revision) throw new KnowledgeError('invalid_response');
    return result;
  }, signal, undefined, 200, true);
}
export function getEvidence(attempt: string, id: string, revision: string, signal?: AbortSignal) {
  return request(`/api/investigation/attempts/${encodeURIComponent(attempt)}/evidence/${encodeURIComponent(id)}`, value => {
    const result = decodeEvidence(value);
    if (result.evidence_id !== id || result.attempt_id !== attempt || result.context_revision !== revision) throw new KnowledgeError('invalid_response');
    return result;
  }, signal, undefined, 200, true);
}
function recoveryAction(parent: Run, operation: 'retry' | 'cancel', key: string, reuse: boolean, signal?: AbortSignal) {
  return request(`/api/investigation/attempts/${encodeURIComponent(parent.attempt_id)}/${operation}`, value => {
    const run = decodeRun(value);
    if (run.case_id !== parent.case_id || run.context_revision !== parent.context_revision || run.snapshot_ref !== parent.snapshot_ref || run.run_id !== parent.run_id ||
      (operation === 'retry' ? run.parent_attempt_id !== parent.attempt_id || run.attempt_id === parent.attempt_id || run.state !== 'created' : run.attempt_id !== parent.attempt_id || run.state !== 'cancelled')) throw new KnowledgeError('invalid_response');
    return run;
  }, signal, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Idempotency-Key': key, 'If-Match': String(parent.revision) }, body: JSON.stringify(operation === 'retry' ? { reuse_evidence: reuse } : {}) }, operation === 'retry' ? 202 : 200, true);
}
export function retryInvestigation(parent: Run, reuse: boolean, key: string, signal?: AbortSignal) { return recoveryAction(parent, 'retry', key, reuse, signal); }
export function cancelInvestigation(parent: Run, key: string, signal?: AbortSignal) { return recoveryAction(parent, 'cancel', key, false, signal); }
export const reportClient = { list: listInvestigations, create: createInvestigation, attempt: getInvestigation, evidence: getEvidence, retry: retryInvestigation, cancel: cancelInvestigation };
