import { useEffect, useRef, type PropsWithChildren } from "react";
import { revealOptions, type RevealPreset } from "./motion";

type Props = PropsWithChildren<{
  preset?: RevealPreset;
  className?: string;
  delay?: number;
  stagger?: number;
}>;

export function Reveal({ children, preset = "fadeUp", className = "", delay = 0, stagger = 0.075 }: Props) {
  const root = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const element = root.current;
    if (!element) return;
    let active = true;
    let cleanup: (() => void) | undefined;
    void Promise.all([import("gsap"), import("gsap/ScrollTrigger")]).then(([gsapModule, scrollTriggerModule]) => {
      if (!active) return;
      const { gsap } = gsapModule;
      const { ScrollTrigger } = scrollTriggerModule;
      gsap.registerPlugin(ScrollTrigger);
      const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      const targets = element.querySelectorAll<HTMLElement>("[data-reveal-item]");
      const animatedTargets: HTMLElement[] = targets.length ? Array.from(targets) : [element];
      const animation = gsap.fromTo(animatedTargets, revealOptions(preset, reduced), {
        x: 0,
        y: 0,
        opacity: 1,
        duration: reduced ? 0.2 : revealOptions(preset, reduced).duration,
        delay,
        stagger: reduced ? 0 : stagger,
        ease: "power2.out",
        scrollTrigger: reduced ? undefined : { trigger: element, start: "top 85%", once: true },
      });
      cleanup = () => {
        ScrollTrigger.getAll().filter((trigger) => trigger.trigger === element).forEach((trigger) => trigger.kill());
        animation.kill();
      };
    }).catch(() => {
      // Content stays visible if the optional animation chunks are unavailable.
    });
    return () => { active = false; cleanup?.(); };
  }, [delay, preset, stagger]);
  return <div ref={root} className={className} data-reveal={preset}>{children}</div>;
}
