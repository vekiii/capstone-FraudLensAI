# Original development request: T221 Phase 1 model training

Date: 2026-11-20 Europe/Budapest

Repo: capstone-FraudLensAI, branch `feature/002-clean-start` (do not push).

Goal: replace the FixtureScorer path with models trained by us on IBM AML HI-Small using the local pinned 5,078,345-row snapshot. No official pretrained weights exist; do not search for or integrate any.

Frozen: `hi-small-temporal-v1` and chronological partitions in `specs/002-data-and-risk-scoring/protocol.md`; showcase is diagnostic only and never used for fitting, tuning, thresholds or model selection, nor described as an unbiased holdout; T219 gate, audit evidence and hashes; Scorer interface in `backend/src/fraudlens/scoring.py`.

Read-only references pinned in `third_party/PINNED_COMMITS.txt`: `third_party/Multi-GNN` optional reference; `third_party/TabGT` out of scope and must not be run; `docs/references/` AMLworld/Multi-GNN papers. Never modify `third_party`; never commit data, checkpoints or logs.

Hardware: CPU only, no GPU/CUDA. Maximum 60 minutes per fit. Use `n_jobs` equal to physical cores minus one. Stop and report if a step exceeds its limit; do not silently subsample.

Phase 1 only, stop after it: read the handoff, protocol, Scorer, feature and partition code and summarize fixed decisions; propose the LightGBM model and bounded grid (`num_leaves` 31/63, learning rate .05/.1, `min_child_samples` 50/200, up to 1000 estimators with validation early stopping, training-prevalence `scale_pos_weight`, fixed seed); use validation only for tuning; report minority F1, PR-AUC, precision and recall; select threshold maximizing validation minority F1 and freeze it before test/showcase; observe CPU/time limits; optionally run a separately reported CPU Multi-GNN reference only on documented subsample or time-limited, skip if it cannot finish; report development, validation, test and showcase sizes/prevalence; update the T219 verifier to check the protocol hash without weakening checks; run tests, Ruff and `git diff --check`; then stop and report diff, questions, risks and approvals needed. Do not fit until the user replies `protocol approved: <hash>`.

Phase 2, only after approval: create resumable one-command `scripts/train_lightgbm.py`; log seed, git SHA, protocol/data hashes, runtime and CPU count; save artifacts only under ignored `artifacts/`; evaluate test once after freezing predictions, showcase diagnostic only; do not retune from test/showcase. Optional Multi-GNN uses the stated flags and is reported separately; never run TabGT.

Phase 3, after training: add model manifest with model/version/source/protocol/data hashes/features/threshold/metrics/artifact path/hash; implement `LightGBMScorer` behind the unchanged Scorer interface with artifact-hash verification and point-in-time features; retain FixtureScorer for tests and select scorer by config; add schema/leakage/manifest tests; update handoff and README reproduction steps.

Rules: every number must come from a saved run log; do not invent or round results. Small commits, one concern each. Do not push unless later requested. Ask before changing anything marked frozen. Report failures/gaps. Results below published baselines are acceptable if documented.
