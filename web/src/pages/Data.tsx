import { Link } from 'react-router-dom';
import { modelEvidence as evidence, modelFeatures } from '../model-evidence';

const integer = (value: number) => new Intl.NumberFormat('en-US').format(value);
const percent = (value: number, digits = 2) => `${(value * 100).toFixed(digits)}%`;
const decimal = (value: number, digits = 4) => value.toFixed(digits);

function MetricTable() {
  const metrics = [
    ['Precision', 'precision', 4], ['Recall', 'recall', 4], ['F1', 'f1', 4],
    ['Average precision (PR-AUC)', 'ap', 4], ['ROC AUC', 'rocAuc', 4],
    ['Brier score', 'brier', 6],
  ] as const;
  return <div className="evidence-table-scroll"><table className="evidence-table">
    <caption>Frozen unweighted LightGBM; threshold {evidence.threshold}</caption>
    <thead><tr><th scope="col">Metric</th>{evidence.results.map(result => <th scope="col" key={result.name}>{result.name}</th>)}</tr></thead>
    <tbody>{metrics.map(([label, key, digits]) => <tr key={key}><th scope="row">{label}</th>{evidence.results.map(result =>
      <td key={result.name}>{decimal(result[key], digits)}</td>)}</tr>)}
      <tr><th scope="row">Alerts at threshold</th>{evidence.results.map(result => <td key={result.name}>{integer(result.alerts)} / {integer(result.rows)} rows</td>)}</tr>
      {[20, 50, 100].map((k, index) => <tr key={k}><th scope="row">Precision@{k}, whole partition</th>{evidence.results.map(result => <td key={result.name}>{result.topK[index][0]}/{result.topK[index][1]} ({percent(result.topK[index][0] / k, 0)})</td>)}</tr>)}
    </tbody>
  </table></div>;
}

function MetricComparison() {
  return <div className="model-metric-comparison" role="group" aria-label="Validation and test metric comparison">
    {(['precision', 'recall', 'f1', 'ap'] as const).map(key => <div className="model-metric-row" key={key}>
      <strong>{key === 'ap' ? 'Average precision' : key === 'f1' ? 'F1' : key[0].toUpperCase() + key.slice(1)}</strong>
      {evidence.results.map(result => <div className="model-metric-track" key={result.name}>
        <span>{result.name}</span><div><i style={{ width: `${result[key] * 100}%` }} /></div><b>{percent(result[key])}</b>
      </div>)}
    </div>)}
    <p>Each bar uses a 0–100% scale. Exact values and denominators appear in the table below.</p>
  </div>;
}

