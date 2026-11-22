import { ContractValidationError } from '../contracts';
import { decodeCanonicalTransactionId, decodePredictionResult, decodeRiskErrorEnvelope, decodeModelResults, decodeEdaSummary } from './contracts';
import type { EdaSummary, ModelResults, PredictionResult, RiskErrorCode } from './contracts';

export type ApiErrorCode = RiskErrorCode
  | 'invalid_response' | 'network_error' | 'timeout' | 'cancelled';

export interface RequestOptions {
  signal?: AbortSignal;
}

const messages: Record<ApiErrorCode, string> = {
  invalid_request: 'Neispravan zahtev.',
  internal_error: 'Usluga trenutno nije dostupna.',
  transaction_not_found: 'Transakcija nije pronađena.',
  transaction_ineligible: 'Transakcija nije podobna za model procenu.',
  model_unavailable: 'Model procena trenutno nije dostupna.',
  results_unavailable: 'Rezultati nisu dostupni.',
  evaluation_not_authorized: 'Evaluacija nije odobrena.',
  dataset_unavailable: 'Podaci nisu dostupni.',
  invalid_response: 'Server je vratio neispravan odgovor.',
  network_error: 'Povezivanje sa serverom nije uspelo.',
  timeout: 'Vreme čekanja na odgovor je isteklo.',
  cancelled: 'Zahtev je otkazan.',
};

export class ApiError extends Error {
  readonly code: ApiErrorCode;
  readonly status: number | undefined;

  constructor(code: ApiErrorCode, status?: number) {
    super(messages[code]);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
  }
}

async function request<T>(
  url: string, decode: (value: unknown) => T, { signal }: RequestOptions,
  errorContract: 'risk' | 'results' | 'eda',
): Promise<T> {
  if (signal?.aborted) throw new ApiError('cancelled');

  const controller = new AbortController();
  let interruption: ApiError | undefined;
  let rejectInterruption: ((error: ApiError) => void) | undefined;
  const interrupted = new Promise<never>((_resolve, reject) => { rejectInterruption = reject; });
  const stop = (code: 'cancelled' | 'timeout') => {
    if (interruption) return;
    interruption = new ApiError(code);
    rejectInterruption?.(interruption);
    controller.abort();
  };
  const cancel = () => stop('cancelled');
  signal?.addEventListener('abort', cancel, { once: true });
  const timer = setTimeout(() => stop('timeout'), 5000);

  const receive = async (): Promise<T> => {
    let response: Response;
    try {
      response = await fetch(url, { signal: controller.signal });
    } catch {
      throw interruption ?? new ApiError('network_error');
    }
    if (interruption) throw interruption;
    const mediaType = response.headers.get('content-type')?.split(';')[0].trim().toLowerCase();
    if (mediaType !== 'application/json') throw new ApiError('invalid_response', response.status);

    let payload: unknown;
    try {
      payload = await response.json();
    } catch (error) {
      if (interruption) throw interruption;
      // Fetch body consumption rejects TypeError if a connection/stream fails;
      // JSON syntax errors are invalid responses. Neither exposes raw text.
      throw new ApiError(error instanceof TypeError ? 'network_error' : 'invalid_response',
        response.status);
    }
    if (interruption) throw interruption;
    try {
      if (response.status === 200) return decode(payload);
      const envelope = decodeRiskErrorEnvelope(payload);
      const expected = errorContract === 'risk' ? expectedRiskErrorCode(response.status)
        : errorContract === 'results' ? expectedResultsErrorCode(response.status)
          : expectedEdaErrorCode(response.status);
      if (envelope.error.code !== expected) {
        throw new ApiError('invalid_response', response.status);
      }
      // Decode but never forward arbitrary server-provided messages to views.
      throw new ApiError(envelope.error.code, response.status);
    } catch (error) {
      if (error instanceof ContractValidationError) {
        throw new ApiError('invalid_response', response.status);
      }
      throw error;
    }
  };

  try {
    // Explicit race also settles requests if a transport/body ignores abort.
    // The deadline covers both headers and JSON consumption.
    return await Promise.race([receive(), interrupted]);
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener('abort', cancel);
  }
}

function expectedRiskErrorCode(status: number): RiskErrorCode | undefined {
  switch (status) {
    case 404: return 'transaction_not_found';
    case 409: return 'transaction_ineligible';
    case 422: return 'invalid_request';
    case 503: return 'model_unavailable';
    case 500: return 'internal_error';
    default: return undefined;
  }
}

function expectedResultsErrorCode(status: number): RiskErrorCode | undefined {
  switch (status) {
    case 404: return 'results_unavailable';
    case 409: return 'evaluation_not_authorized';
    case 422: return 'invalid_request';
    case 500: return 'internal_error';
    default: return undefined;
  }
}

function expectedEdaErrorCode(status: number): RiskErrorCode | undefined {
  switch (status) {
    case 404: return 'dataset_unavailable';
    case 422: return 'invalid_request';
    case 500: return 'internal_error';
    default: return undefined;
  }
}

export function getTransactionRisk(transactionId: string, options: RequestOptions = {}): Promise<PredictionResult> {
  const id = decodeCanonicalTransactionId(transactionId);
  return request(`/api/transactions/${encodeURIComponent(id)}/risk`, value => {
    const result = decodePredictionResult(value);
    if (result.transaction_id !== id) throw new ContractValidationError();
    return result;
  }, options, 'risk');
}

export function getModelResults(options: RequestOptions = {}): Promise<ModelResults> {
  return request('/api/model/results', decodeModelResults, options, 'results');
}

export function getEdaSummary(options: RequestOptions = {}): Promise<EdaSummary> {
  return request('/api/eda/summary', decodeEdaSummary, options, 'eda');
}
