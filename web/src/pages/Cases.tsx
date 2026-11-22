import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, getCase, getCases } from "../api";
import type { CaseDetail, CaseDetailResponse, CaseListResponse } from "../contracts";
interface CaseClient {
  getCases(options: { signal: AbortSignal; dataset?: boolean }): Promise<CaseListResponse>;
  getCase(caseId: string, options: { signal: AbortSignal; snapshot?: string }): Promise<CaseDetailResponse>;
}
const defaultClient: CaseClient = { getCases, getCase };

type ViewState =
  | { kind: "loading-list" }
  | { kind: "list" }
  | { kind: "list-error"; error: ApiError }
  | { kind: "loading-detail"; caseId: string }
  | { kind: "detail"; detail: CaseDetailResponse }
  | { kind: "detail-error"; caseId: string; error: ApiError }
  | { kind: "stale"; caseId: string }
  | { kind: "not-found"; caseId: string };

const sourceNames = { fixture: "fixture — sintetički primer", rules: "rules — pravila", model: "model" };

function publicError(error: unknown): ApiError {
  return error instanceof ApiError ? error : new ApiError("internal_error");
}

function FixtureDetail({ detail }: { detail: CaseDetail }) {
  return <>
    <section className="detail-section"><h3>Transakcija</h3><dl className="fields">
      <div><dt>ID transakcije</dt><dd>{detail.transaction.transaction_id}</dd></div>
      <div><dt>Vreme transakcije (UTC)</dt><dd>{detail.transaction.occurred_at}</dd></div>
      <div><dt>Pošiljalac — demo račun</dt><dd>{detail.transaction.sender_account}</dd></div>
      <div><dt>Primalac — demo račun</dt><dd>{detail.transaction.receiver_account}</dd></div>
      <div><dt>Iznos</dt><dd>{detail.transaction.amount} {detail.transaction.currency}</dd></div>
    </dl></section>
    <section className="detail-section"><h3>Ilustrativna procena</h3>
      <p className="risk-score">{detail.risk_assessment.score} / 1</p>
      <p className="muted">Demonstracioni skor nije verovatnoća prevare.</p>
      <dl className="fields">
        <div><dt>Izvor skora</dt><dd>{sourceNames[detail.risk_assessment.source]}</dd></div>
        <div><dt>Verzija</dt><dd>{detail.risk_assessment.scorer_version}</dd></div>
        <div><dt>Vreme ocenjivanja (UTC)</dt><dd>{detail.risk_assessment.scored_at}</dd></div>
      </dl><h4>Objašnjenje</h4><p className="explanation">{detail.risk_assessment.explanation}</p>
    </section>
  </>;
}

