# Local API

Run the supported local development API with:

```powershell
uv run --locked python backend/run_local_api.py
```

It listens only on `127.0.0.1:8000`; the launcher does not accept a bind-host
override. The API has no authentication architecture, so do not publish it
through a reverse proxy, tunnel, or shared network. Directly launching
`uvicorn fraudlens.main:app` with a public `--host` bypasses this local-only
launcher and is unsupported.

## PostgreSQL integration tests

Tests that use `isolated_live_postgres` are skipped unless
`FRAUDLENS_TEST_PG_DISPOSABLE=1` is explicitly set. Use only a dedicated local
PostgreSQL 16.14 test cluster on loopback. Each test receives a unique
`fraudlens_test_<uuid>` database; cleanup verifies its generated name and
owner before dropping that exact database. The fixture never drops roles.
Migration-created `NOLOGIN` roles may remain in that test cluster. Do not set
the opt-in when pointed at a production or shared cluster.
