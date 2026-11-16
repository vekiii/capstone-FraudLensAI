# T067 convergence preparation — pending review

## User-authorized isolated daily policy and team handoff — 2026-11-16

The user authorized finishing the local technical path for
`boosted_utc_daily_top20_v1` and publishing code/evidence for team review.
The versioned [contract](../../specs/002-data-and-risk-scoring/contracts/data-and-scoring.md),
derived-run code, strict optional API list fields, frontend display, tests and
[private handoff inventory](feature-002-team-handoff-2026-11-16.md) now exist.
The original v3 score archive remains immutable with 166 threshold alerts;
the new policy run preserves all 3,963,424 scores/assessments and is expected
to publish 159 cases after seven daily overflow exclusions. The exact
completed-run outcome and API/browser checks are recorded in
[publication evidence](feature-002-daily-cap-publication-2026-11-16.md).
This is technical local readiness, not shared activation. T065 still needs
another teammate's five-case explanation review; T066 needs her same-hash
boosted and original-tree reproduction; T067 needs real team code/contract/
evidence review and a separate shared-activation decision. No previously
unseen compatible 24-hour source exists locally. Before reading labels in
one, freeze exact interval, boosted artifact, threshold and this policy;
require at least five hits among at most 20 alerts. Phase 2 trace remains
unavailable. Do not mark Feature 002 accepted from the current IBM reuse.

## Local boosted path and capacity decision inventory — 2026-11-16

The contributor has a verified local boosted path and a completed immutable v3 technical run (3,963,424 scored; 166 threshold alerts), with API/UI list/detail checks. The shared active run remains on the original scorer. An offline, read-only daily top-20 proposal would retain 159 and remove seven alerts; 2 September (24→20) and 9 September (23→20) are the two over-capacity full UTC days. In already inspected train/validation rows it would reduce hits from 108 to 106; test labels were not read. [The proposed contract diff](../../specs/002-data-and-risk-scoring/proposals/boosted-daily-cap-contract.md) is pending team decision because current scoring/API contracts define all threshold crossings as alerts and `total_alerts` accordingly. No product cap is active. T065 remains open for another teammate's full five-case explanation review, T066 for her independent same-hash source/artifact/report reproduction, and T067 for human code/contract/evidence review plus capacity decision. A previously unseen compatible 24-hour UTC source with adequate warm-up is still absent; freeze period/model/threshold/approved policy before reading its labels and require at least five hits among no more than 20 alerts. Phase 2 compliance trace remains unavailable. Do not close Feature 002 or promote the shared active run.

## Boosted candidate addendum — 2026-11-14

The separate [boosted development/integration evidence](feature-002-boosted-validation.md#trusted-candidate-artifact-and-isolated-integration--2026-11-14) shows exact 19/20 validation reproduction from a saved trusted local artifact, plus label-free isolated API/UI publication. This does not alter the frozen T029–T064 completion evidence or the published T062 exploratory benchmark. No untouched compatible 24-hour source exists locally, so the user-approved acceptance floor (at least five positives among at most 20 alerts) has no independent result. Full-source candidate scoring and shared activation remain open. The five candidate review examples are ignored at `evals/results/boosted-explanation-review.json`; T065 still requires Isidora's actual five-example review, T066 her independent reproduction, and T067 actual human code/contract/evidence review. Do not mark SC-006, SC-009, independent FR-015 acceptance or Phase 2 compliance complete on this addendum.

### Full-run technical update

The [completed full-run evidence](feature-002-boosted-validation.md#completed-v3-result-and-isolated-application-check) supersedes the earlier "full-source scoring open" statement above: isolated v3 run completed with 3,963,424 scored, 1,114,921 warm-up excluded, 166 alerts, and matching API/UI list/detail behavior. Shared activation remains unchanged. At frozen threshold `0.9936687168275105`, two **full** UTC days exceed 20 alerts: September 2 has 24 and September 9 has 23. Thus the current threshold alone does not satisfy a strict daily review capacity on this existing source. These dates are already inspected technical data, not an independent utility test.

Before proposing a new production policy, predeclare a development-only UTC daily selection rule: among scores at or above the frozen threshold, sort by score descending then transaction ID ascending and retain at most 20 per complete UTC day. On the already inspected development data, compare all alerts with the retained top 20, quantify the four and three over-cap alerts removed on September 2/9, verify ties and UTC boundaries, and inspect the effect on available development labels only after the selection is saved. Record any change to hits and daily count without calling it independent acceptance. Obtain team approval for any policy/contract change, then freeze the rule before an untouched compatible 24-hour UTC period is scored and its labels opened. The acceptance check remains **at least five hits among at most 20 alerts** in that previously unseen period.

T065 remains open pending another teammate's actual review of the [five full-run examples](feature-002-explanation-review.md#boosted-full-run-sample--2026-11-14). T066 remains open pending another teammate's [source/artifact/run/report reproduction](feature-002-peer-reproduction.md#boosted-full-run-reproduction--pending-teammate-run). T067 still needs actual human code, contract and evidence review; independent FR-015 acceptance, SC-006/SC-009, and Phase 2 compliance cannot be marked complete from this run. No shared promotion or Feature 002 closure is supported yet.

This is a handoff inventory, not T067 acceptance. Technical evidence exists for T060–T064: [regression](feature-002-regression.md), [benchmark and numeric repeat](feature-002-benchmark.md), [Phase 5 fit/protocol](feature-002-model-metrics.md), [artifact/explanation](feature-002-artifacts-explanations.md), [publication](feature-002-publication.md), [API/UI](feature-002-api-ui.md). Read tasks.md's FR-001–026 and SC-001–009 coverage table against these records, the specification, plan, data model, JSON Schemas and current code.

Open evidence gates: T065 another teammate's five-example explanation review; T066 another teammate's separate-source import/trusted scorer/report reproduction; T067 actual human code/contract/evidence review and resolution of deviations. SC-006 and SC-009 remain pending those gates. SC-004's numerical comparison/repeat is present, but the earlier 60/20/20 notebook exposed all current test rows, so FR-015 prohibits an independent confirmatory performance claim. FR-016's observed top-20 positives are zero for both scorers, and both frozen thresholds produce zero alerts. This is an exploratory comparison only. The Phase 2 assignment/compliance trace remains unavailable and cannot be asserted. Fresh Phase 8 browser control was disabled; see regression evidence and earlier Phase 7 browser checks.

Reviewer should mark each FR/SC row only after checking the exact test/evidence, record actual person/date/findings, and leave unmet claims open. Do not alter the frozen model, threshold or protocol to improve the benchmark. No human review is claimed here.
