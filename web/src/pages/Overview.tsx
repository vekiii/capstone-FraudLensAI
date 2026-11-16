import { TransitionLink } from "../components/TransitionLink";
import { Reveal } from "../motion/Reveal";
import { Eyebrow, NotMeasured, SectionTitle, SplitRule } from "../components/Atoms";
import { useShowcaseData } from "../site-data";

const pipeline = ["PostgreSQL", "Change capture", "Durable log", "Python worker", "History features", "Pinned model", "Read-only API", "Human review"];

export function Overview() {
  const data = useShowcaseData();
  return <>
    <section className="hero">
      <div className="hero-meta"><Eyebrow>AML INVESTIGATION · LOCAL SYNTHETIC DEMO</Eyebrow><span>FEATURE 005 / IN PROGRESS</span></div>
      <Reveal className="hero-copy" preset="fadeUp"><h1>Catch fraud at the edge of the transaction.</h1><p>A model flags it. Evidence explains it.</p></Reveal>
      <a className="explore-link" href="#approach">EXPLORE <span aria-hidden="true">↓</span></a>
    </section>
    <div className="hero-spacer" aria-hidden="true" />
    <section className="story-scroll" aria-label="Fraud screening context">
      <div className="story-beat"><h2>Every second, millions swipe.</h2></div>
      <div className="story-beat"><h2>A few are not who they seem.</h2></div>
    </section>
    <section id="approach" className="section-block intro-section">
      <SectionTitle index="01">A score is only the beginning.</SectionTitle>
      <div className="intro-copy"><p>Fraud is rare, costly and adversarial. A score alone does not show how a case was assembled. This project pairs a point-in-time history with a pinned model artifact and makes provenance visible for a person to review.</p><p>All displayed examples are synthetic. The prototype does not make legal findings or intervene on an account.</p></div>
      <div className="principle-grid"><article><Eyebrow>01 / HISTORY</Eyebrow><h3>Look back, never ahead.</h3><p>Eleven features summarize prior activity in the 24 hours before an event. The event and equal-time peers stay out of their own history.</p></article><article><Eyebrow>02 / SCORE</Eyebrow><h3>Keep the artifact pinned.</h3><p>The serving boundary checks model identity and preserves an explanation with the saved assessment.</p></article><article><Eyebrow>03 / AUTHORITY</Eyebrow><h3>Keep decisions human.</h3><p>A policy selects alerts separately from the score. An analyst retains the final disposition.</p></article></div>
    </section>
    <section className="section-block dark-section">
      <div className="section-top"><Eyebrow>02 / CURRENT EVIDENCE</Eyebrow><span>PROVENANCE FIRST</span></div><SplitRule />
      <div className="metric-grid">
        {["PR-AUC", "Recall at review capacity", "RAG overturn rate"].map((metric) => <div className="metric" key={metric}><span>{metric}</span><strong><NotMeasured>{data?.metrics.label ?? "Loading metrics source…"}</NotMeasured></strong><small>Source: {data?.metrics.source_version ?? "—"}</small></div>)}
      </div>
      <SplitRule /><p className="disclaimer">{data?.metrics.integration_fixture_label ?? "Evidence file pending"}. No real-world performance claim is made.</p>
    </section>
    <section className="section-block pipeline-section">
      <SectionTitle index="03">A traceable path to review.</SectionTitle>
      <div className="pipeline-grid">{pipeline.map((item, i) => <div className="pipeline-row" key={item}><span>{String(i + 1).padStart(2, "0")}.</span><p>{item}</p><span aria-hidden="true">↗</span></div>)}</div>
    </section>
    <section className="section-block explore-section">
      <Eyebrow>04 / EXPLORE THE WORK</Eyebrow>
      {[["/data", "Data & model", "Read the feature contract and evaluation status."], ["/rag", "RAG", "See the verification design and its limits."], ["/live", "Live demo", "Inspect illustrative states with source labels."]].map(([to, title, desc], i) => <TransitionLink className="explore-row" to={to} key={to}><span>{String(i + 1).padStart(2, "0")}.</span><strong>{title}</strong><small>{desc}</small><b>OPEN ↗</b></TransitionLink>)}
    </section>
  </>;
}
