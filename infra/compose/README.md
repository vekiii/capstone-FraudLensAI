# Feature 005 local service inventory (T002)

**Status: PARTIAL.** The PostgreSQL image digest/version is verified and the isolated PostgreSQL service is running. Other service image versions/digests, numeric retention settings and runtime role grants remain unverified. `versions.env` is an inventory; it does not claim the full stack is compatible.

## Docker observation

On 2026-11-16, Docker CLI reported version `28.3.2`; Docker Compose reported `v2.39.1-desktop.1`. The active context was `desktop-linux`, but the Docker Desktop Linux engine pipe did not exist and the `com.docker.service` Windows service was stopped. `docker image ls --digests --no-trunc` could not connect to the daemon. Therefore image names, tags, versions and digests are `NOT_VERIFIED`; no compatibility claim is made.

| Service | Candidate | Version/digest |
|---|---|---|
| PostgreSQL | `postgres:16-alpine` | Verified: PostgreSQL 16.14, digest `sha256:57c72fd2a128e416c7fcc499958864df5301e940bca0a56f58fddf30ffc07777` |
| Broker | Redpanda candidate or Kafka | NOT VERIFIED — daemon unavailable |
| CDC connector | Debezium PostgreSQL connector | NOT VERIFIED — daemon unavailable |
| SQL transformations | dbt | NOT VERIFIED — daemon unavailable |
| Model tracking/registry | MLflow | NOT VERIFIED — daemon unavailable |
| Metrics | Prometheus | NOT VERIFIED — daemon unavailable |
| Dashboards/alerts | Grafana | NOT VERIFIED — daemon unavailable |

## Proposed database roles

These least-privilege role names and boundaries are PROPOSED and require the owner's confirmation. They are not created or verified database roles/grants:

| Role | Proposed access boundary |
|---|---|
| `live_producer` | Insert immutable live facts only; no update/delete or label access. |
| `cdc_connector` | Read the allowlisted live-facts publication and use the required replication slot; no application writes. |
| `live_worker` | Read operational facts; write derived processing state, predictions and alerts; no confirmed-label access. |
| `label_curator` | Write restricted confirmed labels only; no worker/prediction writes. |
| `registry_operator` | Manage model/deployment metadata and promotion records only through reviewed operations. |
| `live_api_reader` | Read approved live case/alert views only; no writes or label access. |

Exact SQL grants, replication privileges and role ownership remain for T004/T006 review against the selected PostgreSQL version. No database roles were created.

## Proposed retention and outage policy

The retention and outage policy is PROPOSED and requires the owner's confirmation: retain broker events and source WAL for longer than the approved maximum outage plus replay window; retain canonical SQL facts for at least the supported history and replay horizon or keep a reconstructible archive; raise an explicit gap if retention is exceeded. The numerical maximum outage/replay period, WAL size limit, broker retention duration and SQL/archive retention remain unspecified and must be confirmed before service configuration.

Secrets are not stored in this inventory. Future Compose secrets must use ignored local environment files or secret mounts, with placeholders/examples only in Git.

## Isolated PostgreSQL (local development)

Verified image: `postgres:16-alpine@sha256:57c72fd2a128e416c7fcc499958864df5301e940bca0a56f58fddf30ffc07777` (PostgreSQL 16.14, amd64). The image digest and version came from `docker image inspect`; Compose uses `pull_policy: never` and does not update the image. Docker project: `fraudlens-live`. Host mapping: **127.0.0.1:5432 → container 5432** (5432 was free; 5433 was not needed). Data volume: new, dedicated `fraudlens-live-pgdata`.

Create ignored local credentials at `infra/compose/.env.local` (already present on this machine; never commit it). Start and inspect only this project:

```powershell
docker compose --env-file infra/compose/.env.local -p fraudlens-live -f infra/compose/compose.yaml config --quiet
docker compose --env-file infra/compose/.env.local -p fraudlens-live -f infra/compose/compose.yaml up -d --pull never
docker compose --env-file infra/compose/.env.local -p fraudlens-live -f infra/compose/compose.yaml ps
docker inspect fraudlens-live-postgres-1
```

This Compose file declares only the isolated PostgreSQL service. It does not stop, remove, or modify other containers, volumes, networks, or images. The `fraudlens_admin` bootstrap role is a local superuser for migration setup; T004 must create and verify restricted runtime roles before application use. Numeric retention policy, broker and other service images remain unresolved; T002 is still partial overall.