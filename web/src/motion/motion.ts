export const revealPresets = {
  fadeUp: { x: 0, y: 40, opacity: 0, duration: 1 },
  fadeRTL: { x: 100, y: 0, opacity: 0, duration: 1.4 },
  fadeLTR: { x: -100, y: 0, opacity: 0, duration: 1.4 },
} as const;

export type RevealPreset = keyof typeof revealPresets;

export function shouldReduceMotion(matches: boolean): boolean {
  return matches;
}

export function revealOptions(preset: RevealPreset, reducedMotion: boolean) {
  return reducedMotion
    ? { x: 0, y: 0, opacity: 1, duration: 0.2 }
    : revealPresets[preset];
}
