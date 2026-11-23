import { readFile } from "node:fs/promises";
import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { LivePage } from "./pages/Live";
import { SiteDataContext, loadShowcaseData } from "./site-data";

describe("showcase security boundary", () => {
  it("declares a restrictive CSP on the sole browser entry point", async () => {
    const showcase = await readFile("index.html", "utf8");

    for (const html of [showcase]) {
      expect(html).toContain('http-equiv="Content-Security-Policy"');
      expect(html).toContain("default-src 'self'");
      expect(html).toContain("object-src 'none'");
      expect(html).toContain("base-uri 'none'");
      expect(html).toContain("form-action 'none'");
      expect(html).not.toContain("'unsafe-inline'");
      expect(html).not.toContain("'unsafe-eval'");
    }
  });

  it("escapes malicious Unicode sample content instead of creating DOM markup", async () => {
    const payload = `<img src=x onerror="alert('Ω')">`;
    const data = await loadShowcaseData(async (path) => {
      const name = String(path).split("/").pop();
      const body = await readFile(`public/data/${name}`, "utf8");
      const parsed = JSON.parse(body);
      if (name === "samples.json") {
        parsed.samples[0].title = payload;
        parsed.samples[0].status = "\u0000duplicate synthetic state";
      }
      return new Response(JSON.stringify(parsed), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    });

    const html = renderToStaticMarkup(
      <SiteDataContext.Provider value={data}>
        <MemoryRouter><LivePage /></MemoryRouter>
      </SiteDataContext.Provider>,
    );

    expect(html).not.toContain(payload);
    expect(html).not.toContain("<img src=x");
    expect(html).toContain("&lt;img");
    expect(html).toContain("Ω");
  });
});
