import type { EdaSeries, EdaSummary, ModelResults, PredictionResult } from './contracts';

function element<K extends keyof HTMLElementTagNameMap>(tag: K, text?: string, className?: string) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function button(label: string, action: () => void, className = 'button') {
  const node = element('button', label, className);
  node.type = 'button';
  node.addEventListener('click', action);
  return node;
}

function status(message: string, error = false) {
  const node = element('p', message, error ? 'message message-error' : 'message');
  node.setAttribute('role', error ? 'alert' : 'status');
  node.setAttribute('aria-atomic', 'true');
  return node;
}

function fields(entries: readonly (readonly [string, string])[]) {
  const list = element('dl', undefined, 'fields');
  for (const [label, value] of entries) {
    const row = element('div');
    row.append(element('dt', label), element('dd', value));
    list.append(row);
  }
  return list;
}

export type RiskUiState = { kind: 'idle' } | { kind: 'loading' }
  | { kind: 'success'; result: PredictionResult }
  | { kind: 'error'; message: string };

export function createRiskView(root: HTMLElement, assess: (id: string) => void) {
  const section = element('section', undefined, 'risk-workspace');
  section.setAttribute('aria-labelledby', 'risk-title');
  const title = element('h2', 'Model procena transakcije');
  title.id = 'risk-title';
  const intro = element('p',
    'Unesite kanonski IBM HI-Small ID transakcije. Demonstracioni CASE/TX ID-jevi nisu povezani sa ovim podacima.', 'muted');
  const form = element('form');
  const label = element('label', 'Kanonski ID transakcije');
  label.htmlFor = 'risk-transaction-id';
  const input = element('input');
  input.id = 'risk-transaction-id';
  input.name = 'transaction_id';
  input.type = 'text';
  input.maxLength = 160;
  input.autocomplete = 'off';
  input.placeholder = 'ibm-hi-small:<sha256>:row:<broj>';
  const submit = element('button', 'Prikaži risk score', 'button');
  submit.type = 'submit';
  form.addEventListener('submit', event => {
    event.preventDefault();
    assess(input.value.trim());
  });
  form.append(label, input, submit);
  const output = element('div');
  section.append(title, intro, form, output);
  root.append(section);
  return {
    render(state: RiskUiState) {
      output.replaceChildren();
      section.setAttribute('aria-busy', String(state.kind === 'loading'));
      if (state.kind === 'idle') {
        output.append(status('Model procena nije zatražena.'));
      } else if (state.kind === 'loading') {
        output.append(status('Učitavanje model procene…'));
      } else if (state.kind === 'error') {
        output.append(status(state.message, true), button('Pokušaj ponovo', () => assess(input.value.trim())));
      } else {
        const result = state.result;
        const sourceHash = result.transaction_id.split(':')[1];
        output.append(element('p', `${result.risk_score} / 1`, 'risk-score'),
          element('p', 'AML risk score; nije kalibrisana verovatnoća niti nalaz o krivičnom delu.', 'muted'),
          fields([
            ['Status', result.review_status === 'review_recommended'
              ? 'Preporučen ljudski pregled' : 'Ispod praga; ljudska procena ostaje potrebna'],
            ['ID transakcije', result.transaction_id],
            ['Izvor skora', result.source],
            ['Model verzija', result.model_version],
            ['Feature verzija', result.feature_version],
            ['Izvorni skup SHA-256', sourceHash],
            ['Poreklo podataka', 'Sintetički podaci'],
            ['Vreme ocenjivanja (UTC)', result.scored_at],
          ]), element('h3', 'Dostupne činjenice i feature vrednosti'),
          element('p', result.explanation, 'explanation'));
        if (result.review_status === 'review_recommended') {
          const link = element('a', 'Otvori objavljeni modelski slučaj', 'button');
          link.href = '/model-cases?transaction=' + encodeURIComponent(result.transaction_id);
          output.append(link);
        }
      }
    },
  };
}

