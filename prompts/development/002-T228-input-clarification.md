# Original request: clarify and fix T228 blockers

Date: 2026-11-20 Europe/Budapest

> i quite do not understand what is the porblem so if you can fix something fix it, everything was apporoved as a team before this session, for training input give me exact problme **Fitting permission and provenance:** the recorded T203 decision permits local data preparation only, and the T210 manifest still says `provenance_complete=false`.
>
> 1. **Approved protocol:** T219 has no complete, approved FR-021 protocol hash. The frozen LightGBM choices are only one part of it.
> 2. **Training input:** the full dataset has not been published as verified chronological features and train/validation partitions.
> 3. **Safe run command:** there is no full-data runner that checks those gates and enforces the resource limits before fitting.

Clarification asked on 2026-11-20: “Did the team explicitly approve model fitting on the exact local HI-Small CSV (SHA-256 beginning b19d39f5) despite its unknown upstream revision and acquisition date, or was approval limited to the model plan?”

User's answer: “Yes, exact local-copy fitting was approved”. This reports team approval for fitting the source with full SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`. It does not establish the unknown upstream revision, acquisition date, or timezone. It does not supply the complete FR-021 protocol hash. Historical T210 manifest fields remain unchanged.
