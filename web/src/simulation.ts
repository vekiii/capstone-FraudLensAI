// Strict raw-wire decoding shared by injected and HTTP clients.
export interface SimulationClient {
  listScenarios(options?: { signal?: AbortSignal }): Promise<unknown>;
  compare(recipe: unknown, options?: { signal?: AbortSignal }): Promise<unknown>;
}

type Obj = Record<string, unknown>;
function closed(v: unknown, keys: string): Obj {
  if (!v || typeof v !== 'object' || Array.isArray(v)) throw Error('Invalid object');
  const o = v as Obj, expected = keys.split(' ');
  if (Object.keys(o).length !== expected.length || expected.some(k => !(k in o))) throw Error('Invalid fields');
  return o;
}
function text(v: unknown): string { if (typeof v !== 'string' || !v.length) throw Error('Invalid text'); return v; }
function id(v: unknown): string { const s=text(v); if(!/^[A-Za-z0-9_-]{1,80}$(?![\s\S])/.test(s))throw Error('Invalid ID');return s; }
function integer(v: unknown, min=0): number { if(typeof v!=='number'||!Number.isSafeInteger(v)||v<min)throw Error('Invalid integer');return v; }
function literal(v: unknown, expected: string): string {if(v!==expected)throw Error('Invalid literal');return expected;}
function array(v: unknown): unknown[] {if(!Array.isArray(v))throw Error('Invalid array');return v;}
function unique(v: string[]): string[] {if(new Set(v).size!==v.length)throw Error('Duplicate ID');return v;}
function decimal(v: unknown, score=true): string {
  const s=text(v);if(s.length>128||!/^(0|[1-9][0-9]*)(\.[0-9]+)?$(?![\s\S])/.test(s))throw Error('Invalid decimal');
  if(score?!/^(0(\.[0-9]+)?|1(\.0+)?)$(?![\s\S])/.test(s):!/[1-9]/.test(s))throw Error('Decimal range');return s;
}
function utc(v: unknown): string {
  const s=text(v);if(!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?Z$(?![\s\S])/.test(s)||!Number.isFinite(Date.parse(s))||new Date(s).toISOString().slice(0,19)!==s.slice(0,19))throw Error('Invalid UTC');return s;
}
function instantKey(s: string): string { return s.slice(0,19) + '.' + s.slice(19,-1).replace(/^\./,'').padEnd(6,'0') + 'Z'; }
function canonicalDecimal(s: string): string { return s.includes('.') ? s.replace(/0+$/, '').replace(/\.$/, '') : s; }
function reference(v: unknown) {
  const o=closed(v,'scenario_id scenario_version content_sha256'), hash=text(o.content_sha256);
  if(!/^[0-9a-f]{64}$(?![\s\S])/.test(hash))throw Error('Invalid digest');
  return {scenario_id:id(o.scenario_id),scenario_version:integer(o.scenario_version,1),content_sha256:hash};
}
type ScenarioReference = ReturnType<typeof reference>;

