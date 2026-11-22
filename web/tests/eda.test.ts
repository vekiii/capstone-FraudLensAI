import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ApiError, getEdaSummary } from '../src/scoring/api';
import { ContractValidationError } from '../src/contracts';
import { decodeEdaSummary } from '../src/scoring/contracts';

const source = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040';
const summary = {
  dataset_version: 'ibm-hi-small-b19d39f5', source_sha256: source, synthetic_data: true,
  coverage_start_utc: '2022-09-01T00:00:00Z', coverage_end_utc: '2022-09-18T16:18:00Z',
  source_count: 2, accepted_count: 2, rejected_count: 0, warmup_count: 1,
  scoreable_count: 1, quality_counts: {}, omitted_amount_currencies: { paid: 0, received: 0 },
  series: [
    { series_id: 'sender_bank_count', label: 'Sender bank', unit: 'transactions',
      bucket_labels: ['Bank <script>'], values: [2], denominator: 2,
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
};

const fetchMock = vi.fn<typeof fetch>();
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { 'content-type': 'application/json' },
});
beforeEach(() => { fetchMock.mockReset(); vi.stubGlobal('fetch', fetchMock); });
afterEach(() => { vi.unstubAllGlobals(); document.body.replaceChildren(); });

describe('Feature 002 EDA v1 decoder', () => {
  it('accepts the bounded closed aggregate without changing values', () => {
    expect(decodeEdaSummary(summary)).toEqual(summary);
  });

  it.each([
    { ...summary, contract_version: 'v2' },
    { ...summary, is_laundering: true },
    { ...summary, synthetic_data: false },
    { ...summary, source_count: 3 },
    { ...summary, warmup_count: 2 },
    { ...summary, source_sha256: 'bad' },
    { ...summary, accepted_count: -1 },
    { ...summary, scoreable_count: Number.POSITIVE_INFINITY },
    { ...summary, coverage_end_utc: null },
    { ...summary, quality_counts: { positive_count: 1 } },
    { ...summary, series: [{ ...summary.series[0], values: [1, 1] }] },
    { ...summary, series: [{ ...summary.series[0], values: [NaN] }] },
    { ...summary, series: [{ ...summary.series[0], values: [-1] }] },
    { ...summary, series: [{ ...summary.series[2], currency: null }] },
    { ...summary, series: [{ ...summary.series[2], side: 'received' }] },
    { ...summary, series: [{ ...summary.series[0], timezone: 'Europe/Belgrade' }] },
    { ...summary, series: [{ ...summary.series[0], unit: 'ratio' }] },
    { ...summary, series: [{ ...summary.series[0], bucket_labels: Array(367).fill('x'),
      values: Array(367).fill(1) }] },
    { ...summary, series: Array(31).fill(summary.series[0]) },
  ])('rejects malformed, label-bearing or incompatible aggregates', value => {
    expect(() => decodeEdaSummary(value)).toThrow(ContractValidationError);
  });

  it('accepts an explicit empty aggregate with no invented values', () => {
    const empty = { ...summary, source_count: 0, accepted_count: 0, warmup_count: 0,
      scoreable_count: 0, coverage_start_utc: null, coverage_end_utc: null, series: [] };
    expect(decodeEdaSummary(empty)).toEqual(empty);
  });
});

describe('Feature 002 EDA API', () => {
  it('requests only the bounded summary URL and validates the body', async () => {
    fetchMock.mockResolvedValueOnce(json(summary));
    expect(await getEdaSummary()).toEqual(summary);
    expect(fetchMock.mock.calls[0][0]).toBe('/api/eda/summary');
  });

  it('maps unavailable and rejects malformed bodies without exposing server text', async () => {
    fetchMock.mockResolvedValueOnce(json({ error: {
      code: 'dataset_unavailable', message: '/private/secret/path',
    } }, 404));
    await expect(getEdaSummary()).rejects.toMatchObject({ code: 'dataset_unavailable' });
    fetchMock.mockResolvedValueOnce(json({ ...summary, target: 1 }));
    await expect(getEdaSummary()).rejects.toMatchObject({ code: 'invalid_response' });
    expect(new ApiError('dataset_unavailable').message).not.toContain('/private');
  });
});

export { summary };
