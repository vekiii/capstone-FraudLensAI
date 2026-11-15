import { readFileSync } from 'node:fs';
import { afterEach, expect, it, vi } from 'vitest';
import { mountReports } from '../src/investigation/controller';
import { reportClient, KnowledgeError } from '../src/investigation/api';
import { decodeRun } from '../src/investigation/contracts';

const example = (name: string) => JSON.parse(readFileSync(new URL('../../specs/003-ai-investigation/contracts/examples/' + name + '.json', import.meta.url), 'utf8'));
const ready = () => example('run-ready');
const tick = () => new Promise(resolve => setTimeout(resolve, 0));
const reviewed = (run = ready()) => ({ ...run, state: 'reviewed', revision: run.revision + 1,
  report: { ...run.report, semantic_review: 'reviewed_with_notes' }, review: { review_id: 'rev_' + 'd'.repeat(32), report_id: run.report.report_id, actor: 'TEST OPERATOR', disposition: 'close', rationale: 'Test reason', correction_note: null, supersedes_review_id: null, created_at: run.updated_at } });
function client(run = ready()) { return { list: vi.fn().mockResolvedValue({ contract_version: 1, items: [run], total_count: 1, truncated: false, snapshot_ref: run.snapshot_ref, context_revision: run.context_revision }), create: vi.fn(), attempt: vi.fn(), evidence: vi.fn(), retry: vi.fn(), cancel: vi.fn(), review: vi.fn() }; }
let dispose: (() => void) | undefined;
afterEach(() => { dispose?.(); document.body.replaceChildren(); vi.unstubAllGlobals(); });
function root() { const el = document.createElement('section'); document.body.append(el); return el; }
function fill(el: HTMLElement, disposition = 'close', rationale = 'Test reason', note = '') {
  el.querySelector<HTMLSelectElement>('[data-disposition]')!.value = disposition;
  el.querySelector<HTMLTextAreaElement>('[data-rationale]')!.value = rationale;
  el.querySelector<HTMLTextAreaElement>('[data-correction-note]')!.value = note;
  el.querySelector<HTMLFormElement>('[data-review-form]')!.dispatchEvent(new Event('submit', { cancelable: true }));
}

it('requires an explicit decision and trimmed rationale; cites original evidence without changing the draft', async () => {
  const run = ready(), c = client(run), el = root(); c.review.mockResolvedValue(reviewed(run));
  dispose = mountReports(el, run.case_id, c); await tick();
  expect(c.review).not.toHaveBeenCalled(); expect(el.querySelector<HTMLSelectElement>('[data-disposition]')!.value).toBe('');
  fill(el, '', 'Reason'); await tick(); fill(el, 'close', '  '); await tick();
  expect(c.review).not.toHaveBeenCalled();
  const ref = run.report.draft.citations[0]; el.querySelector<HTMLButtonElement>('[data-evidence]')!.click(); await tick();
  expect(c.evidence.mock.calls[0].slice(0, 3)).toEqual([run.attempt_id, ref, run.context_revision]);
  fill(el); await tick(); expect(c.review).toHaveBeenCalledTimes(1);
  expect(c.review.mock.calls[0][1]).toEqual({ report_id: run.report.report_id, disposition: 'close', rationale: 'Test reason', correction_note: null, supersedes_review_id: null });
  expect(el.textContent).toContain(run.report.draft.summary[0].text);
  expect(el.textContent).toContain('TEST OPERATOR'); expect(el.textContent).toContain('nije ocena kvaliteta');
});

it('restricts needs-information and offers no review for failed/cancelled/no-draft runs', async () => {
  const run = ready(); run.state = 'needs_information'; run.report.draft.outcome = 'needs_information';
  const el = root(); dispose = mountReports(el, run.case_id, client(run)); await tick();
  expect([...el.querySelectorAll<HTMLSelectElement>('[data-disposition] option')].map(o => o.value)).toEqual(['', 'request_more_information']);
  dispose();
  for (const state of ['failed', 'cancelled', 'created']) {
    const bad = { ...ready(), state, report: null }; dispose = mountReports(el, run.case_id, client(bad)); await tick();
    expect(el.querySelector('[data-review-form]')).toBeNull(); dispose();
  }
});

