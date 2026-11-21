// Wire contracts: specs/001-project-foundation/contracts/schemas.json.
// External values remain unknown until a decoder has checked every field.
export type ScoreSource = 'fixture' | 'rules' | 'model';
export type ServerErrorCode = 'invalid_request' | 'case_not_found' | 'internal_error';

export interface Transaction {
  transaction_id: string;
  occurred_at: string;
  sender_account: string;
  receiver_account: string;
  amount: string;
  currency: string;
}

export interface RiskAssessment {
  transaction_id: string;
  score: number;
  source: ScoreSource;
  scorer_version: string;
  scored_at: string;
  explanation: string;
}

export interface CaseSummary {
  case_id: string;
  transaction_id: string;
  score: number;
  score_source: ScoreSource;
}

export interface CaseDetail {
  case_id: string;
  transaction: Transaction;
  risk_assessment: RiskAssessment;
}

export interface CaseList {
  items: CaseSummary[];
}

export interface Health {
  status: 'ok';
  mode: 'fixture';
}

export interface ErrorBody {
  code: ServerErrorCode;
  message: string;
}

export interface ErrorEnvelope {
  error: ErrorBody;
}

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

export class ContractValidationError extends Error {
  constructor() {
    // Never include the rejected value or server text in an exception.
    super('Response does not match the foundation contract.');
    this.name = 'ContractValidationError';
  }
}

function invalid(): never {
  throw new ContractValidationError();
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function closedObject(value: unknown, fields: readonly string[]): Record<string, unknown> {
  if (!isRecord(value) || Object.keys(value).length !== fields.length
    || !fields.every(field => Object.hasOwn(value, field))) return invalid();
  return value;
}

function text(value: unknown): string {
  return typeof value === 'string' ? value : invalid();
}

function boundedText(value: unknown, maximum: number): string {
  const result = text(value);
  // JSON Schema measures Unicode code points, rather than UTF-16 code units.
  const length = [...result].length;
  return length >= 1 && length <= maximum ? result : invalid();
}

function patternedText(value: unknown, pattern: RegExp): string {
  const result = text(value);
  return pattern.test(result) ? result : invalid();
}

function caseId(value: unknown): string {
  return patternedText(value, /^CASE-[0-9]{3}(?![\s\S])/);
}

function transactionId(value: unknown): string {
  return patternedText(value, /^TX-[0-9]{3}(?![\s\S])/);
}

function score(value: unknown): number {
  return typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 1
    ? value : invalid();
}

function source(value: unknown): ScoreSource {
  return value === 'fixture' || value === 'rules' || value === 'model' ? value : invalid();
}

function timestamp(value: unknown): string {
  const result = text(value);
  // RFC3339 calendar/time checks, with the schema's strict uppercase Z suffix.
  // Date.parse alone accepts impossible dates by rolling them into another month.
  const parts = /^([0-9]{4})-([0-9]{2})-([0-9]{2})[Tt]([0-9]{2}):([0-9]{2}):([0-9]{2})(?:\.[0-9]+)?Z(?![\s\S])/
    .exec(result);
  if (!parts) return invalid();
  const [, yearText, monthText, dayText, hourText, minuteText, secondText] = parts;
  const year = Number(yearText);
  const month = Number(monthText);
  const day = Number(dayText);
  const leap = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
  const days = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  if (year < 1 || month < 1 || month > 12 || day < 1 || day > days[month - 1]
    || Number(hourText) > 23 || Number(minuteText) > 59 || Number(secondText) > 59) {
    return invalid();
  }
  return result;
}

export function decodeTransaction(value: unknown): Transaction {
  const object = closedObject(value, [
    'transaction_id', 'occurred_at', 'sender_account', 'receiver_account', 'amount', 'currency',
  ]);
  return {
    transaction_id: transactionId(object.transaction_id),
    occurred_at: timestamp(object.occurred_at),
    sender_account: boundedText(object.sender_account, 120),
    receiver_account: boundedText(object.receiver_account, 120),
    amount: patternedText(object.amount, /^(0|[1-9][0-9]*)\.[0-9]{2}(?![\s\S])/),
    currency: patternedText(object.currency, /^[A-Z]{3}(?![\s\S])/),
  };
}

export function decodeRiskAssessment(value: unknown): RiskAssessment {
  const object = closedObject(value, [
    'transaction_id', 'score', 'source', 'scorer_version', 'scored_at', 'explanation',
  ]);
  return {
    transaction_id: transactionId(object.transaction_id),
    score: score(object.score),
    source: source(object.source),
    scorer_version: boundedText(object.scorer_version, 80),
    scored_at: timestamp(object.scored_at),
    explanation: boundedText(object.explanation, 500),
  };
}

export function decodeCaseSummary(value: unknown): CaseSummary {
  const object = closedObject(value, ['case_id', 'transaction_id', 'score', 'score_source']);
  return {
    case_id: caseId(object.case_id),
    transaction_id: transactionId(object.transaction_id),
    score: score(object.score),
    score_source: source(object.score_source),
  };
}

export function decodeCaseDetail(value: unknown): CaseDetail {
  const object = closedObject(value, ['case_id', 'transaction', 'risk_assessment']);
  const transaction = decodeTransaction(object.transaction);
  const assessment = decodeRiskAssessment(object.risk_assessment);
  if (transaction.transaction_id !== assessment.transaction_id) return invalid();
  return { case_id: caseId(object.case_id), transaction, risk_assessment: assessment };
}

export function decodeCaseList(value: unknown): CaseList {
  const object = closedObject(value, ['items']);
  if (!Array.isArray(object.items)) return invalid();
  return { items: object.items.map(decodeCaseSummary) };
}

export function decodeHealth(value: unknown): Health {
  const object = closedObject(value, ['status', 'mode']);
  if (object.status !== 'ok' || object.mode !== 'fixture') return invalid();
  return { status: object.status, mode: object.mode };
}

export function decodeErrorEnvelope(value: unknown): ErrorEnvelope {
  const object = closedObject(value, ['error']);
  const error = closedObject(object.error, ['code', 'message']);
  const code = error.code;
  if (code !== 'invalid_request' && code !== 'case_not_found' && code !== 'internal_error') {
    return invalid();
  }
  return { error: { code, message: boundedText(error.message, 200) } };
}

const canonicalIdPattern = /^ibm-hi-small:[0-9a-f]{64}:row:[1-9][0-9]*(?![\s\S])/;

export function decodeCanonicalTransactionId(value: unknown): string {
  const id = patternedText(value, canonicalIdPattern);
  return [...id].length <= 160 ? id : invalid();
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

function nonnegativeInteger(value: unknown): number {
  return typeof value === 'number' && Number.isSafeInteger(value) && value >= 0 ? value : invalid();
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
