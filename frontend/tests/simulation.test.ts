import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { mountSimulation, type SimulationClient } from '../src/simulation';

// Authored public-wire examples, not fetched HTTP responses or a fake renderer.
const scenario = {
  scenario_id: 'review-capacity-demo', scenario_version: 1,
  content_sha256: '894136f422d013cf0d1d52820acf26e3a3a95076a4b8ab044c4e24faf4105198',
  title: 'Review capacity demo',
  source: { kind: 'bundled_synthetic', data_version: 'authored-v1', time_basis: 'Authored UTC' },
  score_provenance: { source: 'fixture', score_kind: 'illustrative_score', scorer_version: 'illustrative-v1' },
  assumptions: [{ id: 'w', description: 'Equal synthetic weights' }, { id: 'd', description: 'Authored review minutes' }],
  horizon: { starts_at: '2026-01-01T00:00:00Z', ends_at: '2026-01-01T01:00:00Z' },
  window_starts: ['2026-01-01T00:00:00Z'], generation_seed: null,
  defaults: { score_threshold: '0.30', budget_minutes_per_window: 2 },
};
const catalog = { contract_version: 1, items: [scenario] };
const recipe = {
  contract_version: 1,
  scenario: { scenario_id: scenario.scenario_id, scenario_version: 1, content_sha256: scenario.content_sha256 },
  score_threshold: '0.30', budget_minutes_per_window: 2,
  strategy_versions: { fifo: 1, highest_score: 1, weighted_score_per_minute: 1 },
};
const comparison = {
  contract_version: 1, recipe: { ...recipe, score_threshold: '0.3' }, scenario,
  admitted_alerts: ['A', 'B', 'C', 'E'].map((id, i) => ({
    alert_id: id, available_at: '2026-01-01T00:00:00Z', score: ['0.40', '0.90', '0.80', '0.80'][i],
    weight: '1', estimated_review_minutes: i < 2 ? 2 : 1,
    weight_assumption_id: 'w', duration_assumption_id: 'd',
  })),
  strategies: [
    { strategy_id: 'fifo', windows: [{ starts_at: scenario.window_starts[0], ranked_alert_ids: ['A', 'B', 'C', 'E'], reviewed_alert_ids: ['A'], used_minutes: 2 }],
      pending_alert_ids: ['B', 'C', 'E'], counts: { reviewed: 1, backlog: 3, unknown_in_horizon: 0, unknown_reviewed: 0,
        outcomes: { positives_found: 0, positives_missed: 3, positives_missed_threshold: 1, positives_missed_backlog: 2, reviewed_negatives: 1 } } },
    { strategy_id: 'highest_score', windows: [{ starts_at: scenario.window_starts[0], ranked_alert_ids: ['B', 'C', 'E', 'A'], reviewed_alert_ids: ['B'], used_minutes: 2 }],
      pending_alert_ids: ['A', 'C', 'E'], counts: { reviewed: 1, backlog: 3, unknown_in_horizon: 0, unknown_reviewed: 0,
        outcomes: { positives_found: 1, positives_missed: 2, positives_missed_threshold: 1, positives_missed_backlog: 1, reviewed_negatives: 0 } } },
    { strategy_id: 'weighted_score_per_minute', windows: [{ starts_at: scenario.window_starts[0], ranked_alert_ids: ['C', 'E', 'B', 'A'], reviewed_alert_ids: ['C', 'E'], used_minutes: 2 }],
      pending_alert_ids: ['A', 'B'], counts: { reviewed: 2, backlog: 2, unknown_in_horizon: 0, unknown_reviewed: 0,
        outcomes: { positives_found: 1, positives_missed: 2, positives_missed_threshold: 1, positives_missed_backlog: 1, reviewed_negatives: 1 } } },
  ],
};

let root: HTMLElement;
let client: SimulationClient;
let dispose: (() => void) | undefined;
beforeEach(() => {
  root = document.createElement('main'); document.body.append(root);
  client = { listScenarios: vi.fn().mockResolvedValue(structuredClone(catalog)), compare: vi.fn().mockResolvedValue(structuredClone(comparison)) };
});
afterEach(() => {
  dispose?.(); dispose = undefined; document.body.replaceChildren();
  vi.restoreAllMocks(); vi.unstubAllGlobals();
});

