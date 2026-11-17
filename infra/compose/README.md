# Feature 005 local infrastructure inventory (T002)

**Status: PARTIAL / BLOCKING.** The PostgreSQL image/version and a subset of
database grants have prior disposable-test evidence. Docker Engine could not be
reached during the 2026-11-17 review. Other stack pins, numerical retention and
outage limits, and owner approval of the complete access policy remain open.
This inventory does not claim that the proposed full stack is compatible.

## Version and compatibility inventory

| Component | Pin / observed version | Evidence and readiness |
|---|---|---|
| Docker CLI / Compose | 28.3.2 / v2.39.1-desktop.1 | Client versions observed 2026-11-17; not server versions. |
| PostgreSQL | `postgres:16-alpine@sha256:57c72fd2a128e416c7fcc499958864df5301e940bca0a56f58fddf30ffc07777`; server 16.14, amd64 | Image inspect, server query and T004 disposable database tests recorded 2026-11-16. Current engine/container state unavailable in this session. Compose uses this immutable digest and `pull_policy: never`. |
| psycopg / psycopg-binary | 3.3.9 / 3.3.9 | Locked in `uv.lock`; T004 integration tests passed against PostgreSQL 16.14. |
| Kafka-compatible broker | Not selected | Redpanda is a research proposal; Kafka is an alternative. No image/client pin or interoperability test. |
| Debezium PostgreSQL connector | Not selected/pinned | Version, image digest, and compatibility with the chosen broker and PostgreSQL configuration are unverified. |
| dbt, MLflow, Prometheus, Grafana | Not selected/pinned | Image/client compatibility is unverified; these are not configured in the current Compose file. |

Do not choose a broker distribution or claim cross-service compatibility until
the named images/clients are pinned and exercised together. `versions.env` is
the machine-readable inventory; `NOT_VERIFIED` is intentional for unresolved
components.

## Secret handling and rotation

Compose reads `POSTGRES_PASSWORD` from the ignored local file
`infra/compose/.env.local`; `.gitignore` excludes `.env.*`, and the reviewed
local path is untracked. Never print `docker compose config` output because
interpolation can reveal the password. Use `config --quiet` for syntax checks,
keep examples placeholder-only, and pass credentials through environment files
or secret mounts. Never put values in SQL, evidence, prompts, logs, command
arguments, or Git.

The security audit identifies `POSTGRES_PASSWORD` in that ignored local file as
exposed by a test traceback. The credential was rotated once after an earlier
Compose-output disclosure, but the later traceback disclosed the replacement.
The current value therefore must be rotated again before database reuse. It was
not read or printed in the 2026-11-17 review. Rotation is **BLOCKED** because the
Docker Desktop Linux engine pipe is unavailable; changing only the file without
changing the database would break authentication. Rotate the database role and
ignored file together only after confirming the intended local service and an
approved disposable/isolated database.

## Database role policy (proposal; approval pending)

T004 creates `NOLOGIN` roles and verifies the marked privileges in disposable
PostgreSQL tests. The full target matrix below remains a proposed policy, not a
team-approved access decision or a claim that all roles/grants exist.

| Role | Least-privilege boundary | State |
|---|---|---|
| `migration_owner` | `NOLOGIN`; schema ownership and reviewed migrations only; never used by services. | Defined in T004. |
| `live_producer` | Execute `record_live_transaction`; no direct table writes, update/delete, or label reads. | Verified by T004 catalog test. |
| `cdc_connector` | Read the allowlisted fact publication and use only its replication slot; no writes or labels. | Fact `SELECT` verified; publication/slot not configured. |
| `live_worker` | Read canonical facts; later write only its state, prediction and alert tables; no label access. | Fact `SELECT` verified; derived-table grants await those tables. |
| `label_curator` | Restricted writes to confirmed-label tables only; no worker/prediction writes. | Label tables/grants not implemented. |
| `registry_operator` | Reviewed model/deployment metadata only; no transaction/account or label reads. | Remaining grants not implemented. |
| `live_api_reader` | Read approved live case/alert views only; no writes or label access. | Views/grants not implemented. |

Owner approval, role membership review, and exact future SQL grants remain
required before enabling services. The bootstrap `fraudlens_admin` role is a
local superuser for migrations and must never be used by runtime components.

## Retention, outage recovery and data gaps (proposal; approval pending)

Policy rule: WAL and broker retention must cover the approved maximum outage
plus the recovery/replay duration; canonical facts must remain available for
that history/replay horizon or have a reconstructible archive. Derived state
must retain enough lineage to replay its generation. If WAL, broker or archive
coverage is exceeded, stop claiming complete history and require operator-led
reconciliation into a new generation. Do not silently reset offsets or
watermarks.

The actual maximum outage/recovery horizon, broker retention, WAL capacity and
alert thresholds, canonical fact/archive duration, and cleanup schedule have
not been approved or measured. No numeric retention values or settings have
been applied. Owners must decide these limits against local disk/resource
capacity before T006; the current plan's 24-hour feature history is not itself
an outage or replay target.

## Local PostgreSQL configuration

Prior evidence records Docker project `fraudlens-live`, loopback mapping
`127.0.0.1:5432`, a dedicated named volume, and the image pin above. This session
could not inspect current container health or server state. The current Compose
file contains only the PostgreSQL service; it starts no broker, CDC connector,
worker, dbt, MLflow or monitoring service.

Safe configuration validation (does not start services or connect to a
database):

```powershell
docker compose --env-file infra/compose/.env.local -p fraudlens-live -f infra/compose/compose.yaml config --quiet
```

On 2026-11-17 this exited 0. Docker emitted warnings that the user's
`%USERPROFILE%\.docker\config.json` was inaccessible; the Compose file itself
validated. Do not run `up`, `exec`, PostgreSQL integration tests, or credential
rotation until an approved isolated service is available and positively
identified.