it('amends through a linked note, renders literal human text and leaves original AI claims visible', async () => {
  const run = reviewed(), c = client(run), el = root();
  const amended = { ...run, revision: run.revision + 1, review: { ...run.review, review_id: 'rev_' + 'e'.repeat(32), supersedes_review_id: run.review.review_id, correction_note: '<img src=x onerror=alert(1)>', disposition: 'escalate' } };
  c.review.mockResolvedValue(amended); dispose = mountReports(el, run.case_id, c); await tick();
  fill(el, 'escalate'); await tick(); expect(c.review).not.toHaveBeenCalled();
  fill(el, 'escalate', 'Test reason', amended.review.correction_note); await tick();
  expect(c.review.mock.calls[0][1].supersedes_review_id).toBe(run.review.review_id);
  expect(el.textContent).toContain(amended.review.correction_note); expect(el.querySelector('img')).toBeNull();
  expect(el.textContent).toContain(run.report.draft.summary[0].text); expect(el.textContent).toContain(run.review.review_id);
});

it('retains input and key after uncertain transport; stale writes require explicit refresh', async () => {
  const c = client(), el = root(); c.review.mockRejectedValueOnce(new KnowledgeError('timeout')).mockRejectedValueOnce(new KnowledgeError('revision_conflict'));
  dispose = mountReports(el, 'CASE-001', c); await tick(); fill(el); await tick();
  expect(el.querySelector<HTMLTextAreaElement>('[data-rationale]')!.value).toBe('Test reason');
  fill(el); await tick(); expect(c.review.mock.calls[0][2]).toBe(c.review.mock.calls[1][2]);
  expect(el.querySelector<HTMLButtonElement>('[data-review-submit]')!.disabled).toBe(true); expect(c.list).toHaveBeenCalledTimes(1);
  el.querySelector<HTMLButtonElement>('[data-refresh]')!.click(); await tick(); expect(c.list).toHaveBeenCalledTimes(2);
});

it('discards a late review reply after refresh/navigation to another source revision', async () => {
  const c = client(), el = root(); let finish: (value: unknown) => void = () => {};
  c.review.mockImplementation(() => new Promise(resolve => { finish = resolve; }));
  dispose = mountReports(el, 'CASE-001', c); await tick(); fill(el); await tick();
  const other = { ...ready(), context_revision: 'e'.repeat(64), snapshot_ref: 'fixture_' + 'e'.repeat(64) }; other.report.context_revision = other.context_revision;
  c.list.mockResolvedValue({ contract_version: 1, items: [other], total_count: 1, truncated: false, snapshot_ref: other.snapshot_ref, context_revision: other.context_revision });
  el.querySelector<HTMLButtonElement>('[data-refresh]')!.click(); await tick(); finish(reviewed()); await tick();
  expect(el.querySelector('[data-run-state=reviewed]')).toBeNull(); expect(el.textContent).toContain(other.context_revision);
});

it('sends closed review input with If-Match/key and rejects wrong report/revision/review linkage', async () => {
  const run = ready(), body = { report_id: run.report.report_id, disposition: 'close' as const, rationale: 'Test reason', correction_note: null, supersedes_review_id: null };
  const fetcher = vi.fn().mockResolvedValue(new Response(JSON.stringify(reviewed()), { status: 201, headers: { 'content-type': 'application/json' } })); vi.stubGlobal('fetch', fetcher);
  await reportClient.review(run, body, 'test-key');
  expect(fetcher.mock.calls[0][0]).toBe('/api/investigation/attempts/' + run.attempt_id + '/reviews');
  expect(fetcher.mock.calls[0][1].headers).toMatchObject({ 'If-Match': String(run.revision), 'Idempotency-Key': 'test-key' });
  expect(JSON.parse(fetcher.mock.calls[0][1].body)).toEqual(body);
  for (const change of [{ revision: run.revision }, { report: { ...run.report, report_id: 'f'.repeat(64) } }, { review: { ...reviewed().review, supersedes_review_id: 'rev_' + 'f'.repeat(32) } }]) {
    fetcher.mockResolvedValueOnce(new Response(JSON.stringify({ ...reviewed(), ...change }), { status: 201, headers: { 'content-type': 'application/json' } }));
    await expect(reportClient.review(run, body, 'test-key')).rejects.toThrow();
  }
  expect(() => decodeRun({ ...reviewed(), report: ready().report })).toThrow();
});

it('accepts 2000 Unicode characters and rejects an overlong rationale', async () => {
  const c = client(), el = root(); c.review.mockRejectedValue(new KnowledgeError('timeout'));
  dispose = mountReports(el, 'CASE-001', c); await tick();
  expect(el.querySelector<HTMLTextAreaElement>('[data-rationale]')!.maxLength).toBeGreaterThanOrEqual(4000);
  fill(el, 'close', 'x'.repeat(2001)); await tick(); expect(c.review).not.toHaveBeenCalled();
  fill(el, 'close', '😀'.repeat(2000)); await tick(); expect(c.review.mock.calls[0][1].rationale).toBe('😀'.repeat(2000));
});
