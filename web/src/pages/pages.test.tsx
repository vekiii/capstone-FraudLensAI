import { describe, expect, it } from "vitest";
import { readFile } from "node:fs/promises";
import { renderToStaticMarkup } from "react-dom/server";
import type { ReactNode } from "react";
import { MemoryRouter } from "react-router-dom";
import { SiteDataContext, loadShowcaseData } from "../site-data";
import { Overview } from "./Overview";
import { DataPage } from "./Data";
import { RagPage } from "./Rag";
import { LivePage } from "./Live";

async function loadPublicSources() {
  const names = ["metrics.json", "eda.json", "features.json", "explanations_global.json", "kb_stats.json", "rag_eval.json", "samples.json"];
  const bodies = await Promise.all(names.map((name) => readFile(`public/data/${name}`, "utf8")));
  let index = 0;
  const data = await loadShowcaseData(async () => {
    const body = bodies[index++];
    return new Response(body, { status: 200, headers: { "content-type": "application/json" } });
  });
  return { data, requested: index };
}

function markup(page: ReactNode, data: Awaited<ReturnType<typeof loadPublicSources>>["data"]) {
  return renderToStaticMarkup(<SiteDataContext.Provider value={data}><MemoryRouter>{page}</MemoryRouter></SiteDataContext.Provider>);
}

describe("showcase pages", () => {
  it("reads displayed figures and feature definitions from public data files", async () => {
    const { data, requested } = await loadPublicSources();
    expect(requested).toBe(7);
    expect(data.metrics.status).toBe("not_yet_measured");
    expect(data.metrics.generated_at).toBeTruthy();
    expect(data.eda.status).toBe("not_yet_measured");
    expect(data.eda.generated_at).toBeTruthy();
    expect(data.ragEval.status).toBe("not_yet_measured");
    expect(markup(<Overview />, data)).toContain("Not yet measured");
    expect(markup(<DataPage />, data)).toContain("Frozen unweighted LightGBM");
    expect(markup(<RagPage />, data)).toContain("Retrieval-Augmented <em>Investigations</em>");
    const features = markup(<DataPage />, data);
    expect(data.features.features).toHaveLength(11);
    expect(features).toContain("sender_out_count_24h");
    expect(features).toContain("current_payment_format");
    expect(features).toContain("current_amount_paid_log1p");
    expect(features).not.toContain("current_paid_amount</");
  });

  it("labels every illustrative sample in JSON and on screen", async () => {
    const { data } = await loadPublicSources();
    const html = markup(<LivePage />, data);
    expect(data.samples.source).toBe("illustrative");
    expect(data.samples.samples.every((sample) => sample.label === "ILLUSTRATIVE, not model output")).toBe(true);
    expect(html).toContain("ILLUSTRATIVE, not model output");
    expect(html).toContain("FIXTURE");
    expect(html).toContain("All data is synthetic");
  });

  it("separates implemented retrieval, optional semantic selection, and report quality", async () => {
    const { data } = await loadPublicSources();
    const html = markup(<RagPage />, data);
    expect(html).toContain("get_case_facts");
    expect(html).toContain("get_account_history");
    expect(html).toContain("search_procedures");
    expect(html).toContain("GET /api/knowledge/search");
    expect(html).toContain("POST /api/knowledge/semantic-search");
    expect(html).toContain("0.864583");
    expect(html).toContain("0.9375");
    expect(html).toContain("0/8");
    expect(html).toContain("3/4");
    expect(html).toContain("2/3");
    expect(html).toContain("Analyst review");
    expect(html).toMatch(/<ol[^>]*aria-label="Sequential review steps"[^>]*>.*Structured AI report draft.*Validation.*Analyst review.*<\/ol>/);
    expect(html).toContain("Report-quality gate not met");
    expect(html).not.toContain("was absent from this checkout");
    expect(html).not.toContain("proposed advisory verification layer");
  });
});
