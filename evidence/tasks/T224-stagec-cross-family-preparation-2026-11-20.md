# Stage C FR-023 cross-family preparation — 2026-11-20

## Scope and provenance

This record follows the user's request to reconcile `protocol.md` and prepare the remaining comparisons **without project-data fitting**. Read `AGENTS.md`, `next_work.md`, `tasks.md`, FR-023/FR-024 in `spec.md`, `protocol.md`, T221 model choices, frozen T224 cross-family rule, T219/T228/T229 and diagnostic evidence, the complete eight-candidate and five-arm reports, and the current runner/baseline/candidate/evaluation/resource code. Prompt: current user request in this session; no generated prompt changed. Git HEAD at preparation: `aa1accac0ff90f2eb370618be15f145b3cc6bf2b`, with pre-existing local modifications preserved. No commit/push.

## T219 factual reconciliation

`protocol.md` now leads with the actual FR-021 history: original IBM-day candidate canonical `f34c51bcaeec63072a29eceae987b85ff3e8d88ac106fe51e9fc16355d5b3f5f` was not executed; first Mac revision approved canonical `90b2aaa07590f771343e30f7843078f2dbd71d26679040cdafc33a5fbe5c67cf` stopped on a transferred-manifest schema mismatch before any fit; corrected revision approved canonical `1ebac4f24aa198cfd1de70b96204676cb3fbd0cc07786296944c6ade0214f6be` passed read-only prelaunch identity/code/data/lock checks and completed all eight LightGBM candidates. The completed run and first T229 freeze remain unchanged. A separate five-arm diagnostic was approved canonical `22a4e6c8efe744de7d4d9b5304a8252f144ffa532037d7f0d8a5a83c66951b5b` and completed. The original/first/corrected/diagnostic JSON files were not rewritten, and no approval is inferred for the new comparison protocol. The current section binds source, transferred manifest and train/validation/test partition-ID hashes, feature/protocol references, exact selected model and sealed prediction hashes, and resource/identity limitations. The read-only verifier and stopped first attempt are actual mismatch stop evidence; the second preflight/run are pass evidence. T219's stated documentation/hash/stop criteria are therefore satisfied and its checkbox changed from `[ ]` to `[x]`. This is not model acceptance. Older paragraphs in `protocol.md` are explicitly historical.

There is a separate documentation discrepancy: FR-023's later explanatory sentence in `spec.md` still says the complete FR-021 protocol needs approval before fitting, though the later exact-hash approvals and execution already happened. Its requirement and methodology were **not** rewritten in this step; the current status is recorded in `protocol.md` and task/evidence handoff.

## Exact remaining FR-023 work

The fixed [T221 choices](../../specs/002-data-and-risk-scoring/t221-model-choices.json) and implementation require one **no-fit** train-prevalence constant score, two baseline fits, and five HistGradientBoosting fits on the same transferred train/validation partitions:

| Order | Candidate | Exact fit settings |
|---:|---|---|
| 1 | Prevalence constant | `train_positive / train_count`; no estimator fit or class weighting |
| 2 | Decision tree | `max_depth=5`, `min_samples_leaf=500`, class weights `{0:1, 1:train_negative/train_positive}`, seed 42 |
| 3 | L2 logistic | `C=1`, `solver=lbfgs`, `max_iter=1000`, same train-only class weights, seed 42; `StandardScaler` fit on train numeric columns only, categorical one-hot columns unscaled |
| 4 | HGB 1 | `max_iter=200`, `learning_rate=0.05`, `max_leaf_nodes=15`, `l2_regularization=0` |
| 5 | HGB 2 | `200`, `0.05`, `31`, `0` |
| 6 | HGB 3 | `300`, `0.05`, `31`, `1` |
| 7 | HGB 4 | `200`, `0.1`, `15`, `0` |
| 8 | HGB 5 | `300`, `0.1`, `31`, `1` |

All HGB fits keep `loss=log_loss`, `early_stopping=False`, `min_samples_leaf=500`, seed 42 and **train-only** sample weights `{0:1,1:train_negative/train_positive}`. Four threads are required. The previous seven nonselected LightGBM fits remain historical current-phase comparisons; the prior selected LightGBM model and the later **unweighted** diagnostic model are hash-bound existing candidates, with **no refit**. The unweighted native model SHA-256 is `3b4e4019312d60610dd0094c6697897a061611a60e7777ed7be35e133af9451c`; it arose after validation-guided numerical diagnosis. Its proposed formal eligibility needs human review. No earlier HGB result from another branch was imported. Validation has already been used for selection and diagnosis, so new validation comparisons will not independently establish generalization.

## Selection and invalid outcomes fixed before results

The new candidate embeds the existing frozen [cross-family rule](../../specs/002-data-and-risk-scoring/t224-cross-family-selection.json), canonical SHA-256 `bed962c591c71364e424b2e4544e578c69af096be89a30192f625006363f24ae`. For each candidate, choose among distinct validation score values the threshold maximizing positive-class F1; ties go to higher precision, then higher threshold. Rank by validation F1, then AP, then P@20. Score ties for P@20 use transaction ID ascending Unicode code-point order. If still tied, use the frozen family order (`prevalence_constant`, `decision_tree`, `logistic_regression`, `hist_gradient_boosting`, `lightgbm`), then earlier-declared HGB; LightGBM uses fewer leaves, higher min-child, lower rate, earlier best iteration, earlier declaration. Original winner and unweighted diagnostic have the same leaves/min-child/rate, so best iteration would resolve a remaining exact tie. The frozen rule's activation is a **separate reviewed decision** after results; this preparation does not apply it to change the selected model or approve the unweighted model for the app.

