# Feature 002 validation hardening — 2026-11-15

## Scope and baseline

Branch: `model-implementations`, starting HEAD `496025e`. The working tree already contained T065 documentation/scripts, a protocol draft, and an audit draft. Those files were preserved. Reviewed root `AGENTS.md`, `next_work.md`, Feature 002 `contracts/data-and-scoring.md`, `contracts/api.md`, relevant specification clauses, source modules, existing unit/integration tests, and the initial Git status/diff before editing. Tests use authored CSV rows, existing synthetic helpers, and temporary SQLite run stores; no IBM data, model fit, private holdout labels, frozen policy change, shared activation, or frontend change occurred.

The pre-existing suites already cover many requested boundaries: exact supported money maximum and zero, negative/NaN/Infinity/exponent/excess decimals and invalid clock/currency/format, duplicate or altered headers, label separation, half-open history with ties and permutations, model/fixture score bounds, artifact identity checks, latest-100 tie order, zero alerts, and basic 422/409/503 responses. The new cases below target cross-boundary paths or matrix gaps rather than duplicating those exact assertions.

## Added parametrized cases and observed results

All outcomes below are from the final targeted GREEN command, except the two confirmed RED defects identified separately. One table row is one parametrized test function; variants list each collected case.

| Case | Input and expected behavior | Actual final behavior |
|---|---|---|
| Received-amount import policy (7 variants) | Accept `0`, `9999999999999.999999`; reject `-0`, `NaN`, `Infinity`, `1e2`, `0.0000001` as event-invalid, with accounting intact. | All 7 matched. |
| Ineligible-label replay (3) | Blank, `2`, `unknown` labels leave an otherwise valid prior event in strict-past history, but label value/status stay out of feature keys. | All 3 matched; next event sees one prior same-currency payment of `10.20`, with no label predictor. |
| Window edges (3) | A prior fact at exactly `t−24h` counts once; `t−24h−1m` and a same-time peer do not count. | Counts `1`, `0`, `0` as expected. |
| Permuted tied events (2) | Two unsorted input permutations produce the same prior-only peer features and target digest. | Both passed; peer count is 1 and replay digest stable. |
| Coverage interval edges (3) | Missing interval overlapping window gives incomplete/null; interval ending exactly at lower bound gives full/zero; unavailable coverage gives unavailable/null. | All 3 matched and scoreability reflects state. |
| Malformed canonical received amount (4) | Reject `-1`, `NaN`, `Infinity`, `bad` before appending to receiver history, with controlled `ValueError`. | RED: 3 were accepted; `bad` raised `decimal.InvalidOperation` during history mutation. GREEN: all 4 rejected before history update. |
| Run score/threshold matrix (5) | Scores `0`, `1`, threshold equality `0.5`, score just below threshold, and `no_alert` produce alert counts `1`, `1`, `1`, `0`, `0`. | All 5 matched in completed temporary SQLite runs. |
| Rejected run scores (4) | `−0.01`, `1.01`, NaN, Infinity must fail staging, leave run incomplete, and prevent activation. | RED: NaN raised uncontrolled `decimal.InvalidOperation`; other 3 rejected. GREEN: all 4 controlled `ValueError`; no run activated. |
| Artifact mismatch before load (4) | Wrong manifest SHA, dataset version, protocol SHA, or feature version must reject before `joblib.load`. | All 4 rejected with zero deserialization calls. |
| Dataset detail errors (4) | Malformed case ID and missing snapshot -> 422; old snapshot -> 409; unknown well-formed case -> 404. | All 4 status codes matched on a zero-alert active run. |
| Incomplete run publication (2) | Staging runs with expected count 0 or 1 cannot activate; dataset API has no active run and returns 503. | Both matched. |
| Fixture/dataset isolation (2) | Fixture mode returns three v1 cases without a version discriminator; dataset mode with no store returns 503 and does not fall back. | Both matched. An initial test draft incorrectly expected a v1 `contract_version`; corrected to match the reviewed v1 contract without changing production code. |

## Confirmed defects, causes, and minimal fixes

