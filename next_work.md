# Next work - FraudLens AI
Updated 2026-11-13 Europe/Belgrade. Historical specification-start HEAD: 33bcf62.
Current observed branch: model-implementations, created from `002-data-and-risk-scoring` at `27ac7d49e3d638717c752dce225216d291bf9e87`. Phase 3 was rebased over remote documentation through `6952f1d`. Use `git log -1` for the resulting Phase 3 commit SHA; earlier `182d0b2` references are historical review baselines.

## T028 dependency and resource pilot complete — 2026-11-13

On `model-implementations` from starting HEAD
`a2857cdfce02b9d60b2b8c3c276a2500081cbad5`, [T028 evidence](evidence/tasks/feature-002-resource-pilot.md)
records CPython 3.14.10 / Windows x64, locked NumPy 2.5.4, SciPy 1.18.1 and
scikit-learn 1.9.1, with no existing locked package versions changed. The
bounded actual-source pilot processed 100,000 consecutive rows through the
canonical importer and `history-v1`, producing 100,000 snapshots in 145.315 s;
peak working set was 285,134,848 bytes and peak temporary files were
262,063,538 bytes under enforced 3 GiB / 4 GiB / 30-minute limits. The records
are all within warm-up, so none are scoreable. Pilot files were removed and the
original CSV hash remained unchanged. No model fit or holdout access occurred.
T028 is checked complete.

The existing backend check collected 105 cases: 99 passed and six failed in
CLI binding assertions because Windows CRLF mapping bytes differ from the
normalized approved mapping hash; this is the previously recorded checkout
line-ending issue. The other 99 cases pass when those six cases are deselected;
Ruff and `git diff --check` pass. The requested IEEE reference-analysis file is
absent in this checkout, and the booster candidates remain outside T031's
approved grid. This does not alter the current scikit-learn plan.

One concrete next step: **T029** — freeze and hash `feature_002_v1.json`, exact
eligible split membership, and the predeclared resource/fit ceilings before
any model fitting or validation selection.

## T027 immutable temporal protocol GREEN — 2026-11-13

