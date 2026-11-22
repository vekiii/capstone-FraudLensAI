import { useEffect, useRef } from "react";
import { mountSimulation } from "../simulation";

export function SimulationPage() {
  const container = useRef<HTMLElement>(null);

  useEffect(() => {
    if (container.current) return mountSimulation(container.current);
  }, []);

  return <section ref={container} className="simulation-page" lang="sr-Latn" />;
}
