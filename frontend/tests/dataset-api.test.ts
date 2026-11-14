import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { getCase, getCases } from '../src/api';
import { DETAIL_V2, LIST_V2 } from './dataset-fixture';

const fetchMock = vi.fn<typeof fetch>();
function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status, headers: { 'content-type': 'application/json' },
  });
}
beforeEach(() => { fetchMock.mockReset(); vi.stubGlobal('fetch', fetchMock); });
afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks(); });

it('uses relative URLs and pins exact encoded v2 snapshot and case identity', async () => {
  fetchMock.mockResolvedValueOnce(json(LIST_V2)).mockResolvedValueOnce(json(DETAIL_V2));
  expect(await getCases()).toEqual(LIST_V2);
  expect(await getCase(DETAIL_V2.case_id, { snapshot: 'run_test_1' })).toEqual(DETAIL_V2);
  expect(fetchMock.mock.calls[0][0]).toBe('/api/cases');
  expect(fetchMock.mock.calls[1][0])
    .toBe(`/api/cases/${DETAIL_V2.case_id}?snapshot=run_test_1`);
});

it('rejects mismatched detail and controlled stale/unavailable errors', async () => {
  fetchMock.mockResolvedValueOnce(json({ ...DETAIL_V2, snapshot_ref: 'run_other' }));
  await expect(getCase(DETAIL_V2.case_id, { snapshot: 'run_test_1' }))
    .rejects.toMatchObject({ code: 'invalid_response' });
  fetchMock.mockResolvedValueOnce(json({ error: {
    code: 'stale_snapshot', message: 'private server text',
  } }, 409));
  await expect(getCase(DETAIL_V2.case_id, { snapshot: 'run_test_1' }))
    .rejects.toMatchObject({ code: 'stale_snapshot', status: 409 });
  fetchMock.mockResolvedValueOnce(json({ error: {
    code: 'run_unavailable', message: 'private server text',
  } }, 503));
  await expect(getCases({ dataset: true }))
    .rejects.toMatchObject({ code: 'run_unavailable', status: 503 });
  fetchMock.mockResolvedValueOnce(json({ error: {
    code: 'run_unavailable', message: 'private server text',
  } }, 503));
  await expect(getCases()).rejects.toMatchObject({ code: 'invalid_response' });
});
