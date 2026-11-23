import { Eyebrow, SectionTitle, SourceBadge, SplitRule } from "../components/Atoms";
import { useShowcaseData } from "../site-data";
import { useApiAvailability } from "../useApiAvailability";

export function LivePage() {
  const apiStatus = useApiAvailability();
  const data = useShowcaseData();
  return <>
    <section className="page-hero live-hero"><div><Eyebrow>READ-ONLY DEMONSTRATION</Eyebrow><h1>Follow the evidence.</h1><p>All data is synthetic. Illustrative interface states only. No live scoring or verification is connected.</p></div><SourceBadge source="fixture" /></section>
    <section className="section-block"><SectionTitle index="01">Choose an illustrative state</SectionTitle><div className="sample-list">{(data?.samples.samples ?? []).map((sample) => <article className="sample-row" key={sample.id}><span className="sample-index">{sample.id}</span><div><h3>{sample.title}</h3><p>{sample.status}</p></div><span className="sample-amount">{sample.amount} {sample.currency}</span><b>{sample.label}</b></article>)}</div><SplitRule /><p className="disclaimer">{data?.samples.label ?? "Loading samples source…"}. These examples are not model output, predictions, decisions or measured results.</p></section>
    <section className="section-block dark-section"><Eyebrow>02 / API STATE</Eyebrow><h2>{apiStatus === "checking" ? "Checking read-only API." : "Local fallback is available."}</h2><p className="lead-copy">When the read-only API is unavailable, this page keeps its precomputed illustrative states and marks their source as fixture. It has no write path or user-entered transaction fields.</p><div className="fallback-panel"><span>API</span><strong>{apiStatus === "unavailable" ? "Unavailable · showing local illustrative data" : apiStatus === "unwired" ? "Reachable · integration pending T055" : "Checking · local data remains available"}</strong><span>DISPLAY SOURCE</span><strong>FIXTURE · ILLUSTRATIVE ONLY</strong></div></section>
  </>;
}