function sameScenario(a: ScenarioReference, b: ScenarioReference): boolean {
  return a.scenario_id === b.scenario_id && a.scenario_version === b.scenario_version &&
    a.content_sha256 === b.content_sha256;
}
function metadata(v: unknown) {
  const o=closed(v,'scenario_id scenario_version content_sha256 title source score_provenance assumptions horizon window_starts defaults generation_seed');
  const source=closed(o.source,'kind data_version time_basis'), p=closed(o.score_provenance,'source score_kind scorer_version'), h=closed(o.horizon,'starts_at ends_at'), d=closed(o.defaults,'score_threshold budget_minutes_per_window');
  const assumptions=array(o.assumptions).map(v=>{const a=closed(v,'id description');return {id:id(a.id),description:text(a.description)};});unique(assumptions.map(a=>a.id));
  const starts=array(o.window_starts).map(utc), start=utc(h.starts_at), end=utc(h.ends_at);
  if(instantKey(start)>=instantKey(end)||starts.length<1||starts.length>12||instantKey(starts[0])!==instantKey(start)||starts.some((s,i)=>instantKey(s)<instantKey(start)||instantKey(s)>=instantKey(end)||(i>0&&instantKey(s)<=instantKey(starts[i-1]))))throw Error('Invalid windows');
  return {...reference({scenario_id:o.scenario_id,scenario_version:o.scenario_version,content_sha256:o.content_sha256}),title:text(o.title),
    source:{kind:literal(source.kind,'bundled_synthetic'),data_version:text(source.data_version),time_basis:text(source.time_basis)},
    score_provenance:{source:literal(p.source,'fixture'),score_kind:literal(p.score_kind,'illustrative_score'),scorer_version:text(p.scorer_version)},
    assumptions,horizon:{starts_at:start,ends_at:end},window_starts:starts,defaults:{score_threshold:decimal(d.score_threshold),budget_minutes_per_window:integer(d.budget_minutes_per_window)},generation_seed:o.generation_seed===null?null:integer(o.generation_seed)};
}
const strategyOrder = ['fifo', 'highest_score', 'weighted_score_per_minute'] as const;
const currentStrategyVersions = { fifo: 1, highest_score: 1, weighted_score_per_minute: 1 };
const strategyDescriptions: Record<typeof strategyOrder[number], string> = {
  fifo: 'Ranije dostupna upozorenja imaju prednost.',
  highest_score: 'Viši skor rizika ima prednost.',
  weighted_score_per_minute: 'Prednost ima veća vrednost izraza skor × težina scenarija ÷ procenjeni minuti.',
};

function decodeRecipe(value: unknown) {
  const input = closed(value, 'contract_version scenario score_threshold budget_minutes_per_window strategy_versions');
  if (input.contract_version !== 1) throw Error('Invalid version');
  const versions = closed(input.strategy_versions, strategyOrder.join(' '));
  return {
    contract_version: 1 as const,
    scenario: reference(input.scenario),
    score_threshold: decimal(input.score_threshold),
    budget_minutes_per_window: integer(input.budget_minutes_per_window),
    strategy_versions: {
      fifo: integer(versions.fifo, 1),
      highest_score: integer(versions.highest_score, 1),
      weighted_score_per_minute: integer(versions.weighted_score_per_minute, 1),
    },
  };
}

type Recipe = ReturnType<typeof decodeRecipe>;