async function mount() {
  dispose = mountSimulation(root, client);
  await vi.waitFor(() => expect(client.listScenarios).toHaveBeenCalled(), { timeout: 200 });
}
async function run() {
  await mount();
  const select = root.querySelector('select');
  expect(select).toBeInstanceOf(HTMLSelectElement);
  select!.value = scenario.scenario_id;
  select!.dispatchEvent(new Event('change', { bubbles: true }));
  const button = root.querySelector<HTMLButtonElement>('[data-simulation-run]');
  expect(button).toBeInstanceOf(HTMLButtonElement);
  button!.click();
}
async function errorWithoutResults() {
  await vi.waitFor(() => {
    const alert = root.querySelector('[role="alert"]');
    expect(alert).not.toBeNull();
    expect(alert!.textContent!.trim().length).toBeGreaterThan(5);
    expect(root.querySelector('[data-simulation-results]')).toBeNull();
    expect(root.textContent).not.toContain('PRIVATE');
  }, { timeout: 200 });
}

it('opens Simulation & Evaluation with a selectable scenario', async () => {
  await mount();
  expect(root.querySelector('h1,h2')?.textContent).toMatch(/Simulation.*Evaluation/i);
  expect(root.querySelector('option')?.textContent).toContain(scenario.title);
});
it('shows synthetic source, score provenance and authored assumptions', async () => {
  await mount();
  for (const text of ['bundled_synthetic', 'illustrative_score', 'illustrative-v1', 'Authored UTC', 'Equal synthetic weights', 'Authored review minutes']) {
    expect(root.textContent).toContain(text);
  }
});
it('submits catalog defaults as a closed first comparison recipe', async () => {
  await run();
  await vi.waitFor(() => expect(vi.mocked(client.compare).mock.calls[0]?.[0]).toEqual(recipe), { timeout: 200 });
});
it('renders three strategy results in contract order with exact selections and counts', async () => {
  await run();
  await vi.waitFor(() => {
    const rows = [...root.querySelectorAll('[data-strategy-id]')];
    expect(rows.map(r => r.getAttribute('data-strategy-id'))).toEqual(['fifo', 'highest_score', 'weighted_score_per_minute']);
    for (const [i, row] of rows.entries()) {
      expect(row.querySelector('[data-reviewed-alerts]')?.textContent?.replace(/\s/g, '')).toBe(['A', 'B', 'C,E'][i]);
      expect(row.querySelector('[data-positives-found]')?.textContent).toBe(['0', '1', '1'][i]);
      expect(row.querySelector('[data-backlog]')?.textContent).toBe(['3', '3', '2'][i]);
    }
  }, { timeout: 200 });
});
it('rejects malformed catalog instead of trusting the fake client', async () => {
  vi.mocked(client.listScenarios).mockResolvedValue({ contract_version: 1, items: [{ ...scenario, unexpected: true }] });
  dispose = mountSimulation(root, client);
  await errorWithoutResults();
});
it('shows readable catalog request failure with no comparison', async () => {
  vi.mocked(client.listScenarios).mockRejectedValue(new Error('PRIVATE network internals'));
  dispose = mountSimulation(root, client);
  await errorWithoutResults();
});
it('rejects malformed comparison with no results', async () => {
  vi.mocked(client.compare).mockResolvedValue({ ...comparison, strategies: [] });
  await run();
  await errorWithoutResults();
});
it('shows readable comparison request failure with no results', async () => {
  vi.mocked(client.compare).mockRejectedValue(new Error('PRIVATE network internals'));
  await run();
  await errorWithoutResults();
});

type Setting = 'score_threshold' | 'budget_minutes_per_window';

function setting(name: Setting): HTMLInputElement {
  const input = root.querySelector<HTMLInputElement>(`input[name="${name}"]`);
  expect(input, name).toBeInstanceOf(HTMLInputElement);
  return input!;
}

function edit(name: Setting, value: string) {
  const input = setting(name);
  input.value = value;
  input.dispatchEvent(new Event('input', { bubbles: true }));
}

function submit() {
  root.querySelector<HTMLButtonElement>('[data-simulation-run]')!.click();
}

function visibleResults() {
  return root.querySelector('[data-simulation-results]');
}

function deferComparison() {
  let resolve!: (value: unknown) => void;
  let reject!: (reason: Error) => void;
  // Deliberately ignore AbortSignal, as a response may already be on its way.
  const response = new Promise<unknown>((accept, fail) => { resolve = accept; reject = fail; });
  vi.mocked(client.compare).mockReturnValueOnce(response);
  return { resolve, reject };
}

