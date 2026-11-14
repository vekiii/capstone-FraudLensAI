import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { ApiError } from '../src/api';
import { decodeCaseDetailV2, decodeCaseListV2 } from '../src/contracts';
import { mountCaseApp } from '../src/main';
import { DETAIL_V2, LIST_V2 } from './dataset-fixture';

let root: HTMLElement;
let dispose: (() => void) | undefined;
beforeEach(() => { root = document.createElement('main'); document.body.append(root); });
afterEach(() => { dispose?.(); document.body.replaceChildren(); });

it('preserves server v2 order and carries list snapshot into detail', async () => {
  const newer = { ...LIST_V2.items[0], case_id: `C${'2'.repeat(32)}`,
    transaction_id: `D${'2'.repeat(32)}`, event_time: '2022-09-11T10:00:00Z' };
  const list = decodeCaseListV2({ ...LIST_V2, total_alerts: 2, displayed_count: 2,
    selected_time_range: { from: LIST_V2.items[0].event_time, to: newer.event_time },
    items: [LIST_V2.items[0], newer] });
  const getCase = vi.fn(async (_caseId: string,
    _options: { signal: AbortSignal; snapshot?: string }) => decodeCaseDetailV2(DETAIL_V2));
  dispose = mountCaseApp(root, { getCases: async () => list, getCase });
  await vi.waitFor(() => expect(root.querySelectorAll('.case-choice')).toHaveLength(2));
  expect([...root.querySelectorAll('.case-choice')].map(item => item.getAttribute('aria-label')))
    .toEqual([`Otvori ${LIST_V2.items[0].case_id}`, `Otvori ${newer.case_id}`]);
  root.querySelector<HTMLButtonElement>('.case-choice')!.click();
  await vi.waitFor(() => expect(getCase).toHaveBeenCalled());
  expect(getCase.mock.calls[0][1]).toMatchObject({ snapshot: 'run_test_1' });
  await vi.waitFor(() => expect(root.textContent).toContain('1250.000 Australian Dollar'));
  expect(root.textContent).toContain('US Dollar');
  expect(root.textContent).toContain('2026-11-14T13:00:00Z');
  expect(root.textContent).toContain('rules');
  expect(root.textContent).not.toContain('bez ML predikcije');
});

it('offers explicit list refresh on stale detail and keeps old detail out', async () => {
  const getCases = vi.fn(async () => decodeCaseListV2(LIST_V2));
  const getCase = vi.fn(async (_caseId: string,
    _options: { signal: AbortSignal; snapshot?: string }) => {
    throw new ApiError('stale_snapshot', 409);
  });
  dispose = mountCaseApp(root, { getCases, getCase });
  await vi.waitFor(() => expect(root.querySelector('.case-choice')).not.toBeNull());
  root.querySelector<HTMLButtonElement>('.case-choice')!.click();
  await vi.waitFor(() => expect(root.textContent).toContain('Osvježite listu'));
  expect(root.textContent).not.toContain('1250.000 Australian Dollar');
  const refresh = [...root.querySelectorAll('button')].find(button =>
    button.textContent?.includes('Osvježi listu'));
  expect(refresh).toBeDefined();
  refresh!.click();
  await vi.waitFor(() => expect(getCases).toHaveBeenCalledTimes(2));
});

it('shows exact zero-alert empty state and unavailable error separately', async () => {
  const empty = decodeCaseListV2({ ...LIST_V2, total_alerts: 0, displayed_count: 0, items: [],
    selected_time_range: { from: null, to: null } });
  dispose = mountCaseApp(root, { getCases: async () => empty,
    getCase: async () => decodeCaseDetailV2(DETAIL_V2) });
  await vi.waitFor(() => expect(root.textContent).toContain('0'));
  expect(root.textContent).toContain('Nema');
});
