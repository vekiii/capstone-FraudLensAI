# Capstone MVP integration

2026-11-22, Europe/Belgrade. [Original request](../../prompts/development/capstone-mvp-integration.md)
and [draft PR #3](https://github.com/vekiii/capstone-FraudLensAI/pull/3).
The runtime and test inputs below are in 361ff55. The worktree started from
origin/main at 0fbe313.

| Source | Integration commit | Result |
| --- | --- | --- |
| origin/feature/002-clean-start at a844b72 | 88cb454 | Preserved the selected model and contracts. Resolved eight specification conflicts in favor of clean-start and combined the handoff histories. |
| origin/feature/005-real-time-fraud-detection-mlops-spec at 1401889 | 1737ef9 | Ported the React web application. Cases includes risk and aggregate results. The previous dataset overview URL serves the same approved EDA view as /eda. |
| origin/integration/003-investigation-web at 71f34dd and origin/feature03 at 62f0991 | 35a7df7, 361ff55 | Ported fixture investigation, runtime, tests, specs and evidence. Kept the producer contract snapshot and offline eval inputs separate from application prompts. |
| origin/integration/004-simulation-web at 8d964bf and origin/004-simulation-and-prioritization at 45a375f | eab1d2a | Ported Simulation Lab and its bundled scenario and acceptance material. |

## Observed verification

- Node 24.20.0, npm 11.19.0. From the repository root, npm.cmd --prefix web ci
  installed the locked dependencies. npm.cmd --prefix web run test -- --run
  passed 285 tests. npm.cmd --prefix web run build passed TypeScript and Vite.
  Vite reports the existing chunk-size warning for Three.js.
- uv 0.10.9 regenerated the Python lock for the optional pinned investigation
  group. uv 0.13.9 installed Python 3.14.10 into isolated workspace storage
  and synced the locked dev, ml and investigation groups. The managed runtime
  also reported Windows access denied for global executable links and registry
  registration. Those are unnecessary for the isolated environment.
- With PYTHONPATH set to backend/src, Python 3.14.10 ran pytest -q backend/tests
  -rs --tb=short with unique workspace-local basetemp and cache directories.
  Result was 1,373 passed and two skipped. Skips were the positive frozen
  aggregate test requiring project artifacts and a Windows symlink test.
  Six LightGBM deprecation warnings came from synthetic tests.
- Headless Chrome used an isolated profile and local Vite and FastAPI ports
  5191 and 8021. It opened CASE-001, initiated a fixture investigation, ran
  the one-shot test worker, reached ready_for_review, opened saved evidence,
  saved the test analyst decision and restored it after reloading Cases.
  Simulation rendered comparison rows for all three strategies. EDA displayed
  the unavailable state and the proxied HTTP checks returned risk 503,
  EDA 404 and simulation catalog 200. No live provider calls.
- Ruff, lock verification and Git diff checks passed.

The initial backend runs found missing investigation offline inputs, test
configuration leaking across tests and a Python patch mismatch. The final suite
used the upstream fixtures and prompts, restored autouse environment isolation,
and ran on the pinned Python. Byte-verified Feature 002 approval and completion
documents retain their exact published hashes with LF on Windows.

## Remaining verification

The frozen LightGBM model, authorized report and full-source EDA summary were
absent. The live model parity test, model-backed AI investigation adapter and
T252 human review remain open. The model owner can repeat T233 on the candidate
without retraining. Feature 006 and the remaining Feature 005 backend are outside
this draft.
