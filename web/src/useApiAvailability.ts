import { useEffect, useState } from "react";

export type ApiAvailability = "checking" | "unavailable" | "unwired";

export function apiAvailability(ok: boolean, contentType: string | null): ApiAvailability {
  return ok && Boolean(contentType?.includes("application/json")) ? "unwired" : "unavailable";
}

export async function probeLiveApi(fetcher: typeof fetch = fetch, signal?: AbortSignal): Promise<ApiAvailability> {
  try {
    const response = await fetcher("/api/live/v1/alerts?limit=1", { headers: { Accept: "application/json" }, signal });
    return apiAvailability(response.ok, response.headers.get("content-type"));
  } catch {
    return "unavailable";
  }
}

export function useApiAvailability(): ApiAvailability {
  const [status, setStatus] = useState<ApiAvailability>("checking");
  useEffect(() => {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 2500);
    // A reachable response is not consumed until T055 defines the approved live source.
    void probeLiveApi(fetch, controller.signal).then(setStatus).finally(() => window.clearTimeout(timeout));
    return () => { window.clearTimeout(timeout); controller.abort(); };
  }, []);
  return status;
}
