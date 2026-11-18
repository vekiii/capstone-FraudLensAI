# Feature 002 Quickstart (Planned)

This specifies the eventual Windows PowerShell workflow. Only commands marked **existing** are implemented in Feature 001. Other commands below are proposals that tasks must create and verify. This file contains no successful data/model execution claim.

## Existing Feature 001 setup and checks

From repository root, these commands exist; fixture mode requires no dataset or model:

```powershell
uv sync --locked --group dev
npm.cmd --prefix frontend ci
uv run --locked uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8000
npm.cmd --prefix frontend run dev -- --host 127.0.0.1 --port 5173 --strictPort
uv run --locked pytest backend/tests
uv run --locked ruff check backend
npm.cmd --prefix frontend run test -- --run
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend run build
```

Python dependencies use root `uv.lock`; frontend dependencies use `frontend/package-lock.json`. Initial install may require network access; runtime fixture mode does not.

## Proposed Feature 002 commands (not implemented)

1. Acquire `HI-Small_Trans.csv` only after reviewing current source terms. Place it at ignored `data/raw/HI-Small_Trans.csv`; never commit it.
2. Verify bytes/provenance and source schema:

   ```powershell
   uv run --locked python -m fraudlens.data verify-source --input data/raw/HI-Small_Trans.csv
   ```

3. Prepare and validate local canonical data:

   ```powershell
   uv run --locked python -m fraudlens.data prepare --input data/raw/HI-Small_Trans.csv --output data/processed/hi-small-v1
   ```

4. Build features and chronology-only partition boundaries:

   ```powershell
   uv run --locked python -m fraudlens.data build-features --snapshot data/processed/hi-small-v1
   uv run --locked python -m fraudlens.data audit-splits --snapshot data/processed/hi-small-v1 --protocol specs/002-data-and-risk-scoring/protocol.json
   ```

5. After human review of source, resource ceilings, feature contract, ID hashes and permitted aggregate audit, freeze the protocol:

   ```powershell
   uv run --locked python -m fraudlens.data freeze-protocol --protocol specs/002-data-and-risk-scoring/protocol.json
   ```

6. Run only training/validation experiments:

   ```powershell
   uv run --locked python -m fraudlens.training run --protocol specs/002-data-and-risk-scoring/protocol.json
   ```

   The command must fail closed on mismatched hashes or incomplete protocol and must not read test/showcase record labels.

7. Model loading is a deliberate local setting. Without a compatible artifact, start the existing backend/frontend using the Feature 001 commands above; fixture mode remains available. The planned prediction view and EDA route require implementation, with EDA UI conditional on team approval.
8. Add Feature 002 checks to the existing locked pytest/Ruff/Vitest/typecheck/build commands. Record actual command, versions, exit status, outputs and limitations in `evidence/`; do not copy sample outputs as execution evidence.
9. Test evaluation is separate and requires a separate explicit authorization after frozen predictions. It is never part of the training quickstart.

Synthetic fixtures do not establish source validity or model quality. Keep raw/processed data, model artifacts, credentials, logs that expose restricted audits, and generated evaluations out of Git.
