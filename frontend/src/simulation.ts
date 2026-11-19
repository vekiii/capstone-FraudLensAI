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
function recipe(v: unknown) {
  const o=closed(v,'contract_version scenario score_threshold budget_minutes_per_window strategy_versions');if(o.contract_version!==1)throw Error('Invalid version');
  const versions=closed(o.strategy_versions,'fifo highest_score weighted_score_per_minute');if(Object.values(versions).some(v=>v!==1))throw Error('Unsupported strategy');
  return {contract_version:1,scenario:reference(o.scenario),score_threshold:decimal(o.score_threshold),budget_minutes_per_window:integer(o.budget_minutes_per_window),strategy_versions:{fifo:1,highest_score:1,weighted_score_per_minute:1}};
}
function decodeCatalog(v: unknown) {
  const o=closed(v,'contract_version items');if(o.contract_version!==1)throw Error('Invalid version');
  const items=array(o.items).map(metadata);unique(items.map(s=>`${s.scenario_id}/${s.scenario_version}`));return items;
}
function decodeComparison(v: unknown) {
  const o=closed(v,'contract_version recipe scenario admitted_alerts strategies');if(o.contract_version!==1)throw Error('Invalid version');
  const r=recipe(o.recipe),s=metadata(o.scenario);if(r.scenario.scenario_id!==s.scenario_id||r.scenario.scenario_version!==s.scenario_version||r.scenario.content_sha256!==s.content_sha256)throw Error('Mixed scenario');
  const alerts=array(o.admitted_alerts).map(v=>{
    const a=closed(v,'alert_id available_at score weight estimated_review_minutes weight_assumption_id duration_assumption_id');
    const result={alert_id:id(a.alert_id),available_at:utc(a.available_at),score:decimal(a.score),weight:decimal(a.weight,false),estimated_review_minutes:integer(a.estimated_review_minutes,1),weight_assumption_id:id(a.weight_assumption_id),duration_assumption_id:id(a.duration_assumption_id)};
    if(![result.weight_assumption_id,result.duration_assumption_id].every(k=>s.assumptions.some(a=>a.id===k)))throw Error('Unknown assumption');return result;
  });if(alerts.length>250)throw Error('Too many alerts');unique(alerts.map(a=>a.alert_id));const ids=new Set(alerts.map(a=>a.alert_id));
  function idsList(v: unknown){const values=unique(array(v).map(id));if(values.some(k=>!ids.has(k)))throw Error('Foreign alert');return values;}
  const order=['fifo','highest_score','weighted_score_per_minute'];
  const strategies=array(o.strategies).map((v,i)=>{
    const a=closed(v,'strategy_id windows pending_alert_ids counts');if(a.strategy_id!==order[i])throw Error('Strategy order');
    const windows=array(a.windows).map((v,i)=>{
      const w=closed(v,'starts_at ranked_alert_ids reviewed_alert_ids used_minutes'),start=utc(w.starts_at),ranked=idsList(w.ranked_alert_ids),reviewed=idsList(w.reviewed_alert_ids),used=integer(w.used_minutes);
      if(instantKey(start)!==instantKey(s.window_starts[i]??'')||used>r.budget_minutes_per_window||reviewed.some(k=>!ranked.includes(k)))throw Error('Invalid window');
      return {starts_at:start,ranked_alert_ids:ranked,reviewed_alert_ids:reviewed,used_minutes:used};
    });
    const pending=idsList(a.pending_alert_ids),c=closed(a.counts,'reviewed backlog unknown_in_horizon unknown_reviewed outcomes'),reviewed=windows.flatMap(w=>w.reviewed_alert_ids);unique(reviewed);
    if(windows.length!==s.window_starts.length||integer(c.reviewed)!==reviewed.length||integer(c.backlog)!==pending.length||pending.some(k=>reviewed.includes(k)))throw Error('Count mismatch');
    let outcomes=null;
    if(c.outcomes!==null){const x=closed(c.outcomes,'positives_found positives_missed positives_missed_threshold positives_missed_backlog reviewed_negatives');outcomes={positives_found:integer(x.positives_found),positives_missed:integer(x.positives_missed),positives_missed_threshold:integer(x.positives_missed_threshold),positives_missed_backlog:integer(x.positives_missed_backlog),reviewed_negatives:integer(x.reviewed_negatives)};if(outcomes.positives_missed!==outcomes.positives_missed_threshold+outcomes.positives_missed_backlog)throw Error('Miss counts');}
    return {strategy_id:text(a.strategy_id),windows,pending_alert_ids:pending,counts:{reviewed:reviewed.length,backlog:pending.length,unknown_in_horizon:integer(c.unknown_in_horizon),unknown_reviewed:integer(c.unknown_reviewed),outcomes}};
  });if(strategies.length!==3)throw Error('Missing strategies');return {recipe:r,scenario:s,admitted_alerts:alerts,strategies};
}
async function request(url: string, options: RequestInit): Promise<unknown> {
  const controller=new AbortController(),abort=()=>controller.abort();options.signal?.addEventListener('abort',abort,{once:true});if(options.signal?.aborted)controller.abort();const timer=setTimeout(abort,5000);
  try{const response=await fetch(url,{...options,signal:controller.signal});if(!response.ok)throw Error('Request failed');return await response.json();}finally{clearTimeout(timer);options.signal?.removeEventListener('abort',abort);}
}
const defaultClient: SimulationClient={listScenarios:o=>request('/api/simulation/scenarios',{signal:o?.signal}),compare:(body,o)=>request('/api/simulation/comparisons',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body),signal:o?.signal})};
function node<K extends keyof HTMLElementTagNameMap>(tag: K,value=''):HTMLElementTagNameMap[K]{const n=document.createElement(tag);n.textContent=value;return n;}

