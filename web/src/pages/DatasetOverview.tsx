import { useEffect, useState, type CSSProperties } from "react";
import { ApiError, getOverview } from "../api";
import type { Overview, OverviewPoint } from "../contracts";

type LoadState = { kind: "loading" } | { kind: "error"; message: string }
  | { kind: "loaded"; overview: Overview };
type Series = { label: string; key: "transactions" | "flagged" | "not_flagged"; color: string };
interface OverviewClient { getOverview(options: { signal: AbortSignal }): Promise<Overview> }
const defaultClient: OverviewClient = { getOverview };

const number = (value: number) => new Intl.NumberFormat("en-US").format(value);
const percent = (value: number | null) => value === null ? "N/A" : `${(value * 100).toFixed(2)}%`;

function TrendChart({ points, title, series }: { points: OverviewPoint[]; title: string; series: Series[] }) {
  const max = Math.max(1, ...points.flatMap((point) => series.map(({ key }) => point[key])));
  const x = (index: number) => points.length === 1 ? 420 : 44 + index * (752 / (points.length - 1));
  const y = (value: number) => 224 - value / max * 186;
  return <figure className="chart-figure"><svg viewBox="0 0 840 280" role="img" aria-label={title}>
    <title>{title}</title>
    {points.length === 0 ? <text x="420" y="140" textAnchor="middle" className="chart-empty">No timestamped transactions</text>
      : <>
        {series.map((item, seriesIndex) => {
          const coords = points.map((point, pointIndex) => `${x(pointIndex)},${y(point[item.key])}`).join(" ");
          return <g key={item.key}>
            {item.key === "transactions" && <path d={`M${x(0)},224 L${coords.replaceAll(" ", " L")} L${x(points.length - 1)},224 Z`}
              className="chart-area" style={{ fill: item.color }} />}
            <polyline points={coords} className={`chart-line chart-line-${seriesIndex}`} style={{ stroke: item.color }} />
            {points.length <= 60 && points.map((point, pointIndex) =>
              <circle key={`${point.period}-${pointIndex}`} cx={x(pointIndex)} cy={y(point[item.key])} r="3" style={{ fill: item.color }} />)}
          </g>;
        })}
        <text x="44" y="258" className="chart-axis">{points[0].period}</text>
        <text x="796" y="258" textAnchor="end" className="chart-axis">{points.at(-1)?.period}</text>
      </>}
  </svg><figcaption className="chart-legend">{series.map((item) => <span key={item.key} style={{ "--legend-color": item.color } as CSSProperties}>{item.label}</span>)}</figcaption></figure>;
}

function Kpi({ label, value, detail, kind = "" }: { label: string; value: string; detail: string; kind?: string }) {
  return <article className={`kpi-card ${kind}`}><p className="kpi-label">{label}</p>
    <p className="kpi-value">{value}</p><p className="kpi-detail">{detail}</p></article>;
}

