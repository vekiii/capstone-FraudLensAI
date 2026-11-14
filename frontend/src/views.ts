import type { ApiError } from './api';
import type { CaseDetail, CaseDetailResponse, CaseDetailV2, CaseListResponse,
  ScoreSource } from './contracts';

export type UiState =
  | { kind: 'list-loading' }
  | { kind: 'list' }
  | { kind: 'list-error'; error: ApiError }
  | { kind: 'detail-loading'; caseId: string }
  | { kind: 'detail'; detail: CaseDetailResponse }
  | { kind: 'detail-error'; caseId: string; error: ApiError }
  | { kind: 'stale'; caseId: string; error: ApiError }
  | { kind: 'not-found'; caseId: string };

interface Actions {
  select(caseId: string): void;
  back(): void;
  retry(): void;
  refreshList(): void;
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

function datasetDetailContent(detail: CaseDetailV2) {
  const fact = detail.transaction;
  const risk = detail.risk_assessment;
  const transaction = element('section', undefined, 'detail-section');
  transaction.append(element('h3', 'Transakcija iz sintetičkog IBM skupa'), fields([
    ['ID transakcije', fact.transaction_id],
    ['Vrijeme događaja (UTC)', fact.event_time_utc],
    ['Izvorno vrijeme', fact.event_time_raw],
    ['Osnova vremena', fact.time_basis],
    ['Pošiljalac', `${fact.sender.bank} · ${fact.sender.account}`],
    ['Primalac', `${fact.receiver.bank} · ${fact.receiver.account}`],
    ['Plaćeno', `${fact.paid.amount} ${fact.paid.currency}`],
    ['Primljeno', `${fact.received.amount} ${fact.received.currency}`],
    ['Format plaćanja', fact.payment_format ?? 'Nije zabilježeno'],
  ]));
  const assessment = element('section', undefined, 'detail-section');
  assessment.append(element('h3', 'Procjena rizika'),
    element('p', `${risk.score} / 1`, 'risk-score'),
    element('p', risk.score_source === 'model'
      ? 'Procjena modela nije kalibrisana vjerovatnoća niti dokaz krivice.'
      : 'Ordinalni skor pravila nije vjerovatnoća niti dokaz krivice.', 'muted'),
    fields([
      ['Izvor skora', risk.score_source], ['Vrsta skora', risk.score_kind],
      ['Scorer', risk.scorer_version], ['Verzija karakteristika', risk.feature_version],
      ['Dataset', detail.dataset_version], ['Run', risk.run_id],
      ['Vrijeme događaja (UTC)', risk.event_time_utc],
      ['Historija do (isključivo)', risk.history_cutoff_exclusive_at],
      ['Stvarno vrijeme bodovanja (UTC)', risk.scored_at],
      ['Pokrivenost historije', `${risk.history_coverage.state} · `
        + `${risk.history_coverage.start ?? 'nepoznat početak'}`],
    ]), element('h4', 'Objašnjenje'));
  const explanation = risk.explanation;
  if (explanation.status === 'unavailable') {
    assessment.append(element('p', `Objašnjenje nedostupno: ${explanation.reason_code}.`,
      'explanation'));
  } else {
    assessment.append(fields([
      ['Metoda', explanation.method], ['Skala', explanation.explained_scale],
      ['Snapshot digest', explanation.feature_snapshot_digest],
      ['Djelimičan prikaz', explanation.partial ? 'Da' : 'Ne'],
      ['Osnova', explanation.base_value === null ? 'Nije dostupna'
        : String(explanation.base_value)],
      ['Ostatak', explanation.remainder === null ? 'Nije dostupan'
        : String(explanation.remainder)],
    ]));
    const list = element('ul', undefined, 'explanation-items');
    for (const item of explanation.items) {
      list.append(element('li', `${item.feature_key}: ${item.observed_value} ${item.unit}; `
        + `${item.direction} ${item.contribution}`
        + (item.rule_condition ? `; ${item.rule_condition}` : '')));
    }
    assessment.append(list);
  }
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
    render(state: UiState, listing?: CaseListResponse, focus?: string) {
      const dataset = (listing && 'contract_version' in listing)
        || (state.kind === 'detail' && 'contract_version' in state.detail)
        || import.meta.env.VITE_APP_MODE === 'dataset';
      const items = listing?.items ?? [];
      if (dataset) {
        notice.replaceChildren(element('strong', 'Sintetički IBM podaci — pregled procjena'),
          element('p', 'Vrijeme izvora je pretpostavljeno UTC; skor nije dokaz krivice.'));
        navigation.setAttribute('aria-label', 'Upozorenja');
      } else {
        notice.replaceChildren(
          element('strong', 'Demonstracioni podaci — sintetički skor, bez ML predikcije'),
          element('p', 'Podaci su izmišljeni. Rezultati služe isključivo za ilustraciju.'));
        navigation.setAttribute('aria-label', 'Sintetički slučajevi');
      }
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
          if (listing && 'contract_version' in listing) {
            panel.append(status(`Ukupno upozorenja: ${listing.total_alerts}; `
              + `prikazano: ${listing.displayed_count}.`));
            if (listing.truncated) panel.append(element('p',
              'Prikazano je najnovijih 100 upozorenja.', 'muted'));
            if (!items.length) panel.append(element('p', 'Nema upozorenja u aktivnom runu.'));
          } else {
            panel.append(status(items.length ? `Dostupno slučajeva: ${items.length}.`
              : 'Nema dostupnih slučajeva. Lista je prazna.'));
          }
          panel.append(element('p', items.length ? 'Izaberite slučaj za pregled transakcije i skora.'
            : 'Nijedan slučaj nije vraćen. Možete ponovo proveriti dostupnost.', 'muted'));
          if (!items.length) panel.append(button('Pokušaj ponovo', actions.retry));
          break;
        case 'detail-loading':
          panel.append(status('Učitavanje detalja slučaja…'));
          break;
        case 'detail':
          panel.append(...('contract_version' in state.detail
            ? datasetDetailContent(state.detail) : detailContent(state.detail)));
          break;
        case 'stale':
          panel.append(status(state.error.message, true),
            button('Osvježi listu', actions.refreshList));
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
