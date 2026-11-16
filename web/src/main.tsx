import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { SiteFrame } from "./components/SiteFrame";
import { Overview } from "./pages/Overview";
import { DataPage } from "./pages/Data";
import { RagPage } from "./pages/Rag";
import { LivePage } from "./pages/Live";
import "./styles/tokens.css";
import "./styles/site.css";

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes><Route element={<SiteFrame />}>
        <Route path="/" element={<Overview />} />
        <Route path="/data" element={<DataPage />} />
        <Route path="/rag" element={<RagPage />} />
        <Route path="/live" element={<LivePage />} />
        <Route path="*" element={<Overview />} />
      </Route></Routes>
    </BrowserRouter>
  </React.StrictMode>,
);
