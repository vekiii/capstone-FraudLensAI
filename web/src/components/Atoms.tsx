import type { PropsWithChildren } from "react";
import { Reveal } from "../motion/Reveal";
import { MaskReveal } from "../motion/MaskReveal";

export function Eyebrow({ children }: PropsWithChildren) { return <span className="eyebrow">{children}</span>; }
export function SectionTitle({ index, children }: PropsWithChildren<{ index: string }>) {
  return <Reveal className="section-heading" preset="fadeRTL"><Eyebrow>{index} / FIELD NOTES</Eyebrow><h2>{children}</h2></Reveal>;
}
export function SplitRule() { return <div className="split-rule" data-split-border="" aria-hidden="true" />; }
export function FramedReveal({ children }: PropsWithChildren) { return <MaskReveal className="mask-frame">{children}</MaskReveal>; }
export function NotMeasured({ children = "Not yet measured" }: PropsWithChildren) { return <span className="not-measured">{children}</span>; }
export function SourceBadge({ source = "fixture" }: { source?: "fixture" | "batch" | "live" }) {
  return <span className={`source-badge source-${source}`}>{source.toUpperCase()}</span>;
}
