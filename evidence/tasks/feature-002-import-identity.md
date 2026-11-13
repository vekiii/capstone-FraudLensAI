# Feature 002 import identity — preparatory RED evidence

- Date/time and timezone: 2026-11-13, Europe/Belgrade.
- Branch/HEAD: `002-data-and-risk-scoring`, `182d0b290c8819e602fc5d77e8df8e904228b032`; tests are uncommitted working files.
- Request: [original prompt](../../prompts/development/002-t007-t008-fixes-and-t009-t011-red-request-2026-11-13.md).
- Requirements/tasks: [Feature 002 T009–T011](../../specs/002-data-and-risk-scoring/tasks.md#phase-3-us1--import-a-trustworthy-traceable-dataset-p1-first-increment), FR-001–004, FR-009, SC-001; [current T007/T008 technical check](feature-002-t007-t008-team-review-2026-11-13.md#codex-correction-and-preparatory-red-verification--2026-11-13).
- Status: **preparatory RED only**, explicitly requested while the T007/T008 final human review gate remains open. T009–T011 checkboxes remain open; T012–T016 GREEN, actual IBM import, activation and SC-001 acceptance were not run. Mapping `import_allowed=false`.

## Authored synthetic cases

| File | Cases prepared | Current intended failure |
|---|---|---|
| [`backend/tests/unit/test_data_import.py`](../../backend/tests/unit/test_data_import.py) | Exact sender/receiver bank and same account value, separate Decimal paid/received precision, UTC+00 assumed coordinate, `Euro` valid/`EUR` invalid, blank/invalid private label, rejection/counting before a quoted multiline record, unsupported scale/negative/nonfinite/overflow/missing currency/timezone, truncated UTF-8. | Missing T013 `parse_canonical_source` behavior. |
| [`backend/tests/unit/test_data_identity.py`](../../backend/tests/unit/test_data_identity.py) | Pre-filter one-based ordinal, distinct equal rows, separate N/F inputs, reviewed D/C vector, label-only `dv_` change with stable D/C, pinned raw SHA-256 rejection after a label edit. | Missing T013 identity/version/source-binding behavior. |
| [`backend/tests/integration/test_data_store.py`](../../backend/tests/integration/test_data_store.py) | Interrupted **new** staged version leaves an older complete active version; reimport of the **same already-complete** version is idempotent; incomplete row reconciliation cannot complete. | Missing T014 SQLite `data_store` repository. |

These tests specify the intended T013/T014 interfaces; implementation may refine their call shape while preserving the behavioral assertions. Other T009–T011 task-matrix cases (all T004 malformed/header variants, deliberate digest/fact collisions, schema-version mismatch and private role access) still need RED coverage before calling those tasks complete. Synthetic fixtures are not IBM import or model evaluation.

## Commands and observed results

All commands executed at repository root with existing locked `.venv`; `PYTHONPATH=backend/src` as shown. Frontend command ran in `frontend/`.

| Command | Exit | Actual output/reason |
|---|---:|---|
| `PYTHONPATH=backend/src .venv/bin/python -m pytest --collect-only -q backend/tests/unit/test_data_import.py backend/tests/unit/test_data_identity.py backend/tests/integration/test_data_store.py` | 0 | 20 tests collected in 0.01s; no collection/import error. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q --tb=no backend/tests/unit/test_data_import.py backend/tests/unit/test_data_identity.py backend/tests/integration/test_data_store.py` | 1 | **20 failed in 0.03s** in test bodies. T009: 11 failures because `parse_canonical_source` is absent; T010: 4 at missing D/C derivation, 1 at missing standalone version derivation and 1 at missing pinned source digest verification; T011: 3 because `fraudlens.data_store` is absent. These are expected missing behaviors, not environment/collection failures. Earlier 18- and 19-failure runs preceded two added identity cases; the 20-test run is final. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q --tb=short backend/tests/unit/test_data_identity.py::test_label_only_change_has_distinct_dataset_version_in_isolation` | 1 | 1 failed in 0.01s at `T013 missing: version from full source/mapping/policy digests`; confirms isolated version test reaches its intended missing behavior. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests --ignore=backend/tests/unit/test_data_import.py --ignore=backend/tests/unit/test_data_identity.py --ignore=backend/tests/integration/test_data_store.py` | 0 | Existing backend regression: 380 passed, 1 preexisting Starlette/httpx warning, 0.62s. RED files excluded intentionally. |
| `npm test -- --run` (`cwd frontend`) | 0 | 151 passed in 5 files. |
| `.venv/bin/python -m ruff check backend/src backend/tests evidence/tasks/feature-002-team-review-check.py` | 0 | All checks passed. |

## Continuation and review gate

The two Codex technical findings on the mapping N/F description and exact v2 dataset-version syntax were corrected and checked. Actual producing/affected-consumer final-byte review remains pending for T007/T008; the user explicitly permitted this RED preparation before formal gate closure. No human signature, approval, or component-specific finding is inferred. One concrete next step: obtain and record that real final-diff review, then extend T009–T011 RED coverage to the remaining task cases before T012–T016 GREEN implementation.

## Completed T009–T011 RED matrix — 2026-11-13

[Original continuation prompt](../../prompts/development/002-t009-t011-complete-red-2026-11-13.md). Branch `002-data-and-risk-scoring`, HEAD `182d0b290c8819e602fc5d77e8df8e904228b032`; the three test files are uncommitted working files. The previously recorded 20 tests were retained. One existing multiline fixture was corrected from unsupported `Payment Format=Wire\nTransfer` to a multiline nonempty account, preserving the test's CSV-record purpose and the reviewed payment-format allowlist. The new private-label cases assert the contracted supervised-ineligible status for nonbinary tokens without inventing an unsupported/invalid split. No application code, mapping, contract or real IBM data was changed in this RED continuation.

| Task criterion | RED tests in the retained/expanded file |
|---|---|
| T009 exact directional facts, bank-qualified accounts, paid/received money, supported scale/zero/max, raw/UTC assumed time | `test_direction_exact_money_time_and_missing_private_label`, `test_supported_money_boundaries_preserve_lexical_scale`, `test_missing_payment_format_is_null_and_exact_long_currency_is_preserved` |
| T009 unsupported precision/overflow/negative/nonfinite/missing money or currency/timezone/party and unknown payment format | `test_unsupported_observable_fact_is_rejected_and_counted`, `test_invalid_amount_clock_or_party_rejects_event_without_rounding`, `test_unknown_payment_format_rejects_row_pending_mapping_revision` |
| T009 private labels independent of event validity, every row accounted, unknown/target fields excluded | `test_invalid_label_keeps_valid_observable_event`, `test_private_label_status_is_separate_from_operational_event`, `test_nonbinary_label_is_ineligible_but_event_facts_remain`, `test_accounting_reconciles_every_record_and_unknown_fields_never_become_predictors`, `test_each_row_has_prefilter_reference_and_one_event_status` |
| T009 T004 structural/header/encoding/partial-file matrix | `test_structural_or_encoding_error_cannot_publish_partial_import` (empty/header-only, BOM, case/space/duplicate/missing/reordered/extra target-like header, invalid UTF-8/NUL/UTF-16, truncated quote and wrong width), `test_truncated_utf8_cannot_publish_complete_report`, `test_malformed_quoted_record_after_valid_rows_invalidates_whole_attempt`, `test_wrong_width_after_valid_rows_invalidates_whole_attempt`, `test_quoted_multiline_is_one_record_and_rejected_row_is_accounted` |
| T010 pre-filter one-based ordinal, quoted multiline as one record, equal rows, rejected predecessor, bank distinction | `test_prefilter_ordinal_and_distinct_equal_rows`, `test_rejected_row_does_not_renumber_later_equal_valued_rows`, `test_quoted_multiline_record_consumes_one_ordinal`, `test_parser_keeps_prefilter_ordinals_after_rejected_then_equal_rows`, `test_parser_multiline_record_does_not_shift_following_identity`, `test_same_account_number_in_different_banks_has_distinct_join_key` |
| T010 D/C byte vector, namespace/member/release separation, label-only and source/mapping/time version changes, original source SHA-256 | `test_reviewed_synthetic_dc_vector`, `test_namespace_and_member_are_separate_identity_inputs`, `test_member_boundaries_and_release_namespace_do_not_alias`, `test_member_case_and_unicode_bytes_are_not_normalized`, `test_label_only_edit_keeps_dc_but_changes_dataset_version`, `test_label_only_change_has_distinct_dataset_version_in_isolation`, `test_source_mapping_and_time_policy_each_change_dataset_version`, `test_modified_source_fails_pinned_sha256_even_if_dc_is_unchanged` |
| T010 full-digest/changed-fact collision, replay idempotence, no identity guarantee for arbitrary reordered content | `test_truncated_id_collision_with_distinct_full_digest_fails`, `test_case_id_prefix_collision_with_distinct_full_digest_fails`, `test_same_identity_with_changed_label_free_facts_fails`, `test_same_identity_and_facts_can_be_replayed_without_duplication`, `test_reordered_source_changes_version_without_promising_new_row_keys`; store replay check below also asserts no duplicate event/case. |
| T011 staged/complete/failed, row reconciliation, interruption, restart, retry, same-version idempotence, changed-version coexistence | `test_interrupted_new_version_never_replaces_complete_version`, `test_reimport_same_complete_version_is_idempotent` (one event and one case), `test_incomplete_row_accounting_blocks_completion`, `test_failed_new_version_can_retry_after_restart_without_touching_old_complete`, `test_parser_exception_during_batch_does_not_publish_partial_version` |
| T011 unsupported SQLite schema and private-label access boundary | `test_unsupported_sqlite_schema_version_fails_closed`, `test_operational_projection_cannot_read_private_labels` |

All rows use authored synthetic data and provisional T013/T014 internal interfaces. Their assertions define the reviewed behavior; GREEN implementation may adjust interface spelling while preserving these outcomes. The checks do **not** establish working import, actual IBM reconciliation, model evaluation, or active v2 product behavior. T007/T008 collective approval is in the [separate reviewed-hash record](feature-002-t007-t008-team-review-2026-11-13.md#collective-final-byte-approval-conveyed-by-the-user).

### Actual continuation commands and RED reasons

Working directory: repository root on macOS, `PYTHONPATH=backend/src` as shown; existing locked `.venv` used. Intermediate 70-case and 77-case collections/runs exited **0** and **1**, respectively; subsequent C-collision and member-byte cases produced the final 79-case set below. An intermediate `.venv/bin/python -m ruff check backend/tests/unit/test_data_identity.py` exited **1** for two import-order `I001` findings after adding local parser tests; the imports were reordered, without changing behavior.

| Actual command | Exit | Observed result |
|---|---:|---|
| `PYTHONPATH=backend/src .venv/bin/python -m pytest --collect-only -q backend/tests/unit/test_data_import.py backend/tests/unit/test_data_identity.py backend/tests/integration/test_data_store.py` | 0 | **79 tests collected in 0.02s**: T009 53, T010 19, T011 7; no collection errors. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q --tb=no backend/tests/unit/test_data_import.py backend/tests/unit/test_data_identity.py backend/tests/integration/test_data_store.py` | 1 | **79 failed in 0.04s**, all in test bodies; no errors or passes. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q --tb=line backend/tests/unit/test_data_import.py backend/tests/unit/test_data_identity.py backend/tests/integration/test_data_store.py > /tmp/fraudlens-feature002-red-20261113-final.txt 2>&1` | 1 | **79 failed in 0.05s**; local untracked `/tmp` log used only to inspect each actual assertion reason. |
| `rg '^E   AssertionError: T0(13|14) missing:' /tmp/fraudlens-feature002-red-20261113-final.txt \| sort \| uniq -c` | 0 | 79 assertion reasons: 53 missing canonical parser; 8 missing D/C identity; 3 missing dataset-version derivation; 1 each missing source-hash check, pre-filter parser identity, multiline parser identity, bank-qualified account parser, D full-digest collision registry, C full-digest collision registry, fact-digest collision registry and idempotent registry; 7 missing SQLite repository. No unexpected assertion or environment failure. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q --tb=short backend/tests/unit/test_data_import.py::test_malformed_quoted_record_after_valid_rows_invalidates_whole_attempt backend/tests/unit/test_data_identity.py::test_truncated_id_collision_with_distinct_full_digest_fails backend/tests/integration/test_data_store.py::test_unsupported_sqlite_schema_version_fails_closed` | 1 | 3 failed in 0.05s at missing parser, missing collision registry, and missing SQLite repository, respectively. |
| `.venv/bin/python -m ruff check backend/tests/unit/test_data_import.py backend/tests/unit/test_data_identity.py backend/tests/integration/test_data_store.py` | 0 | All checks passed after import-order correction. |
| `git diff --check` | 0 | No working-diff whitespace errors. |

T009, T010 and T011 have their specified RED behavior and negative-case matrix represented by collected tests and intended missing-behavior failures. They are **complete as RED tasks**, not GREEN. T012–T014 remain unstarted. The mapping still has `import_allowed=false`; the real IBM source was not imported. The next implementation step is T012 canonical/import models, then T013 parser/identity and T014 SQLite store, followed by running these tests GREEN and regressions.

## T012–T014 GREEN on authored inputs — 2026-11-13

[Original implementation request](../../prompts/development/002-t012-t014-green-2026-11-13.md). Branch `002-data-and-risk-scoring`, unchanged HEAD `182d0b290c8819e602fc5d77e8df8e904228b032`; all preexisting working changes were preserved. This unit adds [`data_contracts.py`](../../backend/src/fraudlens/data_contracts.py) and [`data_store.py`](../../backend/src/fraudlens/data_store.py), and extends the existing [`data_import.py`](../../backend/src/fraudlens/data_import.py). No CLI import command or HTTP import endpoint was added. Current reviewed mapping raw LF/normalized SHA-256 remains `a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57`; offline contract SHA-256 remains `534de0c70a6ecbec69dd8734d6fec5830a9814da81fa508afe16a0f1dcca9918`. Runtime: Python 3.14.7, Ruff 0.17.4, SQLite 3.53.1 from the existing `.venv`.

- **T012:** frozen canonical transaction keeps exact paid/received strings and currencies, raw/interpreted time, bank-qualified keys, pre-filter ordinal and label-free fact digest. Private label/status is a separate class/table. `ImportReport.reconciled()` enforces all three row/eligibility equations. `DatasetVersion` has staged/complete/failed status; only complete store versions can be selected.
- **T013:** `iter_canonical_rows` streams strict UTF-8 CSV records, exact ordered eleven-column mapping, source record ordinals before filtering, independent observable-fact and private-label validation, and explicit UTC+00 synthetic analysis coordinate. It rejects structural failure without publishing a trustworthy partial report. `parse_canonical_source` collects the iterator for bounded authored fixtures; T015 can consume the iterator with the store in batches. D/C use approved framed UTF-8 N/F/U64BE ordinal and distinct SHA-256 domains; `dv_` uses three full digests. The identity registry checks full digests, framed inputs and label-free facts, including D/C and cross-version persisted-fact collisions. The approved mapping hash is pinned outside the mapping file in code; changed mapping bytes fail the parser boundary. The real IBM source SHA-256 still must be enforced by T015 before import.
- **T014:** SQLite schema version 1 stores dataset stages, operational events and private labels in separate tables, and an active pointer. Unsupported schema versions fail closed. A complete version is immutable except exact idempotent replay; staged/failed retry clears partial rows, parser/batch exceptions fail the stage, and completion reconciles rows transactionally. Source-bound stages verify the derived `dv_` from S/M/T and require one private label status for each event-valid row. Ingest batches are capped at 512 rows in memory. Operational reads omit private labels and source ordinal. An interrupted new version does not replace the previous active complete version.

### Test corrections made during GREEN

Two prior RED fixtures conflicted with the reviewed contract and were corrected without removing behavior coverage: `test_namespace_and_member_are_separate_identity_inputs` now expects an empty F to be rejected (N and F must both be nonempty), and the T011 store tests now pass explicit synthetic C IDs alongside D IDs (the store must not invent a C ID from a D prefix). The same 79 cases remain collected. A new canonical helper initially reused the old inspector's private `_amount` name; the first full backend regression exposed 23 inspector failures. Renaming the new helper `_canonical_amount` restored the read-only inspector without changing its behavior. An initial Ruff pass found import ordering in the new modules; imports were reordered.

### Actual commands and observed results

Commands ran from repository root on macOS with `PYTHONPATH=backend/src` where shown. Exit codes are the actual process results; no IBM CSV was read or imported in this unit.

| Command | Exit | Observed result |
|---|---:|---|
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q --tb=no backend/tests/unit/test_data_import.py backend/tests/unit/test_data_identity.py backend/tests/integration/test_data_store.py` | 1 | Initial baseline **79 expected RED failures in 0.05s**, before application code changes. |
| `.venv/bin/python -m ruff check backend/src/fraudlens/data_contracts.py` | 0 | T012 model file passed. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q --tb=short backend/tests/unit/test_data_import.py backend/tests/unit/test_data_identity.py` | 1 | T013 first pass: 71 passed, 1 failed because the RED test expected an ID for an empty member; approved contract requires nonempty F. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests/unit/test_data_import.py backend/tests/unit/test_data_identity.py` | 0 | After test correction: **72 passed in 0.05s**. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q --tb=short backend/tests/unit/test_data_import.py backend/tests/unit/test_data_identity.py backend/tests/integration/test_data_store.py` | 0 | T014 first complete targeted run: **79 passed in 0.07s**. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests` | 1 | First full backend run: **23 failed, 436 passed**, due solely to new `_amount` shadowing the existing inspector summary helper. No test was bypassed; implementation was renamed. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests` | 0 | After rename and subsequent store hardening, final full backend **459 passed, 1 preexisting Starlette/httpx warning in 0.59s**. Includes all 79 import/identity/store cases and Foundation regressions. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests/unit/test_data_import.py backend/tests/unit/test_data_identity.py backend/tests/integration/test_data_store.py` | 0 | Final targeted **79 passed in 0.08s**. |
| `PYTHONPATH=backend/src .venv/bin/python - <<'PY'` (authored CSV, stream iterator, bound S/M/T stage, exact stored money, private-status completion gate and restart assertions) | 0 | Printed `bound S/M/T version, private-status completion gate, exact operational money: passed`. Other synthetic manual checks of immutable replay/restart and provenance mismatch also exited 0. No raw IBM file used. |
| `.venv/bin/python -m ruff check backend/src backend/tests` | 0 | All checks passed. Earlier first runs on `data_import.py` and `data_store.py` each exited 1 for import order and were fixed by `ruff check --fix`. |
| `shasum -a 256 data/mappings/ibm_hi_small_v1.json specs/002-data-and-risk-scoring/contracts/data-and-scoring.md` | 0 | Approved mapping and offline contract hashes unchanged, as shown above. |
| `PYTHONPATH=backend/src .venv/bin/python evidence/tasks/feature-002-green-smoke.py` | 0 | Reproducible authored-only smoke printed `synthetic bound import/store/restart smoke: passed`. It checks the bound S/M/T version, private-status completion gate, exact operational money, immutable same-version replay and active-version survival after restart. |
| `.venv/bin/python -m ruff check backend/src backend/tests evidence/tasks/feature-002-green-smoke.py` | 0 | All checks passed. First run exited 1 for smoke-script import order; `.venv/bin/python -m ruff check --fix evidence/tasks/feature-002-green-smoke.py` exited 0 and fixed that single finding. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests` | 0 | Final rerun after the reproducible smoke script: **459 passed, 1 preexisting Starlette/httpx warning in 0.66s**. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests/unit/test_data_import.py backend/tests/unit/test_data_identity.py backend/tests/integration/test_data_store.py` | 0 | Final rerun: **79 passed in 0.08s**. |
| `git diff --check` | 0 | No whitespace errors in the tracked working diff. |

**Limitations:** T015 must wire the reviewed source hash/namespace/member and streaming iterator into the local CLI, produce a full ImportReport and refuse import while `import_allowed=false` unless a separately reviewed execution policy enables it. T016 actual IBM import/reimport, large-file resource behavior and SC-001 acceptance were not run. The convenience `parse_canonical_source` materializes authored fixture results; large-source use must stream through `iter_canonical_rows` and the bounded store path. No model evaluation, v2 API/decoder integration, browser run or independent teammate reproduction was claimed. No commit/push/merge.

## T015 local CLI implementation — 2026-11-13

[Original request](../../prompts/development/002-t015-t016-complete-and-publish-2026-11-13.md). The local `import` subcommand takes explicit `--source`, `--mapping`, `--namespace`, `--expected-sha256` and `--store`; it has no HTTP write or bypass flag. Runtime authorization checks the separate [collective final-byte review](feature-002-t007-t008-team-review-2026-11-13.md#collective-final-byte-approval-conveyed-by-the-user) and its linked user confirmation, exact normalized M, exact source namespace/member/size/S and time-policy T. The reviewed mapping's embedded `pending_team_review`/`import_allowed=false` fields remain the historical inspect-only state; execution is source-bound by this external approval, without changing the hash-approved mapping bytes. The `inspect` path remains separate. The CLI report contains only aggregate counts and hashes. The store now supports streaming source-record count finalization, bounded 512-row SQLite batches and the seven aggregate report counts; a new complete version is selected only after reconciliation. Same-version replay verifies S/M/T and returns the immutable complete record without adding rows.

The three new CLI integration tests were first run against the saved pre-T015 CLI (temporarily restored from `HEAD` and then restored to the working implementation). They failed in their bodies because `_load_authorization` and the import behavior were absent: **3 failed, 7 deselected**, exit 1. GREEN on the implementation: **3 passed, 7 deselected**, exit 0. The interrupted-retry fixture was corrected to change only the private label; its earlier observed-fact edit correctly triggered the reviewed same-identity changed-fact guard, so it was not an appropriate retry fixture. No behavioral assertion was removed.

| Command | Exit | Observed result |
|---|---:|---|
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q --tb=short backend/tests/integration/test_data_store.py -k cli_` (pre-T015 CLI restored from `HEAD`) | 1 | 3 intended failures at missing `_load_authorization`/import behavior; 7 deselected. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q --tb=short backend/tests/integration/test_data_store.py -k cli_` (final implementation) | 0 | 3 passed, 7 deselected in 0.06s. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests/integration/test_data_store.py backend/tests/unit/test_data_import.py backend/tests/unit/test_data_identity.py` | 0 | 82 passed in 0.08s. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests` | 0 | 462 passed, 1 preexisting Starlette/httpx warning in 0.81s. |
| `.venv/bin/python -m ruff check backend/src backend/tests evidence/tasks/feature-002-green-smoke.py` | 0 | All checks passed. |
| `PYTHONPATH=backend/src .venv/bin/python evidence/tasks/feature-002-green-smoke.py` | 0 | Authored bound-stage/restart smoke passed. |
| `git diff --check` | 0 | No tracked-diff whitespace errors. |

The real-source T016 first run is in progress at the time of this entry. Its completed results and final publication decision are recorded below when available; this paragraph does not claim T016 completion.

## T016 declared IBM v8 import and exact replay — 2026-11-13

The first run used the existing `data/raw/HI-Small_Trans.csv` and a new ignored `data/processed/feature-002-ibm-v8.sqlite`; `git check-ignore -v` exited 0 and identified `.gitignore:37:/data/processed/`. `df -h data/raw .` exited 0 and reported **774 GiB available** on the data volume before import. The `data/processed` directory did not yet exist, so the first `df -h data/processed data/raw` exited 1 for that path; `mkdir -p data/processed` exited 0. No CSV or SQLite bytes were staged for Git. The earlier read-only inspect established 5,078,345 parsed records; the import below establishes their event and label validity under the reviewed mapping.

Both CLI invocations used this exact command from repository root (with `/usr/bin/time -p`):

```sh
/usr/bin/time -p env PYTHONPATH=backend/src .venv/bin/python -m fraudlens.pipeline_cli import --source data/raw/HI-Small_Trans.csv --mapping data/mappings/ibm_hi_small_v1.json --namespace kaggle:ealtman2019/ibm-transactions-for-anti-money-laundering-aml:v8 --expected-sha256 b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040 --store data/processed/feature-002-ibm-v8.sqlite
```

| Check | First import | Same-command replay |
|---|---|---|
| CLI exit/status | 0 / `complete`, `repeated=false` | 0 / `complete`, `repeated=true` |
| `source_records` | 5,078,345 | 5,078,345 |
| `event_valid` / `event_rejected` | 5,078,345 / 0 | 5,078,345 / 0 |
| `label_eligible` / `label_ineligible` | 5,078,345 / 0 | 5,078,345 / 0 |
| `positives` / `negatives` | 5,177 / 5,073,168 | 5,177 / 5,073,168 |
| `DatasetVersion` | `dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802` | same |
| Source S | `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040` | same |
| Normalized mapping M | `a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57` | same |
| SQLite schema | 1 | 1 |
| `/usr/bin/time -p` real | 1,343.87 s | 12.23 s |

The three required equations hold exactly: 5,078,345 = 5,078,345 + 0; 5,078,345 = 5,078,345 + 0; 5,078,345 = 5,177 + 5,073,168. `stat -f '%z bytes' data/processed/feature-002-ibm-v8.sqlite` exited 0 and printed **7,559,012,352 bytes** after the first import. `shasum -a 256 data/raw/HI-Small_Trans.csv data/processed/feature-002-ibm-v8.sqlite` exited 0 after each import: source S was unchanged at the value above and the entire SQLite file was identically `a7a9495557f5462a8d08d0e31f7d0a81e54c3df10e07ddb2617b4194d7bea8cf` before and after replay. This whole-file equality, together with the CLI `repeated=true` path, proves that replay added no identities or changed complete SQLite content.

`/usr/bin/time -p .venv/bin/python evidence/tasks/feature-002-import-verify.py --source data/raw/HI-Small_Trans.csv --mapping data/mappings/ibm_hi_small_v1.json --store data/processed/feature-002-ibm-v8.sqlite` exited **0** in **80.51 s**. Its read-only SQLite queries found `status=complete`, active `dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802`, **5,078,345 distinct D IDs**, **5,078,345 distinct C IDs**, **5,078,345 separate private label records**, `PRAGMA user_version=1`, `PRAGMA quick_check=ok`, matching stored S/M/T, and `reconciled=true`. No extra or duplicate identity was observed. The reported T is `67a408fc52e57035115186c3c9863dfeac5a72d709292e0f7baeef560086d781`.

### Final local verification before publication

| Command | Exit | Observed result |
|---|---:|---|
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests/integration/test_data_store.py backend/tests/unit/test_data_import.py backend/tests/unit/test_data_identity.py` | 0 | 82 passed in 0.10s, including three T015 CLI tests. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests` | 0 | 462 passed, 1 preexisting Starlette/httpx warning in 0.76s. |
| `.venv/bin/python -m ruff check backend/src backend/tests evidence/tasks/feature-002-green-smoke.py evidence/tasks/feature-002-import-verify.py evidence/tasks/feature-002-team-review-check.py` | 0 | All checks passed. |
| `git diff --check` | 0 | No tracked-diff whitespace errors. |
| `shasum -a 256 data/mappings/ibm_hi_small_v1.json specs/002-data-and-risk-scoring/data-model.md specs/002-data-and-risk-scoring/contracts/data-and-scoring.md specs/002-data-and-risk-scoring/contracts/api.md specs/002-data-and-risk-scoring/contracts/schemas.json` | 0 | All five hashes match the collective final-byte approval table: M `a816260a…093e57`, data model `e8235e35…a0987`, offline `534de0c7…9918`, API `fbf7be0d…b13e`, schema `bf487d84…9f88`. Full values remain in that approval table and the command output. |

`git ls-remote origin refs/heads/002-data-and-risk-scoring` first exited 128 under restricted DNS, then exited 0 with elevated network access and reported `6952f1d90b72cac00983449b1e96079b42a7eb72`. `git fetch origin 002-data-and-risk-scoring` exited 0 and brought in three documentation commits after local base `182d0b2`. Their mapping file has a different raw SHA-256 (`fa2dd0e1…dffb2ba8`) while the older remote technical-resolution record names another review hash (`27445724…439699`). The working Phase 3 import is tied to the independently reviewed local final-byte M above. Publication must preserve the remote commits while keeping that executable mapping and its exact approved hash; this reconciliation is performed before push.

### Remote reconciliation and publication preparation

`git add -A` initially exited 128 because the sandbox denied `.git/index.lock`; the same authorized command with elevated Git permission exited 0. The reviewed staged list contained 33 Phase 3 code/test/contract/evidence/prompt files, no raw CSV, SQLite, journal/WAL or unrelated generated artifact; `git diff --cached --check` exited 0. `git commit -m 'feat(feature-002): complete and verify local dataset import'` exited 0 and made provisional `5ce690a`. `git rebase origin/002-data-and-risk-scoring` exited 1 at three overlapping documents (`next_work.md`, offline contract, `tasks.md`). The rebase was deliberately completed rather than overwriting the remote branch. The five final-byte-approved files were restored exactly from `5ce690a`; remote approval-publication material and contribution ledger remain in the preceding three Git commits, while the intermediate remote mapping digest is explicitly marked historical in source/contract review and the technical-resolution ledger. No individual approval was inferred. Conflict-marker search found none; five SHA-256 values matched the final-byte review; JSON validation, 462 backend tests, Ruff and staged `git diff --cached --check` passed. `GIT_EDITOR=true git rebase --continue` exited 0 and produced provisional rebased commit `c0e3900` after remote `6952f1d`. Final amended/published SHA and push verification are recorded separately after completion.
