import { useEffect, useRef, useState } from "react";

export function InvestigationPanel({ caseId, dataset = false }: { caseId: string; dataset?: boolean }) {
  const [open, setOpen] = useState(false);
  const [loadFailed, setLoadFailed] = useState(false);
  const panel = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const root = panel.current;
    if (!open || !root) return;
    let active = true;
    let dispose: (() => void) | undefined;
    void Promise.all([import("../investigation/controller"), import("../investigation/api")]).then(([{ mountReports }, { reportClient, createDatasetInvestigation }]) => {
      if (active) dispose = mountReports(root, caseId,
        dataset ? { ...reportClient, create: createDatasetInvestigation } : reportClient,
        { sourceMode: dataset ? 'dataset' : 'fixture' });
    }).catch(() => {
      if (active) setLoadFailed(true);
    });
    return () => {
      active = false;
      dispose?.();
    };
  }, [caseId, dataset, open]);

  return <section className="investigation-panel" aria-label="AI istraga" lang="sr-Latn">
    {!open && <button className="button" type="button" onClick={() => setOpen(true)}>
      Prikaži AI istragu
    </button>}
    {loadFailed && <p role="alert">Panel istrage nije mogao da se učita. Osvežite stranicu i pokušajte ponovo.</p>}
    {open && <div ref={panel} />}
  </section>;
}
