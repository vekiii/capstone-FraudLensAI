# Original request: Overview real-data verification

Date: 2026-11-15

Work on the existing `model-implementations` branch. Inspect the repository handoff, current dashboard, dataset configuration, SQLite RunStore, model artifacts, API endpoints, and evaluation metadata. Locate and validate an existing authorized completed dataset-mode run. If available, use existing project configuration and reconcile dashboard totals, predictions, timestamps, model identity/version, and threshold against the stored run. Show precision, recall, and F1 only when verified for the exact model version and evaluation split. Keep confirmed fraud separate from model predictions and retain unavailable states when provenance is missing.

Do not generate replacement production data, train models, fabricate results, expose private labels, change scoring/evaluation rules, add unnecessary dependencies, modify unrelated files, commit, or push. Add only missing focused edge-case tests, run relevant backend/frontend tests, lint, type checks, build, whitespace checks, and smoke-test the API/page. Create `evidence/tasks/overview-real-data-verification.md`, update `next_work.md` with one concrete next task, and finish with **Completed | Verified | Blocked | Next step**.
