# Current-to-target gap audit

**Inspected 2026-11-15; documentation only.** Paths are repository evidence, not deployed-service observations. See [evidence register](evidence.md).

| Component | Status | Evidence and required change |
|---|---|---|
| Synthetic fixture/API and batch SQLite workflow | Existing and reusable | `main.py`, `pipeline_cli.py`, `data_store.py`; protect with regression tests, do not repurpose dataset v2. |
| Strict 24-hour, equal-time history catalog | Existing but requires modification | `feature_history.py` is batch replay from ordered events; build a durable live adapter and prove parity under late delivery. |
| Trusted scikit-learn artifact and explanation | Existing but requires modification | `model_scoring.py` binds dataset/scorer/manifest and `ScoreRequestV2`; a separate live request and compatibility signature are required. Exact approved artifact unavailable locally. |
| PostgreSQL source/migrations and stable live producer ID | Missing | Only SQLite stores exist; define immutable facts, DB roles and migrations. |
| Debezium publication/slot and broker | Missing | No Compose, connector or topic configuration in repository. Scope approval and tested image versions required. |
| Durable buffer, watermark and late-data policy | Missing | Batch replay sorts a complete input; streaming needs bounded event-time finalization and quarantine. |
| Atomic offset/state/prediction/alert persistence | Missing | Existing `RunStore` atomically publishes completed batch runs but is not a streaming checkpoint store. |
| Live FastAPI/frontend routes | Existing but requires modification | Existing case list/detail read an active SQLite run. Add separate live versioned routes and view. |
| SQL/dbt training datasets and confirmed labels | Missing | Current private IBM labels are offline benchmark labels, not confirmed investigation feedback. |
| MLflow registry/promotion | Missing; blocked by decision | No tracked MLflow dependencies, registry or approval record for live model; retain local hash gate. |
| Prometheus/Grafana and recovery runbooks | Missing | No runtime metrics/exporter/Compose stack; add before operational readiness. |
| Feature 002 acceptance/peer evidence | Blocked | T065/T066 still blocked on unavailable original SQLite/artifacts/protocol; do not claim boosted model approved. |

**Breaking-change risks:** dataset version `dv_...` binds an offline CSV lineage; live IDs cannot reuse ordinal-derived `D...` semantics without a reviewed namespace; current v2 scoring validates exact snapshot/digest/run and manifest dependencies; `APP_MODE=dataset` reads a completed SQLite snapshot rather than live rows; one broker partition constrains throughput; late arrivals after finalization require audited replay; model score and alert policy must stay distinct. Do not weaken old validators to make the live path pass. Migration proceeds through additive contracts and shadow comparison with explicit team signoff.
