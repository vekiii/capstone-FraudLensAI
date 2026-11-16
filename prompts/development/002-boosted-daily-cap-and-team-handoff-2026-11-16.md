# Development request record — 2026-11-16

This records the user's request in condensed form; the conversation contains
the full original wording.

Continue in local FraudLensAI on `model-implementations`. Finish the technical
work possible for one contributor and prepare a complete team handoff. The
main local model is `HistGradientBoosting`, scorer
`model-history-v1-boosted-candidate`, threshold `0.9936687168275105`.

Read current instructions, next work, quickstart, daily-cap proposal and
T065–T067 evidence; preserve team and local work and existing full v3 run.
Align the contract and implement the proposed daily top-20 UTC policy in a
new isolated run: threshold eligible transactions, score descending, stable
transaction ID ascending, maximum 20 per date, consistent API list/count and
detail, policy version and provenance. Keep v3's 166 alerts. Validate exact
20, overflow, ties, midnight, zero-alert days and expected 159 alerts on
existing full scores; use a verified score transfer if possible and repeat
full inference only when necessary. Activate only the isolated completed run
and check API/browser; run backend/frontend, Ruff, typecheck, build and diff
checks.

Put code, tests, contract, quickstart, model README, evidence and next work in
Git. Build a local private package containing the complete boosted artifact,
full-precision five-case JSON, label-free operational records and history-v1
snapshots, and the 19/20 validation report, with file hashes and transfer
paths. Inventory and verify the original tree benchmark artifact, saved
predictions, report and ledger separately; keep models, databases and
transaction predictions out of Git. Record local T065 results, peer T066
steps/expected outcomes, T067 technical/team/independent status. If a new
compatible 24-hour period exists, freeze period/model/threshold/policy before
label access and test at least five hits among at most 20 alerts; otherwise
record the missing input. Shared activation is a separate decision. After
checks, review staged diff, commit and push to `origin/model-implementations`
without force, verify remote SHA and return commit link, package path, launch
procedure, cap result and remaining team confirmations.
