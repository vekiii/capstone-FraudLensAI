import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { decodeCaseDetailV2, decodeCaseListV2 } from "../src/contracts";
import { CasesPage } from "../src/pages/Cases";
import { DETAIL_V2, LIST_V2 } from "./dataset-fixture";
import fixtureRun from "../../specs/003-ai-investigation/contracts/examples/run-ready.json";
const datasetRun = { ...fixtureRun, case_id: DETAIL_V2.case_id, source_mode: "dataset",
  snapshot_ref: DETAIL_V2.snapshot_ref };

function listResponse(snapshot: string, items: unknown[] = [], revision = fixtureRun.context_revision) {
  return new Response(JSON.stringify({ contract_version: 1, items, total_count: items.length,
    truncated: false }), { headers: { "content-type": "application/json",
    "x-investigation-snapshot": snapshot, "x-investigation-context": revision } });
}

let container: HTMLDivElement;
let root: Root;
const fetcher = vi.fn<typeof fetch>();

beforeEach(() => {
  container = document.createElement("div");
  document.body.append(container);
  root = createRoot(container);
  fetcher.mockReset();
  vi.stubGlobal("fetch", fetcher);
});

afterEach(async () => {
  await act(async () => root.unmount());
  container.remove();
  vi.unstubAllGlobals();
});

async function click(selector: string) {
  const button = container.querySelector<HTMLButtonElement>(selector);
  expect(button, selector).not.toBeNull();
  await act(async () => button!.click());
}

async function openDataset() {
  const detail = decodeCaseDetailV2(DETAIL_V2);
  const secondId = "C" + "2".repeat(32);
  const listing = decodeCaseListV2({ ...LIST_V2, displayed_count: 2, total_alerts: 2,
    items: [...LIST_V2.items, { ...LIST_V2.items[0], case_id: secondId,
      transaction_id: "D" + "2".repeat(32) }] });
  await act(async () => root.render(<CasesPage dataset client={{
    getCases: async () => listing,
    getCase: async id => ({ ...detail, case_id: id }),
  }} />));
  await click(`[aria-label="Otvori ${detail.case_id}"]`);
  await click(".investigation-panel > button");
  await act(async () => vi.dynamicImportSettled());
  return secondId;
}

it("opens the v2 report panel and creates with the dataset identity and snapshot", async () => {
  fetcher.mockResolvedValueOnce(listResponse(DETAIL_V2.snapshot_ref));
  fetcher.mockResolvedValueOnce(new Response(JSON.stringify(datasetRun), { status: 202,
    headers: { "content-type": "application/json" } }));
  await openDataset();
  expect(fetcher.mock.calls[0][0]).toBe("/api/investigation/runs?case_id=" + DETAIL_V2.case_id);
  await click("[data-start]");
  expect(JSON.parse(String(fetcher.mock.calls[1][1]?.body))).toEqual({
    case_id: DETAIL_V2.case_id, source_mode: "dataset", snapshot_ref: DETAIL_V2.snapshot_ref,
  });
  expect(container.querySelector("[data-run-state]")?.textContent).toContain("ready_for_review");
});

it.each([
  ["stale_snapshot", () => listResponse("run_replaced")],
  ["invalid_response", () => listResponse(DETAIL_V2.snapshot_ref, [datasetRun], "e".repeat(64))],
])("blocks mutations after a %s binding, including after refresh", async (code, response) => {
  fetcher.mockImplementation(async () => response());
  await openDataset();
  expect(container.querySelector(".investigation-panel [role=alert]")?.textContent).toContain(code);
  await click("[data-refresh]");
  expect(container.querySelector<HTMLButtonElement>("[data-start]")?.disabled).toBe(true);
  await click("[data-start]");
  expect(fetcher.mock.calls).toHaveLength(2);
  expect(fetcher.mock.calls.every(([, init]) => !init?.method)).toBe(true);
});

it("aborts an investigation read on selection change and ignores its late result", async () => {
  let finish!: (value: Response) => void;
  fetcher.mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }));
  const nextId = await openDataset();
  const firstSignal = fetcher.mock.calls[0][1]?.signal;
  await click(`[aria-label="Otvori ${nextId}"]`);
  fetcher.mockResolvedValueOnce(listResponse(DETAIL_V2.snapshot_ref));
  await click(".investigation-panel > button");
  await act(async () => vi.dynamicImportSettled());
  expect(firstSignal?.aborted).toBe(true);
  await act(async () => finish(listResponse(DETAIL_V2.snapshot_ref, [datasetRun])));
  expect(container.querySelector("[data-run-state]")).toBeNull();
  expect(container.querySelector(".investigation-panel")?.textContent).toContain("Sačuvano istraga: 0");
  expect(fetcher.mock.calls[1][0]).toBe("/api/investigation/runs?case_id=" + nextId);
});

it("keeps the existing fixture identity and create request", async () => {
  fetcher.mockResolvedValueOnce(listResponse(fixtureRun.snapshot_ref));
  fetcher.mockResolvedValueOnce(new Response(JSON.stringify(fixtureRun), { status: 202,
    headers: { "content-type": "application/json" } }));
  const detail = {
    case_id: "CASE-001",
    transaction: { transaction_id: "TX-001", occurred_at: "2026-01-01T10:00:00Z",
      sender_account: "DEMO-A:001", receiver_account: "DEMO-B:002", amount: "1.00", currency: "EUR" },
    risk_assessment: { transaction_id: "TX-001", score: 0.75, source: "fixture" as const,
      scorer_version: "fixture-v1", scored_at: "2026-01-01T10:00:00Z", explanation: "Synthetic" },
  };
  await act(async () => root.render(<CasesPage dataset={false} client={{
    getCases: async () => ({ items: [{ case_id: detail.case_id, transaction_id: "TX-001",
      score: 0.75, score_source: "fixture" }] }),
    getCase: async () => detail,
  }} />));
  await click(".case-choice");
  await click(".investigation-panel > button");
  await act(async () => vi.dynamicImportSettled());
  await click("[data-start]");
  expect(JSON.parse(String(fetcher.mock.calls[1][1]?.body))).toEqual({
    case_id: "CASE-001", source_mode: "fixture", snapshot_ref: fixtureRun.snapshot_ref,
  });
  expect(container.querySelector("[data-run-state]")?.textContent).toContain("ready_for_review");
});
