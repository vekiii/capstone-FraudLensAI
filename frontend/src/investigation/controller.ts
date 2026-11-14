import { knowledgeClient } from './api';
import type { Documents, Passage, Search } from './contracts';
import { createKnowledgeView } from './views';

export interface KnowledgeClient {
  documents(signal?: AbortSignal): Promise<Documents>;
  search(query: string, corpus: string, retrieval?: string, signal?: AbortSignal): Promise<Search>;
  passage(id: string, corpus: string, signal?: AbortSignal): Promise<Passage>;
}
export function mountKnowledge(root: HTMLElement, client: KnowledgeClient = knowledgeClient): () => void {
  let generation = 0; let pending: AbortController | undefined; let disposed = false;
  let corpus: string | undefined; let retrieval: string | undefined; let query = ''; let selected: string | undefined;
  const begin = () => { generation++; pending?.abort(); pending = new AbortController(); view.loading(); return { token: generation, signal: pending.signal }; };
  const current = (token: number) => !disposed && token === generation;
  const view = createKnowledgeView(root, { search: value => { query = value; selected = undefined; void doSearch(); }, select: id => { selected = id; void doPassage(id); }, retry: () => { if (!corpus) void initialize(); else if (selected) void doPassage(selected); else void doSearch(); } });
  async function initialize() {
    const { token, signal } = begin();
    try { const result = await client.documents(signal); if (!current(token)) return; corpus = result.corpus_version; view.ready(result.documents); }
    catch { if (current(token)) view.error(); }
  }
  async function doSearch() {
    const { token, signal } = begin();
    try { if (!corpus || !query.trim() || [...query.trim()].length > 500) throw new Error(); const result = await client.search(query, corpus, retrieval, signal); if (!current(token)) return; retrieval = result.retrieval_version; view.results(result); }
    catch { if (current(token)) view.error(); }
  }
  async function doPassage(id: string) {
    const { token, signal } = begin();
    try { if (!corpus) throw new Error(); const result = await client.passage(id, corpus, signal); if (current(token)) view.passage(result); }
    catch { if (current(token)) view.error(); }
  }
  void initialize();
  return () => { disposed = true; generation++; pending?.abort(); root.replaceChildren(); };
}
