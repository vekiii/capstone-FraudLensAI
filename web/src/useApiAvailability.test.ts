import { describe, expect, it } from "vitest";
import { apiAvailability, probeLiveApi } from "./useApiAvailability";

describe("live API boundary", () => {
  it("does not treat an absent API or Vite HTML fallback as live data", () => {
    expect(apiAvailability(false, null)).toBe("unavailable");
    expect(apiAvailability(true, "text/html")).toBe("unavailable");
  });
  it("recognizes JSON transport without consuming it before T055", () => {
    expect(apiAvailability(true, "application/json; charset=utf-8")).toBe("unwired");
  });
  it("falls back cleanly when the local API is down", async () => {
    const down = async () => { throw new Error("connection refused"); };
    await expect(probeLiveApi(down as typeof fetch)).resolves.toBe("unavailable");
  });
});
