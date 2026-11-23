import { Eyebrow } from "../components/Atoms";

const responsibilities = [
  ["Risk scoring", "LightGBM prioritizes review; it does not supply procedure evidence."],
  ["Retrieval", "A reviewed corpus supplies relevant, traceable passages."],
  ["Report draft", "An AI workflow assembles case evidence and citations into structured fields."],
  ["Human decision", "An analyst reviews the draft and retains final authority."],
];

const sources = [
  ["03", "Simulated procedure guides", "Original educational guides for review and escalation, narrative citation, and missing or conflicting facts."],
  ["01", "IBM synthetic-data guide", "An authored interpretation of synthetic dataset fields and their limits; not real-customer evidence."],
  ["02", "Historical US FinCEN sources", "Supporting documentation and confidentiality guidance, scoped to historical US material."],
];

const reportFields = ["Investigation outcome", "Executive summary", "Observed facts", "Risk indicators", "Alternative explanations", "Missing information", "Recommended checks", "Limitations", "Source citations"];

function Heading({ id, number, title, intro }: { id: string; number: string; title: string; intro?: string }) {
  return <div className="rag-heading"><Eyebrow>{number} / RAG EVIDENCE</Eyebrow><h2 id={id}>{title}</h2>{intro && <p>{intro}</p>}</div>;
}

