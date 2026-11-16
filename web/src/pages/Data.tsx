import { SectionTitle, Eyebrow, SplitRule, NotMeasured } from "../components/Atoms";
import { useShowcaseData } from "../site-data";

const datasetFacts = [
  ["Source", "Synthetic IBM-derived transaction data"],
  ["Use", "Educational investigation and triage prototype"],
  ["Calibration", "Synthetic data; no real-world calibration claim"],
  ["Labels", "Evaluation-only; excluded from feature and retrieval inputs"],
];

export function DataPage() {
  const data = useShowcaseData();
  return <>
    <section className="page-hero"><Eyebrow>DATA / MODEL / EVALUATION</Eyebrow><h1>What the history can tell us.</h1><p>The dataset, the point-in-time rules and the limits of the current evidence.</p></section>
    <section className="section-block"><SectionTitle index="01">Dataset notes</SectionTitle><div className="facts-table">{datasetFacts.map(([k, v]) => <div className="fact-row" key={k}><span>{k}</span><p>{v}</p></div>)}</div><p className="caption">Dataset size, date range, licences and measured class balance will appear when generated evidence is available.</p></section>
    <section className="section-block dark-section"><Eyebrow>02 / EXPLORATORY ANALYSIS</Eyebrow><h2>Describe before you decide.</h2><div className="metric-grid compact">{["Class balance", "Amount distribution", "Hourly pattern", "Currency mix"].map((label) => <div className="metric" key={label}><span>{label}</span><strong><NotMeasured>{data?.eda.label ?? "Loading EDA source…"}</NotMeasured></strong><small>Source: {data?.eda.source_version ?? "—"}</small></div>)}</div><p className="disclaimer">Accuracy alone is not an appropriate summary for rare events.</p></section>
    <section className="section-block feature-history"><SectionTitle index="03">History-v1 features</SectionTitle><p className="lead-copy">Each snapshot uses only prior events in the half-open window [event time − 24 hours, event time). Equal-time peers do not enter the snapshot.</p><div className="feature-table"><div className="feature-header"><span>FIELD</span><span>DEFINITION</span></div>{(data?.features.features ?? []).map((feature, index) => <div className="feature-row" key={feature.name}><span>{String(index + 1).padStart(2, "0")} · {feature.name}</span><p>{feature.definition}</p></div>)}</div></section>
    <section className="section-block dark-section"><SectionTitle index="04">Evaluation status</SectionTitle><div className="evaluation-grid"><div><Eyebrow>PINNED MODEL</Eyebrow><p>Scikit-learn artifact; identity and digest must be verified before serving.</p></div><div><Eyebrow>MEASURED METRICS</Eyebrow><p><NotMeasured>{data?.metrics.label ?? "Loading metrics source…"}</NotMeasured></p></div><div><Eyebrow>GLOBAL EXPLANATION</Eyebrow><p><NotMeasured>{data?.explanationsGlobal.label ?? "Loading explanation source…"}</NotMeasured></p></div></div><SplitRule /><p className="disclaimer">The displayed status does not claim model performance. No evaluation result has been generated for this showcase.</p></section>
  </>;
}
