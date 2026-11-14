import { decodeDocuments, decodeKnowledgeError, decodePassage, decodeSearch } from './contracts';

export class KnowledgeError extends Error {
  constructor(readonly code: string) { super('Pretraga nije spremna ili zahtev nije uspeo.'); }
}
async function request<T>(url: string, decode: (value: unknown, response: Response) => T, signal?: AbortSignal): Promise<T> {
  if (signal?.aborted) throw new KnowledgeError('cancelled');
  const controller = new AbortController();
  let rejectStop: (error: Error) => void = () => {};
  const stop = new Promise<never>((_, reject) => { rejectStop = reject; });
  const cancel = () => { rejectStop(new KnowledgeError('cancelled')); controller.abort(); };
  signal?.addEventListener('abort', cancel, { once: true });
  const timeout = setTimeout(() => { rejectStop(new KnowledgeError('timeout')); controller.abort(); }, 5000);
  const receive = async () => {
    const response = await fetch(url, { signal: controller.signal });
    if (response.headers.get('content-type')?.split(';')[0].trim() !== 'application/json') throw new KnowledgeError('invalid_response');
    const value: unknown = await response.json();
    if (response.status !== 200) {
      const code = decodeKnowledgeError(value);
      const statuses = { invalid_request: 422, knowledge_unavailable: 503, evidence_not_found: 404, internal_error: 500 };
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
