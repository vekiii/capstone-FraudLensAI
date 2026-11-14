# Feature 002 T026: chronological protocol RED tests

## T029 real history-v1 freeze — 2026-11-14 Europe/Belgrade

Original request: [Phase 5 T029–T036](../../prompts/development/002-phase-5-t029-t036-2026-11-14.md). Branch `model-implementations`; fetched `origin` and switched cleanly to tracking HEAD `fb32b8c8467bb5cffe6b4cbc57730b484af1b1db`. The existing tree experiment source/evidence was retained. Its ignored `artifacts/trees-*/manifest.json` was absent in this checkout; no notebook binary was reused. `uv sync --locked --group dev` initially exited 2 because sandbox DNS could not reach PyPI, then succeeded with network permission (exit 0; NumPy 2.5.4, SciPy 1.18.1, scikit-learn 1.9.1). The original 34 temporal/tree tests passed, exit 0.

The existing `build_split_manifest` stores and sorts every Python snapshot and ID, so it was not used for the 5.08 million row run. New `evaluation_store.audit_sqlite_split` opens the existing 12,443,103,232-byte `data/processed/feature-002-ibm-v8-rules-work.sqlite` with SQLite `mode=ro` and `query_only=ON`. It groups timestamps with SQLite file-backed temporary sorting, holds only timestamp counts in Python, then streams ID/coverage/label rows. Boundary choice reads only scoreable timestamp counts; the later label join computes class counts. A controlled parity test compares boundaries, exact ID membership and class counts against T027's in-memory implementation and passes. A first draft used 17/10 for the second boundary and was rejected by that parity test; 17/20 is the corrected and frozen rule.

Read-only `PRAGMA quick_check` returned `ok` (exit 0). DatasetVersion `dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802` and `history-v1` feature build both have `complete` status; the source/provenance digests reproduce the version ID. There are **5,078,345** source records and snapshots, **0** rejected, **1,114,921** warm-up records before 2022-09-02 00:00 UTC, **0** later coverage exclusions, and **3,963,424** scoreable records across 13,578 scoreable timestamp groups. All 5,078,345 private labels are eligible (5,177 positives, 5,073,168 negatives). The read-only audit itself finished in 48.679 seconds with measured macOS `ru_maxrss` **45,350,912 bytes** (exit 0); the first `/usr/bin/time -l` wrapper exited 1 due unavailable `sysctl kern.clockrate`, although its Python audit printed a result. It is not used as the accepted memory measure. SQLite temporary disk peak was not measured.

The frozen 70/15/15 split uses whole timestamps and earlier-boundary distance ties:

| Role | Inclusive time range UTC | Rows | Positive | Negative | Ordered IDs SHA-256 |
|---|---|---:|---:|---:|---|
| Train | 2022-09-02 00:00 through 2022-09-08 07:21 | 2,774,357 | 2,822 | 2,771,535 | `e3682ddb990e5ba1c36c65a1b88e9e9ac6796253e612eb818869cd170febef7a` |
| Validation | 2022-09-08 07:22 through 2022-09-09 09:31 | 594,715 | 588 | 594,127 | `e0f845095364e061ea505678530713a13c474a3f49fb1a981e53b6ad74e2be8c` |
| Test | 2022-09-09 09:32 through 2022-09-18 16:18 | 594,352 | 1,445 | 592,907 | `e0187baa4749c5cf11b19533bd5df8ac9a092466de718b703f5b48b5436c7575` |

Exact ordered IDs remain reproducible from the immutable source with `SELECT transaction_id FROM feature_snapshots WHERE version=? AND feature_version='history-v1' AND scoreable=1 AND event_time [within frozen role bounds] ORDER BY event_time,transaction_id`; the digest in the tracked protocol verifies each stream without committing millions of IDs. Every role has both classes, and outer validation/test each exceed 20 positives. The original 60/20/20 notebook split includes warm-up and ends old train at 2022-09-06 13:35, old validation at 2022-09-08 16:12. Overlap with new train is 1,931,940 old train / 842,417 old validation; new validation is 173,503 old validation / 421,212 old test; **all 594,352 new test rows are in the old test period**. The notebook already published test metrics. This test period is exposed, and no independent confirmatory performance claim is permitted.

