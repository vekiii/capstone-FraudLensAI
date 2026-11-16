# Feature 005 T002 â€” local versions, roles and retention inventory

**Status: PARTIAL / BLOCKED for version verification. Date:** 2026-11-16.
**Feature directory:** `specs/005-real-time-fraud-detection-mlops`
**Scope:** T002 only. No secrets or credentials recorded.

## Decision provenance and limitation

The current requester decision explicitly accepts T003 while T002 remains PARTIAL for non-PostgreSQL services. For this task, the proposed database roles and retention/outage horizon below remain PROPOSED and require owner confirmation. PostgreSQL image/version/service health are independently verified; role grants and other service pins are not.

## Commands and observed results

Read-only commands were run in PowerShell. Docker checks were retried with elevated execution after the initial sandbox call could not read the user's Docker config/engine pipe.

| Command | Observed result |
|---|---|
| `docker version` | Exit 1. Client version `28.3.2`, API `1.51`, context `desktop-linux`; server query failed because `//./pipe/dockerDesktopLinuxEngine` does not exist. |
| `docker image ls --digests --no-trunc` | Exit 1. Could not connect to the same missing Docker Desktop engine pipe; no image list or digests available. |
| `docker compose version` | Exit 0. `Docker Compose version v2.39.1-desktop.1`. |
| `Get-Service -Name com.docker.service` | `com.docker.service` is `Stopped`, start type `Manual`. |
| PostgreSQL tool discovery (`Get-Command psql, pg_isready, initdb, pg_ctl`) | All four commands unavailable. |
| Loopback availability probe `127.0.0.1:5432` | `NOT LISTENING` after a 1.5-second connection attempt. No database credentials were tried. |
| `git status --short --ignored infra/compose` | Reported only untracked `infra/compose/`; no ignored secret files were listed. No secret values were created. |
| `docker compose -f infra/compose/compose.yaml config` | Not run: the Compose file is a later T006 deliverable and does not exist. |

**Conclusion:** Docker CLI/Compose client versions are observed, but Docker engine and image digests are NOT VERIFIED. No isolated PostgreSQL server is available in this environment. The required real-database gate blocks T003; no SQLite or mock substitute was used.

## Inventory recorded

- `infra/compose/versions.env` records client versions and `NOT_VERIFIED` for PostgreSQL, broker, Debezium, dbt, MLflow, Prometheus and Grafana images. It is explicitly an inventory, not a Compose source file.
- `infra/compose/README.md` records proposed service roles and retention rules.
- `backend/migrations/README.md` records proposed role boundaries and migration/retention policy.
- Proposed database principals (pending owner confirmation): `migration_owner`, `live_producer`, `cdc_connector`, `live_worker`, `label_curator`, `registry_operator`, and `live_api_reader`. No roles or grants were created.
- Proposed retention/outage horizon (pending owner confirmation): WAL and broker events exceed the approved outage/replay horizon; canonical facts remain available for that horizon or have a reconstructible archive; any exceeded horizon is exposed as a gap. Numeric durations, caps and the approved outage target remain unset in the specification and are not invented here.

## T002 verification and disposition

The Verify command cannot pass: image digests and compatibility are not inspectable without the Docker engine, and numeric retention bounds remain unspecified. The approved policy approach is documented, but technical version/compatibility checks remain NOT VERIFIED. T002 remains PARTIAL. `tasks.md` remains unchecked. No PostgreSQL, Compose services or secrets were created. T003 and later tasks were not started because no real isolated PostgreSQL is available, as required by the user's instruction.

## Follow-up â€” PostgreSQL Docker verification (2026-11-16)

The requester reported Docker was running. Read-only inspection confirmed Docker Engine 28.3.2, Compose v2.39.1, five pre-existing stopped containers, existing images/volumes/networks, and no listener on 127.0.0.1:5432 or :5433. No existing container, volume, image or network was stopped, removed or modified.

Commands and observed results:

