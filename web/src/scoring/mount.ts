import { ApiError, getEdaSummary, getModelResults, getTransactionRisk } from './api';
import { ContractValidationError } from '../contracts';
import { decodeCanonicalTransactionId } from './contracts';
import { createEdaView, createModelResultsView, createRiskView } from './views';

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
