import { act, createElement } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { MemoryRouter, Outlet } from 'react-router-dom';
import { AppRoutes } from '../src/AppRoutes';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { decodeEdaSummary } from '../src/scoring/contracts';
import { createEdaView } from '../src/scoring/views';

const source = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040';
const summary = decodeEdaSummary({
  dataset_version: 'ibm-hi-small-b19d39f5', source_sha256: source, synthetic_data: true,
  coverage_start_utc: '2022-09-01T00:00:00Z', coverage_end_utc: '2022-09-02T00:00:00Z',
  source_count: 2, accepted_count: 2, rejected_count: 0, warmup_count: 1,
  scoreable_count: 1, quality_counts: {}, omitted_amount_currencies: { paid: 0, received: 0 },
  series: [
    { series_id: 'sender_bank_count', label: 'Sender bank', unit: 'transactions',
      bucket_labels: ['Bank <img src=x onerror=alert(1)>'], values: [2], denominator: 2,
      currency: null, side: null, timezone: null },
    { series_id: 'utc_transaction_count', label: 'Transactions by UTC day', unit: 'transactions',
      bucket_labels: ['2022-09-01'], values: [2], denominator: 2,
      currency: null, side: null, timezone: 'UTC' },
    { series_id: 'paid_amount_US Dollar', label: 'Paid amount: US Dollar', unit: 'amount',
      bucket_labels: ['2022-09-01'], values: [10], denominator: 1,
      currency: 'US Dollar', side: 'paid', timezone: 'UTC' },
    { series_id: 'received_amount_Euro', label: 'Received amount: Euro', unit: 'amount',
      bucket_labels: ['2022-09-01'], values: [9], denominator: 1,
      currency: 'Euro', side: 'received', timezone: 'UTC' },
  ],
});

vi.mock('../src/components/SiteFrame', () => ({ SiteFrame: Outlet }));
let routeRoot: Root | undefined;
async function openEdaRoute() {
  routeRoot = createRoot(document.getElementById('app')!);
  await act(async () => { routeRoot!.render(createElement(MemoryRouter, { initialEntries: ['/eda'] }, createElement(AppRoutes))); });
}

beforeEach(() => {
  window.history.replaceState({}, '', '/');
  document.body.innerHTML = '<main id="app"></main>';
});
afterEach(async () => { if (routeRoot) await act(async () => { routeRoot?.unmount(); }); routeRoot = undefined; document.body.replaceChildren(); vi.unstubAllGlobals(); });

it('renders an accessible bounded EDA page with separate currency units and safe text', () => {
  const root = document.querySelector<HTMLElement>('#app')!;
  const view = createEdaView(root, () => {});
  view.render({ kind: 'success', result: summary });
  expect(root.querySelector('h1')?.textContent).toContain('EDA');
  expect(root.querySelector('nav a[href="/"]')).not.toBeNull();
  expect(root.textContent).toContain(source);
  expect(root.textContent).toContain('2022-09-01');
  expect(root.textContent).toContain('2');
  expect(root.textContent).toContain('US Dollar');
  expect(root.textContent).toContain('Euro');
  expect(root.textContent).toContain('imenilac: 2');
  expect(root.textContent).toContain('imenilac: 1');
  expect(root.textContent).toContain('UTC');
  expect(root.querySelectorAll('table').length).toBeGreaterThan(0);
  expect(root.querySelectorAll('details.eda-disclosure').length).toBe(2);
  expect(root.querySelector('img, script')).toBeNull();
  expect(root.textContent).not.toMatch(/is_laundering|sender_account|receiver_account|transaction_id/);
});

it('shows explicit loading, empty, unavailable, malformed and retry states', () => {
  const root = document.querySelector<HTMLElement>('#app')!;
  let retries = 0;
  const view = createEdaView(root, () => { retries += 1; });
  view.render({ kind: 'loading' });
  expect(root.querySelector('[aria-busy="true"]')).not.toBeNull();
  expect(root.textContent).toMatch(/Učitavanje/);
  view.render({ kind: 'success', result: { ...summary, source_count: 0, accepted_count: 0,
    warmup_count: 0, scoreable_count: 0, coverage_start_utc: null,
    coverage_end_utc: null, series: [] } });
  expect(root.textContent).toMatch(/Nema.*podataka|Prazan/i);
  view.render({ kind: 'unavailable' });
  expect(root.querySelector('[role="alert"]')?.textContent).toMatch(/nisu dostupni/);
  view.render({ kind: 'error', message: 'Server je vratio neispravan odgovor.' });
  expect(root.querySelector('[role="alert"]')?.textContent).toMatch(/neispravan/);
  root.querySelector<HTMLButtonElement>('button')!.click();
  expect(retries).toBe(1);
});

it('opens /eda as a separate route and calls only the summary API', async () => {
  window.history.replaceState({}, '', '/eda');
  const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(new Response(JSON.stringify(summary), {
    headers: { 'content-type': 'application/json' },
  }));
  vi.stubGlobal('fetch', fetchMock);
  await openEdaRoute();
  await vi.waitFor(() => expect(document.body.textContent).toContain('US Dollar'));
  expect(fetchMock.mock.calls.map(([input]) => String(input))).toEqual(['/api/eda/summary']);
  expect(document.querySelector('nav a[href="/"]')).not.toBeNull();
  window.history.replaceState({}, '', '/');
});

it('moves through loading, unavailable, malformed and retry without a fallback summary', async () => {
  window.history.replaceState({}, '', '/eda');
  let resolveFirst!: (value: Response) => void;
  const first = new Promise<Response>(resolve => { resolveFirst = resolve; });
  const fetchMock = vi.fn<typeof fetch>()
    .mockReturnValueOnce(first)
    .mockResolvedValueOnce(new Response(JSON.stringify({ ...summary, target: 1 }), {
      headers: { 'content-type': 'application/json' },
    }))
    .mockResolvedValueOnce(new Response(JSON.stringify(summary), {
      headers: { 'content-type': 'application/json' },
    }));
  vi.stubGlobal('fetch', fetchMock);
  await openEdaRoute();
  expect(document.body.textContent).toContain('Učitavanje EDA');
  resolveFirst(new Response(JSON.stringify({ error: {
    code: 'dataset_unavailable', message: '/private/secret',
  } }), { status: 404, headers: { 'content-type': 'application/json' } }));
  await vi.waitFor(() => expect(document.querySelector('[role="alert"]')?.textContent)
    .toContain('nisu dostupni'));
  expect(document.body.textContent).not.toContain('/private/secret');
  document.querySelector<HTMLButtonElement>('button')!.click();
  await vi.waitFor(() => expect(document.querySelector('[role="alert"]')?.textContent)
    .toContain('neispravan odgovor'));
  expect(document.body.textContent).not.toContain('US Dollar');
  document.querySelector<HTMLButtonElement>('button')!.click();
  await vi.waitFor(() => expect(document.body.textContent).toContain('US Dollar'));
  expect(fetchMock).toHaveBeenCalledTimes(3);
  window.history.replaceState({}, '', '/');
});
