import { readFile } from 'node:fs/promises';
import { renderToStaticMarkup } from 'react-dom/server';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { modelEvidence, modelFeatures } from '../src/model-evidence';
import { DataPage } from '../src/pages/Data';

describe('frozen model presentation', () => {
  it('reconciles every partition and confusion matrix with the approved aggregate counts', () => {
    expect(modelEvidence.partitions.reduce((sum, item) => sum + item.rows, 0))
      .toBe(modelEvidence.scoreableDevelopment);
    for (const partition of modelEvidence.partitions) {
      expect(partition.positive + partition.negative).toBe(partition.rows);
    }
    for (const result of modelEvidence.results) {
      expect(result.tp + result.fn).toBe(result.positive);
      expect(result.tn + result.fp).toBe(result.negative);
      expect(result.tp + result.fp).toBe(result.alerts);
      expect(result.tp / result.alerts).toBeCloseTo(result.precision, 12);
      expect(result.tp / result.positive).toBeCloseTo(result.recall, 12);
      expect(2 * result.precision * result.recall / (result.precision + result.recall))
        .toBeCloseTo(result.f1, 12);
    }
  });

  it('uses the implemented eleven-feature order and names the frozen model on the page', async () => {
    const kernel = await readFile('../backend/src/fraudlens/data/features.py', 'utf8');
    const order = kernel.slice(kernel.indexOf('HISTORY_FEATURE_ORDER = ('), kernel.indexOf('_NAIVE_TIMESTAMP'));
    const names = [...order.matchAll(/'([^']+)'/g)].map(match => match[1]);
    expect(modelFeatures.map(([name]) => name)).toEqual(names);
    const html = renderToStaticMarkup(<MemoryRouter><DataPage /></MemoryRouter>);
    expect(html).toContain('Frozen unweighted LightGBM');
    expect(html).toContain('1,884,981');
    expect(html).toContain('0.2489517623052024');
    expect(html).toContain(modelEvidence.reportSha);
    expect(html).toContain('href="/eda"');
    expect(html).not.toContain('Not yet measured');
  });
});
