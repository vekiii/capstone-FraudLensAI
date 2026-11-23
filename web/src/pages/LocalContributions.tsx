import { useCallback, useEffect, useState } from 'react';
import { decodeLocalContribution, type LocalContribution, type LocalContributionResponse } from '../scoring/localContributions';
import type { CaseDetailResponse } from '../contracts';

type DatasetCase = Extract<CaseDetailResponse, { contract_version: 2 }>;
type View = { state: 'loading' | 'error'; message?: string } | { state: 'ready'; data: LocalContributionResponse };
type Item = LocalContribution['items'][number];

const featureLabels: Record<string, string> = {
  sender_out_count_24h: 'Odlazne transakcije pošiljaoca u prethodna 24 h',
  sender_distinct_receivers_24h: 'Različiti primaoci pošiljaoca u prethodna 24 h',
  sender_paid_count_same_currency_24h: 'Plaćanja pošiljaoca u istoj valuti u prethodna 24 h',
  sender_paid_sum_same_currency_24h: 'Zbir plaćenog iznosa pošiljaoca u istoj valuti u prethodna 24 h',
  receiver_in_count_24h: 'Dolazne transakcije primaoca u prethodna 24 h',
  receiver_distinct_senders_24h: 'Različiti pošiljaoci primaoca u prethodna 24 h',
  receiver_received_count_same_currency_24h: 'Prijemi primaoca u istoj valuti u prethodna 24 h',
  receiver_received_sum_same_currency_24h: 'Zbir primljenog iznosa primaoca u istoj valuti u prethodna 24 h',
  current_amount_paid_log1p: 'Plaćeni iznos (log1p transformacija)',
  current_payment_currency: 'Valuta plaćanja',
  current_payment_format: 'Format plaćanja',
};

const rounded = (value: number) => value !== 0 && Math.abs(value) < 0.00005
  ? `${value < 0 ? '−' : ''}<0.0001` : value.toFixed(4);

function observed(item: Item, detail: DatasetCase): string {
  if (item.unit === 'category') return `${item.observed_value} (kategorija)`;
  if (item.unit === 'count') return `${item.observed_value} (broj)`;
  const numeric = Number(item.observed_value);
  const shown = Number.isFinite(numeric) ? numeric.toFixed(item.unit === 'log1p_source_amount' ? 4 : 2)
    : item.observed_value;
  if (item.unit === 'log1p_source_amount') return `${shown} (log1p iznosa; bez valute)`;
  if (item.unit !== 'same_currency_amount') return `${item.observed_value} (${item.unit})`;
  const currency = item.feature_key.startsWith('receiver_')
    ? detail.transaction.received.currency : detail.transaction.paid.currency;
  return `${shown} ${currency}`;
}

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
      <p>Metoda: {view.data.method}; skala doprinosa: log-odds. Osnovna vrijednost: {rounded(view.data.base_value)} log-odds.</p>
      <ul>{view.data.items.map(item => <li key={item.feature_key}>
        {featureLabels[item.feature_key] ?? item.feature_key}: {observed(item, detail)} —
        {item.direction === 'increases' ? ' povećava' : item.direction === 'decreases' ? ' smanjuje' : ' ne mijenja'}
        {' '}log-odds za {rounded(Math.abs(item.contribution))}
      </li>)}</ul>
      <p>Ostali doprinosi zajedno: {rounded(view.data.remainder)} log-odds; sirovi izlaz modela: {rounded(view.data.raw_score)} log-odds.</p>
      <p className="muted">Doprinosi nisu procenti rizika, uzroci ni dokaz pranja novca. Prikazani log1p iznos nije izvorni novčani iznos; izvorni iznos i valuta su u podacima transakcije.</p>
      <details className="contribution-details">
        <summary>Pune vrijednosti i identiteti</summary>
        <dl>
          <dt>Metoda i skala</dt><dd>{view.data.method}; log-odds</dd>
          <dt>Osnovna vrijednost</dt><dd>{view.data.base_value}</dd>
          {view.data.items.map(item => <div key={item.feature_key}>
            <dt>{item.feature_key}</dt>
            <dd>Izvorna modelska vrijednost: {item.observed_value} ({item.unit}); doprinos: {item.contribution} log-odds.</dd>
          </div>)}
          <dt>Ostali doprinosi</dt><dd>{view.data.remainder} log-odds</dd>
          <dt>Sirovi izlaz</dt><dd>{view.data.raw_score} log-odds</dd>
          <dt>Objavljeni score</dt><dd>{view.data.score}</dd>
          <dt>Case / transakcija / run</dt><dd>{view.data.case_id} / {view.data.transaction_id} / {view.data.assessment_run_id}</dd>
          <dt>Digest dokaza</dt><dd>{view.data.evidence_digest}</dd>
        </dl>
      </details>
    </>}
  </section>;
}
