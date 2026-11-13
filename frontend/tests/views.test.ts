import { afterEach, beforeEach, expect, it, vi } from 'vitest';

const NOTICE = 'Demonstracioni podaci — sintetički skor, bez ML predikcije';
const DETAILS = [0.75, 0.4, 0.1].map((score, index) => {
  const suffix = String(index + 1).padStart(3, '0');
  return {
    case_id: `CASE-${suffix}`,
    transaction: {
      transaction_id: `TX-${suffix}`, occurred_at: '2026-01-01T10:00:00Z',
      sender_account: `DEMO-SENDER:${suffix}`, receiver_account: `DEMO-RECEIVER:${suffix}`,
      amount: `${1250 * (index + 1)}.00`, currency: 'EUR',
    },
    risk_assessment: {
      transaction_id: `TX-${suffix}`, score, source: 'fixture', scorer_version: 'fixture-v1',
      scored_at: '2026-01-01T10:00:00Z',
      explanation: `Illustrative synthetic score for CASE-${suffix}; no ML inference performed.`,
    },
  };
});
const LIST = {
  items: DETAILS.map(detail => ({
    case_id: detail.case_id, transaction_id: detail.transaction.transaction_id,
    score: detail.risk_assessment.score, score_source: 'fixture',
  })),
};
const fetchMock = vi.fn<typeof fetch>();
const entryModules = import.meta.glob('../src/main.ts');
let root: HTMLElement;

beforeEach(() => {
  vi.resetModules();
  fetchMock.mockReset();
  vi.stubGlobal('fetch', fetchMock);
  document.body.innerHTML = '<main id="app"></main>';
  root = document.querySelector<HTMLElement>('#app')!;
  window.history.replaceState({}, '', '/');
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  document.body.replaceChildren();
});

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status, headers: { 'content-type': 'application/json' },
  });
}

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason: unknown) => void;
  const promise = new Promise<T>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, resolve, reject };
}

function serveCases(overrides: Record<string, () => Promise<Response>> = {}) {
  fetchMock.mockImplementation(input => {
    const url = input instanceof Request ? input.url : String(input);
    const path = new URL(url, window.location.origin).pathname;
    if (overrides[path]) return overrides[path]();
    if (path === '/api/cases') return Promise.resolve(jsonResponse(LIST));
    const detail = DETAILS.find(item => path === `/api/cases/${item.case_id}`);
    if (detail) return Promise.resolve(jsonResponse(detail));
    if (path.startsWith('/api/cases/')) {
      return Promise.resolve(jsonResponse({
        error: { code: 'case_not_found', message: 'Case not found.' },
      }, 404));
    }
    return Promise.reject(new Error(`Unexpected test request: ${path}`));
  });
}

async function mount() {
  // Exercise the actual existing entry point; do not add a fake mount/view module.
  // Glob loading also supports the current TypeScript script with no exports.
  const load = entryModules['../src/main.ts'];
  expect(load, 'Missing existing application entry point').toBeTypeOf('function');
  await load();
}

function text(): string {
  return (root.textContent ?? '').replace(/\s+/g, ' ').trim();
}

function visible(element: HTMLElement): boolean {
  let current: HTMLElement | null = element;
  while (current) {
    const style = getComputedStyle(current);
    if (current.hidden || current.getAttribute('aria-hidden') === 'true' ||
        style.display === 'none' || style.visibility === 'hidden') return false;
    if (current === root) return true;
    current = current.parentElement;
  }
  return false;
}

function expectNotice() {
  const notice = [...root.querySelectorAll<HTMLElement>('*')].find(element =>
    (element.textContent ?? '').replace(/\s+/g, ' ').trim() === NOTICE && visible(element));
  expect(notice, 'Missing visible synthetic/illustrative data notice').toBeDefined();
}

function findControl(name: RegExp): HTMLElement | undefined {
  return [...root.querySelectorAll<HTMLElement>('button, a, [role="button"]')].find(element => {
    const label = element.getAttribute('aria-label') ?? element.textContent ?? '';
    return visible(element) && name.test(label);
  });
}

