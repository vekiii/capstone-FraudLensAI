import { ApiError, getCase, getCases, getEdaSummary, getModelResults, getTransactionRisk } from './api';
import type { CaseDetail, CaseList, CaseSummary } from './contracts';
import { ContractValidationError, decodeCanonicalTransactionId } from './contracts';
import { createCaseView, createEdaView, createModelResultsView, createRiskView } from './views';
import type { UiState } from './views';
import './styles.css';

export interface CaseClient {
  getCases(options: { signal: AbortSignal }): Promise<CaseList>;
  getCase(caseId: string, options: { signal: AbortSignal }): Promise<CaseDetail>;
}

export function mountCaseApp(
  root: HTMLElement, client: CaseClient = { getCases, getCase },
): () => void {
  let items: CaseSummary[] = [];
  let state: UiState = { kind: 'list-loading' };
  let generation = 0;
  let pending: AbortController | undefined;
  let disposed = false;

  const view = createCaseView(root, {
    select: caseId => { void loadDetail(caseId); },
    back: () => {
      const previous = state.kind === 'detail' ? state.detail.case_id
        : 'caseId' in state ? state.caseId : undefined;
      invalidate();
      state = { kind: 'list' };
      view.render(state, items, previous);
    },
    retry: () => {
      if ('caseId' in state) void loadDetail(state.caseId);
      else void loadList();
    },
  });

  function invalidate(): number {
    // Invalidate first: even a synchronous abort reaction belongs to the old request.
    generation += 1;
    pending?.abort();
    pending = undefined;
    return generation;
  }

  function begin(next: UiState, focus = false) {
    const token = invalidate();
    const controller = new AbortController();
    pending = controller;
    state = next;
    // Replacing the panel immediately removes all previous detail content.
    view.render(state, items, focus ? 'panel' : undefined);
    return { token, controller };
  }

  function current(token: number): boolean {
    return !disposed && token === generation;
  }

  function publicError(error: unknown): ApiError {
    return error instanceof ApiError ? error : new ApiError('internal_error');
  }

  async function loadList(): Promise<void> {
    const { token, controller } = begin({ kind: 'list-loading' });
    try {
      const result = await client.getCases({ signal: controller.signal });
      if (!current(token)) return;
      items = [...result.items].sort((left, right) =>
        left.case_id < right.case_id ? -1 : left.case_id > right.case_id ? 1 : 0);
      state = { kind: 'list' };
      view.render(state, items);
    } catch (error) {
      if (!current(token)) return;
      state = { kind: 'list-error', error: publicError(error) };
      view.render(state, items);
    } finally {
      if (current(token)) pending = undefined;
    }
  }

  async function loadDetail(caseId: string): Promise<void> {
    const { token, controller } = begin({ kind: 'detail-loading', caseId }, true);
    try {
      const detail = await client.getCase(caseId, { signal: controller.signal });
      if (!current(token)) return;
      state = { kind: 'detail', detail };
      view.render(state, items);
    } catch (error) {
      if (!current(token)) return;
      const failure = publicError(error);
      state = failure.code === 'case_not_found' ? { kind: 'not-found', caseId }
        : { kind: 'detail-error', caseId, error: failure };
      view.render(state, items);
    } finally {
      if (current(token)) pending = undefined;
    }
  }

  void loadList();
  return () => {
    disposed = true;
    invalidate();
    root.replaceChildren();
  };
}

export function mountRiskApp(root: HTMLElement): () => void {
  let pending: AbortController | undefined;
  let generation = 0;
  let disposed = false;
  const view = createRiskView(root, id => { void loadRisk(id); });
  view.render({ kind: 'idle' });
  async function loadRisk(id: string) {
    pending?.abort();
    const token = ++generation;
    let canonical: string;
    try {
      canonical = decodeCanonicalTransactionId(id);
    } catch (error) {
      if (!(error instanceof ContractValidationError)) throw error;
      view.render({ kind: 'error', message: 'Unesite ispravan kanonski ID transakcije.' });
      return;
    }
    const controller = new AbortController();
    pending = controller;
    view.render({ kind: 'loading' });
    try {
      const result = await getTransactionRisk(canonical, { signal: controller.signal });
      if (!disposed && token === generation) view.render({ kind: 'success', result });
    } catch (error) {
      if (disposed || token !== generation) return;
      const safe = error instanceof ApiError ? error : new ApiError('internal_error');
      view.render({ kind: 'error', message: safe.message });
    } finally {
      if (token === generation) pending = undefined;
    }
  }
  return () => { disposed = true; generation += 1; pending?.abort(); };
}

export function mountModelResultsApp(root: HTMLElement): () => void {
  let pending: AbortController | undefined;
  let generation = 0;
  let disposed = false;
  const view = createModelResultsView(root, () => { void load(); });
  view.render({ kind: 'idle' });
  async function load() {
    pending?.abort();
    const token = ++generation;
    const controller = new AbortController();
    pending = controller;
    view.render({ kind: 'loading' });
    try {
      const result = await getModelResults({ signal: controller.signal });
      if (!disposed && token === generation) view.render({ kind: 'success', result });
    } catch (error) {
      if (disposed || token !== generation) return;
      const safe = error instanceof ApiError ? error : new ApiError('internal_error');
      view.render(safe.code === 'evaluation_not_authorized' ? { kind: 'unauthorized' }
        : safe.code === 'results_unavailable' ? { kind: 'unavailable' }
          : { kind: 'error', message: safe.message });
    } finally {
      if (token === generation) pending = undefined;
    }
  }
  return () => { disposed = true; generation += 1; pending?.abort(); };
}

export function mountEdaApp(root: HTMLElement): () => void {
  let pending: AbortController | undefined;
  let generation = 0;
  let disposed = false;
  const view = createEdaView(root, () => { void load(); });
  async function load() {
    pending?.abort();
    const token = ++generation;
    const controller = new AbortController();
    pending = controller;
    view.render({ kind: 'loading' });
    try {
      const result = await getEdaSummary({ signal: controller.signal });
      if (!disposed && token === generation) view.render({ kind: 'success', result });
    } catch (error) {
      if (disposed || token !== generation) return;
      const safe = error instanceof ApiError ? error : new ApiError('internal_error');
      view.render(safe.code === 'dataset_unavailable' ? { kind: 'unavailable' }
        : { kind: 'error', message: safe.message });
    } finally {
      if (token === generation) pending = undefined;
    }
  }
  void load();
  return () => { disposed = true; generation += 1; pending?.abort(); };
}

const root = document.querySelector<HTMLElement>('#app');
if (root) {
  if (window.location.pathname === '/eda') {
    const disposeEda = mountEdaApp(root);
    import.meta.hot?.dispose(disposeEda);
  } else {
    const disposeCases = mountCaseApp(root);
    const disposeRisk = mountRiskApp(root);
    const disposeResults = mountModelResultsApp(root);
    import.meta.hot?.dispose(() => { disposeCases(); disposeRisk(); disposeResults(); });
  }
}
