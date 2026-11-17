import { describe, expect, it } from 'vitest';
import {
  ContractValidationError, decodeErrorEnvelope, decodeHealth, decodeRiskAssessment,
  decodeTransaction,
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
