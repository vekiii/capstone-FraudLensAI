import { boundedText, closedObject, invalid, isRecord, nonnegativeInteger, patternedText, score, text, timestamp } from '../contracts';

export type RiskErrorCode = 'invalid_request' | 'transaction_not_found' | 'transaction_ineligible'
  | 'model_unavailable' | 'results_unavailable' | 'evaluation_not_authorized'
  | 'dataset_unavailable' | 'internal_error';

export interface PredictionResult {
  transaction_id: string;
  risk_score: number;
  review_status: 'review_recommended' | 'below_threshold';
  source: 'model';
  model_version: string;
  feature_version: string;
  synthetic_data: true;
  scored_at: string;
  explanation: string;
}

export interface Metric {
  name: string;
  value: number | null;
  denominator: number;
  unit: string;
}

export interface PartitionResults {
  partition: 'train' | 'validation' | 'test';
  state: 'available' | 'not_authorized' | 'unavailable';
  synthetic_data: true;
  coverage_utc: string;
  row_count: number;
  positive_count: number;
  negative_count: number;
  metrics: Metric[];
}

export interface ModelResults {
  model_version: string;
  feature_version: string;
  dataset_version: string;
  threshold: number | null;
  calibration_status: 'not_assessed' | 'assessed';
  partitions: PartitionResults[];
  limitations: string[];
}

export interface RiskErrorEnvelope {
  error: { code: RiskErrorCode; message: string };
}

export interface EdaSeries {
  series_id: string;
  label: string;
  unit: 'transactions' | 'amount';
  bucket_labels: string[];
  values: number[];
  denominator: number;
  currency: string | null;
  side: 'paid' | 'received' | null;
  timezone: 'UTC' | null;
}

export interface EdaSummary {
  dataset_version: string;
  source_sha256: string;
  synthetic_data: true;
  coverage_start_utc: string | null;
  coverage_end_utc: string | null;
  source_count: number;
  accepted_count: number;
  rejected_count: number;
  warmup_count: number;
  scoreable_count: number;
  quality_counts: Record<string, number>;
  omitted_amount_currencies: { paid: number; received: number };
  series: EdaSeries[];
}

const canonicalIdPattern = /^ibm-hi-small:[0-9a-f]{64}:row:[1-9][0-9]*(?![\s\S])/;

export function decodeCanonicalTransactionId(value: unknown): string {
  const id = patternedText(value, canonicalIdPattern);
  return [...id].length <= 160 ? id : invalid();
}

export function decodeModelCaseBinding(value: unknown) {
  const v = closedObject(value, ['contract_version', 'canonical_transaction_id', 'case_id',
    'transaction_id', 'case_digest', 'transaction_digest', 'snapshot_ref', 'dataset_version',
    'model_sha256', 'feature_version', 'feature_manifest_sha256', 'source_sha256',
    'threshold', 'risk_score', 'review_status', 'event_time_utc', 'assessed_at_utc']);
  if (v.contract_version !== 1 || v.review_status !== 'review_recommended') invalid();
  const canonical_transaction_id = decodeCanonicalTransactionId(v.canonical_transaction_id);
  const case_id = patternedText(v.case_id, /^C[0-9a-f]{32}$/);
  const transaction_id = patternedText(v.transaction_id, /^D[0-9a-f]{32}$/);
  const case_digest = patternedText(v.case_digest, /^[0-9a-f]{64}$/);
  const transaction_digest = patternedText(v.transaction_digest, /^[0-9a-f]{64}$/);
  const source_sha256 = patternedText(v.source_sha256, /^[0-9a-f]{64}$/);
  const model_sha256 = patternedText(v.model_sha256, /^[0-9a-f]{64}$/);
  const feature_manifest_sha256 = patternedText(v.feature_manifest_sha256, /^[0-9a-f]{64}$/);
  const threshold = score(v.threshold), risk_score = score(v.risk_score);
  if (canonical_transaction_id.split(':')[1] !== source_sha256 || risk_score < threshold
      || case_id.slice(1) !== case_digest.slice(0, 32)
      || transaction_id.slice(1) !== transaction_digest.slice(0, 32)) invalid();
  return { contract_version: 1 as const, canonical_transaction_id, case_id, transaction_id,
    case_digest, transaction_digest, snapshot_ref: patternedText(v.snapshot_ref, /^run_[A-Za-z0-9_-]{1,64}$/),
    dataset_version: patternedText(v.dataset_version, /^dv_[0-9a-f]{64}$/), model_sha256,
    feature_version: boundedText(v.feature_version, 80), feature_manifest_sha256, source_sha256,
    threshold, risk_score, review_status: 'review_recommended' as const,
    event_time_utc: timestamp(v.event_time_utc), assessed_at_utc: timestamp(v.assessed_at_utc) };
}

