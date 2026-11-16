# Feature 005 T004 — PostgreSQL immutable facts/store

**Status:** DONE for T004. `tasks.md` keeps T002 unchecked and T003–T005 now reflect their verified task commands. Tests use only real PostgreSQL 16.14 disposable databases created and dropped by `backend/tests/integration/conftest.py`; the persistent `fraudlens_live` database was never used for tests or migrated.

## T002 PostgreSQL-only inventory

The already-running container was reused. `docker inspect` and authenticated SQL reported image `postgres:16-alpine@sha256:57c72fd2a128e416c7fcc499958864df5301e940bca0a56f58fddf30ffc07777`, matching image ID, PostgreSQL 16.14, `running/healthy`, loopback `127.0.0.1:5432`. `infra/compose/versions.env` matches. `BROKER_IMAGE`, `DEBEZIUM_IMAGE`, `DBT_IMAGE`, `MLFLOW_IMAGE`, `PROMETHEUS_IMAGE`, and `GRAFANA_IMAGE` remain `NOT_VERIFIED`. T002 remains PARTIAL and unchecked.

The six runtime-role boundaries (producer, CDC connector, worker, label curator, registry operator, read-only API reader) and retention/outage horizon are documented as **PROPOSED, pending requester confirmation** in the T002 evidence and Compose README. Numeric outage, WAL, broker, and SQL/archive horizons are unspecified. Migration-owner and runtime roles are `NOLOGIN`; actual role grants are inspected below. This does not complete T002.

## Migration and dependency

Added `backend/migrations/001_live_facts.sql` and `backend/src/fraudlens/live_store.py`. The migration creates `fraudlens.live_transactions`, `fraudlens.ingestion_receipts`, a database immutability trigger and a controlled `SECURITY DEFINER` ingest function. Amounts use unconstrained exact `NUMERIC` with checks matching the schema's nonnegative bound `< 10^13` and maximum scale 6 (13 integer digits and 6 fractional digits); this avoids typmod rounding. Times use finite `TIMESTAMPTZ`; IDs are scoped by source namespace/event ID. No label column exists. Same facts return `FALSE` without another receipt; any reused identity with different facts raises SQLSTATE 23505. Producer has function execution only; connector/worker get fact reads; other roles have no live-fact reads. Update/delete grants are absent and the trigger rejects mutation even by the owner.

Added `psycopg[binary]>=3.2,<4` using `uv add`; locked `psycopg` and `psycopg-binary` are both 3.3.9 in `uv.lock`. A PostgreSQL DB-API driver is necessary for the Python store and integration fixtures to connect to the real server, create/destroy disposable test databases, and execute SQL without mocks or subprocess/SQLite substitutes.

## Actual checks

| Command | Result |
|---|---|
| `docker inspect --format '{{.Config.Image}} {{.Image}} {{.State.Status}} {{.State.Health.Status}} {{json .NetworkSettings.Ports}}' fraudlens-live-postgres-1` | Image digest matches `versions.env`; running, healthy, `127.0.0.1:5432->5432/tcp`. |
| `docker exec fraudlens-live-postgres-1 psql -U fraudlens_admin -d fraudlens_live -v ON_ERROR_STOP=1 -Atc 'select current_setting(''server_version''), current_database();'` | `16.14|fraudlens_live`. |
| `uv run --locked pytest backend/tests/integration/test_live_transactions.py -q` | Exit 0; **10 passed in 3.45s** on disposable databases. |
| `uv run --locked pytest backend/tests/integration/test_live_transactions.py::test_catalog_enforces_keys_immutability_no_labels_and_role_boundaries -q -s` | Exit 0; **1 passed**; catalog output below. |
| `uv run --locked ruff check backend/src/fraudlens/live_store.py backend/tests/integration/conftest.py backend/tests/integration/test_live_transactions.py` | Exit 0; all checks passed. |
| Feature 002 documented regression, with `PYTHONPATH=.;backend/src`, `--basetemp=.cache/pytest-feature005-t004`, `--ignore=backend/tests/unit/test_pretrained_loader.py --ignore=backend/tests/unit/test_pretrained_ibm_inference.py --tb=short` | Exit 1; **705 passed, 5 failed, 4 errors, 1 skipped**. Four model tests require absent Feature 002 manifests/artifacts; one existing symlink test fails with Windows `WinError 1314`. No Feature 002 files were changed. |

