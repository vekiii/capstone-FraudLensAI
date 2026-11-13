# Feature 002 pretrained model integration proposal

**Status:** Proposed on 2026-11-13; team decision pending. This is a review
record, not an amendment to the approved specification, protocol, or tasks.
No pretrained artifact has been selected or loaded. No model fit, inference,
validation, or holdout disclosure is claimed.

**Starting point:** `model-implementations` at
`d606fb7137be1c4f43cce6b89c8c89d350054862`, descended from
`002-data-and-risk-scoring` at `27ac7d49e3d638717c752dce225216d291bf9e87`.
The branch already existed and was active when this proposal began.

## Requested change and reason

The requested direction is to download and integrate an already-trained
fraud-detection model for inference. The team would not train, retrain,
fine-tune, or optimize a model. The possible benefit is avoiding local model
fitting and its compute cost, provided a lawful, trusted and compatible
artifact exists. This is a material change from [the approved model-selection
specification](../spec.md), [plan](../plan.md), [research decisions](../research.md)
and [T026–T036](../tasks.md), which require a locally fitted, bounded candidate
comparison and validation-selected model. Under the [constitution](../../../.specify/memory/constitution.md)
and [AGENTS.md](../../../AGENTS.md), the team must approve the deviation and
its affected acceptance criteria before implementation. The current request
authorizes documenting the proposal, not a team decision to amend those files.

## Requirement impact

| Task | Approved requirement | Impact of inference-only direction |
| --- | --- | --- |
| T026–T027 | Chronological, whole-timestamp split; eligible label roles; sealed test/holdout | Keep these completed safeguards. A downloaded model's original training data and time boundary would also need provenance checks; existing splits alone cannot prove absence of prior exposure. |
| T028 | Locked fitting dependencies and 100,000-row resource pilot | Completed evidence remains historical. The new artifact needs separate inference runtime, dependency, memory, disk and safe-loading checks. The fitting pilot does not establish those results. |
| T029 | Freeze exact source/split, candidate grid, at most six fits, train-only transforms, validation selection and threshold before experiments | Current task cannot be completed as written for an inference-only model. A revised protocol would need to freeze artifact identity and provenance, schema, preprocessing, acceptance criteria, evaluation roles and operating policy before label inspection. The uncommitted T029 draft in the worktree is not a frozen protocol. |
| T030 | RED tests for train-only fitting, six-fit bound, candidate ranking and validation threshold selection | Fitting and candidate-selection assertions conflict. New tests would need to cover artifact provenance, safe loading, feature/preprocessing parity, inference outputs, label isolation and failure states. Existing T030 remains open. |
| T031 | Fit L2 logistic and decision-tree candidates on `history-v1` training data | Direct conflict. Downloaded weights and preprocessing could be used only if their input schema and semantics exactly match the approved IBM `history-v1` snapshots and the trust contract is amended. T031 remains open. |
| T032 | Select a winner by validation AP/Precision@K and optimize a scorer-specific validation F0.5 threshold | Candidate selection and threshold optimization conflict with the requested no-optimization rule. The team must define a fixed operational threshold or another prospective, non-optimized policy and revise acceptance criteria. No test-label choice is permitted. |
| T033–T034 | Test and implement metrics, same-population rules comparison and single sealed-holdout disclosure | Core evaluation protections still apply if a compatible model is found. Model-selection assumptions and any probability/calibration claims must be revised; an incompatible model must fail closed rather than produce a benchmark claim. |
| T035–T036 | Test and wire `freeze-protocol`/`evaluate` commands, including failed candidates and frozen outputs | Command contracts must reflect an approved artifact acceptance and inference path instead of a fitted-candidate path. Holdout reuse and immutable-report checks remain necessary. Both tasks remain open. |

[FR-012–018](../spec.md) currently require train-only learned transforms,
validation-selected candidates and thresholds, reproducible fitting lineage,
and a trusted local artifact. [Research Decision 12](../research.md) permits
loading only artifacts produced by the reviewed local workflow, with hash,
schema, scorer and dependency checks. A downloaded binary would cross a new
trust boundary. [FR-019](../spec.md) also requires model-local explanations
bound to the actual output scale; the artifact must support a verifiable
explanation method or the requirement needs an approved change. The later real
IBM benchmark and independent reproduction tasks would need to be reconciled
with the revised protocol; prior synthetic checks cannot count as those results.

The approved product target is IBM HI-Small **`Is Laundering`** on the
`history-v1` feature catalog. An IEEE-CIS payment-fraud `isFraud` model, or any
model needing IEEE identity/Vesta features or `TransactionDT`, cannot be
assumed to transfer to that target. A repository containing model-training
code is not evidence of a downloadable trained artifact. No model URL, weight
file, license, checksum, feature schema, label definition, preprocessing,
threshold, explanation method or training-data exposure has yet been verified.

## Schedule and decision record

The six-fit local fitting path might be removed, but artifact investigation,
legal and trust review, schema parity, revised specification/tasks, inference
tests and an honest IBM evaluation add work. A duration estimate is not
supported until an actual artifact is identified. The completed T026–T028
evidence remains intact; T029–T036 checkboxes remain open. No production API/UI
or model code changes are authorized by this proposal.

**Decision:** Pending actual team approval. **Reviewers/date:** Pending.
Before implementation, record approval or rejection and its date, revise the
specification, plan, research, tasks and evaluation contract together, then
begin RED tests for the approved behavior. Preserve holdout secrecy throughout.

**Immediate next step:** Investigate a specific pretrained model artifact:
source and license, downloadable weights, checksum/version, safe format,
training population and target, exact input features and preprocessing,
`history-v1` parity, runtime compatibility, explanations and prospective
evaluation/threshold policy. Report incompatibility rather than substitute
features or claims.