Precision, recall, ROC AUC, Brier, P@50/100, recall@k, confusion matrix, alerts, saturation/ties, runtime and memory are diagnostics, not new ranking keys. Nonfinite or out-of-[0,1] score stops the run as incomplete; there is no clipping, post-hoc model exclusion, changed threshold or replacement ranking. Saturation and large ties alone are reported and do not exclude a candidate under the frozen rule. The weighted score outputs are not calibrated probabilities. If reviewers want stability-based exclusion, that would change the rule and requires a separate decision **before** applying it.

## New pending candidate and executable support

New [comparison candidate](../../specs/002-data-and-risk-scoring/t224-cross-family-comparison.ibm-day-60-20-20.candidate.json): canonical SHA-256 **`7fd4e7349b2ef4921166d008f5c3b7e147c21a6554eae5160f33948d323bac32`**; file-byte SHA-256 `64cb6f6370b2a2670c79a462c30827da26035ec77be31fe9b521de74fd7b80ad`. Status `pending_human_review`. It binds the approved FR-021 parent, approved diagnostic, transferred train/validation manifests/files, frozen T221/T224 canonical hashes, existing weighted/unweighted LightGBM model/result files, Python 3.14.10, LightGBM 4.7.0, NumPy 2.5.5, scikit-learn 1.9.1, `uv.lock` SHA-256 `b9b1c52056c3706fd21fc1fefa9934fc1c1c8c09dd2b0f465d8d49ad25cc1ffe`, Git HEAD and full hashes of 10 executable files. Existing validation summaries are recorded compactly; their complete reports are linked by hash. New runner SHA-256 `96e1ed3613f9c43f2ec53592ef1119de68000905ebf48cd5229658a29919ee37`; new test SHA-256 `5b2ac5b76e93a0eab5cbd028bab28f16fcf4bf89bde65903aae0bc58d5a2f0ce`. All historical hashes remain historical.

`comparison_run.py` reuses the diagnostic's hash-bound train/validation-only input preparation and `resource_guard` subprocess supervisor. It persists each new candidate's model or constant state, effective parameters including train-only weight/scaler, aligned validation score CSV, full metrics/threshold/confusion, iteration count where defined, runtime, observed worker RSS and hashes. Scikit-learn models are written as hashed trusted-local pickle **research artifacts**; the runner never unpickles them, and they are not approved for app loading. A later selected scikit-learn family needs a reviewed safe serving format. The final `experiment.json` and `status.json` appear only after all eight new candidates complete; a failure retains an `.incomplete` directory and cannot masquerade as success. No test prediction is generated. The guard inherits 20 GiB initial free disk, 10 GiB reserve, 8 GiB sampled RSS, 3,600 seconds per active fit, 28,800 seconds phase and 54,000 seconds total. macOS 0.1-second sampling may miss shorter descendant RSS peaks; Windows observes only direct-worker memory. These are documented limits, not hard instantaneous guarantees.

## Commands and observed checks

1. RED: `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests/unit/test_comparison_run.py` failed collection with `ModuleNotFoundError: No module named 'fraudlens.training.comparison_run'`, the intended missing behavior.
2. GREEN focused synthetic test: same command passed `2 passed` before the later negative check was added. A later targeted run of six relevant modules under normal process access passed **61 tests**, six LightGBM deprecation warnings, no project-data fits. The synthetic comparison fitted small generated arrays only, checked candidate count/order, hashes, finite metrics and train-only scaler means; the negative case rejects NaN scores. The initial in-sandbox six-module attempt produced **8 watchdog-test failures solely because `ps` returned `Operation not permitted` before those scenarios ran**; rerunning the unchanged suite with process-monitor access passed all 61. This is an execution-environment restriction, not a code fix or successful sandbox test.
3. `PYTHONPATH=backend/src .venv/bin/python - <<'PY' ... verify_protocol(...) ... PY` passed: current code/parent/diagnostic/model/result/lock/runtime identities match. Project canonical JSON and independent `json.dumps(sort_keys=True,separators=(',', ':'),ensure_ascii=False,allow_nan=False)` hashes both produced the canonical SHA-256 above.
4. `.venv/bin/ruff check backend/src/fraudlens/training/comparison_run.py backend/tests/unit/test_comparison_run.py` passed. `git diff --check` passed. Neither command is a training run.

The exact future command, **text only, not executed**:

```sh
PYTHONPATH=backend/src .venv/bin/python -m fraudlens.training.comparison_run \
  --features data/processed/t219-ibm-day-60-20-20-v1 \
  --labels data/processed/t219-ibm-day-60-20-20-labels-v1 \
  --protocol specs/002-data-and-risk-scoring/t224-cross-family-comparison.ibm-day-60-20-20.candidate.json \
  --protocol-sha256 7fd4e7349b2ef4921166d008f5c3b7e147c21a6554eae5160f33948d323bac32 \
  --output data/eval/ibm-day-cross-family-comparison-001 \
  --root . --n-jobs 4
```

Before any authorized run, recheck exact protocol, current implementation, lock/runtime and input hashes; ensure output and `.incomplete` sibling are absent. After complete results, human reviewers decide whether to activate the frozen cross-family rule and whether the unweighted diagnostic model is formally eligible. Only then can a new selected-model freeze bind model bytes, threshold, feature vocabulary/order, runtime and validation metrics in a trusted manifest. A separate authorized label-free export would freeze new test predictions and their hash. T230 requires its own authorization and exact matching snapshot/prediction identity; this Mac currently lacks the original T210 accepted snapshot. Application activation is later still. No project fit, new test prediction, test/showcase label access, T230 or app activation occurred here.