function renderResults(results: HTMLElement, comparison: ReturnType<typeof decodeComparison>) {
  const table = node('table');
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
  results.append(table);
  results.dataset.simulationResults = '';
}

export function mountSimulation(root: HTMLElement, client: SimulationClient = defaultClient): () => void {
  let disposed = false;
  let generation = 0;
  let pending: AbortController | undefined = new AbortController();
  let items: ReturnType<typeof decodeCatalog> = [];

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
  const status = node('p');
  status.setAttribute('aria-live', 'polite');
  const results = node('section');
  root.replaceChildren(
    node('h1', 'Simulation & Evaluation'),
    node('p', 'Sintetička simulacija; savetodavni redosled, bez intervencija nad računima.'),
    selector, provenance, form, status, results,
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

  function selectScenario() {
    if (disposed || !items.length) return;
    clearComparison();
    const selected = items[selector.selectedIndex];
    for (const control of [threshold, budget, button]) control.disabled = !selected;
    threshold.value = selected?.defaults.score_threshold ?? '';
    budget.value = selected ? String(selected.defaults.budget_minutes_per_window) : '';
    provenance.replaceChildren();
    if (!selected) return;
    const { source, score_provenance, assumptions } = selected;
    provenance.append(
      node('p', `${source.kind} / ${source.data_version} / ${source.time_basis}`),
      node('p', `${score_provenance.source} / ${score_provenance.score_kind} / ${score_provenance.scorer_version}`),
      ...assumptions.map(a => node('p', `${a.id}: ${a.description}`)),
    );
  }

  async function compare() {
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
    const input = {
      contract_version: 1,
      scenario: { scenario_id, scenario_version, content_sha256 },
      score_threshold: scoreThreshold,
      budget_minutes_per_window: minutes,
      strategy_versions: { fifo: 1, highest_score: 1, weighted_score_per_minute: 1 },
    };
    const token = generation;
    pending = new AbortController();
    status.textContent = 'Računanje…';
    try {
      const response = await client.compare(input, { signal: pending.signal });
      if (disposed || token !== generation) return;
      const decoded = decodeComparison(response);
      const returned = decoded.recipe;
      if (
        returned.scenario.scenario_id !== scenario_id ||
        returned.scenario.scenario_version !== scenario_version ||
        returned.scenario.content_sha256 !== content_sha256 ||
        returned.budget_minutes_per_window !== minutes ||
        canonicalDecimal(returned.score_threshold) !== canonicalDecimal(scoreThreshold)
      ) throw Error('Wrong recipe');
      renderResults(results, decoded);
      status.textContent = 'Poređenje završeno.';
    } catch {
      if (!disposed && token === generation) showError(requestError);
    } finally {
      if (token === generation) pending = undefined;
    }
  }

  selector.addEventListener('change', selectScenario);
  threshold.addEventListener('input', clearComparison);
  budget.addEventListener('input', clearComparison);
  form.addEventListener('submit', event => {
    event.preventDefault();
    void compare();
  });
  void (async () => {
    try {
      const response = await client.listScenarios({ signal: pending?.signal });
      if (disposed) return;
      pending = undefined;
      items = decodeCatalog(response);
      for (const scenario of items) {
        const option = node('option', `${scenario.title} (v${scenario.scenario_version})`);
        option.value = scenario.scenario_id;
        selector.append(option);
      }
      selector.disabled = !items.length;
      if (items.length) selectScenario();
      else status.textContent = 'Nema dostupnih scenarija.';
    } catch {
      if (!disposed) showError(requestError);
    }
  })();
  return () => {
    disposed = true;
    cancelPending();
    root.replaceChildren();
  };
}
