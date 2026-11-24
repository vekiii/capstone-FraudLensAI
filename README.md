# FraudLens AI

FraudLens AI is an educational AML prototype for reviewing suspicious synthetic transactions. An analyst can look up a LightGBM risk score, open the linked case, inspect transaction facts and account history, and run an AI investigation that cites evidence and applicable procedures. The analyst records the final decision and can reopen it with its original evidence. Simulation Lab replays synthetic scenarios and compares prioritization policies.

The score is uncalibrated. The application runs locally and does not execute account actions or file regulatory reports.

## Capstone submission

[Submitted snapshot `5b5a208`](https://github.com/vekiii/capstone-FraudLensAI/tree/5b5a208603eb6d3d8b7964d7114706168ffed1de) includes the React demo, Feature 006 evaluation, and the CAP-08 contribution update. The execution evidence below identifies the commit on which each check ran.

| Check | Executed revision | Outcome |
| --- | --- | --- |
| Manual live demo | `77ed64c` | Real model score, live investigation, factual citation and saved analyst decision reopened after reload. The procedure search returned `no_match`. [Demo record](evidence/tasks/capstone-evening-demo-guide.md) |
| Integrated live evaluation | `3cfadcc` | 16/16 scenarios, including fresh generation with `gpt-6-luna`, a supported procedure citation and reopening the same saved decision in Chrome with zero additional provider requests. EV-01 and EV-06 used the published model-bridge case from the integrated demo. [Results and settings](evidence/tasks/feature-006-integrated-recheck-2026-11-24.md) |
| Integrated regression | `3cfadcc` | 1,476 backend tests passed and one was skipped. All 300 web tests, typecheck and build passed. The backend run used `PYTHONUTF8=1` on Windows. [Evaluation record](evidence/tasks/feature-006-integrated-recheck-2026-11-24.md) |
| Controlled failure | `55444ce` | The request-budget check rejected an oversized request before provider dispatch. Reopening the failure did not dispatch a request. [CAP-06 record](evidence/security/cap06-submission-verification-2026-11-23.md) |

The submitted snapshot has the same application code, application prompts and lockfiles as the integrated evaluation candidate. The integrated 16/16 is a regression result on a known, adapted evaluation pack. The [historical comparison](evidence/tasks/feature-006-sc002-live-v2.md) retains its original inputs and named revisions. See the [CAP evidence map](evidence/tasks/feature-006-capstone-evidence-map.md) and [CAP-08 contribution](evidence/tasks/cap08-vedran-mitic.md).

## Run the local fixture demo

Use Git, uv, Python 3.14.x, Node 24.x and npm. Run the following in PowerShell from the repository root.

```powershell
uv sync --locked --group dev
npm.cmd --prefix web ci
```

In terminal 1, start the API.

```powershell
uv run --locked uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8000
```

In terminal 2, start the React application.

```powershell
npm.cmd --prefix web run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` to the local backend. The default `fixture` mode uses synthetic scenarios and can start without a provider key or model artifacts. Check the API directly and through the proxy.

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/api/health'
Invoke-RestMethod 'http://127.0.0.1:5173/api/health'
```

Use the [fixture investigation setup](evidence/tasks/feature-003-web-integration.md#run-the-local-demo) to prepare the local knowledge store and test-provider worker. Open **Cases** to inspect an investigation. Open **Simulation** to run the bundled synthetic scenario. The fixture provider returns scripted responses.

## Run the scored and live demo

Follow the [Windows demo guide](evidence/tasks/capstone-evening-demo-guide.md) for the verified artifact package, hash checks, model-case bridge, contribution sidecar, provider configuration and worker. The guide also records the earlier manual run. For the integrated live configuration, use the [evaluation settings](evidence/tasks/feature-006-integrated-recheck-2026-11-24.md), including the optional report v7 profile. Keep the key and local artifacts outside version control.

## Checks

```powershell
$env:PYTHONUTF8 = '1'
uv run --locked --python 3.14.10 --group dev --group ml --group investigation pytest backend/tests --basetemp .cache/readme-pytest
npm.cmd --prefix web test -- --run
npm.cmd --prefix web run build
git diff --check
```

Project specifications are in [specs](specs). The [Feature 006 quickstart](specs/006-capstone-evaluation/quickstart.md) describes the historical evaluation runner. See [next_work.md](next_work.md) for the contributor handoff.