// T240 presentation boundary: only render an already decoded, authorized response.
// T251 must supply that response before this becomes a live screen.
export function modelResultsContent(results: ModelResults): HTMLElement {
  const section = element('section', undefined, 'detail-section');
  section.append(element('h2', 'Agregatni rezultati modela'), fields([
    ['Model verzija', results.model_version],
    ['Feature verzija', results.feature_version],
    ['Verzija podataka', results.dataset_version],
    ['Prag', results.threshold === null ? 'Nije dostupan' : String(results.threshold)],
    ['Kalibracija', results.calibration_status === 'assessed' ? 'Procenjena' : 'Nije procenjena'],
  ]));
  for (const partition of results.partitions) {
    const block = element('section', undefined, 'detail-section');
    block.append(element('h3', `Particija: ${partition.partition}`),
      element('p', partition.state === 'available' ? 'Dostupni agregati — sintetički podaci'
        : partition.state === 'not_authorized' ? 'Evaluacija nije odobrena'
          : 'Rezultati nisu dostupni', 'muted'),
      fields([
        ['Vremenski obuhvat (UTC)', partition.coverage_utc],
        ['Broj redova', String(partition.row_count)],
        ['Pozitivni primjeri', String(partition.positive_count)],
        ['Negativni primjeri', String(partition.negative_count)],
      ]));
    if (partition.state === 'available') {
      block.append(fields(partition.metrics.map(metric => [metric.name,
        `${metric.value === null ? 'Nedefinisano' : metric.value} ${metric.unit}; imenilac ${metric.denominator}`] as const)));
    }
    section.append(block);
  }
  const limitations = element('ul');
  for (const item of results.limitations) limitations.append(element('li', item));
  section.append(element('h3', 'Ograničenja'), limitations);
  return section;
}

export type ModelResultsUiState = { kind: 'idle' } | { kind: 'loading' }
  | { kind: 'success'; result: ModelResults }
  | { kind: 'unavailable' } | { kind: 'unauthorized' }
  | { kind: 'error'; message: string };

export function createModelResultsView(root: HTMLElement, load: () => void) {
  const section = element('section', undefined, 'risk-workspace');
  section.setAttribute('aria-labelledby', 'results-title');
  const title = element('h2', 'Agregatni rezultati modela');
  title.id = 'results-title';
  const output = element('div');
  section.append(title, element('p',
    'Prikaz postojećih odobrenih izvještaja za zamrznuti model. Ne pokreće evaluaciju.', 'muted'),
  button('Učitaj rezultate', load), output);
  root.append(section);
  return {
    render(state: ModelResultsUiState) {
      output.replaceChildren();
      section.setAttribute('aria-busy', String(state.kind === 'loading'));
      if (state.kind === 'idle') output.append(status('Rezultati nisu učitani.'));
      else if (state.kind === 'loading') output.append(status('Učitavanje agregatnih rezultata…'));
      else if (state.kind === 'success') output.append(modelResultsContent(state.result));
      else {
        const message = state.kind === 'unavailable' ? 'Agregatni rezultati nisu dostupni.'
          : state.kind === 'unauthorized' ? 'Test evaluacija nije odobrena za ovaj režim.'
            : state.message;
        output.append(status(message, true), button('Pokušaj ponovo', load));
      }
    },
  };
}

export type EdaUiState = { kind: 'loading' } | { kind: 'success'; result: EdaSummary }
  | { kind: 'unavailable' } | { kind: 'error'; message: string };

function edaSeriesTable(series: EdaSeries): HTMLElement {
  const section = element('section', undefined, 'eda-series');
  const heading = element('h3', series.label);
  const unit = series.unit === 'transactions' ? 'transakcije'
    : `${series.currency} — zbir iznosa, ${series.side === 'paid' ? 'plaćeno' : 'primljeno'}`;
  section.append(heading, element('p', `Jedinica: ${unit}; imenilac: ${series.denominator} transakcija${series.timezone ? '; UTC' : ''}.`, 'muted'));
  if (series.values.length === 0) {
    section.append(status('Nema podataka za ovu seriju.'));
    return section;
  }
  const table = element('table', undefined, 'eda-table');
  const caption = element('caption', `${series.label} — jedinica: ${unit}; imenilac: ${series.denominator} transakcija.`);
  const head = element('thead');
  const headers = element('tr');
  headers.append(element('th', series.timezone ? 'UTC period' : 'Kategorija'),
    element('th', series.unit === 'transactions' ? 'Broj transakcija' : `Iznos (${series.currency})`));
  head.append(headers);
  const body = element('tbody');
  const maximum = Math.max(...series.values, 0);
  series.bucket_labels.forEach((bucket, index) => {
    const row = element('tr');
    const label = element('th', bucket);
    label.scope = 'row';
    const value = element('td');
    const number = element('span', String(series.values[index]), 'eda-value');
    const bar = element('span', undefined, 'eda-bar');
    bar.setAttribute('aria-hidden', 'true');
    bar.style.width = `${maximum === 0 ? 0 : (series.values[index] / maximum) * 100}%`;
    value.append(number, bar);
    row.append(label, value);
    body.append(row);
  });
  table.append(caption, head, body);
  section.append(table);
  return section;
}

