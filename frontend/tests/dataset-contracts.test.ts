import { expect, it } from 'vitest';
import { decodeCaseDetailResponse, decodeCaseListResponse } from '../src/contracts';
import { DETAIL_V2, LIST_V2 } from './dataset-fixture';

it('decodes closed v2 list and detail by response discriminator', () => {
  expect(decodeCaseListResponse(LIST_V2)).toEqual(LIST_V2);
  expect(decodeCaseDetailResponse(DETAIL_V2)).toEqual(DETAIL_V2);
});

it('decodes boosted probability explanation without changing snapshot identity', () => {
  const assessment = DETAIL_V2.risk_assessment;
  const explanation = assessment.explanation;
  if (explanation.status !== 'available') throw new Error('fixture explanation unavailable');
  const boosted = {
    ...DETAIL_V2,
    risk_assessment: {
      ...assessment,
      score_source: 'model', score_kind: 'uncalibrated_probability_estimate',
      scorer_version: 'model-history-v1-boosted-candidate',
      explanation: { ...explanation, method: 'boosted_sequential_probability',
        explained_scale: 'positive_class_estimate', base_value: assessment.score,
        remainder: 0, items: [] },
    },
  };
  expect(decodeCaseDetailResponse(boosted)).toMatchObject({ risk_assessment: {
    explanation: { status: 'available', method: 'boosted_sequential_probability' },
  } });
});

it.each([
  { ...LIST_V2, extra: 1 },
  { ...LIST_V2, displayed_count: 2 },
  { ...LIST_V2, snapshot_ref: 'run_test_1\n' },
  { ...LIST_V2, score_source: 'model' },
  { ...LIST_V2, selected_time_range: { from: null, to: null } },
])('rejects invalid list or semantic count/source %j', payload => {
  expect(() => decodeCaseListResponse(payload)).toThrow();
});

it.each([
  { ...DETAIL_V2, label: 1 },
  { ...DETAIL_V2, transaction: { ...DETAIL_V2.transaction,
    event_time_utc: '2022-02-30T10:00:00Z' } },
  { ...DETAIL_V2, transaction: { ...DETAIL_V2.transaction,
    paid: { amount: '1250.000\n', currency: 'Australian Dollar' } } },
  { ...DETAIL_V2, risk_assessment: { ...DETAIL_V2.risk_assessment, run_id: 'run_other' } },
  { ...DETAIL_V2, risk_assessment: { ...DETAIL_V2.risk_assessment, score: Infinity } },
  { ...DETAIL_V2, risk_assessment: { ...DETAIL_V2.risk_assessment,
    explanation: { ...DETAIL_V2.risk_assessment.explanation, explained_scale: 'log_odds' } } },
])('rejects invalid detail or explanation %j', payload => {
  expect(() => decodeCaseDetailResponse(payload)).toThrow();
});
