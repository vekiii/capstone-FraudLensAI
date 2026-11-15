import type { Overview, OverviewPoint } from './contracts';

export type OverviewState =
  | { kind: 'loading' }
  | { kind: 'error'; message: string }
  | { kind: 'loaded'; overview: Overview };

function element<K extends keyof HTMLElementTagNameMap>(tag: K, text?: string,
  className?: string): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function svgElement<K extends keyof SVGElementTagNameMap>(tag: K): SVGElementTagNameMap[K] {
  return document.createElementNS('http://www.w3.org/2000/svg', tag);
}

function number(value: number): string {
  return new Intl.NumberFormat('en-US').format(value);
}

function percent(value: number | null): string {
  return value === null ? 'N/A' : `${(value * 100).toFixed(2)}%`;
}

function chart(points: OverviewPoint[], title: string,
  series: { label: string; key: 'transactions' | 'flagged' | 'not_flagged'; color: string }[]) {
  const figure = element('figure', undefined, 'chart-figure');
  const svg = svgElement('svg');
  svg.setAttribute('viewBox', '0 0 840 280');
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', title);
  const heading = svgElement('title');
  heading.textContent = title;
  svg.append(heading);
  if (!points.length) {
    const empty = svgElement('text');
    empty.setAttribute('x', '420'); empty.setAttribute('y', '140');
    empty.setAttribute('text-anchor', 'middle'); empty.setAttribute('class', 'chart-empty');
    empty.textContent = 'No timestamped transactions';
    svg.append(empty);
  } else {
    const max = points.reduce((highest, point) => Math.max(highest,
      ...series.map(item => point[item.key])), 1);
    const x = (index: number) => points.length === 1
      ? 420 : 44 + index * (752 / (points.length - 1));
    const y = (value: number) => 224 - value / max * 186;
    for (const [index, item] of series.entries()) {
      const coords = points.map((point, pointIndex) => `${x(pointIndex)},${y(point[item.key])}`);
      if (item.key === 'transactions') {
        const area = svgElement('path');
        area.setAttribute('d', `M${x(0)},224 L${coords.join(' L')} L${x(points.length - 1)},224 Z`);
        area.setAttribute('class', 'chart-area');
        area.style.fill = item.color;
        svg.append(area);
      }
      const line = svgElement('polyline');
      line.setAttribute('points', coords.join(' '));
      line.setAttribute('class', `chart-line chart-line-${index}`);
      line.style.stroke = item.color;
      svg.append(line);
      if (points.length <= 60) points.forEach((point, pointIndex) => {
        const dot = svgElement('circle');
        dot.setAttribute('cx', String(x(pointIndex)));
        dot.setAttribute('cy', String(y(point[item.key])));
        dot.setAttribute('r', '3');
        dot.style.fill = item.color;
        svg.append(dot);
      });
    }
    const first = svgElement('text');
    first.setAttribute('x', '44'); first.setAttribute('y', '258'); first.textContent = points[0].period;
    const last = svgElement('text');
    last.setAttribute('x', '796'); last.setAttribute('y', '258');
    last.setAttribute('text-anchor', 'end'); last.textContent = points.at(-1)!.period;
    first.setAttribute('class', 'chart-axis'); last.setAttribute('class', 'chart-axis');
    svg.append(first, last);
  }
  figure.append(svg);
  const legend = element('figcaption', undefined, 'chart-legend');
  for (const item of series) {
    const entry = element('span', item.label);
    entry.style.setProperty('--legend-color', item.color);
    legend.append(entry);
  }
  figure.append(legend);
  return figure;
}

function kpi(label: string, value: string, detail: string, kind = '') {
  const card = element('article', undefined, `kpi-card ${kind}`.trim());
  card.append(element('p', label, 'kpi-label'), element('p', value, 'kpi-value'),
    element('p', detail, 'kpi-detail'));
  return card;
}

function section(title: string, subtitle?: string) {
  const header = element('header', undefined, 'panel-heading');
  header.append(element('h2', title));
  if (subtitle) header.append(element('p', subtitle, 'muted'));
  return header;
}

