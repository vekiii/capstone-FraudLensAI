# Prompt 1 technical resolution — T006–T008

2026-11-13 Europe/Belgrade. [Actual user approval/authorization](../../prompts/development/002-technical-resolution-request-2026-11-13.md). Baseline branch `002-data-and-risk-scoring`, HEAD `63d33843bc6483d66362e10133ec21c261c76df1`. The preceding investigation/proposal changes were already uncommitted at task start; they were preserved and extended within the requested scope. Applicable AGENTS.md then next_work.md, complete proposals/, source audit/review/evidence, T006–T008 and affected contracts/code/tests were read; Feature 002 explicitly selected. No branch switch, reset, commit or push.

**T006 source audit/source-reference verification complete. T007/T008 technically prepared/amended, pending actual team review.** User technical approval is recorded separately from producer/affected-consumer review. No named reviewers, dates, decisions or approvals are invented. This is not Prompt 2 or full Feature 002 acceptance.

## Verified source reference and release-specific license

Only the authorized HI-Small_Trans.csv member was requested from the explicit pinned Kaggle v8 endpoint. [Reproducible verifier](feature-002-verify-v8.py), [actual download receipt](feature-002-verify-v8.json).

```text
Request: https://www.kaggle.com/api/v1/datasets/download/ealtman2019/ibm-transactions-for-anti-money-laundering-aml/HI-Small_Trans.csv?datasetVersionNumber=8
Original: data/raw/HI-Small_Trans.csv
Reference: data/raw/release-verification/v8-20261113-approved/HI-Small_Trans.csv
Both sizes: 475664283 bytes
Both SHA-256: b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040
```

HTTP 200, text/csv; the file was delivered directly, not as an archive. Download 2026-11-13 05:03:19–05:03:39 UTC (06:03 local). The original before/after hash matches; the separate reference remains intact and ignored. Adopt **Kaggle v8 equivalence as the reproducible reference**, exactly as authorized. Original acquisition date was user-declared earlier; exact original acquisition/version history remains unknown. Equal bytes may appear in multiple releases, so this is not a reconstruction of download history.

The verification request also read the publisher's public metadata at download time: dataset ID 2948142, currentVersionNumber 8, lastUpdated 2025-07-08T14:59:13.28Z, data license **CDLA-Sharing-1.0**. The receipt binds those version/license observations to the explicitly pinned v8 member transfer and matching hash. IBM's pinned README separately distinguishes the same data license from repository Apache-2.0. No repository code license was substituted for data licensing. This identifies the publisher's release license; no independent legal opinion is claimed.

No Kaggle account, credential file, CLI installation, temporary third-party tool or project dependency change was needed: the existing project Python 3.14.7 standard library performed the authorized download. Public redirects were followed without printing/storing signed URLs or cookie/token headers. Only the final host name is retained. No patterns/accounts or other dataset member, PDF, application artifact or model was downloaded. The verifier refuses an existing destination/oversized/non-file response and preserves successful evidence on repeat; it can rehash the saved reference without redownloading.

## Documented semantics versus assumptions

