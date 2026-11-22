import { lazy, Suspense, type ReactNode } from "react";
import { Route, Routes } from "react-router-dom";
import { SiteFrame } from "./components/SiteFrame";

const Overview = lazy(() => import("./pages/Overview").then(({ Overview }) => ({ default: Overview })));
const DataPage = lazy(() => import("./pages/Data").then(({ DataPage }) => ({ default: DataPage })));
const RagPage = lazy(() => import("./pages/Rag").then(({ RagPage }) => ({ default: RagPage })));
const LivePage = lazy(() => import("./pages/Live").then(({ LivePage }) => ({ default: LivePage })));
const CasesPage = lazy(() => import("./pages/Cases").then(({ CasesPage }) => ({ default: CasesPage })));
const EdaPage = lazy(() => import("./pages/Scoring").then(({ EdaPage }) => ({ default: EdaPage })));
const RiskTools = lazy(() => import("./pages/Scoring").then(({ RiskTools }) => ({ default: RiskTools })));

const SimulationPage = lazy(() => import("./pages/Simulation").then(({ SimulationPage }) => ({ default: SimulationPage })));

function loadPage(page: ReactNode) {
  return <Suspense fallback={<p className="route-loading" role="status">Loading page…</p>}>{page}</Suspense>;
}

export function AppRoutes() {
  return (
      <Routes><Route element={<SiteFrame />}>
        <Route path="/" element={loadPage(<Overview />)} />
        <Route path="/data" element={loadPage(<DataPage />)} />
        <Route path="/rag" element={loadPage(<RagPage />)} />
        <Route path="/live" element={loadPage(<LivePage />)} />
        <Route path="/cases" element={loadPage(<><CasesPage /><RiskTools /></>)} />
        <Route path="/dataset-overview" element={loadPage(<EdaPage />)} />
        <Route path="/eda" element={loadPage(<EdaPage />)} />
        <Route path="/simulation" element={loadPage(<SimulationPage />)} />
        <Route path="*" element={loadPage(<Overview />)} />
      </Route></Routes>
  );
}
