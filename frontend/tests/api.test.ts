import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

// Test-local public boundary convention; no production API module is supplied.
interface CaseApi {
  getCases(options?: { signal?: AbortSignal }): Promise<unknown>;
  getCase(caseId: string, options?: { signal?: AbortSignal }): Promise<unknown>;
}

const apiModules = import.meta.glob<CaseApi>('../src/api.ts');
const fetchMock = vi.fn<typeof fetch>();
const DETAIL = {
  case_id: 'CASE-001',
  transaction: {
    transaction_id: 'TX-001', occurred_at: '2026-01-01T10:00:00Z',
    sender_account: 'DEMO-BANK-A:001', receiver_account: 'DEMO-BANK-B:002',
    amount: '1250.00', currency: 'EUR',
  },
  risk_assessment: {
    transaction_id: 'TX-001', score: 0.75, source: 'fixture',
    scorer_version: 'fixture-v1', scored_at: '2026-01-01T10:00:00Z',
    explanation: 'Illustrative synthetic score; no ML inference performed.',
  },
};
const LIST = {
  items: [{ case_id: 'CASE-001', transaction_id: 'TX-001', score: 0.75, score_source: 'fixture' }],
};

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal('fetch', fetchMock);
});

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

async function apiClient(): Promise<CaseApi> {
  const load = apiModules['../src/api.ts'];
  // Glob discovery keeps collection valid while T017 is intentionally absent.
  expect(load, 'Missing frontend fetch/decoding boundary (T017)').toBeTypeOf('function');
  const api = await load();
  expect(api.getCases, 'Missing getCases request boundary').toBeTypeOf('function');
  expect(api.getCase, 'Missing getCase request boundary').toBeTypeOf('function');
  return api;
}

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status, headers: { 'content-type': 'application/json' },
  });
}

function changed(payload: unknown, path: readonly (string | number)[], value: unknown): unknown {
  // Deliberately invalid test input must bypass TypeScript's success-payload types.
  const copy = structuredClone(payload);
  let object = copy as Record<string | number, unknown>;
  for (const key of path.slice(0, -1)) object = object[key] as Record<string | number, unknown>;
  object[path[path.length - 1]] = value;
  return copy;
}

function pendingFetch(): { signal: () => AbortSignal | null | undefined } {
  let requestSignal: AbortSignal | null | undefined;
  fetchMock.mockImplementation((_input, init) => {
    requestSignal = init?.signal;
    return new Promise<Response>((_resolve, reject) => {
      const cancel = () => reject(new DOMException('Aborted transport', 'AbortError'));
      if (requestSignal?.aborted) cancel();
      else requestSignal?.addEventListener('abort', cancel, { once: true });
    });
  });
  return { signal: () => requestSignal };
}

describe('successful response decoding', () => {
  it('decodes the exact case list using a relative API URL', async () => {
    const api = await apiClient();
    fetchMock.mockResolvedValueOnce(jsonResponse(LIST));
    expect(await api.getCases()).toEqual(LIST);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][0]).toBe('/api/cases');
  });

  it('decodes complete case details without substituting scores or transaction data', async () => {
    const api = await apiClient();
    fetchMock.mockResolvedValueOnce(jsonResponse(DETAIL));
    expect(await api.getCase('CASE-001')).toEqual(DETAIL);
    expect(fetchMock.mock.calls[0][0]).toBe('/api/cases/CASE-001');
  });

  it('preserves the contract-defined empty list', async () => {
    const api = await apiClient();
    fetchMock.mockResolvedValueOnce(jsonResponse({ items: [] }));
    expect(await api.getCases()).toEqual({ items: [] });
  });

  it.each(['fixture', 'rules', 'model'])('accepts schema-valid source %s and score endpoints', async source => {
    const api = await apiClient();
    for (const score of [0, 1]) {
      const detail = structuredClone(DETAIL);
      detail.risk_assessment.source = source;
      detail.risk_assessment.score = score;
      const list = { items: [{ ...LIST.items[0], score, score_source: source }] };
      fetchMock.mockResolvedValueOnce(jsonResponse(list)).mockResolvedValueOnce(jsonResponse(detail));
      expect(await api.getCases()).toEqual(list);
      expect(await api.getCase('CASE-001')).toEqual(detail);
    }
  });
});