export function RagPage() {
  return <div className="rag-page">
    <header className="rag-hero">
      <Eyebrow>FRAUDLENS / INVESTIGATION ARCHITECTURE</Eyebrow>
      <h1>Retrieval-Augmented <em>Investigations</em></h1>
      <div className="rag-hero-bottom"><p>Reviewed procedure passages meet selected case facts and permitted history in a structured AI report draft. Evidence is validated before a human analyst reviews it.</p><a href="#rag-pipeline">Explore the pipeline <span aria-hidden="true">↘</span></a></div>
      <div className="rag-boundary" aria-label="Four distinct responsibilities">{responsibilities.map(([label, detail], i) => <div key={label}><span>0{i + 1} / {label}</span><p>{detail}</p></div>)}</div>
    </header>

    <section className="rag-section" id="rag-pipeline" aria-labelledby="rag-pipeline-title">
      <Heading id="rag-pipeline-title" number="01" title="Two evidence paths. One review." intro="Case evidence and procedure search are separate, server-controlled branches. Neither the model nor a retrieval result decides whether a transaction is fraudulent." />
      <div className="rag-flow" role="group" aria-label="Investigation evidence flow">
        <div className="rag-flow-start"><span className="rag-flow-index">START</span><strong>Selected case + question</strong><small>Server binds the case, source snapshot, permissions and evidence IDs.</small></div>
        <div className="rag-flow-branches">
          <div className="rag-flow-card"><span className="rag-flow-index">01 / CASE EVIDENCE</span><strong>Facts + permitted history</strong><code>get_case_facts</code><code>get_account_history</code><p>Account side is selected, but identity is resolved by the server. History is strictly pre-cutoff: seven days, at most 50 events.</p></div>
          <div className="rag-flow-card rag-flow-procedure"><span className="rag-flow-index">02 / PROCEDURE EVIDENCE</span><strong>Reviewed passages</strong><code>search_procedures</code><p>A 1–500 character query returns up to five exact passages, or explicit <code>no_match</code>.</p></div>
        </div>
        <div className="rag-flow-join"><span className="rag-flow-index">03 / JOIN</span><strong>Evidence assembly</strong><small>Saved facts, history, passage IDs and provenance remain traceable.</small></div>
        <div className="rag-flow-tail"><div><span className="rag-flow-index">04</span><strong>Structured AI report draft</strong></div><div><span className="rag-flow-index">05</span><strong>Validation</strong></div><div><span className="rag-flow-index">06 / FINAL AUTHORITY</span><strong>Analyst review</strong></div></div>
      </div>
    </section>

    <section className="rag-section rag-tinted" aria-labelledby="rag-corpus-title">
      <Heading id="rag-corpus-title" number="02" title="Six documents. Six selected passages." intro="A compact English educational corpus. Each document has recorded provenance, review metadata, included sections and a SHA-256 content hash." />
      <div className="rag-corpus-grid">{sources.map(([number, title, detail]) => <article key={title}><span className="rag-big-number">{number}</span><h3>{title}</h3><p>{detail}</p></article>)}</div>
      <div className="rag-method-line"><span>PREPARE</span><p>Named-section extraction → hash validation → 2,400-character chunks → versioned passage identities → immutable SQLite corpus archive.</p></div>
      <p className="rag-note">The historical archive publication is recorded, but the generated SQLite archive was absent from this checkout on 23 Nov 2026. The live knowledge API is therefore not claimed available here. Historical US guidance is not Serbian law or current legal advice.</p>
    </section>

    <section className="rag-section" aria-labelledby="rag-retrieval-title">
      <Heading id="rag-retrieval-title" number="03" title="Two ways to find a passage." intro="Both methods work from the approved corpus. The optional provider path is a bounded passage selector, not an embedding or vector search." />
      <div className="rag-methods">
        <article><span className="rag-method-tag">A / LOCAL & DETERMINISTIC</span><h3>BM25 retrieval</h3><code className="rag-endpoint">GET /api/knowledge/search</code><p>Normalized tokens are ranked with BM25. The implementation uses <strong>k1 = 1.2</strong> and <strong>b = 0.75</strong>, an adequacy cutoff and deterministic passage-ID tie breaking.</p><div className="rag-method-foot">≤ 5 exact passages · explicit <code>no_match</code> · no embedding model or vector database · no provider-call cost</div></article>
        <article><span className="rag-method-tag">B / OPTIONAL · OFF BY DEFAULT</span><h3>OpenAI semantic selection</h3><code className="rag-endpoint">POST /api/knowledge/semantic-search</code><p>A bounded OpenAI Responses request selects from the approved passage pool. Output must identify known passages with valid quotes, or say evidence is insufficient. Later v8 ranks a closed source set and copies authoritative source text.</p><div className="rag-method-foot">Explicit enablement · reserved and recorded provider spending · provider failures remain failures</div></article>
      </div>
    </section>

    <section className="rag-section rag-tinted" aria-labelledby="rag-report-title">
      <Heading id="rag-report-title" number="04" title="From evidence to a draft." intro="The workflow saves evidence and citations, asks for structured fields, and checks the result before it reaches an analyst." />
      <div className="rag-report"><div><span className="rag-method-tag">INPUT / SERVER BOUND</span><ul><li>Selected case facts</li><li>Permitted historical context</li><li>Retrieved procedure passages</li><li>Saved evidence and citations</li></ul></div><div><span className="rag-method-tag">OUTPUT / STRUCTURED DRAFT</span><ul>{reportFields.map(field => <li key={field}>{field}</li>)}</ul></div></div>
      <div className="rag-validation"><strong>Validate → analyst review</strong><p>Source references and archived passages are checked. A syntactically valid citation ID does not prove a generated statement interprets its source correctly.</p></div>
    </section>

    <section className="rag-section" aria-labelledby="rag-retrieval-eval-title">
      <Heading id="rag-retrieval-eval-title" number="05" title="Retrieval, measured." intro="These are recorded experiments on different question sets and methods, not a controlled head-to-head benchmark or a live service claim." />
      <div className="rag-eval-grid"><article><span className="rag-method-tag">ORIGINAL / MULTILINGUAL BM25</span><div className="rag-eval-numbers"><div><strong>0.50</strong><span>Recall@5</span></div><div><strong>0.50</strong><span>MRR@5</span></div><div><strong>4/4</strong><span>No-answer</span></div></div><p>Below the stated retrieval targets on the original held-out evaluation.</p></article><article><span className="rag-method-tag">LATER / ENGLISH-ONLY SEMANTIC V6</span><div className="rag-eval-numbers"><div><strong>0.864583</strong><span>Recall@5</span></div><div><strong>0.9375</strong><span>MRR@5</span></div><div><strong>4/4</strong><span>No-answer</span></div></div><p>20-question integrated evaluation. One provider failure counted as zero. The numeric gate was met under an automated same-model reference method.</p></article></div>
      <p className="rag-note">The corpus has only six documents; the later question set is English-only. Automated reference judgments and limited coverage constrain generalization.</p>
    </section>

    <section className="rag-section rag-quality" aria-labelledby="rag-quality-title">
      <Heading id="rag-quality-title" number="06" title="A retrieved passage is not a validated report." intro="Retrieval results and report quality are separate outcomes." />
      <div className="rag-quality-grid"><article><strong>0/8</strong><span>Original reports passed</span><p>Six of eight produced no report.</p></article><article><strong>3/4</strong><span>Later v8 development reports locally valid</span><p>The development gate failed; no held-out promotion followed.</p></article><article><strong>2/3</strong><span>Final-live judge calibration</span><p>Favorable raw ratings were not accepted as quality scores.</p></article></div>
      <p className="rag-quality-conclusion">Retrieval improvements do not establish accepted end-to-end investigation-report quality.</p>
    </section>

    <section className="rag-section rag-last" aria-labelledby="rag-limits-title"><Heading id="rag-limits-title" number="07" title="The operating boundary." /><div className="rag-limits"><p>Six reviewed sources limit retrieval coverage. The underlying AML data is synthetic. Historical US material is not Serbian law or current legal advice.</p><p>Semantic selection requires an explicitly configured provider. Citation validation cannot guarantee interpretation, and report-quality acceptance remains unproven. The analyst makes the final decision.</p></div></section>
  </div>;
}
