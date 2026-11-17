# Feature 005 migration policy (T002)

**Readiness: PARTIAL / BLOCKING.** T004 migration `001_live_facts.sql` and its
role-boundary assertions passed against disposable PostgreSQL 16.14 databases;
the image digest and test record are in
[`infra/compose/README.md`](../../infra/compose/README.md) and
[`evidence/tasks/feature-005-t004.md`](../../evidence/tasks/feature-005-t004.md).
The current Docker Engine could not be reached, and the T002 stack, retention,
outage and access-policy decisions remain incomplete.

Migrations are numbered and append-only. Do not edit an applied migration.
Apply future migrations to an approved disposable PostgreSQL database using a
dedicated migration owner, then inspect catalog constraints, ownership,
memberships and grants before enabling runtime principals.

## Role boundaries

The complete least-privilege policy remains proposed pending owner review.
T004 verified that `live_producer` can execute the controlled immutable ingest
function but cannot update/delete facts, and that `cdc_connector` and
`live_worker` can select facts. Remaining targets are:

| Role | Intended boundary |
|---|---|
| `migration_owner` | `NOLOGIN`; owns schema and applies reviewed migrations; not used by services. |
| `live_producer` | Execute the ingest function only; no direct table mutation or label reads. |
| `cdc_connector` | Read the allowlisted publication/use its slot only; no application writes or label access. |
| `live_worker` | Read facts and later write only owned state/prediction/alert tables; no labels. |
| `label_curator` | Restricted confirmed-label writes only; no prediction/worker access. |
| `registry_operator` | Reviewed model/deployment metadata only; no transaction or label reads. |
| `live_api_reader` | Read approved live views only; no writes or labels. |

Roles/tables not yet implemented have no claimed grants. Review membership and
exact SQL grants before service activation. Credentials come from ignored local
environment files or secret mounts; never include values in migrations or docs.

## Retention and recovery

Proposed rule pending owner approval: retain WAL and broker events for the
approved maximum outage plus replay horizon; preserve canonical facts for the
history/replay horizon or a reconstructible archive; retain derived state with
its generation lineage. A missing range is a coverage gap requiring
operator-led reconciliation, not an empty-history reset. Numeric outage,
replay, WAL capacity, broker, SQL/archive retention and cleanup limits are not
approved or configured.
