# Remotion product demo request — 2026-11-23

Original user request:

> Use the remotion-create and remotion-markup skills. Build a 1920x1080, 30fps, 45s product demo for a fraud detection app, driven by `src/data/transactions.json`. Scenes: (1) title, (2) transaction card slides in, (3) flows into an ML model node, risk score counts up against a threshold line, (4) flagged transaction goes to a RAG node, retrieved chunks with source citations appear, (5) explanation text types out, (6) recap with metrics. Dark UI, one accent color (red for fraud, green for legit). Add captions with remotion-captions. Start the studio so I can preview.

Scope decision: make an educational video in the existing `fraud-demo/` Remotion scaffold. Illustrate the model and retrieval stages without claiming live execution or model evaluation. Do not alter the application frontend, backend, or data contracts.
