import { Eyebrow, SectionTitle, SplitRule, NotMeasured } from "../components/Atoms";
import { useShowcaseData } from "../site-data";

const steps = ["Build a label-free query from snapshot, score, coverage and explanation.", "Retrieve relevant passages from a reviewed corpus.", "Ask for a structured advisory assessment with citations.", "Check citations against retrieved passages; downgrade weak evidence to uncertain."];

export function RagPage() {
  const data = useShowcaseData();
  return <>
    <section className="page-hero"><Eyebrow>RETRIEVAL / EVIDENCE / LIMITS</Eyebrow><h1>Ground a review in sources.</h1><p>Retrieval-augmented generation is a proposed advisory verification layer. It does not decide a case.</p></section>
    <section className="section-block"><SectionTitle index="01">The proposed call</SectionTitle><div className="numbered-list">{steps.map((step, index) => <div className="numbered-row" key={step}><span>{String(index + 1).padStart(2, "0")}.</span><p>{step}</p></div>)}</div><p className="caption">No external model call or retrieval is active in this preview.</p></section>
    <section className="section-block dark-section"><Eyebrow>02 / KNOWLEDGE BASE</Eyebrow><h2>Reviewed material only.</h2><p className="lead-copy">A future corpus may include licensed typologies, review guidance and synthetic case notes. Each item needs a source, licence and reviewer.</p><div className="metric-grid compact"><div className="metric"><span>Corpus status</span><strong><NotMeasured>{data?.kbStats.label ?? "Loading corpus source…"}</NotMeasured></strong><small>{data?.kbStats.note}</small></div><div className="metric"><span>Evaluation</span><strong><NotMeasured>{data?.ragEval.label ?? "Loading evaluation source…"}</NotMeasured></strong><small>{data?.ragEval.note}</small></div></div></section>
    <section className="section-block"><SectionTitle index="03">Review stays with a person.</SectionTitle><div className="decision-grid"><div><Eyebrow>SUPPORTS</Eyebrow><p>May raise review priority; never close or block an account.</p></div><div><Eyebrow>REJECTS</Eyebrow><p>May disagree with an alert; the alert stays in the queue.</p></div><div><Eyebrow>UNCERTAIN / UNAVAILABLE</Eyebrow><p>Show the limitation. Do not turn missing evidence into confidence.</p></div></div><SplitRule /><p className="caption">Corpus, vector store, embedding model and provider decisions remain under review.</p></section>
  </>;
}
