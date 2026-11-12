# Codex prompts for Feature 002

Created 2026-11-12. These are **future copy-ready prompts**, not executed
commands or authorization to mark work complete. Start each prompt in the
repository checkout after the preceding gate is met. The current
Feature 002 plan is [plan.md](../../specs/002-data-and-risk-scoring/plan.md);
the feature has no tasks.md or implementation at creation of this file.

These prompts deliberately use work-package names rather than invented
task IDs. Once tasks.md exists, replace the work-package scope with the
corresponding actual task IDs. Do not treat the review transcript as
more authoritative than the revised spec and plan.

## Prompt 0 — Generate reviewable implementation tasks

> Work only on Feature 002 planning-to-tasks. Do not implement application
> code, download data, train models, or claim checks passed.
>
> Read applicable AGENTS.md, then root next_work.md before planning. Set
> SPECIFY_FEATURE_DIRECTORY to specs/002-data-and-risk-scoring in the
> PowerShell session. Read the constitution, original_idea.md, Feature 002
> spec.md, plan.md, research.md, data-model.md, quickstart.md and both
> contracts files plus schemas.json. Read the Feature 001 API/schema,
> current backend/frontend code/tests and docs/decisions/foundation.md.
> Treat prompts/development/002-review.md as review history; the current
> spec and plan are the working requirements.
>
> Apply the local speckit-tasks skill to create tasks.md. Make tasks
> dependency ordered and independently reviewable. Map every FR-001–026
> and SC-001–009 to tasks/tests/evidence. Separate source audit and
> mapping gate; v2 contract/consumer review; importer/identity; feature
> replay; rules baseline; split/protocol; bounded model/metrics;
> explanation/artifact safety; completed-run publication; API/UI
> migration; regression/reproduction/convergence. Put RED tests before
> GREEN business behavior. Give source-unavailable and Phase 2
> requirements-unavailable paths explicit pending states, not invented
> observations. Keep Foundation v1 fixture checks intact.
>
> Validate task ordering, requirement coverage and actual file paths.
> Update next_work.md with what was actually generated and one concrete
> next step. Record commands and limitations in evidence/tasks/.
> Do not commit or push automatically.

## Prompt 1 — Audit the source and freeze mapping/contracts

> Implement only the Feature 002 task slice for source inspection,
> mapping decisions and contract review identified in tasks.md. Start
> by reading applicable AGENTS.md, then next_work.md; set the explicit
> Feature 002 directory. Read the spec, plan, research, data model,
> contracts, relevant tasks, current Foundation code and tests. Keep
> the current branch and unrelated working changes.
>
> Inspect only an authorized local IBM AML HI-Small source if present.
> Before generating artifacts, add and verify a Git ignore rule for the
> local artifact directory; raw and processed data are already ignored.
> Record exact source/release/license/hash, observed headers/encoding/
> dialect, row and label counts, timestamp resolution/timezone evidence,
> amount/currency forms, file size and ambiguities. Do not infer a field
> from a paper or sample and call it observed. If the source is absent,
> implement only independent source-shaped inspection behavior/tests
> and leave the actual mapping and substantive evaluation pending.
>
> Propose/freeze the reviewed mapping and v2 contract only when
> supported by evidence. Compare with Foundation v1 backend schema,
> frontend strict decoder, case ordering and unconditional fixture
> banner. Record affected producer/consumer review under the
> Foundation shared-contract procedure; do not invent reviewers or
> approval. If review is pending, finish independent work but do not
> integrate a breaking contract. Add exact negative tests for duplicate
> and target-like headers, missing fields, invalid encoding and source
> mismatch. Record RED/GREEN and one next step. No commit/push.

## Prompt 2 — Build import, identity and local persistence

> Implement only the importer, canonical facts, row accounting,
> stable identity, private-label separation and staged local import
> tasks from Feature 002 tasks.md. Read AGENTS.md then next_work.md;
> select the feature; read its spec/plan/research/data model/contracts
> and the actual source mapping if frozen. Preserve Foundation v1.
>
> Write and run RED tests for event-valid versus label-eligible rows,
> label-only perturbation, equal-valued distinct rows, bank-qualified
> direction, pre-filter source-row identity, reimport, changed source/
> mapping versions, exact Decimal/time/currency preservation,
> empty/malformed/overflowing files, interrupted import and retry.
> RED must fail for the intended missing behavior. Implement the
> smallest streaming CSV plus local SQLite path in the plan, then run
> GREEN and relevant v1 regressions. Do not accept incomplete imports
> as active, include labels in scorer/public models, round money, or
> silently assume a timezone. Record actual commands/exits, data
> hashes and limits in evidence/tasks/ and update next_work.md.
> Leave actual IBM import pending if the source remains unavailable.

## Prompt 3 — Build point-in-time features and rule scorer

