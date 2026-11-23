import { useCallback, useEffect, useState } from 'react';
import { decodeLocalContribution, type LocalContributionResponse } from '../scoring/localContributions';
import type { CaseDetailResponse } from '../contracts';

type DatasetCase = Extract<CaseDetailResponse, { contract_version: 2 }>;
type View = { state: 'loading' | 'error'; message?: string } | { state: 'ready'; data: LocalContributionResponse };

export function LocalContributions({ detail }: { detail: DatasetCase }) {
  const [view, setView] = useState<View>({ state: 'loading' });
  const [retry, setRetry] = useState(0);
  const load = useCallback(() => setRetry(value => value + 1), []);
  useEffect(() => {
    const controller = new AbortController();
    setView({ state: 'loading' });
    void fetch('/api/model/cases/' + encodeURIComponent(detail.case_id) + '/local-contributions',
      { signal: controller.signal })
      .then(async response => {
        if (!response.ok || response.headers.get('content-type')?.split(';')[0].trim() !== 'application/json') {
          throw new Error('Lokalni dodatak trenutno nije dostupan.');
        }
        const data = decodeLocalContribution(await response.json());
        if (data.status === 'available' && (data.case_id !== detail.case_id ||
            data.transaction_id !== detail.transaction.transaction_id ||
            data.assessment_run_id !== detail.snapshot_ref ||
            data.feature_snapshot_digest !== detail.risk_assessment.explanation.feature_snapshot_digest ||
            Math.abs(data.score - detail.risk_assessment.score) > 1e-12)) {
          throw new Error('Veza lokalnog objašnjenja nije ispravna.');
        }
        if (!controller.signal.aborted) setView({ state: 'ready', data });
      }).catch((error: unknown) => {
        if (!controller.signal.aborted) setView({ state: 'error',
          message: error instanceof Error ? error.message : 'Lokalni dodatak trenutno nije dostupan.' });
      });
    return () => controller.abort();
  }, [detail, retry]);
  return <section className="detail-section" aria-label="Lokalni doprinosi modela">
    <h4>Posebni lokalni doprinosi modela</h4>
    {view.state === 'loading' && <p role="status">Provjera dodatka…</p>}
    {view.state === 'error' && <><p role="alert">{view.message}</p>
      <button type="button" onClick={load}>Pokušaj ponovo</button></>}
    {view.state === 'ready' && view.data.status === 'unavailable' &&
      <p>Posebni lokalni doprinosi nisu dostupni ({view.data.reason_code}).</p>}
    {view.state === 'ready' && view.data.status === 'invalid' &&
      <p role="alert">Posebni lokalni doprinosi nisu prošli provjeru ({view.data.reason_code}). Skor ostaje dostupan.</p>}
    {view.state === 'ready' && view.data.status === 'available' && <>
      <p>Metoda: {view.data.method}; skala: log-odds. Osnovna vrijednost: {view.data.base_value}.</p>
      <ul>{view.data.items.map(item => <li key={item.feature_key}>
        {item.feature_key}: {item.observed_value} ({item.unit}) —
        {item.direction === 'increases' ? ' povećava' : item.direction === 'decreases' ? ' smanjuje' : ' ne mijenja'}
        {' '}log-odds za {Math.abs(item.contribution)}
      </li>)}</ul>
      <p>Ostali doprinosi zajedno: {view.data.remainder} log-odds; raw score: {view.data.raw_score}.</p>
      <p className="muted">Doprinosi nisu procenti rizika, uzroci ni dokaz pranja novca. Iznos log1p nije izvorni novčani iznos.</p>
      <p className="muted">Digest dokaza: {view.data.evidence_digest}</p>
    </>}
  </section>;
}
