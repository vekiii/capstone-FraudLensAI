import { describe, expect, it } from 'vitest';
import {
  ContractValidationError, decodeErrorEnvelope, decodeHealth, decodeRiskAssessment,
  decodeTransaction, decodePredictionResult, decodeModelResults, decodeRiskErrorEnvelope,
} from '../src/contracts';

const transaction = {
  transaction_id: 'TX-001', occurred_at: '2026-01-01T10:00:00Z',
  sender_account: 'DEMO-A:001', receiver_account: 'DEMO-B:002', amount: '0.00', currency: 'EUR',
};
const assessment = {
  transaction_id: 'TX-001', score: 0.75, source: 'fixture', scorer_version: 'fixture-v1',
  scored_at: '2026-01-01T10:00:00Z', explanation: 'Illustrative synthetic score.',
};

function without(value: Record<string, unknown>, field: string): unknown {
  const copy = { ...value };
  delete copy[field];
  return copy;
}

describe('canonical nested contracts and calendar boundaries', () => {
  it.each(Object.keys(transaction))('requires nested transaction field %s', field => {
    expect(() => decodeTransaction(without(transaction, field))).toThrow(ContractValidationError);
  });

  it.each(Object.keys(assessment))('requires nested assessment field %s', field => {
    expect(() => decodeRiskAssessment(without(assessment, field))).toThrow(ContractValidationError);
  });

  it.each([
    '0001-01-01T00:00:00Z', '2000-02-29T23:59:59.123456Z', '2024-02-29t00:00:00Z',
  ])('accepts valid RFC3339 UTC timestamp %s', occurred_at => {
    expect(decodeTransaction({ ...transaction, occurred_at }).occurred_at).toBe(occurred_at);
  });

  it.each([
    '0000-01-01T00:00:00Z', '1900-02-29T00:00:00Z', '2026-04-31T00:00:00Z',
    '2026-00-01T00:00:00Z', '2026-01-00T00:00:00Z', '2026-01-01T24:00:00Z',
    '2026-01-01T00:60:00Z', '2026-01-01T00:00:60Z', '2026-01-01T00:00:00Z\n',
    '2026-01-01T00:00:00z',
  ])('rejects invalid UTC calendar/time %s', occurred_at => {
    expect(() => decodeTransaction({ ...transaction, occurred_at })).toThrow(ContractValidationError);
  });

  it('uses Unicode code point limits without truncating account names or explanations', () => {
    const sender_account = '🧪'.repeat(120);
    const explanation = '🧪'.repeat(500);
    expect(decodeTransaction({ ...transaction, sender_account }).sender_account).toBe(sender_account);
    expect(decodeRiskAssessment({ ...assessment, explanation }).explanation).toBe(explanation);
    expect(() => decodeTransaction({ ...transaction, sender_account: `${sender_account}x` }))
      .toThrow(ContractValidationError);
    expect(() => decodeRiskAssessment({ ...assessment, explanation: `${explanation}x` }))
      .toThrow(ContractValidationError);
  });

  it('validates the canonical health response', () => {
    expect(decodeHealth({ status: 'ok', mode: 'fixture' })).toEqual({ status: 'ok', mode: 'fixture' });
    for (const body of [{ status: 'ok' }, { status: 'ok', mode: 'model' },
      { status: 'ok', mode: 'fixture', extra: true }]) {
      expect(() => decodeHealth(body)).toThrow(ContractValidationError);
    }
  });

  it.each([
    {}, { error: null }, { error: { code: 'internal_error' } },
    { error: { code: 'internal_error', message: null } },
    { error: { code: 'internal_error', message: 'x'.repeat(201) } },
  ])('rejects incomplete or invalid error envelopes %j', body => {
    expect(() => decodeErrorEnvelope(body)).toThrow(ContractValidationError);
  });
});

