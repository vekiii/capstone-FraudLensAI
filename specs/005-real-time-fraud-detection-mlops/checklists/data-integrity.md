# Data integrity and historical correctness gate

- [ ] Compare live and batch `history-v1` outputs on hand-computed and generated timelines, including equal-time peers and `[t-24h,t)` boundaries; T017 parity report.
- [ ] Test bank-qualified sender/receiver state and distinct counterparties; T016/T017.
- [ ] Test paid/received currency separation, Decimal sums, zero versus unavailable history and no FX conversion; T016/T017.
- [ ] Test duplicate same-ID/same-digest no-op and changed digest conflict in SQL, CDC and consumer; T005/T010/T022.
- [ ] Test out-of-order within watermark, skewed future time, quiet-stream heartbeat and late-after-finalization quarantine; T013/T014.
- [ ] Crash before and after SQL commit; reconcile offsets, buffers, finalized state and visible alerts; T024/T025.
- [ ] Verify no label/target data enters event schema, feature digest, prediction or live API; static/negative tests T016/T032.
- [ ] Verify replay creates a new generation and detects missing retention/WAL range; T023/T025.
