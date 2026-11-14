import { afterEach, expect, it, vi } from 'vitest';
import { decodeSearch } from '../src/investigation/contracts';
import { searchKnowledge } from '../src/investigation/api';
import { mountKnowledge } from '../src/investigation/controller';

const corpus = 'corpus_' + 'a'.repeat(64);
const retrieval = 'b'.repeat(64);
const document = { doc_id: 'authored', title: 'SIMULATED test', origin_kind: 'simulated',
  source_uri: 'local:test', published_at: null, unknown_date_reason: 'Unknown',
  retrieved_at: '2026-01-01T00:00:00Z', jurisdiction: 'SIMULATED', version: 'test-v1',
  reviewed_by: 'TEST REVIEWER', reviewed_at: '2026-01-02T00:00:00Z', reuse_terms: 'Authored',
  content_sha256: 'c'.repeat(64), included_sections: ['Test'], applicability_notes: 'Not real policy' };
const passage = { passage_id: 'd'.repeat(64), corpus_version: corpus, document,
  section: 'Test', ordinal: 0, text: '<img src=x onerror=alert(1)> literal', content_sha256: 'e'.repeat(64) };
const result = { contract_version: 1, corpus_version: corpus, retrieval_version: retrieval,
  query: 'money', status: 'matched', hits: [{ rank: 1, score: 1, passage }] };
const tick = () => new Promise(resolve => setTimeout(resolve, 0));
let dispose: (() => void) | undefined;
afterEach(() => { dispose?.(); dispose = undefined; documentGlobal().body.replaceChildren(); vi.unstubAllGlobals(); });
function documentGlobal() { return window.document; }
function root() { const element = window.document.createElement('main'); window.document.body.append(element); return element; }
function submit(element: HTMLElement, query = 'money') {
  const input = element.querySelector('input'); expect(input).not.toBeNull();
  input!.value = query;
  element.querySelector('form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
}

it('strictly decodes closed nested search results', () => {
  expect(decodeSearch(result)).toEqual(result);
  for (const value of [{ ...result, secret: true }, { ...result, hits: [{ rank: 1, score: NaN, passage }] },
    { ...result, hits: [{ rank: 1, score: 1, passage: { ...passage, extra: true } }] }]) {
    expect(() => decodeSearch(value)).toThrow();
  }
});

it('uses relative encoded URLs and propagates caller cancellation', async () => {
  const fetcher = vi.fn().mockResolvedValue(new Response(JSON.stringify({ ...result, query: 'a&b' }),
    { headers: { 'content-type': 'application/json' } }));
  vi.stubGlobal('fetch', fetcher);
  const controller = new AbortController();
  await searchKnowledge('a&b', corpus, retrieval, controller.signal);
  expect(fetcher.mock.calls[0][0]).toBe(`/api/knowledge/search?q=a%26b&corpus=${corpus}&retrieval=${retrieval}`);
  expect(fetcher.mock.calls[0][1].signal).toBeInstanceOf(AbortSignal);
  fetcher.mockImplementationOnce(() => new Promise(() => {}));
  const cancelled = searchKnowledge('money', corpus, retrieval, controller.signal);
  controller.abort();
  await expect(cancelled).rejects.toMatchObject({ code: 'cancelled' });
  expect(fetcher.mock.calls[1][1].signal.aborted).toBe(true);
});

it('shows provenance and literal passage text with keyboard focus', async () => {
  const element = root();
  const client = { documents: vi.fn().mockResolvedValue({ contract_version: 1, corpus_version: corpus, documents: [document] }),
    search: vi.fn().mockResolvedValue(result), passage: vi.fn().mockResolvedValue(passage) };
  dispose = mountKnowledge(element, client);
  await tick(); submit(element); await tick();
  const button = element.querySelector<HTMLButtonElement>('[data-passage]'); expect(button).not.toBeNull();
  button!.click(); await tick();
  expect(element.textContent).toContain('SIMULATED'); expect(element.textContent).toContain('test-v1');
  expect(element.textContent).toContain('Not real policy'); expect(element.textContent).toContain(passage.text);
  expect(element.querySelector('img')).toBeNull();
  expect(window.document.activeElement?.textContent).toContain('Izvor');
});

it('renders no match, error/retry and ignores old search/selection responses', async () => {
  const element = root(); let oldSearch: (v: unknown) => void = () => {}; let oldPassage: (v: unknown) => void = () => {};
  const client = { documents: vi.fn().mockResolvedValue({ contract_version: 1, corpus_version: corpus, documents: [document] }),
    search: vi.fn().mockImplementationOnce(() => new Promise(resolve => { oldSearch = resolve; }))
      .mockResolvedValueOnce({ ...result, query: 'second', status: 'no_match', hits: [] })
      .mockRejectedValueOnce(new Error('PRIVATE raw error')).mockResolvedValue(result),
    passage: vi.fn().mockImplementationOnce(() => new Promise(resolve => { oldPassage = resolve; })) };
  dispose = mountKnowledge(element, client); await tick();
  submit(element); await tick(); submit(element, 'second'); await tick();
  oldSearch(result); await tick(); expect(element.textContent).toContain('Nema');
  expect(client.search.mock.calls[0][3].aborted).toBe(true);
  submit(element); await tick(); expect(element.textContent).not.toContain('PRIVATE');
  const retry = Array.from(element.querySelectorAll('button')).find(b => b.textContent?.includes('Pokušaj'));
  expect(retry).toBeDefined(); retry!.click(); await tick();
  element.querySelector<HTMLButtonElement>('[data-passage]')!.click(); await tick();
  submit(element, 'second'); await tick(); oldPassage(passage); await tick();
  expect(element.textContent).not.toContain(passage.text);
});

it('rejects invalid timestamps, versions, missing nullable metadata and oversized result arrays', () => {
  const changed = (patch: object) => ({ ...result, hits: [{ rank: 1, score: 1, passage: { ...passage, document: { ...document, ...patch } } }] });
  for (const value of [changed({ reviewed_at: '2026-02-30T00:00:00Z' }),
    changed({ retrieved_at: '2026-01-01T24:00:00Z' }),
    changed({ retrieved_at: '2026-01-01T00:00:00Z\n' }),
    { ...result, contract_version: 2 }, { ...result, hits: Array(6).fill(result.hits[0]) }]) {
    expect(() => decodeSearch(value)).toThrow();
  }
  const missing = structuredClone(result);
  Reflect.deleteProperty(missing.hits[0].passage.document, 'published_at');
  expect(() => decodeSearch(missing)).toThrow();
});