function clickControl(name: RegExp) {
  const element = findControl(name);
  expect(element, `Missing visible control matching ${name}`).toBeDefined();
  element!.click();
}

async function selectCase(caseId: string) {
  const name = new RegExp(caseId);
  // Both a persistent list and a detail/back/list layout satisfy the story.
  if (!findControl(name)) {
    clickControl(/nazad|back|lista/i);
    await vi.waitFor(() => expect(findControl(name)).toBeDefined(), { timeout: 300 });
  }
  clickControl(name);
}

async function expectList() {
  await vi.waitFor(() => {
    for (const item of LIST.items) {
      expect(findControl(new RegExp(item.case_id)), `Missing case selection ${item.case_id}`)
        .toBeDefined();
    }
  }, { timeout: 300, interval: 10 });
}

async function expectDetail(index: number) {
  const detail = DETAILS[index];
  await vi.waitFor(() => {
    expect(text()).toContain(detail.transaction.sender_account);
    expect(text()).toContain(detail.transaction.receiver_account);
    expect(text()).toContain(detail.risk_assessment.explanation);
  }, { timeout: 300, interval: 10 });
  expect(text()).toContain(detail.case_id);
  expect(text()).toContain(detail.transaction.transaction_id);
  expectNotice();
}

async function drainResponses() {
  // A real turn drains fetch/body microtasks after a deliberately late result.
  await new Promise<void>(resolve => setTimeout(resolve, 0));
}

async function expectRequested(path: string) {
  await vi.waitFor(() => {
    expect(fetchMock.mock.calls.some(([input]) => {
      const url = input instanceof Request ? input.url : String(input);
      return new URL(url, window.location.origin).pathname === path;
    }), `Missing fetch for ${path}`).toBe(true);
  }, { timeout: 300, interval: 10 });
}

it('shows loading and the synthetic notice while the initial list request is pending', async () => {
  const pending = deferred<Response>();
  serveCases({ '/api/cases': () => pending.promise });
  await mount();
  const status = root.querySelector('[role="status"]');
  expect(status, 'Missing list loading state').not.toBeNull();
  expect(status!.textContent).toMatch(/učit|ucit|loading/i);
  expectNotice();
  expect(text()).not.toContain(DETAILS[0].transaction.sender_account);
  pending.resolve(jsonResponse(LIST));
  await expectList();
});

it('renders three selectable synthetic cases and their returned scores', async () => {
  serveCases();
  await mount();
  await expectList();
  expectNotice();
  for (const item of LIST.items) {
    expect(text()).toContain(item.case_id);
    const score = String(item.score).replace('.', '[.,]');
    expect(text()).toMatch(new RegExp(`${score}|${Math.round(item.score * 100)}\\s*%`));
  }
});

it('shows an explicit empty state without fabricated cases', async () => {
  serveCases({ '/api/cases': async () => jsonResponse({ items: [] }) });
  await mount();
  await vi.waitFor(() => expect(text()).toMatch(/nema|prazn|empty/i), { timeout: 300 });
  expectNotice();
  for (const detail of DETAILS) expect(text()).not.toContain(detail.case_id);
});

it.each(['network', 'http500'])('shows a controlled %s error with retry and no private message', async kind => {
  serveCases({
    '/api/cases': async () => {
      if (kind === 'network') throw new TypeError('PRIVATE_NETWORK_ERROR C:\\private\\cases.json');
      return jsonResponse({ error: { code: 'internal_error', message: 'PRIVATE_SERVER_ERROR' } }, 500);
    },
  });
  await mount();
  await vi.waitFor(() => expect(root.querySelector('[role="alert"]')).not.toBeNull(), { timeout: 300 });
  expect(text()).toMatch(/grešk|gresk|nedostup|neuspe|error|unavailable/i);
  expect(findControl(/ponovo|ponovi|retry/i)).toBeDefined();
  expect(text()).not.toMatch(/PRIVATE_|C:\\private|TypeError/);
  expectNotice();
  for (const detail of DETAILS) expect(text()).not.toContain(detail.transaction.sender_account);
});

