import { ApiError, getCase, getCases } from './api';
import type { CaseDetailResponse, CaseListResponse } from './contracts';
import { createCaseView } from './views';
import type { UiState } from './views';
import './styles.css';

export interface CaseClient {
  getCases(options: { signal: AbortSignal; dataset?: boolean }): Promise<CaseListResponse>;
  getCase(caseId: string, options: { signal: AbortSignal; snapshot?: string }):
    Promise<CaseDetailResponse>;
}

export function mountCaseApp(
  root: HTMLElement, client: CaseClient = { getCases, getCase },
): () => void {
  let listing: CaseListResponse | undefined;
  let state: UiState = { kind: 'list-loading' };
  let generation = 0;
  let pending: AbortController | undefined;
  let disposed = false;
  let selectedSnapshot: string | undefined;
  const configuredDataset = import.meta.env.VITE_APP_MODE === 'dataset';

  const view = createCaseView(root, {
    select: caseId => {
      selectedSnapshot = listing && 'contract_version' in listing
        ? listing.snapshot_ref : undefined;
      void loadDetail(caseId);
    },
    back: () => {
      const previous = state.kind === 'detail' ? state.detail.case_id
        : 'caseId' in state ? state.caseId : undefined;
      invalidate();
      state = { kind: 'list' };
      view.render(state, listing, previous);
    },
    retry: () => {
      if ('caseId' in state) void loadDetail(state.caseId);
      else void loadList();
    },
    refreshList: () => { void loadList(); },
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
    view.render(state, listing, focus ? 'panel' : undefined);
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
      const result = await client.getCases({ signal: controller.signal,
        dataset: configuredDataset });
      if (!current(token)) return;
      listing = 'contract_version' in result ? result : {
        items: [...result.items].sort((left, right) =>
          left.case_id < right.case_id ? -1 : left.case_id > right.case_id ? 1 : 0),
      };
      selectedSnapshot = undefined;
      state = { kind: 'list' };
      view.render(state, listing);
    } catch (error) {
      if (!current(token)) return;
      state = { kind: 'list-error', error: publicError(error) };
      view.render(state, listing);
    } finally {
      if (current(token)) pending = undefined;
    }
  }

  async function loadDetail(caseId: string): Promise<void> {
    const { token, controller } = begin({ kind: 'detail-loading', caseId }, true);
    try {
      const detail = await client.getCase(caseId, { signal: controller.signal,
        snapshot: selectedSnapshot });
      if (!current(token)) return;
      if (selectedSnapshot !== undefined && (!('contract_version' in detail)
          || detail.snapshot_ref !== selectedSnapshot)) {
        throw new ApiError('invalid_response');
      }
      state = { kind: 'detail', detail };
      view.render(state, listing);
    } catch (error) {
      if (!current(token)) return;
      const failure = publicError(error);
      state = failure.code === 'case_not_found' ? { kind: 'not-found', caseId }
        : failure.code === 'stale_snapshot' ? { kind: 'stale', caseId, error: failure }
          : { kind: 'detail-error', caseId, error: failure };
      view.render(state, listing);
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
