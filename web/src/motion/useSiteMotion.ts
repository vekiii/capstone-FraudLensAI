import { useEffect } from "react";

export function useSiteMotion(pathname: string) {
  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      window.scrollTo({ top: 0, behavior: "auto" });
      return;
    }

    let active = true;
    let cleanup: (() => void) | undefined;
    void Promise.all([import("lenis"), import("gsap"), import("gsap/ScrollTrigger")])
      .then(([lenisModule, gsapModule, scrollTriggerModule]) => {
        if (!active) return;
        const Lenis = lenisModule.default;
        const { gsap } = gsapModule;
        const { ScrollTrigger } = scrollTriggerModule;
        gsap.registerPlugin(ScrollTrigger);

        const lenis = new Lenis({ autoRaf: false });
        const onScroll = () => ScrollTrigger.update();
        lenis.on("scroll", onScroll);
        const tick = (time: number) => lenis.raf(time * 1000);
        gsap.ticker.add(tick);
        gsap.ticker.lagSmoothing(0);
        const anchorClick = (event: MouseEvent) => {
          const anchor = (event.target as HTMLElement).closest<HTMLAnchorElement>('a[href^="#"]');
          if (!anchor) return;
          const target = document.querySelector(anchor.hash);
          if (!target) return;
          event.preventDefault();
          lenis.scrollTo(target, { duration: 3, easing: (t) => 1 - (1 - t) ** 4 });
        };
        document.addEventListener("click", anchorClick);
        const context = gsap.context(() => {
          const splitRules = gsap.utils.toArray<HTMLElement>("[data-split-border]");
          splitRules.forEach((rule) => gsap.fromTo(rule, { scaleX: 0 }, {
            scaleX: 1,
            duration: 0.8,
            ease: "power2.inOut",
            scrollTrigger: { trigger: rule, start: "top 88%", once: true },
          }));
          const storyHeadings = gsap.utils.toArray<HTMLElement>(".story-beat h2");
          storyHeadings.forEach((heading) => gsap.fromTo(heading, { x: -50, opacity: 0 }, {
            x: 0,
            opacity: 1,
            duration: 0.7,
            scrollTrigger: { trigger: heading.parentElement, start: "top center", end: "center center", scrub: true },
          }));
          const hero = document.querySelector<HTMLElement>(".hero");
          const heroSpacer = document.querySelector<HTMLElement>(".hero-spacer");
          if (hero && heroSpacer) {
            gsap.to(hero, {
              y: -60,
              opacity: 0,
              ease: "none",
              scrollTrigger: { trigger: heroSpacer, start: "top top", end: "bottom top", scrub: true },
            });
          }
        });
        ScrollTrigger.refresh();
        lenis.scrollTo(0, { immediate: true });
        cleanup = () => {
          lenis.off("scroll", onScroll);
          document.removeEventListener("click", anchorClick);
          context.revert();
          gsap.ticker.remove(tick);
          lenis.destroy();
        };
      })
      .catch(() => {
        // Native scrolling remains available if optional animation chunks fail to load.
      });

    return () => {
      active = false;
      cleanup?.();
    };
  }, [pathname]);
}
