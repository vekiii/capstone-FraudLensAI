# Feature 002 source inspection, audit and mapping decisions

## T007 source-mapping gate re-verification - 2026-11-13

**Result: complete; no new mapping approval is required.** The user's [collective final-byte confirmation](../../prompts/development/002-t007-t008-final-team-approval-2026-11-13.md) and the [separate review record](feature-002-t007-t008-team-review-2026-11-13.md#collective-final-byte-approval-conveyed-by-the-user) approve the exact IBM HI-Small mapping under normalized SHA-256 `a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57`. The current LF working file has that raw and normalized digest, `git diff --exit-code -- data/mappings/ibm_hi_small_v1.json` found no change, and Git reports LF in index and worktree. T007 was already checked in `tasks.md`; this review leaves its marker and mapping bytes unchanged.

The mapping requires the exact 11 ordered headers. Positions 2 and 4 distinguish sender and receiver `Account`. The importer preserves exact bank/account strings and frames each bank/account pair for joins. D/C transaction and case IDs use the reviewed namespace, member and one-based pre-filter CSV ordinal with separate hash domains. DatasetVersion binds source, normalized mapping and time-policy digests. `Timestamp` remains raw and is interpreted as a minute-resolution fixed +00:00 **analysis coordinate**; the source timezone remains unknown. `Amount Received`/`Receiving Currency` and `Amount Paid`/`Payment Currency` remain separate. Amount strings are validated as exact plain decimals without FX or rounding, and the reviewed currency names are preserved. `Is Laundering` produces a separate private evaluation label; it is absent from canonical event facts and scorer predictor fields. Unsupported fields or values fail the reviewed policy.

The JSON's embedded `pending_team_review`, `executable_mapping=false`, `import_allowed=false` and null reviewer fields are historical inspection metadata deliberately retained inside the hashed file. The local import CLI checks the **external** final-byte approval, pinned mapping/source hashes, namespace/member, source size and time policy before staging. T015/T016 evidence records a completed IBM import and replay through that source-bound path. These embedded flags do not reopen T007 or block this approved local CLI. They do not authorize changed data or mappings. The separate pretrained graph-state account/cutoff compatibility gate remains open.

The mapping digest still matches its approved record. Among the four other files pinned in the combined T007/T008 final-byte review, current LF-normalized `contracts/api.md` (`fbf7be0d...17b13e`) and `contracts/schemas.json` (`bf487d84...f88`) match their reviewed digests. The current LF-normalized `data-model.md` is `4b3a8ff93dba0750132f55f06fe7d90965bb9e5cb282b3f7e66377cb2ebc8ff0` (reviewed: `e8235e35...a0987`), and `contracts/data-and-scoring.md` is `2654f4e2bab0a17b15bc71e885307dc44912159047b8f764a0a444ceb365ee3d` (reviewed: `534de0c7...a9918`). Both have later Phase 3/4 content revisions. This is a **current-contract review distinction**, not a change to M or a reopened source-mapping decision. Review those later revisions separately before claiming exact current-byte T008 approval.

Checks from repository root on `model-implementations` at `a031b16`:

| Check | Exit | Observed |
|---|---:|---|
| `Get-FileHash -Algorithm SHA256` on mapping and raw CSV; source size check | 0 | M `a816260a...093e57`; source S `b19d39f5...c5b040`, 475,664,283 bytes; both match pinned evidence. |
| `git diff --exit-code -- data/mappings/ibm_hi_small_v1.json`; `git ls-files --eol` | 0 | No mapping diff; index and worktree both LF. |
| `.venv/Scripts/python.exe evidence/tasks/feature-002-team-review-check.py` | 0 | Final M, LF/CRLF equivalence, D/C synthetic vectors and time-policy digest matched. |
| `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider backend/tests/unit/test_data_identity.py backend/tests/unit/test_source_mapping_inspection.py backend/tests/unit/test_data_import.py backend/tests/contracts/test_v2_design_amendments.py --tb=short --basetemp data/artifacts/pytest-mapping-gate` | 0 | 106 passed in 1.26 s; controlled contract checks, not a new full-source import. |
| `.venv/Scripts/python.exe -c` with `hashlib.sha256(Path(p).read_bytes().replace(b'\r\n', b'\n'))` for the four reviewed contract paths | 0 | API and schema match; data model and offline data/scoring contract differ after later revisions as shown above. |
| `.venv/Scripts/python.exe -m json.tool data/mappings/ibm_hi_small_v1.json` | 0 | Mapping JSON parses; no content edit. |
| `Test-Path` for the three new local evidence/prompt link targets | 0 | All three paths exist. |
| `git diff --check` | 0 | No whitespace errors; Git emitted nonfatal LF-to-CRLF notices. |