function Dashboard({ overview }: { overview: Overview }) {
  const predictions = overview.predictions;
  const share = predictions.flag_rate;
  return <div className="overview-dashboard">
    <header className="overview-header"><p className="eyebrow">FRAUDLENS AI · ANALYTICS</p>
      <h1>Dataset &amp; Model Overview</h1>
      <p className="intro">A read-only view of the active scoring run and its verified scope.</p>
      <p className="data-source-line"><span>IBM AML synthetic dataset · {overview.dataset.dataset_version}</span>
        <span className="run-id">{overview.dataset.run_id}</span></p>
    </header>
    <aside className="integrity-notice" aria-label="Ground-truth label availability">
      <strong>Confirmed labels are unavailable in this dashboard.</strong>
      <p>{overview.dataset.label_unavailable_reason} Flagged and not flagged counts below are model predictions, not confirmed fraud or legitimate transactions.</p>
    </aside>
    {overview.dataset.scored_transactions === 0 && <p className="empty-state">No transactions were scored in this completed run.</p>}
    <section className="kpi-grid" aria-label="Dataset statistics">
      <Kpi label="Transactions scored" value={number(overview.dataset.scored_transactions)} detail="Active run population" kind="kpi-total" />
      <Kpi label="Confirmed fraudulent" value="N/A" detail="Private evaluation labels are not exposed." kind="kpi-fraud" />
      <Kpi label="Legitimate transactions" value="N/A" detail="Private evaluation labels are not exposed." />
      <Kpi label="Confirmed fraud rate" value="N/A" detail="Cannot be calculated without confirmed labels." />
    </section>
    <section className="panel time-panel"><header className="panel-heading"><h2>Transaction volume over time</h2>
      <p>{overview.aggregation === "week" ? "Weekly" : "Daily"} counts from completed run scores.</p></header>
      <TrendChart points={overview.series} title="Transactions scored over time" series={[{ label: "Transactions scored", key: "transactions", color: "#329DD2" }]} />
    </section>
    <section className="panel trend-panel"><header className="panel-heading"><h2>Model predictions over time</h2>
      <p>Predicted flagged vs not flagged. These are not ground-truth classes.</p></header>
      <TrendChart points={overview.series} title="Model flagged and not flagged predictions over time" series={[
        { label: "Model flagged", key: "flagged", color: "#FF4C2B" },
        { label: "Not flagged", key: "not_flagged", color: "#329DD2" },
      ]} />
    </section>
    <section className="panel distribution-panel"><header className="panel-heading"><h2>Prediction distribution</h2><p>Model output at the active threshold.</p></header>
      <div className="prediction-donut" role="img" aria-label={share === null ? "No predictions available for an empty run"
        : `${number(predictions.flagged)} model flagged; ${number(predictions.not_flagged)} not flagged`}
        style={share === null ? undefined : { "--flag-share": `${share * 100}%` } as CSSProperties}>
        <span>{percent(share)}</span></div>
      <ul className="distribution-legend"><li className="legend-fraud">Model flagged · {number(predictions.flagged)}</li>
        <li className="legend-clear">Not flagged · {number(predictions.not_flagged)}</li></ul>
    </section>
    <section className="panel model-panel"><header className="panel-heading"><h2>Active model</h2><p>Identity from the completed active scoring run.</p></header>
      <h3 className="model-name">{overview.model.name}</h3>
      <div className="metric-grid"><Kpi label="Precision · fraud class" value="N/A" detail="No ground-truth labels in this run." />
        <Kpi label="Recall · fraud class" value="N/A" detail="No ground-truth labels in this run." />
        <Kpi label="F1-score · fraud class" value="N/A" detail="No ground-truth labels in this run." /></div>
      <dl className="model-fields"><div><dt>Model version</dt><dd>{overview.model.scorer_version}</dd></div>
        <div><dt>Scoring source</dt><dd>{overview.model.source}</dd></div>
        <div><dt>Evaluation dataset / split</dt><dd>N/A · not attached to this run</dd></div>
        <div><dt>Decision threshold</dt><dd>{overview.model.threshold}</dd></div>
        <div><dt>Metric source</dt><dd>{overview.model.metric_source}</dd></div></dl>
    </section>
    <p className="overview-footnote">Unknown timestamps: {number(overview.dataset.unknown_timestamp_transactions)}. The aggregate endpoint does not read private labels or return transaction records.</p>
  </div>;
}

export function DatasetOverviewPage({ client = defaultClient }: { client?: OverviewClient }) {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<LoadState>({ kind: "loading" });
  useEffect(() => {
    const controller = new AbortController();
    setState({ kind: "loading" });
    void client.getOverview({ signal: controller.signal }).then((overview) => setState({ kind: "loaded", overview }))
      .catch((error: unknown) => {
        if (controller.signal.aborted) return;
        const failure = error instanceof ApiError ? error : new ApiError("internal_error");
        setState({ kind: "error", message: failure.code === "run_unavailable"
          ? "No active dataset or model run is configured." : failure.message });
      });
    return () => controller.abort();
  }, [attempt, client]);

  if (state.kind === "loading") return <section className="dataset-overview" aria-busy="true"><p role="status">Loading dataset and model overview…</p></section>;
  if (state.kind === "error") return <section className="dataset-overview overview-error"><h1>Dataset &amp; Model Overview</h1>
    <p role="alert">{state.message}</p><button className="button" type="button" onClick={() => setAttempt((value) => value + 1)}>Retry overview</button>
    {state.message.includes("No active dataset") && <p className="muted">Start a completed dataset-mode run to view aggregates.</p>}
  </section>;
  return <section className="dataset-overview"><Dashboard overview={state.overview} /></section>;
}