function DatasetDetail({ detail }: { detail: Extract<CaseDetailResponse, { contract_version: 2 }> }) {
  const { transaction, risk_assessment: risk } = detail;
  return <>
    <section className="detail-section"><h3>Transakcija iz sintetičkog IBM skupa</h3><dl className="fields">
      <div><dt>ID transakcije</dt><dd>{transaction.transaction_id}</dd></div>
      <div><dt>Vreme događaja (UTC)</dt><dd>{transaction.event_time_utc}</dd></div>
      <div><dt>Izvorno vreme</dt><dd>{transaction.event_time_raw}</dd></div>
      <div><dt>Osnova vremena</dt><dd>{transaction.time_basis}</dd></div>
      <div><dt>Pošiljalac</dt><dd>{transaction.sender.bank} · {transaction.sender.account}</dd></div>
      <div><dt>Primalac</dt><dd>{transaction.receiver.bank} · {transaction.receiver.account}</dd></div>
      <div><dt>Plaćeno</dt><dd>{transaction.paid.amount} {transaction.paid.currency}</dd></div>
      <div><dt>Primljeno</dt><dd>{transaction.received.amount} {transaction.received.currency}</dd></div>
      <div><dt>Format plaćanja</dt><dd>{transaction.payment_format ?? "Nije zabeleženo"}</dd></div>
    </dl></section>
    <section className="detail-section"><h3>Procena rizika</h3><p className="risk-score">{risk.score} / 1</p>
      <p className="muted">{risk.score_source === "model"
        ? "Procena modela nije kalibrisana verovatnoća niti dokaz krivice."
        : "Ordinalni skor pravila nije verovatnoća niti dokaz krivice."}</p>
      <dl className="fields">
        <div><dt>Izvor skora</dt><dd>{risk.score_source}</dd></div>
        <div><dt>Vrsta skora</dt><dd>{risk.score_kind}</dd></div>
        <div><dt>Scorer</dt><dd>{risk.scorer_version}</dd></div>
        <div><dt>Verzija karakteristika</dt><dd>{risk.feature_version}</dd></div>
        <div><dt>Dataset</dt><dd>{detail.dataset_version}</dd></div>
        <div><dt>Run</dt><dd>{risk.run_id}</dd></div>
        <div><dt>Vreme događaja (UTC)</dt><dd>{risk.event_time_utc}</dd></div>
        <div><dt>Istorija do (isključivo)</dt><dd>{risk.history_cutoff_exclusive_at}</dd></div>
        <div><dt>Stvarno vreme bodovanja (UTC)</dt><dd>{risk.scored_at}</dd></div>
        <div><dt>Pokrivenost istorije</dt><dd>{risk.history_coverage.state} · {risk.history_coverage.start ?? "nepoznat početak"}</dd></div>
      </dl><h4>Objašnjenje</h4>
      {risk.explanation.status === "unavailable"
        ? <p className="explanation">Objašnjenje nedostupno: {risk.explanation.reason_code}.</p>
        : <>
          <dl className="fields">
            <div><dt>Metoda</dt><dd>{risk.explanation.method}</dd></div>
            <div><dt>Skala</dt><dd>{risk.explanation.explained_scale}</dd></div>
            <div><dt>Snapshot digest</dt><dd>{risk.explanation.feature_snapshot_digest}</dd></div>
            <div><dt>Delimičan prikaz</dt><dd>{risk.explanation.partial ? "Da" : "Ne"}</dd></div>
            <div><dt>Osnova</dt><dd>{risk.explanation.base_value ?? "Nije dostupna"}</dd></div>
            <div><dt>Ostatak</dt><dd>{risk.explanation.remainder ?? "Nije dostupan"}</dd></div>
          </dl>
          <ul className="explanation-items">{risk.explanation.items.map((item) =>
            <li key={item.feature_key}>{item.feature_key}: {item.observed_value} {item.unit}; {item.direction} {item.contribution}{item.rule_condition ? `; ${item.rule_condition}` : ""}</li>)}</ul>
        </>}
    </section>
  </>;
}

