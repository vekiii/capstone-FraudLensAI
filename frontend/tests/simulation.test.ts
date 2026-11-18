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
afterEach(() => { dispose?.(); dispose = undefined; document.body.replaceChildren(); vi.restoreAllMocks(); });

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
