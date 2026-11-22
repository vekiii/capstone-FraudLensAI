import { useEffect, useRef, useState } from "react";

export function InvestigationPanel({ caseId }: { caseId: string }) {
  const [open, setOpen] = useState(false);
  const [loadFailed, setLoadFailed] = useState(false);
  const panel = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const root = panel.current;
    if (!open || !root) return;
    let active = true;
    let dispose: (() => void) | undefined;
    void import("../investigation/controller").then(({ mountReports }) => {
      if (active) dispose = mountReports(root, caseId);
    }).catch(() => {
      if (active) setLoadFailed(true);
    });
    return () => {
      active = false;
      dispose?.();
    };
  }, [caseId, open]);

  return <section className="investigation-panel" aria-label="AI istraga" lang="sr-Latn">
    {!open && <button className="button" type="button" onClick={() => setOpen(true)}>
      Prikaži AI istragu
    </button>}
    {loadFailed && <p role="alert">Panel istrage nije mogao da se učita. Osvežite stranicu i pokušajte ponovo.</p>}
    {open && <div ref={panel} />}
  </section>;
}
