import { createContext, useContext } from "react";

export type FigureStatus = { status: string; source_version: string; generated_at: string | null; label: string; note?: string };
export type FeatureCatalog = { status: string; source_version: string; generated_at: string | null; features: Array<{ name: string; definition: string }> };
export type DemoSamples = { source: string; source_version: string; generated_at: string | null; label: string; samples: Array<{ id: string; label: string; title: string; status: string; amount: string; currency: string }> };
export type ShowcaseData = {
  metrics: FigureStatus & { integration_fixture_label: string };
  eda: FigureStatus;
  features: FeatureCatalog;
  explanationsGlobal: FigureStatus;
  kbStats: FigureStatus;
  ragEval: FigureStatus;
  samples: DemoSamples;
};

export const SiteDataContext = createContext<ShowcaseData | null>(null);
export const useShowcaseData = () => useContext(SiteDataContext);

const sources = [
  ["metrics", "/data/metrics.json"],
  ["eda", "/data/eda.json"],
  ["features", "/data/features.json"],
  ["explanationsGlobal", "/data/explanations_global.json"],
  ["kbStats", "/data/kb_stats.json"],
  ["ragEval", "/data/rag_eval.json"],
  ["samples", "/data/samples.json"],
] as const;

export async function loadShowcaseData(fetcher: typeof fetch = fetch): Promise<ShowcaseData> {
  const entries = await Promise.all(sources.map(async ([key, path]) => {
    const response = await fetcher(path, { headers: { Accept: "application/json" } });
    if (!response.ok || !response.headers.get("content-type")?.includes("application/json")) {
      throw new Error(`Showcase source unavailable: ${path}`);
    }
    return [key, await response.json()] as const;
  }));
  return Object.fromEntries(entries) as ShowcaseData;
}
