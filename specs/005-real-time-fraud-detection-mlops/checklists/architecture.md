# Architecture and integration gate

- [ ] Verify migrations create named keys, FKs, unique constraints, indexes and role grants exactly as [data model](../data-model.md) specifies; inspect migration and database catalog, T004.
- [ ] Prove one SQL insert yields one committed CDC event with expected topic key and LSN; integration test T008–T009.
- [ ] Prove single-worker/one-partition invariant is enforced, and reject unsafe parallel consumption; integration test T009/T012.
- [ ] Trace DB commit before offset acknowledgment and all recovery paths; fault injection T021/T024.
- [ ] Verify model-serving adapter maintains trusted artifact checks and no fake `dv_` lineage; negative contracts T019/T020.
- [ ] Check API response/generation cursor matches persisted assessment and UI detail; contract/E2E T027–T030.
- [ ] Demonstrate offline batch CLI and fixture mode still run independently; regression T046.
