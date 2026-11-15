import { ApiError, getCase, getCases, getOverview } from './api';
import type { CaseDetailResponse, CaseListResponse } from './contracts';
import type { Overview } from './contracts';
import { createOverviewView } from './overview-view';
import type { OverviewState } from './overview-view';
import { createCaseView } from './views';
import type { UiState } from './views';
import './styles.css';

export interface CaseClient {
  getCases(options: { signal: AbortSignal; dataset?: boolean }): Promise<CaseListResponse>;
  getCase(caseId: string, options: { signal: AbortSignal; snapshot?: string }):
    Promise<CaseDetailResponse>;
}

export interface OverviewClient {
  getOverview(options: { signal: AbortSignal }): Promise<Overview>;
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

export function mountFraudLensApp(
  root: HTMLElement,
  overviewClient: OverviewClient = { getOverview },
  caseClient?: CaseClient,
): () => void {
  let activePage: 'overview' | 'cases' = 'overview';
  let overviewState: OverviewState = { kind: 'loading' };
  let controller: AbortController | undefined;
  let caseDispose: (() => void) | undefined;
  let generation = 0;
  let disposed = false;

  const header = document.createElement('header');
  header.className = 'app-header';
  const brand = document.createElement('p');
  brand.className = 'eyebrow'; brand.textContent = 'FRAUDLENS AI';
  const nav = document.createElement('nav');
  nav.className = 'primary-navigation'; nav.setAttribute('aria-label', 'Primary navigation');
  const overviewTab = document.createElement('button');
  overviewTab.type = 'button'; overviewTab.textContent = 'Overview'; overviewTab.dataset.page = 'overview';
  const casesTab = document.createElement('button');
  casesTab.type = 'button'; casesTab.textContent = 'Cases'; casesTab.dataset.page = 'cases';
  nav.append(overviewTab, casesTab);
  header.append(brand, nav);
  const pageRoot = document.createElement('div'); pageRoot.className = 'page-content';
  root.replaceChildren(header, pageRoot);

  const view = createOverviewView(pageRoot, () => { void loadOverview(); });
  function cancelActive(): void {
    generation += 1;
    controller?.abort(); controller = undefined;
    caseDispose?.(); caseDispose = undefined;
  }
  function current(token: number): boolean { return !disposed && token === generation; }
  function selectTab(): void {
    overviewTab.setAttribute('aria-current', String(activePage === 'overview' ? 'page' : 'false'));
    casesTab.setAttribute('aria-current', String(activePage === 'cases' ? 'page' : 'false'));
  }
  async function loadOverview(): Promise<void> {
    cancelActive();
    activePage = 'overview'; selectTab();
    const token = generation;
    const requestController = new AbortController(); controller = requestController;
    overviewState = { kind: 'loading' }; view.render(overviewState);
    try {
      const overview = await overviewClient.getOverview({ signal: requestController.signal });
      if (!current(token)) return;
      overviewState = { kind: 'loaded', overview }; view.render(overviewState);
    } catch (error) {
      if (!current(token)) return;
      const failure = error instanceof ApiError ? error : new ApiError('internal_error');
      overviewState = { kind: 'error', message: failure.code === 'run_unavailable'
        ? 'No active dataset or model run is configured.' : failure.message };
      view.render(overviewState);
    } finally {
      if (current(token)) controller = undefined;
    }
  }
  function loadCases(): void {
    cancelActive();
    activePage = 'cases'; selectTab();
    caseDispose = mountCaseApp(pageRoot, caseClient);
  }
  overviewTab.addEventListener('click', () => { void loadOverview(); });
  casesTab.addEventListener('click', loadCases);
  selectTab();
  void loadOverview();
  return () => {
    disposed = true; cancelActive(); root.replaceChildren();
  };
}

const root = document.querySelector<HTMLElement>('#app');
if (root) {
  const dispose = mountFraudLensApp(root);
  import.meta.hot?.dispose(dispose);
}