function nextTurn() {
  return new Promise<void>(resolve => setTimeout(resolve, 0));
}

it('uses catalog settings and sends the edited threshold as the exact decimal string', async () => {
  await mount();
  expect(setting('score_threshold').value).toBe('0.30');
  expect(setting('budget_minutes_per_window').value).toBe('2');
  const threshold = '0.30000000000000000000000001';
  const edited = { ...recipe, score_threshold: `${threshold}00` };
  vi.mocked(client.compare).mockResolvedValueOnce({ ...comparison, recipe: { ...edited, score_threshold: threshold } });
  edit('score_threshold', edited.score_threshold);
  submit();
  expect(vi.mocked(client.compare).mock.calls[0]?.[0]).toEqual(edited);
  await vi.waitFor(() => expect(visibleResults()).not.toBeNull());
});

it('rejects a returned recipe for a different threshold even when both round to the same number', async () => {
  await mount();
  edit('score_threshold', '0.30000000000000000000000001');
  submit();
  await errorWithoutResults();
});

it('sends zero minutes as a numeric budget and renders the new backlog and distinct miss reasons', async () => {
  await run();
  await vi.waitFor(() => expect(visibleResults()).not.toBeNull());
  const zeroBudget = { ...recipe, budget_minutes_per_window: 0 };
  vi.mocked(client.compare).mockResolvedValueOnce({
    ...comparison, recipe: zeroBudget,
    strategies: comparison.strategies.map(row => ({
      ...row, windows: row.windows.map(w => ({ ...w, reviewed_alert_ids: [], used_minutes: 0 })),
      pending_alert_ids: ['A', 'B', 'C', 'E'], counts: {
        ...row.counts, reviewed: 0, backlog: 4,
        outcomes: { positives_found: 0, positives_missed: 3, positives_missed_threshold: 1, positives_missed_backlog: 2, reviewed_negatives: 0 },
      },
    })),
  });
  edit('budget_minutes_per_window', '0');
  expect(visibleResults()).toBeNull();
  submit();
  expect(vi.mocked(client.compare).mock.calls[1]?.[0]).toEqual(zeroBudget);
  await vi.waitFor(() => {
    const row = visibleResults()?.querySelector('[data-strategy-id="fifo"]');
    expect(row?.querySelector('[data-positives-found]')?.textContent).toBe('0');
    expect(row?.querySelector('[data-missed-threshold]')?.textContent).toBe('1');
    expect(row?.querySelector('[data-missed-backlog]')?.textContent).toBe('2');
    expect(row?.querySelector('[data-backlog]')?.textContent).toBe('4');
  });
});

it.each([
  ['score_threshold', ''], ['score_threshold', '1.00000000000000000001'],
  ['score_threshold', '-0.1'], ['score_threshold', '3e-1'], ['score_threshold', 'NaN'],
  ['score_threshold', `0.${'0'.repeat(127)}`],
  ['budget_minutes_per_window', ''], ['budget_minutes_per_window', '-1'],
  ['budget_minutes_per_window', '1.5'], ['budget_minutes_per_window', '2e0'],
  ['budget_minutes_per_window', '9007199254740992'],
] as const)('rejects invalid %s value %s locally', async (name, value) => {
  await run();
  await vi.waitFor(() => expect(visibleResults()).not.toBeNull());
  edit(name, value);
  expect(visibleResults()).toBeNull();
  submit();
  await errorWithoutResults();
  expect(setting(name).getAttribute('aria-invalid')).toBe('true');
  expect(client.compare).toHaveBeenCalledTimes(1);
});