The tracked [frozen protocol](../../evals/protocols/feature_002_v1.json) fixes candidate order (two L2 logistic and four depth/leaf trees), seed 42, six fits, train-only transforms, validation AP then P@20 then grid order, AP tie 1e-6, inclusive distinct-score F0.5 thresholds with no-alert, K=20, no calibration/AutoML, 30 minutes per fit / 3 hours total, 3 GiB process peak and 4 GiB scratch, numeric tolerances and label-free five-example sampling. Initial protocol SHA-256 was `919587580575234438612a2b07cc0489bb4485b03f6029c3ccdea432160d17d1` with full train. The first full-train candidate attempt loaded 2,774,357 train and 594,715 validation rows (RSS 617,431,040 bytes at load) but stopped at a frozen fit resource ceiling before any candidate validation metric; the first runner did not log which ceiling value was exceeded, so that narrower cause is unknown. Before the next fit, amendment 1 fixed train-only `SHA256(transaction_id)` first eight bytes modulo 4 equal zero. It retains full feature history, all validation/test rows and boundaries. The resulting train view has **693,230 rows, 719 positives and 692,511 negatives**; eligibility was rechecked. Final protocol SHA-256 is `01fff67d44895b5a1aa6de6dfbb6c6c107f01c041ba7c972bf42210e2b316068`. No boundary was moved to improve metrics.

The real `freeze-protocol --store ... --dataset-version ... --config evals/protocols/feature_002_v1.json` CLI re-audited the source and returned `status=frozen`, `eligible=true`, matching final hash (exit 0). No import, replay, database copy or write, actual test prediction/metric join, push or merge occurred.

- Date: 2026-11-13, Europe/Budapest (about 16:04).
- Branch and starting HEAD: `model-implementations`, `27ac7d49e3d638717c752dce225216d291bf9e87`.
- Original request: the user's 2026-11-13 instruction to implement **T026 only**, collect and execute synthetic RED tests, leave production evaluation and IBM data untouched, then commit the test/evidence handoff.
- Authority: `specs/002-data-and-risk-scoring/tasks.md` T026; `spec.md` FR-010–013 and SC-005; `plan.md` split flow; `research.md` Decision 9; `data-model.md` SplitManifest/EvaluationProtocol; `contracts/data-and-scoring.md` evaluation and history contracts.
- Runtime: repository `.venv` Python 3.14.10, pytest 9.2.0. The resolved lockfile was not changed. Feature selection: `SPECIFY_FEATURE_DIRECTORY=specs/002-data-and-risk-scoring` for the initial collection/execution session; later direct pytest commands used the same explicit test path.
- Fixture: 162 authored canonical events and `history-v1` snapshots, with 2 warm-up rows and 160 scoreable rows. The intended whole-timestamp partition is 110/26/24 because the 70% target (112) is equally distant from boundaries at 110 and 114; the earlier boundary wins. Train has 3 positive/107 negative, validation 20/6, test 20/4. Private labels are separate objects. These are synthetic counts, not IBM observations.

## Test matrix

| Cases | Intended assertion |
|---:|---|
| 1 passing fixture check | Existing replay produces label-free, as-of snapshots; warm-up is not scoreable and same-time peers share earlier history. |
| 1 | Nearest 70/15/15 whole-timestamp split; exact IDs, warm-up exclusions and strict chronology. |
| 1 | Reversing input order and changing private label eligibility cannot move partition IDs. |
| 1 | Exact event-valid/scoreable, eligible/ineligible, class and natural prevalence counts. |
| 3 | Removing a partition's positive class produces explicit ineligibility and blocks fit. |
| 2 | Nineteen positives in validation or test fail the 20-positive guardrail without changing membership. |
| 3 | Removing a partition's negative class produces explicit ineligibility. |
| 5 | Wrong dataset version/source hash, future as-of, unknown coverage state and staged dataset fail closed. |
| 1 | Known incomplete coverage is excluded from benchmark scoring while event-valid facts remain accounted for. |
| 1 | No scoreable rows gives an explicit insufficient-data result and no fit. |
| 1 | A later event and private label change do not alter earlier replayed feature values or digest. |

## Commands and observed results

Working directory: repository root.

| Command | Exit | Observed |
|---|---:|---|
| `uv run --locked pytest --collect-only -q backend/tests/unit/test_evaluation_protocol.py` | 1 | `uv` was not recognized in this shell. Environment failure; **not** RED evidence. |
| `.\.venv\Scripts\python.exe -m pytest --collect-only -q -p no:cacheprovider backend/tests/unit/test_evaluation_protocol.py` | 0 | **20 tests collected**; no collection/import error. |
| `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider backend/tests/unit/test_evaluation_protocol.py --tb=no` | 1 | **19 failed, 1 passed**. All 19 protocol cases call the absent evaluator and fail in the test body with `Failed: T027 missing behavior: fraudlens.evaluation.build_split_manifest` (the same failure text was observed in the preceding `--tb=line` run before the final case expansion). The one replay fixture check passes. |
| `.\.venv\Scripts\ruff.exe check backend/tests/unit/test_evaluation_protocol.py` | 0 | `All checks passed!` |
| `git diff --check` | 0 | No whitespace errors. |

## Contract for T027 and limits

