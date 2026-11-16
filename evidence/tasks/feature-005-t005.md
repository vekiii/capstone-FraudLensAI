# Feature 005 T005 — deterministic synthetic producer

**Status:** DONE for T005. Feature 002 regression remains a separate FAIL/BLOCKED baseline issue described below. The producer tests use disposable databases on the real PostgreSQL 16.14 service and never use the persistent `fraudlens_live` database.

## Implementation

Added `backend/src/fraudlens/live_producer.py` and `backend/tests/integration/test_live_producer.py`. The timeline has stable transaction/source IDs, BANK-ALPHA and BANK-BETA, EUR and USD, UTC timestamps with an equal-time pair, and exact `Decimal` values. The canonical digest hashes deterministic JSON with decimal strings and UTC ISO time. Store insertion returns the inserted count; repeat insertion is a no-op; changed facts for the same source identity raise `FactConflict` and leave the original row unchanged.

## Commands and observed results

| Command | Result |
|---|---|
| `uv run --locked ruff check backend/src/fraudlens/live_store.py backend/src/fraudlens/live_producer.py backend/tests/integration/conftest.py backend/tests/integration/test_live_transactions.py backend/tests/integration/test_live_producer.py` | Exit 0; all checks passed. Ruff's initial import-order finding was corrected. |
| `uv run --locked pytest backend/tests/integration/test_live_producer.py -q` | Initial run: 2 passed, 1 failed because the test caught the expected conflict inside, rather than outside, the psycopg savepoint context. Corrected only exception scope; the conflict expectation/schema were unchanged. Rerun exit 0; **3 passed in 0.69s**. |
| `uv run --locked pytest backend/tests/integration/test_live_transactions.py backend/tests/integration/test_live_producer.py -q` | Exit 0; **13 passed in 4.13s** against disposable PostgreSQL databases. |
| Feature 002 documented regression with `PYTHONPATH=.;backend/src`, `--basetemp=.cache/pytest-feature005-t005`, pretrained-loader/inference exclusions, `--tb=short` | Exit 1; **708 passed, 5 failed, 4 errors, 1 skipped**. Four errors and four boosted-integration failures require absent Feature 002 model manifests/artifacts; the fifth failure is the existing Windows symlink privilege failure (`WinError 1314`). No Feature 002 code was changed. |

All commands avoided printing Compose configuration, `.env.local`, passwords and DSNs. The previous/current password grep is recorded in the final handoff after it runs.