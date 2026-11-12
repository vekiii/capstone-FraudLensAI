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
