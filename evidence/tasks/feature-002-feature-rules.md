# Feature 002 T017 — frozen feature catalog and RulePolicy v1

- Date/time and timezone: 2026-11-13 12:47 CET (Europe/Belgrade).
- Branch / reviewed HEAD before edits: `002-data-and-risk-scoring` / `55306089b506458fcaec9b621f49c00dd971d46e`; working tree initially clean.
- Task / requirements: [T017](../../specs/002-data-and-risk-scoring/tasks.md#phase-4-us2--label-free-feature-replay-and-rules-baseline-p1), [FR-005–FR-007](../../specs/002-data-and-risk-scoring/spec.md#historical-context-and-repeatable-scoring), [data model](../../specs/002-data-and-risk-scoring/data-model.md#featuredefinition-and-historicalfeaturesnapshot), [research decisions 7–8](../../specs/002-data-and-risk-scoring/research.md#decision-7--historical-time-semantics).
- Original development prompt: [T017 request](../../prompts/development/002-t017-feature-rules-request-2026-11-13.md); [Prompt 3](../../prompts/development/002-implementation-prompts.md#prompt-3--build-point-in-time-features-and-rule-scorer) read as scope context. The current request stops after T017.
- Status: **T017 complete as a contract gate** after the checks below. T018/T019 RED tests and T020 replay implementation were not started. No IBM import, SQLite write, model fit, commit or push.

## Frozen decisions and examples

The [offline contract](../../specs/002-data-and-risk-scoring/contracts/data-and-scoring.md#frozen-history-v1-catalog) now enumerates all **11** existing `history-v1` keys from `data-model.md`: four sender, four receiver and three current features. Each row records canonical inputs, directional join/aggregation, unit, availability, consumer and null/unknown semantics. Bank and account are paired for joins only; sender paid currency and receiver received currency have separate exact Decimal aggregates. `current_payment_format` is a source-audited optional categorical field, not an R1–R3 input. IDs, labels, label eligibility, future and full-file aggregates are excluded from predictors.

The half-open `[t−24h,t)` window includes its lower boundary and excludes `t`; peers at `t` share one earlier-history state before the group is appended. The first 24 h from source observation are context-only warm-up. `full` with no account matches gives measured integer/Decimal zero; `incomplete` or `unavailable` gives null history and no score. Valid facts with blank/invalid private labels remain in later history. The rules require matching complete dataset, `history-v1`, full coverage and post-warm-up event time. Under full coverage, fewer than three prior same-paid-currency events makes only R3's comparison unavailable; R1/R2 can still be evaluated.

The [RulePolicy v1 table](../../specs/002-data-and-risk-scoring/contracts/data-and-scoring.md#rulepolicy-v1) retains R1 `>=3` outgoing / `0.35`, R2 `>=3` incoming / `0.30`, and R3 `>=3` prior same-paid-currency outgoing plus exact `current_paid_amount * count >= 2 * prior_paid_sum` / `0.35`. Exact Decimal contributions form an ordinal score in `[0,1]`. The canonical machine policy JSON includes the aggregation, coverage gate and unavailable-R3 behavior and has SHA-256 `a281d38b8777b53882f4515dda7de927ff64dce43188e99c258419b1d605b5ce`; a changed rule requires a new version/digest before evaluation. No private evaluation labels were used to select features or thresholds.

The contract's six synthetic rows cover the exact time lower/upper edges, equal-time peers, bank-qualified counterparties, Euro paid versus US Dollar received aggregation, warm-up boundary, full-coverage measured zero versus absent history, label/future invariance and threshold edges. In the main hand calculation, three prior `A:1` outgoing Euro amounts `10+20+30=60` and three prior `R:1` incoming US Dollar amounts `7+9+11=27` give sender/receiver counts `3/3`. A current `40` Euro pays exactly `40*3=2*60`, firing all rules for `1.00`; a same-time peer paying `39.999999` Euro fails R3 while R1/R2 remain true for `0.65`. Two prior rows make R3 comparison unavailable and leave score `0.00` when R1/R2 are also below three. These are authored arithmetic checks, not results from the IBM dataset or the future replay implementation.

## Commands and observed results

All commands ran from the repository root. Python was **3.14.7**. `git branch --show-current && git rev-parse HEAD && git status --short` exited **0**, printed the branch and HEAD above and no working changes before editing. Reading T017–T019, the data model, offline contract, Prompt 3, research decisions and FR-005–007 was read-only.

The following inline verification command was repeated for the final policy and exited **0**, printing `11 catalog keys; policy a281d38b8777b53882f4515dda7de927ff64dce43188e99c258419b1d605b5ce ; boundary, bank, currency and Decimal rule vectors passed`:

```sh
.venv/bin/python - <<'PY'
import hashlib, json, re
from datetime import UTC, datetime, timedelta
from decimal import Decimal as D
from pathlib import Path
c = Path('specs/002-data-and-risk-scoring/contracts/data-and-scoring.md').read_text()
m = Path('specs/002-data-and-risk-scoring/data-model.md').read_text()
keys = ('sender_out_count_24h','sender_distinct_receivers_24h','sender_paid_count_same_currency_24h','sender_paid_sum_same_currency_24h','receiver_in_count_24h','receiver_distinct_senders_24h','receiver_received_count_same_currency_24h','receiver_received_sum_same_currency_24h','current_paid_amount','current_paid_currency','current_payment_format')
assert all(k in c and k in m for k in keys)
p = json.loads(re.search(r'The machine policy identifier.*?```json\n([^\n]+)\n```', c, re.S).group(1))
h = hashlib.sha256(json.dumps(p, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode()).hexdigest()
assert h == 'a281d38b8777b53882f4515dda7de927ff64dce43188e99c258419b1d605b5ce' and h in c
t0 = datetime(2026,1,1,tzinfo=UTC); t = t0 + timedelta(hours=36)
assert t-timedelta(hours=24) <= t-timedelta(hours=24) < t
assert not (t-timedelta(hours=24) <= t-timedelta(hours=24,minutes=1))
assert not (t < t) and t0+timedelta(hours=23,minutes=59) < t0+timedelta(hours=24)
assert len({('B','7'),('C','7'),('D','8')}) == 3
assert sum(map(D, ('10','20','30'))) == D('60')
assert sum(map(D, ('7','9','11'))) == D('27')
assert D('40')*3 == 2*D('60') and D('39.999999')*3 < 2*D('60')
assert D('0.35')+D('0.30')+D('0.35') == D('1.00')
assert D('0.35')+D('0.30') == D('0.65')
print('11 catalog keys; policy', h, '; boundary, bank, currency and Decimal rule vectors passed')
PY
```

A separate, longer in-memory Python replay of the six authored scenarios also exited **0** and printed: `PASS: 11 catalog keys, policy SHA-256, window edges, tied peers, separate currencies, exact R1-R3 thresholds, warm-up, measured zero, deficient coverage, label/future invariance`. It created no file or test and was not a T018/T019 RED execution.

`git show 55306089:specs/002-data-and-risk-scoring/contracts/data-and-scoring.md | shasum -a 256` exited **0**, yielding `03c1faa48b425263e3039ed64aca1f8b5793949b16f55a7b6bd7f94768a39703`. That is the Phase 3 cleanup contract hash; the older T007/T008 approved hash `534de0c70a6ecbec69dd8734d6fec5830a9814da81fa508afe16a0f1dcca9918` remains in its historical review record. `shasum -a 256` of the final T017 offline contract exited **0** with `359c5e16292d5475cb64e559a30ecf1ecf682557c7d5445d13744d8e00a8dbeb`. The T017 diff only adds feature catalog, replay/coverage and rule-policy details; it does not change the approved mapping, D/C/DatasetVersion recipe or v2 API/schema. Mapping SHA-256 remains `a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57`; data-model SHA-256 remains `e8235e358c6d01fc13e3f5f9a8ad0600d2d98c44d4afda4aa75809aa3efa0987` (`shasum -a 256`, exit **0**). The earlier T007/T008 review hashes remain historical and are not overwritten by this T017 revision.

`git diff --check` exited **0** with no whitespace findings. No application tests were run because T017 freezes a contract and the T018/T019 behavioral RED tests are the next tasks; no production replay/scorer exists to run GREEN. The in-memory checks verify the authored examples and policy bytes only. Independent human review and second-person reproduction were not claimed.

A read-only `python3 - <<'PY'` document check counted **11** catalog rows, confirmed T017 checked and T018/T019 open, and resolved local Markdown link targets; exit **0**, output `11 catalog rows; T017 checked, T018/T019 open; relative document links resolve`. A combined final status/hash command exited **1** only because its last `shasum` argument named a nonexistent mapping path under `specs/.../contracts/ibm-aml-v8-mapping.yaml`; no file was changed. Repeating `shasum -a 256 data/mappings/ibm_hi_small_v1.json; git diff --check` exited **0** with the mapping digest above and no whitespace output. Final branch and HEAD remained `002-data-and-risk-scoring` / `55306089b506458fcaec9b621f49c00dd971d46e`.

## Next step

Write and run T018's hand-calculated replay RED tests in `backend/tests/unit/test_feature_history.py`, then T019's allowlist/lineage RED tests; T020 is the later GREEN implementation.

## T018/T019 synthetic RED matrix — 2026-11-13

- Original request: [T018/T019 RED prompt](../../prompts/development/002-t018-t019-red-request-2026-11-13.md).
- Reviewed branch/HEAD: `002-data-and-risk-scoring` / `55306089b506458fcaec9b621f49c00dd971d46e`; the uncommitted T017 contract, task, handoff, prompt and evidence changes above were preserved. No production replay, actual IBM import, SQLite write, commit or push occurred.
- Proposed T020 interface pinned by these RED tests: `fraudlens.feature_history.build_feature_snapshots(events, dataset_version, coverage_start, purpose='scoring', missing_intervals=(), coverage_available=True)` returns snapshots keyed by transaction ID with `feature_values`, `coverage_state` and `scoreable`; `feature_catalog()` provides keyed lineage/unknown metadata; `validate_feature_projection()` accepts only versioned, approved feature values with join metadata outside predictors and rejects extras recursively. The tests express expected behavior, not an implemented API.

| Requirement | RED tests | Hand-computed expectation |
|---|---|---|
| T018 all 11 keys, direction, exact money | `test_all_eleven_catalog_values_and_directional_decimal_sums`, `test_paid_and_received_currency_are_grouped_independently` | Three A:1 outgoing Euro payments `10+20+30=60`; three R:1 incoming US Dollar receipts `7+9+11=27`; distinct bank-qualified counterparties `3/3`; current `40` Euro and `Wire`. Mixed currencies give same-paid Euro `1.000001+4.000004=5.000005` and same-received US Dollar `2.000002+3.000003=5.000005`, with separate directional counts. |
| T018 time window, tie group, ordering, future | `test_window_includes_exact_lower_bound_excludes_upper_peer`, `test_input_permutation_does_not_change_snapshots`, `test_tied_peers_share_prior_history_then_both_update_later_history`, `test_future_append_does_not_change_prior_snapshot` | At `t`, `t−24h−1min` excluded, `t−24h` and `t−1min` included, `t` peers excluded: count `2`. Two peers each see one prior event; later event sees `3`. Shuffle/future append preserve the earlier snapshot. |
| T018 held-out facts, bank identity, warm-up/coverage | `test_earlier_heldout_facts_contribute_without_labels`, `test_bank_qualified_accounts_and_counterparties_do_not_alias`, `test_first_24_hours_are_context_only_and_boundary_is_scoreable`, `test_full_coverage_cold_account_has_measured_zero`, `test_deficient_coverage_is_null_not_measured_zero` | Two prior validation/test facts yield sender count `2`, Euro sum `20` without labels. `B:7` and `C:7` are distinct; `A:1` and `X:1` do not alias. At `source_start+23h59m`: incomplete/unscoreable; at exactly `+24h`: full/scoreable, two earlier facts included. A new account with full coverage has integer/Decimal zero; known missing interval or absent provenance gives null history and no score. |
| T018 private label and replay purpose | `test_blank_invalid_or_removed_private_label_never_changes_replay`, `test_training_and_scoring_replay_have_identical_feature_values` | Parsed `1`, blank and invalid private labels give the same prior D identity and later feature values; the source-start fact is 36 h earlier and outside `[t−24h,t)`, so only the recent prior fact contributes sender count `1`. Training/scoring projections agree for identical facts. |
| T019 allowlist, source lineage, join-only keys | `test_catalog_exact_allowlist_and_source_lineage`, `test_bank_account_join_metadata_is_not_returned_as_predictor` | Exactly 11 keys; sender paid sum comes from sender bank/account, paid amount/currency and event time; receiver sum uses receiver bank/account, received amount/currency and event time. Bank/account keys can join but do not appear in the predictor result. |
| T019 negative and nested leakage | `test_forbidden_predictor_or_proxy_is_rejected` (23 cases), `test_catalog_candidate_cannot_launder_forbidden_source` (7), `test_nested_extra_field_cannot_hide_private_label`, `test_nested_extra_field_cannot_hide_hashed_identifier`, `test_unknown_feature_or_unversioned_projection_is_rejected` | Raw/encoded/hashed IDs, target copies, label eligibility, CSV order, future/full-file aggregates, unapproved source lineage and nested private values must raise a validation error rather than silently enter a model input. Unknown feature/version is rejected. |
| T019 categorical unknown state | `test_unknown_category_semantics_are_frozen_without_refit` | `current_paid_currency` and audited optional `current_payment_format` declare frozen unknown encoding for later model transform; missing payment format is explicit null. Approved source strings (`Euro`, `Wire`) remain unchanged in the feature projection. This does not fit an encoder or treat an unsupported source token as approved. |

Commands from the repository root, with observed results:

- `.venv/bin/python -m pytest --collect-only -qq backend/tests/unit/test_feature_history.py backend/tests/unit/test_feature_lineage.py` → exit **0**, **50 collected**: T018 **14**, T019 **36**. No collection/import error because T020 is imported only inside test bodies.
- `.venv/bin/python -m pytest -q --tb=line backend/tests/unit/test_feature_history.py backend/tests/unit/test_feature_lineage.py` → exit **1**, **50 failed** in test bodies. All failures are `ModuleNotFoundError: No module named 'fraudlens.feature_history'`, the missing T020 implementation boundary. These are intentional RED failures, not proof that any individual assertion has passed. A targeted run of `test_blank_invalid_or_removed_private_label_never_changes_replay` exited **1** at the same missing module after its synthetic parser assertions passed. A standalone parser probe initially exited **1** because `fraudlens` was absent from the direct interpreter path; `PYTHONPATH=backend/src .venv/bin/python - <<'PY'` repeated it successfully (exit **0**), showing label states `eligible_positive`, `missing`, `invalid`, all with three event-valid facts and the same prior D ID `D9abe95b7169c912e8919a351926f9a02`.
- `.venv/bin/ruff check backend/tests/unit/test_feature_history.py backend/tests/unit/test_feature_lineage.py` → exit **0**, `All checks passed!`.
- `git diff --check` → exit **0**, no output. T018/T019 are completed RED tasks; T020 GREEN and later scorer tests/implementation remain open. This is authored synthetic coverage, not independent reproduction or model evaluation.

One concrete next step: implement the versioned replay/catalog/projection boundary in T020 and run this 50-case matrix GREEN, then relevant existing backend regressions.

## T020 replay and local feature build GREEN — 2026-11-13

- Original request: [T020 GREEN prompt](../../prompts/development/002-t020-feature-replay-green-request-2026-11-13.md). Reviewed branch/HEAD: `002-data-and-risk-scoring` / `55306089b506458fcaec9b621f49c00dd971d46e`, with the uncommitted T017–T019 changes preserved. The T017 offline contract and its historical hashes above were not rewritten.
- Starting RED repeated with `.venv/bin/python -m pytest -q --tb=line backend/tests/unit/test_feature_history.py backend/tests/unit/test_feature_lineage.py`: exit **1**, **50 failed** in test bodies with `ModuleNotFoundError: No module named 'fraudlens.feature_history'`; collection was successful. This is the actual pre-implementation baseline in this session.
- [Pure `history-v1` replay](../../backend/src/fraudlens/feature_history.py) computes all 11 frozen keys from canonical operational facts. It sorts bounded fixture inputs by event time/ID; the streaming iterator requires event-time order and keeps only the sliding 24-hour window plus per-account/currency counters and Decimal sums. Every tied peer gets a snapshot before the group updates history. State is `full`, `incomplete` or `unavailable`; deficient history is null, whereas a full-coverage cold account has measured zeros. Feature input digests cover dataset/feature version, event fact digest, cutoff, coverage and typed values, excluding labels and wall-clock creation time. The fixed catalog declares source lineage, direction, unit, availability, consumers and unknown handling. Projection validation rejects unknown keys, unapproved lineage, nested extras and join keys as predictors.
- [SQLite store](../../backend/src/fraudlens/data_store.py) reads only complete provenance-bound datasets through an event-time SQL cursor; no private-label table participates. It lazily adds feature-build/snapshot tables under the existing schema version 1, stages bounded 512-row batches, checks count reconciliation, and marks the build complete transactionally. Readers see only complete builds. A failed write removes partial snapshots and marks the build failed; a staged build left by process interruption is invisible and cleared on retry. A prior complete version and its snapshots remain available. A repeated complete build checks count integrity and leaves the rows unchanged.
- [Local CLI](../../backend/src/fraudlens/pipeline_cli.py) adds `build-features --store PATH --dataset-version dv_... [--feature-version history-v1]`, returning only version, status, snapshot count and repeated flag or a controlled error code. It rejects incomplete/provenance-incompatible datasets and unsupported feature versions. Its SQL cursor and sliding window avoid loading the complete IBM event set into Python memory; a single tied-time group and 24-hour context still require memory. The CLI was exercised only against temporary authored SQLite files.

### Observed checks and test correction

| Command / check | Exit | Observed result |
|---|---:|---|
| `.venv/bin/python -m pytest -q --tb=short backend/tests/unit/test_feature_history.py backend/tests/unit/test_feature_lineage.py` after first replay implementation | 1 | **49 passed, 1 failed**. The test expected source-start history count 2 at `t=source_start+36h`, but that source-start fact is outside `[t−24h,t)`; the correct count is 1. Only this expected number and its RED matrix explanation were corrected; label invariance and time-boundary coverage remain asserted. |
| `.venv/bin/python -m pytest -q backend/tests/unit/test_feature_history.py backend/tests/unit/test_feature_lineage.py backend/tests/integration/test_feature_store.py` | 0 | **55 passed**: all original 50 T018/T019 cases GREEN plus 5 synthetic CLI/SQLite integration cases. |
| `.venv/bin/python -m pytest -q backend/tests` | 0 | **520 passed**, one existing Starlette/httpx deprecation warning. |
| `.venv/bin/ruff check backend/src backend/tests` | 0 | `All checks passed!` |
| `git diff --check` | 0 | No whitespace findings. |

The five integration cases verify local CLI success and subprocess replay, 3 persisted snapshots with warm-up/full states and private-label exclusion, rejection of staged/incompatible versions, cleanup after an injected failure following a committed snapshot batch while preserving an older complete build, invisibility/retry of an abandoned staged build, and actual bounded writes of **513** authored events in **512+1** batches. A completed synthetic build remained immutable on repeat. These are authored synthetic checks; no full IBM replay, model training, existing IBM SQLite modification, second-person reproduction, commit or push occurred. T020 is complete; T021 v2 scorer-boundary RED is the next task.

## T021 v2 scorer boundary RED — 2026-11-13

- Original prompt: [T021 request](../../prompts/development/002-t021-scorer-boundary-red-request-2026-11-13.md). Reviewed branch and HEAD: `002-data-and-risk-scoring` / `55306089b506458fcaec9b621f49c00dd971d46e`. The uncommitted T017–T020 files above remain local. This unit adds only contract tests and documentation, and marks the RED task complete.
- Contract references: [T021/T022](../../specs/002-data-and-risk-scoring/tasks.md), [ScoreRequestV2 boundary](../../specs/002-data-and-risk-scoring/contracts/data-and-scoring.md#scorerequestv2-and-scorerv2), [data model](../../specs/002-data-and-risk-scoring/data-model.md#scorerequest-riskassessment-and-explanation), FR-008/009/012. The test expresses the intended T022 callable as `score_v2(request, scorer, artifact=None)`, with `ScoreRequestV2` carrying the seven fields already listed in the offline contract. This callable name is the test-side implementation seam for T022, not a claim that it exists now.

| T021 criterion | Authored test cases in `backend/tests/contracts/test_data_scoring.py` | Assertion awaiting GREEN |
|---|---|---|
| Valid request and response, exact references and explanation digest | `test_valid_request_and_response_preserve_all_references_and_digest` | A full-coverage synthetic event returns score `0.35` with matching D ID, `dv_` ID, run, feature/scorer version, as-of, coverage and snapshot digest; all-reject implementations fail this positive case. |
| Request identity, version, schema and coverage | `test_request_rejects_mismatched_version_or_as_of` (3), `test_request_rejects_changed_snapshot_transaction_identity`, `test_request_rejects_bad_snapshot_schema_or_coverage` (5) | Reject wrong dataset/feature/as-of, D ID, unknown predictor, altered digest, incomplete or unscoreable snapshot. |
| Response identity, versions, digest, coverage and extras | `test_response_rejects_changed_identity_or_version` (6), `test_response_rejects_wrong_explanation_digest`, `test_response_rejects_bad_coverage_or_extra_private_data` (4) | Reject mismatched D/dataset/run/feature/scorer/as-of, explanation digest, coverage and private/nested response extras. |
| Artifact, time and repeatability | `test_required_artifact_absent_fails_without_calling_scorer`, `test_event_as_of_and_actual_scoring_times_are_distinct`, `test_repeated_scoring_compares_semantics_separately_from_execution_metadata` | A scorer requiring an artifact cannot run without one. Event time and exclusive history cutoff are event-related; actual scored time is later. The repeated semantic fields match while scored times differ. |
| Mutation, private data and score rejection | `test_injected_scorer_cannot_mutate_original_request`, `test_request_rejects_private_or_nested_unexpected_data` (2), `test_invalid_score_fails_without_coercion_clamp_zero_or_fallback` (8) | Deep copy protects the original feature dict; top-level private label and nested target are rejected; bool, string, nonfinite and out-of-range scores raise after exactly one controlled-scorer call, without fallback/clamp/default. |

Observed commands from repository root:

| Command | Exit | Actual result |
|---|---:|---|
| `git branch --show-current && git rev-parse HEAD && git status --short` | 0 | Branch and HEAD above; local T017–T020 edits present before this unit. |
| `.venv/bin/python -m pytest --collect-only -qq backend/tests/contracts/test_data_scoring.py` | 0 | **35 collected**, no import or collection error. |
| `PYTHONPATH=backend/src:backend/tests/contracts .venv/bin/python -c 'import test_data_scoring as t; f=t._fields(); s=f["feature_snapshot"]; assert s.scoreable and s.coverage_state=="full" and s.as_of==t.EVENT_TIME and s.transaction_id==f["canonical_transaction"].transaction_id; print("synthetic fixture full, scoreable, identities/as-of aligned")'` | 0 | Printed `synthetic fixture full, scoreable, identities/as-of aligned`. This validates the authored positive input fixture independently of the missing T022 boundary. |
| `.venv/bin/python -m pytest -q --tb=line --no-header backend/tests/contracts/test_data_scoring.py` | 1 | **35 failed** in test bodies, each with `AssertionError: T022 missing: ScoreRequestV2` at the lazy boundary. The missing type is absent from current `fraudlens.data_contracts`; no case passed or reached its later validation assertion. This is the intended RED reason, not evidence that each negative validation already works. |
| `.venv/bin/ruff check --fix backend/tests/contracts/test_data_scoring.py` | 0 | Corrected only import spacing in the newly authored test file after initial Ruff exit 1. |
| `.venv/bin/ruff check backend/tests/contracts/test_data_scoring.py` | 0 | Final result: `All checks passed!`. |
| `git diff --check` | 0 | No whitespace findings in tracked changes. |

T021 is complete as a RED-test writing task. T022 remains open; its implementation must turn these cases GREEN and preserve Foundation v1. No production scorer, real IBM replay, existing IBM SQLite write, commit or push occurred.

## T022–T025 Prompt 3 scorer and rules completion — 2026-11-13

- [Original request](../../prompts/development/002-t022-t025-prompt-3-request-2026-11-13.md). Branch / reviewed HEAD: `002-data-and-risk-scoring` / `55306089b506458fcaec9b621f49c00dd971d46e`. The uncommitted T017–T021 work listed above was preserved. The frozen T017 contract and policy SHA-256 were not edited.
- T022 adds `ScoreRequestV2`, `ScorerV2`, `RiskAssessmentV2`, `ExplanationV2` and `score_v2` in `data_contracts.py`. The boundary checks matching D/dataset/run/feature/scorer references, event and exclusive as-of time, full post-warm-up coverage, exact closed `history-v1` values, recomputed feature digest, allowed explanation keys/digest and a finite uncoerced score in `[0,1]`. It copies the request before calling the injected scorer once, validates its result, rejects private/nested extras and does not fall back. Model output requires an artifact descriptor; actual model artifact loading/hash verification belongs to later T038. Foundation `scoring.py` was unchanged.
- T023's first **10** authored cases collected successfully and all failed in test bodies with `ModuleNotFoundError: No module named 'fraudlens.rule_scoring'` before T024. They cover exact R1/R2 count 3, R3 `40*3 = 2*60`, just-below `39.999999*3 < 120`, two-row unavailable R3, full-coverage measured zero, incomplete/unavailable coverage, independent R1/R2, paid-currency separation, future/private-label exclusion and opaque ID invariance. After GREEN, three adapter/repeat/zero-explanation checks were added; the final rule set has **13** passing cases. The prior 35 T021 cases pass; one added negative case rejects a private label disguised as an available explanation feature (**36** passing scorer-boundary cases).
- T024 implements the exact frozen `rules-v1` policy in `rule_scoring.py`; its canonical sorted compact JSON hashes to `a281d38b8777b53882f4515dda7de927ff64dce43188e99c258419b1d605b5ce`. R1/R2/R3 contribute Decimal `0.35/0.30/0.35`; R3 compares `current*count >= 2*sum` without division or float rounding. Three structured reasons retain counts, amounts/currency, condition/state and contribution, including `comparison_unavailable`. The rules adapter uses the T022 boundary and a real UTC `scored_at`; its score kind is `ordinal_rule_score`.

### T025 actual-source replay and repeatability

The existing complete IBM v8 import was **not** reimported. `cp -c` made the ignored work copy `data/processed/feature-002-ibm-v8-rules-work.sqlite` from the original `data/processed/feature-002-ibm-v8.sqlite`; `git check-ignore -v` identified `.gitignore:37:/data/processed/`. `df -h data/processed` before the copy reported **767 GiB available**. The first CLI invocation without `PYTHONPATH` exited **1** with `ModuleNotFoundError: No module named 'fraudlens'`; the corrected invocation below completed. During the full build, read-only checks observed `staged` and increasing snapshot counts. Only after reconciliation did the copy expose `complete`.

| Executed command / check | Exit | Observed result |
|---|---:|---|
| `.venv/bin/python -m pytest --collect-only -qq backend/tests/unit/test_rule_scoring.py` before T024 | 0 | **10 collected**. |
| `.venv/bin/python -m pytest -q --tb=line backend/tests/unit/test_rule_scoring.py` before T024 | 1 | **10 failed**, all at absent `fraudlens.rule_scoring`; assertions beyond that import were not yet exercised. |
| `.venv/bin/python -m pytest -q --tb=line backend/tests/contracts/test_data_scoring.py` after T022, before the later extra negative case | 0 | Original **35 passed**. |
| `PYTHONPATH=backend/src .venv/bin/python -m fraudlens.pipeline_cli build-features --store data/processed/feature-002-ibm-v8-rules-work.sqlite --dataset-version dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802` | 0 | `status: complete`, `repeated: false`, **5,078,345 snapshots**, feature version `history-v1`. This ran against only the ignored copy. |
| Same `build-features` command repeated | 0 | `status: complete`, `repeated: true`, same DatasetVersion and **5,078,345 snapshots**. |
| `PYTHONPATH=backend/src .venv/bin/python -S -c 'from fraudlens.rule_scoring import POLICY_SHA256, RuleScorer; print(POLICY_SHA256, RuleScorer.requires_artifact)'` | 0 | Printed frozen policy hash and `False`. `-S` excluded site packages; the rules adapter imported without model or provider packages. |
| `PYTHONPATH=backend/src .venv/bin/python -S /tmp/fraudlens_t025_probe.py` | 0 | Read only operational events and completed snapshots from the copy. Three real scoreable events yielded ordinal scores `0`, `0.65`, `0.65`. Each was scored under two different run IDs; replacing only run ID and actual `scored_at` made each pair equal. Policy hash matched T017. No private-label table was queried. The temporary probe script is an execution aid, not product code. |
| Read-only SQLite count/coverage query on the work copy | 0 | Schema version **1**, operational events **5,078,345**, snapshots **5,078,345**, `feature_builds` **complete**; `full` **3,963,424**, `incomplete` **1,114,921**. Work-copy main database size **12,443,103,232 bytes** at measurement. |
| `shasum -a 256 data/processed/feature-002-ibm-v8.sqlite` | 0 | Original base remained `a7a9495557f5462a8d08d0e31f7d0a81e54c3df10e07ddb2617b4194d7bea8cf`. |
| `.venv/bin/python --version` | 0 | `Python 3.14.7`. |
| `.venv/bin/python -m pytest -q backend/tests` | 0 | **569 passed**, one existing Starlette/httpx deprecation warning. This includes Foundation v1 regressions, 36 scorer-boundary cases and 13 rule cases. |
| `.venv/bin/ruff check backend/src backend/tests` | 0 | `All checks passed!` |
| `git diff --check` | 0 | No whitespace findings. |

T025 is complete for the rules-only integration increment. The full real feature replay and the three actual-source rule scores are **not** model evaluation or trained-model SC-003 evidence. They do not establish predictive performance, calibration or a completed scored run; those belong to later tasks. The work copy remains ignored for subsequent work, while the original IBM database and CSV were preserved.

## Final Phase 4 technical review — 2026-11-13

Source: [original final-review prompt](../../prompts/development/002-phase-4-final-review-2026-11-13.md). Reviewed branch `002-data-and-risk-scoring`, HEAD `55306089b506458fcaec9b621f49c00dd971d46e` and the **uncommitted tracked diff plus all untracked Phase 4 files**. This section is a Codex technical review, not a team signoff. Historical T017–T025 RED/GREEN, source and policy hash records above remain intact.

| Task | Review of actual code/tests/evidence | Result |
|---|---|---|
| T017 | Eleven frozen catalog entries, exact paid/received currency direction, `history-v1`, `[t−24h,t)`, full/incomplete/unavailable and `rules-v1` hand vectors in the offline contract. | Complete. |
| T018 | Fourteen hand-value tests cover all 11 keys, boundaries, ties, shuffle, future append, held-out facts, bank-qualified joins, exact Decimal, warm-up/zero/gaps and label independence. | Complete; GREEN. |
| T019 | Thirty-six lineage cases reject target/eligibility/identifier/source-order/future/full-file proxies and nested extras; unknown categories follow frozen semantics. | Complete; GREEN. |
| T020 | Timestamp-group replay and bounded SQLite batches; complete compatible versions only, staged results hidden, interrupted restart/retry preserves an older build. Five integration tests and actual-source count reconciliation below. | Complete; GREEN. |
| T021 | The 35-case authored v2 scorer RED matrix is preserved. | Complete as RED task. |
| T022 | Closed request/response identity, digest, coverage, time, score, private-field and mutation checks are GREEN. Final review found and fixed available rule-explanation source/scale/reconstruction acceptance; three new regressions were RED, then GREEN. Foundation v1 `scoring.py` has an empty Git diff. | Complete after correction. |
| T023 | Hand arithmetic at R1/R2 count 3 and R3 `40*3=2*60`, just below, measured zero and deficient coverage remains in the authored rule tests. | Complete as RED task, now GREEN. |
| T024 | Exact Decimal `0.35+0.30+0.35`, actual states/reasons and `rules-v1` policy digest are implemented; no model/provider import dependency. | Complete; GREEN. |
| T025 | A full IBM feature build, repeated completed build and three real-event semantic scoring repeats are separate prior observations, rechecked below where read-only. | Complete as rules-only evidence, not model SC-003. |

The confirmed T022 defect: an injected scorer could send an `available` explanation with `score_source=rules` but `method=tree_path`, `explained_scale=log_odds`, or contributions totaling `0.30` with a returned `0.35` score. The existing schema-only check accepted all three. The new test `test_available_rule_explanation_matches_source_scale_and_score` first produced **3 `DID NOT RAISE` failures (exit 1)**. `score_v2` now requires rule method, risk-score scale, a full Decimal reconstruction and rejects mismatches. This changes only the scorer boundary; stored snapshots, catalog and policy are unchanged, so the multi-million-row replay was not repeated. Later model-artifact verification, model explanations and public v2 delivery remain assigned to their later tasks.

### Read-only IBM work-copy audit and separate repeats

The existing ignored work copy `data/processed/feature-002-ibm-v8-rules-work.sqlite` was opened with SQLite `mode=ro` and `PRAGMA query_only=ON`. It is **12,443,103,232 bytes**. DatasetVersion is `dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802`, catalog `history-v1`, rule policy `rules-v1` / SHA-256 `a281d38b8777b53882f4515dda7de927ff64dce43188e99c258419b1d605b5ce`. The earlier full `build-features` invocation returned `repeated=false` and 5,078,345 snapshots (exit 0); the *separate* second CLI invocation returned `repeated=true` and the same count (exit 0). The current review did not invoke that write-capable CLI again.

Read-only SQL compared `operational_events` and `feature_snapshots`: **5,078,345 each**, including **5,078,345 distinct snapshot transaction IDs**. `feature_builds` is `complete` with `snapshot_count=5078345`. The first trusted event time is **2022-09-01 00:00:00+00:00**; the last is 2022-09-18 16:18:00+00:00. The exact warm-up cutoff is **2022-09-02 00:00:00+00:00**. All **1,114,921** events with `t < cutoff` have `incomplete`, `scoreable=0`, with eight null history values; all **3,963,424** with `t >= cutoff` have `full`, `scoreable=1`; **unavailable=0** and misclassified rows **0**. At 2022-09-01 23:59 there are **606 incomplete**; at the inclusive cutoff 2022-09-02 00:00 there are **961 full**. The production CLI supplies `coverage_start=first.event_time_utc`, the replay default is `missing_intervals=()` and `coverage_available=True`; therefore no gap or unavailable reason contributes to this IBM count. A direct real incomplete-snapshot scorer probe raised `ValueError: score request lacks full, scoreable coverage` (exit 0 for the assertion). An independent JSON check showed all eight historical fields null in an incomplete snapshot and all eight nonnull in a full snapshot.

The *third* operation is semantic scoring repeat, not feature rebuild: `PYTHONPATH=backend/src .venv/bin/python -S /tmp/fraudlens_t025_probe.py` exited **0**, read only three scoreable operational events plus matching complete snapshots and printed scores `0`, `0.65`, `0.65`, `semantic_repeat=true`. Each was scored under two run IDs; after excluding run ID and `scored_at`, both assessments in each pair matched. `-S` and `RuleScorer.requires_artifact=False` confirm rules-only execution without installed model/provider packages. This sample does not establish model performance.

### Final-review commands and outputs

All commands ran from the repository root. The following SQL statements were executed through `python3` using `sqlite3.connect('file:...rules-work.sqlite?mode=ro', uri=True)` and `PRAGMA query_only=ON`, exit **0**:

```sql
SELECT version,feature_version,status,snapshot_count FROM feature_builds;
SELECT COUNT(*),MIN(json_extract(payload_json,'$.event_time_utc')),MAX(json_extract(payload_json,'$.event_time_utc')) FROM operational_events;
SELECT coverage_state,scoreable,COUNT(*),MIN(event_time),MAX(event_time),MIN(coverage_start),MAX(coverage_start) FROM feature_snapshots GROUP BY coverage_state,scoreable;
SELECT SUM(event_time<'2022-09-02T00:00:00+00:00'),SUM(event_time>='2022-09-02T00:00:00+00:00'),SUM(event_time='2022-09-02T00:00:00+00:00'),SUM(event_time='2022-09-01T23:59:00+00:00') FROM feature_snapshots;
SELECT event_time,coverage_state,scoreable,COUNT(*) FROM feature_snapshots WHERE event_time IN ('2022-09-01T23:59:00+00:00','2022-09-02T00:00:00+00:00') GROUP BY event_time,coverage_state,scoreable;
SELECT COUNT(*) FROM feature_snapshots WHERE (event_time<'2022-09-02T00:00:00+00:00' AND (coverage_state!='incomplete' OR scoreable!=0)) OR (event_time>='2022-09-02T00:00:00+00:00' AND (coverage_state!='full' OR scoreable!=1));
```

| Command | Exit | Observed |
|---|---:|---|
| `git branch --show-current` / `git rev-parse HEAD` / `git status --short --untracked-files=all` | 0 each | Branch and HEAD above; all prior Phase 4 edits present and preserved. |
| `.venv/bin/python -m pytest -q --tb=line backend/tests/contracts/test_data_scoring.py -k test_available_rule_explanation_matches_source_scale_and_score` before fix | 1 | 3 failed, all because mismatched available rule explanations were accepted. |
| `.venv/bin/python -m pytest -q backend/tests/unit/test_feature_history.py backend/tests/unit/test_feature_lineage.py backend/tests/integration/test_feature_store.py backend/tests/contracts/test_data_scoring.py backend/tests/unit/test_rule_scoring.py` after fix | 0 | **107 passed**. |
| `.venv/bin/python -m pytest -q backend/tests` | 0 | **572 passed**, one existing Starlette/httpx warning. |
| `.venv/bin/ruff check backend/src backend/tests` | 0 | `All checks passed!` |
| `PYTHONPATH=backend/src .venv/bin/python -S /tmp/fraudlens_t025_probe.py` | 0 | Three real scores and semantic repeats as above. |
| `PYTHONPATH=backend/src .venv/bin/python -S -c 'from fraudlens.rule_scoring import POLICY_SHA256, RuleScorer; print(POLICY_SHA256, RuleScorer.requires_artifact)'` | 0 | Frozen policy hash and `False`. |
| `git diff -- backend/src/fraudlens/scoring.py` | 0 | Empty: Foundation v1 scorer untouched. |
| `git ls-files data/raw data/processed` | 0 | Empty; no raw CSV or SQLite database tracked. `git check-ignore -v` matched `/data/raw/` and `/data/processed/` for the CSV, original and work-copy databases. |
| `git diff --check` | 0 | No tracked-diff whitespace errors. |
| Local Markdown link check over next_work, tasks, quickstart, data-model, offline contract and this evidence | 0 | 131 relative links checked, 0 missing files. |

Reviewed file SHA-256 values after the scorer correction: `feature_history.py` `7fecb0a303918b5ed2c21997a3a20ef2052f17a30f6a8f58c23a3bebab62663e`; `rule_scoring.py` `2401bc322888d505b1d6ce8d9683c1900ef869fa360d4aeeaa1028c4aa3f679b`; `data_contracts.py` `f0822718817d10d344913ceab4d95ad0acdfe82f79bc69ce41e4cbe4b4b447b8`; `data_store.py` `9212c5ec3bff4968dd41a9baea0ffd4aa156400712b68045b5fc9b215b817b7e`. The current offline-contract raw SHA-256 is `2654f4e2bab0a17b15bc71e885307dc44912159047b8f764a0a444ceb365ee3d`; the historical T017 value `359c5e16292d5475cb64e559a30ecf1ecf682557c7d5445d13744d8e00a8dbeb` remains an earlier-byte record. This Phase 4 documentation addendum changes that file's bytes without changing its frozen catalog or rule policy. The approved Phase 3 source/mapping hashes remain in their earlier evidence.

Technical conclusion: T017–T025 satisfy the rules-only Phase 4 criteria after the targeted boundary fix and are **technically ready for a later reviewed push**. T026 is the first open task. No trained-model SC-003 completion, scientific evaluation, completed scored run, v2 API/frontend integration, team signoff for this final review, commit or push is inferred.

## T020 concurrent feature-build correction — 2026-11-13

- [Original correction prompt](../../prompts/development/002-t020-concurrent-feature-build-fix-2026-11-13.md). Started on `002-data-and-risk-scoring` at published HEAD `0f5ad9ac0b04cc406e3c19b0f1934da4cc29d10d` with a clean working tree. This is a synthetic SQLite correction after the Phase 4 publication above; the historical review and its hashes remain unchanged.
- Confirmed fault: two `DatasetStore` connections could build the same `(dataset_version, feature_version)` concurrently. The second reset the first `staged` row and published three snapshots. The first then hit a `UNIQUE` constraint and its unconditional exception handler deleted the second's snapshots. The metadata still claimed `complete`, `snapshot_count=3`, while the actual row count was `0`; retry returned `dataset_incompatible`.
- The new deterministic interleaving test calls the second connection inside the first connection's batch callback, after the first has entered `staged`. Before correction, `.venv/bin/python -m pytest -q --tb=short backend/tests/integration/test_feature_store.py -k concurrent_build_cannot_erase_published_snapshots` exited **1**: **1 failed**, `published=3, actual=0, retry=dataset_incompatible`, with the first attempt's `UNIQUE constraint failed: feature_snapshots.version, feature_snapshots.feature_version, feature_snapshots.transaction_id`. This is the intended RED reason.
- Fix: a nonblocking operating-system file lock keyed by resolved SQLite path plus `(dataset version, feature version)` surrounds the entire build, including cleanup and publication. An overlapping caller gets `feature_build_in_progress` (CLI exit 2 with that error code). The lock is released by the OS if the owner exits, so an abandoned `staged` row remains recoverable on the next attempt. The lock file stays in place to avoid unlink races; its contents do not enter the database or snapshots. Only the owner holding the lock can write or clean that key. Snapshot schema, payload, digest, ordering and `history-v1` values are unchanged; no IBM replay is required.
- After correction, the interleaving test verifies the published count and actual rows are both **3**, all three snapshots are readable, and retry returns `{'snapshot_count': 3, 'repeated': True}`. A second test verifies the controlled CLI response while the owner is staged. Existing interruption, abandoned-stage recovery, bounded 512-row batches and same-version repeat checks remain in the SQLite suite.

| Executed command from repository root | Exit | Actual result |
|---|---:|---|
| `.venv/bin/python -m pytest -q --tb=short backend/tests/integration/test_feature_store.py -k concurrent_build_cannot_erase_published_snapshots` before fix | 1 | 1 intended RED failure with published 3, actual 0, retry `dataset_incompatible`. |
| Same targeted command after fix | 0 | 1 passed, 5 deselected (before the added CLI-specific case). |
| `.venv/bin/python -m pytest -q backend/tests/integration/test_feature_store.py` after both regressions | 0 | 7 passed, including interruption/restart, abandoned-stage recovery, bounded batches and CLI idempotence. |
| `.venv/bin/python -m pytest -q backend/tests/integration/test_feature_store.py backend/tests/integration/test_data_store.py` | 0 | **20 passed** across feature SQLite/CLI and existing datastore integration. |
| `.venv/bin/python -m pytest -q backend/tests` | 0 | **574 passed**, one pre-existing Starlette/httpx deprecation warning. |
| `.venv/bin/ruff check backend/src backend/tests` | 0 | `All checks passed!` |
| `git diff --check` | 0 | No tracked-diff whitespace errors. |
| `.venv/bin/python --version` | 0 | `Python 3.14.7`. |
| `stat -f '%N %z bytes' data/processed/feature-002-ibm-v8.sqlite data/processed/feature-002-ibm-v8-rules-work.sqlite` | 0 | Both existing IBM databases remain: **7,559,012,352** and **12,443,103,232** bytes. Neither was opened for a new build/import. |

The lock changes build coordination only; no snapshot content or format changed.
The full IBM replay was therefore not rerun. T026 remains the first open task;
this correction was not committed or pushed in this session.

### Separate CLI process verification and publication gate — 2026-11-13

[Original publication request](../../prompts/development/002-t020-concurrent-feature-build-publication-2026-11-13.md). The original regression above used two connections in one Python process. A new synthetic integration case starts two separate `python -m fraudlens.pipeline_cli build-features` processes against the same temporary SQLite file. A test-only `sitecustomize.py` in `tmp_path` pauses the first process after its staged row exists. The second CLI exits **2** with `feature_build_in_progress`; releasing the first gives a complete build with **3** snapshots. A new connection reads all 3 rows, and a third CLI process reports `repeated: true` with the same count. The hook and SQLite database are temporary, not repository artifacts. The published Phase 4 HEAD and remote both initially resolved to `0f5ad9ac0b04cc406e3c19b0f1934da4cc29d10d`.

| Executed command from repository root | Exit | Actual result |
|---|---:|---|
| `git ls-remote --heads origin 002-data-and-risk-scoring` | 0 | Remote `0f5ad9ac0b04cc406e3c19b0f1934da4cc29d10d`; equal to starting local HEAD. Initial sandbox attempt exited 128 because DNS was unavailable; authorized network retry succeeded. |
| `.venv/bin/python -m pytest -q backend/tests/integration/test_feature_store.py -k separate_cli_processes` | 0 | **1 passed, 7 deselected**; separate CLI processes, controlled overlap, readable complete snapshots, idempotent retry. |
| `.venv/bin/python -m pytest -q backend/tests/integration/test_feature_store.py backend/tests/integration/test_data_store.py` | 0 | **21 passed**. |
| `.venv/bin/python -m pytest -q backend/tests` | 0 | **575 passed**, one existing Starlette/httpx deprecation warning. |
| `.venv/bin/ruff check backend/src backend/tests` | 0 | `All checks passed!` |
| `git diff --check` | 0 | No whitespace errors. |

This verification changes the test suite and documentation only; the existing lock fix and snapshot format are unchanged. T026 remains the first open task.
