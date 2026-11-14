import type { KnowledgeDocument, Passage, Search } from './contracts';

import type { Run, Evidence } from './contracts';
function node<K extends keyof HTMLElementTagNameMap>(tag: K, text?: string) { const element = document.createElement(tag); if (text !== undefined) element.textContent = text; return element; }
export function createKnowledgeView(root: HTMLElement, actions: { search(query: string): void; select(id: string): void; retry(): void }) {
  const title = node('h1', 'Pretraga izvora'); title.tabIndex = -1;
  const form = node('form'); const label = node('label', 'Upit za pretragu ');
  const input = node('input'); input.maxLength = 500; input.required = true; label.append(input);
  const submit = node('button', 'Pretraži'); submit.type = 'submit'; form.append(label, submit);
  form.addEventListener('submit', e => { e.preventDefault(); actions.search(input.value); });
  const panel = node('section'); panel.setAttribute('aria-live', 'polite');
  root.replaceChildren(title, node('p', 'Lokalni pregled izvora. Demo prag nije potvrda kvaliteta; skor nije verovatnoća. Najviše 5 pogodaka.'), form, panel);
  const heading = (text: string) => { const h = node('h2', text); h.tabIndex = -1; panel.append(h); h.focus(); };
  function metadata(document: KnowledgeDocument) {
    panel.append(node('p', `${document.title} | ${document.version} | ${document.origin_kind} | ${document.jurisdiction}`),
      node('p', document.applicability_notes), node('p', document.source_uri),
      node('p', `Objavljeno: ${document.published_at ?? document.unknown_date_reason}; preuzeto: ${document.retrieved_at}`), node('p', document.reuse_terms));
  }
  return {
    loading() { panel.replaceChildren(node('p', 'Učitavanje…')); },
    ready(documents: KnowledgeDocument[]) { panel.replaceChildren(); panel.append(node('p', 'Unesite upit.')); for (const doc of documents) metadata(doc); },
    results(result: Search) {
      panel.replaceChildren(); heading(result.status === 'no_match' ? 'Nema dovoljno dobrog pogotka.' : 'Rezultati');
      if (result.truncated) panel.append(node('p', 'Prikazano prvih 5; postoje dodatni pogoci.'));
      for (const hit of result.hits) { const button = node('button', `${hit.rank}. ${hit.passage.document.title} — ${hit.passage.section}`); button.type = 'button'; button.dataset.passage = hit.passage.passage_id; button.addEventListener('click', () => actions.select(hit.passage.passage_id)); panel.append(button); }
    },
    passage(value: Passage) { panel.replaceChildren(); heading('Izvor — ' + value.section); metadata(value.document); const pre = node('pre', value.text); pre.style.whiteSpace = 'pre-wrap'; panel.append(pre); },
    error() { panel.replaceChildren(); heading('Pretraga nije spremna ili zahtev nije uspeo.'); const retry = node('button', 'Pokušaj ponovo'); retry.type = 'button'; retry.addEventListener('click', actions.retry); panel.append(retry); },
  };
}