function dashboard(overview: Overview) {
  const root = element('div', undefined, 'overview-dashboard');
  const heading = element('header', undefined, 'overview-header');
  heading.append(element('p', 'FRAUDLENS AI · ANALYTICS', 'eyebrow'),
    element('h1', 'Dataset & Model Overview'),
    element('p', 'A read-only view of the active scoring run and its verified scope.', 'intro'));
  const source = element('p', undefined, 'data-source-line');
  source.append(element('span', `IBM AML synthetic dataset · ${overview.dataset.dataset_version}`,
    'dataset-identity'), element('span', overview.dataset.run_id, 'run-id'));
  heading.append(source);

  const notice = element('aside', undefined, 'integrity-notice');
  notice.setAttribute('aria-label', 'Ground-truth label availability');
  notice.append(element('strong', 'Confirmed labels are unavailable in this dashboard.'),
    element('p', overview.dataset.label_unavailable_reason
      + ' Flagged and not flagged counts below are model predictions, not confirmed fraud or legitimate transactions.'));

  const kpis = element('section', undefined, 'kpi-grid');
  kpis.setAttribute('aria-label', 'Dataset statistics');
  kpis.append(
    kpi('Transactions scored', number(overview.dataset.scored_transactions),
      'Active run population', 'kpi-total'),
    kpi('Confirmed fraudulent', 'N/A', 'Private evaluation labels are not exposed.', 'kpi-fraud'),
    kpi('Legitimate transactions', 'N/A', 'Private evaluation labels are not exposed.'),
    kpi('Confirmed fraud rate', 'N/A', 'Cannot be calculated without confirmed labels.'),
  );

  const timePanel = element('section', undefined, 'panel time-panel');
  timePanel.append(section('Transaction volume over time',
    `${overview.aggregation === 'week' ? 'Weekly' : 'Daily'} counts from completed run scores.`),
  chart(overview.series, 'Transactions scored over time', [
    { label: 'Transactions scored', key: 'transactions', color: '#329DD2' },
  ]));

  const predictionPanel = element('section', undefined, 'panel trend-panel');
  predictionPanel.append(section('Model predictions over time',
    'Predicted flagged vs not flagged. These are not ground-truth classes.'),
  chart(overview.series, 'Model flagged and not flagged predictions over time', [
    { label: 'Model flagged', key: 'flagged', color: '#FF4C2B' },
    { label: 'Not flagged', key: 'not_flagged', color: '#329DD2' },
  ]));

  const distribution = element('section', undefined, 'panel distribution-panel');
  distribution.append(section('Prediction distribution', 'Model output at the active threshold.'));
  const share = overview.predictions.flag_rate;
  const donut = element('div', undefined, 'prediction-donut');
  donut.setAttribute('role', 'img');
  donut.setAttribute('aria-label', share === null
    ? 'No predictions available for an empty run'
    : `${number(overview.predictions.flagged)} model flagged; `
      + `${number(overview.predictions.not_flagged)} not flagged`);
  if (share !== null) donut.style.setProperty('--flag-share', `${share * 100}%`);
  donut.append(element('span', share === null ? 'N/A' : percent(share)));
  distribution.append(donut);
  const predictionLegend = element('ul', undefined, 'distribution-legend');
  predictionLegend.append(
    element('li', `Model flagged · ${number(overview.predictions.flagged)}`, 'legend-fraud'),
    element('li', `Not flagged · ${number(overview.predictions.not_flagged)}`, 'legend-clear'));
  distribution.append(predictionLegend);

  const model = element('section', undefined, 'panel model-panel');
  model.append(section('Active model', 'Identity from the completed active scoring run.'));
  const modelName = element('h3', overview.model.name, 'model-name');
  const performance = element('div', undefined, 'metric-grid');
  performance.append(kpi('Precision · fraud class', 'N/A', 'No ground-truth labels in this run.'),
    kpi('Recall · fraud class', 'N/A', 'No ground-truth labels in this run.'),
    kpi('F1-score · fraud class', 'N/A', 'No ground-truth labels in this run.'));
  model.append(modelName, performance);
  const fields = element('dl', undefined, 'model-fields');
  const fieldRows: [string, string][] = [
    ['Model version', overview.model.scorer_version],
    ['Scoring source', overview.model.source],
    ['Evaluation dataset / split', 'N/A · not attached to this run'],
    ['Decision threshold', overview.model.threshold],
    ['Metric source', overview.model.metric_source],
  ];
  for (const [label, value] of fieldRows) {
    const row = element('div'); row.append(element('dt', label), element('dd', value));
    fields.append(row);
  }
  model.append(fields);

  const footer = element('p', `Unknown timestamps: ${number(overview.dataset.unknown_timestamp_transactions)}. `
    + 'The aggregate endpoint does not read private labels or return transaction records.', 'overview-footnote');
  root.append(heading, notice, kpis, timePanel, predictionPanel, distribution, model, footer);
  if (overview.dataset.scored_transactions === 0) {
    root.insertBefore(element('p', 'No transactions were scored in this completed run.',
      'empty-state'), kpis);
  }
  return root;
}

export function createOverviewView(root: HTMLElement, retry: () => void) {
  return {
    render(state: OverviewState) {
      root.replaceChildren();
      root.setAttribute('aria-busy', String(state.kind === 'loading'));
      if (state.kind === 'loading') {
        const loading = element('p', 'Loading dataset and model overview…', 'state-message');
        loading.setAttribute('role', 'status'); root.append(loading); return;
      }
      if (state.kind === 'error') {
        const panel = element('section', undefined, 'overview-error');
        const message = element('p', state.message);
        message.setAttribute('role', 'alert');
        const button = element('button', 'Retry overview', 'button');
        button.dataset.action = 'retry-overview'; button.type = 'button';
        button.addEventListener('click', retry);
        panel.append(element('h1', 'Dataset & Model Overview'), message, button);
        if (state.message.includes('run_unavailable')) {
          panel.append(element('p', 'No active dataset or model run is configured. Start a completed dataset-mode run to view aggregates.', 'muted'));
        }
        root.append(panel); return;
      }
      root.append(dashboard(state.overview));
    },
  };
}