function sameRecipe(a: Recipe, b: Recipe): boolean {
  return sameScenario(a.scenario, b.scenario) && a.budget_minutes_per_window === b.budget_minutes_per_window &&
    canonicalDecimal(a.score_threshold) === canonicalDecimal(b.score_threshold) &&
    strategyOrder.every(strategy => a.strategy_versions[strategy] === b.strategy_versions[strategy]);
}
function decodeCatalog(v: unknown) {
  const o=closed(v,'contract_version items');if(o.contract_version!==1)throw Error('Invalid version');
  const items=array(o.items).map(metadata);unique(items.map(s=>`${s.scenario_id}/${s.scenario_version}`));return items;
}
function decodeComparison(v: unknown) {
  const o=closed(v,'contract_version recipe scenario admitted_alerts strategies');if(o.contract_version!==1)throw Error('Invalid version');
  const r=decodeRecipe(o.recipe),s=metadata(o.scenario);if(!sameScenario(r.scenario,s))throw Error('Mixed scenario');
  const alerts=array(o.admitted_alerts).map(v=>{
    const a=closed(v,'alert_id available_at score weight estimated_review_minutes weight_assumption_id duration_assumption_id');
    const result={alert_id:id(a.alert_id),available_at:utc(a.available_at),score:decimal(a.score),weight:decimal(a.weight,false),estimated_review_minutes:integer(a.estimated_review_minutes,1),weight_assumption_id:id(a.weight_assumption_id),duration_assumption_id:id(a.duration_assumption_id)};
    if(![result.weight_assumption_id,result.duration_assumption_id].every(k=>s.assumptions.some(a=>a.id===k)))throw Error('Unknown assumption');return result;
  });if(alerts.length>250)throw Error('Too many alerts');unique(alerts.map(a=>a.alert_id));const ids=new Set(alerts.map(a=>a.alert_id));
  function idsList(v: unknown){const values=unique(array(v).map(id));if(values.some(k=>!ids.has(k)))throw Error('Foreign alert');return values;}
  const strategies=array(o.strategies).map((v,i)=>{
    const strategyId = strategyOrder[i];
    const a=closed(v,'strategy_id windows pending_alert_ids counts');if(!strategyId||a.strategy_id!==strategyId)throw Error('Strategy order');
    const windows=array(a.windows).map((v,i)=>{
      const w=closed(v,'starts_at ranked_alert_ids reviewed_alert_ids used_minutes'),start=utc(w.starts_at),ranked=idsList(w.ranked_alert_ids),reviewed=idsList(w.reviewed_alert_ids),used=integer(w.used_minutes);
      if(instantKey(start)!==instantKey(s.window_starts[i]??'')||used>r.budget_minutes_per_window||reviewed.some(k=>!ranked.includes(k)))throw Error('Invalid window');
      return {starts_at:start,ranked_alert_ids:ranked,reviewed_alert_ids:reviewed,used_minutes:used};
    });
    const pending=idsList(a.pending_alert_ids),c=closed(a.counts,'reviewed backlog unknown_in_horizon unknown_reviewed outcomes'),reviewed=windows.flatMap(w=>w.reviewed_alert_ids);unique(reviewed);
    if(windows.length!==s.window_starts.length||integer(c.reviewed)!==reviewed.length||integer(c.backlog)!==pending.length||pending.some(k=>reviewed.includes(k)))throw Error('Count mismatch');
    let outcomes=null;
    if(c.outcomes!==null){const x=closed(c.outcomes,'positives_found positives_missed positives_missed_threshold positives_missed_backlog reviewed_negatives');outcomes={positives_found:integer(x.positives_found),positives_missed:integer(x.positives_missed),positives_missed_threshold:integer(x.positives_missed_threshold),positives_missed_backlog:integer(x.positives_missed_backlog),reviewed_negatives:integer(x.reviewed_negatives)};if(outcomes.positives_missed!==outcomes.positives_missed_threshold+outcomes.positives_missed_backlog)throw Error('Miss counts');}
    return {strategy_id:strategyId,windows,pending_alert_ids:pending,counts:{reviewed:reviewed.length,backlog:pending.length,unknown_in_horizon:integer(c.unknown_in_horizon),unknown_reviewed:integer(c.unknown_reviewed),outcomes}};
  });if(strategies.length!==3)throw Error('Missing strategies');return {recipe:r,scenario:s,admitted_alerts:alerts,strategies};
}
class SimulationVersionUnavailable extends Error {}

async function request(url: string, options: RequestInit): Promise<unknown> {
  const controller=new AbortController(),abort=()=>controller.abort();options.signal?.addEventListener('abort',abort,{once:true});if(options.signal?.aborted)controller.abort();const timer=setTimeout(abort,5000);
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    if (response.status === 409) throw new SimulationVersionUnavailable();
    if (!response.ok) throw Error('Request failed');
    return await response.json();
  } finally {
    clearTimeout(timer);
    options.signal?.removeEventListener('abort', abort);
  }
}
const defaultClient: SimulationClient={listScenarios:o=>request('/api/simulation/scenarios',{signal:o?.signal}),compare:(body,o)=>request('/api/simulation/comparisons',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body),signal:o?.signal})};
function node<K extends keyof HTMLElementTagNameMap>(tag: K,value=''):HTMLElementTagNameMap[K]{const n=document.createElement(tag);n.textContent=value;return n;}