| Command | Result |
|---|---|
| `docker info` (elevated) | Exit 0; Engine 28.3.2, Docker Desktop Linux, 5 stopped containers, 10 images. |
| `docker ps -a --no-trunc` | Listed only the five pre-existing stopped containers before setup. |
| `docker image ls --digests --no-trunc` | PostgreSQL candidate existed locally as `postgres:16-alpine`, digest `sha256:57c72fd2a128e416c7fcc499958864df5301e940bca0a56f58fddf30ffc07777`. |
| `docker image inspect postgres:16-alpine` | `PG_VERSION=16.14`, linux/amd64, RepoDigest `postgres@sha256:57c72fd2a128e416c7fcc499958864df5301e940bca0a56f58fddf30ffc07777`. No pull or image mutation. |
| Port probe for 5432 and 5433 | No listening socket found; Compose used 5432 as requested. |
| `docker compose --env-file infra/compose/.env.local -p fraudlens-live -f infra/compose/compose.yaml config --quiet` | Exit 0. Configuration is scoped to project `fraudlens-live`, host bind `127.0.0.1:5432`, new volume `fraudlens-live-pgdata`. |
| `docker compose --env-file infra/compose/.env.local -p fraudlens-live -f infra/compose/compose.yaml up -d --pull never` | Created only `fraudlens-live_default`, `fraudlens-live-pgdata`, and `fraudlens-live-postgres-1`; reused the existing pinned image. |
| `docker inspect --format ... fraudlens-live-postgres-1` | State `running`, health `healthy`, project label `fraudlens-live`, port `127.0.0.1:5432->5432/tcp`, image ID matches inspected digest. |
| `docker exec fraudlens-live-postgres-1 pg_isready -U fraudlens_admin -d fraudlens_live` | `/var/run/postgresql:5432 - accepting connections`. |
| `docker exec fraudlens-live-postgres-1 postgres --version` | `postgres (PostgreSQL) 16.14`. |
| Authenticated SQL: `select current_database(), current_user, version();` | `fraudlens_live|fraudlens_admin|PostgreSQL 16.14 on x86_64-pc-linux-musl ... 64-bit`. |

Credential handling: `.env.local` is ignored by Git. The initial Compose config display rendered its interpolated credential in command output; it was immediately rotated in PostgreSQL and `.env.local`, then authenticated SQL was verified with the replacement. The former credential must not be reused. No credential value is recorded here.

**Disposition:** PostgreSQL image/version, isolation, loopback bind and health are verified for this service. T002 remains PARTIAL: broker, Debezium, dbt, MLflow and monitoring images/compatibility, numeric retention policy and actual least-privilege roles are not yet verified or implemented. No application migration or test was run.
## Current T002 owner direction (2026-11-16)

The requester explicitly accepts starting T003 while T002 stays PARTIAL for broker, Debezium, dbt and MLflow. The real database is the existing `fraudlens-live` PostgreSQL service; it was reused, not recreated. Verified values: PostgreSQL 16.14, image `postgres:16-alpine@sha256:57c72fd2a128e416c7fcc499958864df5301e940bca0a56f58fddf30ffc07777`, `POSTGRES_IMAGE_ID` matches, host port 5432 loopback. `PROMETHEUS_IMAGE` and `GRAFANA_IMAGE` also remain `NOT_VERIFIED`.

Policy proposals, requiring requester confirmation:

| Role | Proposed boundary |
|---|---|
| `live_producer` | Insert immutable live facts/receipts through the controlled ingest boundary; no update/delete. |
| `cdc_connector` | Read only the allowlisted live-facts publication and use its configured replication slot. |
| `live_worker` | Read live facts and later write derived processing state; no label access. |
| `label_curator` | Restricted confirmed-label write boundary only. |
| `registry_operator` | Reviewed model/deployment metadata operations only. |
| `live_api_reader` | Read-only access to approved views, no writes or label access. |

**Retention/outage proposal (needs owner confirmation):** retain source WAL and broker events longer than the maximum supported outage plus replay horizon; retain canonical SQL facts for the supported history/replay horizon or keep a reconstructible archive; declare a gap if that horizon is exceeded. The numeric outage horizon, WAL cap, broker duration and canonical/archive retention are unspecified. No concrete retention settings are applied. T002 remains unticked.
