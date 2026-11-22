import type { KnowledgeDocument, Passage, Search } from './contracts';

import type { Run, Evidence } from './contracts';
import type { ReviewInput } from './api';
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

export function createReportView(root: HTMLElement, actions: { start(): void; refresh(): void; select(id: string): void; evidence(id: string): void; retry(reuse: boolean): void; cancel(): void; parent(): void; review(body: ReviewInput): void }, sourceMode: Run['source_mode']) {
  const heading = node('h2', 'AI istraga'); heading.tabIndex = -1;
  const list = node('div'); const panel = node('section'); panel.setAttribute('aria-live', 'polite');
  const source = node('section'); source.setAttribute('aria-live', 'polite');
  const history = node('div');
  const start = node('button', 'Pokreni novu istragu'); start.type = 'button'; start.dataset.start = ''; start.addEventListener('click', actions.start); start.disabled = true;
  const refresh = node('button', 'Osveži sačuvano stanje'); refresh.type = 'button'; refresh.dataset.refresh = ''; refresh.addEventListener('click', actions.refresh);
  const notice = sourceMode === 'dataset'
    ? 'Objavljeni skor sintetičke transakcije. AI nacrt podržava ljudsku odluku.'
    : 'Sintetički fixture podaci, bez ML predikcije. Skor nije verovatnoća prevare. AI nacrt podržava ljudsku odluku.';
  root.replaceChildren(heading, node('p', notice), start, refresh, list, history, panel, source);
  const section = (title: string) => { panel.append(node('h3', title)); };
  function reviewForm(run: Run) {
    const report = run.report!;
    const form = node('form'); form.dataset.reviewForm = '';
    const title = node('h3', run.review ? 'Korekcija odluke analitičara' : 'Odluka analitičara');
    const label = node('label', 'Odluka '), select = node('select'); select.required = true; select.dataset.disposition = '';
    const blank = node('option', 'Izaberite odluku'); blank.value = ''; select.append(blank);
    const choices = report.draft.outcome === 'needs_information' ? ['request_more_information'] : ['escalate', 'close', 'request_more_information'];
    const names: Record<string, string> = { escalate: 'Eskalirati', close: 'Zatvoriti', request_more_information: 'Zatražiti dodatne podatke' };
    for (const choice of choices) { const option = node('option', names[choice]); option.value = choice; select.append(option); }
    label.append(select);
    const reasonLabel = node('label', 'Obrazloženje (obavezno) '), reason = node('textarea'); reason.required = true; reason.maxLength = 4000; reason.dataset.rationale = ''; reasonLabel.append(reason);
    const noteLabel = node('label', run.review ? 'Beleška o korekciji (obavezno) ' : 'Beleška analitičara (opciono) '), note = node('textarea'); note.maxLength = 4000; note.required = !!run.review; note.dataset.correctionNote = ''; noteLabel.append(note);
    const submit = node('button', run.review ? 'Sačuvaj povezanu korekciju' : 'Sačuvaj odluku'); submit.type = 'submit'; submit.dataset.reviewSubmit = '';
    const message = node('p'); message.setAttribute('role', 'alert');
    form.append(title, node('p', `Odluka se vezuje za AI nacrt ${report.report_id}, revizija pokušaja ${run.revision}. Originalni nacrt i dokazi ostaju sačuvani. Ovo nije ocena kvaliteta LLM-a.`), label, reasonLabel, noteLabel, submit, message);
    form.addEventListener('submit', e => {
      e.preventDefault(); const rationale = reason.value.trim(), correction = note.value.trim();
      if (!choices.includes(select.value) || !rationale || [...rationale].length > 2000 || [...correction].length > 2000 || (run.review && !correction)) { message.textContent = 'Izaberite odluku i unesite obavezno obrazloženje i belešku za korekciju.'; return; }
      actions.review({ report_id: report.report_id, disposition: select.value as ReviewInput['disposition'], rationale, correction_note: correction || null, supersedes_review_id: run.review?.review_id ?? null });
    });
    panel.append(form);
  }
  return {
    loading() { start.disabled = true; panel.replaceChildren(node('p', 'Učitavanje sačuvane istrage…')); source.replaceChildren(); },
    saved(runs: Run[], total: number, truncated: boolean) {
      start.disabled = false; list.replaceChildren(node('p', `Sačuvano istraga: ${total}${truncated ? '; prikazano poslednjih 20' : ''}.`));
      for (const run of runs) { const select = node('button', `${run.created_at} | ${run.state}`); select.type = 'button'; select.dataset.attempt = run.attempt_id; select.addEventListener('click', () => actions.select(run.attempt_id)); list.append(select); }
    },
    empty() { panel.replaceChildren(node('p', 'Nema sačuvane istrage. Pokretanje je izričita radnja.')); },
    historical(runs: Run[]) { history.replaceChildren(); for (const run of runs) { const button = node('button', `Istorijski izveštaj | ${run.created_at}`); button.dataset.history = run.attempt_id; button.addEventListener('click', () => actions.select(run.attempt_id)); history.append(button); } },
    recoveryError(code: string, blocked = false) { const alert = node('p', `${code}. ${blocked ? 'Osvežite sačuvano stanje pre nove radnje.' : 'Ishod radnje nije potvrđen; ponovite istu radnju ili osvežite stanje.'}`); alert.setAttribute('role', 'alert'); panel.append(alert); if (blocked) { start.disabled = true; panel.querySelectorAll<HTMLButtonElement>('button[data-retry],button[data-cancel],button[data-review-submit]').forEach(button => { button.disabled = true; }); } },
    run(run: Run, { historicalAttempt = false, sourceContextChanged = false } = {}) {
      const readOnly = historicalAttempt || sourceContextChanged;
      panel.replaceChildren(); source.replaceChildren(); start.disabled = ['created', 'gathering_evidence', 'drafting'].includes(run.state);
      const status = node('p', run.state === 'created' ? 'Posao je sačuvan i čeka worker.' : `Stanje: ${run.state}`); status.dataset.runState = run.state; panel.append(status);
      if (readOnly) panel.append(node('p', 'Istorijski pokušaj — samo za čitanje.'));
      if (sourceContextChanged) panel.append(node('p', 'Sačuvani pokušaj je vezan za prethodni kontekst izvora.'));
      if (run.parent_attempt_id) { panel.append(node('p', `Ponovljeni pokušaj; prethodni: ${run.parent_attempt_id}. Prethodni zahtevi mogu imati nepoznat ishod i potrošnju.`)); const parent = node('button', 'Prikaži prethodni pokušaj'); parent.dataset.parent = ''; parent.addEventListener('click', actions.parent); panel.append(parent); }
      if (!readOnly && ['created', 'gathering_evidence', 'drafting'].includes(run.state)) { const cancel = node('button', 'Otkaži pokušaj'); cancel.dataset.cancel = ''; cancel.addEventListener('click', actions.cancel); panel.append(cancel); }
      if (!readOnly && ['failed', 'cancelled', 'needs_information'].includes(run.state)) {
        panel.append(node('p', 'Novi pokušaj može izazvati dodatnu potrošnju; prethodni zahtev nije nužno bio besplatan.'));
        const label = node('label', 'Ponovo koristi proverene dokaze '); const reuse = node('input'); reuse.type = 'checkbox'; reuse.checked = true; reuse.dataset.reuse = ''; label.append(reuse);
        const retry = node('button', 'Pokreni novi pokušaj'); retry.dataset.retry = ''; retry.addEventListener('click', () => actions.retry(reuse.checked)); panel.append(label, retry);
      }
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
      if (run.review) {
        const review = run.review;
        section('Sačuvana odluka analitičara');
        panel.append(node('p', `${review.actor} | ${review.created_at} | ${review.disposition} | ${review.review_id}`), node('p', review.rationale));
        if (review.correction_note) panel.append(node('p', review.correction_note));
        if (review.supersedes_review_id) panel.append(node('p', `Korekcija prethodne odluke: ${review.supersedes_review_id}. Prethodni zapis je sačuvan.`));
        panel.append(node('p', 'Lokalni zapis odluke; nije ocena kvaliteta LLM-a niti potpis nezavisnog evaluatora.'));
      }
      if (!readOnly && ['ready_for_review', 'needs_information', 'reviewed'].includes(run.state)) reviewForm(run);
    },
    restoreReview(body: ReviewInput) {
      const select = panel.querySelector<HTMLSelectElement>('[data-disposition]'), reason = panel.querySelector<HTMLTextAreaElement>('[data-rationale]'), note = panel.querySelector<HTMLTextAreaElement>('[data-correction-note]');
      if (select && reason && note) { select.value = body.disposition; reason.value = body.rationale; note.value = body.correction_note ?? ''; }
    },
    paused() { panel.append(node('p', 'Automatska provera je zaustavljena. Osvežite sačuvano stanje; novi provider zahtev se time ne pokreće.')); },
    evidence(item: Evidence, corpus: string) {
      source.replaceChildren(); const title = node('h3', 'Sačuvani dokaz'); title.tabIndex = -1; source.append(title, node('pre', item.text)); title.focus();
      for (const fact of item.facts) source.append(node('p', `${fact.path}: ${fact.value}`));
      source.append(node('p', `Vraćeno: ${item.returned_count}; raspoloživo: ${item.eligible_count ?? 'nepoznato'}; skraćeno: ${item.truncated ? 'da' : 'ne'}.`));
      if (item.history) source.append(node('p', `Istorija: ${item.history.availability}; pokrivenost: ${item.history.coverage}; do: ${item.history.cutoff ?? 'nepoznato'}; ${item.history.reason ?? ''}`));
      if (item.passage) { const p = item.passage, d = p.document; source.append(node('p', `Tačna sačuvana verzija | ${d.title} | ${d.version} | ${d.origin_kind} | ${d.jurisdiction} | ${p.section}`), node('p', `Korpus izveštaja: ${corpus}`), node('p', d.source_uri), node('p', d.applicability_notes), node('p', d.reuse_terms), node('p', `Objavljeno: ${d.published_at ?? d.unknown_date_reason}; preuzeto: ${d.retrieved_at}; pregledao: ${d.reviewed_by} (${d.reviewed_at})`), node('pre', p.text)); }
    },
    error(code = 'unavailable') {
      start.disabled = true;
      const text = code === 'stale_snapshot' && sourceMode === 'dataset'
        ? 'Izabrani dataset pregled više nije aktivan (stale_snapshot). Osvežite stranicu i ponovo otvorite slučaj.'
        : `Istraga nije spremna ili odgovor nije ispravan (${code}). Osvežite stanje.`;
      const message = node('p', text); message.setAttribute('role', 'alert'); panel.replaceChildren(message); source.replaceChildren();
    },
    evidenceError() { source.replaceChildren(node('p', 'Dokaz nije dostupan za ovaj izveštaj.')); },
  };
}
