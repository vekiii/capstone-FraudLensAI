# Feature 002 proposed inference-only Phase 5 scope — 2026-11-13

## Basis and decision status

The [original Phase 5 checklist](../../specs/002-data-and-risk-scoring/tasks.md) keeps T026–T028 complete and T029–T036 open. The [final Phase 5 handoff](feature-002-pretrained-final-review.md#phase-5-task-reconciliation---2026-11-13) confirms no loader, IBM model adapter or real prediction exists. The [replacement-model audit](feature-002-replacement-model.md) finds Kluey and Daemons-Q **BLOCKED** for direct `history-v1` inference; the earlier FraudSentinel graph review also blocks that candidate. The untracked T029 protocol draft belongs to the original training path and is not a committed pretrained protocol. Existing unrelated untracked files were preserved.

The [IBM model decision](../../specs/002-data-and-risk-scoring/proposals/pretrained-ibm-model-decision.md) records the user's 2026-11-13 statement that all team members approved and verified the **direction** to use pretrained IBM inference. That is the evidence for investigating and drafting this path. It provides no reviewer names, signed approval of the [new P5I checklist](../../specs/002-data-and-risk-scoring/proposals/pretrained-inference-only-checklist.md), approved candidate, accepted departures from T029–T036, or approved evaluation design. The older [integration proposal](../../specs/002-data-and-risk-scoring/proposals/pretrained-model-integration.md) remains pending as a formal requirements amendment. Do not turn the general direction into a waiver of local fitting, validation selection, metrics or holdout controls.

| Approval field | Recorded evidence |
| --- | --- |
| Direction | User-reported collective approval to investigate/continue pretrained IBM direction, recorded 2026-11-13 in the IBM model decision. |
| Reviewer identity | No individual reviewer names recorded for this replacement checklist. Do not invent them. |
| Checklist acceptance date | None; draft date 2026-11-13 is not an approval date. |
| Accepted deviations/waivers | None recorded for T029–T036. All remain open. |
| Candidate and artifact authorization | None of the audited candidates passes feature/history compatibility. No candidate is approved for implementation. |
| Evaluation authorization | No independent publisher/local row disjointness proof or approved inference-only metric protocol. Holdout remains sealed. |

## Proposal and schedule impact

The [separate checklist](../../specs/002-data-and-risk-scoring/proposals/pretrained-inference-only-checklist.md) proposes P5I-01–P5I-06: candidate/artifact verification, frozen manifest/evaluation policy, loader RED/GREEN, inference RED/GREEN, small real IBM smoke and an independent-evaluation decision. Its task-by-task matrix maps to T029–T036 without marking any original task complete. Proposed benefit: use unchanged learned weights without local training if a trustworthy, semantically compatible IBM model exists. Proposed cost: additional source/security/legal review, exact preprocessing and point-in-time parity work, protocol/spec/plan updates, tests, evaluation-exposure audit and human review. No defensible time estimate or model-performance gain is available. If no candidate passes, retain rules/Foundation scoring and report the model path blocked.

The constitution's team-controlled scope, specification-before-implementation, independent-evaluation and verifiable-claims principles apply. **Implementation stop:** obtain a specific compatible candidate and record an actual team decision on this checklist, the exact accepted deviations, affected spec/plan/research/contracts and the evaluation/threshold policy before loader or inference work. The existing synthetic RED suites remain interface evidence only; they do not validate a new candidate.

## Documentation checks

This was documentation work only. No model file, dataset, source mapping, application code, task checkbox, holdout or private label was modified or accessed for scoring. `git diff --check` exited **0** with no whitespace errors (only a nonfatal LF/CRLF working-copy notice for `next_work.md`). `rg -n '^\- \[ \] T0(29|30|31|32|33|34|35|36)' specs/002-data-and-risk-scoring/tasks.md` exited **0** and found all eight original tasks still unchecked. No test suite was run; no GREEN claim is made.

**Next action:** identify and audit a pretrained IBM laundering model with immutable weights, full preprocessing state, bank-qualified identity, strict point-in-time `history-v1` semantics and documented training-row exposure; then present that candidate and this exact checklist for a recorded team scope decision.
