import { flushSync } from "react-dom";
import { useLocation, useNavigate } from "react-router-dom";
import type { MouseEvent, PropsWithChildren } from "react";

type Props = PropsWithChildren<{ to: string; className?: string; exact?: boolean }>;

export function TransitionLink({ to, className = "", exact = false, children }: Props) {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const active = exact ? pathname === to : pathname === to || pathname.startsWith(`${to}/`);
  const click = (event: MouseEvent<HTMLAnchorElement>) => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    const doc = document as Document & { startViewTransition?: (update: () => void) => unknown };
    const update = () => flushSync(() => navigate(to, { flushSync: true }));
    if (doc.startViewTransition && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) doc.startViewTransition(update);
    else update();
  };
  return <a href={to} className={`${className}${active ? " active" : ""}`} aria-current={active ? "page" : undefined} onClick={click}>{children}</a>;
}
