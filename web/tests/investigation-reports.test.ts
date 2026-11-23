import { readFileSync } from 'node:fs';
import { afterEach, expect, it, vi } from 'vitest';
import { decodeRun, decodeEvidence } from '../src/investigation/contracts';
import { mountReports } from '../src/investigation/controller';
import { reportClient } from '../src/investigation/api';

const example = (name: string) => JSON.parse(readFileSync(new URL('../../specs/003-ai-investigation/contracts/examples/' + name + '.json', import.meta.url), 'utf8'));
const ready = () => example('run-ready');
const evidence = () => example('evidence-fixture');
const tick = () => new Promise(resolve => setTimeout(resolve, 0));
let dispose: (() => void) | undefined;
afterEach(() => { dispose?.(); dispose = undefined; document.body.replaceChildren(); vi.useRealTimers(); vi.unstubAllGlobals(); });
function root() { const el = document.createElement('section'); document.body.append(el); return el; }
function clientWith(run = ready()) {
  return {
    list: vi.fn().mockResolvedValue({ contract_version: 1, total_count: 1, truncated: false, items: [run], snapshot_ref: run.snapshot_ref, context_revision: run.context_revision }),
    create: vi.fn().mockResolvedValue(run), attempt: vi.fn().mockResolvedValue(run), evidence: vi.fn().mockResolvedValue(evidence()),
    retry: vi.fn(), cancel: vi.fn(), review: vi.fn(),
  };
}

it('uses relative encoded report URLs, strict status errors and server snapshot binding', async () => {
  const run = ready();
  const fetcher = vi.fn().mockResolvedValue(new Response(JSON.stringify({ contract_version: 1, total_count: 1, truncated: false, items: [run] }), { headers: { 'content-type': 'application/json', 'x-investigation-snapshot': run.snapshot_ref, 'x-investigation-context': run.context_revision } }));
  vi.stubGlobal('fetch', fetcher);
  expect((await reportClient.list('CASE-001')).snapshot_ref).toBe(run.snapshot_ref);
  expect(fetcher.mock.calls[0][0]).toBe('/api/investigation/runs?case_id=CASE-001');
  fetcher.mockResolvedValueOnce(new Response(JSON.stringify(run), { status: 202, headers: { 'content-type': 'application/json' } }));
  await reportClient.create('CASE-001', run.snapshot_ref, run.context_revision, 'fixed-key');
  const sent = fetcher.mock.calls[1][1];
  expect(JSON.parse(sent.body)).toEqual({ case_id: 'CASE-001', source_mode: 'fixture', snapshot_ref: run.snapshot_ref });
  expect(sent.headers['Idempotency-Key']).toBe('fixed-key');
  fetcher.mockResolvedValueOnce(new Response(JSON.stringify({ ...evidence(), attempt_id: 'att_' + 'f'.repeat(32) }), { headers: { 'content-type': 'application/json' } }));
  await expect(reportClient.evidence(run.attempt_id, evidence().evidence_id, run.context_revision)).rejects.toThrow();
  fetcher.mockResolvedValueOnce(new Response(JSON.stringify({ contract_version: 1, error: { code: 'request_conflict', message: 'Controlled', retryable: false } }), { status: 503, headers: { 'content-type': 'application/json' } }));
  await expect(reportClient.attempt(run.attempt_id, run.case_id, run.context_revision)).rejects.toMatchObject({ code: 'invalid_response' });
});

it('decodes complete closed nested report and evidence envelopes', () => {
  expect(decodeRun(ready())).toEqual(ready());
  expect(decodeEvidence(evidence())).toEqual(evidence());
});

it('rejects unknown fields, broken identities, invented citations and bounds', () => {
  const mutations = [
    (v: ReturnType<typeof ready>) => { v.secret = true; },
    (v: ReturnType<typeof ready>) => { v.report.draft.summary[0].permission = true; },
    (v: ReturnType<typeof ready>) => { v.report.attempt_id = 'att_' + 'f'.repeat(32); },
    (v: ReturnType<typeof ready>) => { v.report.context_revision = 'f'.repeat(64); },
    (v: ReturnType<typeof ready>) => { v.report.draft.citations = []; },
    (v: ReturnType<typeof ready>) => { v.budget.provider_requests = 9; },
    (v: ReturnType<typeof ready>) => { v.state = 'failed'; },
    (v: ReturnType<typeof ready>) => { v.created_at = '2026-02-30T00:00:00Z'; },
  ];
  for (const mutate of mutations) { const run = ready(); mutate(run); expect(() => decodeRun(run)).toThrow(); }
  const item = evidence(); item.facts[0].permission = true;
  expect(() => decodeEvidence(item)).toThrow();
});

