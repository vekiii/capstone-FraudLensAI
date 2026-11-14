import type { KnowledgeDocument, Passage, Search } from './contracts';

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
