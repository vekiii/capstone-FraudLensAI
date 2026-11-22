import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { getPublishedModelCase, getPublishedModelCases } from '../api';
import { decodeCanonicalTransactionId, decodeModelCaseBinding } from '../scoring/contracts';
import { CasesPage } from './Cases';

const client = { getCases: getPublishedModelCases, getCase: getPublishedModelCase };

export function ModelCasesPage() {
  const [params] = useSearchParams();
  const transaction = params.get('transaction');
  const [selected, setSelected] = useState<string>();
  const [error, setError] = useState<string>();
  useEffect(() => {
    if (!transaction) { setSelected(undefined); setError(undefined); return; }
    const controller = new AbortController();
    setSelected(undefined); setError(undefined);
    let canonical: string;
    try { canonical = decodeCanonicalTransactionId(transaction); }
    catch { setError('Neispravan kanonski ID.'); return; }
    void fetch('/api/model/cases/by-transaction/' + encodeURIComponent(canonical), { signal: controller.signal })
      .then(async response => {
        if (response.headers.get('content-type')?.split(';')[0].trim() !== 'application/json') throw new Error();
        const body: unknown = await response.json();
        if (!response.ok) {
          if (response.status === 404) throw new Error('Upozorenje nije objavljeno kao slučaj.');
          if (response.status === 409) throw new Error('Aktivni modelski run je promijenjen.');
          throw new Error('Objavljeni modelski slučaj nije dostupan.');
        }
        const binding = decodeModelCaseBinding(body);
        if (binding.canonical_transaction_id !== canonical) throw new Error();
        if (!controller.signal.aborted) setSelected(binding.case_id);
      }).catch((reason: unknown) => {
        if (controller.signal.aborted) return;
        const message = reason instanceof Error ? reason.message : '';
        setError(['Upozorenje nije objavljeno kao slučaj.',
          'Aktivni modelski run je promijenjen.',
          'Objavljeni modelski slučaj nije dostupan.'].includes(message)
          ? message : 'Objavljeni modelski slučaj nije dostupan.');
      });
    return () => controller.abort();
  }, [transaction]);
  return <>
    {transaction && !selected && !error && <p role="status">Provjera objavljenog slučaja…</p>}
    {error && <p role="alert">{error}</p>}
    {(!transaction || selected) && <CasesPage client={client} dataset initialCase={selected} />}
  </>;
}