export function decodePredictionResult(value: unknown): PredictionResult {
  const object = closedObject(value, [
    'transaction_id', 'risk_score', 'review_status', 'source', 'model_version',
    'feature_version', 'synthetic_data', 'scored_at', 'explanation',
  ]);
  if (object.review_status !== 'review_recommended' && object.review_status !== 'below_threshold') invalid();
  if (object.source !== 'model' || object.synthetic_data !== true) invalid();
  return {
    transaction_id: decodeCanonicalTransactionId(object.transaction_id),
    risk_score: score(object.risk_score), review_status: object.review_status,
    source: 'model', model_version: boundedText(object.model_version, 80),
    feature_version: boundedText(object.feature_version, 80), synthetic_data: true,
    scored_at: timestamp(object.scored_at), explanation: boundedText(object.explanation, 1000),
  };
}

function finiteOrNull(value: unknown): number | null {
  return value === null ? null : typeof value === 'number' && Number.isFinite(value) ? value : invalid();
}

function decodeMetric(value: unknown): Metric {
  const object = closedObject(value, ['name', 'value', 'denominator', 'unit']);
  return { name: boundedText(object.name, 80), value: finiteOrNull(object.value),
    denominator: nonnegativeInteger(object.denominator), unit: boundedText(object.unit, 40) };
}

function decodePartition(value: unknown): PartitionResults {
  const object = closedObject(value, [
    'partition', 'state', 'synthetic_data', 'coverage_utc', 'row_count',
    'positive_count', 'negative_count', 'metrics',
  ]);
  if (object.partition !== 'train' && object.partition !== 'validation' && object.partition !== 'test') invalid();
  if (object.state !== 'available' && object.state !== 'not_authorized' && object.state !== 'unavailable') invalid();
  if (object.synthetic_data !== true || !Array.isArray(object.metrics) || object.metrics.length > 40) invalid();
  if (object.state !== 'available' && object.metrics.length !== 0) invalid();
  const row_count = nonnegativeInteger(object.row_count);
  const positive_count = nonnegativeInteger(object.positive_count);
  const negative_count = nonnegativeInteger(object.negative_count);
  if (positive_count + negative_count !== row_count) invalid();
  return { partition: object.partition, state: object.state, synthetic_data: true,
    coverage_utc: boundedText(object.coverage_utc, 120),
    row_count, positive_count, negative_count,
    metrics: object.metrics.map(decodeMetric) };
}

export function decodeModelResults(value: unknown): ModelResults {
  const object = closedObject(value, [
    'model_version', 'feature_version', 'dataset_version', 'threshold',
    'calibration_status', 'partitions', 'limitations',
  ]);
  if (object.calibration_status !== 'not_assessed' && object.calibration_status !== 'assessed') invalid();
  if (!Array.isArray(object.partitions) || object.partitions.length > 3
    || !Array.isArray(object.limitations) || object.limitations.length > 20) invalid();
  const threshold = object.threshold === null ? null : score(object.threshold);
  const partitions = object.partitions.map(decodePartition);
  if (new Set(partitions.map(partition => partition.partition)).size !== partitions.length) invalid();
  return { model_version: boundedText(object.model_version, 80),
    feature_version: boundedText(object.feature_version, 80),
    dataset_version: boundedText(object.dataset_version, 120), threshold,
    calibration_status: object.calibration_status, partitions,
    limitations: object.limitations.map(item => {
      const result = text(item);
      return [...result].length <= 300 ? result : invalid();
    }) };
}

export function decodeRiskErrorEnvelope(value: unknown): RiskErrorEnvelope {
  const object = closedObject(value, ['error']);
  const error = closedObject(object.error, ['code', 'message']);
  const codes: readonly RiskErrorCode[] = [
    'invalid_request', 'transaction_not_found', 'transaction_ineligible',
    'model_unavailable', 'results_unavailable', 'evaluation_not_authorized',
    'dataset_unavailable', 'internal_error',
  ];
  const code = codes.find(item => item === error.code);
  if (code === undefined) invalid();
  return { error: { code, message: boundedText(error.message, 200) } };
}