export function DataPage() {
  return <div className="model-evidence-page" lang="en">
    <header className="model-page-hero"><p className="eyebrow">DATA / METHOD / FROZEN MODEL</p>
      <h1>Data &amp; model</h1><p>How the synthetic AML dataset was prepared, how the local model was selected, and what the authorized evaluation measured.</p>
      <Link className="evidence-link" to="/eda">Explore dataset aggregates →</Link>
    </header>

    <section className="model-section" aria-labelledby="research-title"><span className="eyebrow">01 / SOURCE</span><h2 id="research-title">A specific synthetic source</h2>
      <p>IBM Transactions for Anti-Money Laundering, HI-Small transaction CSV. The target is IBM’s simulated “Is Laundering” label. It is neither a verified crime nor a payment fraud finding. This local copy was selected for a reproducible educational AML triage study.</p>
      <div className="evidence-callout"><strong>Source identity</strong><code>{evidence.sourceSha}</code><span>SHA-256 of the exact local CSV. Upstream Kaggle revision, acquisition date, and publisher timezone are unknown.</span></div>
      <p>Source timestamps have minute precision and no offset; the project interprets them as UTC. The completed source contains 5,078,345 accepted rows and zero rejected rows. <Link to="/eda">Dataset overview</Link> shows its configured, label-free aggregate summary.</p>
    </section>

    <section className="model-section" aria-labelledby="pipeline-title"><span className="eyebrow">02 / PREPARATION</span><h2 id="pipeline-title">From transaction to model input</h2>
      <ol className="model-pipeline"><li>Verify source bytes and positional CSV schema</li><li>Validate and canonicalize transactions</li><li>Build strict-prior 24-hour features</li><li>Freeze complete UTC-day research splits</li><li>Fit and select on train/validation</li><li>Evaluate frozen test predictions once</li></ol>
      <p>Raw timestamps, sender/receiver banks and accounts, paid/received amounts and currencies, and payment format are parsed with explicit roles. Duplicate source “Account” headers are mapped by position. The target label stays outside prediction features.</p>
      <p>Eight history features use only events in <code>[t − 24h, t)</code>. Transactions sharing an instant never contribute to one another. Three current-event fields complete the eleven-field feature contract. Missing required values are rejected; no imputation is performed.</p>
      <details className="model-disclosure"><summary>Show all 11 source feature fields</summary><div className="evidence-table-scroll"><table className="evidence-table"><thead><tr><th scope="col">Feature</th><th scope="col">Meaning</th></tr></thead><tbody>{modelFeatures.map(([name, meaning]) => <tr key={name}><th scope="row"><code>{name}</code></th><td>{meaning}</td></tr>)}</tbody></table></div></details>
      <p>Two categorical fields use train-only vocabularies with an unknown bucket. Nine numeric fields and one-hot categories form the final 32-column model matrix. Numeric tree inputs are not standardized.</p>
    </section>

    <section className="model-section" aria-labelledby="split-title"><span className="eyebrow">03 / FROZEN PARTITIONS</span><h2 id="split-title">Train, validate, then test</h2>
      <p>The research split covers {integer(evidence.scoreableDevelopment)} scoreable development rows. Complete UTC-day boundaries preserve temporal order. The first 24 hours are history-only; later showcase rows are outside model selection and this evaluation. Five development dates make the intended 60/20/20 split approximate.</p>
      <div className="split-bar" role="img" aria-label="Train 62.03 percent; validation 25.61 percent; test 12.36 percent">{evidence.partitions.map(partition => <span key={partition.name} style={{ width: `${partition.rows / evidence.scoreableDevelopment * 100}%` }} title={`${partition.name}: ${integer(partition.rows)}`} />)}</div>
      <div className="evidence-table-scroll"><table className="evidence-table"><caption>Denominator: {integer(evidence.scoreableDevelopment)} scoreable development transactions</caption><thead><tr><th scope="col">Partition</th><th scope="col">UTC coverage</th><th scope="col">Rows</th><th scope="col">Share</th><th scope="col">Positive</th><th scope="col">Negative</th><th scope="col">Prevalence</th></tr></thead><tbody>{evidence.partitions.map(partition => <tr key={partition.name}><th scope="row">{partition.name}</th><td>{partition.period}</td><td>{integer(partition.rows)}</td><td>{percent(partition.rows / evidence.scoreableDevelopment)}</td><td>{integer(partition.positive)}</td><td>{integer(partition.negative)}</td><td>{percent(partition.positive / partition.rows, 4)}</td></tr>)}</tbody></table></div>
      <p className="model-note">The earlier 70/15/15 development split is historical. These displayed rows are the final day-based research partitions. The test period ends at 11:12 UTC and is not a full day.</p>
    </section>

    <section className="model-section" aria-labelledby="model-title"><span className="eyebrow">04 / SELECTED MODEL</span><h2 id="model-title">Frozen unweighted LightGBM</h2>
      <p>A bounded comparison of LightGBM, HistGradientBoosting, decision tree, logistic regression, and a constant baseline ranked this existing diagnostic model first on reused validation F1. The team accepted its exact bytes for opt-in local capstone use. It was not refitted when frozen for test prediction.</p>
      <p className="model-note">These are frozen research and acceptance facts; this page does not assert that the currently running server has model mode enabled.</p>
      <dl className="model-fact-grid"><div><dt>Training rows</dt><dd>{integer(evidence.partitions[0].rows)}</dd></div><div><dt>Input width</dt><dd>11 fields → 32 columns</dd></div><div><dt>Best iteration</dt><dd>140 trees</dd></div><div><dt>Parameters</dt><dd>31 leaves · learning rate 0.05 · minimum child samples 200</dd></div><div><dt>Class handling</dt><dd>No class weighting or resampling; scale_pos_weight = 1</dd></div><div><dt>Selection</dt><dd>Positive-class F1 on validation; threshold {evidence.threshold}</dd></div></dl>
      <details className="model-disclosure"><summary>Frozen model identity</summary><code>{evidence.modelSha}</code><p>Native LightGBM model SHA-256. The independently trusted artifact manifest binds feature order, vocabulary, source, and threshold.</p></details>
    </section>

    <section className="model-section" aria-labelledby="evaluation-title"><span className="eyebrow">05 / AUTHORIZED AGGREGATES</span><h2 id="evaluation-title">What the model measured</h2>
      <p>Validation and test results below belong to the same frozen model and threshold. Test metrics come from one separately authorized evaluation of sealed predictions. The classes are highly imbalanced.</p>
      <MetricComparison />
      <MetricTable />
      <div className="confusion-grid">{evidence.results.map(result => <article key={result.name}><h3>{result.name} confusion matrix</h3><p>{integer(result.rows)} rows · {integer(result.positive)} positive · {integer(result.negative)} negative</p><dl><div><dt>True positive</dt><dd>{integer(result.tp)}</dd></div><div><dt>False positive</dt><dd>{integer(result.fp)}</dd></div><div><dt>True negative</dt><dd>{integer(result.tn)}</dd></div><div><dt>False negative</dt><dd>{integer(result.fn)}</dd></div></dl></article>)}</div>
      <p className="model-note">At this threshold, test recall is {percent(evidence.results[1].recall)} despite ROC AUC {decimal(evidence.results[1].rocAuc)}. A strong ranking metric does not mean most positive cases are alerted. Whole-partition Precision@K is not a daily review-capacity estimate.</p>
      <details className="model-disclosure"><summary>Evaluation report identity</summary><code>{evidence.reportSha}</code><p>SHA-256 of the approved aggregate T230 report. No test labels or per-transaction predictions are included in this page.</p></details>
    </section>

    <section className="model-section model-limits" aria-labelledby="limits-title"><span className="eyebrow">06 / INTERPRETATION</span><h2 id="limits-title">Limits and human authority</h2>
      <p>A score is a model output for a synthetic transaction, not a calibrated probability, legal finding, or decision to intervene. Brier score is a diagnostic; calibration has not been established. The validation partition was reused in model selection and diagnosis, and the test covers part of one UTC day. The source is synthetic and its original release and timezone remain unresolved.</p>
      <p>Human analysts make final case dispositions. RAG investigation is a separate advisory workflow; it was not part of LightGBM training or scoring.</p>
      <Link className="evidence-link" to="/eda">Inspect the dataset overview →</Link>
    </section>
  </div>;
}