No raw CSV, mapping, model, holdout or generated store was modified for this review.

**Current Phase 3 outcome:** [T015/T016 actual import and replay](feature-002-import-identity.md#t016-declared-ibm-v8-import-and-exact-replay--2026-11-13) completed against the final-byte mapping M `a816260a…093e57`. Its embedded pending/inspect-only fields remain historical; the local CLI requires the separate collective final-byte review, exact M, namespace/member and S before execution. Earlier import-disabled statements below record the state before T015.

## Collective final mapping approval — 2026-11-13

[The user's confirmation](../../prompts/development/002-t007-t008-final-team-approval-2026-11-13.md) reports that the entire team reviewed and approved the final T007 mapping and identity/hash rules, with no blocking objections. This collective report is the review source and decision; no individual names or signatures were supplied or inferred. Reviewed state: uncommitted working diff on branch `002-data-and-risk-scoring` against HEAD `182d0b290c8819e602fc5d77e8df8e904228b032`, pinned by mapping SHA-256 M `a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57` (also raw LF SHA-256 on this checkout), data-model SHA-256 `e8235e358c6d01fc13e3f5f9a8ad0600d2d98c44d4afda4aa75809aa3efa0987`, offline identity contract SHA-256 `534de0c70a6ecbec69dd8734d6fec5830a9814da81fa508afe16a0f1dcca9918`. Read-only comparison with the previous final-byte evidence found 3/3 matching values and no later edit. [Full approval and hash check](feature-002-t007-t008-team-review-2026-11-13.md#collective-final-byte-approval-conveyed-by-the-user).

T007 review gate is complete. The reviewed mapping bytes are frozen by this separate record; its embedded `pending_team_review`, `executable_mapping=false`, and `import_allowed=false` remain untouched, so import is still disabled. The original source S and selected time-policy T are unchanged. A future hashed mapping-content change needs a new external review binding. Historical pending entries below document earlier states.

## Current Codex correction check — 2026-11-13

The [current working-diff verification](feature-002-t007-t008-team-review-2026-11-13.md#codex-correction-and-preparatory-red-verification--2026-11-13) fixes the prior N/F ambiguity: N is exactly `source.namespace`, F exactly `source.member`, independently length-framed. Current raw LF/normalized mapping SHA-256 is `a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57`; raw CRLF-copy SHA-256 is `9a87e1ddaad2c6825d76111eae4fdcf54e2bec5ed0c7c25685b1ea8a0dd42ae1`, and normalizing that copy gives the same M. `python3 evidence/tasks/feature-002-team-review-check.py` exited 0; 380 existing backend tests and Ruff passed. The prior `e829…` M below is historical. The team's joint technical decision remains recorded; actual final-byte producer/affected-consumer review is pending. No individual review is inferred. T007 remains open and import disabled.

## Joint T007 technical decision — 2026-11-13

The user [relayed the team's joint decision](../../prompts/development/002-t007-t008-team-decision-and-red-request-2026-11-13.md) to adopt the exact D/C and `dv_` byte recipes, CRLF-normalized full-file mapping hash and separate review record. This is a **collective technical decision**, not a claim of individual data/scoring or consumer signatures. The [separate T007/T008 record](feature-002-t007-t008-team-review-2026-11-13.md) identifies reference commit `182d0b290c8819e602fc5d77e8df8e904228b032`, the uncommitted working diff, rationale, vectors and calculated SHA-256 values. The current mapping's normalized M pending final owner review is `e82903264382ae710b8b93ce43a3e37d954ec6a6629414e217b698664e6769d6`; source S is `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`; selected time-policy T is `67a408fc52e57035115186c3c9863dfeac5a72d709292e0f7baeef560086d781`. Exact source bytes, ordered headers, Account positions, money/currency/label and assumed UTC+00 analysis policy were already technically audited in the sections and linked evidence below. The team decision adopts those choices; no unknown source timezone or original acquisition history is inferred.

The old self-referential mapping hash field was removed. Review identity lives outside the mapping, so a later content edit invalidates the pinned M. The current file remains an import-disabled pending inspection configuration; the future importer must check the matching external record and explicit import enablement. No import or activation was performed. Earlier pending-review statements below describe the state *before* this user-relayed decision and remain as history.

**Current resolution:** [authorized technical/source verification](feature-002-technical-resolution.md)
completes T006: the pinned v8 CSV hash matches, its listing license is verified,
and account/binary semantics have publisher reference-code support. The user
approved an explicit assumed UTC+00 analysis policy. [Technical mapping](../../data/mappings/ibm_hi_small_v1.json)
is now present but pending team review and import-disabled. Earlier observations
below are the preserved initial audit; its missing-release/mapping statements
are historical, not current blockers. Source timezone and acquisition history
remain unknown facts and are not invented.

Continuation: [independent publisher-source investigation](feature-002-source-investigation.md)
now verifies public Kaggle v8/license metadata and IBM's positional account direction.
Local release binding and clock/owner decisions remain pending. The [concrete review
packet](../../specs/002-data-and-risk-scoring/proposals/README.md) supersedes the
preliminary alternatives below; no approved mapping has been created.

2026-11-13 Europe/Belgrade. T004/T005 complete; T006 audit **partial: release and local license binding pending**; T007 `pending_mapping_review`. FR-001–004, FR-026. [Original request](../../prompts/development/002-source-inspection-request-2026-11-13.md), [revision/environment/verification ledger](feature-002-implementation.md). No import, canonical mapping freeze, model evaluation or SC-001 acceptance.

## Source and provenance

Only authorized local `data/raw/HI-Small_Trans.csv` was scanned, in binary read mode and streaming CSV mode. No other local dataset opened; no dataset download or raw-data edit. User supplied acquisition source/date in the linked clarification:

- Acquisition source: [Kaggle, ealtman2019 IBM AML](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml).
- Acquired 2026-11-13 (user declaration; no independent acquisition log).
- Member: `HI-Small_Trans.csv`. Variant HI-Small is declared from supplied member/source, not a verified release identifier.
- Exact release/version: **unknown, pending verification**. No archive manifest or distribution checksum available to bind these local bytes to an exact Kaggle version.
- Size: **475,664,283 bytes**.
- SHA-256: `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`.
- [IBM AML-Data README](https://github.com/IBM/AML-Data#aml-data), fetched 2026-11-13 using web open, distinguishes the code repository license (Apache-2.0) from data license (CDLA-Sharing-1.0) and directly links the same Kaggle dataset. This verifies the upstream data-license statement and intended Kaggle distribution relationship. Kaggle's page returned no readable content in the browsing tool. **Applicability to the exact acquired release remains pending**, because that release/local-byte binding is unavailable. The repository code license was not substituted for the data license. This is provenance evidence, not a legal determination.

Inspector provenance contains the declared URLs and `release: null`; nonzero result prevents missing provenance becoming a successful release identification. Inspector does not validate licenses remotely or infer a release from a filename/hash. Upstream documentation is not used as evidence of local field values.

## Observed bytes, schema and dialect

Full file passed strict UTF-8 decoding, no BOM. An independent binary scan found **0 non-ASCII bytes**, so the bytes are ASCII-compatible and UTF-8-compatible; this does not prove a unique originating encoding. It found **5,078,346 LF bytes, 0 CR bytes and 0 quote bytes**. Comma delimiter produced exactly 11 fields in every record, with one header record and 5,078,345 data records. No quoted fields occur in this file, so quote/escape behavior is an explicit tested parser policy, not independently observable from these bytes. Parser settings: quotechar `"`, doublequote true, escapechar null, skipinitialspace false, strict true; no encoding/dialect heuristic.

Exact observed header, preserving both occurrences:

```text
Timestamp,From Bank,Account,To Bank,Account,Amount Received,Receiving Currency,Amount Paid,Payment Currency,Payment Format,Is Laundering
```

Zero-based positions below are **unreviewed inspection roles** chosen from the observed header, not an approved import mapping or a claim of verified business semantics. No account values, raw records or row-level labels are published.

| Index | Observed header | Inspection interpretation / observed form |
|---|---|---|
| 0 | Timestamp | All 5,078,345 calendar-valid `YYYY/MM/DD HH:MM` texts; length 16; minute lexical resolution; no timezone suffix. |
| 1 | From Bank | Proposed sender-bank role; token lengths 3–7, normalization unresolved. |
| 2 | Account | First account occurrence; token length 9; sender direction proposed, not approved. |
| 3 | To Bank | Proposed receiver-bank role; token lengths 3–7. |
| 4 | Account | Second account occurrence; token length 9; receiver direction proposed, not approved. |
| 5 | Amount Received | Plain decimal text, details below. |
| 6 | Receiving Currency | 15 distinct currency-name strings, lengths 3–17. |
| 7 | Amount Paid | Plain decimal text, details below. |
| 8 | Payment Currency | 15 distinct currency-name strings, lengths 3–17. |
| 9 | Payment Format | 7 distinct strings; lengths 3–12. |
| 10 | Is Laundering | Observed literal tokens `0`/`1`; semantic positive mapping requires review. |

All 11 columns: **0 missing/whitespace-only values**. Every parsed record has the expected width. Duplicate normalized-header group is exactly **[2, 4]**. No extra/unknown or additional target-like columns under this explicitly declared positional observation layout. This layout does not resolve the duplicate-header import gate.

## Counts, time and money

- Complete parsed-record denominator: **5,078,345**. Literal label counts: `0` **5,073,168**, `1` **5,177**, missing **0**, other **0**. Token-1 fraction = `5177/5078345` = approximately **0.10194266045335635%**. These are source-token counts, not supervised event-valid/eligible counts, split counts, prediction metrics or a legal finding. No per-row or partition labels inspected/published.
- Wall-time range: **2022/09/01 00:00 – 2022/09/18 16:18**. All texts resolve to minute precision, with no seconds/fractional text and **5,078,345 absent-timezone observations**. Neither UTC nor any geographical timezone is evidenced. Underlying generator clock resolution beyond the stored text is unknown. No UTC conversion or time-policy hash created.
- Both amount columns: minimum **0.000001**, maximum **1046302363293.48**, maximum 13 integer digits and 16 total characters, 0 negative, 0 zero, 0 non-plain-decimal, 0 missing. Final lexical summary confirms 5,078,345 unsigned values and 0 integer parts with redundant leading zeros on each side. Exact Decimal comparisons used, no float, rounding or FX conversion.
- Received amount scale: **4,930,194** records with 2 fractional digits; **148,151** with 6.
- Paid amount scale: **4,932,279** records with 2 fractional digits; **146,066** with 6.
- Zero/negative/unsupported-scale import policies remain review decisions; absence of observed zero does not establish whether zero is supported.

| Exact currency token | Receiving Currency count | Payment Currency count |
|---|---:|---:|
| Australian Dollar | 138511 | 136769 |
| Bitcoin | 148151 | 146066 |
| Brazil Real | 71544 | 70703 |
| Canadian Dollar | 141357 | 140042 |
| Euro | 1172017 | 1168297 |
| Mexican Peso | 111030 | 110159 |
| Ruble | 157361 | 155178 |
| Rupee | 192065 | 190202 |
| Saudi Riyal | 89971 | 89014 |
| Shekel | 194988 | 192184 |
| Swiss Franc | 237884 | 234860 |
| UK Pound | 181255 | 180738 |
| US Dollar | 1879341 | 1895172 |
| Yen | 156319 | 155209 |
| Yuan | 206551 | 213752 |

Each currency column sums to 5,078,345. No ISO-code or FX interpretation applied. Payment Format counts: ACH 600797; Bitcoin 146091; Cash 490891; Cheque 1864331; Credit Card 1323324; Reinvestment 481056; Wire 171855 (sum 5,078,345). Categorical output cap is 64 values/120 characters; none omitted in the actual source report.

## Actual inspect command and result

After [ignore verification](feature-002-artifacts-explanations.md), from repository root:

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/002-data-and-risk-scoring'
$env:PYTHONPATH = 'backend/src'
New-Item -ItemType Directory -Path data/artifacts -Force | Out-Null
$sourceHash = (Get-FileHash -LiteralPath data/raw/HI-Small_Trans.csv -Algorithm SHA256).Hash.ToLowerInvariant()
$auditResult = & .\.venv\Scripts\python.exe -m fraudlens.pipeline_cli inspect --source data/raw/HI-Small_Trans.csv --source-name https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml --license-ref https://github.com/IBM/AML-Data --expected-sha256 $sourceHash --column timestamp=0 --column sender_bank=1 --column sender_account=2 --column receiver_bank=3 --column receiver_account=4 --column received_amount=5 --column received_currency=6 --column paid_amount=7 --column paid_currency=8 --column payment_format=9 --column label=10
$auditExit = $LASTEXITCODE
$auditResult | Set-Content -LiteralPath data/artifacts/feature-002-source-inspection.json -Encoding utf8
```

Actual exit **2**; stderr `Inspection blocked; duplicate_headers,provenance_incomplete`. JSON status blocked, complete_parse true, row_count 5078345. Not a successful import/mapping. Initial report SHA-256: `8745dc4e7e88449c7ae7c1060e5b4c11d77ccd4ddb7162badebc081c561fa995` (PowerShell UTF-8 output bytes).

After adding explicit lexical forms/sign counts/ambiguities through a second RED/GREEN cycle, reran the same inspect command with the literal expected SHA-256 above in place of `$sourceHash` and the same output path. Exit **2**, same complete record counts/ranges/hash and duplicate/provenance blockers. Final ignored report SHA-256: **`66b284f7863f235672b8f26c9fc63b1fcf087b781c3d642a13b17839fa520996`**. Final timestamp lexical-form histogram is exactly `{"9999/99/99 99:99":5078345}`, directly supporting the slash/space/minute shape recorded above. Explicit ambiguities: mapping_unreviewed, duplicate_headers, provenance_incomplete, timezone_absent, label_meaning_unreviewed. Report remains ignored/local; this sanitized evidence preserves observations for checkout readers.

Inspector rehashes the same descriptor after parsing and the named path afterward. Separate pre-inspection `Get-FileHash` and post-inspection streaming SHA-256 matched the digest above. Source bytes unchanged across audit. Independent post-scan `python -` byte counting/check script exited 0: checked size/hash, ASCII/newline/quote counts, label/currency/format/scale count reconciliation and v2 schema checks described in [contract review](feature-002-contract-review.md). It used 1 MiB binary chunks, `hashlib.sha256`, byte counts, and no record output.

## RED → GREEN and limits

[Ledger](feature-002-implementation.md) records exact commands/exits: initial **30 RED** assertions for missing inspector, then 29 passed/one incorrect multiline length expectation corrected, then **30 GREEN**. Added six successful form/options checks after inspection: **36 inspection tests passed**. A follow-up lexical/sign-summary RED produced **2 failures/34 passes**, followed by **36 GREEN** after implementation. Final full backend **346 passed**, frontend **151 passed**, Ruff/typecheck/build passed. These are authored fixtures/regressions, not IBM evaluation. Negative cases include exact/normalized/BOM/case/whitespace duplicates; target-like/unknown headers; missing roles/alias fields; ambiguous aliases; missing/unreadable files; invalid/unsupported encoding/NUL; empty/header-only/truncated quoted/partial parse/width errors; explicit hash mismatch and same-size changed source; bounded private aggregates; CLI controlled exit/no import subcommand. Valid multiline records count once, BOM/semicolon are explicit, fractional timestamp text is retained through nine digits, and malformed facts/labels are aggregate observations, never silently canonicalized.

Structural failures return no trustworthy row total or prefix column summaries. Inspector performs no writes or active-state operations. Tests verify source bytes (except externally injected mutation), temporary directory inventory, and an existing active-state sentinel remain unchanged. Current full regressions and warning are in the ledger. No resource pilot, canonical row accounting, benchmark, model delivery or independent reproduction performed.

## Proposed mapping decisions — not frozen

No `data/mappings/ibm_hi_small_v1.json` created. Mapping version/hash, timezone-policy hash and source namespace are **unassigned**. Reviewer/date/approval **pending**.

1. Confirm exact Kaggle release/member/archive and data-license binding to local hash. A local content hash identifies bytes but cannot establish their distribution version.
2. Duplicate `Account` headers require a reviewed positional/occurrence mapping bound to exact ordered headers and source hash, or an explicitly reviewed preprocessing/version change. Current data/scoring contract says normalized duplicates block import: it needs an explicit producer/consumer decision before any exception. Do not rename/overwrite columns or infer account direction silently.
3. Preserve separate bank/account sides, source bank/account text and explicit normalization decisions. First/second account direction above is proposed from header placement; confirm semantics before freeze. Identity uses reviewed release namespace/member and one-based CSV record ordinal before filtering; do not derive namespace from this unknown release or IDs from labels/hash.
4. Establish defensible timestamp/timezone evidence or explicitly reviewed assumption before UTC conversion/import. Minute precision is observed; UTC is not. Preserve raw text.
5. Freeze nonnegative Decimal range/scale/zero and currency policies using observed 13 integer digits, up to 6 fractional digits and 17-character source currency names. Current v2 currency maxLength 12 cannot represent this source; resolve through shared review, not truncation/undocumented ISO conversion. Foundation v1 remains unchanged.
6. Review binary label meanings/eligibility separately from valid event facts, label-free features and operational delivery. Missing/invalid-label behavior remains required even though none was observed here. Freeze any optional payment-format mapping only with actual review.

T006 remains incomplete on provenance; T007 `pending_mapping_review`; [T008 review](feature-002-contract-review.md) `pending_consumer_review`. Substantive evaluation stays pending. One next step: obtain the exact acquired-release evidence and review these mapping/contract blockers with the producing and affected consuming owners before import.


## Historical remote collective-approval publication — 2026-11-13

This section came from the three remote documentation commits ending at `6952f1d`. It records the team's earlier collective approval convention and an **intermediate** mapping digest `27445724…439699`. That digest does not match the current final-byte mapping. The later, separately [confirmed final-byte review](#collective-final-mapping-approval--2026-11-13) pins M `a816260a…093e57`, which the T015 CLI checks. The remote commits and their contribution ledger remain in branch history; this dated note preserves their record without treating the intermediate digest as the import authorization.

The user confirms the team works jointly on project code and documentation and that one member?s approval represents the team. The user explicitly approved T007 and T008; this is recorded as collective project-team approval conveyed by the user. Individual owner names are not asserted.

- T007 mapping review: approved collectively on 2026-11-13; approved mapping SHA-256: `27445724712e9bca6f0d22ac991a2f923a18d5df33fc79a41c852244cd439699`.
- T008 producer/consumer contract review: approved collectively on 2026-11-13; the reviewed Feature 002 contract hashes remain the ones in the technical-resolution manifest. The v1 compatibility boundary is preserved.
- This collective approval closes the T007/T008 review gates. Import remains disabled pending implementation of an import command; no runtime importer or v2 application integration is claimed.
