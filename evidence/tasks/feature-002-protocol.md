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
