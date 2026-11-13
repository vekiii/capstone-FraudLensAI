# Feature 002 T002 — ignored artifact boundary

2026-11-13 Europe/Belgrade. Mechanical setup for FR-018; RED not applicable. [Session/revision/prompt/environment](feature-002-implementation.md). This file records only T002; later artifact/explanation tasks are not implemented.

Added `/data/artifacts/` to root `.gitignore` before creating `data/artifacts/` or writing the inspection result. Existing rules for raw, processed and large evaluation outputs retained.

```powershell
git check-ignore -v data/raw/HI-Small_Trans.csv data/processed/probe.sqlite data/artifacts/probe.json evals/results/probe.json
git ls-files -- data/raw data/processed data/artifacts evals/results
```

Both exit 0. Ignore output: `.gitignore:36:/data/raw/`, `:37:/data/processed/`, `:38:/data/artifacts/`, `:39:/evals/results/`. `ls-files` output empty: none tracked. Probe paths were not created. Actual report path `data/artifacts/feature-002-source-inspection.json` also checked with `git check-ignore -v` (exit 0, rule at line 38).

Shared `.agents/`, `.specify/`, lockfiles and original `data/fixtures/cases.json` preserved. No model binaries/explanations generated. Human review pending; no reviewer/approval invented.
