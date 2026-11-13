import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

interface CaseApi {
  getCases(options?: { signal?: AbortSignal }): Promise<unknown>;
  getCase(caseId: string, options?: { signal?: AbortSignal }): Promise<unknown>;
}

const modules = import.meta.glob<CaseApi>('../src/api.ts');
const fetchMock = vi.fn<typeof fetch>();
const empty = () => new Response('{"items":[]}', {
  headers: { 'content-type': 'application/json' },
});

async function client(): Promise<CaseApi> {
  const load = modules['../src/api.ts'];
  expect(load, 'Missing T017 API boundary').toBeTypeOf('function');
  return load();
}

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal('fetch', fetchMock);
});

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('request lifecycle and public error safety', () => {
  it('times out while reading a body after headers arrive', async () => {
    const api = await client();
    vi.useFakeTimers();
    const response = empty();
    vi.spyOn(response, 'json').mockImplementation(() => new Promise(() => {}));
    fetchMock.mockResolvedValueOnce(response);
    const outcome = api.getCases().catch((error: unknown) => error);
    await vi.advanceTimersByTimeAsync(5000);
    await expect(outcome).resolves.toMatchObject({ code: 'timeout' });
    expect(fetchMock.mock.calls[0][1]?.signal?.aborted).toBe(true);
    expect(vi.getTimerCount()).toBe(0);
  });

  it('cancels promptly even if transport ignores abort and resolves later', async () => {
    const api = await client();
    vi.useFakeTimers();
    let complete: ((response: Response) => void) | undefined;
    fetchMock.mockImplementation(() => new Promise(resolve => { complete = resolve; }));
    const controller = new AbortController();
    const outcome = api.getCases({ signal: controller.signal }).catch((error: unknown) => error);
    controller.abort('PRIVATE_ABORT_REASON');
    await expect(outcome).resolves.toMatchObject({ code: 'cancelled' });
    complete?.(empty());
    await vi.advanceTimersByTimeAsync(0);
    await expect(outcome).resolves.toMatchObject({ code: 'cancelled' });
    expect(vi.getTimerCount()).toBe(0);
  });

  it.each(['success', 'network', 'invalid', 'http'])(
    'removes caller listeners and timers after %s', async kind => {
      const api = await client();
      vi.useFakeTimers();
      const controller = new AbortController();
      const add = vi.spyOn(controller.signal, 'addEventListener');
      const remove = vi.spyOn(controller.signal, 'removeEventListener');
      if (kind === 'network') fetchMock.mockRejectedValueOnce(new TypeError('PRIVATE'));
      else if (kind === 'invalid') fetchMock.mockResolvedValueOnce(new Response('invalid'));
      else if (kind === 'http') fetchMock.mockResolvedValueOnce(new Response(
        '{"error":{"code":"internal_error","message":"Unavailable."}}',
        { status: 500, headers: { 'content-type': 'application/json' } },
      ));
      else fetchMock.mockResolvedValueOnce(empty());
      await api.getCases({ signal: controller.signal }).catch(() => undefined);
      expect(vi.getTimerCount()).toBe(0);
      const listener = add.mock.calls.find(([event]) => event === 'abort')?.[1];
      if (listener) expect(remove.mock.calls.some(
        ([event, callback]) => event === 'abort' && callback === listener,
      )).toBe(true);
      controller.abort();
      expect(fetchMock.mock.calls[0][1]?.signal?.aborted).toBe(false);
    },
  );

  it.each(['http', 'network', 'json'])(
    'keeps private %s exception text out of public errors', async kind => {
      const api = await client();
      if (kind === 'network') fetchMock.mockRejectedValueOnce(new TypeError('PRIVATE_NETWORK'));
      else if (kind === 'json') {
        const response = empty();
        vi.spyOn(response, 'json').mockRejectedValueOnce(new SyntaxError('PRIVATE_PARSER'));
        fetchMock.mockResolvedValueOnce(response);
      } else fetchMock.mockResolvedValueOnce(new Response(
        '{"error":{"code":"internal_error","message":"PRIVATE_SERVER C:/secret/file.py"}}',
        { status: 500, headers: { 'content-type': 'application/json' } },
      ));
      const error: unknown = await api.getCases().catch((failure: unknown) => failure);
      expect(error).toBeInstanceOf(Error);
      expect(String(error)).not.toMatch(/PRIVATE|secret|file\.py/);
      expect(JSON.stringify(error)).not.toMatch(/PRIVATE|secret|file\.py/);
    },
  );

  it('rejects a valid envelope whose code disagrees with HTTP status', async () => {
    const api = await client();
    fetchMock.mockResolvedValueOnce(new Response(
      '{"error":{"code":"case_not_found","message":"Missing."}}',
      { status: 500, headers: { 'content-type': 'application/json' } },
    ));
    await expect(api.getCase('CASE-001')).rejects.toMatchObject({ code: 'invalid_response' });
  });

  it.each([201, 503])('rejects undocumented HTTP status %i', async status => {
    const api = await client();
    fetchMock.mockResolvedValueOnce(new Response('{"items":[]}', {
      status, headers: { 'content-type': 'application/json' },
    }));
    await expect(api.getCases()).rejects.toMatchObject({ code: 'invalid_response', status });
  });

  it('rejects a JSON-looking body with the wrong media type', async () => {
    const api = await client();
    fetchMock.mockResolvedValueOnce(new Response('{"items":[]}', {
      headers: { 'content-type': 'text/plain' },
    }));
    await expect(api.getCases()).rejects.toMatchObject({ code: 'invalid_response' });
  });

  it('distinguishes a connection lost during body reading from invalid JSON', async () => {
    const api = await client();
    const response = empty();
    vi.spyOn(response, 'json').mockRejectedValueOnce(new TypeError('PRIVATE_CONNECTION_LOST'));
    fetchMock.mockResolvedValueOnce(response);
    await expect(api.getCases()).rejects.toMatchObject({ code: 'network_error' });
  });
});
