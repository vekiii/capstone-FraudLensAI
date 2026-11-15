import { afterEach, expect, it, vi } from 'vitest';
import { ApiError } from '../src/api';
import { mountFraudLensApp } from '../src/main';
import type { Overview } from '../src/contracts';

const overview: Overview = {
  contract_version: 1,
  dataset: {
    data_source: 'ibm_aml_hi_small', dataset_version: 'dv_' + 'a'.repeat(64),
    run_id: 'run_overview', scored_transactions: 3, unknown_timestamp_transactions: 0,
    confirmed_fraud: null, legitimate: null, fraud_rate: null,
    label_unavailable_reason: 'Ground-truth labels are not available to the serving API.',
  },
  predictions: { flagged: 2, not_flagged: 1, flag_rate: 2 / 3 },
  series: [{ period: '2022-09-10', transactions: 3, flagged: 2, not_flagged: 1 }],
  aggregation: 'day',
  model: {
    name: 'Rule-based scorer', source: 'rules', scorer_version: 'rules-v1',
    threshold: '0.5', evaluation_dataset: null, evaluation_split: null,
    precision: null, recall: null, f1: null,
    metric_source: 'Unavailable because this active run has no ground-truth labels.',
  },
};

let dispose: (() => void) | undefined;
afterEach(() => { dispose?.(); dispose = undefined; document.body.replaceChildren(); });

it('shows four trustworthy KPIs, prediction chart, model provenance and navigation', async () => {
  const root = document.createElement('main');
  document.body.append(root);
  dispose = mountFraudLensApp(root, { getOverview: async () => overview });
  await vi.waitFor(() => expect(root.querySelector('.overview-dashboard')).not.toBeNull());
  expect(root.querySelectorAll('.kpi-grid > .kpi-card')).toHaveLength(4);
  expect(root.textContent).toContain('3');
  expect(root.textContent).toContain('N/A');
  expect(root.textContent).toContain('Model flagged');
  expect(root.textContent).toContain('Not flagged');
  expect(root.textContent).toContain('no ground-truth labels');
  expect(root.querySelector('svg[role="img"]')).not.toBeNull();
  expect(root.querySelector('[aria-label="Primary navigation"]')).not.toBeNull();
  root.querySelector<HTMLButtonElement>('[data-page="cases"]')!.click();
  await vi.waitFor(() => expect(root.querySelector('.case-navigation')).not.toBeNull());
  root.querySelector<HTMLButtonElement>('[data-page="overview"]')!.click();
  await vi.waitFor(() => expect(root.querySelector('.overview-dashboard')).not.toBeNull());
});

it('shows loading, empty and API error states without crashing', async () => {
  const root = document.createElement('main');
  document.body.append(root);
  let fail = true;
  dispose = mountFraudLensApp(root, { getOverview: async () => {
    if (fail) throw new ApiError('run_unavailable', 503);
    return { ...overview, dataset: { ...overview.dataset, scored_transactions: 0 },
      predictions: { flagged: 0, not_flagged: 0, flag_rate: null }, series: [] };
  } });
  await vi.waitFor(() => expect(root.textContent).toContain('No active dataset or model run'));
  fail = false;
  root.querySelector<HTMLButtonElement>('[data-action="retry-overview"]')!.click();
  await vi.waitFor(() => expect(root.textContent).toContain('No transactions were scored'));
  expect(root.querySelectorAll('.kpi-grid > .kpi-card')).toHaveLength(4);
});

it('announces loading while the aggregate request is pending', async () => {
  const root = document.createElement('main');
  document.body.append(root);
  let resolve!: (value: Overview) => void;
  const pending = new Promise<Overview>(yes => { resolve = yes; });
  dispose = mountFraudLensApp(root, { getOverview: async () => pending });
  expect(root.querySelector('.page-content')?.getAttribute('aria-busy')).toBe('true');
  expect(root.querySelector('[role="status"]')?.textContent).toContain('Loading');
  resolve(overview);
  await vi.waitFor(() => expect(root.querySelector('.overview-dashboard')).not.toBeNull());
});