The tests propose `build_split_manifest(dataset_version, snapshots, labels, source_start, expected_source_sha256)` returning immutable `SplitManifest` state with `partitions`, exclusions, counts, eligibility, ineligibility reasons and `fit_allowed`. `backend/src/fraudlens/evaluation.py` does not yet exist. T027 may refine naming only by updating the tests and evidence together while preserving all behavioral assertions.

The RED result proves valid collection and the intended missing evaluator boundary. The downstream split, count, eligibility and provenance assertions have **not yet run past that boundary** and are not claimed to pass. No production evaluator, model, fit, metrics, real dataset or holdout was accessed. No full backend suite was run because this is an intentionally failing RED milestone. Human review and independent reproduction remain pending. The pre-existing uncommitted contribution-report edit was preserved outside this task.

Next step: **T027 GREEN** — implement the immutable split and eligibility behavior, then execute these cases through their assertions and record actual results here.

## T027 GREEN implementation — 2026-11-13

- Original request: the user's 2026-11-13 instruction to implement **T027 only** on `model-implementations`, run T026 and relevant backend regression checks, and commit the verified slice without pushing.
- Starting HEAD: `fe310c1a7213655b47cc2ffb22554fc39b4e2acf`.
- Implementation: `backend/src/fraudlens/evaluation.py` adds frozen `EvaluationProtocol`, `Partition` and `SplitManifest` objects with read-only role/partition mappings. A complete dataset's source, mapping and time-policy digests must derive its version ID; snapshots must match that version, `history-v1`, source start, as-of time, supported schema and coverage state. Exact scoreable membership and 70/15/15 boundaries are chosen by whole timestamp before private labels are joined. Label counts, natural prevalence, class coverage and the 20-positive outer guardrail then yield explicit eligibility/reasons. The manifest records warm-up/coverage exclusions, role times and IDs, deterministic membership/protocol hashes and an undisclosed holdout state. No fit/selection/metrics routine is present.
- T026 assertions were retained. Five focused cases were added for changed mapping provenance, deterministic immutable state, inconsistent/overlapping manifests (including digest tampering) and mismatched event identity. The suite now contains 25 cases.
- Synthetic fixture policy: 160 scoreable events, 2 warm-up events, four identical-timestamp events around the 70% boundary; expected split 110/26/24. No real IBM rows or holdout labels were loaded.

### Commands and observed results

Working directory: repository root; Feature 002 selected with `SPECIFY_FEATURE_DIRECTORY=specs/002-data-and-risk-scoring` for the focused and full pytest sessions.

| Command | Exit | Observed |
|---|---:|---|
| `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider backend/tests/unit/test_evaluation_protocol.py --tb=short` | 0 | **25 passed** in 0.28s after final changes. |
| `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider backend/tests/unit/test_evaluation_protocol.py backend/tests/unit/test_feature_history.py backend/tests/contracts/test_data_scoring.py --tb=short` | 0 | **78 passed** in 0.46s after final changes. |
| `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider backend/tests --tb=short` | 1 | **594 passed, 6 failed, 1 existing Starlette/httpx warning** in 18.64s. The six existing `backend/tests/integration/test_data_store.py` CLI cases stop at the mapping raw-byte SHA assertion before their test action. All 25 protocol cases passed in this run. |
| `.\.venv\Scripts\ruff.exe check backend/src backend/tests` | 0 | `All checks passed!` after final changes. |
| `git diff --check` | 0 | No whitespace errors; Git printed a line-ending conversion warning for the edited test file. |

The six full-suite failures are unrelated to the new evaluator: `data/mappings/ibm_hi_small_v1.json` has no Git diff, but its on-disk SHA-256 is `9a87e1ddaad2c6825d76111eae4fdcf54e2bec5ed0c7c25685b1ea8a0dd42ae1` while the tracked HEAD blob is `a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57`. The working file has 292 CRLF pairs; HEAD has none. Replacing CRLF with LF in memory makes the bytes identical. System Git has `core.autocrlf=true`. The pinned authorization hash matches the tracked LF bytes, so these six integration checks cannot pass against this checkout's CRLF working copy. The mapping was not edited during T027. This needs a separate checkout/line-ending correction and verification before claiming a full green backend suite.

### Limits and continuation

T027 proves controlled split/eligibility behavior, not real benchmark eligibility or model performance. `frozen_at` remains unset because the real benchmark protocol is frozen at T029; `holdout_disclosed` is false and no disclosure method is implemented here. The evaluator receives prebuilt snapshots and validates their structural/provenance fields, but it cannot independently recompute a feature-input digest without canonical events. The full-source membership/row-accounting gate also remains for the actual protocol. Human review and independent reproduction are pending. The pre-existing uncommitted contribution-report edit remains untouched.

Next task: **T028 resource/dependency pilot**, with the mapping line-ending issue tracked separately.
