import { act, type ReactNode } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, expect, it, vi } from "vitest";
import { ApiError } from "../src/api";
import type { Overview } from "../src/contracts";
import { DatasetOverviewPage } from "../src/pages/DatasetOverview";

const overview: Overview = {
  contract_version: 1,
  dataset: { data_source: "ibm_aml_hi_small", dataset_version: `dv_${"a".repeat(64)}`,
    run_id: "run_overview", scored_transactions: 3, unknown_timestamp_transactions: 0,
    confirmed_fraud: null, legitimate: null, fraud_rate: null,
    label_unavailable_reason: "Ground-truth labels are not available to the serving API." },
  predictions: { flagged: 2, not_flagged: 1, flag_rate: 2 / 3 },
  series: [{ period: "2022-09-10", transactions: 3, flagged: 2, not_flagged: 1 }],
  aggregation: "day",
  model: { name: "Rule-based scorer", source: "rules", scorer_version: "rules-v1",
    threshold: "0.5", evaluation_dataset: null, evaluation_split: null,
    precision: null, recall: null, f1: null,
    metric_source: "Unavailable because this active run has no ground-truth labels." },
};

let container: HTMLDivElement;
let root: Root;
async function render(node: ReactNode): Promise<void> {
  await act(async () => { root.render(node); });
}
afterEach(async () => {
  await act(async () => { root.unmount(); });
  container.remove();
});

it("renders trusted aggregate counts, trends, label limits and model provenance", async () => {
  container = document.createElement("div"); document.body.append(container); root = createRoot(container);
  await render(<DatasetOverviewPage client={{ getOverview: async () => overview }} />);
  expect(container.querySelectorAll(".kpi-grid > .kpi-card")).toHaveLength(4);
  expect(container.textContent).toContain("3");
  expect(container.textContent).toContain("N/A");
  expect(container.textContent).toContain("Model flagged");
  expect(container.textContent).toContain("not confirmed fraud");
  expect(container.textContent).toContain("rules-v1");
  expect(container.querySelector('svg[role="img"]')).not.toBeNull();
});

it("keeps unavailable runs explicit and retries on user action", async () => {
  container = document.createElement("div"); document.body.append(container); root = createRoot(container);
  let fail = true;
  const getOverview = vi.fn(async () => {
    if (fail) throw new ApiError("run_unavailable", 503);
    return { ...overview, dataset: { ...overview.dataset, scored_transactions: 0 },
      predictions: { flagged: 0, not_flagged: 0, flag_rate: null }, series: [] };
  });
  await render(<DatasetOverviewPage client={{ getOverview }} />);
  expect(container.textContent).toContain("No active dataset or model run");
  fail = false;
  const retry = container.querySelector<HTMLButtonElement>("button");
  if (!retry) throw new Error("Missing retry control");
  await act(async () => { retry.click(); });
  expect(container.textContent).toContain("No transactions were scored");
  expect(container.querySelectorAll(".kpi-grid > .kpi-card")).toHaveLength(4);
});
