# Original development request — Dataset & Model Overview

Date: 2026-11-15
Requested branch: `model-implementations`

## Task: Implement FraudLens AI — Dataset & Model Overview Dashboard

Act as a **Senior Full-Stack Engineer, Data Architect, and MLOps Lead**.

Work directly on the existing `model-implementations` branch of `capstone-FraudLensAI`.

**Goal:** Implement a functional, responsive Dataset & Model Overview page using real project data. Complete implementation, testing, and verification autonomously.

### 1. Inspect before implementing

Read `AGENTS.md`, `README.md`, `next_work.md`, and relevant frontend/backend code.

Identify:

- Existing frontend framework, routing, components, and styling.
- Available datasets, database tables, and API endpoints.
- Active model, model metadata, evaluation artifacts, and verified metrics.

Reuse existing architecture. Do not introduce a new frontend framework or unnecessary dependencies.

### 2. Dashboard requirements

Add an accessible **Overview** page to the existing application navigation.

**Dataset statistics**

- Total transactions
- Confirmed fraudulent transactions
- Legitimate transactions
- Fraud rate (%)

**Visualizations**

- Transaction volume over time (line/area chart).
- Fraudulent vs. legitimate transactions over time.
- Fraud distribution (small donut or horizontal bar).

Use daily or weekly aggregation based on dataset size.

**Model information**

- Active model name and version
- Precision (fraud class)
- Recall and F1-score, when available
- Evaluation dataset/split and decision threshold

Clearly distinguish confirmed labels from model predictions. Display the metric source and never present training metrics as test performance.

**Data integrity requirements**

- Use real backend data or existing verified artifacts.
- Never hardcode fabricated metrics.
- Prefer existing endpoints; add one small read-only aggregate endpoint only if necessary.
- Aggregate on the backend; never send the entire dataset to the browser.
- Handle empty datasets, unknown labels, missing timestamps, unavailable model metrics, and API failures.
- Show `N/A` with a clear explanation when reliable information is unavailable.
- Do not calculate or expose private holdout metrics.

### 3. UI design

Create a **minimalist premium financial analytics dashboard**.

Strict palette:

- Midnight Ink: `#080F1B` — primary background
- Azure Blue: `#329DD2` — primary highlights, charts, links
- Vermilion Orange: `#FF4C2B` — fraud indicators, warnings

Use restrained neutral text/borders. Aim for:

- Clean typography, generous whitespace, subtle borders
- Four prominent KPI cards
- One large time-series chart
- Compact fraud-distribution and model-performance panels
- Responsive desktop/mobile layouts
- Proper loading, empty, and error states

Avoid decorative clutter, heavy gradients, excessive animation, and unnecessary UI libraries.

### 4. Implementation constraints

- Keep changes limited to this dashboard and its required data integration.
- Do not retrain models or change inference, thresholds, evaluation protocols, or dataset mappings.
- Do not modify unrelated functionality or overwrite user changes.
- Reuse existing project conventions and test utilities.
- Never expose raw transaction records or sensitive labels through new APIs.
- Do not commit or push.

### 5. Execute and verify

Do not stop after writing code.

1. Run existing relevant tests before changes.
2. Implement frontend and minimal backend integration.
3. Add focused tests for aggregate calculations, fraud percentages, timestamp boundaries, zero records, missing metrics, and API errors.
4. Run backend tests, frontend tests, linting, type checks, and production build using the repository's actual commands.
5. Start the application and smoke-test the Overview route and API responses.
6. Fix any failures introduced by your changes and rerun affected checks.
7. Run `git diff --check` and review the final diff.

Use synthetic fixtures for tests. Never invent production values.

### 6. Mandatory evidence

Create `evidence/tasks/dataset-model-overview.md` containing:

- Implemented features and changed files
- Actual data sources and formulas used
- Model identity, metric provenance, and unavailable fields
- Tests added, commands executed, exit codes, pass/fail counts
- Screenshot or visual verification evidence, if browser tooling is available
- Issues discovered and fixes made
- Remaining limitations and any checks that could not run

Update `next_work.md` with completion status and evidence path.

### Definition of done

The page must load through existing navigation, show trustworthy dataset/model information, render charts without crashing, handle missing data gracefully, work on mobile, and pass applicable checks.

**Execute the entire task without requesting confirmation for routine implementation decisions. Do not claim completion without verification.**

Finish with a concise report: **Implemented | Tested | Evidence | Remaining issues**.