it('retries the failed list request and renders the recovered cases', async () => {
  let attempts = 0;
  serveCases({ '/api/cases': async () => {
    if (++attempts === 1) throw new TypeError('Unavailable');
    return jsonResponse(LIST);
  } });
  await mount();
  await vi.waitFor(() => expect(findControl(/ponovo|ponovi|retry/i)).toBeDefined(), { timeout: 300 });
  clickControl(/ponovo|ponovi|retry/i);
  await expectList();
  expect(attempts).toBe(2);
  expect(root.querySelector('[role="alert"]')).toBeNull();
});

it.each([0, 1, 2])('selects case index %i, displays its detail, and returns to the list', async index => {
  serveCases();
  await mount();
  await expectList();
  await selectCase(DETAILS[index].case_id);
  await expectDetail(index);
  clickControl(/nazad|back|lista/i);
  await expectList();
  expect(text()).not.toContain(DETAILS[index].transaction.sender_account);
  expectNotice();
});

it('shows detail loading instead of presenting invented or previous details', async () => {
  const pending = deferred<Response>();
  serveCases({ '/api/cases/CASE-001': () => pending.promise });
  await mount();
  await expectList();
  await selectCase('CASE-001');
  await vi.waitFor(() => {
    expect(root.querySelector('[role="status"]')?.textContent).toMatch(/učit|ucit|loading/i);
  }, { timeout: 300 });
  expect(text()).not.toContain(DETAILS[0].transaction.sender_account);
  expectNotice();
  pending.resolve(jsonResponse(DETAILS[0]));
  await expectDetail(0);
});

it('shows not-found for a case that disappeared after the list loaded', async () => {
  const unknown = { ...LIST.items[0], case_id: 'CASE-999', transaction_id: 'TX-999' };
  serveCases({ '/api/cases': async () => jsonResponse({ items: [unknown] }) });
  await mount();
  await vi.waitFor(() => expect(findControl(/CASE-999/)).toBeDefined(), { timeout: 300 });
  await selectCase('CASE-999');
  await vi.waitFor(() => expect(text()).toMatch(/nije pronađen|nije pronadjen|ne postoji|not found/i),
    { timeout: 300 });
  expectNotice();
  for (const detail of DETAILS) expect(text()).not.toContain(detail.transaction.sender_account);
});

it('retries the selected detail after a failure without changing the selected case', async () => {
  let attempts = 0;
  serveCases({ '/api/cases/CASE-002': async () => {
    if (++attempts === 1) return jsonResponse({ error: { code: 'internal_error', message: 'Unavailable.' } }, 500);
    return jsonResponse(DETAILS[1]);
  } });
  await mount();
  await expectList();
  await selectCase('CASE-002');
  await vi.waitFor(() => expect(findControl(/ponovo|ponovi|retry/i)).toBeDefined(), { timeout: 300 });
  clickControl(/ponovo|ponovi|retry/i);
  await expectDetail(1);
  expect(attempts).toBe(2);
});

it('clears old detail immediately when a different case is selected', async () => {
  const pending = deferred<Response>();
  serveCases({ '/api/cases/CASE-002': () => pending.promise });
  await mount();
  await expectList();
  await selectCase('CASE-001');
  await expectDetail(0);
  await selectCase('CASE-002');
  expect(text()).not.toContain(DETAILS[0].transaction.sender_account);
  expect(text()).not.toContain(DETAILS[0].risk_assessment.explanation);
  pending.resolve(jsonResponse(DETAILS[1]));
  await expectDetail(1);
});

