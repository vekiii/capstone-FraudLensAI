# Feature 002 T026: chronological protocol RED tests

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