1. **Medium — replay accepted malformed received amounts from a constructed canonical event.** `feature_history._event_fact` checked only `paid_amount`, while `update()` summed `received_amount`. Negative/nonfinite amounts could corrupt receiver sums; malformed text raised a late decimal exception after history counters had begun mutating. Added symmetric finite/nonnegative Decimal validation for both money fields at the existing event boundary. This is defense in depth: the CSV importer already rejects these values before constructing canonical events. Changed `backend/src/fraudlens/feature_history.py`.
2. **Low — nonfinite staged score could raise uncontrolled decimal exception.** `_public_detail` checked the JSON schema and reconstructed explanations but did not explicitly guard a NaN score. During reconstruction `Decimal('NaN')` raised `decimal.InvalidOperation`; rollback still prevented publication. Added a finite `[0,1]` check before reconstruction. Changed `backend/src/fraudlens/data_store.py`.

Test additions: `backend/tests/unit/test_validation_hardening.py` (12 parametrized functions, 43 synthetic cases). Prompt record: `prompts/development/002-validation-hardening-2026-11-15.md`. This evidence and `next_work.md` are the documentation changes.

## Commands and execution record

Commands were run from the repository root in PowerShell; `PYTHONPATH='backend/src;.'` was set before each pytest command. The sandbox could not use the user profile's default pytest temp directory, so controlled reruns set `--basetemp` under ignored `data/processed/` and disabled pytest's cache provider.

| Phase | Exact command | Exit and result |
|---|---|---|
| Initial RED attempt | `$env:PYTHONPATH='backend/src;.'; .\.venv\Scripts\python.exe -m pytest -q backend/tests/unit/test_validation_hardening.py` | Exit 1: 15 passed, 7 failed, 17 setup errors. The setup errors were `WinError 5` at the default user-profile pytest temp directory; three test failures were a test-side float-vs-Decimal assertion. This attempt is not the clean defect count. |
| Controlled RED | `$env:PYTHONPATH='backend/src;.'; .\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp data/processed/.pytest-validation backend/tests/unit/test_validation_hardening.py --tb=line` | Exit 1: 34 passed, 5 failed. Four replay failures and one NaN run-stage failure reproduced the defects above. |
| First GREEN | Same controlled targeted command | Exit 0: 39 passed, 1 third-party deprecation warning. |
| Initial broader regression | `$env:PYTHONPATH='backend/src;.'; .\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp data/processed/.pytest-regression backend/tests --ignore=backend/tests/unit/test_pretrained_loader.py --ignore=backend/tests/unit/test_pretrained_ibm_inference.py --tb=line` | Exit 1: 720 passed, 1 skipped, 5 failed, 4 errors. Eight artifact-dependent cases lacked the original tree/boosted manifests; one existing symlink security test failed with Windows `WinError 1314` privilege. No new failure implicated the patch. |
| Ruff during development | `.\.venv\Scripts\ruff.exe check backend/src/fraudlens/feature_history.py backend/src/fraudlens/data_store.py backend/tests/unit/test_validation_hardening.py` | First exit 1 for imported fixture alias style; test-only fix, then exit 0. |
| Added-case test draft | Controlled targeted command above | Exit 1: 42 passed, 1 failed. The new fixture-isolation assertion incorrectly expected a v1 `contract_version`; corrected the test to match the approved fixture v1 shape. |
| Final targeted GREEN | Controlled targeted command above | Exit 0: 43 passed, 1 third-party Starlette/httpx deprecation warning. The four added fixture/publication cases passed. |
| Final applicable regression | `$env:PYTHONPATH='backend/src;.'; .\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp data/processed/.pytest-regression-clean backend/tests --ignore=backend/tests/unit/test_pretrained_loader.py --ignore=backend/tests/unit/test_pretrained_ibm_inference.py --ignore=backend/tests/unit/test_boosted_integration.py --ignore=backend/tests/unit/test_model_scoring.py --deselect=backend/tests/unit/test_model_artifacts.py::test_escaped_path_upload_and_incompatible_manifest_reject --tb=line` | Exit 0: 722 passed, 1 skipped, 1 deselected, 1 third-party warning. |
| Backend Ruff | `.\.venv\Scripts\ruff.exe check backend/src backend/tests` | Final exit 0, all checks passed. |
| Whitespace | `git diff --check` | Final exit 0, no whitespace errors in tracked changes. |

## Limits and follow-up

The two documented pretrained proposal RED suites were intentionally excluded. Two existing artifact-dependent suites need the unavailable original saved models; the one symlink case needs a Windows symlink privilege. These were not treated as application failures. No real-data or independent model metric was measured. Frontend checks were not run because no frontend file or public contract changed. One next step: obtain the approved original artifacts and rerun the deferred artifact-dependent tests (and symlink case on a capable host) before using the model integration as release evidence.
