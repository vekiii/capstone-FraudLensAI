import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { mountCaseApp } from '../src/main';
import type { CaseClient } from '../src/main';
import type { CaseDetail } from '../src/contracts';

const details: CaseDetail[] = [1, 2].map(index => ({
  case_id: `CASE-00${index}`,
  transaction: {
    transaction_id: `TX-00${index}`, occurred_at: '2026-01-01T10:00:00Z',
    sender_account: `DEMO-SENDER:${index}`, receiver_account: `DEMO-RECEIVER:${index}`,
    amount: '10.00', currency: 'EUR',
  },
  risk_assessment: {
    transaction_id: `TX-00${index}`, score: 0.4, source: 'fixture',
    scorer_version: 'fixture-v1', scored_at: '2026-01-01T10:00:00Z',
    explanation: `Illustrative case ${index}.`,
  },
}));
let root: HTMLElement;
let dispose: (() => void) | undefined;

beforeEach(() => {
  root = document.createElement('main');
  document.body.append(root);
});
afterEach(() => {
  dispose?.();
  dispose = undefined;
  document.body.replaceChildren();
});

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason: unknown) => void;
  const promise = new Promise<T>((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

function client(getCase: CaseClient['getCase']): CaseClient {
  return {
    getCases: async () => ({ items: details.map(detail => ({
      case_id: detail.case_id, transaction_id: detail.transaction.transaction_id,
      score: detail.risk_assessment.score, score_source: detail.risk_assessment.source,
    })).reverse() }),
    getCase,
  };
}

function control(label: string): HTMLButtonElement {
  const node = [...root.querySelectorAll('button')].find(button =>
    button.getAttribute('aria-label') === label || button.textContent === label);
  expect(node).toBeDefined();
  return node!;
}

async function mounted(api: CaseClient) {
  dispose = mountCaseApp(root, api);
  await vi.waitFor(() => expect(root.querySelectorAll('.case-choice')).toHaveLength(2));
}

it('orders cases, marks selection accessibly, and restores focus on back', async () => {
  await mounted(client(async () => details[0]));
  expect([...root.querySelectorAll('.case-choice')].map(button => button.getAttribute('aria-label')))
    .toEqual(['Otvori CASE-001', 'Otvori CASE-002']);
  control('Otvori CASE-001').click();
  await vi.waitFor(() => expect(root.textContent).toContain('DEMO-SENDER:1'));
  expect(control('Otvori CASE-001').getAttribute('aria-pressed')).toBe('true');
  expect(document.activeElement?.id).toBe('panel-title');
  control('← Nazad na listu').click();
  expect(document.activeElement).toBe(control('Otvori CASE-001'));
});

it.each(['success', 'failure'])('ignores stale client %s even when the client ignores abort', async kind => {
  const late = deferred<CaseDetail>();
  let oldSignal: AbortSignal | undefined;
  await mounted(client((id, { signal }) => {
    if (id === 'CASE-001') { oldSignal = signal; return late.promise; }
    return Promise.resolve(details[1]);
  }));
  control('Otvori CASE-001').click();
  control('Otvori CASE-002').click();
  expect(oldSignal?.aborted).toBe(true);
  await vi.waitFor(() => expect(root.textContent).toContain('DEMO-SENDER:2'));
  if (kind === 'success') late.resolve(details[0]);
  else late.reject(new Error('PRIVATE_LATE_ERROR'));
  await new Promise(resolve => setTimeout(resolve, 0));
  expect(root.textContent).toContain('DEMO-SENDER:2');
  expect(root.textContent).not.toMatch(/DEMO-SENDER:1|PRIVATE/);
  expect(root.querySelector('[role="alert"]')).toBeNull();
});

it('invalidates and cancels pending detail on back and disposal', async () => {
  const late = deferred<CaseDetail>();
  const signals: AbortSignal[] = [];
  await mounted(client((_id, { signal }) => { signals.push(signal); return late.promise; }));
  control('Otvori CASE-001').click();
  control('← Nazad na listu').click();
  expect(signals[0].aborted).toBe(true);
  control('Otvori CASE-002').click();
  dispose?.();
  expect(signals[1].aborted).toBe(true);
  late.resolve(details[0]);
  await new Promise(resolve => setTimeout(resolve, 0));
  expect(root.childElementCount).toBe(0);
});
