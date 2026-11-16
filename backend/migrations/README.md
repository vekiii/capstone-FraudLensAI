# Feature 005 migration policy (T002)

**Status: PROPOSED; no PostgreSQL image/server version is verified.** Migrations are planned to be append-only and numbered (`001_live_facts.sql`, then later migrations); do not edit a migration after it has been applied. Apply to an isolated PostgreSQL database with a dedicated migration owner, then inspect the catalog and grants before enabling application roles.

## Proposed roles for migration review

| Role | Intended boundary |
|---|---|
| `migration_owner` | Own schema and apply reviewed migrations; unavailable to runtime services. |
| `live_producer` | Insert `live_transactions`; no update, delete or label access. |
| `cdc_connector` | Read only the approved live-facts publication and use its replication slot; no fact mutation. |
| `live_worker` | Read facts and write derived state, predictions and alerts; no confirmed-label access. |
| `label_curator` | Write restricted confirmed labels only. |
| `registry_operator` | Manage reviewed deployment/model metadata only. |
| `live_api_reader` | Select approved live read views only; no writes or labels. |

These are proposed role names/boundaries, not existing grants or an approved access policy. T004 must define and verify exact SQL privileges against the pinned PostgreSQL version. Credentials must be supplied outside Git; no secret values belong in migration files or this README.

## Retention proposal

Keep source WAL and broker events for longer than the approved maximum outage plus replay horizon; retain canonical facts for the history/replay horizon or preserve a reconstructible archive; treat any exceeded horizon as an explicit data gap. The exact duration, size caps, archive process and approved outage target remain unset. No retention values or service settings have been applied.
