import { readFileSync } from 'node:fs';
import { afterEach, expect, it, vi } from 'vitest';
import { mountReports } from '../src/investigation/controller';
import { reportClient, KnowledgeError } from '../src/investigation/api';

const example = (name: string) => JSON.parse(readFileSync(new URL('../../specs/003-ai-investigation/contracts/examples/' + name + '.json', import.meta.url), 'utf8'));
const ready = () => example('run-ready');
const ended = () => ({ ...ready(), state: 'failed', report: null, failure: { code: 'interrupted', message: 'Controlled', outcome_unknown: true } });
const tick = () => new Promise(resolve => setTimeout(resolve, 0));
const list = (run = ended()) => ({ contract_version: 1, items: [run], total_count: 1, truncated: false, snapshot_ref: run.snapshot_ref, context_revision: run.context_revision });
function client() { return { list: vi.fn().mockResolvedValue(list()), create: vi.fn(), attempt: vi.fn(), evidence: vi.fn(), retry: vi.fn(), cancel: vi.fn(), review: vi.fn() }; }
let dispose: (() => void) | undefined;
afterEach(() => { dispose?.(); document.body.replaceChildren(); vi.unstubAllGlobals(); });
function root() { const el = document.createElement('section'); document.body.append(el); return el; }

it('sends explicit retry/cancel headers and checks child/parent/context identity', async () => {
  const parent = ended(), child = { ...parent, attempt_id: 'att_' + 'd'.repeat(32), parent_attempt_id: parent.attempt_id, state: 'created', failure: null, revision: 1 };
  const fetcher = vi.fn().mockResolvedValue(new Response(JSON.stringify(child), { status: 202, headers: { 'content-type': 'application/json' } })); vi.stubGlobal('fetch', fetcher);
  await reportClient.retry(parent, true, 'retry-key');
  expect(fetcher.mock.calls[0][0]).toContain('/' + parent.attempt_id + '/retry');
  expect(fetcher.mock.calls[0][1].headers).toMatchObject({ 'If-Match': String(parent.revision), 'Idempotency-Key': 'retry-key' });
  expect(JSON.parse(fetcher.mock.calls[0][1].body)).toEqual({ reuse_evidence: true });
  fetcher.mockResolvedValueOnce(new Response(JSON.stringify({ ...parent, state: 'cancelled' }), { headers: { 'content-type': 'application/json' } }));
  await reportClient.cancel(parent, 'cancel-key');
  expect(JSON.parse(fetcher.mock.calls[1][1].body)).toEqual({});
  fetcher.mockResolvedValueOnce(new Response(JSON.stringify({ ...child, parent_attempt_id: null }), { status: 202, headers: { 'content-type': 'application/json' } }));
  await expect(reportClient.retry(parent, true, 'retry-key')).rejects.toThrow();
});

it('requires explicit retry, discloses spend and keeps one action key after uncertain transport', async () => {
  const c = client(), el = root(); c.retry.mockRejectedValue(new KnowledgeError('timeout'));
  dispose = mountReports(el, 'CASE-001', c); await tick();
  expect(c.retry).not.toHaveBeenCalled(); expect(el.textContent).toContain('dodatnu potrošnju');
  el.querySelector<HTMLButtonElement>('[data-retry]')!.click(); await tick();
  el.querySelector<HTMLButtonElement>('[data-retry]')!.click(); await tick();
  expect(c.retry).toHaveBeenCalledTimes(2);
  expect(c.retry.mock.calls[0][2]).toBe(c.retry.mock.calls[1][2]);
  expect(c.create).not.toHaveBeenCalled();
});

it('stale revision requires explicit refresh, never auto retry', async () => {
  const c = client(), el = root(); c.retry.mockRejectedValue(new KnowledgeError('revision_conflict'));
  dispose = mountReports(el, 'CASE-001', c); await tick();
  el.querySelector<HTMLButtonElement>('[data-retry]')!.click(); await tick();
  expect(c.list).toHaveBeenCalledTimes(1); expect(el.querySelector<HTMLButtonElement>('[data-retry]')?.disabled ?? true).toBe(true);
  el.querySelector<HTMLButtonElement>('[data-refresh]')!.click(); await tick(); expect(c.list).toHaveBeenCalledTimes(2);
});

it('ignores same-case old-context retry replies after explicit refresh', async () => {
  const c = client(), el = root(); let finish: (v: unknown) => void = () => {};
  c.retry.mockImplementation(() => new Promise(resolve => { finish = resolve; }));
  dispose = mountReports(el, 'CASE-001', c); await tick();
  el.querySelector<HTMLButtonElement>('[data-retry]')!.click(); await tick();
  const changed = { ...ended(), context_revision: 'e'.repeat(64), snapshot_ref: 'fixture_' + 'e'.repeat(64) };
  c.list.mockResolvedValue(list(changed));
  el.querySelector<HTMLButtonElement>('[data-refresh]')!.click(); await tick();
  finish({ ...ended(), state: 'created', failure: null, parent_attempt_id: ended().attempt_id, attempt_id: 'att_' + 'd'.repeat(32) }); await tick();
  expect(el.textContent).toContain(changed.context_revision); expect(el.querySelector('[data-run-state=created]')).toBeNull();
});

it('keeps a selected historical report when refresh finds a new source snapshot', async () => {
  const c = client(), el = root(), old = ready(); c.list.mockResolvedValue(list(old));
  dispose = mountReports(el, 'CASE-001', c); await tick();
  const changed = { ...ended(), context_revision: 'e'.repeat(64), snapshot_ref: 'fixture_' + 'e'.repeat(64) };
  c.list.mockResolvedValue({ ...list(changed), items: [], total_count: 0 });
  el.querySelector<HTMLButtonElement>('[data-refresh]')!.click(); await tick();
  expect(el.querySelector('[data-history]')).not.toBeNull();
  el.querySelector<HTMLButtonElement>('[data-history]')!.click(); await tick();
  expect(el.querySelector('[data-run-state=ready_for_review]')).not.toBeNull();
  expect(el.textContent).toContain('Istorijski');
  expect(el.querySelector('[data-evidence]')).not.toBeNull();
});

it('reopens the saved parent draft from a child without starting a new attempt', async () => {
  const c = client(), el = root(), parent = ready(); parent.state = 'needs_information'; parent.report.draft.outcome = 'needs_information';
  const child = { ...ended(), attempt_id: 'att_' + 'd'.repeat(32), parent_attempt_id: parent.attempt_id };
  c.list.mockResolvedValue(list(child)); c.attempt.mockResolvedValue(parent);
  dispose = mountReports(el, 'CASE-001', c); await tick();
  el.querySelector<HTMLButtonElement>('[data-parent]')!.click(); await tick();
  expect(c.attempt.mock.calls[0].slice(0, 3)).toEqual([parent.attempt_id, parent.case_id, parent.context_revision]);
  expect(el.querySelector('[data-run-state=needs_information]')).not.toBeNull();
  expect(el.textContent).toContain('Istorijski'); expect(c.retry).not.toHaveBeenCalled();
});