The first full, unfiltered `uv run --locked python -m pytest backend/tests -q` also ran after T004: **709 passed, 71 failed, 4 errors, 1 skipped**; failures include the separately known pretrained suites. The locked regression run above follows Feature 002's documented non-pretrained command and uses a workspace-local pytest temp root.

### Observed SQL catalog

These rows came from the catalog assertions inside the disposable database test. No catalog output contains account data or credentials.

```text
CATALOG columns=['event_fact_digest', 'event_time', 'ingested_at', 'paid_amount', 'paid_currency', 'payment_format', 'received_amount', 'received_currency', 'receiver_account', 'receiver_bank', 'sender_account', 'sender_bank', 'source_event_id', 'source_namespace', 'transaction_id']
CATALOG constraints: live_transactions PRIMARY KEY (transaction_id); UNIQUE (source_namespace, source_event_id); bounded amount/digest/nonempty identity/currency and finite timestamp checks. ingestion_receipts PRIMARY KEY (source_namespace, source_event_id); foreign keys to both live transaction identities; digest/result/time checks.
CATALOG triggers=[('live_transactions_immutable', 'O')]
CATALOG role_privileges={'producer_execute': True, 'producer_update': False, 'producer_delete': False, 'cdc_select': True, 'worker_select': True, 'labels_select': False, 'registry_select': False, 'api_select': False}
```

No `confirmed_labels` or target column appears in `live_transactions`. Role membership is not granted to login principals. No passwords, DSNs, or `.env.local` contents are in this record.

## Post-completion test-harness hardening — 2026-11-16

The historical T004 database results above are unchanged. The current working
tree makes their fixture safer for future execution: it requires explicit
`FRAUDLENS_TEST_PG_DISPOSABLE=1`, accepts only loopback PostgreSQL, uses a unique
`fraudlens_test_<uuid>` database under an advisory lock, rejects pre-existing
name collisions, verifies exact name and owner before dropping, and no longer
drops migration-created roles. Pure guard tests cover loopback/non-loopback
hosts, generated namespace acceptance, and rejection of persistent, mismatched,
unowned, or malformed database targets.

The live transaction test module also adds boundary cases for a negative amount,
inclusive zero and maximum valid amount, SQL-injection-shaped and oversized
identifiers, blank text, transaction-ID reuse across sources, rollback of facts
and receipts, and concurrent identical retries. These new live cases are
**present but not executed**: the reconciliation run deliberately omitted the
disposable-cluster flag and reported **13 fixture-guard passes and 20 live-test
skips**. The separate loopback-launcher test also passed, producing the combined
**14 passed, 20 skipped** result. No PostgreSQL connection or mutation occurred.

Ruff passed across the modified fixture, live tests, pure safety tests, local
launcher, and HTTP security test module. This follow-up strengthens future test
safety and coverage but does not replace the need to run the 20 live cases on an
approved disposable PostgreSQL cluster.

## Security fault follow-up — 2026-11-16

Two further fault tests were added. A loopback outage test selects an ephemeral
closed port, uses a synthetic username/password and one-second connection
timeout, and passed within the three-second bound. A live lock-contention test
holds an access-exclusive lock, applies a 100 ms `lock_timeout`, expects
`LockNotAvailable`, and then checks that neither facts nor receipts were partly
persisted. The lock test is **SKIPPED / NOT TESTABLE** because Docker Desktop and
the approved disposable PostgreSQL service were unavailable.

The first failed fixture connection exposed the ignored local PostgreSQL
credential in pytest's rendering of expanded `psycopg` keyword arguments. The
fixture now uses a credential-redacting connection helper, and all live
integration callers use that boundary. A repeat failure showed only host, port,
database and `ConnectionTimeout`; the credential did not recur. The disclosed
local credential still requires rotation before reuse. These outcomes and exact
commands are recorded in the security audit; they do not alter T004's historical
completion status or represent the skipped lock test as a pass.
