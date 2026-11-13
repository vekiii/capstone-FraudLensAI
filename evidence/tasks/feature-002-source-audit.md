# Feature 002 source inspection, audit and mapping decisions

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