const canonicalId = `ibm-hi-small:${'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'}:row:12345`;
const prediction = {
  transaction_id: canonicalId, risk_score: 0.2489517623052024,
  review_status: 'review_recommended', source: 'model',
  model_version: 'lightgbm-3b4e4019312d', feature_version: 'hi-small-temporal-v1',
  synthetic_data: true, scored_at: '2026-11-21T10:00:00Z',
  explanation: 'Observed amount: 125.00 USD.',
};
const results = {
  model_version: 'lightgbm-3b4e4019312d', feature_version: 'hi-small-temporal-v1',
  dataset_version: 'ibm-hi-small-b19d39f5', threshold: 0.2489517623052024,
  calibration_status: 'not_assessed', partitions: [{ partition: 'validation',
    state: 'available', synthetic_data: true, coverage_utc: '2022-09-05 UTC',
    row_count: 100, positive_count: 1, negative_count: 99,
    metrics: [{ name: 'Average Precision', value: 0.2, denominator: 100, unit: 'ratio' }] }],
  limitations: ['Synthetic data; local capstone only.'],
};

describe('Feature 002 v1 closed decoders', () => {
  it('accepts a complete prediction and aggregate results without altering values', () => {
    expect(decodePredictionResult(prediction)).toEqual(prediction);
    expect(decodeModelResults(results)).toEqual(results);
  });

  it.each(Object.keys(prediction))('rejects missing prediction field %s', field => {
    expect(() => decodePredictionResult(without(prediction, field))).toThrow(ContractValidationError);
  });

  it.each(Object.keys(results))('rejects missing aggregate field %s', field => {
    expect(() => decodeModelResults(without(results, field))).toThrow(ContractValidationError);
  });

  it.each([
    ['transaction_id', 'TX-001'], ['transaction_id', `${canonicalId}\n`],
    ['risk_score', -0.1], ['risk_score', 1.1], ['risk_score', NaN],
    ['risk_score', Infinity], ['risk_score', -Infinity], ['risk_score', '0.5'],
    ['review_status', 'approved'], ['source', 'fixture'],
    ['model_version', ''], ['feature_version', 'x'.repeat(81)],
    ['synthetic_data', false], ['scored_at', '2026-02-30T00:00:00Z'],
    ['explanation', ''], ['explanation', 'x'.repeat(1001)],
  ] as const)('rejects invalid prediction %s=%s', (field, value) => {
    expect(() => decodePredictionResult({ ...prediction, [field]: value }))
      .toThrow(ContractValidationError);
  });

  it('rejects unknown versions, extra fields and record-level labels', () => {
    expect(() => decodePredictionResult({ ...prediction, contract_version: 'v2' }))
      .toThrow(ContractValidationError);
    expect(() => decodePredictionResult({ ...prediction, is_laundering: 1 }))
      .toThrow(ContractValidationError);
    expect(() => decodeModelResults({ ...results, target_label: 1 }))
      .toThrow(ContractValidationError);
  });

  it('rejects malformed aggregate metrics and unauthorized metric leakage', () => {
    expect(() => decodeModelResults({ ...results, partitions: null })).toThrow(ContractValidationError);
    expect(() => decodeModelResults({ ...results, calibration_status: 'calibrated' }))
      .toThrow(ContractValidationError);
    expect(() => decodeModelResults({ ...results, partitions: [{
      ...results.partitions[0], metrics: [{ ...results.partitions[0].metrics[0], denominator: -1 }],
    }] })).toThrow(ContractValidationError);
    expect(() => decodeModelResults({ ...results, partitions: [{
      ...results.partitions[0], state: 'not_authorized',
    }] })).toThrow(ContractValidationError);
    for (const value of [NaN, Infinity, -Infinity]) {
      expect(() => decodeModelResults({ ...results, threshold: value }))
        .toThrow(ContractValidationError);
      expect(() => decodeModelResults({ ...results, partitions: [{
        ...results.partitions[0], metrics: [{ ...results.partitions[0].metrics[0], value }],
      }] })).toThrow(ContractValidationError);
    }
  });

  it('decodes controlled Feature 002 errors and rejects unknown codes', () => {
    expect(decodeRiskErrorEnvelope({ error: { code: 'model_unavailable', message: 'Unavailable.' } }))
      .toEqual({ error: { code: 'model_unavailable', message: 'Unavailable.' } });
    expect(() => decodeRiskErrorEnvelope({ error: { code: 'new_error', message: 'x' } }))
      .toThrow(ContractValidationError);
  });
});
