export const DETAIL_V2 = {
  contract_version: 2, snapshot_ref: 'run_test_1',
  dataset_version: `dv_${'a'.repeat(64)}`, case_id: `C${'1'.repeat(32)}`,
  transaction: {
    transaction_id: `D${'1'.repeat(32)}`, event_time_utc: '2022-09-10T10:00:00Z',
    event_time_raw: '2022/09/10 10:00',
    time_basis: 'assumed_utc_for_synthetic_benchmark',
    sender: { bank: 'Bank A', account: '001' },
    receiver: { bank: 'Bank B', account: '002' },
    paid: { amount: '1250.000', currency: 'Australian Dollar' },
    received: { amount: '1250.000', currency: 'US Dollar' },
    payment_format: 'ACH',
  },
  risk_assessment: {
    transaction_id: `D${'1'.repeat(32)}`, run_id: 'run_test_1',
    dataset_version: `dv_${'a'.repeat(64)}`, score: 0.65,
    score_kind: 'ordinal_rule_score', score_source: 'rules',
    scorer_version: 'rules-v1', feature_version: 'history-v1',
    event_time_utc: '2022-09-10T10:00:00Z',
    history_cutoff_exclusive_at: '2022-09-10T10:00:00Z',
    scored_at: '2026-11-14T13:00:00Z',
    history_coverage: { state: 'full', start: '2022-09-01T00:00:00Z' },
    explanation: {
      status: 'available', method: 'rules', explained_scale: 'risk_score',
      feature_snapshot_digest: 'b'.repeat(64), partial: false,
      base_value: 0.65, remainder: 0, items: [],
    },
  },
};

export const LIST_V2 = {
  contract_version: 2, snapshot_ref: 'run_test_1',
  dataset_version: `dv_${'a'.repeat(64)}`, data_source: 'ibm_aml_hi_small',
  score_source: 'rules', scorer_version: 'rules-v1', total_alerts: 1,
  displayed_count: 1, truncated: false,
  selected_time_range: { from: '2022-09-10T10:00:00Z', to: '2022-09-10T10:00:00Z' },
  items: [{ case_id: `C${'1'.repeat(32)}`, transaction_id: `D${'1'.repeat(32)}`,
    event_time: '2022-09-10T10:00:00Z', score: 0.65,
    score_kind: 'ordinal_rule_score', score_source: 'rules' }],
};