On `model-implementations` from T026 HEAD `fe310c1a7213655b47cc2ffb22554fc39b4e2acf`,
[T027 implementation and commands](evidence/tasks/feature-002-protocol.md#t027-green-implementation--2026-11-13)
added a deterministic, immutable split manifest and offline label eligibility
join for Feature 002. The T026 suite now has **25 passing** cases; focused
history/scoring focused regressions had **78 passing** cases on the final
rerun. Ruff and `git diff --check` passed. The full backend run had
**594 passed, 6 failed**: existing import CLI integration tests compare the
mapping's pinned LF-byte hash to a CRLF working copy generated under Git
`core.autocrlf=true`. The tracked mapping is unchanged; normalizing CRLF to
LF in memory matches HEAD exactly. No dataset import, model fit, metric or
holdout access occurred. The unrelated uncommitted contribution-report edit
remains preserved.

One concrete next step: **T028** — verify the Python 3.14 ML dependencies and
run the prescribed resource pilot, recording actual limits. Resolve the
mapping checkout line endings separately before claiming a full green backend
suite.

## T026 chronological protocol RED tests — 2026-11-13

On `model-implementations` from Feature 002 HEAD `27ac7d49e3d638717c752dce225216d291bf9e87`,
[T026 synthetic test matrix and commands](evidence/tasks/feature-002-protocol.md)
cover whole-timestamp 70/15/15 splits, warm-up and coverage exclusions,
membership before private-label eligibility, class/positive minimums,
explicit ineligibility and provenance failures. Test collection exited 0
with **20 cases**; execution exited 1 with **19 intended RED failures** at
the missing `fraudlens.evaluation.build_split_manifest` behavior and **1
passing replay fixture check**. Ruff and `git diff --check` passed. The
downstream assertions remain unverified until T027. No evaluator, model,
IBM import, training, metrics or holdout access occurred. An unrelated
uncommitted contribution-report edit remains preserved.

One concrete next step: **T027 GREEN** — implement immutable split/eligibility
state, run the T026 assertions through completion and record results in the
protocol evidence.

## T020 concurrent feature-build correction — 2026-11-13

[Original request](prompts/development/002-t020-concurrent-feature-build-fix-2026-11-13.md);
[RED reproduction and GREEN evidence](evidence/tasks/feature-002-feature-rules.md#t020-concurrent-feature-build-correction--2026-11-13).
Started from published Phase 4 HEAD `0f5ad9ac0b04cc406e3c19b0f1934da4cc29d10d`
on `002-data-and-risk-scoring`, with a clean tree. A two-connection synthetic
regression reproduced the T020 race: published 3, actual 0, retry
`dataset_incompatible` after the first attempt erased the second's complete
snapshots. A per-database, per-version OS lock now gives an overlapping attempt
the controlled `feature_build_in_progress` result and preserves the owner's
complete build. The corrected test confirms three readable snapshots and a
successful idempotent retry; the CLI also reports the controlled error.
Interrupted/abandoned staged recovery and 512-row batch behavior remain covered.
Targeted SQLite/CLI **20 passed**, full backend **574 passed** with one existing
warning, Ruff and `git diff --check` exited 0. Before publication, a further
[separate-CLI-process regression](evidence/tasks/feature-002-feature-rules.md#separate-cli-process-verification-and-publication-gate--2026-11-13)
confirmed the in-progress response, three readable snapshots, and a successful
retry; the updated targeted suite passed **21** and the full backend **575**.
Snapshot content and format are unchanged, so the IBM replay was not repeated;
the original and working IBM databases remain local. T017's stale statement
about open T018/T019 was removed. Publication details are recorded in Git.

One concrete next step: start **T026** RED tests for chronological partitioning
and protocol eligibility, keeping private labels outside scoring inputs.

## Phase 4 final technical review — 2026-11-13

[Original request](prompts/development/002-phase-4-final-review-2026-11-13.md);
[task-by-task review, corrected scorer-boundary regression and read-only IBM coverage audit](evidence/tasks/feature-002-feature-rules.md#final-phase-4-technical-review--2026-11-13).
On `002-data-and-risk-scoring` at HEAD `55306089b506458fcaec9b621f49c00dd971d46e`,
all uncommitted T017–T025 work was preserved. One confirmed T022 defect allowed
an available rules explanation with a model method, wrong scale or contributions
not reconstructing the score; three regression cases were RED and then GREEN.
The existing IBM work copy was read only: 5,078,345 event-valid facts and distinct
complete snapshots, 3,963,424 full, 1,114,921 incomplete, **0 unavailable**.
All incomplete snapshots fall before the exact 2022-09-02 00:00 UTC warm-up
boundary; there are no other missing-coverage causes in this build. An actual
incomplete event was rejected by the scorer. The full replay and `repeated=true`
build remain distinct prior runs; three real-event scores repeated semantically
across run IDs. Targeted **107 passed**, full backend **572 passed** with one
existing warning, Ruff and `git diff --check` passed. The offline contract and
quickstart now reflect the implemented local build and corrected rule boundary.
Foundation v1 scorer is unchanged. No IBM reimport, full replay rerun, original
database/CSV modification, model fit, commit or push occurred. T017–T025 remain
complete as a rules-only Phase 4 increment; trained-model SC-003, evaluation
and public v2 integration remain later work.

One concrete next step: start **T026** RED tests for chronological partitions
and protocol eligibility, keeping private labels outside scoring inputs.

## Prompt 3 T022–T025 complete — 2026-11-13

[Original request](prompts/development/002-t022-t025-prompt-3-request-2026-11-13.md);
[RED/GREEN and actual-source rules evidence](evidence/tasks/feature-002-feature-rules.md#t022t025-prompt-3-scorer-and-rules-completion--2026-11-13).
On `002-data-and-risk-scoring` at HEAD `55306089b506458fcaec9b621f49c00dd971d46e`,
the uncommitted T017–T021 work was preserved. T022's original 35 RED cases are
GREEN; the expanded v2 scorer boundary has 36 passing cases. T023 collected 10
cases and failed only because `rule_scoring` was absent; T024's final 13 rule
cases are GREEN with frozen Decimal `rules-v1` policy hash
`a281d38b8777b53882f4515dda7de927ff64dce43188e99c258419b1d605b5ce`.
The full IBM feature replay ran against the ignored copy
`data/processed/feature-002-ibm-v8-rules-work.sqlite`: **5,078,345 complete
snapshots**, of which **3,963,424 full** and **1,114,921 incomplete**. The
repeat build was idempotent. Three actual-source scoreable events gave rule
scores `0`, `0.65`, `0.65`; each pair matched semantically across two run IDs
after excluding run ID and actual scoring time. The original database hash
remained `a7a9495557f5462a8d08d0e31f7d0a81e54c3df10e07ddb2617b4194d7bea8cf`.
The full backend suite passed **569 tests** with one existing Starlette/httpx
warning; Ruff and `git diff --check` passed. No model training, IBM reimport, original database modification,
commit or push occurred. T022–T025 are checked in `tasks.md`; trained-model
SC-003 and later workflow remain open.

One concrete next step: start T026's Phase 5 RED tests for chronological
partitioning and evaluation protocol, using the existing complete source
and keeping private labels outside scoring inputs.

## T021 v2 scorer boundary RED complete — 2026-11-13

[Original T021 request](prompts/development/002-t021-scorer-boundary-red-request-2026-11-13.md);
[35-case RED matrix and observed results](evidence/tasks/feature-002-feature-rules.md#t021-v2-scorer-boundary-red--2026-11-13).
On `002-data-and-risk-scoring` at HEAD `55306089b506458fcaec9b621f49c00dd971d46e`,
the existing uncommitted T017–T020 work was preserved. T021 has **35 collected**
synthetic contract cases; collection exits 0, execution exits 1 with **35 expected
test-body failures**, all at the missing `ScoreRequestV2` boundary in
`fraudlens.data_contracts`. The fixture's full coverage, identity and as-of
preconditions were separately checked. Individual validation assertions remain
unverified until T022 GREEN. Ruff and `git diff --check` pass. No production scorer,
IBM replay, existing SQLite database, commit or push was touched. T021 is checked
in `tasks.md`; T022 remains open.

One concrete next step: implement T022 `ScoreRequestV2` and the fail-closed v2
scorer validation boundary, then run these 35 cases GREEN without changing
Foundation v1 scoring.

## T020 feature replay and local build complete — 2026-11-13

[Original T020 request](prompts/development/002-t020-feature-replay-green-request-2026-11-13.md);
[RED/GREEN commands, test correction and synthetic SQLite/CLI evidence](evidence/tasks/feature-002-feature-rules.md#t020-replay-and-local-feature-build-green--2026-11-13).
Branch `002-data-and-risk-scoring`, HEAD `55306089b506458fcaec9b621f49c00dd971d46e`;
all uncommitted T017–T019 work was preserved. Starting RED repeated: **50 failed**
for absent `fraudlens.feature_history` (exit 1). The `history-v1` replay,
closed catalog, lineage checks, local `build-features` CLI and gated SQLite
snapshot storage now pass **50 T018/T019 tests** plus **5 synthetic integration
tests**. One authored expected count was corrected from 2 to 1 because the
source-start event lay 36 hours before the target. Full backend: **520 passed**
with one existing Starlette/httpx warning; Ruff and `git diff --check` passed.
The CLI reads a complete provenance-bound version via an event-time SQL cursor,
writes 512-row batches and exposes only complete builds. No IBM replay, existing
IBM SQLite write, model training, commit or push occurred. T020 is checked in
`tasks.md`; T021 remains open.

One concrete next step: write and run T021 v2 scorer-boundary RED tests in
`backend/tests/contracts/test_data_scoring.py` before implementing T022.

## T018/T019 RED completed on synthetic facts — 2026-11-13

[Original T018/T019 request](prompts/development/002-t018-t019-red-request-2026-11-13.md);
[criterion-to-test matrix, hand values and commands](evidence/tasks/feature-002-feature-rules.md#t018t019-synthetic-red-matrix--2026-11-13).
Branch `002-data-and-risk-scoring`, HEAD `55306089b506458fcaec9b621f49c00dd971d46e`;
the uncommitted T017 contract/evidence/prompt changes remain preserved. T018 has
14 collected replay cases and T019 has 36 collected lineage cases. Collection
exited 0; execution exited 1 with 50 intended test-body failures because the
T020 `fraudlens.feature_history` module does not yet exist. The authored
assertions cover all 11 features, window/tie/held-out/coverage/label invariance,
bank and currency direction, and fail-closed predictor/source/unknown rules.
Ruff and `git diff --check` exited 0. T018/T019 are checked in `tasks.md` as
completed RED tasks; T020 remains open. No IBM import, SQLite write, commit or
push occurred. These tests are not GREEN verification or model evaluation.

One concrete next step: implement T020 pure timestamp-group replay and
versioned feature catalog/projection boundary, then run the 50 RED cases GREEN.

## T017 feature catalog and rule policy frozen — 2026-11-13

[Original T017 request](prompts/development/002-t017-feature-rules-request-2026-11-13.md);
[contract, synthetic vectors, exact commands and hashes](evidence/tasks/feature-002-feature-rules.md).
Started on clean `002-data-and-risk-scoring` at HEAD
`55306089b506458fcaec9b621f49c00dd971d46e`; this work remains local.
`history-v1` now freezes 11 directional, label-free features with exact
inputs, units, availability, permitted consumers and missing semantics.
`rules-v1` freezes R1/R2/R3 at `3/3/3`, Decimal weights `0.35/0.30/0.35`,
exact R3 threshold and an ordinal sum. Window `[t−24h,t)`, tied-time groups,
context-only first 24 h and full/incomplete/unavailable coverage are explicit.
Synthetic hand calculations and an in-memory verification passed, including
the exact R3 equality `40*3 = 2*60`, score `1.00`, below-threshold `0.65`,
measured zero and no score for deficient coverage. Rule-policy SHA-256 is
`a281d38b8777b53882f4515dda7de927ff64dce43188e99c258419b1d605b5ce`.
The offline contract's T017 raw SHA-256 is
`359c5e16292d5475cb64e559a30ecf1ecf682557c7d5445d13744d8e00a8dbeb`;
the Phase 3 and T007/T008 hashes remain historical. Mapping/data-model bytes
are unchanged. No IBM import, SQLite write, backend RED/GREEN tests, model
evaluation, commit or push was run. T017 is checked in `tasks.md`; T018/T019
remain open and T020 has not begun.

One concrete next step: write and run T018's hand-calculated replay RED tests
in `backend/tests/unit/test_feature_history.py`, followed by T019 lineage RED.

## Phase 3 final cleanup verified — 2026-11-13

[Original request](prompts/development/002-phase-3-final-cleanup-2026-11-13.md);
[RED/GREEN, full IBM replay and read-only evidence](evidence/tasks/feature-002-import-identity.md#phase-3-final-cleanup--2026-11-13);
[executable quickstart](specs/002-data-and-risk-scoring/quickstart.md). Starting
revision and confirmed remote were both `b5f75211c9a6aa5befa602f04308918df98ac106`.
The importer now checks the SHA-256 and byte count of the exact stream parsed
before marking a new version complete. Synthetic in-place, replacement and
size-change regressions pass while preserving an older complete version.
Targeted tests **85 passed**, full backend **465 passed**, Ruff and
`git diff --check` passed. The new ignored IBM v8 SQLite import completed
all **5,078,345** rows in **1,315.29 s**, and the same-command replay returned
`repeated=true` in **13.41 s**. DatasetVersion, S/M/T, all counts and the
whole-file database hash match; read-only verification found 5,078,345 unique
D and C IDs, schema 1, `quick_check=ok` and reconciled row equations. The
original database is unchanged. The offline contract text has a separate
documentation-only hash record; the approved mapping bytes are unchanged.
T015/T016 remain complete. T060 full later quickstart coverage, another
teammate's independent reproduction and later scoring/v2 integration remain
open. One concrete next step after this cleanup publication: start **T017**
feature-catalog and RulePolicy freeze in a separate authorized session.

## Phase 3 T015/T016 import complete — 2026-11-13

[Original request](prompts/development/002-t015-t016-complete-and-publish-2026-11-13.md); [CLI RED/GREEN and actual IBM import/replay evidence](evidence/tasks/feature-002-import-identity.md#t015-local-cli-implementation--2026-11-13). T015 source-bound local import CLI passes its 3 new integration cases and preserves inspect/Foundation v1; T016 imported all **5,078,345** declared IBM v8 records with **5,078,345 event-valid**, 0 rejected, **5,078,345 label-eligible**, 5,177 positives and 5,073,168 negatives. The identical replay returned the same `dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802` without changing the SQLite file hash. Read-only SQL found 5,078,345 distinct D and C IDs and `quick_check=ok`. Source S and reviewed mapping M stayed unchanged. The ignored database is 7,559,012,352 bytes; no real data are staged.

Backend **462 passed** with one preexisting Starlette/httpx warning; targeted T009–T015 **82 passed**; Ruff and `git diff --check` passed. T015/T016 are checked in `tasks.md`. The remote feature branch advanced by three documentation commits (to `6952f1d`) while this local work was underway. Rebase retained those commits and the reviewed five final-byte files, including executable M `a816260a…093e57`; intermediate remote approval hashes are marked historical in the reconciled evidence. Historical sections below describe prior states.

One concrete next step after this Phase 3 publication: start T017 feature-catalog and RulePolicy freeze in a later authorized session. No Phase 4 code was started here.

## T012–T014 GREEN completed on synthetic inputs — 2026-11-13

[Original request](prompts/development/002-t012-t014-green-2026-11-13.md); [actual RED/GREEN commands, test corrections and limitations](evidence/tasks/feature-002-import-identity.md#t012t014-green-on-authored-inputs--2026-11-13). Branch `002-data-and-risk-scoring`, HEAD `182d0b290c8819e602fc5d77e8df8e904228b032`; earlier local changes retained. T012 internal canonical/private/report/version models, T013 reviewed-policy streaming parser and D/C/`dv_` identity, and T014 staged/complete/failed SQLite store with private table, bounded batches, reconciliation, immutable replay and restart safety are implemented. The CLI still has no import command; mapping `import_allowed=false` and actual IBM import was not run.

Initial RED repeated: **79 failed**, exit 1. After GREEN and two contract-aligned test corrections, targeted **79 passed**, exit 0; full backend **459 passed**, exit 0, with one preexisting Starlette/httpx warning. Ruff passed, exit 0. The first full regression revealed a helper-name collision with the read-only inspector (23 failures); the new canonical helper was renamed and the final full suite passed. Approved mapping/offline hashes stayed unchanged. The [reproducible authored-only smoke](evidence/tasks/feature-002-green-smoke.py) passed for bound-stage import, exact money, private-status gating, immutable replay and restart. T012–T014 are checked in `tasks.md`; T015/T016 remain open. Historical RED/pending sections below describe earlier states.

One concrete next step: T015 — wire the approved source hash, namespace/member and streaming iterator to the local import CLI, preserving the explicit import-disabled gate until a separately reviewed execution policy enables actual IBM import; then perform T016 in its own evidence step.

## Completed T009–T011 RED and next GREEN unit — 2026-11-13

[Original Prompt 2 continuation](prompts/development/002-t009-t011-complete-red-2026-11-13.md); [requirement-to-test matrix and actual commands](evidence/tasks/feature-002-import-identity.md#completed-t009t011-red-matrix--2026-11-13). Branch `002-data-and-risk-scoring`, HEAD `182d0b290c8819e602fc5d77e8df8e904228b032`; preexisting local work preserved. The 20 existing RED tests were retained and expanded in their three files to cover T009 CSV boundaries, malformed/encoding/partial files, exact money/time and private labels; T010 pre-filter/multiline/rejected-row identity, namespace/member/version distinctions, collision and replay; T011 unsupported SQLite schema, label-private operational boundary, reconciliation, interrupted/new-version retry/restart and same-version idempotence.

Final collection **79 tests**, exit 0. Final execution **79 intended RED failures**, exit 1, all in test bodies for missing T013 parser/identity or T014 SQLite repository; no collection/environment errors. Ruff on the three test files and `git diff --check` passed, exit 0. These are synthetic authored tests, not IBM import or GREEN verification. T009, T010 and T011 are checked as completed RED tasks in `tasks.md`; T007/T008 remain complete. Import remains disabled (`import_allowed=false`) and no application import/store implementation was added.

One concrete next step: implement T012 canonical/import models, then T013 parser/identity and T014 SQLite store against this RED suite; run it GREEN and relevant Foundation regressions before progressing to T015/T016.

## Collective T007/T008 approval and next RED work — 2026-11-13

[User confirmation](prompts/development/002-t007-t008-final-team-approval-2026-11-13.md) reports that the entire team approved the final mapping, D/C and `dv_` identity/hash rules and v2 contracts with strict `DatasetVersionId`, with no blocking objections. [Collective approval, reviewed uncommitted diff against HEAD `182d0b290c8819e602fc5d77e8df8e904228b032`, full SHA-256 table and current match check](evidence/tasks/feature-002-t007-t008-team-review-2026-11-13.md#collective-final-byte-approval-conveyed-by-the-user); [source audit](evidence/tasks/feature-002-source-audit.md#collective-final-mapping-approval--2026-11-13); [contract review and later migrations](evidence/tasks/feature-002-contract-review.md#collective-final-v2-contract-approval--2026-11-13). All five approved file hashes match the prior final-byte evidence exactly; no later edits to those approved files were found. No individual roles/signatures were inferred. This session ran `git diff --check` from repository root: exit 0, no output or working-diff whitespace errors. T007 and T008 are now **complete** in `tasks.md`. Earlier pending-review sections below are historical.

[Existing 20-test RED record](evidence/tasks/feature-002-import-identity.md) collected successfully and failed for missing parser/identity/SQLite behavior, but is **partial** against the explicit T009–T011 matrices. T009 still lacks zero and supported-scale boundaries, unsupported labels and the full T004 structural/header/encoding/partial-file import cases and predictor exclusion. T010 lacks explicit rejected-row and quoted-multiline identity stability, mapping/release/source-member changes as separate version scenarios, deliberate digest/fact collisions and repeat-import identity checks. T011 lacks schema-version mismatch, private-label role exclusion, changed-version coexistence/retry after failure, injected parser failure and restart reconciliation. Thus T009, T010 and T011 remain **open**; T012–T014 GREEN is not yet the next task. Import remains disabled (`import_allowed=false`); no IBM import or v2 runtime integration occurred in this approval-recording session.

One concrete next step for the user's independent implementation: complete and run the missing T009 synthetic RED cases in `backend/tests/unit/test_data_import.py`, then finish T010/T011 RED before beginning T012–T014 GREEN.

## Current technical corrections and preparatory RED — 2026-11-13

[Exact request](prompts/development/002-t007-t008-fixes-and-t009-t011-red-request-2026-11-13.md); [corrected current hashes, vectors and checks](evidence/tasks/feature-002-t007-t008-team-review-2026-11-13.md#codex-correction-and-preparatory-red-verification--2026-11-13); [T009–T011 RED evidence](evidence/tasks/feature-002-import-identity.md). Branch `002-data-and-risk-scoring`, unchanged HEAD `182d0b290c8819e602fc5d77e8df8e904228b032`; earlier local edits and historical evidence preserved.

The two Codex findings are technically resolved: v2 `DatasetVersionId` now requires `dv_` plus exactly 64 lowercase hex digits and absolute end; all three examples and negative schema tests agree. Mapping/data model explicitly bind N=`source.namespace`, F=`source.member`, separately framed. Current LF/normalized mapping M `a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57`; raw CRLF hash `9a87e1ddaad2c6825d76111eae4fdcf54e2bec5ed0c7c25685b1ea8a0dd42ae1`, whose normalized M is equal. Synthetic blank/label-1 versions are `dv_55e9a2fe16d796aa75aa917f82c516b92caeb7d91fc2f3ee59efc757fca0bb3d` / `dv_33e5d9754468adc36e4ceb77a71c4e1e7ab0faad94cd37da29f8e5282b809dfa`; D/C unchanged. Current full hashes are in the linked evidence; earlier M/vectors below are historical. No new technical blocker found.

Targeted v2/mapping tests: **34 passed**; existing backend regression excluding new RED files: **380 passed**; frontend **151 passed**; reproducible hash script, Ruff and `git diff --check` exited 0. The user's explicit preparatory exception produced **20 collected** synthetic T009–T011 tests (collection exit 0), then **20 intended failures** (test exit 1) for missing parser/identity/SQLite behavior. These are partial RED coverage, not completed T009–T011 or GREEN. T007/T008 remain open solely for actual final-byte producing/affected-consumer review with real date, findings/decision and remaining migrations; no signatures are inferred. T009–T011 checkboxes remain open; import and v2 runtime integration remain disabled/unimplemented. Historical validation and three branch-comparison EOF warnings remain separate.

One concrete next step: obtain and record actual final-diff review for data/scoring and affected v2 consumers, then complete the remaining T009–T011 RED cases before starting T012–T016 GREEN.

## Codex review of final local diff — 2026-11-13

[Original request](prompts/development/002-final-local-diff-review-request-2026-11-13.md); [technical findings, exact hashes, component impact and commands](evidence/tasks/feature-002-t007-t008-team-review-2026-11-13.md#codex-technical-review-of-the-final-local-diff--2026-11-13). The user's earlier joint team technical direction remains recorded separately in that evidence. This review inspected the working diff against full HEAD `182d0b290c8819e602fc5d77e8df8e904228b032`, including untracked evidence, without changing mapping/contract/schema behavior or assigning individual approvals.

T007 mapping preserves directional bank/account roles, exact paid/received Decimal and named currencies, raw minute time with explicit synthetic UTC+00 analysis assumption, and private labels outside operations. Repeated D/C and old/current `dv_` vectors matched; current LF mapping M is `e82903264382ae710b8b93ce43a3e37d954ec6a6629414e217b698664e6769d6`, equal to the normalized CRLF M. Actual source SHA-256 matches. Read-only full mapped inspect parsed 5,078,345 rows and exited 2 for the still-disabled review gate. Foundation v1 code/contracts are unchanged; 375 backend and 151 frontend tests passed.

**Technical corrections before freeze:** v2 JSON Schema accepts impossible `dv_` shapes although the new recipe requires exactly 64 lowercase hex digits; its examples/tests use those short shapes. The mapping still describes D/C as “proposed”, and the data model ambiguously describes whether the member is inside the namespace before the byte recipe appends it. Align these texts/schema/examples/tests with the adopted recipe, then recalculate mapping M and vectors if mapping bytes change. T007/T008 also still require real final-diff producing/affected-consumer review with date, findings/decision and remaining migrations; the prior joint direction did not supply that review. Thus T007/T008 remain unchecked; T009–T011 remain not started by dependency, and import remains disabled. Backend active-run/list-detail checks, frontend v1/v2 decoding and investigation/priority adapters are later integration, not implemented here. No commit/push.

One concrete next step: correct the two documented identity/contract inconsistencies, recalculate the final hashes/vectors, and present that exact diff to the actual producing and affected-consuming reviewers for the required recorded review before starting T009–T011.

## Current T007/T008 team direction and gate — 2026-11-13

The user [communicated the team's joint technical decision](prompts/development/002-t007-t008-team-decision-and-red-request-2026-11-13.md) adopting the handoff's byte-level D/C and `dv_` recipes, LF-normalized mapping hash in a separate review record, and the current v2/strict Foundation v1 direction. [Decision, current hashes, old/new vectors and actual checks](evidence/tasks/feature-002-t007-t008-team-review-2026-11-13.md); [macOS handoff and prior proposal](evidence/tasks/feature-002-macos-handoff.md); [source audit](evidence/tasks/feature-002-source-audit.md); [contract review](evidence/tasks/feature-002-contract-review.md). HEAD remains `182d0b290c8819e602fc5d77e8df8e904228b032`; the working diff is uncommitted and earlier local changes are preserved.

Current candidate M is `e82903264382ae710b8b93ce43a3e37d954ec6a6629414e217b698664e6769d6` after removing self-referential `approved_mapping_sha256`; source S and policy T remain pinned. The existing historical manifest is unchanged. The reference commit's mapping M and the changed working M yield different synthetic `dv_` vectors; D/C remain stable under a label-only change. Targeted mapping/v2/Foundation tests passed **122/122**; the reproducible hash/vector script, source SHA-256 check, Ruff and working `git diff --check` passed. A premature exploratory 8-failure RED run was removed when the final owner-review gate was recognized; no RED test files or GREEN implementation remain.

**Status:** T007/T008 open because the new final working bytes and component impacts still need actual producing/affected-consuming review with real status, date, findings/decision and remaining migrations. The user's joint direction is recorded without individual signatures or invented component findings. T009–T011 not started; import remains `false` and the CLI has no import command. The prior proposal and earlier pending-review sections below are historical snapshots. No browser, IBM import, v2 runtime integration or model evaluation occurred in this session.

One concrete next step: actual data/scoring, frontend/API, investigation and priority/simulation reviewers inspect the current working diff and hash table in the linked decision record, then communicate their real review outcome and remaining migrations; only then close T007/T008 and start Prompt 2 RED tests.

## T007 byte-level identity and hash proposal — 2026-11-13

[Proposal, actual in-memory command and synthetic vectors](evidence/tasks/feature-002-macos-handoff.md#t007-reproducible-identity-and-hash-proposal--2026-11-13-not-approved); [exact user request](prompts/development/002-identity-hash-proposal-request-2026-11-13.md). Against commit `182d0b290c8819e602fc5d77e8df8e904228b032`, proposed D/C identities use domain-separated SHA-256 over UTF-8 length-framed namespace/member and U64BE pre-filter ordinal; `dv_` uses the raw 32-byte source, normalized-mapping and existing time-policy digests in fixed order. A read-only Python calculation produced stable D/C IDs for a label-only synthetic change, distinct `dv_` values, and the same proposed mapping SHA-256 after LF/CRLF normalization. These are **proposal checks only**, not T009–T011 execution or IBM import.

One concrete next step: actual data/scoring and affected-consuming owners decide whether to adopt the exact byte framing/domain/output recipe, LF-normalized full-file mapping hash, and separate approval record pinned to final mapping bytes; they must also decide how final review state and import enablement are represented without a self-referential hash. Record real names, dates, findings and decisions before freezing T007/T008. Current mapping/manifest/contracts/importer are unchanged, `import_allowed=false`, T007/T008 remain open and T009–T011 still depend on T008.

## macOS local verification and owner-review preparation — 2026-11-13

[Actual commands, versions, exits, source scan, Git hash audit and owner questions](evidence/tasks/feature-002-macos-handoff.md); [original verification prompt](prompts/development/002-macos-verification-request-2026-11-13.md); [documentation continuation](prompts/development/002-macos-review-handoff-request-2026-11-13.md). This documentation handoff uses the clean verification commit above as its reference and remains uncommitted.

- Locked uv sync succeeded after moving the cache to a writable local path; npm ci succeeded. Backend 375 passed, frontend 151 passed, Ruff and typecheck/build passed. In-process fixture smoke passed five HTTP assertions after setting `PYTHONPATH`. Initial default-cache sync and first smoke import failed; both attempts and retries are recorded in the evidence. No browser or live-server result was supplied or claimed.
- Local CSV SHA-256 matched the source manifest. Read-only mapped inspect parsed 5,078,345 rows in 25.76 s, then exited 2 for `pending_team_review`; `complete_parse=true` and `import_allowed=false`. No import, model evaluation or Prompt 2.
- Git review-hash audit: 5/15 manifest values match raw Git bytes and 10/15 match only after LF→CRLF conversion. The manifest remains unchanged; full raw Git hashes for mapping and three v2 contracts are in the evidence. Branch comparison with `origin/initialization` reports three pre-existing blank-line-at-EOF findings; worktree `git diff --check` was clean during verification.
- T007/T008 remain unchecked. The mapping still has `pending_team_review`, `executable_mapping=false` and `import_allowed=false`; no actual owner review, approval or independent teammate reproduction is inferred.
- [T009–T011 technical findings and proposed tests](evidence/tasks/feature-002-macos-handoff.md#t009t011-technical-findings-and-proposed-tests--not-executed) are documentation only and unexecuted: valid `Euro` versus rejected `EUR`, bank-qualified accounts, separate money scales, missing private label, pre-filter ordinals, interrupted new-version import, idempotent same-version reimport and the two distinct label-only/hash checks. The next implementation step T009–T011 depends on completed T008; no RED tests were written.

One concrete next step: the actual data/scoring, frontend/API, investigation and priority/simulation owners review the pinned commit and raw Git hashes, then record their real names, dates, findings, decisions and remaining migrations in the source-audit/contract-review evidence before considering the T007/T008 gates. T009–T011 implementation follows only after T008 is complete.

## Current Prompt 1 technical resolution — 2026-11-13

**T001–T006 complete; T007/T008 technical work complete, actual team review pending.**
[Resolution and actual commands](evidence/tasks/feature-002-technical-resolution.md),
[current review hashes](evidence/tasks/feature-002-technical-resolution.json),
[user technical approval](prompts/development/002-technical-resolution-request-2026-11-13.md).

- Authorized download fetched only pinned Kaggle v8 HI-Small_Trans.csv into
  ignored data/raw/release-verification/v8-20261113-approved/. HTTP 200 text/csv;
  no account or extra tool/dependency install needed. Both CSVs are 475,664,283
  bytes and SHA-256 b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040.
  Original before/after hashes unchanged. Adopt v8 as the reproducible reference;
  original acquisition history remains unknown. [Receipt](evidence/tasks/feature-002-verify-v8.json).
- Publisher metadata identifies CDLA-Sharing-1.0 for version 8 at transfer time.
  IBM reference code supports Account directions and binary 1=laundering /
  0=non-laundering for these synthetic labels. [Semantics](evidence/tasks/feature-002-source-semantics.json).
  No source timezone, synchronization or lifecycle-stage fact was invented.
- [Technical mapping](data/mappings/ibm_hi_small_v1.json) binds exact headers,
  Account positions 2/4, source hash/member/v8 namespace, decimal/currency/label
  policy and the user-approved explicit synthetic UTC+00 analysis assumption.
  Raw timestamp text/minute ties are preserved. Configuration remains
  pending_team_review, executable_mapping=false and import_allowed=false; actual
  producing/affected-consuming review entries remain pending/null.
- Feature 002 schema/API/offline contract now contain currency length 17,
  required detail-envelope dataset_version and equality obligations, strict end
  assertions, exact source-bound duplicate exception and explicit assumed-clock
  discriminator. Examples/data model/spec/plan/research/quickstart are aligned.
  Foundation v1 application/schema/fixture/frontend/order/banner/locks unchanged.
- Inspect supports --mapping for read-only observation; generic inspection
  remains strict. Full mapped scan: 5,078,345 records, complete_parse=true,
  controlled exit 2 pending_team_review, import_allowed=false. No import command,
  model training, activation or v2 application/decoder integration exists here.
- RED: 21 intended mapping/schema failures in test bodies. GREEN: 57 targeted;
  after additional boundary/example checks, full backend **375 passed**, frontend
  **151 passed**, Ruff/typecheck/build passed. Existing Starlette/httpx warning only.
  No human review, independent teammate reproduction, model result or Phase 2
  assignment compliance inferred. No commit/push; current branch preserved.

One concrete next step: have the actual data/scoring producer, frontend/API and
affected investigation/priority owners review the current hash manifest and
record their real findings/decisions. Keep T007/T008 unchecked and import disabled
until the required gates are satisfied. Do not start Prompt 2 from this handoff
without its separate authorization. Absolute source clock/lifecycle claims would
still need publisher evidence; the approved analysis assumption resolves only
this prototype's coordinate policy.

## Prior Prompt 1 investigation/proposal handoff — 2026-11-13

Independent research and concrete proposal work is complete; T006–T008 remain
unchecked because provenance/decisions/review are still pending. [Investigation](evidence/tasks/feature-002-source-investigation.md),
[review packet](specs/002-data-and-risk-scoring/proposals/README.md),
[mapping draft](specs/002-data-and-risk-scoring/proposals/source-mapping.json),
[exact v2 patch proposal](specs/002-data-and-risk-scoring/proposals/v2-contract-changes.json).

- Public unauthenticated Kaggle metadata verifies current version 8 (2025-07-08)
  and CDLA-Sharing-1.0 on that listing. HI-Small member size matches the local
  475,664,283 bytes, but no publisher checksum was returned. Exact local release
  and original acquisition history remain unknown; v8 is a candidate reference.
- IBM's pinned official formatter supports sender Account at index 2 paired with
  From Bank and receiver Account at index 4 paired with To Bank. It parses naive
  minute timestamps and does not establish a source timezone or clock semantics.
- Mapping draft requires exact source-bound ordered-header/Account occurrence
  validation, separate sides, exact Decimal/source currencies, proposed 13 integer
  digits/scales 0–6/zero support and pre-filter CSV ordinal identity. Namespace,
  selected time policy, approved mapping/time hashes and reviewers remain null.
- Core v2 proposal: currency maxLength 17; required detail-envelope dataset_version;
  strict terminal-pattern fixes. Optional separate assumed_utc_for_synthetic_benchmark
  basis requires an explicit team decision; it is not a source UTC fact. Default
  import block remains. Public transaction version is checked internally and via
  detail/assessment/list/run equality; future semantic validators remain unimplemented.
- Corrected prior standalone-schema probe construction (root oneOf was retained).
  Proper probes demonstrate current ID/money final-newline acceptance and the
  candidate fix. Review probes pass; [exact hashes/results](evidence/tasks/feature-002-proposal-validation.json).
- No account access, dataset/PDF download, product/authoritative contract changes,
  import, training, activation or messages. No application tests rerun in this
  documentation slice; prior 346/151 results below remain historical. No commit/push.
  Baseline was clean at 63d3384; branch and existing work preserved.

One concrete next step: review the packet and supply retained provenance, or
authorize its single-file pinned-v8 verification, then record actual producer and
affected-consumer decisions before freezing mapping/contracts. Exact download,
hash comparison and missing-document steps are in the packet and were not run.

## Initial Feature 002 inspection handoff — 2026-11-13

This update supersedes planning-era source-absent/not-implemented statements below
for the inspection slice only. T001–T005 complete; T006 partial on source provenance;
T007 `pending_mapping_review`; T008 `pending_consumer_review`. [Implementation ledger](evidence/tasks/feature-002-implementation.md),
[source audit](evidence/tasks/feature-002-source-audit.md), [contract review](evidence/tasks/feature-002-contract-review.md).

- Read-only streaming `fraudlens.pipeline_cli inspect` and 36 authored inspection
  tests implemented. Only inspect is available; no import/model/run/v2 integration.
  Artifact ignore rule added and checked before local report generation.
- Local authorized `data/raw/HI-Small_Trans.csv`: 475,664,283 bytes;
  SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`;
  5,078,345 records; label tokens 0=5,073,168 and 1=5,177. These are source counts,
  not event-valid/supervised/model metrics. User supplied acquisition date/source;
  exact Kaggle release remains unknown. IBM upstream data-license statement
  verified; applicability to the exact acquired release remains pending.
- Duplicate `Account` headers at positions 2/4; minute timestamps without timezone;
  amount scales 2/6; currency names reach 17 characters, exceeding proposed v2
  maxLength 12. Mapping/namespace/time-policy hashes not frozen; no mapping file
  created. Contract review records a separate detail-version wording inconsistency.
- Actual source scan returned controlled exit 2 (`duplicate_headers`,
  `provenance_incomplete`), with complete observations; source hash verified unchanged.
  Small sanitized evidence is prepared for Git; full report remains ignored/local.
- Initial RED: 30 intended missing-inspector failures in test bodies. GREEN: 30,
  then 36 inspection tests after extra form/option assertions. Lexical-summary
  follow-up: 2 RED/34 passing, then 36 GREEN. Final backend 346 passed; frontend
  151 passed; Ruff/typecheck/build passed. Existing Starlette/httpx warning remains.
  Foundation v1 code, schema, fixture and frontend unchanged.
- Phase 2 source lookup complete, compliance `pending_requirements_unavailable`.
  Human code/mapping/contract review and independent reproduction pending.
  No download, training, substantive evaluation, browser run, commit or push.

One concrete next step: obtain exact acquired-release evidence and actual
producer/affected-consumer decisions for duplicate-header direction, timezone,
currency bounds and detail-version wording before starting import.

## Current state
Feature 001-project-foundation completed/accepted in its local synthetic-demo scope:
T001-T028 checked. Vedran Mitic confirms joint setup verification and human
code/contracts/evidence review by all team members. No individual signatures or
separate-machine installations claimed. Historical pending entries superseded.
- Peer results: 310 backend passed (exit 0), 151 frontend passed, Ruff,
  typecheck/build, health/UI/retry and 404/422 results recorded.
- Project Python 3.14.3; system py 3.14.7; Node 24.20.0; npm 11.19.0; uv 0.10.9.
- Prior temp permission errors resolved through unique workspace temp/cache paths.
- Known Starlette/httpx warning remains, no outstanding failure reported.
- Evidence: evidence/tasks/peer-reproduction.md, human-review.md,
  phase-06-handoff.md and foundation-validation.md. Browser evidence remains the
  historical T019 run; no new browser/test run during acceptance recording.

Feature **002-data-and-risk-scoring planning history** (current inspection progress above):
- [Specification](specs/002-data-and-risk-scoring/spec.md): import/provenance, historical
  features and rules, bounded ML comparison, local explanations and dataset-backed case review.
- [Quality checklist](specs/002-data-and-risk-scoring/checklists/requirements.md): agent
  document review recorded; human, Phase 2, technical-plan and implementation gates
  remain open. No unresolved clarification markers.
- [Specification evidence](evidence/tasks/feature-002-specification.md) and
  [original request](prompts/development/002-data-and-risk-scoring-specification.md).
- [Technical plan](specs/002-data-and-risk-scoring/plan.md),
  [research decisions](specs/002-data-and-risk-scoring/research.md),
  [data model](specs/002-data-and-risk-scoring/data-model.md),
  [v2 contracts](specs/002-data-and-risk-scoring/contracts/api.md),
  [quickstart](specs/002-data-and-risk-scoring/quickstart.md) and
  [Codex prompts](prompts/development/002-implementation-prompts.md) are drafted.
  [tasks.md](specs/002-data-and-risk-scoring/tasks.md) now contains the generated
  implementation plan. Source audit, mapping approval, affected-consumer contract
  review, implementation and actual Feature 002 verification remain pending.
- [Adversarial review transcript](prompts/development/002-review.md) is reflected in the
  revised specification: label-independent event history, meaningful rule baseline,
  temporal/threshold/evaluation safeguards, import/run completion, contract migration,
  acceptance scenarios and a proposed contributor code/task handoff. See
  [revision evidence](evidence/tasks/feature-002-specification.md).
- Authoritative Phase 2 assignment requirements remain unavailable; the checklist
  is not that source and no Phase 2 compliance claim is made.
- No IBM dataset downloaded/audited, no model trained, no dependencies or product code changed.
- Defaults: chronological 70/15/15, strict past-only history, label-free operational data,
  one deployed explainable model compared to rules. AutoML is optional and bounded.
- Foundation's fixed-size IDs and amount/currency limits require explicit reviewed contract
  migration; do not relax validators or lose source precision silently.
- The preceding planning request authorized technical planning and future
  prompts only. No Feature 002 implementation was performed by that unit.

## Historical next step before the inspection slice
Start Feature 002 T001: create the implementation evidence ledger with the actual
working revision, original implementation prompt and environment after reading
AGENTS.md and this handoff. The next implementation slice is source-independent
inspection; its RED/GREEN tasks are T004–T005 after the setup/ignore prerequisites.
Use [tasks.md](specs/002-data-and-risk-scoring/tasks.md) for exact dependencies.
Select specs/002-data-and-risk-scoring explicitly in each PowerShell session.
The current request authorizes planning-to-tasks only; implementation requires a
later work request. No automatic commit/push is authorized for this unit.
Preserve existing local changes and the Foundation v1 fixture checks.

## Contribution evidence report added 2026-11-12

- Added [consolidated evidence and contribution plan](evidence/tasks/project-evidence-plan-2026-11-12.md),
  with the complete 19-commit ledger through f63bffe, three identifiable contributors,
  task-level attribution, shared T019 credit and future evidence/time capture plan.
- [Reproducible calculation](evidence/tasks/project-evidence-calculations-2026-11-12.json)
  gives 10.76 provisional person-hours centrally, 7.17–14.34 under explicit
  publication-window assumptions. These are not measured hours or confidence bounds.
  No work/hours assigned to an unnamed fourth member, per current user clarification.
- Documentation only; no application tests/browser runs, feature implementation,
  acceptance marker changes or Git commit/push. Historical runtime/test results above
  remain unchanged. See report for source limitations and participant confirmation needs.
- Audit verification passed: calculation script; 19-row Git/date/author reconciliation;
  independent arithmetic; 43 local links; UTF-8/fences/whitespace/helper syntax;
  historical test-count reconciliation. Source inventory covers 69 pinned files.
- This contribution report does not authorize implementation; the current next
  development step is Feature 002 task generation described above.

## Feature 002 technical-plan handoff added 2026-11-12

- See [planning evidence](evidence/tasks/feature-002-technical-plan.md) and
  [original request](prompts/development/002-technical-plan-request-2026-11-12.md).
  The plan and supporting research/data/API/scoring contracts, JSON Schema,
  quickstart and eight future Codex prompts are documentation proposals.
- The current shell lacks an invokable Python 3.14 and `jsonschema`; JSON parse,
  internal schema references, example arithmetic and 52 local Markdown links
  were checked with Python 3.13.3. `git diff --check` passed. No application
  tests or IBM import/model run occurred.
- `data/artifacts/` is not yet ignored by Git. The first implementation slice
  must add/check that ignore rule before artifact generation. Raw/processed
  paths are already ignored. Source audit, Phase 2 document, contract review,
  tasks, human review and independent reproduction are open.
- This handoff preserves existing local edits and makes no Git commit/push.

## Documentation publication request — 2026-11-12

- The user explicitly requested commits and a push for all pending documentation;
  see the [original publication request](prompts/development/002-publication-request-2026-11-12.md).
  That instruction supersedes earlier no-commit/no-push statements for this
  session. It does not expand Feature 002 implementation scope.
- The [contribution report addendum](evidence/tasks/project-evidence-plan-2026-11-12.md)
  names the four publication commits and their distinct contents. The historical
  19-commit time calculation remains pinned and does not count unmeasured hours
  from these documentation commits.
- Verify the current local/remote branch state with Git. The concrete next
  development step remains Feature 002 tasks.md generation and source/contract
  audit; human, Phase 2, dataset and implementation gates remain open.

## Feature 002 task-generation handoff added 2026-11-13

- Generated [tasks.md](specs/002-data-and-risk-scoring/tasks.md) using the local
  speckit-tasks skill: 67 unchecked tasks, explicit dependencies, RED before GREEN,
  five story increments and separate source audit, mapping and consumer gates.
  Coverage tables allocate every FR-001–026 and SC-001–009 to work, tests and
  future evidence. They do not establish requirement satisfaction.
- [Task-generation evidence](evidence/tasks/feature-002-task-generation.md) records
  inputs, commands, execution-policy/launch limitations and unrun work.
  [Static inspection inventory](evidence/tasks/feature-002-task-plan-validation.json)
  records 35 requirement rows, 23 existing paths and 51 explicitly planned paths;
  no document-order/coverage-reference/undeclared-path issues were reported.
  The [inspection script](evidence/tasks/feature-002-task-plan-validation.ps1)
  only reads planning text and file metadata; it does not run application checks.
- IBM source is absent under data/: T006 remains pending_source_unavailable;
  mapping T007 and dependent source work remain pending. T008 requires actual
  producer/consumer review. Phase 2 remains pending_requirements_unavailable;
  human explanation/code review and independent reproduction remain pending.
- No application/lockfile/v1 contract changes, dependency installs, downloads,
  import, training, model metrics, backend/frontend tests or browser runs occurred.
  Historical Foundation evidence is unchanged. No commit, push or branch switch
  was issued. The 2026-11-12 publication request above is historical; this unit
  follows the current explicit no-commit/no-push instruction.