const edaCountIds = new Set([
  'sender_bank_count', 'receiver_bank_count', 'payment_currency_count',
  'receiving_currency_count', 'payment_format_count', 'utc_transaction_count',
]);

function decodeEdaSeries(value: unknown): EdaSeries {
  const object = closedObject(value, [
    'series_id', 'label', 'unit', 'bucket_labels', 'values', 'denominator',
    'currency', 'side', 'timezone',
  ]);
  const series_id = boundedText(object.series_id, 80);
  const label = boundedText(object.label, 120);
  if (object.unit !== 'transactions' && object.unit !== 'amount') invalid();
  if (!Array.isArray(object.bucket_labels) || !Array.isArray(object.values)
    || object.bucket_labels.length > 366 || object.values.length > 366
    || object.bucket_labels.length !== object.values.length) invalid();
  const bucket_labels = object.bucket_labels.map(item => {
    const value = text(item);
    return [...value].length <= 120 ? value : invalid();
  });
  const values = object.values.map(item =>
    typeof item === 'number' && Number.isFinite(item) && item >= 0 ? item : invalid());
  const denominator = nonnegativeInteger(object.denominator);
  const currency = object.currency === null ? null : boundedText(object.currency, 40);
  if (object.side !== null && object.side !== 'paid' && object.side !== 'received') invalid();
  if (object.timezone !== null && object.timezone !== 'UTC') invalid();
  if (object.unit === 'transactions') {
    if (currency !== null || object.side !== null || !edaCountIds.has(series_id)) invalid();
  } else if (currency === null || object.side === null
    || series_id !== `${object.side}_amount_${currency}`) invalid();
  return { series_id, label, unit: object.unit, bucket_labels, values, denominator,
    currency, side: object.side, timezone: object.timezone };
}

export function decodeEdaSummary(value: unknown): EdaSummary {
  const object = closedObject(value, [
    'dataset_version', 'source_sha256', 'synthetic_data', 'coverage_start_utc',
    'coverage_end_utc', 'source_count', 'accepted_count', 'rejected_count',
    'warmup_count', 'scoreable_count', 'quality_counts',
    'omitted_amount_currencies', 'series',
  ]);
  if (object.synthetic_data !== true) invalid();
  const source_sha256 = patternedText(object.source_sha256, /^[0-9a-f]{64}(?![\s\S])/);
  const source_count = nonnegativeInteger(object.source_count);
  const accepted_count = nonnegativeInteger(object.accepted_count);
  const rejected_count = nonnegativeInteger(object.rejected_count);
  const warmup_count = nonnegativeInteger(object.warmup_count);
  const scoreable_count = nonnegativeInteger(object.scoreable_count);
  if (source_count !== accepted_count + rejected_count
    || accepted_count !== warmup_count + scoreable_count) invalid();
  const coverage_start_utc = object.coverage_start_utc === null ? null : timestamp(object.coverage_start_utc);
  const coverage_end_utc = object.coverage_end_utc === null ? null : timestamp(object.coverage_end_utc);
  if ((coverage_start_utc === null) !== (coverage_end_utc === null)
    || (accepted_count === 0) !== (coverage_start_utc === null)
    || (coverage_start_utc !== null && coverage_end_utc !== null
      && coverage_start_utc > coverage_end_utc)) invalid();
  if (!isRecord(object.quality_counts) || Object.keys(object.quality_counts).length > 20) invalid();
  const quality_counts: Record<string, number> = Object.create(null);
  for (const [key, count] of Object.entries(object.quality_counts)) {
    if (!key || [...key].length > 80
      || /label|launder|target|positive|negative|fraud/i.test(key)) invalid();
    quality_counts[key] = nonnegativeInteger(count);
  }
  const omitted = closedObject(object.omitted_amount_currencies, ['paid', 'received']);
  const omitted_amount_currencies = {
    paid: nonnegativeInteger(omitted.paid), received: nonnegativeInteger(omitted.received),
  };
  if (!Array.isArray(object.series) || object.series.length > 30) invalid();
  const series = object.series.map(decodeEdaSeries);
  if (series.some(item => item.denominator > accepted_count)) invalid();
  return { dataset_version: boundedText(object.dataset_version, 120), source_sha256,
    synthetic_data: true, coverage_start_utc, coverage_end_utc, source_count,
    accepted_count, rejected_count, warmup_count, scoreable_count, quality_counts,
    omitted_amount_currencies, series };
}
