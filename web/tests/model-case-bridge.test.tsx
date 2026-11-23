import { act } from 'react';
import { readFileSync } from 'node:fs';
import { createRoot } from 'react-dom/client';
import { MemoryRouter } from 'react-router-dom';
import { expect, it, vi } from 'vitest';
import { decodeCaseDetailV2, decodeCaseListV2 } from '../src/contracts';
import { CasesPage } from '../src/pages/Cases';
import { ModelCasesPage } from '../src/pages/ModelCases';
import { decodeModelCaseBinding } from '../src/scoring/contracts';
import { createRiskView } from '../src/scoring/views';
import { decodeRun } from '../src/investigation/contracts';
import { createDatasetInvestigation } from '../src/investigation/api';
import { DETAIL_V2, LIST_V2 } from './dataset-fixture';

const canonical = 'ibm-hi-small:b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040:row:2980342';
const binding = { contract_version: 1, canonical_transaction_id: canonical,
  case_id: 'C157e60df5584c2cbbbac01aa0a6e2a60', transaction_id: 'D2adcb5bb7f6b9a8e5aa0dd4b0238c6dd',
  case_digest: '157e60df5584c2cbbbac01aa0a6e2a60258cc6e3e1a74cc1983f420659fe39e3',
  transaction_digest: '2adcb5bb7f6b9a8e5aa0dd4b0238c6dd54e44ca1e1c6f4ff1e763d96c7207e29',
  snapshot_ref: 'run_model_bridge_example', dataset_version: 'dv_' + 'a'.repeat(64),
  model_sha256: '3b4e4019312d60610dd0094c6697897a061611a60e7777ed7be35e133af9451c',
  feature_version: 'hi-small-temporal-v1', feature_manifest_sha256: '63873b79a1ff875c5702a62c40c7a9cb3faef6bb7e0bb658739abac35274c05f',
  source_sha256: canonical.split(':')[1], threshold: 0.2489517623052024, risk_score: 0.5,
  review_status: 'review_recommended', event_time_utc: '2022-09-06T12:00:00Z', assessed_at_utc: '2026-11-22T12:00:00Z' };

it('accepts closed published binding and refuses below-threshold or private fields', () => {
  expect(decodeModelCaseBinding(binding).case_id).toBe(binding.case_id);
  expect(() => decodeModelCaseBinding({ ...binding, risk_score: 0.1 })).toThrow();
  expect(() => decodeModelCaseBinding({ ...binding, is_laundering: 1 })).toThrow();
  expect(() => decodeModelCaseBinding({ ...binding, case_id: 'CASE-001' })).toThrow();
});

it('links only a review-recommended model result to the published case route', () => {
  const root = document.createElement('div');
  const view = createRiskView(root, () => {});
  const result = { transaction_id: canonical, risk_score: 0.5, review_status: 'review_recommended' as const,
    source: 'model' as const, model_version: 'lightgbm-3b4e4019312d', feature_version: 'hi-small-temporal-v1',
    synthetic_data: true as const, scored_at: '2022-09-06T12:00:00Z', explanation: 'Observed facts.' };
  view.render({ kind: 'success', result });
  expect(root.querySelector('a')?.getAttribute('href')).toContain('/model-cases?transaction=');
  view.render({ kind: 'success', result: { ...result, review_status: 'below_threshold' } });
  expect(root.querySelector('a')).toBeNull();
});

it('opens a typed published case with a dataset investigation panel', async () => {
  const container = document.createElement('div'); document.body.append(container);
  const root = createRoot(container);
  const list = decodeCaseListV2(LIST_V2), detail = decodeCaseDetailV2(DETAIL_V2);
  const getCase = vi.fn(async () => detail);
  await act(async () => { root.render(<CasesPage dataset initialCase={detail.case_id}
    client={{ getCases: async () => list, getCase }} />); });
  expect(getCase).toHaveBeenCalledWith(detail.case_id, expect.objectContaining({ snapshot: list.snapshot_ref }));
  expect(container.textContent).toContain('Prikaži AI istragu');
  expect(container.textContent).toContain('1250.000');
  await act(async () => { root.unmount(); }); container.remove();
});

it('accepts only the published C identity and sends an explicit dataset investigation request', async () => {
  const run = JSON.parse(readFileSync('../specs/003-ai-investigation/contracts/examples/run-ready.json', 'utf8'));
  run.case_id = binding.case_id;
  run.source_mode = 'dataset';
  run.snapshot_ref = binding.snapshot_ref;
  expect(decodeRun(run).case_id).toBe(binding.case_id);
  expect(() => decodeRun({ ...run, case_id: 'C' + 'g'.repeat(32) })).toThrow();
  const fetcher = vi.fn().mockResolvedValue(new Response(JSON.stringify(run), { status: 202, headers: { 'content-type': 'application/json' } }));
  vi.stubGlobal('fetch', fetcher);
  await createDatasetInvestigation(binding.case_id, binding.snapshot_ref, run.context_revision, 'test-key');
  expect(JSON.parse(fetcher.mock.calls[0][1].body).source_mode).toBe('dataset');
  vi.unstubAllGlobals();
});

it('shows a controlled unavailable state for a malformed published binding', async () => {
  const fetcher = vi.fn().mockResolvedValue(new Response(JSON.stringify({ unexpected: 'private' }), {
    status: 200, headers: { 'content-type': 'application/json' },
  }));
  vi.stubGlobal('fetch', fetcher);
  const container = document.createElement('div'); document.body.append(container);
  const root = createRoot(container);
  await act(async () => {
    root.render(<MemoryRouter initialEntries={['/model-cases?transaction=' + encodeURIComponent(canonical)]}>
      <ModelCasesPage />
    </MemoryRouter>);
  });
  await act(async () => { await Promise.resolve(); });
  expect(container.textContent).toContain('Objavljeni modelski slučaj nije dostupan.');
  expect(container.textContent).not.toContain('Invalid scoring response');
  expect(container.textContent).not.toContain('Sintetički slučajevi');
  await act(async () => { root.unmount(); }); container.remove(); vi.unstubAllGlobals();
});