export function CasesPage({ client = defaultClient, dataset = import.meta.env.VITE_APP_MODE === "dataset" }: {
  client?: CaseClient;
  dataset?: boolean;
}) {
  const [listing, setListing] = useState<CaseListResponse>();
  const [state, setState] = useState<ViewState>({ kind: "loading-list" });
  const generation = useRef(0);
  const pending = useRef<AbortController | undefined>(undefined);

  const loadList = useCallback(async () => {
    generation.current += 1;
    const token = generation.current;
    pending.current?.abort();
    const controller = new AbortController();
    pending.current = controller;
    setState({ kind: "loading-list" });
    try {
      const result = await client.getCases({ signal: controller.signal, dataset });
      if (generation.current !== token) return;
      const ordered = "contract_version" in result ? result : {
        items: [...result.items].sort((left, right) => left.case_id.localeCompare(right.case_id)),
      };
      setListing(ordered);
      setState({ kind: "list" });
    } catch (error) {
      if (generation.current === token) setState({ kind: "list-error", error: publicError(error) });
    } finally {
      if (generation.current === token) pending.current = undefined;
    }
  }, [client, dataset]);

  useEffect(() => {
    void loadList();
    return () => { generation.current += 1; pending.current?.abort(); };
  }, [loadList]);

  const selectCase = async (caseId: string) => {
    const snapshot = listing && "contract_version" in listing ? listing.snapshot_ref : undefined;
    generation.current += 1;
    const token = generation.current;
    pending.current?.abort();
    const controller = new AbortController();
    pending.current = controller;
    setState({ kind: "loading-detail", caseId });
    try {
      const detail = await client.getCase(caseId, snapshot === undefined
        ? { signal: controller.signal } : { signal: controller.signal, snapshot });
      if (generation.current !== token) return;
      setState({ kind: "detail", detail });
    } catch (error) {
      if (generation.current !== token) return;
      const failure = publicError(error);
      setState(failure.code === "case_not_found" ? { kind: "not-found", caseId }
        : failure.code === "stale_snapshot" ? { kind: "stale", caseId }
          : { kind: "detail-error", caseId, error: failure });
    } finally {
      if (generation.current === token) pending.current = undefined;
    }
  };

  const items = listing?.items ?? [];
  const selected = state.kind === "detail" ? state.detail.case_id
    : "caseId" in state ? state.caseId : undefined;
  const isDataset = (listing && "contract_version" in listing)
    || (state.kind === "detail" && "contract_version" in state.detail) || dataset;

  return <section className="section-block cases-page">
    <div className="page-hero"><div><span className="eyebrow">{isDataset ? "DATASET ALERTS" : "LOCAL SYNTHETIC DEMO"}</span>
      <h1>Pregled slučajeva</h1><p className="lead-copy">Lista upozorenja i podaci koji podržavaju procenu.</p></div></div>
    <aside className="synthetic-notice" aria-label="Napomena o demonstracionim podacima">
      <strong>{isDataset ? "Sintetički IBM podaci — pregled procena" : "Demonstracioni podaci — sintetički skor, bez ML predikcije"}</strong>
      <p>{isDataset ? "Vreme izvora je pretpostavljeno UTC; skor nije dokaz krivice."
        : "Podaci su izmišljeni. Rezultati služe isključivo za ilustraciju."}</p>
    </aside>
    <div className="workspace">
      <nav className="case-navigation" aria-label={isDataset ? "Upozorenja" : "Sintetički slučajevi"}>
        <h2>Slučajevi</h2><ul className="case-list">{items.map((item) =>
          <li key={item.case_id}><button className="case-choice" type="button"
            aria-pressed={item.case_id === selected} aria-label={`Otvori ${item.case_id}`}
            onClick={() => { void selectCase(item.case_id); }}>
            <strong>{item.case_id}</strong><span className="muted">{item.transaction_id}</span>
            <span className="case-score">Skor {item.score} / 1 · {item.score_source}</span>
          </button></li>)}</ul>
      </nav>
      <section className="case-panel" aria-labelledby="panel-title" aria-busy={state.kind.startsWith("loading")}>
        <h2 id="panel-title">{selected ? `Slučaj ${selected}` : "Pregled slučajeva"}</h2>
        {state.kind === "loading-list" && <p role="status">Učitavanje slučajeva…</p>}
        {state.kind === "loading-detail" && <p role="status">Učitavanje detalja…</p>}
        {state.kind === "list" && <>
          {listing && "contract_version" in listing
            ? <p role="status">Ukupno upozorenja: {listing.total_alerts}; prikazano: {listing.displayed_count}.</p>
            : <p role="status">{items.length ? `Dostupno slučajeva: ${items.length}.` : "Nema dostupnih slučajeva. Lista je prazna."}</p>}
          {listing && "contract_version" in listing && listing.truncated && <p className="muted">Prikazano je najnovijih 100 upozorenja.</p>}
          {!items.length && <><p>{isDataset ? "Nema upozorenja u aktivnom runu." : "Nema dostupnih slučajeva."}</p>
            <button className="button" type="button" onClick={() => { void loadList(); }}>Pokušaj ponovo</button></>}
        </>}
        {state.kind === "list-error" && <><p role="alert">{state.error.message}</p>
          <button className="button" type="button" onClick={() => { void loadList(); }}>Pokušaj ponovo</button></>}
        {"caseId" in state && <button className="button button-back" type="button"
          onClick={() => setState({ kind: "list" })}>← Nazad na listu</button>}
        {state.kind === "detail" && ("contract_version" in state.detail
          ? <DatasetDetail detail={state.detail} /> : <FixtureDetail detail={state.detail} />)}
        {state.kind === "stale" && <><p role="alert">Izabrani pregled više nije aktivan.</p>
          <button className="button" type="button" onClick={() => { void loadList(); }}>Osveži listu</button></>}
        {state.kind === "not-found" && <p role="alert">Slučaj nije pronađen.</p>}
        {state.kind === "detail-error" && <p role="alert">{state.error.message}</p>}
      </section>
    </div>
  </section>;
}
