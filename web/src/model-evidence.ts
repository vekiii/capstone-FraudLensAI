// Approved aggregate-only presentation values. See evidence/dataset-model-page-source-audit.md.
export const modelEvidence = {
  sourceSha: 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040',
  modelSha: '3b4e4019312d60610dd0094c6697897a061611a60e7777ed7be35e133af9451c',
  reportSha: '5027dae9354796718a080086a6cadc0319d1b376336ad4dac8d93b4e534d9cdb',
  threshold: 0.2489517623052024,
  scoreableDevelopment: 1884981,
  partitions: [
    { name: 'Train', period: '02–04 Sep 2022 UTC', rows: 1169261, positive: 1206, negative: 1168055 },
    { name: 'Validation', period: '05 Sep 2022 UTC', rows: 482650, positive: 471, negative: 482179 },
    { name: 'Test', period: '06 Sep 2022, 00:00–11:12 UTC', rows: 233070, positive: 218, negative: 232852 },
  ],
  results: [
    { name: 'Validation', rows: 482650, positive: 471, negative: 482179, alerts: 229,
      tp: 107, fp: 122, tn: 482057, fn: 364, precision: 0.4672489082969432,
      recall: 0.22717622080679406, f1: 0.3057142857142857,
      ap: 0.2166607046990379, rocAuc: 0.9662388881499545,
      brier: 0.000846056224071008, topK: [[17, 20], [38, 50], [65, 100]] },
    { name: 'Test', rows: 233070, positive: 218, negative: 232852, alerts: 65,
      tp: 44, fp: 21, tn: 232831, fn: 174, precision: 0.676923076923077,
      recall: 0.2018348623853211, f1: 0.31095406360424027,
      ap: 0.2745021334479726, rocAuc: 0.9761554451171647,
      brier: 0.0007701183332511783, topK: [[18, 20], [38, 50], [52, 100]] },
  ],
} as const;

export const modelFeatures = [
  ['sender_out_count_24h', 'Earlier outgoing sender events'],
  ['sender_distinct_receivers_24h', 'Distinct bank-qualified receivers'],
  ['sender_paid_count_same_currency_24h', 'Earlier outgoing payments in the current paid currency'],
  ['sender_paid_sum_same_currency_24h', 'Exact sum of those earlier paid amounts'],
  ['receiver_in_count_24h', 'Earlier incoming receiver events'],
  ['receiver_distinct_senders_24h', 'Distinct bank-qualified senders'],
  ['receiver_received_count_same_currency_24h', 'Earlier receipts in the current received currency'],
  ['receiver_received_sum_same_currency_24h', 'Exact sum of those earlier received amounts'],
  ['current_amount_paid_log1p', 'Log(1 + current paid amount)'],
  ['current_payment_currency', 'Current source payment currency'],
  ['current_payment_format', 'Current payment format'],
] as const;