describe('invalid success payloads', () => {
  it.each([null, [], 'invalid', {}, { items: null }, { items: {} }, { items: [null] }]
    .map(payload => ({ payload })))(
    'rejects malformed list $payload instead of fabricating an empty list', async ({ payload }) => {
      const api = await apiClient();
      fetchMock.mockResolvedValueOnce(jsonResponse(payload));
      await expect(api.getCases()).rejects.toMatchObject({ code: 'invalid_response' });
      expect(fetchMock).toHaveBeenCalledTimes(1);
    },
  );

  it.each([null, [], 'invalid', {}, { ...DETAIL, transaction: null },
    { ...DETAIL, risk_assessment: null }].map(payload => ({ payload })))(
    'rejects malformed detail $payload', async ({ payload }) => {
    const api = await apiClient();
    fetchMock.mockResolvedValueOnce(jsonResponse(payload));
    await expect(api.getCase('CASE-001')).rejects.toMatchObject({ code: 'invalid_response' });
    },
  );

  const invalidSummaryFields: [string, unknown][] = [
    ['case_id', 'CASE-1'], ['case_id', 'CASE-001\n'], ['transaction_id', 'TX-01'],
    ['score', -0.01], ['score', 1.01], ['score', '0.75'], ['score', true], ['score', null],
    ['score_source', 'unknown'],
  ];
  it.each(invalidSummaryFields)('rejects summary field %s=%j', async (field, value) => {
    const api = await apiClient();
    fetchMock.mockResolvedValueOnce(jsonResponse(changed(LIST, ['items', 0, field], value)));
    await expect(api.getCases()).rejects.toMatchObject({ code: 'invalid_response' });
  });

  const invalidDetailFields: [readonly string[], unknown][] = [
    [['case_id'], 'CASE-001\n'], [['transaction', 'transaction_id'], 'TX-0001'],
    [['transaction', 'amount'], 1250], [['transaction', 'amount'], '-1.00'],
    [['transaction', 'amount'], '01.00'], [['transaction', 'amount'], '1.0'],
    [['transaction', 'amount'], '1.00\n'], [['transaction', 'currency'], 'eur'],
    [['transaction', 'currency'], 'EUR\n'], [['transaction', 'sender_account'], ''],
    [['transaction', 'receiver_account'], 'a'.repeat(121)],
    [['transaction', 'occurred_at'], '2026-02-30T10:00:00Z'],
    [['transaction', 'occurred_at'], '2026-01-01T10:00:00+00:00'],
    [['risk_assessment', 'transaction_id'], 'TX-002'],
    [['risk_assessment', 'score'], -0.01], [['risk_assessment', 'score'], 1.01],
    [['risk_assessment', 'score'], '0.75'], [['risk_assessment', 'score'], true],
    [['risk_assessment', 'source'], 'unknown'], [['risk_assessment', 'scorer_version'], ''],
    [['risk_assessment', 'scorer_version'], 'v'.repeat(81)],
    [['risk_assessment', 'explanation'], ''], [['risk_assessment', 'explanation'], 'e'.repeat(501)],
    [['risk_assessment', 'scored_at'], '2026-02-30T10:00:00Z'],
  ];
  it.each(invalidDetailFields)('rejects detail field %j=%j', async (path, value) => {
    const api = await apiClient();
    fetchMock.mockResolvedValueOnce(jsonResponse(changed(DETAIL, path, value)));
    await expect(api.getCase('CASE-001')).rejects.toMatchObject({ code: 'invalid_response' });
  });

  it.each(['case_id', 'transaction', 'risk_assessment'])('rejects missing detail %s', async field => {
    const api = await apiClient();
    const body = { ...DETAIL } as Record<string, unknown>;
    delete body[field];
    fetchMock.mockResolvedValueOnce(jsonResponse(body));
    await expect(api.getCase('CASE-001')).rejects.toMatchObject({ code: 'invalid_response' });
  });

  it.each(['case_id', 'transaction_id', 'score', 'score_source'])('rejects missing summary %s', async field => {
    const api = await apiClient();
    const item = { ...LIST.items[0] } as Record<string, unknown>;
    delete item[field];
    fetchMock.mockResolvedValueOnce(jsonResponse({ items: [item] }));
    await expect(api.getCases()).rejects.toMatchObject({ code: 'invalid_response' });
  });

  it.each([
    ['list root', 'list', ['unexpected']],
    ['list item', 'list', ['items', 0, 'isFraud']],
    ['detail root', 'detail', ['reference_decision']],
    ['transaction', 'detail', ['transaction', 'Is Laundering']],
    ['assessment', 'detail', ['risk_assessment', 'unexpected']],
  ] as const)('rejects additional properties at %s', async (_name, kind, path) => {
    const api = await apiClient();
    fetchMock.mockResolvedValueOnce(jsonResponse(changed(kind === 'list' ? LIST : DETAIL, path, true)));
    await expect(kind === 'list' ? api.getCases() : api.getCase('CASE-001'))
      .rejects.toMatchObject({ code: 'invalid_response' });
  });

  it('rejects nonfinite numeric JSON rather than clamping it to a fallback score', async () => {
    const api = await apiClient();
    const raw = JSON.stringify(DETAIL).replace('"score":0.75', '"score":1e400');
    fetchMock.mockResolvedValueOnce(new Response(raw, { headers: { 'content-type': 'application/json' } }));
    await expect(api.getCase('CASE-001')).rejects.toMatchObject({ code: 'invalid_response' });
  });

  it('rejects a valid detail belonging to a different requested case', async () => {
    const api = await apiClient();
    fetchMock.mockResolvedValueOnce(jsonResponse({ ...DETAIL, case_id: 'CASE-002' }));
    await expect(api.getCase('CASE-001')).rejects.toMatchObject({ code: 'invalid_response' });
  });

  it.each([
    ['truncated JSON', '{"items":', 'application/json'],
    ['HTML body', '<html>PRIVATE_SERVER_ERROR</html>', 'text/html'],
    ['empty body', '', 'application/json'],
  ])('rejects %s as an invalid server response', async (_name, body, contentType) => {
    const api = await apiClient();
    fetchMock.mockResolvedValueOnce(new Response(body, { headers: { 'content-type': contentType } }));
    await expect(api.getCases()).rejects.toMatchObject({ code: 'invalid_response' });
  });
});

