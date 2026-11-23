import { act } from 'react';
import { readFileSync } from 'node:fs';
import { createRoot } from 'react-dom/client';
import { expect, it, vi } from 'vitest';
import { decodeLocalContribution } from '../src/scoring/localContributions';
import { LocalContributions } from '../src/pages/LocalContributions';
import { DETAIL_V2 } from './dataset-fixture';

const example = JSON.parse(readFileSync('../specs/003-ai-investigation/contracts/examples/' +
  'local-contribution-sidecar-v1.proposal.json', 'utf8')).contribution_sidecar_v1;
const detail = { ...DETAIL_V2, case_id: example.case_id, snapshot_ref: example.assessment_run_id,
  transaction: { ...DETAIL_V2.transaction, transaction_id: example.transaction_id,
    paid: { ...DETAIL_V2.transaction.paid, currency: 'Canadian Dollar' },
    received: { ...DETAIL_V2.transaction.received, currency: 'Canadian Dollar' } },
  risk_assessment: { ...DETAIL_V2.risk_assessment, score: example.score,
    explanation: { status: 'unavailable', reason_code: 'unsupported_method',
      feature_snapshot_digest: example.feature_snapshot_digest } } } as any;

it('decodes the separate method and rejects nonfinite or incorrect reconstruction', () => {
  expect(decodeLocalContribution(example)).toMatchObject({ status: 'available', explained_scale: 'log_odds' });
  expect(() => decodeLocalContribution({ ...example, explained_scale: 'risk_score' })).toThrow();
  expect(() => decodeLocalContribution({ ...example, score: Infinity })).toThrow();
  expect(() => decodeLocalContribution({ ...example, raw_score: 0 })).toThrow();
});

it.each([
  [example, 'log-odds'],
  [{ contract_version: 1, status: 'unavailable', reason_code: 'not_configured' }, 'nisu dostupni'],
  [{ contract_version: 1, status: 'invalid', reason_code: 'verification_failed' }, 'nisu prošli provjeru'],
])('shows available, unavailable and invalid states', async (payload, expected) => {
  const fetcher = vi.fn().mockResolvedValue(new Response(JSON.stringify(payload),
    { headers: { 'content-type': 'application/json' } }));
  vi.stubGlobal('fetch', fetcher);
  const container = document.createElement('div'); document.body.append(container);
  const root = createRoot(container);
  await act(async () => { root.render(<LocalContributions detail={detail} />); });
  await act(async () => { await Promise.resolve(); });
  expect(container.textContent).toContain(expected);
  await act(async () => { root.unmount(); }); container.remove(); vi.unstubAllGlobals();
});

it('offers retry after malformed response', async () => {
  const fetcher = vi.fn().mockResolvedValue(new Response('{"bad":true}',
    { headers: { 'content-type': 'application/json' } }));
  vi.stubGlobal('fetch', fetcher);
  const container = document.createElement('div'); document.body.append(container);
  const root = createRoot(container);
  await act(async () => { root.render(<LocalContributions detail={detail} />); });
  await act(async () => { await Promise.resolve(); });
  expect(container.querySelector('[role="alert"]')).not.toBeNull();
  await act(async () => { (container.querySelector('button') as HTMLButtonElement).click(); });
  expect(fetcher).toHaveBeenCalledTimes(2);
  await act(async () => { root.unmount(); }); container.remove(); vi.unstubAllGlobals();
});

it('shows readable rounded log-odds with exact sidecar values in expandable details', async () => {
  const payload = { ...example, items: [
    example.items[0],
    { feature_key: 'current_amount_paid_log1p', observed_value: '8.82710875774195',
      unit: 'log1p_source_amount', contribution: 2.4703085537597906, direction: 'increases' },
    { feature_key: 'sender_paid_sum_same_currency_24h', observed_value: '123.456789',
      unit: 'same_currency_amount', contribution: -3.804758062294226, direction: 'decreases' },
  ] };
  payload.remainder = payload.raw_score - payload.base_value -
    payload.items.reduce((total: number, item: { contribution: number }) => total + item.contribution, 0);
  const fetcher = vi.fn().mockResolvedValue(new Response(JSON.stringify(payload),
    { headers: { 'content-type': 'application/json' } }));
  vi.stubGlobal('fetch', fetcher);
  const container = document.createElement('div'); document.body.append(container);
  const root = createRoot(container);
  await act(async () => { root.render(<LocalContributions detail={detail} />); });
  await act(async () => { await Promise.resolve(); });
  const summary = container.querySelector('ul')?.textContent ?? '';
  expect(summary).toContain('Format plaćanja');
  expect(summary).toContain('Plaćeni iznos (log1p transformacija)');
  expect(summary).toContain('8.8271');
  expect(summary).toContain('Zbir plaćenog iznosa pošiljaoca');
  expect(summary).toContain('123.46 Canadian Dollar');
  expect(summary).toContain('log-odds');
  expect(summary).not.toContain('current_amount_paid_log1p');
  expect(summary).not.toContain('8.82710875774195');
  expect(container.textContent).toContain('nije izvorni novčani iznos');
  const disclosure = container.querySelector('details');
  expect(disclosure?.open).toBe(false);
  expect(disclosure?.textContent).toContain('8.82710875774195');
  expect(disclosure?.textContent).toContain('123.456789');
  expect(disclosure?.textContent).toContain('2.4703085537597906');
  expect(disclosure?.textContent).toContain('-9.945714675483181');
  await act(async () => { disclosure?.querySelector('summary')?.click(); });
  expect(disclosure?.open).toBe(true);
  await act(async () => { root.unmount(); }); container.remove(); vi.unstubAllGlobals();
});
