import {
  ContractValidationError, decodeCaseDetailResponse, decodeCaseListResponse,
  decodeErrorEnvelope, decodeErrorEnvelopeV2,
} from './contracts';
import type { CaseDetailResponse, CaseListResponse, V2ErrorCode } from './contracts';

export type ApiErrorCode = V2ErrorCode
  | 'invalid_response' | 'network_error' | 'timeout' | 'cancelled';

export interface RequestOptions {
  signal?: AbortSignal;
  snapshot?: string;
  dataset?: boolean;
}

const messages: Record<ApiErrorCode, string> = {
  invalid_request: 'Neispravan zahtev.',
  case_not_found: 'Slučaj nije pronađen.',
  internal_error: 'Usluga trenutno nije dostupna.',
  stale_snapshot: 'Izabrani pregled više nije aktivan. Osvježite listu.',
  run_unavailable: 'Trenutno nema dostupnog kompletnog pregleda.',
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

function expectedErrorCode(status: number, dataset: boolean): V2ErrorCode | undefined {
  switch (status) {
    case 404: return 'case_not_found';
    case 422: return 'invalid_request';
    case 500: return 'internal_error';
    case 409: return dataset ? 'stale_snapshot' : undefined;
    case 503: return dataset ? 'run_unavailable' : undefined;
    default: return undefined;
  }
}

async function request<T>(
  url: string, decode: (value: unknown) => T, { signal, dataset = false }: RequestOptions,
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
      const envelope = dataset ? decodeErrorEnvelopeV2(payload) : decodeErrorEnvelope(payload);
      if (envelope.error.code !== expectedErrorCode(response.status, dataset)) {
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

export function getCases(options: RequestOptions = {}): Promise<CaseListResponse> {
  return request('/api/cases', value => {
    const result = decodeCaseListResponse(value);
    if (options.dataset && !('contract_version' in result)) throw new ContractValidationError();
    return result;
  }, options);
}

export function getCase(caseId: string, options: RequestOptions = {}): Promise<CaseDetailResponse> {
  const snapshot = options.snapshot;
  const url = `/api/cases/${encodeURIComponent(caseId)}`
    + (snapshot === undefined ? '' : `?snapshot=${encodeURIComponent(snapshot)}`);
  return request(url, value => {
    const detail = decodeCaseDetailResponse(value);
    if (detail.case_id !== caseId) throw new ContractValidationError();
    if (snapshot !== undefined) {
      if (!('contract_version' in detail) || detail.snapshot_ref !== snapshot) {
        throw new ContractValidationError();
      }
    } else if ('contract_version' in detail) throw new ContractValidationError();
    return detail;
  }, { ...options, dataset: snapshot !== undefined });
}