type Scenario = ReturnType<typeof metadata>;
type Comparison = ReturnType<typeof decodeComparison>;
type AdmittedAlert = Comparison['admitted_alerts'][number];

function downloadRecipe(recipe: Recipe) {
  const blob = new Blob([JSON.stringify(recipe, null, 2) + '\n'], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = node('a');
  link.href = url;
  link.download = `simulation-recipe-${recipe.scenario.scenario_id}-v${recipe.scenario.scenario_version}.json`;
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

function renderRunSettings(recipe: Recipe) {
  const details = node('details');
  details.dataset.simulationRunSettings = '';
  details.append(node('summary', 'Podešavanja izvršenog poređenja'));
  const entries = node('dl');
  const { scenario, strategy_versions } = recipe;
  for (const [label, value] of [
    ['Ugovor', recipe.contract_version],
    ['Scenario i verzija', `${scenario.scenario_id} (v${scenario.scenario_version})`],
    ['Otisak scenarija (SHA-256)', scenario.content_sha256],
    ['Prag skora rizika', recipe.score_threshold],
    ['Budžet minuta po prozoru', recipe.budget_minutes_per_window],
    ['Verzije strategija', strategyOrder.map(name => `${name} v${strategy_versions[name]}`).join(', ')],
  ]) entries.append(node('dt', String(label)), node('dd', String(value)));
  details.append(entries);
  return details;
}

function renderAlertFacts(alerts: AdmittedAlert[], assumptions: Map<string, string>) {
  const table = node('table');
  const header = table.createTHead().insertRow();
  for (const label of ['Upozorenje', 'Dostupno od (UTC)', 'Skor rizika', 'Težina scenarija', 'Procenjeni minuti']) {
    const cell = node('th', label);
    cell.scope = 'col';
    header.append(cell);
  }
  const body = table.createTBody();
  for (const alert of alerts) {
    const row = body.insertRow();
    row.dataset.alertId = alert.alert_id;
    const idCell = node('th', alert.alert_id);
    idCell.scope = 'row';
    row.append(idCell);
    row.insertCell().textContent = alert.available_at;
    const score = row.insertCell();
    score.dataset.score = '';
    score.textContent = alert.score;
    const weight = row.insertCell();
    weight.dataset.scenarioWeight = '';
    weight.append(
      String(alert.weight),
      node('small', `Pretpostavka: ${assumptions.get(alert.weight_assumption_id)}`),
    );
    const minutes = row.insertCell();
    minutes.dataset.reviewMinutes = '';
    minutes.append(
      String(alert.estimated_review_minutes),
      node('small', `Pretpostavka: ${assumptions.get(alert.duration_assumption_id)}`),
    );
  }
  return table;
}

function collapsible(label: string, content: () => Node[]) {
  const details = node('details');
  details.append(node('summary', label));
  function populate() {
    if (!details.open) return;
    details.append(...content());
    details.removeEventListener('toggle', populate);
  }
  details.addEventListener('toggle', populate);
  return details;
}

function renderOrdering(comparison: Comparison) {
  const section = node('section');
  section.className = 'simulation-ordering';
  section.append(
    node('h2', 'Redosled po vremenskom prozoru'),
    node('p', 'Kod izjednačenja prednost imaju ranije dostupna upozorenja, zatim upozorenja po rastućem ID-u.'),
  );
  const alerts = new Map(comparison.admitted_alerts.map(alert => [alert.alert_id, alert]));
  const assumptions = new Map(comparison.scenario.assumptions.map(item => [item.id, item.description]));
  const score = comparison.scenario.score_provenance;
  const scoreSource = `Poreklo skora: ${score.source} / ${score.score_kind} / ${score.scorer_version}`;
  for (const strategy of comparison.strategies) {
    section.append(node('h3', strategy.strategy_id), node('p', strategyDescriptions[strategy.strategy_id]));
    for (const window of strategy.windows) {
      const details = collapsible(window.starts_at, () => {
        const minutes = node('p', `Iskorišćeno minuta: ${window.used_minutes} od ${comparison.recipe.budget_minutes_per_window}`);
        minutes.dataset.usedMinutes = '';
        const reviewed = node('ol');
        reviewed.dataset.reviewedOrder = '';
        reviewed.append(...window.reviewed_alert_ids.map(id => node('li', id)));
        const content = [
          minutes, node('h4', 'Redosled pregleda'),
          window.reviewed_alert_ids.length ? reviewed : node('p', 'Nijedno upozorenje nije pregledano.'),
          node('h4', 'Rangirani kandidati'),
        ];
        if (!window.ranked_alert_ids.length) return [...content, node('p', 'Nema kandidata u ovom prozoru.')];
        // The comparison decoder has already verified that every ranked ID resolves.
        const ranked = renderAlertFacts(window.ranked_alert_ids.map(id => alerts.get(id)!), assumptions);
        ranked.dataset.rankedAlerts = '';
        return [...content, node('p', scoreSource), ranked];
      });
      details.dataset.windowStart = window.starts_at;
      details.dataset.strategy = strategy.strategy_id;
      section.append(details);
    }
    if (strategy.pending_alert_ids.length) {
      section.append(node('p', `Završni zaostatak: ${strategy.pending_alert_ids.join(', ')}`));
    }
  }
  if (comparison.admitted_alerts.length) {
    const admitted = collapsible('Sva upozorenja koja ispunjavaju prag', () => [
      node('p', scoreSource), renderAlertFacts(comparison.admitted_alerts, assumptions),
    ]);
    admitted.dataset.admittedAlertFacts = '';
    section.append(admitted);
  }
  return section;
}

function renderResults(results: HTMLElement, comparison: Comparison) {
  const download = node('button', 'Preuzmi recept (JSON)');
  download.type = 'button';
  download.className = 'button button-back';
  download.dataset.simulationDownload = '';
  download.addEventListener('click', () => downloadRecipe(comparison.recipe));
  results.append(download, renderRunSettings(comparison.recipe));
  const table = node('table');
  table.createCaption().textContent = 'Ishodi prema referentnim oznakama simulacije';
  const head = table.createTHead().insertRow();
  for (const label of [
    'Strategija', 'Pregledani', 'Pronađeni pozitivni', 'Ukupno propušteni pozitivni',
    'Propušteni pragom', 'Propušteni u zaostatku', 'Pregledani negativni', 'Završni zaostatak',
    'Bez oznake u periodu', 'Pregledani bez oznake',
  ]) {
    const cell = node('th', label);
    cell.scope = 'col';
    head.append(cell);
  }
  const body = table.createTBody();
  for (const result of comparison.strategies) {
    const { outcomes, backlog, unknown_in_horizon, unknown_reviewed } = result.counts;
    const row = body.insertRow();
    row.dataset.strategyId = result.strategy_id;
    const strategy = node('th', result.strategy_id);
    strategy.scope = 'row';
    row.append(strategy);
    const cells = [
      ['reviewedAlerts', result.windows.flatMap(w => w.reviewed_alert_ids).join(',')],
      ['positivesFound', outcomes?.positives_found],
      ['positivesMissed', outcomes?.positives_missed],
      ['missedThreshold', outcomes?.positives_missed_threshold],
      ['missedBacklog', outcomes?.positives_missed_backlog],
      ['reviewedNegatives', outcomes?.reviewed_negatives],
      ['backlog', backlog],
      ['unknownInHorizon', unknown_in_horizon],
      ['unknownReviewed', unknown_reviewed],
    ] as const;
    for (const [field, value] of cells) {
      const cell = row.insertCell();
      cell.dataset[field] = '';
      cell.textContent = String(value ?? 'Nedostupno');
    }
  }

  if (comparison.strategies.some(row => row.counts.outcomes === null)) {
    results.append(node('p', 'Nema poznatih oznaka ishoda. Metrike pozitivnih i negativnih ishoda su nedostupne.'));
  } else if (comparison.strategies.some(row => row.counts.unknown_in_horizon > 0)) {
    results.append(node('p', 'Pokrivenost oznakama ishoda je delimična. Metrike pozitivnih i negativnih ishoda obuhvataju samo poznate oznake.'));
  }
  results.append(table, renderOrdering(comparison));
  results.dataset.simulationResults = '';
}

export function mountSimulation(root: HTMLElement, client: SimulationClient = defaultClient): () => void {
  let disposed = false;
  let generation = 0;
  let pending: AbortController | undefined = new AbortController();
  const items: Scenario[] = [];

  const selector = node('select');
  selector.setAttribute('aria-label', 'Scenario');
  selector.disabled = true;
  const provenance = node('section');
  const form = node('form');
  form.className = 'simulation-settings';
  const thresholdLabel = node('label', 'Prag skora rizika (0–1)');
  const threshold = node('input');
  threshold.name = 'score_threshold';
  threshold.inputMode = 'decimal';
  thresholdLabel.append(threshold);
  const budgetLabel = node('label', 'Budžet (minuti po vremenskom prozoru)');
  const budget = node('input');
  budget.name = 'budget_minutes_per_window';
  budget.inputMode = 'numeric';
  budgetLabel.append(budget);
  const button = node('button', 'Uporedi strategije');
  button.type = 'submit';
  button.className = 'button';
  button.dataset.simulationRun = '';
  for (const control of [threshold, budget, button]) control.disabled = true;
  form.append(thresholdLabel, budgetLabel, button);
  const recipeLabel = node('label', 'Otvori recept (JSON)');
  recipeLabel.className = 'simulation-recipe-file';
  const recipeFile = node('input');
  recipeFile.type = 'file';
  recipeFile.name = 'simulation_recipe';
  recipeFile.accept = '.json,application/json';
  recipeFile.disabled = true;
  recipeLabel.append(recipeFile);
  const status = node('p');
  status.setAttribute('aria-live', 'polite');
  const results = node('section');
  root.replaceChildren(
    node('h1', 'Simulation & Evaluation'),
    node('p', 'Sintetička simulacija; savetodavni redosled, bez intervencija nad računima.'),
    selector, provenance, form, recipeLabel, status, results,
  );

  function cancelPending() {
    generation++;
    pending?.abort();
    pending = undefined;
  }

  function clearComparison() {
    cancelPending();
    results.replaceChildren();
    results.removeAttribute('data-simulation-results');
    status.removeAttribute('role');
    status.textContent = '';
    threshold.removeAttribute('aria-invalid');
    budget.removeAttribute('aria-invalid');
  }

  function showError(message: string, input?: HTMLInputElement) {
    status.setAttribute('role', 'alert');
    status.textContent = message;
    input?.setAttribute('aria-invalid', 'true');
    input?.focus();
  }

  const requestError = 'Simulacija nije dostupna ili je odgovor neispravan. Pokušajte ponovo.';

  function addScenario(scenario: Scenario) {
    items.push(scenario);
    const option = node('option', `${scenario.title} (v${scenario.scenario_version})`);
    option.value = scenario.scenario_id;
    selector.append(option);
    selector.disabled = false;
  }

  function showScenario(selected?: Scenario, settings = selected?.defaults) {
    for (const control of [threshold, budget, button]) control.disabled = !selected;
    threshold.value = settings?.score_threshold ?? '';
    budget.value = settings ? String(settings.budget_minutes_per_window) : '';
    provenance.replaceChildren();
    if (!selected) return;
    const { source, score_provenance, assumptions, horizon, generation_seed } = selected;
    provenance.append(
      node('p', `${source.kind} / ${source.data_version} / ${source.time_basis}`),
      node('p', `${score_provenance.source} / ${score_provenance.score_kind} / ${score_provenance.scorer_version}`),
      node('p', `Period simulacije (UTC): od ${horizon.starts_at} do ${horizon.ends_at}`),
      ...assumptions.map(a => node('p', `${a.id}: ${a.description}`)),
    );
    if (generation_seed !== null) provenance.append(node('p', `Seme generatora: ${generation_seed}`));
  }

  function selectScenario() {
    if (disposed || !items.length) return;
    clearComparison();
    showScenario(items[selector.selectedIndex]);
  }

  function submitComparison() {
    const selected = items[selector.selectedIndex];
    if (disposed || !selected) return;
    clearComparison();

    let scoreThreshold: string;
    try {
      scoreThreshold = decimal(threshold.value);
    } catch {
      showError('Unesite prag od 0 do 1, sa tačkom kao decimalnim separatorom (najviše 128 znakova).', threshold);
      return;
    }
    const minutes = Number(budget.value);
    if (!/^\d+$/.test(budget.value) || !Number.isSafeInteger(minutes)) {
      showError(`Unesite ceo broj minuta od 0 do ${Number.MAX_SAFE_INTEGER} po vremenskom prozoru.`, budget);
      return;
    }

    const { scenario_id, scenario_version, content_sha256 } = selected;
    void compare({
      contract_version: 1,
      scenario: { scenario_id, scenario_version, content_sha256 },
      score_threshold: scoreThreshold,
      budget_minutes_per_window: minutes,
      strategy_versions: { ...currentStrategyVersions },
    });
  }

  async function reopenRecipe() {
    if (disposed || recipeFile.disabled) return;
    const file = recipeFile.files?.[0];
    if (!file) return;
    recipeFile.value = '';
    clearComparison();
    const token = generation;
    status.textContent = 'Čitanje recepta…';
    let saved: Recipe;
    try {
      const contents = await file.text();
      if (disposed || token !== generation) return;
      saved = decodeRecipe(JSON.parse(contents));
    } catch {
      if (!disposed && token === generation) showError('Recept nije ispravan. Izaberite JSON recept za simulaciju (ugovor v1).');
      return;
    }
    void compare(saved, true);
  }

  async function compare(input: Recipe, reopened = false) {
    const token = generation;
    pending = new AbortController();
    status.textContent = 'Računanje…';
    try {
      const response = await client.compare(input, { signal: pending.signal });
      if (disposed || token !== generation) return;
      const decoded = decodeComparison(response);
      if (!sameRecipe(decoded.recipe, input)) throw Error('Wrong recipe');
      if (reopened) {
        let index = items.findIndex(item => sameScenario(item, input.scenario));
        if (index === -1) {
          index = items.length;
          addScenario(decoded.scenario);
        }
        selector.selectedIndex = index;
        showScenario(decoded.scenario, input);
      }
      renderResults(results, decoded);
      status.textContent = 'Poređenje završeno.';
    } catch (error) {
      if (disposed || token !== generation) return;
      showError(error instanceof SimulationVersionUnavailable
        ? 'Tražena verzija scenarija ili strategije nije dostupna. Za druga podešavanja pokrenite novo poređenje.'
        : requestError);
    } finally {
      if (token === generation) pending = undefined;
    }
  }

  selector.addEventListener('change', selectScenario);
  threshold.addEventListener('input', clearComparison);
  budget.addEventListener('input', clearComparison);
  recipeFile.addEventListener('change', () => { void reopenRecipe(); });
  form.addEventListener('submit', event => {
    event.preventDefault();
    submitComparison();
  });
  void (async () => {
    try {
      const response = await client.listScenarios({ signal: pending?.signal });
      if (disposed) return;
      for (const scenario of decodeCatalog(response)) addScenario(scenario);
      if (items.length) showScenario(items[selector.selectedIndex]);
      else status.textContent = 'Nema dostupnih scenarija.';
    } catch {
      if (!disposed) showError(requestError);
    } finally {
      if (!disposed) {
        pending = undefined;
        recipeFile.disabled = false;
      }
    }
  })();
  return () => {
    disposed = true;
    cancelPending();
    root.replaceChildren();
  };
}
