import { knowledgeClient } from './api';
import type { Documents, Passage, Search } from './contracts';
import { createKnowledgeView, createReportView } from './views';
import { reportClient, KnowledgeError } from './api';
import { decodeRun, decodeEvidence, decodeRuns, decodeContextBinding } from './contracts';
import type { Run } from './contracts';
import type { ReviewInput } from './api';

export type ReportClient = typeof reportClient;
export function mountReports(root: HTMLElement, caseId: string, client: ReportClient = reportClient, options: { pollInterval?: number; maxPolls?: number } = {}) {
  let generation = 0, disposed = false, polls = 0;
  let pending = new AbortController(), evidencePending: AbortController | undefined;
  let timer: ReturnType<typeof setTimeout> | undefined;
  let snapshot = '', revision = '', selected: Run | undefined;
  let saved: Run[] = [];
  let totalCount = 0;
  let createKey: string | undefined;
  const actionKeys = new Map<string, string>();
  const history = new Map<string, Run>();
  let blocked: string | undefined;
  const interval = Math.min(5000, Math.max(10, options.pollInterval ?? 1000));
  const maximum = Math.min(120, Math.max(1, options.maxPolls ?? 120));
  const current = (token: number) => !disposed && generation === token;
  function begin() { generation++; clearTimeout(timer); pending.abort(); evidencePending?.abort(); pending = new AbortController(); return generation; }
  const view = createReportView(root, { start: () => { void create(); }, refresh: () => { void initialize(); }, select: id => { const run = saved.find(item => item.attempt_id === id) ?? history.get(id); if (run) { const token = begin(); polls = 0; show(run, token); } }, evidence: id => { void evidence(id); }, retry: reuse => { void mutate('retry', reuse); }, cancel: () => { void mutate('cancel', false); }, parent: () => { void parent(); }, review: body => { void review(body); } });
  function checked(value: unknown, expected?: string) { const run = decodeRun(value); if (run.case_id !== caseId || run.context_revision !== revision || run.snapshot_ref !== snapshot || (expected && run.attempt_id !== expected)) throw new Error(); return run; }
  function show(run: Run, token: number) {
    saved = saved.map(item => item.attempt_id === run.attempt_id ? run : item);
    view.saved(saved, totalCount, totalCount > 20);
    selected = run; view.run(run, run.context_revision !== revision || !saved.some(item => item.attempt_id === run.attempt_id));
    if (run.report) history.set(run.attempt_id, run);
    view.historical([...history.values()].filter(item => item.context_revision !== revision));
    if (blocked) view.recoveryError(blocked, true);
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
      if (revision !== binding.context_revision) { createKey = undefined; actionKeys.clear(); }
      snapshot = binding.snapshot_ref; revision = binding.context_revision; blocked = undefined;
      saved = result.items.map(run => checked(run)); totalCount = result.total_count; view.saved(saved, totalCount, result.truncated);
      view.historical([...history.values()].filter(item => item.context_revision !== revision));
      if (saved.length) show(saved[0], token); else { selected = undefined; view.empty(); }
    } catch (error) { if (current(token)) view.error(error instanceof KnowledgeError ? error.code : 'invalid_response'); }
  }
  async function create() {
    if (!snapshot || disposed || blocked) return;
    const token = begin(); view.loading(); polls = 0;
    createKey ??= crypto.randomUUID();
    try {
      const value = await client.create(caseId, snapshot, revision, createKey, pending.signal);
      if (!current(token)) return;
      const run = checked(value); createKey = undefined;
      if (!saved.some(item => item.attempt_id === run.attempt_id)) totalCount++;
      saved = [run, ...saved.filter(item => item.attempt_id !== run.attempt_id)].slice(0, 20);
      show(run, token);
    } catch (error) { if (current(token)) { const code = error instanceof KnowledgeError ? error.code : 'invalid_response'; blocked = ['stale_snapshot', 'revision_conflict', 'request_conflict'].includes(code) ? code : undefined; view.error(code); } }
  }
  async function mutate(operation: 'retry' | 'cancel', reuse: boolean) {
    const run = selected;
    if (!run || disposed || blocked || run.context_revision !== revision) return;
    const token = begin(); view.loading(); polls = 0;
    // The action key survives uncertain transport, including an aborted browser request.
    const identity = `${run.attempt_id}:${run.revision}:${operation}:${reuse}`;
    let key = actionKeys.get(identity); if (!key) { key = crypto.randomUUID(); actionKeys.set(identity, key); }
    try {
      const value = operation === 'retry' ? await client.retry(run, reuse, key, pending.signal) : await client.cancel(run, key, pending.signal);
      if (!current(token)) return;
      const next = checked(value, operation === 'cancel' ? run.attempt_id : undefined);
      if (next.run_id !== run.run_id || (operation === 'retry' && (next.parent_attempt_id !== run.attempt_id || next.attempt_id === run.attempt_id))) throw new Error();
      actionKeys.delete(identity);
      if (operation === 'retry') saved = [next, ...saved.filter(item => item.run_id !== next.run_id)].slice(0, 20);
      show(next, token);
    } catch (error) {
      if (!current(token)) return;
      const code = error instanceof KnowledgeError ? error.code : 'invalid_response';
      blocked = ['stale_snapshot', 'revision_conflict', 'request_conflict', 'invalid_transition'].includes(code) ? code : undefined;
      show(run, token); clearTimeout(timer);
      if (!blocked) view.recoveryError(code, false);
    }
  }
  async function parent() {
    const run = selected; if (!run?.parent_attempt_id) return;
    const token = begin(); view.loading();
    try {
      const value = await client.attempt(run.parent_attempt_id, caseId, run.context_revision, pending.signal);
      if (!current(token)) return;
      const previous = decodeRun(value);
      if (previous.attempt_id !== run.parent_attempt_id || previous.run_id !== run.run_id || previous.case_id !== caseId || previous.context_revision !== run.context_revision || previous.snapshot_ref !== run.snapshot_ref) throw new Error();
      show(previous, token);
    } catch { if (current(token)) view.error('invalid_response'); }
  }
  async function review(body: ReviewInput) {
    const run = selected;
    if (!run?.report || disposed || blocked || run.context_revision !== revision || !saved.some(item => item.attempt_id === run.attempt_id)) return;
    const token = begin(); view.loading();
    const identity = `${run.attempt_id}:${run.revision}:review:${JSON.stringify(body)}`;
    let key = actionKeys.get(identity); if (!key) { key = crypto.randomUUID(); actionKeys.set(identity, key); }
    try {
      const value = await client.review(run, body, key, pending.signal);
      if (!current(token)) return;
      const next = checked(value, run.attempt_id);
      if (next.run_id !== run.run_id || next.revision !== run.revision + 1 || next.state !== 'reviewed' || next.report?.report_id !== body.report_id || next.review?.supersedes_review_id !== body.supersedes_review_id) throw new Error();
      actionKeys.delete(identity); show(next, token);
    } catch (error) {
      if (!current(token)) return;
      const code = error instanceof KnowledgeError ? error.code : 'invalid_response';
      blocked = ['stale_snapshot', 'revision_conflict', 'request_conflict', 'invalid_transition'].includes(code) ? code : undefined;
      show(run, token); view.restoreReview(body);
      if (!blocked) view.recoveryError(code, false);
    }
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