export function createReportView(root: HTMLElement, actions: { start(): void; refresh(): void; select(id: string): void; evidence(id: string): void }) {
  const heading = node('h2', 'AI istraga'); heading.tabIndex = -1;
  const list = node('div'); const panel = node('section'); panel.setAttribute('aria-live', 'polite');
  const source = node('section'); source.setAttribute('aria-live', 'polite');
  const start = node('button', 'Pokreni novu istragu'); start.type = 'button'; start.dataset.start = ''; start.addEventListener('click', actions.start); start.disabled = true;
  const refresh = node('button', 'Osveži sačuvano stanje'); refresh.type = 'button'; refresh.dataset.refresh = ''; refresh.addEventListener('click', actions.refresh);
  root.replaceChildren(heading, node('p', 'Sintetički fixture podaci, bez ML predikcije. Skor nije verovatnoća prevare. AI nacrt podržava ljudsku odluku.'), start, refresh, list, panel, source);
  const section = (title: string) => { panel.append(node('h3', title)); };
  return {
    loading() { start.disabled = true; panel.replaceChildren(node('p', 'Učitavanje sačuvane istrage…')); source.replaceChildren(); },
    saved(runs: Run[], total: number, truncated: boolean) {
      start.disabled = false; list.replaceChildren(node('p', `Sačuvano istraga: ${total}${truncated ? '; prikazano poslednjih 20' : ''}.`));
      for (const run of runs) { const select = node('button', `${run.created_at} | ${run.state}`); select.type = 'button'; select.dataset.attempt = run.attempt_id; select.addEventListener('click', () => actions.select(run.attempt_id)); list.append(select); }
    },
    empty() { panel.replaceChildren(node('p', 'Nema sačuvane istrage. Pokretanje je izričita radnja.')); },
    run(run: Run) {
      panel.replaceChildren(); source.replaceChildren(); start.disabled = ['created', 'gathering_evidence', 'drafting'].includes(run.state);
      const status = node('p', run.state === 'created' ? 'Posao je sačuvan i čeka worker.' : `Stanje: ${run.state}`); status.dataset.runState = run.state; panel.append(status);
      panel.append(node('p', run.provider_mode === 'test' ? 'TEST provider — autorski odgovori; nije procena kvaliteta LLM-a.' : `Provider: ${run.returned_model ?? run.requested_model ?? 'nepoznat'}`),
        node('p', `Provider zahtevi: ${run.budget.provider_requests}/8; alati: ${run.budget.tool_calls}/12.`), node('p', `Kontekst: ${run.context_revision}; snapshot: ${run.snapshot_ref}; korpus: ${run.corpus_version}`));
      for (const step of run.trace) panel.append(node('p', `${step.sequence}. ${step.name}: ${step.status} (${step.elapsed_ms} ms)`));
      if (run.failure) { const failure = node('p', `Istraga nije završena: ${run.failure.code}${run.failure.outcome_unknown ? '; ishod prethodnog zahteva nepoznat' : ''}.`); failure.setAttribute('role', 'alert'); panel.append(failure); }
      if (!run.report) return;
      panel.append(node('p', 'Automatska provera šeme i referenci: prošla.'), node('p', run.report.semantic_review === 'not_reviewed' ? 'Semantički pregled: na čekanju' : 'Semantički pregled: sa beleškama'));
      const draft = run.report.draft;
      const sections = [['Sažetak', draft.summary], ['Uočene činjenice', draft.observed_facts], ['Indikatori rizika', draft.risk_indicators], ['Alternativna objašnjenja', draft.alternative_explanations], ['Preporučene provere', draft.recommended_checks]] as const;
      for (const [title, claims] of sections) {
        section(title);
        if (!claims.length) panel.append(node('p', 'Nije navedeno.'));
        for (const claim of claims) {
          panel.append(node('p', `[${claim.kind}] ${claim.text}`));
          for (const exact of claim.exact_assertions) panel.append(node('p', `${exact.path}: ${exact.value}`));
          for (const quote of claim.quotes) panel.append(node('blockquote', quote.text));
          for (const ref of claim.evidence_refs) { const link = node('button', 'Dokaz ' + ref); link.type = 'button'; link.dataset.evidence = ref; link.addEventListener('click', () => actions.evidence(ref)); panel.append(link); }
        }
      }
      for (const [title, values] of [['Nedostajuće informacije', draft.missing_information], ['Ograničenja', draft.limitations]] as const) { section(title); for (const value of values) panel.append(node('p', value)); }
    },
    paused() { panel.append(node('p', 'Automatska provera je zaustavljena. Osvežite sačuvano stanje; novi provider zahtev se time ne pokreće.')); },
    evidence(item: Evidence, corpus: string) {
      source.replaceChildren(); const title = node('h3', 'Sačuvani dokaz'); title.tabIndex = -1; source.append(title, node('pre', item.text)); title.focus();
      for (const fact of item.facts) source.append(node('p', `${fact.path}: ${fact.value}`));
      source.append(node('p', `Vraćeno: ${item.returned_count}; raspoloživo: ${item.eligible_count ?? 'nepoznato'}; skraćeno: ${item.truncated ? 'da' : 'ne'}.`));
      if (item.history) source.append(node('p', `Istorija: ${item.history.availability}; pokrivenost: ${item.history.coverage}; do: ${item.history.cutoff ?? 'nepoznato'}; ${item.history.reason ?? ''}`));
      if (item.passage) { const p = item.passage, d = p.document; source.append(node('p', `Tačna sačuvana verzija | ${d.title} | ${d.version} | ${d.origin_kind} | ${d.jurisdiction} | ${p.section}`), node('p', `Korpus izveštaja: ${corpus}`), node('p', d.source_uri), node('p', d.applicability_notes), node('p', d.reuse_terms), node('p', `Objavljeno: ${d.published_at ?? d.unknown_date_reason}; preuzeto: ${d.retrieved_at}; pregledao: ${d.reviewed_by} (${d.reviewed_at})`), node('pre', p.text)); }
    },
    error(code = 'unavailable') { start.disabled = true; const message = node('p', `Istraga nije spremna ili odgovor nije ispravan (${code}). Osvežite stanje.`); message.setAttribute('role', 'alert'); panel.replaceChildren(message); source.replaceChildren(); },
    evidenceError() { source.replaceChildren(node('p', 'Dokaz nije dostupan za ovaj izveštaj.')); },
  };
}