describe('controlled HTTP and transport errors', () => {
  it.each([
    [404, 'case_not_found'], [422, 'invalid_request'], [500, 'internal_error'],
  ])('handles HTTP %i with its controlled code %s', async (status, code) => {
    const api = await apiClient();
    fetchMock.mockResolvedValueOnce(jsonResponse({ error: { code, message: 'Unavailable.' } }, status));
    await expect(api.getCase('CASE-001')).rejects.toMatchObject({ code, status });
  });

  it.each([
    { error: { code: 'internal_error', message: '' } },
    { error: { code: 'unknown', message: 'Unavailable.' } },
    { error: { code: 'internal_error', message: 'Unavailable.', stack: 'PRIVATE_STACK' } },
    { error: { code: 'internal_error', message: 'Unavailable.' }, extra: true },
    { detail: 'PRIVATE_SERVER_ERROR' },
  ])('rejects a contract-invalid error envelope %j', async body => {
    const api = await apiClient();
    fetchMock.mockResolvedValueOnce(jsonResponse(body, 500));
    await expect(api.getCases()).rejects.toMatchObject({ code: 'invalid_response' });
  });

  it('distinguishes network failure without fallback data or automatic retries', async () => {
    const api = await apiClient();
    fetchMock.mockRejectedValueOnce(new TypeError('PRIVATE_NETWORK_FAILURE'));
    await expect(api.getCases()).rejects.toMatchObject({ code: 'network_error' });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('stays pending through 4999 ms, then times out and aborts at 5000 ms', async () => {
    const api = await apiClient();
    vi.useFakeTimers();
    const transport = pendingFetch();
    let settled = false;
    const outcome = api.getCases().then(
      () => ({ code: 'unexpected_success' }), error => error,
    ).finally(() => { settled = true; });
    await vi.advanceTimersByTimeAsync(4999);
    expect(settled).toBe(false);
    await vi.advanceTimersByTimeAsync(1);
    expect(transport.signal()?.aborted).toBe(true);
    expect(settled).toBe(true);
    await expect(outcome).resolves.toMatchObject({ code: 'timeout' });
    expect(vi.getTimerCount()).toBe(0);
  });

  it('classifies caller cancellation separately from timeout and network failure', async () => {
    const api = await apiClient();
    vi.useFakeTimers();
    const transport = pendingFetch();
    const controller = new AbortController();
    const outcome = api.getCase('CASE-001', { signal: controller.signal })
      .then(() => ({ code: 'unexpected_success' }), error => error);
    controller.abort();
    await vi.advanceTimersByTimeAsync(0);
    expect(transport.signal()?.aborted).toBe(true);
    await expect(outcome).resolves.toMatchObject({ code: 'cancelled' });
    expect(vi.getTimerCount()).toBe(0);
  });

  it('honors an already cancelled signal without resolving fallback data', async () => {
    const api = await apiClient();
    const transport = pendingFetch();
    const controller = new AbortController();
    controller.abort();
    await expect(api.getCases({ signal: controller.signal }))
      .rejects.toMatchObject({ code: 'cancelled' });
    // Either short-circuit or pass the cancelled signal to fetch: both prevent
    // a real request. Do not prescribe the client's internal implementation.
    if (fetchMock.mock.calls.length) expect(transport.signal()?.aborted).toBe(true);
  });

  it('clears the timeout after a successful response', async () => {
    const api = await apiClient();
    vi.useFakeTimers();
    fetchMock.mockResolvedValueOnce(jsonResponse(LIST));
    expect(await api.getCases()).toEqual(LIST);
    expect(vi.getTimerCount()).toBe(0);
  });
});