export function createEdaView(root: HTMLElement, load: () => void) {
  const header = element('header', undefined, 'app-header');
  header.append(element('p', 'SINTETIČKI PODACI', 'eyebrow'),
    element('h1', 'FraudLens AI — EDA'),
    element('p', 'Pregled provjerenih agregata izvora, bez pojedinačnih transakcija i labela.', 'intro'));
  const navigation = element('nav', undefined, 'site-nav');
  navigation.setAttribute('aria-label', 'Glavna navigacija');
  const home = element('a', '← Pregled slučajeva i modela');
  home.href = '/';
  navigation.append(home);
  header.append(navigation);
  const output = element('section', undefined, 'risk-workspace');
  output.setAttribute('aria-labelledby', 'eda-title');
  const title = element('h2', 'Agregatni pregled podataka');
  title.id = 'eda-title';
  const content = element('div');
  output.append(title, content);
  root.replaceChildren(header, output);

  return {
    render(state: EdaUiState) {
      content.replaceChildren();
      output.setAttribute('aria-busy', String(state.kind === 'loading'));
      if (state.kind === 'loading') {
        content.append(status('Učitavanje EDA sažetka…'));
      } else if (state.kind === 'unavailable' || state.kind === 'error') {
        content.append(status(state.kind === 'unavailable' ? 'EDA podaci nisu dostupni.'
          : state.message, true), button('Pokušaj ponovo', load));
      } else {
        const result = state.result;
        if (result.accepted_count === 0) {
          content.append(status('Nema podataka u prihvaćenom izvoru. Prazan EDA sažetak.'));
          return;
        }
        content.append(element('p', 'Sintetički IBM HI-Small podaci. Vremena su prikazana po UTC projektnoj konvenciji; izvorna vremenska zona i upstream verzija nisu potvrđene.', 'muted'),
          fields([
            ['Verzija podataka', result.dataset_version],
            ['Izvorni SHA-256', result.source_sha256],
            ['Početak obuhvata (UTC)', result.coverage_start_utc ?? 'Nije dostupan'],
            ['Kraj obuhvata (UTC)', result.coverage_end_utc ?? 'Nije dostupan'],
            ['Ukupno redova', String(result.source_count)],
            ['Prihvaćeno', String(result.accepted_count)],
            ['Odbijeno', `${result.rejected_count}; imenilac: ${result.source_count} redova izvora`],
            ['Warm-up', `${result.warmup_count}; imenilac: ${result.accepted_count} prihvaćenih`],
            ['Podobno za skoriranje', `${result.scoreable_count}; imenilac: ${result.accepted_count} prihvaćenih`],
          ]));
        const quality = element('section', undefined, 'detail-section');
        quality.append(element('h2', 'Kvalitet izvora'));
        const qualityEntries = Object.entries(result.quality_counts);
        quality.append(qualityEntries.length
          ? fields(qualityEntries.map(([key, count]) => [key, `${count}; imenilac: ${result.source_count} redova izvora`]))
          : element('p', 'Nema dodatnih brojača odbijanja u provjerenom manifestu.', 'muted'));
        content.append(quality);
        for (const [heading, series] of [
          ['Kategorije', result.series.filter(item => item.unit === 'transactions' && item.timezone === null)],
          ['Broj transakcija kroz vrijeme', result.series.filter(item => item.unit === 'transactions' && item.timezone === 'UTC')],
          ['Iznosi po valuti i strani', result.series.filter(item => item.unit === 'amount')],
        ] as const) {
          const group = element('section', undefined, 'detail-section');
          group.append(element('h2', heading));
          if (series.length === 0) group.append(status('Nema dostupnih serija.'));
          else for (const item of series) {
            if (item.unit === 'amount') {
              const disclosure = element('details', undefined, 'eda-disclosure');
              disclosure.append(element('summary', `${item.side === 'paid' ? 'Plaćeno' : 'Primljeno'} — ${item.currency}; imenilac: ${item.denominator} transakcija`),
                edaSeriesTable(item));
              group.append(disclosure);
            } else group.append(edaSeriesTable(item));
          }
          content.append(group);
        }
        content.append(element('p', `Izostavljene valute zbog granice prikaza: plaćeno ${result.omitted_amount_currencies.paid}, primljeno ${result.omitted_amount_currencies.received}. Iznosi se ne sabiraju između valuta.`, 'muted'));
      }
    },
  };
}
