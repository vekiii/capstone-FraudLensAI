# ML/data + case investigation technical agreement

**Status:** working technical agreement for joint review; the counterpart's identity and explicit concurrence have not been supplied in this session. The four decisions below are proposed from the current repository contracts and the request. Record any disagreement in the decision column and update this file after the ML/data review.

**Date:** 2026-11-16
**Reviewed repository SHA:** `9454bfc42bc6d954e916c777c30cac499df1a94d` (`HEAD` at review time)
**Participants:** Requester / repository review: not named in this record; ML/data counterpart: not supplied. Do not treat this draft as evidence that another person reviewed or approved it.

## Decisions and review notes

| # | Topic | Proposed technical decision | Review / decision |
|---|---|---|---|
| 1 | Case, dataset, and run identity | Keep the identifiers distinct and propagate them as separate fields. The case is `case_id` (`C` + 32 lowercase hex); transaction identity is `transaction_id` (`D` + 32 lowercase hex). A dataset is `dataset_version` (`dv_` + 64 lowercase hex), derived from source, mapping, and time-policy digests. Scoring request/response carries `transaction_id`, `dataset_version`, and `run_id`; `run_id` identifies one execution and is not a substitute for dataset or case identity. The case list/detail is located by `case_id`; dataset detail is pinned to the run using `snapshot`/`snapshot_ref` and the response echoes dataset and run IDs. Reject mismatched identity across request, snapshot, run, and response; never infer one ID from another. | **Proposed, consistent with current Feature 002 contracts.** ML/data counterpart to confirm the identifiers remain stable through the investigation handoff and whether investigation needs `transaction_id` alongside `case_id` (recommended: yes). |
| 2 | Amounts, currencies, and time | Preserve paid and received amount text/Decimal value and their independent source currency strings. Do not convert currencies, round, normalize to ISO, or coerce amount text through binary float. Preserve original timestamp text and canonical event time; comparisons use timezone-aware UTC instants under the declared time policy, with unknown source timezone caveat retained. API/UI display both paid and received amount/currency as supplied. | **Proposed, supported by current importer/scoring contracts.** For investigation evidence, pass exact values and an explicit timestamp/basis; do not fabricate FX values or claim actual UTC where policy only assumes it. Review any serializer boundary for lossless decimal and timestamp precision. |
| 3 | `boosted_sequential_probability` | This is the explanation method for the exploratory boosted scorer, not a separate scoring algorithm or calibrated/causal explanation. It sequentially changes each input in the fixed feature order from a deterministic baseline (train-fitted numeric medians and unknown-category baseline), records the change in positive-class probability, and reports up to three largest absolute changes. Base + contributions + remainder reconstruct the scorer's returned uncalibrated probability within `1e-8`. The contributions are order/baseline-dependent local model attribution, not SHAP values, causal effects, or independently calibrated probabilities. | **Meaning is documented in the Feature 002 contract and implementation.** Candidate remains research-only pending independent acceptance. ML/data reviewer to confirm these labels and user-facing explanation text; do not present the candidate as an approved active model. |
| 4 | Account history for investigation | Investigation history is a separate evidence query keyed by the exact pair `(bank, account)`, never account string alone. For a focal event at `t`, include only events with `t - 7 days <= event_time < t`; exclude same-time and future events. Retain exact amount/currency/time and direction, and state coverage bounds/count so missing history is not represented as â€œno activity.â€ Exclude private/evaluation labels and label-derived fields at source/query/DTO boundaries; no label should be available to the investigation model or analyst evidence payload. The existing `history-v1` scoring features are 24-hour features: do not stretch or relabel them as seven-day investigation history. Implement seven-day retrieval as a separately named investigation evidence contract/query. | **User-requested target; not yet implemented or jointly accepted.** Data owner to confirm bank/account fields, interval boundary, which event fields/directions are returned, coverage semantics, and prove label exclusion. Default proposal above uses a strict-prior half-open interval `[t-7d, t)`. |

## Interface notes

- Handoff should carry `case_id`, `transaction_id`, `dataset_version`, `run_id`, `event_time_utc`, exact amounts/currencies, and a declared time basis. The consumer validates that the case and transaction agree with the selected run detail.
- Account-history access should accept the bank and account pair plus focal `event_time`; callers must not supply an arbitrary future `as_of`. The service derives the strict-prior seven-day interval from the focal event and returns provenance/coverage, not labels.
- Private evaluation labels are held separately from operational event facts in Feature 002. Keep that separation through serialization, tool schemas, retrieval, prompts, logs, and evidence exports; do not rely only on hiding label fields in the UI.
- The seven-day investigation contract is an additional requested investigation boundary. It does not alter Feature 002 `history-v1`'s current 24-hour scoring contract or authorize out-of-course scope by itself. If it requires a new feature/specification or changes an agreed contract, route it through the project's scope process before implementation.

## Source files reviewed

- [Feature 002 scoring contract](../../specs/002-data-and-risk-scoring/contracts/data-and-scoring.md)
- [Feature 002 data model](../../specs/002-data-and-risk-scoring/data-model.md)
- [Dataset scoring request/response validation](../../backend/src/fraudlens/data_contracts.py)
- [Point-in-time history feature implementation](../../backend/src/fraudlens/feature_history.py)
- [Boosted scorer and explanation implementation](../../backend/src/fraudlens/model_scoring.py) and [explanation builder](../../backend/src/fraudlens/explanations.py)

## Review record

This document records a repository-based draft, not a completed pair review. Fill in both participants' names, the review date, the exact SHA each person inspected, and per-item decision/remarks after the joint technical discussion. Any change to the reviewed commit requires a new SHA entry and review of affected decisions. Current working tree also has unrelated untracked drafts; they were not included in the reviewed SHA and were left untouched.