it.each(['empty', 'partial', 'unlabeled'] as const)('renders %s outcomes distinctly', async coverage => {
  const empty = coverage === 'empty';
  const unlabeled = coverage === 'unlabeled';
  vi.mocked(client.compare).mockResolvedValueOnce({
    ...comparison, admitted_alerts: empty ? [] : comparison.admitted_alerts,
    strategies: comparison.strategies.map(row => ({
      ...row,
      windows: empty ? row.windows.map(w => ({ ...w, ranked_alert_ids: [], reviewed_alert_ids: [], used_minutes: 0 })) : row.windows,
      pending_alert_ids: empty ? [] : row.pending_alert_ids,
      counts: {
        reviewed: empty ? 0 : row.counts.reviewed, backlog: empty ? 0 : row.counts.backlog,
        unknown_in_horizon: empty ? 0 : unlabeled ? 5 : 1,
        unknown_reviewed: empty ? 0 : unlabeled ? row.counts.reviewed : Number(row.strategy_id === 'fifo'),
        outcomes: unlabeled ? null : empty ? {
          positives_found: 0, positives_missed: 0, positives_missed_threshold: 0, positives_missed_backlog: 0, reviewed_negatives: 0,
        } : { ...row.counts.outcomes, reviewed_negatives: 0 },
      },
    })),
  });
  await run();
  await vi.waitFor(() => {
    const row = visibleResults()?.querySelector('[data-strategy-id="fifo"]');
    expect(row?.querySelector('[data-positives-found]')?.textContent).toBe(unlabeled ? 'Nedostupno' : '0');
    expect(row?.querySelector('[data-unknown-in-horizon]')?.textContent).toBe(empty ? '0' : unlabeled ? '5' : '1');
    expect(row?.querySelector('[data-unknown-reviewed]')?.textContent).toBe(empty ? '0' : '1');
    if (!empty) expect(visibleResults()?.querySelector('p')?.textContent).toMatch(/oznaka/i);
  });
});

it.each([
  ['score_threshold', '0.4', '0.30'],
  ['budget_minutes_per_window', '4', '2'],
] as const)('cancels the run and ignores a late success after editing %s, even if reverted', async (name, changed, original) => {
  await mount();
  const late = deferComparison();
  submit();
  const signal = vi.mocked(client.compare).mock.calls[0]?.[1]?.signal;
  edit(name, changed);
  edit(name, original);
  expect(signal?.aborted).toBe(true);
  late.resolve(comparison);
  await nextTurn();
  expect(visibleResults()).toBeNull();
  expect(root.querySelector('[role="alert"]')).toBeNull();
  submit();
  await vi.waitFor(() => expect(visibleResults()).not.toBeNull());
});

it('clears displayed results on scenario change, restores defaults and ignores a late failure from the previous scenario', async () => {
  const second = {
    ...scenario, scenario_id: 'second-demo', title: 'Second demo',
    defaults: { score_threshold: '0.7', budget_minutes_per_window: 7 },
  };
  vi.mocked(client.listScenarios).mockResolvedValueOnce({ ...catalog, items: [scenario, second] });
  await run();
  await vi.waitFor(() => expect(visibleResults()).not.toBeNull());
  const select = root.querySelector('select')!;
  const choose = (id: string) => {
    select.value = id;
    select.dispatchEvent(new Event('change', { bubbles: true }));
  };
  choose(second.scenario_id);
  expect(visibleResults()).toBeNull();
  expect(setting('score_threshold').value).toBe('0.7');
  expect(setting('budget_minutes_per_window').value).toBe('7');
  const late = deferComparison();
  submit();
  choose(scenario.scenario_id);
  expect(vi.mocked(client.compare).mock.calls[1]?.[1]?.signal?.aborted).toBe(true);
  submit();
  await vi.waitFor(() => expect(visibleResults()).not.toBeNull());
  late.reject(new Error('Late failure'));
  await nextTurn();
  expect(visibleResults()).not.toBeNull();
  expect(root.querySelector('[role="alert"]')).toBeNull();
});

it('ignores the response of a run replaced by resubmission', async () => {
  await mount();
  const late = deferComparison();
  submit();
  const signal = vi.mocked(client.compare).mock.calls[0]?.[1]?.signal;
  vi.mocked(client.compare).mockRejectedValueOnce(new Error('Current failure'));
  submit();
  expect(client.compare).toHaveBeenCalledTimes(2);
  expect(signal?.aborted).toBe(true);
  await errorWithoutResults();
  late.resolve(comparison);
  await nextTurn();
  expect(visibleResults()).toBeNull();
  expect(root.querySelector('[role="alert"]')).not.toBeNull();
});

it('ignores a late comparison after leaving the simulation view', async () => {
  await mount();
  const late = deferComparison();
  submit();
  dispose?.();
  dispose = undefined;
  root.textContent = 'Cases';
  late.resolve(comparison);
  await nextTurn();
  expect(root.textContent).toBe('Cases');
  expect(visibleResults()).toBeNull();
});

