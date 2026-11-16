import { useEffect, useRef, type PropsWithChildren } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

type Props = PropsWithChildren<{ className?: string }>;

export function MaskReveal({ children, className = "" }: Props) {
  const node = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const element = node.current;
    if (!element) return;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const animation = gsap.fromTo(element, { clipPath: reduced ? "inset(0 0 0 0)" : "inset(0 0 100% 0)" }, {
      clipPath: "inset(0 0 0 0)",
      duration: reduced ? 0.2 : 1.2,
      ease: "power2.inOut",
      scrollTrigger: reduced ? undefined : { trigger: element, start: "top 85%", once: true },
    });
    return () => {
      ScrollTrigger.getAll().filter((trigger) => trigger.trigger === element).forEach((trigger) => trigger.kill());
      animation.kill();
    };
  }, []);
  return <div ref={node} className={className} data-mask-reveal="">{children}</div>;
}

gsap.registerPlugin(ScrollTrigger);
