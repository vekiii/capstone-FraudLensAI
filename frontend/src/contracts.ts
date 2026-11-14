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

// Feature 002 public dataset union. Foundation validators above remain unchanged.
export type V2Source = 'rules' | 'model';
export type V2Kind = 'ordinal_rule_score' | 'uncalibrated_probability_estimate'
  | 'calibrated_probability';
export type V2ErrorCode = ServerErrorCode | 'stale_snapshot' | 'run_unavailable';
export interface CaseSummaryV2 {
  case_id: string; transaction_id: string; event_time: string; score: number;
  score_kind: V2Kind; score_source: V2Source;
}
export interface CaseListV2 {
  contract_version: 2; snapshot_ref: string; dataset_version: string;
  data_source: 'ibm_aml_hi_small'; score_source: V2Source; scorer_version: string;
  total_alerts: number; displayed_count: number; truncated: boolean;
  selected_time_range: { from: string | null; to: string | null };
  items: CaseSummaryV2[];
}
export interface TransactionV2 {
  transaction_id: string; event_time_utc: string; event_time_raw: string;
  time_basis: 'source_explicit_timezone' | 'documented_source_timezone'
    | 'assumed_utc_for_synthetic_benchmark';
  sender: { bank: string; account: string }; receiver: { bank: string; account: string };
  paid: { amount: string; currency: string }; received: { amount: string; currency: string };
  payment_format: string | null;
}
export interface ExplanationItemV2 {
  feature_key: string; observed_value: string; unit: string;
  direction: 'increases' | 'decreases' | 'neutral'; contribution: number;
  rule_condition: string | null;
}
export type ExplanationV2 =
  | { status: 'unavailable'; reason_code: 'missing_context' | 'unsupported_method'
      | 'missing_artifact'; feature_snapshot_digest: string }
  | { status: 'available'; method: 'rules' | 'linear_log_odds' | 'tree_path';
      explained_scale: 'risk_score' | 'log_odds' | 'positive_class_estimate';
      feature_snapshot_digest: string; partial: boolean; base_value: number | null;
      remainder: number | null; items: ExplanationItemV2[] };
export interface AssessmentV2 {
  transaction_id: string; run_id: string; dataset_version: string; score: number;
  score_kind: V2Kind; score_source: V2Source; scorer_version: string;
  feature_version: string; event_time_utc: string; history_cutoff_exclusive_at: string;
  scored_at: string; history_coverage: { state: 'full' | 'incomplete' | 'unavailable';
    start: string | null }; explanation: ExplanationV2;
}
export interface CaseDetailV2 {
  contract_version: 2; snapshot_ref: string; dataset_version: string;
  case_id: string; transaction: TransactionV2; risk_assessment: AssessmentV2;
}
export interface HealthV2 {
  contract_version: 2; status: 'ok' | 'unavailable'; mode: 'dataset';
  data_source: 'ibm_aml_hi_small'; score_source: V2Source;
  dataset_version: string | null; active_run_id: string | null;
}
export type CaseListResponse = CaseList | CaseListV2;
export type CaseDetailResponse = CaseDetail | CaseDetailV2;