function chooseRecipe(file: File) {
  const input = root.querySelector<HTMLInputElement>('input[type="file"][name="simulation_recipe"]');
  expect(input).toBeInstanceOf(HTMLInputElement);
  Object.defineProperty(input!, 'files', { configurable: true, value: [file] });
  input!.dispatchEvent(new Event('change', { bubbles: true }));
}

function recipeFile(contents: string) {
  return new File([contents], 'comparison.json', { type: 'application/json' });
}

function downloadButton() {
  return root.querySelector<HTMLButtonElement>('[data-simulation-download]');
}

it('downloads only the canonical returned recipe and reopens it after remounting', async () => {
  const createObjectURL = vi.fn((_blob: Blob) => 'blob:recipe');
  const revokeObjectURL = vi.fn();
  vi.stubGlobal('URL', class extends URL {
    static createObjectURL = createObjectURL;
    static revokeObjectURL = revokeObjectURL;
  });
  const downloads: string[] = [];
  vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function (this: HTMLAnchorElement) {
    downloads.push(this.download);
  });
  await run();
  await vi.waitFor(() => expect(visibleResults()).not.toBeNull());
  const before = visibleResults()!.querySelector('table')!.textContent;
  expect(downloadButton()).toBeInstanceOf(HTMLButtonElement);
  downloadButton()!.click();
  expect(downloads).toEqual(['simulation-recipe-review-capacity-demo-v1.json']);
  const blob = createObjectURL.mock.calls[0]?.[0];
  expect(blob.type).toBe('application/json');
  const saved = await blob.text();
  expect(JSON.parse(saved)).toEqual(comparison.recipe);
  await vi.waitFor(() => expect(revokeObjectURL).toHaveBeenCalledWith('blob:recipe'));

  dispose?.();
  await mount();
  chooseRecipe(recipeFile(saved));
  await vi.waitFor(() => {
    expect(client.compare).toHaveBeenLastCalledWith(comparison.recipe, expect.anything());
    expect(visibleResults()?.querySelector('table')?.textContent).toBe(before);
  });
});

it('opens the exact saved revision and decimal instead of substituting the catalog defaults', async () => {
  const revision = { ...scenario, scenario_version: 2, content_sha256: '1'.repeat(64) };
  const saved = {
    ...recipe, scenario: { ...recipe.scenario, scenario_version: 2, content_sha256: revision.content_sha256 },
    score_threshold: '0.3000000000000000000000000100',
  };
  vi.mocked(client.listScenarios).mockResolvedValueOnce({ ...catalog, items: [scenario, revision] });
  vi.mocked(client.compare).mockResolvedValueOnce({
    ...comparison, scenario: revision, recipe: { ...saved, score_threshold: '0.30000000000000000000000001' },
  });
  await mount();
  chooseRecipe(recipeFile(JSON.stringify(saved)));
  await vi.waitFor(() => {
    expect(client.compare).toHaveBeenCalledExactlyOnceWith(saved, expect.anything());
    expect(setting('score_threshold').value).toBe(saved.score_threshold);
    expect(root.querySelector('select')?.selectedIndex).toBe(1);
    expect(visibleResults()?.querySelector('[data-simulation-run-settings]')?.textContent)
      .toContain(revision.content_sha256);
  });
  edit('budget_minutes_per_window', '4');
  expect(visibleResults()).toBeNull();
  expect(downloadButton()).toBeNull();
  expect(client.compare).toHaveBeenCalledTimes(1);
});

it.each([
  ['broken JSON', '{broken'],
  ['extra fields', JSON.stringify({ ...recipe, alerts: [] })],
  ['numeric threshold', JSON.stringify({ ...recipe, score_threshold: 0.3 })],
  ['fractional budget', JSON.stringify({ ...recipe, budget_minutes_per_window: 1.5 })],
  ['unsupported contract', JSON.stringify({ ...recipe, contract_version: 2 })],
  ['invalid strategy version', JSON.stringify({ ...recipe, strategy_versions: { ...recipe.strategy_versions, fifo: 0 } })],
])('rejects a locally invalid recipe with %s and clears previous results', async (_case, saved) => {
  await run();
  await vi.waitFor(() => expect(visibleResults()).not.toBeNull());
  chooseRecipe(recipeFile(saved));
  expect(visibleResults()).toBeNull();
  expect(downloadButton()).toBeNull();
  await errorWithoutResults();
  expect(root.querySelector('[role="alert"]')?.textContent).toMatch(/recept/i);
  expect(client.compare).toHaveBeenCalledTimes(1);
});

