# Feature 002 T007/T008 joint technical direction and working bytes

- Date: 2026-11-13, Europe/Belgrade.
- Source of decision: [the user's original message relaying the team's agreement](../../prompts/development/002-t007-t008-team-decision-and-red-request-2026-11-13.md). The user reports a **joint team technical decision** for T007/T008. No individual participation, signature, component-specific finding or second-person run was supplied or inferred.
- Technical baseline: `182d0b290c8819e602fc5d77e8df8e904228b032` on `002-data-and-risk-scoring`, plus the uncommitted working diff listed below. The prior local modifications to `next_work.md` and the macOS handoff/prompts were preserved. The user-relayed decision preceded these final edited bytes; no final hash-specific owner confirmation was supplied.
- Earlier technical proposal and vectors: [macOS handoff](feature-002-macos-handoff.md#t007-reproducible-identity-and-hash-proposal--2026-11-13-not-approved). That section remains an accurate historical **proposal at the reference commit**; this record documents subsequent adoption and revised mapping bytes.

## Joint decision communicated by the user

Adopt the handoff's exact domain-separated D/C identity recipe and three-digest `dv_` recipe. D/C derive solely from reviewed namespace, exact source member and one-based CSV record ordinal before filtering. Use the first 128 SHA-256 bits for public D/C suffixes while keeping full digests, framed inputs and observable-fact digests for collision checks. A label-only change alters source hash and `dv_`, not D/C. An edited IBM v8 file cannot claim the pinned original source hash.

Adopt SHA-256 of the entire mapping's UTF-8 bytes after CRLF-to-LF replacement, with no other byte changes. Store the calculated digest in this separate record, outside the mapping; the former self-referential `identity.approved_mapping_sha256` field was removed. This record does not become part of the mapping hash. Any later change to hashed mapping content, including review or execution fields, yields a new M and needs its own review before import. Preserve the historical manifest as the initial byte-check record. The calculated final M below is **pending confirmation against the final diff by the actual producing and affected-consuming reviewers**; it is not an invented final-file approval.

Keep Foundation v1 closed and unchanged and retain the current separate v2 list/detail format. The backend later verifies detail against the active complete run, snapshot and dataset version; the frontend later strictly decodes v1/v2 and checks list/detail consistency. Investigation and priority/simulation later consume versioned, label-free operational facts under existing provenance, explanation and ordering rules. Private labels and eligibility stay out of API, scoring, feature, investigation and priority/simulation inputs. Import uses exact mapping currency names (`Euro` is valid, `EUR` is not). These are component obligations, not assignments or claims that migrations have been implemented.

The current mapping continues to be a read-only **inspection configuration** with `pending_team_review`, `executable_mapping=false` and `import_allowed=false`. These embedded historical status/review fields were not converted into fabricated individual approvals. The separate joint decision adopts the technical direction; T007/T008 remain open until the final changed bytes and component impact receive actual review. No import command exists, and activation remains prohibited until later implementation explicitly checks a confirmed review record, matching M, source hash and import-enable policy. The existing inspector's raw-file SHA-256 is informational and does not serve as a normalized M approval check.

## Technical findings and calculated hashes

This section reports Codex calculations and checks, distinct from the team's decision above. SHA-256 values below are of actual working-file bytes after this documentation/mapping diff, unless labeled otherwise. The raw Git blobs at the reference commit were checked in the [macOS handoff](feature-002-macos-handoff.md); 10 of 15 historical manifest hashes match only after LF→CRLF conversion. The manifest was not rewritten.

| Item | SHA-256 / value |
|---|---|
| Exact original IBM v8 CSV bytes, expected in mapping | `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040` |
| Reference-commit mapping raw Git blob / old normalized M (LF) | `0b0b85db9cc18cf959bbef80e5899707a3895cef147b6c1c0ae696b96645cc0b` |
| Reference mapping with CRLF, raw bytes (historical manifest) | `4a8200f72c3fcd8f1d0c1ce99dd054a37d0972e4159c23c803174cdefaf207bf` |
| Current mapping raw working bytes / normalized M (LF), pending final review | `e82903264382ae710b8b93ce43a3e37d954ec6a6629414e217b698664e6769d6` |
| Existing selected time-policy T | `67a408fc52e57035115186c3c9863dfeac5a72d709292e0f7baeef560086d781` |
| Current `contracts/api.md` raw working bytes | `8836ec9cf15f610d840384ca78247e549ed55ddafbaa971bcbdd008b27e3a1ed` |
| Current `contracts/data-and-scoring.md` raw working bytes | `534de0c70a6ecbec69dd8734d6fec5830a9814da81fa508afe16a0f1dcca9918` |
| Current `contracts/schemas.json` raw working bytes | `9e93f40da78381d280da52a2a6ea421837e14c7d46420ccc85a41f1b404c0fc7` |
| Current `data-model.md` raw working bytes | `7f885086a3388f0077b887638b7f85d0a67247f53c3822317c8ed3515cf575f2` |

The source hash is of exact CSV bytes and is never normalized. The inspector reports the mapping's **raw** SHA-256. M normalizes only CRLF pairs and equals the raw hash on the LF checkout; a CRLF checkout has a different raw hash but identical M. T hashes only selected-policy canonical JSON, not the entire mapping. S, M and T are included as full **32-byte digests** in `dv_`, not concatenated hex strings. Mapping JSON validity and duplicate-key rejection are separate input checks.

## Identity vectors

These are synthetic algorithm checks, not IBM import or T009–T011 test results. The seven-record input and the command body are preserved in the [handoff](feature-002-macos-handoff.md#executed-in-memory-vector-check). Namespace `synthetic:fraudlens-review:v1`, member `review-7.csv`, ordinal 7, and target row with paid `100.00 Euro`, received `99.123456 Bitcoin` and empty private label. The variant changes only the label to `1`; the observable facts and row position remain fixed. Both variants have `I=0000001d73796e7468657469633a66726175646c656e732d7265766965773a76310000000c7265766965772d372e6373760000000000000007`, `D425884d07ae8e842624343aa411210de` and `C1cb19a78e9497dd29eee2de9e7527c60`.

| Input | S (exact source bytes) | `dv_` with old M at reference commit | `dv_` with current working M |
|---|---|---|---|
| Empty label, 678 bytes | `a77db4d5f32043d538e1dd1a799119161912689bcdfb277bc75ba8670e78a588` | `dv_83ce36822c035a5c2ca8e8a8a6c3371e7e3e1371b86df086b83a1c2dbb2b6aa6` | `dv_a690ce1a968ea16a90efe14d2c244af47d57c391668c8eaf58df69bee99df6c0` |
| Label `1`, 679 bytes | `76984a07b7a7e8cf3ebeeb1732ce3852fa08383966c8e1bf3ed5ac3a1532afa9` | `dv_dfa703ee0abc65eee9a19791b23f5c8e3ed0e5d94c3f121b139086259aca984c` | `dv_f424fa3c36837d0d63caec997fbc813ff34f74d53a49e58ef938798bf50b3582` |

For each mapping version, LF and CRLF copies yield the same normalized M and therefore the same pair of `dv_` values. Removing the embedded null field changed M, so the old and current vectors are deliberately different.

## Compatibility and remaining integration

| Boundary | Reviewed technical contract | Later implementation/verification |
|---|---|---|
| Foundation v1 | Existing fixture wire objects, strict decoder, case order and banner remain intact. | Run v1 regressions after any v2 integration. |
| v2 list/detail | Separate dataset version, run/snapshot and currency-name model; labels excluded. | Backend active run/snapshot/version linkage, stale 409 and unavailable 503; frontend strict discriminator dispatch, semantic list/detail checks and error handling. JSON Schema checks shape and local syntax; it cannot prove repository context or cross-response equality. |
| Offline import | Source-bound ordered header/duplicate Account exception, exact Decimal and currency text, assumed UTC+00 analysis coordinate. | T009–T016 parser/store/CLI; refuse source-hash mismatch, incomplete imports and nonmatching reviewed M; no real import yet. |
| Investigation and priority/simulation | Consume versioned operational facts only; preserve lineage/explanations/order and human decision. | Migrate consumer adapters/contracts and test label exclusion and run compatibility in their integration tasks. |

No individual findings or signatures were supplied. There is no browser verification, model evaluation, IBM import, v2 runtime/decoder integration or independent teammate reproduction in this record. Historical `git diff --check` **between branches** reported three blank-line-at-EOF warnings; those are separate from the current working-diff check and were not edited here.

### Final owner-review fields still required by T007/T008

| Component review | Actual reviewer or collective review source | Review date | Finding and decision on this final diff/hash | Remaining migration |
|---|---|---|---|---|
| Data/scoring producer: mapping, source, identity and offline contract | Pending | Pending | Pending | Pending |
| Frontend/API consumer: v1/v2 schema, examples and decoder impact | Pending | Pending | Pending | Pending |
| Investigation consumer: versioned operational facts/lineage | Pending | Pending | Pending | Pending |
| Priority/simulation consumer: score/run/order/explanation inputs | Pending | Pending | Pending | Pending |

The user's joint technical-direction message is the decision source above; it does not fill in these final-file review findings. A collective response is acceptable if it actually identifies what the team reviewed and decided, without inventing individual names.

## Executed checks and gate state

Working directory: repository root on macOS, branch `002-data-and-risk-scoring`, HEAD `182d0b290c8819e602fc5d77e8df8e904228b032`; `PYTHONPATH=backend/src` for pytest. The actual preexisting worktree changes are listed in this record's baseline and were preserved. System `python3` is 3.9.6; the locked `.venv/bin/python` is the existing macOS project environment. No source, mapping or store bytes were written by the check script.

| Actual command | Exit | Observed result |
|---|---:|---|
| `python3 evidence/tasks/feature-002-team-review-check.py` | 0 | Reference M `0b0b85db…45cc0b`; current M `e8290326…6769d6`; each LF equals normalized CRLF; D/C, T and four `dv_` vectors match the full values above. Current API/offline/schema/data-model hashes match the table. |
| `shasum -a 256 data/raw/HI-Small_Trans.csv` | 0 | `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`; original v8 bytes match the mapping. A one-label change would change S and fail this pinned check; no 475 MB edit was performed. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests/unit/test_source_mapping_inspection.py backend/tests/contracts/test_v2_design_amendments.py backend/tests/contracts/test_models.py` | 0 | **122 passed in 0.15s**; source binding, pending inspect behavior, v2 schema/examples and Foundation model regressions. |
| `PYTHONPATH=backend/src .venv/bin/python -m ruff check backend/src/fraudlens/data_import.py backend/tests/unit/test_source_mapping_inspection.py backend/tests/contracts/test_v2_design_amendments.py` | 0 | All checks passed. |
| `rg -n 'approved_mapping_sha256' data/mappings backend/src backend/tests specs/002-data-and-risk-scoring evidence/tasks/feature-002-proposal-validation.py` | 0 | Remaining two references are only the historical `proposals/source-mapping.json` and its proposal validator; no current mapping/runtime/test dependency remains. |
| `git diff --check` | 0 | No working-diff whitespace errors. This is distinct from the three preexisting blank-line-at-EOF warnings in the branch comparison. |

During gate assessment, an exploratory T009–T011 RED attempt was run with `PYTHONPATH=backend/src .venv/bin/python -m pytest -q --tb=line backend/tests/unit/test_data_import.py backend/tests/unit/test_data_identity.py backend/tests/integration/test_data_store.py`: exit **1**, **8 failed in 0.04s** for missing parser/identity/source-binding/SQLite interfaces. The first Ruff run on those temporary tests exited 1 for import order; `ruff check --fix` corrected that and a later Ruff run exited 0. The attempted test files were **removed** when the still-open T007/T008 final-review gate was recognized. They are not retained as T009–T011 RED deliverables, and no GREEN code was started.

**Gate conclusion:** the user supplied a real joint decision on technical direction, but the resulting new working-file hashes and component-specific impact have not been reviewed by actual producing/affected-consuming owners. The T007 mapping and T008 shared-contract task criteria expressly require that review, including real reviewer/date/decision and remaining migrations. The user's message supplies no individual names/findings, and this record does not infer them. Therefore T007/T008 remain unchecked, T009–T011 remain not started, and import remains disabled. One concrete next step: the actual data/scoring, frontend/API, investigation and priority/simulation reviewers inspect this final working diff and hash table, then provide their collective or named review status, date, findings/decision and remaining migrations for the source-audit and contract-review records. Once the required review is real and recorded, T007/T008 can close and Prompt 2 RED tests can begin.

## Codex technical review of the final local diff — 2026-11-13

This section is **Codex's technical finding**, separate from the user's earlier report of the team's joint direction. [Original review request](../../prompts/development/002-final-local-diff-review-request-2026-11-13.md). Reviewed branch `002-data-and-risk-scoring`, HEAD `182d0b290c8819e602fc5d77e8df8e904228b032`, tracked working diff against that full commit, the untracked macOS handoff, this record and its read-only reproduction script. Inputs: `original_idea.md`, Feature 002 spec/plan/tasks/data model/API/offline/schema, Foundation v1 boundary and shared-contract procedure, current mapping and source/contract audit. The tracked application code, Foundation v1 contract and frontend files have no diff against this HEAD; untracked evidence was read separately. Hashes of mapping/API/offline/schema/data-model remain the full values in the table above. Current mapping raw CRLF-copy SHA-256 is `7f8c7b043ac7e7f16a9c8e8d41515b9ff9f87c1e269eafdf9cd99cb0c92735b4`; normalizing that copy to LF yields M `e82903264382ae710b8b93ce43a3e37d954ec6a6629414e217b698664e6769d6`.

### T007 findings against FR-001–004 and SC-001

The mapping's fixed eleven-column order binds `From Bank`/first `Account` at indices 1/2 to sender and `To Bank`/second `Account` at 3/4 to receiver; the two Account values cannot overwrite each other. Received amount/currency remain columns 5/6 and paid amount/currency 7/8. It retains exact nonnegative Decimal text, supported scale 0–6 and separate source currency names (`Euro` accepted, `EUR` excluded), with no FX conversion. It preserves the minute timestamp text and interprets it at fixed UTC+00 **only as a synthetic analysis assumption**; source timezone remains unknown. `Is Laundering` at column 10 is a private evaluation label; an empty/invalid label excludes supervised use without discarding valid event facts. See mapping lines 70–133, 136–152, 199–266; data model lines 110–138; spec FR-002–004. These are correct **contract decisions**, not proof of a working importer.

The independent reproduction script returned stable D `D425884d07ae8e842624343aa411210de` and C `C1cb19a78e9497dd29eee2de9e7527c60` at ordinal 7. For the current mapping M, blank-label `dv_a690ce1a968ea16a90efe14d2c244af47d57c391668c8eaf58df69bee99df6c0` changes to label-1 `dv_f424fa3c36837d0d63caec997fbc813ff34f74d53a49e58ef938798bf50b3582` while D/C remain fixed. LF and CRLF mapping copies give the same M. The original IBM v8 source hash still matches the pinned digest; an edited IBM file cannot pass that binding. This validates the **specified calculation and synthetic vectors**, not T009–T011 implementation.

### T008 component findings against FR-008–009, FR-019–026 and SC-007–008

| Component | Technical finding | Contract/requirement | What remains later |
|---|---|---|---|
| Scoring/backend | ScoreRequestV2 and AssessmentV2 carry transaction, dataset, run, feature, as-of and real scored time; score source/kind and label-free explanation have separate semantics. Directional canonical money/time inputs suffice for the planned rules/model boundary. | [Offline scorer boundary](../../specs/002-data-and-risk-scoring/contracts/data-and-scoring.md#scorerequestv2-and-scorerv2), [API assessment](../../specs/002-data-and-risk-scoring/contracts/api.md#casedetailv2), spec FR-008–009, FR-019–020. | Implement typed validation and active complete-run/snapshot/dataset equality; verify explanation lineage and score kind. |
| Frontend/API | Existing separate v2 list/detail shape carries data source, score source, `dataset_version`, snapshot, exact source amounts/currencies, time basis, alert counts/order and explanation. Foundation v1 contract/decoder/code are untouched and all current regressions pass. | [API mode/list/detail](../../specs/002-data-and-risk-scoring/contracts/api.md#mode-and-compatibility), [v2 schema](../../specs/002-data-and-risk-scoring/contracts/schemas.json), spec FR-021–024 and SC-007–008. | Tighten `DatasetVersionId` first (problem 1 below); then implement strict v1/v2 dispatch, semantic list/detail comparisons, 409/503 handling and truthful mode-specific UI copy. |
| Investigation | Detail supplies bank-qualified parties, both money sides, raw/interpreted time, assumed-clock discriminator, assessment/run/version and method-backed explanation without labels. It supplies the planned case/scoring facts; external evidence, RAG and workflow belong to their own feature. | [Transaction/assessment/detail](../../specs/002-data-and-risk-scoring/contracts/api.md#casedetailv2), [operational label boundary](../../specs/002-data-and-risk-scoring/data-model.md#privateevaluationlabel), spec FR-019–021, original idea sections 1 and 7. | Build a versioned adapter, preserve provenance and disclose the UTC+00 assumption; never pass private labels to investigation. |
| Priority/simulation | The score kind, scorer/run/dataset versions, event time, stable IDs and complete ScoredRun model provide a versioned operational starting point. The 100-item API list is an analyst display subset, **not** the full simulation population. Capacity, case weights and review times require a separate explicit policy/assumption; AML amount is not bank loss. | [ScoredRun/ReviewCaseSnapshot](../../specs/002-data-and-risk-scoring/data-model.md#scoredrun-reviewcasesnapshot-and-evaluationreport), [bounded list](../../specs/002-data-and-risk-scoring/contracts/api.md#caselistv2), spec FR-022, original idea sections 1 and 8. | Define the later consumer's full-run interface and deterministic capacity/replay policy; keep holdout labels outside operational priority inputs. |

JSON Schema checks local response shape, required fields, closed objects, enums, patterns and numeric bounds. It cannot establish that a dataset version is the **computed** SHA-256 of S/M/T, that a detail belongs to the active run, or that list/detail/assessment identities and versions agree. Backend must enforce repository/run/source binding; frontend must enforce strict decoding and consistency with its pinned list. Those semantic checks are planned integration, not present behavior.

### Problems requiring correction before T007/T008 freeze

1. **T008 contract mismatch (technical blocker).** FR-004/FR-023 and SC-008 require version identity and schema/decoder parity. [data-model.md lines 43–49](../../specs/002-data-and-risk-scoring/data-model.md#identity-and-version-rules) now require `dv_` plus exactly 64 lowercase hex digits, but [schemas.json line 33](../../specs/002-data-and-risk-scoring/contracts/schemas.json) accepts 1–64 arbitrary letters, digits, `_` or `-`. The targeted validator accepted `dv_A`, `dv_` plus 63 `a` characters and `dv_` plus 64 uppercase `A` characters. [API example lines 137/159/175](../../specs/002-data-and-risk-scoring/contracts/api.md#example-rules-list-and-detail) and [contract test line 32](../../backend/tests/contracts/test_v2_design_amendments.py) use the now impossible `dv_example` shape. A backend/frontend decoder following the schema could accept a version no importer can calculate; tightening only one side would break examples/parity. **Smallest fix:** update `DatasetVersionId` to exactly 64 lowercase hex digits, replace the three example values with one valid-shaped synthetic `dv_`, and update the positive/negative schema tests (including the semantic mismatch probe with a different *valid-shaped* ID). Preserve the v2 fields and Foundation v1.
2. **T007 mapping identity description is stale and potentially ambiguous.** T007 requires a frozen mapping with identity/hash rules. [mapping lines 278–285](../../data/mappings/ibm_hi_small_v1.json) still call D/C an “existing proposed” scheme and name only an “approved mapping SHA-256” input, while the adopted byte recipe and normalized M live in [data-model.md lines 28–69](../../specs/002-data-and-risk-scoring/data-model.md#identity-and-version-rules) and the external record. [data-model.md line 25](../../specs/002-data-and-risk-scoring/data-model.md#identity-and-version-rules) also says namespace is release identifier “plus source member” even though the actual mapping namespace excludes the member and the recipe appends it separately. For example, one implementer could append `HI-Small_Trans.csv` inside N and again as F while another uses `source.namespace` as N; they would generate different D/C for the same row. **Smallest fix:** make the mapping identity text explicitly reference the final domain/framing recipe and external normalized-M record, and state that N is exactly `source.namespace` while F is exactly `source.member`. After any mapping-byte change, recalculate M and both `dv_` vectors and seek final-file review; keep the historical manifest unchanged.

Neither problem has been silently edited in this review. Problem 1 blocks T008 contract freeze; problem 2 blocks an unambiguous T007 mapping freeze. The existing missing final owner review remains a **separate review gate**, not an algorithm failure. T009–T011 depend on T008 in `tasks.md`, so they must wait for these corrections and actual review. The calculation itself is reproducible, and no additional parser/math blocker was found in the inspected contract. Actual IBM import remains prohibited by `import_allowed=false` and does not exist yet.

### Commands and actual results of this review

| Command from repository root, except frontend as noted | Exit | Observed result |
|---|---:|---|
| `git status --short --branch`; `git diff 182d0b290c8819e602fc5d77e8df8e904228b032 -- ...`; separate reads of untracked evidence | 0 each | Branch/HEAD unchanged; tracked diff is mapping, data model/offline contract, tasks/next_work and source/contract evidence. Untracked handoff/review/script/prompts inspected separately. No tracked backend/frontend/Foundation v1 diff. |
| `python3 evidence/tasks/feature-002-team-review-check.py` | 0 | Old/current M and four full `dv_` vectors matched this record; LF/CRLF normalized hashes equal. |
| `python3 - <<'PY'` (read-only mapping role/currency/time/label and LF/CRLF raw-hash assertions, command executed in this review) | 0 | Sender indices 1/2, receiver 3/4, received 5/6, paid 7/8, private label 10; 15 allowed currency names, `Euro` yes/`EUR` no; time basis assumed UTC+00, source zone null; LF raw/current M `e8290326…6769d6`, CRLF raw `7f8c7b04…735b4`, CRLF normalized M equal LF. |
| `PYTHONPATH=backend/src .venv/bin/python - <<'PY'` (Draft202012Validator schema/ID probe) | 0 | Schema valid; `dv_example_1`, `dv_A`, uppercase 64-hex and 63-hex variants all incorrectly accepted; valid 64 lowercase hex accepted. |
| `shasum -a 256 data/raw/HI-Small_Trans.csv data/mappings/ibm_hi_small_v1.json specs/002-data-and-risk-scoring/contracts/api.md specs/002-data-and-risk-scoring/contracts/data-and-scoring.md specs/002-data-and-risk-scoring/contracts/schemas.json specs/002-data-and-risk-scoring/data-model.md` | 0 | Source, mapping and four design-file hashes matched this record's full hash table. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests/unit/test_source_mapping_inspection.py backend/tests/contracts/test_v2_design_amendments.py backend/tests/contracts/test_models.py` | 0 | 122 passed in 0.14s; existing tests do not assert exact new `dv_` syntax. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests` | 0 | 375 passed, 1 existing Starlette/httpx deprecation warning, in 0.66s. |
| `npm test -- --run` (cwd `frontend/`) | 0 | 151 tests in 5 files passed; fixture/v1 regression only, not v2 runtime integration. |
| `.venv/bin/python -m ruff check backend/src backend/tests evidence/tasks/feature-002-team-review-check.py` | 0 | All checks passed. |
| Read-only mapped `inspect` via `.venv/bin/python -m fraudlens.pipeline_cli inspect --source data/raw/HI-Small_Trans.csv --mapping data/mappings/ibm_hi_small_v1.json` in a Python subprocess wrapper with `PYTHONPATH=backend/src` | CLI child **2**, wrapper **0** | 25.25 s; `status=blocked`, `complete_parse=true`, `row_count=5078345`, `error_codes=["pending_team_review"]`, `import_allowed=false`; source SHA-256 matched and inspector raw mapping SHA-256 was current M on this LF checkout. |
| `git diff --check` | 0 | No tracked working-diff whitespace errors. |

These are local checks and a technical review, not human owner review, independent reproduction, model evaluation or browser verification. T007/T008 remain open under their existing criteria; no T009–T011 RED or import implementation was added in this review.


## Codex correction and preparatory RED verification — 2026-11-13

[Exact user request](../../prompts/development/002-t007-t008-fixes-and-t009-t011-red-request-2026-11-13.md). Branch `002-data-and-risk-scoring`, unchanged HEAD `182d0b290c8819e602fc5d77e8df8e904228b032`; all values below refer to the **current uncommitted working diff**, not the historical hashes above. This is Codex's technical verification, separate from the earlier user-relayed joint decision and from the still-pending actual component review.

The two prior technical findings are corrected. `DatasetVersionId` now matches `^dv_[0-9a-f]{64}(?![\\s\\S])` in the JSON source, demanding 64 lowercase hex characters and an absolute end. All three v2 API examples and schema tests use a valid-shaped ID; negative tests reject `dv_example`, 63/65 characters, uppercase and a terminal LF. Foundation v1 and v2 field sets are unchanged. Mapping and data model now explicitly bind N to `source.namespace` and F to `source.member`; the member is framed once as its own input, after N, by the adopted UTF-8/U32BE/U64BE recipe. The importer remains absent and the mapping remains `pending_team_review`, `executable_mapping=false`, `import_allowed=false`.

| Current file/input | SHA-256 / value |
|---|---|
| Original IBM v8 CSV S (pinned, historical successful scan; not rescanned in this slice) | `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040` |
| Mapping raw LF bytes and normalized M | `a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57` |
| Mapping raw CRLF-converted bytes | `9a87e1ddaad2c6825d76111eae4fdcf54e2bec5ed0c7c25685b1ea8a0dd42ae1` |
| Mapping CRLF bytes after CRLF→LF normalization | `a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57` |
| Time-policy T | `67a408fc52e57035115186c3c9863dfeac5a72d709292e0f7baeef560086d781` |
| `contracts/api.md` | `fbf7be0df60a9d7bf7e881d44d8727d5eadc64e758af7944150149700f17b13e` |
| `contracts/data-and-scoring.md` | `534de0c70a6ecbec69dd8734d6fec5830a9814da81fa508afe16a0f1dcca9918` |
| `contracts/schemas.json` | `bf487d84ccac1e315d0e20fece0d2a7f45990bce954ba40bf97cd54e43929f88` |
| `data-model.md` | `e8235e358c6d01fc13e3f5f9a8ad0600d2d98c44d4afda4aa75809aa3efa0987` |

The reproduction script uses the same synthetic row and input digests as the prior record. For **this mapping M**, blank label gives `dv_55e9a2fe16d796aa75aa917f82c516b92caeb7d91fc2f3ee59efc757fca0bb3d`; label `1` gives `dv_33e5d9754468adc36e4ceb77a71c4e1e7ab0faad94cd37da29f8e5282b809dfa`. D=`D425884d07ae8e842624343aa411210de` and C=`C1cb19a78e9497dd29eee2de9e7527c60` remain unchanged. The previous `e8290326…6769d6` mapping and its vectors above are historical; they are not approved hashes for these edited bytes. A label edit to the real v8 CSV would fail its pinned S check; no CSV bytes were changed here.

Commands below ran from repository root unless `cwd frontend` is stated. Existing `.venv` and frontend locked dependencies were used; no setup or import command was run in this slice.

| Command | Exit | Observed result |
|---|---:|---|
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests/contracts/test_v2_design_amendments.py backend/tests/unit/test_source_mapping_inspection.py` | 0 | 34 passed in 0.08s; exact v2 ID positive/negative cases, examples and mapping inspection. |
| `python3 evidence/tasks/feature-002-team-review-check.py` | 0 | Full raw/normalized hashes and current/reference synthetic D/C/`dv_` vectors printed as above; LF/CRLF M equality asserted. |
| `shasum -a 256 data/mappings/ibm_hi_small_v1.json specs/002-data-and-risk-scoring/contracts/api.md specs/002-data-and-risk-scoring/contracts/data-and-scoring.md specs/002-data-and-risk-scoring/contracts/schemas.json specs/002-data-and-risk-scoring/data-model.md` | 0 | Five file hashes match the current table. |
| `PYTHONPATH=backend/src .venv/bin/python -m pytest -q backend/tests --ignore=backend/tests/unit/test_data_import.py --ignore=backend/tests/unit/test_data_identity.py --ignore=backend/tests/integration/test_data_store.py` | 0 | 380 passed, 1 preexisting Starlette/httpx warning, in 0.62s. New RED files intentionally excluded. |
| `npm test -- --run` (`cwd frontend`) | 0 | 151 passed in 5 files. |
| `.venv/bin/python -m ruff check backend/src backend/tests evidence/tasks/feature-002-team-review-check.py` | 0 | All checks passed. |
| `git diff --check` | 0 | No working-diff whitespace errors. |

No new technical blocker for starting synthetic T009–T011 tests was found. The **only remaining T007/T008 gate** is actual review of these final working bytes and consumer impacts, with real date/findings/decision and remaining migrations. The user explicitly authorized preparatory T009–T011 RED work while this human gate remains open; [the separate import identity record](feature-002-import-identity.md) contains its collection/failures. This does not close T007/T008, complete T009–T011, or enable import. Later v2 backend/frontend/consumer integration remains separate work. Historical branch-comparison `diff --check` warnings about three blank EOF lines are unchanged; the current working-diff check above is clean.


## Collective final-byte approval conveyed by the user — 2026-11-13

[User confirmation](../../prompts/development/002-t007-t008-final-team-approval-2026-11-13.md) states that the **entire team** reviewed and approved the final T007/T008 changes on `002-data-and-risk-scoring`: mapping, D/C and `DatasetVersion` identity/hash rules, and the v2 contracts with the stricter `DatasetVersionId`. The team reported no open objections blocking continuation; the user will take subsequent implementation independently. This is a collective approval conveyed by the user, not individual signatures, assigned roles, or Codex's own human-review claim. Date is the date of that confirmation, 2026-11-13 (Europe/Belgrade).

Reviewed state is the uncommitted working diff relative to full HEAD `182d0b290c8819e602fc5d77e8df8e904228b032`, pinned by the following **full final-content SHA-256 values**. A read-only Python comparison of the current file bytes to the immediately preceding final-hash table exited 0: **5/5 match; no later edits to these approved files were found**. For the LF mapping on this checkout, raw SHA-256 equals normalized M; CRLF-converted raw SHA-256 differs but normalizes to the same M.

| Approved file | SHA-256 |
|---|---|
| `data/mappings/ibm_hi_small_v1.json` (normalized M; current raw LF also equal) | `a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57` |
| `specs/002-data-and-risk-scoring/data-model.md` | `e8235e358c6d01fc13e3f5f9a8ad0600d2d98c44d4afda4aa75809aa3efa0987` |
| `specs/002-data-and-risk-scoring/contracts/data-and-scoring.md` | `534de0c70a6ecbec69dd8734d6fec5830a9814da81fa508afe16a0f1dcca9918` |
| `specs/002-data-and-risk-scoring/contracts/api.md` | `fbf7be0df60a9d7bf7e881d44d8727d5eadc64e758af7944150149700f17b13e` |
| `specs/002-data-and-risk-scoring/contracts/schemas.json` | `bf487d84ccac1e315d0e20fece0d2a7f45990bce954ba40bf97cd54e43929f88` |

Historical review-hash manifest and earlier proposal hashes remain historical and unchanged. The separate approval record is authoritative for these reviewed mapping bytes; the mapping file itself retains `pending_team_review`, `executable_mapping=false` and `import_allowed=false` so no import is enabled by documentation alone. Any future mapping-content edit changes M and requires a new review binding. Source S and time-policy T remain as recorded in the preceding correction section.

The earlier compatibility matrix and component obligations remain the reviewed technical direction. **Remaining migrations are implementation work, not open review objections:** T009–T016 canonical models/parser/store/CLI; later backend active complete-run/snapshot/dataset validation, frontend strict v1/v2 decoding and list/detail consistency, investigation and priority/simulation versioned operational adapters, and negative/v1 regressions. No private evaluation labels may enter operational or API inputs. The collective approval clears T007/T008 review gates; it does not claim those later migrations are implemented or that the 20 preparatory RED cases fully satisfy T009–T011.

Actual verification in this approval-recording session from repository root: `git rev-parse HEAD` exited 0 and printed `182d0b290c8819e602fc5d77e8df8e904228b032`; a `python3 - <<'PY'` read-only SHA-256 comparison of the five current files against the full values in the preceding correction table exited 0 and printed five `match=True` results. `git diff --check` result is recorded in `next_work.md`. No IBM import, commit, push or merge was run.
