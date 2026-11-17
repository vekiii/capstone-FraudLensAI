import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { getOverview, ApiError } from '../src/api';
import type { Overview } from '../src/contracts';

const body: Overview = {
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

const fetchMock = vi.fn<typeof fetch>();
function json(value: unknown, status = 200): Response {
  return new Response(JSON.stringify(value), {
    status, headers: { 'content-type': 'application/json' },
  });
}
beforeEach(() => { fetchMock.mockReset(); vi.stubGlobal('fetch', fetchMock); });
afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks(); });

it('decodes the aggregate endpoint and keeps a relative API URL', async () => {
  fetchMock.mockResolvedValueOnce(json(body));
  expect(await getOverview()).toEqual(body);
  expect(fetchMock.mock.calls[0][0]).toBe('/api/overview');
});

it('rejects fabricated numeric metrics and maps unavailable API responses', async () => {
  fetchMock.mockResolvedValueOnce(json({ ...body, model: { ...body.model, f1: 0.99 } }));
  await expect(getOverview()).rejects.toMatchObject({ code: 'invalid_response' });
  fetchMock.mockResolvedValueOnce(json({ error: {
    code: 'run_unavailable', message: 'private detail',
  } }, 503));
  await expect(getOverview()).rejects.toMatchObject({ code: 'run_unavailable', status: 503 });
  fetchMock.mockRejectedValueOnce(new TypeError('offline'));
  await expect(getOverview()).rejects.toBeInstanceOf(ApiError);
});
