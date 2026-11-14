import { knowledgeClient } from './api';
import type { Documents, Passage, Search } from './contracts';
import { createKnowledgeView, createReportView } from './views';
import { reportClient, KnowledgeError } from './api';
import { decodeRun, decodeEvidence, decodeRuns, decodeContextBinding } from './contracts';
import type { Run } from './contracts';

export type ReportClient = typeof reportClient;
export function mountReports(root: HTMLElement, caseId: string, client: ReportClient = reportClient, options: { pollInterval?: number; maxPolls?: number } = {}) {
  let generation = 0, disposed = false, polls = 0;
  let pending = new AbortController(), evidencePending: AbortController | undefined;
  let timer: ReturnType<typeof setTimeout> | undefined;
  let snapshot = '', revision = '', selected: Run | undefined;
  let saved: Run[] = [];
  let totalCount = 0;
  let createKey: string | undefined;
  const interval = Math.min(5000, Math.max(10, options.pollInterval ?? 1000));
  const maximum = Math.min(120, Math.max(1, options.maxPolls ?? 120));
  const current = (token: number) => !disposed && generation === token;
  function begin() { generation++; clearTimeout(timer); pending.abort(); evidencePending?.abort(); pending = new AbortController(); return generation; }
  const view = createReportView(root, { start: () => { void create(); }, refresh: () => { void initialize(); }, select: id => { const run = saved.find(item => item.attempt_id === id); if (run) { const token = begin(); polls = 0; show(run, token); } }, evidence: id => { void evidence(id); } });
  function checked(value: unknown, expected?: string) { const run = decodeRun(value); if (run.case_id !== caseId || run.context_revision !== revision || run.snapshot_ref !== snapshot || (expected && run.attempt_id !== expected)) throw new Error(); return run; }
  function show(run: Run, token: number) {
    saved = saved.map(item => item.attempt_id === run.attempt_id ? run : item);
    view.saved(saved, totalCount, totalCount > 20);
    selected = run; view.run(run);
    if (['created', 'gathering_evidence', 'drafting'].includes(run.state)) {
      if (polls >= maximum) view.paused();
      else timer = setTimeout(() => { void poll(run.attempt_id, token); }, interval);
    }
  }
  async function poll(id: string, token: number) {
    polls++;
    try { const value = await client.attempt(id, caseId, revision, pending.signal); if (current(token)) show(checked(value, id), token); }
    catch (error) { if (current(token)) view.error(error instanceof KnowledgeError ? error.code : 'invalid_response'); }
  }
  async function initialize() {
    const token = begin(); view.loading(); polls = 0;
    try {
      const value = await client.list(caseId, pending.signal); if (!current(token)) return;
      const { snapshot_ref, context_revision, ...body } = value;
      const result = decodeRuns(body); const binding = decodeContextBinding(snapshot_ref, context_revision);
      snapshot = binding.snapshot_ref; revision = binding.context_revision;
      saved = result.items.map(run => checked(run)); totalCount = result.total_count; view.saved(saved, totalCount, result.truncated);
      if (saved.length) show(saved[0], token); else { selected = undefined; view.empty(); }
    } catch (error) { if (current(token)) view.error(error instanceof KnowledgeError ? error.code : 'invalid_response'); }
  }
  async function create() {
    if (!snapshot || disposed) return;
    const token = begin(); view.loading(); polls = 0;
    createKey ??= crypto.randomUUID();
    try {
      const value = await client.create(caseId, snapshot, revision, createKey, pending.signal);
      if (!current(token)) return;
      const run = checked(value); createKey = undefined;
      if (!saved.some(item => item.attempt_id === run.attempt_id)) totalCount++;
      saved = [run, ...saved.filter(item => item.attempt_id !== run.attempt_id)].slice(0, 20);
      show(run, token);
    } catch (error) { if (current(token)) view.error(error instanceof KnowledgeError ? error.code : 'invalid_response'); }
  }
  async function evidence(id: string) {
    const run = selected, token = generation; if (!run?.report?.draft.citations.includes(id)) return;
    evidencePending?.abort(); const controller = new AbortController(); evidencePending = controller;
    try {
      const value = await client.evidence(run.attempt_id, id, run.context_revision, controller.signal);
      if (!current(token) || evidencePending !== controller || selected?.attempt_id !== run.attempt_id) return;
      const item = decodeEvidence(value);
      if (item.attempt_id !== run.attempt_id || item.evidence_id !== id || item.context_revision !== run.context_revision || (item.passage && item.passage.corpus_version !== run.corpus_version)) throw new Error();
      view.evidence(item, run.corpus_version);
    } catch { if (current(token) && evidencePending === controller) view.evidenceError(); }
  }
  void initialize();
  return () => { disposed = true; begin(); root.replaceChildren(); };
}

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
