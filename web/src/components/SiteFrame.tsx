import { Outlet, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { Reveal } from "../motion/Reveal";
import { useSiteMotion } from "../motion/useSiteMotion";
import { Backdrop } from "../webgl/Backdrop";
import { FramedReveal } from "./Atoms";
import { TransitionLink } from "./TransitionLink";
import { SiteDataContext, loadShowcaseData, type ShowcaseData } from "../site-data";

const links = [
  ["/", "Overview"],
  ["/data", "Data & model"],
  ["/rag", "RAG"],
  ["/live", "Live demo"],
] as const;

export function SiteFrame() {
  const { pathname } = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const [siteData, setSiteData] = useState<ShowcaseData | null>(null);
  useSiteMotion(pathname);
  useEffect(() => { window.scrollTo({ top: 0, behavior: "auto" }); setMenuOpen(false); }, [pathname]);
  useEffect(() => { let active = true; void loadShowcaseData().then((data) => { if (active) setSiteData(data); }).catch(() => { if (active) setSiteData(null); }); return () => { active = false; }; }, []);
  return <>
    <Backdrop />
    <SiteDataContext.Provider value={siteData}>
    <div className="site-shell">
      <header className="site-header">
        <TransitionLink className="wordmark" to="/" exact><span className="mark" aria-hidden="true">◈</span> FraudLens</TransitionLink>
        <button className="menu-toggle" type="button" aria-expanded={menuOpen} aria-controls="site-nav" onClick={() => setMenuOpen((open) => !open)}>{menuOpen ? "CLOSE −" : "MENU +"}</button>
        <nav id="site-nav" className={menuOpen ? "open" : ""} aria-label="Main navigation">{links.map(([to, text]) => <TransitionLink key={to} to={to} exact={to === "/"}>{text}</TransitionLink>)}</nav>
      </header>
      <main id="main-content" key={pathname} className="route-view" aria-live="polite"><Outlet /></main>
      <footer className="site-footer">
        <FramedReveal><Reveal className="footer-inner" preset="fadeUp">
          <div><span className="eyebrow">SYNTHETIC DATA · HUMAN REVIEW</span><p className="footer-wordmark">FraudLens</p></div>
          <div className="footer-links">{links.map(([to, text]) => <TransitionLink key={to} to={to} exact={to === "/"}>{text}</TransitionLink>)}</div>
          <a className="back-top" href="#main-content">Back to top ↑</a>
        </Reveal></FramedReveal>
      </footer>
    </div>
    </SiteDataContext.Provider>
  </>;
}
