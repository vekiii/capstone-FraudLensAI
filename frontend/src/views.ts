import type { ApiError } from './api';
import type { CaseDetail, CaseSummary, ModelResults, PredictionResult, ScoreSource } from './contracts';

export type UiState =
  | { kind: 'list-loading' }
  | { kind: 'list' }
  | { kind: 'list-error'; error: ApiError }
  | { kind: 'detail-loading'; caseId: string }
  | { kind: 'detail'; detail: CaseDetail }
  | { kind: 'detail-error'; caseId: string; error: ApiError }
  | { kind: 'not-found'; caseId: string };

interface Actions {
  select(caseId: string): void;
  back(): void;
  retry(): void;
}

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

const sources: Record<ScoreSource, string> = {
  fixture: 'fixture — sintetički primer', rules: 'rules — pravila', model: 'model',
};

function detailContent(detail: CaseDetail) {
  const transaction = element('section', undefined, 'detail-section');
  transaction.append(element('h3', 'Transakcija'), fields([
    ['ID transakcije', detail.transaction.transaction_id],
    ['Vreme transakcije (UTC)', detail.transaction.occurred_at],
    ['Pošiljalac — demo račun', detail.transaction.sender_account],
    ['Primalac — demo račun', detail.transaction.receiver_account],
    ['Iznos', `${detail.transaction.amount} ${detail.transaction.currency}`],
  ]));
  const risk = detail.risk_assessment;
  const assessment = element('section', undefined, 'detail-section');
  assessment.append(element('h3', 'Ilustrativna procena'),
    element('p', `${risk.score} / 1`, 'risk-score'),
    element('p', 'Demonstracioni skor nije verovatnoća prevare.', 'muted'),
    fields([
      ['Izvor skora', sources[risk.source]], ['Verzija', risk.scorer_version],
      ['Vreme ocenjivanja (UTC)', risk.scored_at],
    ]), element('h4', 'Objašnjenje'), element('p', risk.explanation, 'explanation'));
  return [transaction, assessment];
}

export function createCaseView(root: HTMLElement, actions: Actions) {
  const header = element('header', undefined, 'app-header');
  header.append(element('p', 'LOKALNA DEMONSTRACIJA', 'eyebrow'), element('h1', 'FraudLens AI'),
    element('p', 'Pregled sintetičkih transakcija i ilustrativnih skorova.', 'intro'));
  const notice = element('aside', undefined, 'synthetic-notice');
  notice.setAttribute('aria-label', 'Napomena o demonstracionim podacima');
  notice.append(element('strong', 'Demonstracioni podaci — sintetički skor, bez ML predikcije'),
    element('p', 'Podaci su izmišljeni. Rezultati služe isključivo za ilustraciju.'));
  const layout = element('div', undefined, 'workspace');
  const navigation = element('nav', undefined, 'case-navigation');
  navigation.setAttribute('aria-label', 'Sintetički slučajevi');
  const panel = element('section', undefined, 'case-panel');
  panel.setAttribute('aria-labelledby', 'panel-title');
  layout.append(navigation, panel);
  root.replaceChildren(header, notice, layout);

  return {
    render(state: UiState, items: readonly CaseSummary[], focus?: string) {
      const panelHadFocus = panel.contains(document.activeElement);
      const selected = state.kind === 'detail' ? state.detail.case_id
        : 'caseId' in state ? state.caseId : undefined;
      navigation.replaceChildren(element('h2', 'Slučajevi'));
      const selections = new Map<string, HTMLButtonElement>();
      const list = element('ul', undefined, 'case-list');
      for (const item of items) {
        const row = element('li');
        const select = button('', () => actions.select(item.case_id), 'case-choice');
        select.setAttribute('aria-pressed', String(item.case_id === selected));
        select.setAttribute('aria-label', `Otvori ${item.case_id}`);
        select.append(element('strong', item.case_id), element('span', item.transaction_id, 'muted'),
          element('span', `Skor ${item.score} / 1 · ${item.score_source}`, 'case-score'));
        selections.set(item.case_id, select);
        row.append(select);
        list.append(row);
      }
      navigation.append(list);

      panel.replaceChildren();
      const isDetail = selected !== undefined;
      if (isDetail) panel.append(button('← Nazad na listu', actions.back, 'button button-back'));
      const title = element('h2', selected ? `Slučaj ${selected}` : 'Pregled slučajeva');
      title.id = 'panel-title';
      title.tabIndex = -1;
      panel.append(title);
      panel.setAttribute('aria-busy', String(state.kind.endsWith('loading')));

      switch (state.kind) {
        case 'list-loading':
          panel.append(status('Učitavanje slučajeva…'));
          break;
        case 'list':
          panel.append(status(items.length ? `Dostupno slučajeva: ${items.length}.`
            : 'Nema dostupnih slučajeva. Lista je prazna.'));
          panel.append(element('p', items.length ? 'Izaberite slučaj za pregled transakcije i skora.'
            : 'Nijedan slučaj nije vraćen. Možete ponovo proveriti dostupnost.', 'muted'));
          if (!items.length) panel.append(button('Pokušaj ponovo', actions.retry));
          break;
        case 'detail-loading':
          panel.append(status('Učitavanje detalja slučaja…'));
          break;
        case 'detail':
          panel.append(...detailContent(state.detail));
          break;
        case 'not-found':
          panel.append(status(`Slučaj ${state.caseId} nije pronađen.`, true));
          break;
        case 'list-error':
        case 'detail-error':
          // Only ApiError's controlled message reaches this view, never raw errors.
          panel.append(status(`Greška: ${state.error.message}`, true),
            button('Pokušaj ponovo', actions.retry));
          break;
      }
      if (focus && focus !== 'panel') selections.get(focus)?.focus();
      else if (focus === 'panel' || panelHadFocus) title.focus();
    },
  };
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
