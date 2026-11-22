import { describe, expect, it } from "vitest";
import { revealOptions, revealPresets, shouldReduceMotion } from "./motion";
import { createWebGLCanvas, isLowPowerDevice } from "../webgl/capabilities";

describe("motion system", () => {
  it("exposes the three contract reveal presets", () => {
    expect(Object.keys(revealPresets)).toEqual(["fadeUp", "fadeRTL", "fadeLTR"]);
    expect(revealOptions("fadeUp", false)).toEqual({ x: 0, y: 40, opacity: 0, duration: 1 });
  });

  it("uses a short static path when reduced motion is requested", () => {
    expect(shouldReduceMotion(true)).toBe(true);
    expect(revealOptions("fadeRTL", true)).toEqual({ x: 0, y: 0, opacity: 1, duration: 0.2 });
  });

  it("selects the static fallback when WebGL initialization fails", () => {
    const canvas = document.createElement("canvas");
    expect(createWebGLCanvas(canvas, () => { throw new Error("WebGL unavailable"); })).toBeNull();
    expect(canvas.dataset.webgl).toBe("fallback");
    expect(isLowPowerDevice(2, 2)).toBe(true);
  });
});