function v2Instant(value: unknown): string {
  const result = patternedText(value,
    /^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,9})?Z(?![\s\S])/);
  return timestamp(result);
}
function v2CaseId(value: unknown): string {
  return patternedText(value, /^C[0-9a-f]{32}(?![\s\S])/);
}
function v2TransactionId(value: unknown): string {
  return patternedText(value, /^D[0-9a-f]{32}(?![\s\S])/);
}
function v2RunId(value: unknown): string {
  return patternedText(value, /^run_[A-Za-z0-9_-]{1,64}(?![\s\S])/);
}
function v2Version(value: unknown): string {
  return patternedText(value, /^dv_[0-9a-f]{64}(?![\s\S])/);
}
function nonnegativeInteger(value: unknown): number {
  return typeof value === 'number' && Number.isSafeInteger(value) && value >= 0
    ? value : invalid();
}
function finite(value: unknown): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : invalid();
}
function v2Source(value: unknown): V2Source {
  return value === 'rules' || value === 'model' ? value : invalid();
}
function v2Kind(value: unknown): V2Kind {
  return value === 'ordinal_rule_score' || value === 'uncalibrated_probability_estimate'
    || value === 'calibrated_probability' ? value : invalid();
}
function nullableInstant(value: unknown): string | null {
  return value === null ? null : v2Instant(value);
}
function v2BankAccount(value: unknown): { bank: string; account: string } {
  const object = closedObject(value, ['bank', 'account']);
  return { bank: boundedText(object.bank, 120), account: boundedText(object.account, 120) };
}
function v2Money(value: unknown): { amount: string; currency: string } {
  const object = closedObject(value, ['amount', 'currency']);
  const amount = boundedText(object.amount, 200);
  if (!/^(0|[1-9][0-9]*)(?:\.[0-9]+)?(?![\s\S])/.test(amount)) return invalid();
  return { amount, currency: boundedText(object.currency, 17) };
}
function v2Transaction(value: unknown): TransactionV2 {
  const object = closedObject(value, ['transaction_id', 'event_time_utc', 'event_time_raw',
    'time_basis', 'sender', 'receiver', 'paid', 'received', 'payment_format']);
  const basis = object.time_basis;
  if (basis !== 'source_explicit_timezone' && basis !== 'documented_source_timezone'
      && basis !== 'assumed_utc_for_synthetic_benchmark') return invalid();
  return {
    transaction_id: v2TransactionId(object.transaction_id),
    event_time_utc: v2Instant(object.event_time_utc),
    event_time_raw: boundedText(object.event_time_raw, 120), time_basis: basis,
    sender: v2BankAccount(object.sender), receiver: v2BankAccount(object.receiver),
    paid: v2Money(object.paid), received: v2Money(object.received),
    payment_format: object.payment_format === null ? null : boundedText(object.payment_format, 120),
  };
}
function v2Explanation(value: unknown, sourceValue: V2Source, scoreValue: number): ExplanationV2 {
  if (!isRecord(value)) return invalid();
  if (value.status === 'unavailable') {
    const object = closedObject(value, ['status', 'reason_code', 'feature_snapshot_digest']);
    const reason = object.reason_code;
    if (reason !== 'missing_context' && reason !== 'unsupported_method'
        && reason !== 'missing_artifact') return invalid();
    return { status: 'unavailable', reason_code: reason,
      feature_snapshot_digest: boundedText(object.feature_snapshot_digest, 100) };
  }
  const object = closedObject(value, ['status', 'method', 'explained_scale',
    'feature_snapshot_digest', 'partial', 'base_value', 'remainder', 'items']);
  if (object.status !== 'available') return invalid();
  const method = object.method;
  if (method !== 'rules' && method !== 'linear_log_odds' && method !== 'tree_path') return invalid();
  const scale = { rules: 'risk_score', linear_log_odds: 'log_odds',
    tree_path: 'positive_class_estimate' } as const;
  if (object.explained_scale !== scale[method] || (sourceValue === 'rules') !== (method === 'rules')
      || typeof object.partial !== 'boolean' || !Array.isArray(object.items)
      || object.items.length > 3) return invalid();
  const items: ExplanationItemV2[] = object.items.map(item => {
    const part = closedObject(item, ['feature_key', 'observed_value', 'unit',
      'direction', 'contribution', 'rule_condition']);
    const direction = part.direction;
    if (direction !== 'increases' && direction !== 'decreases' && direction !== 'neutral') {
      return invalid();
    }
    return { feature_key: boundedText(part.feature_key, 120),
      observed_value: boundedText(part.observed_value, 200), unit: boundedText(part.unit, 40),
      direction, contribution: finite(part.contribution),
      rule_condition: part.rule_condition === null ? null : boundedText(part.rule_condition, 300) };
  });
  const base = object.base_value === null ? null : finite(object.base_value);
  const remainder = object.remainder === null ? null : finite(object.remainder);
  if ((base === null) !== (remainder === null)) return invalid();
  if (base !== null && remainder !== null) {
    const raw = base + remainder + items.reduce((total, item) => total + item.contribution, 0);
    const reconstructed = method === 'linear_log_odds' ? 1 / (1 + Math.exp(-raw)) : raw;
    if (Math.abs(reconstructed - scoreValue) > 1e-8) return invalid();
  }
  return { status: 'available', method, explained_scale: scale[method],
    feature_snapshot_digest: boundedText(object.feature_snapshot_digest, 100),
    partial: object.partial, base_value: base, remainder, items };
}
function v2Assessment(value: unknown): AssessmentV2 {
  const object = closedObject(value, ['transaction_id', 'run_id', 'dataset_version', 'score',
    'score_kind', 'score_source', 'scorer_version', 'feature_version', 'event_time_utc',
    'history_cutoff_exclusive_at', 'scored_at', 'history_coverage', 'explanation']);
  const scoreSource = v2Source(object.score_source);
  const scoreKind = v2Kind(object.score_kind);
  if ((scoreSource === 'rules') !== (scoreKind === 'ordinal_rule_score')) return invalid();
  const coverage = closedObject(object.history_coverage, ['state', 'start']);
  if (coverage.state !== 'full' && coverage.state !== 'incomplete'
      && coverage.state !== 'unavailable') return invalid();
  const result: AssessmentV2 = {
    transaction_id: v2TransactionId(object.transaction_id), run_id: v2RunId(object.run_id),
    dataset_version: v2Version(object.dataset_version), score: score(object.score),
    score_kind: scoreKind, score_source: scoreSource,
    scorer_version: boundedText(object.scorer_version, 80),
    feature_version: boundedText(object.feature_version, 80),
    event_time_utc: v2Instant(object.event_time_utc),
    history_cutoff_exclusive_at: v2Instant(object.history_cutoff_exclusive_at),
    scored_at: v2Instant(object.scored_at),
    history_coverage: { state: coverage.state, start: nullableInstant(coverage.start) },
    explanation: v2Explanation(object.explanation, scoreSource, score(object.score)),
  };
  if (result.history_cutoff_exclusive_at !== result.event_time_utc) return invalid();
  return result;
}
function v2Summary(value: unknown): CaseSummaryV2 {
  const object = closedObject(value, ['case_id', 'transaction_id', 'event_time',
    'score', 'score_kind', 'score_source']);
  const scoreSource = v2Source(object.score_source);
  const scoreKind = v2Kind(object.score_kind);
  if ((scoreSource === 'rules') !== (scoreKind === 'ordinal_rule_score')) return invalid();
  return { case_id: v2CaseId(object.case_id),
    transaction_id: v2TransactionId(object.transaction_id),
    event_time: v2Instant(object.event_time), score: score(object.score),
    score_kind: scoreKind, score_source: scoreSource };
}
export function decodeCaseListV2(value: unknown): CaseListV2 {
  const object = closedObject(value, ['contract_version', 'snapshot_ref', 'dataset_version',
    'data_source', 'score_source', 'scorer_version', 'total_alerts', 'displayed_count',
    'truncated', 'selected_time_range', 'items']);
  if (object.contract_version !== 2 || object.data_source !== 'ibm_aml_hi_small'
      || !Array.isArray(object.items) || object.items.length > 100
      || typeof object.truncated !== 'boolean') return invalid();
  const range = closedObject(object.selected_time_range, ['from', 'to']);
  const items = object.items.map(v2Summary);
  const total = nonnegativeInteger(object.total_alerts);
  const count = nonnegativeInteger(object.displayed_count);
  const sourceValue = v2Source(object.score_source);
  const from = nullableInstant(range.from);
  const to = nullableInstant(range.to);
  if (count !== items.length || count > 100 || total < count
      || object.truncated !== (total > count)
      || from !== (items[0]?.event_time ?? null)
      || to !== (items.at(-1)?.event_time ?? null)
      || items.some(item => item.score_source !== sourceValue)
      || new Set(items.map(item => item.case_id)).size !== count
      || new Set(items.map(item => item.transaction_id)).size !== count
      || items.some((item, index) => index > 0 &&
        `${items[index - 1].event_time}/${items[index - 1].transaction_id}`
        > `${item.event_time}/${item.transaction_id}`)) return invalid();
  return { contract_version: 2, snapshot_ref: v2RunId(object.snapshot_ref),
    dataset_version: v2Version(object.dataset_version), data_source: 'ibm_aml_hi_small',
    score_source: sourceValue, scorer_version: boundedText(object.scorer_version, 80),
    total_alerts: total, displayed_count: count, truncated: object.truncated,
    selected_time_range: { from, to }, items };
}
export function decodeCaseDetailV2(value: unknown): CaseDetailV2 {
  const object = closedObject(value, ['contract_version', 'snapshot_ref', 'dataset_version',
    'case_id', 'transaction', 'risk_assessment']);
  if (object.contract_version !== 2) return invalid();
  const transaction = v2Transaction(object.transaction);
  const assessment = v2Assessment(object.risk_assessment);
  const snapshot = v2RunId(object.snapshot_ref);
  const version = v2Version(object.dataset_version);
  if (transaction.transaction_id !== assessment.transaction_id
      || transaction.event_time_utc !== assessment.event_time_utc
      || assessment.run_id !== snapshot || assessment.dataset_version !== version) return invalid();
  return { contract_version: 2, snapshot_ref: snapshot, dataset_version: version,
    case_id: v2CaseId(object.case_id), transaction, risk_assessment: assessment };
}
export function decodeHealthV2(value: unknown): HealthV2 {
  const object = closedObject(value, ['contract_version', 'status', 'mode', 'data_source',
    'score_source', 'dataset_version', 'active_run_id']);
  if (object.contract_version !== 2 || object.mode !== 'dataset'
      || object.data_source !== 'ibm_aml_hi_small'
      || (object.status !== 'ok' && object.status !== 'unavailable')) return invalid();
  const version = object.dataset_version === null ? null : v2Version(object.dataset_version);
  const active = object.active_run_id === null ? null : v2RunId(object.active_run_id);
  if ((object.status === 'ok') !== (version !== null && active !== null)) return invalid();
  return { contract_version: 2, status: object.status, mode: 'dataset',
    data_source: 'ibm_aml_hi_small', score_source: v2Source(object.score_source),
    dataset_version: version, active_run_id: active };
}
export function decodeErrorEnvelopeV2(value: unknown): { error: { code: V2ErrorCode;
  message: string } } {
  const object = closedObject(value, ['error']);
  const body = closedObject(object.error, ['code', 'message']);
  const code = body.code;
  if (code !== 'invalid_request' && code !== 'case_not_found' && code !== 'internal_error'
      && code !== 'stale_snapshot' && code !== 'run_unavailable') return invalid();
  return { error: { code, message: boundedText(body.message, 200) } };
}
export function decodeCaseListResponse(value: unknown): CaseListResponse {
  return isRecord(value) && Object.hasOwn(value, 'contract_version')
    ? decodeCaseListV2(value) : decodeCaseList(value);
}
export function decodeCaseDetailResponse(value: unknown): CaseDetailResponse {
  return isRecord(value) && Object.hasOwn(value, 'contract_version')
    ? decodeCaseDetailV2(value) : decodeCaseDetail(value);
}