- Account direction: publisher [formatter at pinned revision](https://raw.githubusercontent.com/IBM/Multi-GNN/31d5d4578c9f1b9bc89a890a5b344787ee39e6ee/format_kaggle_files.py) pairs From Bank with zero-based column 2 and To Bank with column 4. The two observed raw Account headers remain unchanged. No Account.1 alias, header rename or plain bank/account concatenation is used.
- Binary meaning: [pinned IBM loader](https://raw.githubusercontent.com/IBM/Multi-GNN/11056bb128b6048ecc94ec4fe9dec2cc0a4a3e7e/data_loading.py), lines 26/28, reads Is Laundering unchanged and calculates illicit count as sum(y). Together with the observed literal binary domain, this supports **1=synthetic laundering, 0=synthetic non-laundering**. This is publisher reference-implementation evidence, not an inference from prevalence or a claim of a prose definition. Exact source revision/hash/line references are in [semantics evidence](feature-002-source-semantics.json). It is not a legal finding.
- Timestamp: source is timezone-free minute text. No source timezone, cross-bank synchronization or booking/value/settlement-stage meaning was established. These remain unknown source facts.
- Approved assumption: the user selected synthetic-common-wall-clock-fixed-offset-zero-v1, basis assumed_utc_for_synthetic_benchmark, as a common synthetic UTC+00 analysis coordinate. Preserve raw text/minute ties; pad seconds to 00 only as a coordinate convention. Never derive offset from the host, banks or currencies. The selected policy/hash is explicit in the mapping; actual scored_at remains real execution UTC. This resolves the analysis policy without inventing source UTC or clock comparability evidence.

The existing full source audit's 5,078,345 records, 0/1 counts, missingness, headers/dialect/ASCII-compatible UTF-8, date range, 2/6 decimal scales and currencies remain actual local observations. The complete mapped reinspection confirms those counts/ranges; it is not canonical import accounting or a model evaluation. No label/time tail analysis, holdout join, split change or training occurred. The previously documented publisher tail warning remains a later protocol-design limitation, not permission to tune on labels now.

## Applied technical mapping and contracts

[Technical mapping](../../data/mappings/ibm_hi_small_v1.json) now fixes the exact source/member/hash/v8 namespace and eleven positions. Original bank/account strings, separate paid/received Decimal text and fifteen currency names are retained. The selected 13-integer-digit/0–6-scale/zero-allowed policy is explicitly a design choice beyond observed scales 2/6 and no observed zeros. Unsupported forms, unknown fields/currencies and any schema drift remain rejection/review conditions. Private labels never become predictor/analyst fields. Identity policy remains specified only; no canonical events/IDs were generated.

The mapping has pending_team_review, executable_mapping=false, import_allowed=false and only inspect in allowed_commands. All four required review entries remain pending/null. The selected policy has a real technical content hash; approved_mapping_sha256 remains null. Technical file hashes are review inputs, not signoff. [Current hash manifest](feature-002-technical-resolution.json) records exact mapping/schema/API/offline contract bytes for producing and consuming owners.

Applied only the approved schema changes: currency maxLength 17; required CaseDetailV2 envelope dataset_version; six strict end assertions; and explicit assumed-clock basis. API examples now use a long source currency name, raw minute text and the assumption discriminator. The API requires detail/assessment/list/completed-run version equality and an internal canonical-transaction version check, while public TransactionV2 has no dataset_version property. Snapshot/run equality remains mandatory. Schema alone cannot enforce cross-object equality: tests/probes explicitly retain that limitation. Typed runtime backend/decoder checks belong to the later coordinated integration and are **not implemented or claimed here**.

The offline contract now permits only the exact source-bound duplicate pair for inspection and records the pending team/import gate. Feature spec/plan/research/data model/quickstart/data policy and proposal archive status are aligned. Exact historical pre-amendment contract text is retained in proposals/technical-amendment-baseline.json to reproduce original patch preconditions. Foundation v1 models/schema/API/fixture/frontend, its case ordering/unconditional banner, locks, dependencies and shared governance files remain unchanged.

## RED → GREEN and actual checks

Existing environment: CPython 3.14.7, pytest 9.2.0, jsonschema 4.26.0, Ruff 0.17.4; Node 24.20.0/npm 11.19.0. No dependency install or lockfile change. Commands below from repository root unless stated otherwise; each exit was checked independently.

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/002-data-and-risk-scoring'
git check-ignore -v data/raw/release-verification/v8-20261113-approved/probe.zip data/artifacts/probe.json
.\.venv\Scripts\python.exe evidence/tasks/feature-002-verify-v8.py
# Network escalation for the authorized transfer; exit 0, matching hashes, original preserved.
.\.venv\Scripts\python.exe -m pytest backend/tests/unit/test_source_mapping_inspection.py backend/tests/contracts/test_v2_design_amendments.py -q --tb=short --basetemp .cache/feature002-resolution-red-20261113 -p no:cacheprovider
# exit 1: 21 intended failures in collected test bodies; missing mapping argument/CLI,
# missing currency/detail/clock amendments and permissive terminal matching.
.\.venv\Scripts\python.exe -m pytest backend/tests/unit/test_source_inspection.py backend/tests/unit/test_source_mapping_inspection.py backend/tests/contracts/test_v2_design_amendments.py -q --tb=short --basetemp .cache/feature002-resolution-green-20261113 -p no:cacheprovider
# exit 0: 57 passed after implementation.
.\.venv\Scripts\python.exe -m pytest backend/tests/unit/test_source_inspection.py backend/tests/unit/test_source_mapping_inspection.py backend/tests/contracts/test_v2_design_amendments.py -q --basetemp .cache/feature002-resolution-green2-20261113 -p no:cacheprovider
# exit 0: 57 passed after declaration/review-register/source-size hardening.
.\.venv\Scripts\python.exe -m pytest backend/tests/unit/test_source_mapping_inspection.py backend/tests/contracts/test_v2_design_amendments.py -q --tb=short --basetemp .cache/feature002-resolution-boundaries-20261113 -p no:cacheprovider
# exit 0: 29 passed after eight additional malformed-config/example/boundary checks.
.\.venv\Scripts\python.exe evidence/tasks/feature-002-proposal-validation.py
# exit 0: historical patch preconditions and actually applied definitions agree;
# fifteen currency names, strict endings, examples, pending mapping/review/import flags checked.
.\.venv\Scripts\python.exe -m pytest backend/tests -q --basetemp .cache/feature002-resolution-regression-20261113 -p no:cacheprovider
# exit 0: 375 passed, existing Starlette/httpx deprecation warning only.
.\.venv\Scripts\python.exe -m ruff check backend evidence/tasks/feature-002-verify-v8.py evidence/tasks/feature-002-proposal-validation.py
# exit 0: all checks passed.
# From frontend/:
npm.cmd test -- --run
# exit 0: 151 passed in five files.
npm.cmd run build
# exit 0: TypeScript check and Vite build succeeded.
```

Mapped actual inspection command, with PYTHONPATH=backend/src:

```powershell
.\.venv\Scripts\python.exe -m fraudlens.pipeline_cli inspect --source data/raw/HI-Small_Trans.csv --mapping data/mappings/ibm_hi_small_v1.json
```

Actual exit **2**, `pending_team_review`, complete_parse=true, row_count=5078345, import_allowed=false. It preserves duplicate_header_groups [2,4] while recognizing only the exact approved technical pair; source_timezone=null and approved assumption are explicit. Report is local ignored `data/artifacts/feature-002-v8-mapped-inspection.json`; current manifest records its hash. Generic inspection remains strict and does not silently whitelist duplicates. No file/store/active-state writes occur in inspection. Tests prove mismatched source/hash/declarations and missing member fields, reordered/case/whitespace/missing/extra-target headers, forged review flags, self-enabled import, changed policy hash and malformed/duplicate-key/invalid-byte mapping failures are controlled; original source-independent encoding/header/partial-parser negatives remain intact. Extra contract probes check the updated authored examples and explicitly show schema-only semantic equality limits.

Mechanical documentation patch-context mistakes and an abandoned formatting-preservation helper failed without applying changes. They are not RED tests. Actual v2 object equality against the approved patch is checked; no unrelated schema bounds were changed. Source download/reference and ignored artifact boundaries were verified before generation. No tests, browser runs, scientific results, team review or second-person reproduction are inferred.

## Remaining requirements and one next step

Final static verification passed: 36 changed/new files, 144 resolving local links,
UTF-8/JSON/code fences, exactly six completed task markers and 61 open tasks,
and all current review-input hashes. `git diff --check` exited 0. Original schema
layout was restored after asserting the parsed amended object stayed identical;
proposal validation passed again and its final byte hash is in the manifest.
No test behavior changed in that formatting step. A final local verifier repeat
rehashes both CSVs without redownloading and exits 0. Ignore/tracked-file checks
confirm raw/processed/artifact/evaluation paths remain untracked. The Foundation
boundary `git diff --exit-code HEAD -- backend/src/fraudlens/contracts.py backend/src/fraudlens/cases.py backend/src/fraudlens/scoring.py backend/src/fraudlens/settings.py backend/src/fraudlens/main.py frontend data/fixtures specs/001-project-foundation uv.lock pyproject.toml .gitignore .agents .specify`
exited 0. Branch and HEAD are unchanged; all original raw bytes are preserved.

No remaining account/download/license/binary-label evidence step blocks this adopted reference. Source timezone, lifecycle stage, cross-bank synchronization and original acquisition history remain unavailable facts; the approved synthetic-clock policy is clearly separate. Absolute real-world timing claims would require new publisher evidence. The Phase 2 assignment remains unavailable under its separate earlier gate; no course-compliance claim.

Required producing/affected-consuming owners must actually review the current mapping/time policy/canonical/scoring/API/schema changes and migration obligations, with real participants, dates and findings. **T007 and T008 remain unchecked; no import-ready freeze or v2 integration is claimed.** One concrete next step: conduct that owner review against the current hash manifest and record actual decisions. No Prompt 2, dataset import, model training, activation, application v2 integration, team messages, commit or push was performed.


## Collective team approval update ? 2026-11-13

The user confirms the team works jointly on project code and documentation and that one member?s approval represents the team. The user explicitly approved T007 and T008; this is recorded as collective project-team approval conveyed by the user. Individual owner names are not asserted.

- T007 mapping review: approved collectively on 2026-11-13; approved mapping SHA-256: `27445724712e9bca6f0d22ac991a2f923a18d5df33fc79a41c852244cd439699`.
- T008 producer/consumer contract review: approved collectively on 2026-11-13; the reviewed Feature 002 contract hashes remain the ones in the technical-resolution manifest. The v1 compatibility boundary is preserved.
- This collective approval closes the T007/T008 review gates. Import remains disabled pending implementation of an import command; no runtime importer or v2 application integration is claimed.
