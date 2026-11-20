# T221 team scope decision reported by the user

Date/timezone: 2026-11-20, Europe/Budapest.

Current request:

> continue implmentation when done commit if something si not working report problem T221 [US3] Resolve and freeze exact candidate grid, class strategy, threshold objective, feature admission policy and budget before any fit; record human decision in protocol/evidence (FR-021, FR-023–026).

In response to a choice between retaining the existing FR-023/024 model plan and preparing the previously requested LightGBM/F1 change, the user replied:

> prepare both all models but start with implmnetation of light gmb and team has already agreed on this and it apporved chnages

This is the user's report of team approval to add LightGBM and change the model-selection plan while retaining the original baseline and HistGradientBoosting comparison. The user did not provide meeting minutes, approver names, or an approved full canonical protocol SHA-256. The earlier T221 Phase 1 instruction still requires `protocol approved: <hash>` before any fit. The T203 local-copy exception and T219 provenance gate remain separate blockers.

The exact combined-model grid, preprocessing representation and fit ceilings in `specs/002-data-and-risk-scoring/t221-model-choices.json` are routine implementation choices made under this direction. An initial cross-family ranking was also proposed, then narrowed by the user's later reply below. The user explicitly approved the expanded model scope, not each generated parameter value or the future complete FR-021 protocol hash.

Later, in response to whether one validation ranking should choose across all model families, the user replied:

> lets focus on light gbm now

The current phase therefore ranks only the eight LightGBM candidates. The previously requested baseline and HistGradientBoosting models remain declared for later comparison. A cross-family winner rule is deferred until that work is requested; no final model across all families is claimed. The revised model-choice digest is recorded in the protocol and T221 evidence.