it('reports an actual client 409 for the requested recipe and waits for an explicit new run', async () => {
  const unavailable = { ...recipe, strategy_versions: { ...recipe.strategy_versions, fifo: 9 } };
  const posted: unknown[] = [];
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (url, init) => {
    if (url === '/api/simulation/scenarios') return Response.json(catalog);
    expect(url).toBe('/api/simulation/comparisons');
    posted.push(JSON.parse(String(init?.body)));
    return posted.length === 1
      ? Response.json({ error: { code: 'simulation_version_unavailable', message: 'PRIVATE' } }, { status: 409 })
      : Response.json(comparison);
  });
  dispose = mountSimulation(root);
  await vi.waitFor(() => expect(root.querySelector('option')).not.toBeNull());
  chooseRecipe(recipeFile(JSON.stringify(unavailable)));
  await errorWithoutResults();
  expect(root.querySelector('[role="alert"]')?.textContent).toMatch(/verzij.*dostupn/i);
  await nextTurn();
  expect(posted).toEqual([unavailable]);
  expect(downloadButton()).toBeNull();
  submit();
  await vi.waitFor(() => expect(visibleResults()).not.toBeNull());
  expect(posted).toEqual([unavailable, recipe]);
});

it('ignores a saved recipe result that resolves after navigation despite cancellation', async () => {
  await mount();
  const late = deferComparison();
  chooseRecipe(recipeFile(JSON.stringify(comparison.recipe)));
  await vi.waitFor(() => expect(client.compare).toHaveBeenCalledTimes(1));
  const signal = vi.mocked(client.compare).mock.calls[0]?.[1]?.signal;
  dispose?.();
  dispose = undefined;
  root.textContent = 'Cases';
  expect(signal?.aborted).toBe(true);
  late.resolve(comparison);
  await nextTurn();
  expect(root.textContent).toBe('Cases');
  expect(visibleResults()).toBeNull();
});

it('ignores a late file read after a new comparison is submitted', async () => {
  await mount();
  const file = recipeFile('{}');
  let finish!: (value: string) => void;
  vi.spyOn(file, 'text').mockReturnValue(new Promise(resolve => { finish = resolve; }));
  chooseRecipe(file);
  submit();
  await vi.waitFor(() => expect(visibleResults()).not.toBeNull());
  finish(JSON.stringify(recipe));
  await nextTurn();
  expect(client.compare).toHaveBeenCalledExactlyOnceWith(recipe, expect.anything());
  expect(visibleResults()).not.toBeNull();
});

it('shows ranked and reviewed order, score provenance and linked assumptions for a window', async () => {
  await run();
  await vi.waitFor(() => expect(visibleResults()).not.toBeNull());
  const window = root.querySelector<HTMLDetailsElement>('details[data-window-start][data-strategy="weighted_score_per_minute"]');
  expect(window).toBeInstanceOf(HTMLDetailsElement);
  expect(window!.dataset.windowStart).toBe(scenario.window_starts[0]);
  window!.open = true;
  window!.dispatchEvent(new Event('toggle'));
  const ranked = [...window!.querySelectorAll<HTMLElement>('[data-ranked-alerts] [data-alert-id]')];
  expect(ranked.map(row => row.dataset.alertId)).toEqual(['C', 'E', 'B', 'A']);
  expect([...window!.querySelectorAll('[data-reviewed-order] li')].map(row => row.textContent)).toEqual(['C', 'E']);
  expect(window!.querySelector('[data-used-minutes]')?.textContent).toContain('2');
  expect(window!.textContent).toContain('illustrative-v1');
  expect(ranked[0].querySelector('[data-score]')?.textContent).toBe('0.80');
  expect(ranked[0].querySelector('[data-scenario-weight]')?.textContent).toContain('1');
  expect(ranked[0].querySelector('[data-scenario-weight]')?.textContent).toContain('Equal synthetic weights');
  expect(ranked[0].querySelector('[data-review-minutes]')?.textContent).toContain('1');
  expect(ranked[0].querySelector('[data-review-minutes]')?.textContent).toContain('Authored review minutes');
  expect(window!.textContent).not.toMatch(/\b(positive|negative)\b/);
});
