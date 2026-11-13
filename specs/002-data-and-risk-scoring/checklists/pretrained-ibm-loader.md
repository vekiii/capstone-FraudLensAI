# IBM pretrained loader review checklist

Status: preparatory RED tests authored; production loader and real artifact
verification remain open. This checklist tracks the team-approved pretrained
direction separately from the original training-based T029–T036 tasks.

- [x] Team scope approval reported by the user on 2026-11-13; recorded in the [decision](../proposals/pretrained-ibm-model-decision.md).
- [x] IBM AML LightGBM source revision, 22-name source feature recipe and publisher preprocessing SHA-256 recorded in [artifact evidence](../../../evidence/tasks/feature-002-pretrained-model.md).
- [x] Synthetic loader test module authored and collected without dependency or collection error.
- [ ] Independently verify the native model's exact bytes, size, SHA-256, header and categorical metadata.
- [ ] Obtain a safe, complete primitive representation of the pinned graph preprocessing state; do not deserialize joblib in the application.
- [ ] Reconcile account identity and time coverage against the actual saved state and freeze an IBM-specific artifact manifest with the real checksums and runtime.
- [ ] Observe substantive intended RED failures for loader behavior, beyond the missing-interface assertion.
- [ ] Implement Prompt 05 loader GREEN and run fixture/rules regressions without fitting or holdout evaluation.

The historical T026–T028 completion and open T029–T036 markers remain unchanged.
- [ ] Implement Prompt 07 transaction inference only after loader GREEN, approved source mapping, safe graph-state provenance, native runtime and the Prompt 06 contract checks. The 2026-11-13 gate check is recorded in pretrained-model evidence.
- [ ] Verify Prompt 08 real IBM inference only after a real approved manifest, compatible graph state and eligible label-free smoke population exist; do not claim independent performance without exposure proof and an approved protocol. The gate audit is in `evidence/tasks/feature-002-pretrained-evaluation.md`.