it('ignores an older success arriving after the newly selected case has rendered', async () => {
  const older = deferred<Response>();
  const newer = deferred<Response>();
  // Deliberately ignore AbortSignal: stale-result protection must still work
  // when a transport completes despite cancellation.
  serveCases({ '/api/cases/CASE-001': () => older.promise, '/api/cases/CASE-002': () => newer.promise });
  await mount();
  await expectList();
  await selectCase('CASE-001');
  await expectRequested('/api/cases/CASE-001');
  await selectCase('CASE-002');
  await expectRequested('/api/cases/CASE-002');
  newer.resolve(jsonResponse(DETAILS[1]));
  await expectDetail(1);
  older.resolve(jsonResponse(DETAILS[0]));
  await drainResponses();
  await expectDetail(1);
  expect(text()).not.toContain(DETAILS[0].transaction.sender_account);
  expect(text()).not.toContain(DETAILS[0].risk_assessment.explanation);
});

it('ignores an older response while the new case is still loading', async () => {
  const older = deferred<Response>();
  const newer = deferred<Response>();
  serveCases({ '/api/cases/CASE-001': () => older.promise, '/api/cases/CASE-003': () => newer.promise });
  await mount();
  await expectList();
  await selectCase('CASE-001');
  await expectRequested('/api/cases/CASE-001');
  await selectCase('CASE-003');
  await expectRequested('/api/cases/CASE-003');
  older.resolve(jsonResponse(DETAILS[0]));
  await drainResponses();
  expect(text()).not.toContain(DETAILS[0].transaction.sender_account);
  expect(text()).not.toContain(DETAILS[0].risk_assessment.explanation);
  expect(root.querySelector('[role="status"]')?.textContent).toMatch(/učit|ucit|loading/i);
  newer.resolve(jsonResponse(DETAILS[2]));
  await expectDetail(2);
});

it('ignores an older failure instead of replacing the current successful detail', async () => {
  const older = deferred<Response>();
  serveCases({ '/api/cases/CASE-001': () => older.promise });
  await mount();
  await expectList();
  await selectCase('CASE-001');
  await expectRequested('/api/cases/CASE-001');
  await selectCase('CASE-002');
  await expectDetail(1);
  older.reject(new TypeError('PRIVATE_LATE_ERROR'));
  await drainResponses();
  await expectDetail(1);
  expect(root.querySelector('[role="alert"]')).toBeNull();
  expect(text()).not.toContain('PRIVATE_LATE_ERROR');
});

it('keeps the list visible when an abandoned detail completes after back navigation', async () => {
  const pending = deferred<Response>();
  serveCases({ '/api/cases/CASE-001': () => pending.promise });
  await mount();
  await expectList();
  await selectCase('CASE-001');
  await expectRequested('/api/cases/CASE-001');
  clickControl(/nazad|back|lista/i);
  await expectList();
  pending.resolve(jsonResponse(DETAILS[0]));
  await drainResponses();
  await expectList();
  expect(text()).not.toContain(DETAILS[0].transaction.sender_account);
});

it('shows invalid server data as an error instead of a fallback case or zero score', async () => {
  serveCases({ '/api/cases/CASE-001': async () => jsonResponse({
    ...DETAILS[0], risk_assessment: { ...DETAILS[0].risk_assessment, score: null },
  }) });
  await mount();
  await expectList();
  await selectCase('CASE-001');
  await vi.waitFor(() => expect(root.querySelector('[role="alert"]')).not.toBeNull(), { timeout: 300 });
  expect(text()).not.toContain(DETAILS[0].transaction.sender_account);
  expect(text()).not.toContain(DETAILS[0].risk_assessment.explanation);
});

it('renders transaction text literally without treating returned strings as HTML', async () => {
  const literal = '<img src=x onerror="window.privateMarker=true">';
  serveCases({ '/api/cases/CASE-001': async () => jsonResponse({
    ...DETAILS[0], transaction: { ...DETAILS[0].transaction, sender_account: literal },
  }) });
  await mount();
  await expectList();
  await selectCase('CASE-001');
  await vi.waitFor(() => expect(text()).toContain(literal), { timeout: 300 });
  expect(root.querySelector('img')).toBeNull();
});
