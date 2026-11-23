import { act, type ReactNode } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, expect, it, vi } from "vitest";
import { ApiError } from "../src/api";
import { decodeCaseDetailV2, decodeCaseListV2 } from "../src/contracts";
import { CasesPage } from "../src/pages/Cases";
import { DETAIL_V2, LIST_V2 } from "./dataset-fixture";

const fixtureList = {
  items: [{ case_id: "CASE-001", transaction_id: "TX-001", score: 0.75,
    score_source: "fixture" as const }],
};
const fixtureDetail = {
  case_id: "CASE-001",
  transaction: { transaction_id: "TX-001", occurred_at: "2026-01-01T10:00:00Z",
    sender_account: "DEMO-A:001", receiver_account: "DEMO-B:002", amount: "1250.00", currency: "EUR" },
  risk_assessment: { transaction_id: "TX-001", score: 0.75, source: "fixture" as const,
    scorer_version: "fixture-v1", scored_at: "2026-01-01T10:00:00Z",
    explanation: "Illustrative synthetic score; no ML inference performed." },
};

let container: HTMLDivElement;
let root: Root;
async function render(node: ReactNode): Promise<void> {
  await act(async () => { root.render(node); });
}
async function click(selector: string): Promise<void> {
  const button = container.querySelector<HTMLButtonElement>(selector);
  if (!button) throw new Error(`Missing button ${selector}`);
  await act(async () => { button.click(); });
}

afterEach(async () => {
  await act(async () => { root.unmount(); });
  container.remove();
});

it("lists fixture cases and opens their typed details", async () => {
  container = document.createElement("div"); document.body.append(container);
  root = createRoot(container);
  await render(<CasesPage client={{ getCases: async () => fixtureList,
    getCase: async () => fixtureDetail }} dataset={false} />);
  expect(container.textContent).toContain("CASE-001");
  await click(".case-choice");
  expect(container.textContent).toContain("DEMO-A:001");
  expect(container.textContent).toContain("Illustrative synthetic score");
});

it("sorts fixture cases by ID and ignores a late response from an older selection", async () => {
  container = document.createElement("div"); document.body.append(container); root = createRoot(container);
  const fixtureListTwo = { items: [
    { case_id: "CASE-002", transaction_id: "TX-002", score: 0.4, score_source: "rules" as const },
    ...fixtureList.items,
  ] };
  let resolveFirst!: (detail: typeof fixtureDetail) => void;
  let resolveSecond!: (detail: typeof fixtureDetail) => void;
  const getCase = vi.fn((caseId: string) => new Promise<typeof fixtureDetail>((resolve) => {
    if (caseId === "CASE-001") resolveFirst = resolve;
    else resolveSecond = resolve;
  }));
  await render(<CasesPage client={{ getCases: async () => fixtureListTwo, getCase }} dataset={false} />);
  expect([...container.querySelectorAll(".case-choice")].map((button) => button.textContent?.slice(0, 8)))
    .toEqual(["CASE-001", "CASE-002"]);
  await click(".case-choice");
  const buttons = container.querySelectorAll<HTMLButtonElement>(".case-choice");
  await act(async () => { buttons[1]?.click(); });
  const secondDetail = { ...fixtureDetail, case_id: "CASE-002",
    transaction: { ...fixtureDetail.transaction, transaction_id: "TX-002", sender_account: "SECOND-BANK:002" },
    risk_assessment: { ...fixtureDetail.risk_assessment, transaction_id: "TX-002" } };
  await act(async () => { resolveSecond(secondDetail); });
  expect(container.textContent).toContain("SECOND-BANK:002");
  await act(async () => { resolveFirst(fixtureDetail); });
  expect(container.textContent).toContain("SECOND-BANK:002");
  expect(container.textContent).not.toContain("DEMO-A:001");
});

it("keeps the v2 snapshot on detail requests and shows stale recovery", async () => {
  container = document.createElement("div"); document.body.append(container);
  root = createRoot(container);
  const getCase = vi.fn(async () => { throw new ApiError("stale_snapshot", 409); });
  const listing = decodeCaseListV2(LIST_V2);
  await render(<CasesPage client={{ getCases: async () => listing, getCase }} dataset />);
  await click(".case-choice");
  expect(getCase).toHaveBeenCalledWith(LIST_V2.items[0].case_id,
    expect.objectContaining({ snapshot: LIST_V2.snapshot_ref }));
  expect(container.textContent).toContain("listu");
  expect(container.textContent).not.toContain("1250.000 Australian Dollar");
});

it("separates empty dataset state from an unavailable API", async () => {
  container = document.createElement("div"); document.body.append(container);
  root = createRoot(container);
  const empty = decodeCaseListV2({ ...LIST_V2, total_alerts: 0, displayed_count: 0,
    selected_time_range: { from: null, to: null }, items: [] });
  const detail = decodeCaseDetailV2(DETAIL_V2);
  await render(<CasesPage client={{ getCases: async () => empty, getCase: async () => detail }} dataset />);
  expect(container.textContent).toContain("0");
  expect(container.textContent).toContain("Nema upozorenja");
});

it("recovers explicitly from stale snapshots and escapes API text", async () => {
  container = document.createElement("div"); document.body.append(container); root = createRoot(container);
  const getCases = vi.fn(async () => decodeCaseListV2(LIST_V2));
  const getCase = vi.fn(async () => { throw new ApiError("stale_snapshot", 409); });
  await render(<CasesPage client={{ getCases, getCase }} dataset />);
  await click(".case-choice");
  await click(".case-panel button:not(.button-back)");
  expect(getCases).toHaveBeenCalledTimes(2);

  const hostileDetail = { ...fixtureDetail, transaction: { ...fixtureDetail.transaction,
    sender_account: '<img src=x onerror="alert(1)">' } };
  await render(<CasesPage client={{ getCases: async () => fixtureList,
    getCase: async () => hostileDetail }} dataset={false} />);
  await click(".case-choice");
  expect(container.querySelector("img")).toBeNull();
  expect(container.textContent).toContain('<img src=x onerror="alert(1)">');
});
