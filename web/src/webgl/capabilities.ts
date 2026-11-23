export function isLowPowerDevice(deviceMemory?: number, hardwareConcurrency?: number): boolean {
  return (deviceMemory !== undefined && deviceMemory < 4) || (hardwareConcurrency !== undefined && hardwareConcurrency < 4);
}

export function createWebGLCanvas(
  canvas: HTMLCanvasElement,
  createRenderer: (canvas: HTMLCanvasElement) => { dispose: () => void },
): (() => void) | null {
  try {
    const renderer = createRenderer(canvas);
    canvas.dataset.webgl = "ready";
    return () => renderer.dispose();
  } catch {
    canvas.dataset.webgl = "fallback";
    return null;
  }
}
