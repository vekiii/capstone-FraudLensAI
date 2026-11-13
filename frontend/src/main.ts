import { ApiError, getCase, getCases } from './api';
import type { CaseDetail, CaseList, CaseSummary } from './contracts';
import { createCaseView } from './views';
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

const root = document.querySelector<HTMLElement>('#app');
if (root) {
  const dispose = mountCaseApp(root);
  import.meta.hot?.dispose(dispose);
}