it('renders typed sections, literal text, notices and exact bound evidence on explicit click', async () => {
  const run = ready(); run.report.draft.summary[0].text = '<img src=x onerror=alert(1)> literal';
  const client = clientWith(run); const el = root();
  dispose = mountReports(el, 'CASE-001', client);
  await tick();
  expect(client.create).not.toHaveBeenCalled();
  expect(el.textContent).toContain('TEST provider');
  expect(el.textContent).toContain('nije verovatnoća');
  expect(el.textContent).toContain('Semantički pregled: na čekanju');
  expect(el.textContent).toContain('<img src=x onerror=alert(1)> literal');
  expect(el.querySelector('img')).toBeNull();
  expect(el.textContent).toContain('Uočene činjenice');
  el.querySelector<HTMLButtonElement>('[data-evidence]')!.click(); await tick();
  expect(client.evidence.mock.calls[0].slice(0, 3)).toEqual([run.attempt_id, evidence().evidence_id, run.context_revision]);
  expect(el.textContent).toContain(evidence().text);
});

it('shows queued work, starts only on explicit action and stops bounded polling', async () => {
  vi.useFakeTimers();
  const run = ready(); run.state = 'created'; run.report = null; run.trace = [];
  const client = clientWith(run); client.list.mockResolvedValue({ contract_version: 1, total_count: 0, truncated: false, items: [], snapshot_ref: run.snapshot_ref, context_revision: run.context_revision });
  const el = root(); dispose = mountReports(el, 'CASE-001', client, { pollInterval: 10, maxPolls: 2 });
  await vi.advanceTimersByTimeAsync(0);
  expect(client.create).not.toHaveBeenCalled();
  el.querySelector<HTMLButtonElement>('[data-start]')!.click();
  await vi.advanceTimersByTimeAsync(50);
  expect(client.create).toHaveBeenCalledTimes(1);
  expect(client.attempt).toHaveBeenCalledTimes(2);
  expect(el.textContent).toContain('čeka worker');
  expect(el.textContent).toContain('Automatska provera je zaustavljena');
  expect(el.querySelector('[data-refresh]')).not.toBeNull();
});

it.each(['needs_information', 'failed', 'gathering_evidence', 'drafting'])('shows truthful %s state', async state => {
  const run = ready(); run.state = state;
  if (state === 'needs_information') run.report.draft.outcome = state;
  else run.report = null;
  if (state === 'failed') run.failure = { code: 'output_invalid', message: 'Controlled failure', outcome_unknown: false };
  const el = root(); dispose = mountReports(el, 'CASE-001', clientWith(run)); await tick();
  expect(el.querySelector('[data-run-state]')?.getAttribute('data-run-state')).toBe(state);
  if (state === 'failed') expect(el.textContent).toContain('output_invalid');
});

it('reopens a budget failure without starting or retrying an investigation', async () => {
  const run = ready();
  run.state = 'failed';
  run.report = null;
  run.failure = { code: 'budget_exhausted', message: 'Budget exceeded', outcome_unknown: false };
  const client = clientWith(run);
  const el = root();
  dispose = mountReports(el, 'CASE-001', client);
  await tick();

  expect(el.querySelector('[data-run-state="failed"]')).not.toBeNull();
  expect(el.querySelector('[role="alert"]')?.textContent).toContain('budget_exhausted');
  expect(el.querySelector('[data-evidence]')).toBeNull();
  expect(client.create).not.toHaveBeenCalled();
  expect(client.retry).not.toHaveBeenCalled();
});

it('rejects other-case replies and cancels obsolete browser work including late evidence', async () => {
  const run = ready(); const wrong = { ...run, case_id: 'CASE-002' };
  const el = root(); dispose = mountReports(el, 'CASE-001', clientWith(wrong)); await tick();
  expect(el.querySelector('[role=alert]')).not.toBeNull();
  dispose();
  const client = clientWith();
  let finish: (value: unknown) => void = () => {};
  client.evidence.mockImplementation(() => new Promise(resolve => { finish = resolve; }));
  dispose = mountReports(el, 'CASE-001', client); await tick();
  el.querySelector<HTMLButtonElement>('[data-evidence]')!.click(); await tick();
  const signal = client.evidence.mock.calls[0][3] as AbortSignal;
  dispose(); finish(evidence()); await tick();
  expect(signal.aborted).toBe(true); expect(el.textContent).toBe('');
});
