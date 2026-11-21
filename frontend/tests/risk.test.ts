import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ApiError, getModelResults, getTransactionRisk } from '../src/api';
import { createModelResultsView, createRiskView, modelResultsContent } from '../src/views';
import { decodeModelResults } from '../src/contracts';

const id = `ibm-hi-small:${'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'}:row:12345`;
const result = {
  transaction_id: id, risk_score: 0.2489517623052024,
  review_status: 'review_recommended', source: 'model',
  model_version: 'lightgbm-3b4e4019312d', feature_version: 'hi-small-temporal-v1',
  synthetic_data: true, scored_at: '2026-11-21T10:00:00Z',
  explanation: 'Observed amount: <img src=x onerror=alert(1)> USD; sender count: 2.',
};
const fetchMock = vi.fn<typeof fetch>();
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { 'content-type': 'application/json' },
});

beforeEach(() => { fetchMock.mockReset(); vi.stubGlobal('fetch', fetchMock); });
afterEach(() => { vi.unstubAllGlobals(); document.body.replaceChildren(); });

describe('Feature 002 risk API', () => {
  it('uses the canonical identity and preserves the exact returned score', async () => {
    fetchMock.mockResolvedValueOnce(json(result));
    expect(await getTransactionRisk(id)).toEqual(result);
    expect(fetchMock.mock.calls[0][0]).toBe(`/api/transactions/${encodeURIComponent(id)}/risk`);
  });

  it.each([
    [404, 'transaction_not_found'], [409, 'transaction_ineligible'],
    [503, 'model_unavailable'], [422, 'invalid_request'],
  ] as const)('maps controlled %i %s without exposing server text', async (status, code) => {
    fetchMock.mockResolvedValueOnce(json({ error: { code, message: '<script>PRIVATE</script>' } }, status));
    await expect(getTransactionRisk(id)).rejects.toMatchObject({ code, status });
  });

  it('rejects identity mismatch, label leakage, invalid score and incompatible error code', async () => {
    for (const body of [
      { ...result, transaction_id: id.replace('12345', '12346') },
      { ...result, is_laundering: 1 }, { ...result, risk_score: 2 },
    ]) {
      fetchMock.mockResolvedValueOnce(json(body));
      await expect(getTransactionRisk(id)).rejects.toMatchObject({ code: 'invalid_response' });
    }
    fetchMock.mockResolvedValueOnce(json({ error: { code: 'case_not_found', message: 'x' } }, 404));
    await expect(getTransactionRisk(id)).rejects.toMatchObject({ code: 'invalid_response' });
  });

  it('rejects fixture IDs before any request', () => {
    expect(() => getTransactionRisk('TX-001')).toThrow();
    expect(fetchMock).not.toHaveBeenCalled();
  });
});

describe('Feature 002 risk view', () => {
  it('shows loading, safe score/provenance/explanation and no target label', () => {
    const root = document.createElement('main');
    document.body.append(root);
    const view = createRiskView(root, () => {});
    view.render({ kind: 'loading' });
    expect(root.getAttribute('aria-busy')).toBeNull();
    expect(root.textContent).toMatch(/Učitavanje model procene/);
    view.render({ kind: 'success', result: resultValue() });
    expect(root.textContent).toContain(String(result.risk_score));
    expect(root.textContent).toContain('Preporučen ljudski pregled');
    expect(root.textContent).toContain('Sintetički podaci');
    expect(root.textContent).toContain(result.model_version);
    expect(root.textContent).toContain(result.feature_version);
    expect(root.textContent).toContain(id.split(':')[1]);
    expect(root.textContent).toContain(result.explanation);
    expect(root.querySelector('img')).toBeNull();
    expect(root.textContent).not.toMatch(/is_laundering|target_label|SHAP/);
  });

  it('shows an error and retry control', () => {
    const root = document.createElement('main');
    document.body.append(root);
    const view = createRiskView(root, () => {});
    view.render({ kind: 'error', message: new ApiError('model_unavailable').message });
    expect(root.querySelector('[role="alert"]')?.textContent).toMatch(/dostupna/);
    expect([...root.querySelectorAll('button')].some(button => /ponovo/.test(button.textContent ?? '')))
      .toBe(true);
  });
});

