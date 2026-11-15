# Security and operational readiness gate

- [ ] Verify separate producer/connector/worker/API/label/registry roles and least-privilege grants; T002/T043.
- [ ] Ensure secrets are ignored/mounted and absent from Git, logs, metrics labels and API errors; static scan and integration T043.
- [ ] Measure CDC slot/WAL, Kafka lag, buffer/watermark age, quarantine and model digest metrics; alert injection T041/T042.
- [ ] Restore from backup and replay a known range; compare digest/count and document retention gap behavior; T044.
- [ ] Test broker, connector, DB and worker outage/restart without duplicate/lost assessments; T024/T045.
- [ ] Verify live endpoints have role checks, bounded pagination, redacted list data and stale-token errors; T027/T028.
- [ ] Record Docker image versions, dependency locks, host resources and cleanup/reset steps; T006/T044.
