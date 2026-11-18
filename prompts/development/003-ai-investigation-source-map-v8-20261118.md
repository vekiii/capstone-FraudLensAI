# Technical development record — T101/T102 prospective candidate

Version: source-map-v8/report-v5,2026-11-18. Scope: offline implementation and tests;
not a live execution instruction, new task, training request or acceptance claim.

Implementation instructions used for this candidate:

> Preserve all executed source/prompt/code snapshots and failed results. Replace
> the opt-in selector response list with a closed object containing one rank per
> authorized source. Copy exact source text in deterministic code; reject invalid
> keys/ranks/verdicts/overflow instead of silently repairing. Preserve old profiles,
> default policy IDs, public contracts and dispatch/deadline limits. Version report
> instructions to name the actual score.source and disclose the actual available
> history filter. Keep calibration/gold/private obligations outside model inputs.
> Test negative cases and binding/retry behavior before claiming local readiness.

Outputs: `prompts/application/retrieval-answerability-v8.md`,
`prompts/application/investigation-v5.md`, the opt-in adapter/settings implementation
and regression tests. Full1150 backend tests pass. No numerical live v8 quality or
retrieval acceptance. New-version/source/budget review remains pending in
`specs/003-ai-investigation/t101-t102-source-map-v8-proposal-20261118.md`.
