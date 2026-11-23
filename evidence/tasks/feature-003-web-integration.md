# Feature 03 React integration

- Date: 2026-11-19.
- Local branch: `integration/003-investigation-web` from Feature 05 at `1401889`.
- Feature 03 source: `62f0991`.
- [Original request](../../prompts/development/003-investigation-web-integration.md).

In React Cases, open `CASE-001` and select **Prikaži AI istragu**. The panel reuses
the verified Feature 03 controller and closed API contracts. Case changes and
navigation dispose the old controller. The developer proxy preserves the
browser Host so the backend can enforce the same-origin mutation guard.

## Run the local demo

In each backend or worker PowerShell session, from the repository root:

```powershell
$env:PYTHONPATH = 'backend/src'
$env:APP_MODE = 'fixture'
$env:INVESTIGATION_ENABLED = 'true'
$env:INVESTIGATION_PROVIDER = 'test'
$env:INVESTIGATION_SOURCE = 'fixture'
$env:INVESTIGATION_SEMANTIC_RETRIEVAL = 'false'
$env:INVESTIGATION_STORE = 'data/processed/investigation-web-demo.sqlite'
```

Set `INVESTIGATION_ANALYST` to the local demo operator name in the backend
session. Prepare knowledge and start FastAPI:

```powershell
.venv/Scripts/python.exe -m fraudlens.investigation.cli prepare-knowledge --manifest data/knowledge/fraudlens-aml-knowledge-v1/manifest.json --store $env:INVESTIGATION_STORE
.venv/Scripts/python.exe -m uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8000
```

Run `npm.cmd --prefix web run dev` in another session with `VITE_APP_MODE=fixture`.
After opening a new investigation in Cases, claim it from the worker session:

```powershell
.venv/Scripts/python.exe -m fraudlens.investigation.cli worker --store $env:INVESTIGATION_STORE --once
```

## Observed checks

- React tests: 205 passed. Typecheck and production build passed. Vite still warns about the existing Three.js chunk size.
- Targeted backend tests: 79 passed across the investigation, knowledge, review, recovery, fixture Cases and dataset API routes. Ruff passed.
- Full backend suite: 763 passed, 24 skipped, 72 failed and 4 errors. Full acceptance of the shared base remains pending. The suite includes unfinished Feature 05 behavior and local model artifact prerequisites.
- Headless Chrome exercised React, the Vite proxy, FastAPI and the one-shot worker on isolated ports 5184 and 8013. The synthetic `CASE-001` attempt reached `ready_for_review`, its saved procedure citation opened, and the local test decision was restored after reload. Switching to `CASE-002` displayed a fresh panel.
- Before the proxy fix a same-origin POST returned 403 because the forwarding changed Host. With Host preservation the browser workflow passed, and a POST from a mismatched origin still returned 403.

The test provider generated an authored diagnostic report. The React panel is enabled
for fixture case details. Dataset integration and live provider verification remain
outside this demo. No OpenAI requests were made.