it('renders only supplied aggregate metrics with partition, denominator and limits', () => {
  const decoded = decodeModelResults({
    model_version: 'lightgbm-v1', feature_version: 'features-v1', dataset_version: 'source-v1',
    threshold: 0.2489517623052024, calibration_status: 'not_assessed',
    partitions: [{ partition: 'validation', state: 'available', synthetic_data: true,
      coverage_utc: '2022-09-05 UTC', row_count: 482650,
      positive_count: 471, negative_count: 482179,
      metrics: [{ name: 'Average Precision', value: 0.2, denominator: 482650, unit: 'ratio' }] },
    { partition: 'test', state: 'not_authorized', synthetic_data: true,
      coverage_utc: '2022-09-06 UTC', row_count: 0, positive_count: 0,
      negative_count: 0, metrics: [] }],
    limitations: ['Local capstone only; <unsafe>'],
  });
  const node = modelResultsContent(decoded);
  expect(node.textContent).toContain('validation');
  expect(node.textContent).toContain('2022-09-05 UTC');
  expect(node.textContent).toContain('482650');
  expect(node.textContent).toContain('471');
  expect(node.textContent).toContain('482179');
  expect(node.textContent).toContain('imenilac 482650');
  expect(node.textContent).toContain('Nije procenjena');
  expect(node.textContent).toContain('Evaluacija nije odobrena');
  expect(node.textContent).toContain('<unsafe>');
  expect(node.querySelector('unsafe')).toBeNull();
});

const aggregate = {
  model_version: 'lightgbm-3b4e4019312d', feature_version: 'hi-small-temporal-v1',
  dataset_version: 'ibm-hi-small-sha256:b19d39f5', threshold: 0.2489517623052024,
  calibration_status: 'not_assessed',
  partitions: [{ partition: 'validation', state: 'available', synthetic_data: true,
    coverage_utc: '2022-09-05 UTC', row_count: 100, positive_count: 1,
    negative_count: 99, metrics: [{ name: 'Whole-partition P@20', value: 0.5,
      denominator: 20, unit: 'ratio' }] }],
  limitations: ['Synthetic local result.'],
};

describe('live aggregate results boundary', () => {
  it('loads and decodes the real results URL without a query filter', async () => {
    fetchMock.mockResolvedValueOnce(json(aggregate));
    expect(await getModelResults()).toEqual(aggregate);
    expect(fetchMock.mock.calls[0][0]).toBe('/api/model/results');
  });

  it.each([[404, 'results_unavailable'], [409, 'evaluation_not_authorized']] as const)(
    'maps %i %s to a controlled state', async (status, code) => {
      fetchMock.mockResolvedValueOnce(json({ error: { code, message: 'PRIVATE PATH' } }, status));
      await expect(getModelResults()).rejects.toMatchObject({ code, status });
    },
  );

  it('rejects label leakage and malformed counts', async () => {
    for (const body of [{ ...aggregate, is_laundering: 1 },
      { ...aggregate, partitions: [{ ...aggregate.partitions[0], positive_count: 2 }] }]) {
      fetchMock.mockResolvedValueOnce(json(body));
      await expect(getModelResults()).rejects.toMatchObject({ code: 'invalid_response' });
    }
  });

  it('shows loading, unavailable, unauthorized and retry without invented metrics', () => {
    const root = document.createElement('main');
    document.body.append(root);
    const view = createModelResultsView(root, () => {});
    view.render({ kind: 'idle' });
    expect(root.textContent).not.toContain('Whole-partition P@20');
    view.render({ kind: 'loading' });
    expect(root.textContent).toContain('Učitavanje agregatnih rezultata');
    view.render({ kind: 'unavailable' });
    expect(root.querySelector('[role="alert"]')?.textContent).toContain('nisu dostupni');
    expect(root.textContent).not.toContain('Whole-partition P@20');
    view.render({ kind: 'unauthorized' });
    expect(root.querySelector('[role="alert"]')?.textContent).toContain('nije odobrena');
    view.render({ kind: 'error', message: new ApiError('network_error').message });
    expect(root.querySelector('[role="alert"]')?.textContent).toContain('Povezivanje');
    expect([...root.querySelectorAll('button')].some(button => /ponovo/.test(button.textContent ?? '')))
      .toBe(true);
  });
});

function resultValue() {
  return { ...result, review_status: 'review_recommended' as const, source: 'model' as const,
    synthetic_data: true as const };
}
