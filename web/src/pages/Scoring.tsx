import { useEffect, useRef } from 'react';
import { mountEdaApp, mountModelResultsApp, mountRiskApp } from '../scoring/mount';

export function RiskTools() {
  const root = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const element = root.current;
    if (!element) return;
    const disposeRisk = mountRiskApp(element);
    const disposeResults = mountModelResultsApp(element);
    return () => {
      disposeRisk();
      disposeResults();
      element.replaceChildren();
    };
  }, []);
  return <div className="section-block scoring-section" ref={root} />;
}

export function EdaPage() {
  const root = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const element = root.current;
    if (!element) return;
    const dispose = mountEdaApp(element);
    return () => {
      dispose();
      element.replaceChildren();
    };
  }, []);
  return <div className="section-block scoring-section" ref={root} />;
}