> Implement only the historical replay, feature catalog and real
> rules baseline tasks. Read AGENTS.md then next_work.md; select
> Feature 002; read current spec, plan, data model, contracts and
> importer state. Do not train a model in this slice.
>
> Start with RED hand-calculated timeline tests for [t−24h,t),
> exact boundary, out-of-order input, tied timestamps, future event
> append, earlier held-out fact, label perturbation, warm-up versus
> full-coverage cold start, distinct banks and same-currency
> aggregates. Add proxy/identifier rejection tests. Implement
> timestamp-group replay: compute all tied snapshots before updating
> history. Then implement frozen RulePolicy v1 R1–R3 and actual
> trigger/value/weight explanations. A fixture constant or test-only
> scorer is not the baseline. Verify source/run/feature identity and
> finite scores; no label, ID or future dependence. Run targeted and
> Foundation regression checks, record RED/GREEN/results and
> limitations, update next_work.md, and stop at this scope.

## Prompt 4 — Freeze protocol and evaluate bounded candidates

> Implement only split, protocol, train-only transform, bounded
> candidate selection and scientific evaluation tasks. Start with
> AGENTS.md, next_work.md and explicit Feature 002 selection; read
> all feature design artifacts and actual data/feature evidence.
> If no eligible source import exists, implement synthetic protocol/
> metric behavior tests and leave substantive IBM results unclaimed.
>
> Write RED tests for whole-timestamp 70/15/15 membership,
> observable-before-label boundary choice, class/20-positive guard,
> fit calls restricted to training IDs, unseen categories, candidate
> AP/P@K/simplicity selection, scorer-specific F0.5 threshold policy,
> no-alert choice, K-boundary ties, Recall@K denominator, test
> prediction freeze and consumed holdout. Use the six-fit grid,
> seed and numeric tolerance in the plan unless a documented
> pre-experiment amendment follows the resource pilot. Keep
> optional AutoML/calibration out of the initial run. Compare rules
> and selected model on identical eligible IDs. Report exact counts,
> prevalence, AP, K/threshold metrics, probability-output Brier/
> reliability status and uncertainty limitations. Never tune after
> test disclosure or claim synthetic fixture checks as model
> evaluation. Record actual RED/GREEN/metric commands and limits;
> update next_work.md.

## Prompt 5 — Secure artifacts and faithful explanations

> Implement only artifact manifest/loading and local explanation
> tasks. Read AGENTS.md, next_work.md, explicit feature selection,
> spec/plan/contracts and actual candidate artifacts. Do not add
> a model registry, uploaded-model endpoint, SHAP dependency or
> new screen.
>
> Test artifact path containment, SHA-256, dependency/feature/
> transform/scorer compatibility and corruption before loading.
> Treat pickle-derived local files as trusted only within the
> recorded build workflow. Test wrong transaction/run/snapshot/
> output-scale explanations. Implement rule reasons from actual
> fired conditions. For logistic regression explain raw log odds
> with intercept/top three/remainder and label the displayed
> score transform; for the tree verify path contributions to its
> declared output. Do not claim top three reconstruct the output
> unless base/remainder make that true within frozen tolerance.
> Record RED/GREEN and manual sample-review status honestly.
> Update next_work.md.

## Prompt 6 — Publish completed runs and migrate the case UI

> Implement only completed-run staging/activation, dataset read API,
> v2 frontend decoder and existing list/detail UI tasks. Read
> AGENTS.md then next_work.md; select Feature 002 and read all
> versioned contracts, current Foundation API/backend/frontend
> code/tests and affected-consumer review status. If contract
> review is still pending, complete independent tests/adapters
> but do not silently widen Foundation v1.
>
> RED-test mid-run failure, restart, active-pointer switch, stale
> snapshot, stable case ID across scorer versions, zero alerts,
> latest-100 selection/order/counts and label exclusion. Publish
> only a validated completed run in one local transaction; read
> one active snapshot without request-time scoring. Add strict v2
> GET responses and controlled 409/503 errors while keeping v1
> fixture bodies/order/errors unchanged. Update frontend decoders,
> detail snapshot query, case-ID sorting and fixture banner
> conditionally. Check loading/empty/error/retry/cancellation and
> source/score explanation copy. Run backend/frontend contract and
> regression suites, typecheck/build and record actual results.
> Update next_work.md and stop at this slice.

## Prompt 7 — Converge, reproduce and report

> Perform the final Feature 002 requirements and evidence review
> after implementation. Read AGENTS.md then next_work.md, select
> Feature 002, apply the local speckit-converge workflow to the
> feature's spec/plan/tasks, and inspect actual code/tests/evidence.
> Do not check off tasks merely because they are documented.
>
> Trace every FR-001–026 and SC-001–009 to code, negative/contract/
> scientific tests, actual commands/outcomes and remaining limits.
> Run targeted and full Foundation/Feature 002 backend tests,
> Ruff, frontend tests/typecheck/build and v1/v2 API/UI checks.
> Compare substantive IBM evaluation only if the authorized source,
> frozen protocol and trusted artifacts exist; otherwise report
> the exact pending result. Have an actual second teammate
> reproduce the declared import/scoring/report; do not substitute
> another agent or your own fresh terminal. Record human review
> only after actual participant/date/findings are supplied. If
> authoritative Phase 2 requirements remain missing, state that
> compliance is unverified. Fix confirmed gaps inside scope,
> leave new out-of-course work pending team decision, and update
> next_work.md with one concrete next step. No automatic commit/push.
