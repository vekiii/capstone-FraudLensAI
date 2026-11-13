# Prompt 1 review packet: source mapping and v2 amendments

**Historical proposal packet, superseded technically by the user's 2026-11-13
approval and [resolution](../../../evidence/tasks/feature-002-technical-resolution.md).**
The pinned v8 download was authorized and completed with matching CSV hashes;
binary semantics now have publisher reference-code evidence. The selected UTC+00
policy remains an assumption. Technical changes are applied in the authoritative
contracts and [pending mapping](../../../data/mappings/ibm_hi_small_v1.json), with
import disabled and actual team review still open. Original JSON proposals below
are retained as historical review inputs, not current configuration. The exact
pre-amendment contract text is preserved in [baseline](technical-amendment-baseline.json)
so proposal preconditions remain reproducible. Future steps marked NOT RUN below
are historical suggestions; consult the actual download receipt before repeating.

2026-11-13 Europe/Belgrade. **Proposal only. T006–T008 remain open.** No approved mapping, source namespace, time-policy hash or owner approval is created by this packet. Nothing here is read by the application/CLI. Do not copy it to `data/mappings/` or apply it to the authoritative contracts before the pending decisions.

[Independent source investigation](../../../evidence/tasks/feature-002-source-investigation.md) separates local observations, primary documentation and assumptions. [Mapping proposal](source-mapping.json) and [v2 change proposal](v2-contract-changes.json) are machine-readable review inputs, not executable/frozen configurations. [Validation evidence](../../../evidence/tasks/feature-002-proposal-validation.json) identifies their exact hashes.

## What is established

| Item | Verified evidence | Remaining limitation |
|---|---|---|
| Public distribution | Kaggle metadata: dataset ID 2948142, current version 8, updated 2025-07-08T14:59:13.28Z. | Current public version is not proof of the acquired version. |
| Data license | Kaggle listing names CDLA-Sharing-1.0; pinned IBM README independently identifies that data license, separately from code Apache-2.0. | Bind the local member to a verified/adopted release; acquisition history remains unknown. |
| File identity | Local SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`; public current member size matches 475,664,283 bytes. | Returned member metadata contains no checksum. Size/name/count similarity cannot prove byte identity or historical version. |
| Account direction | IBM's pinned reference formatter explicitly pairs From Bank with column 2 and To Bank with column 4. | This supports the positional mapping; it does not approve our duplicate-header exception. |
| Timestamp | Local complete scan: `%Y/%m/%d %H:%M`, minute precision, no zone. IBM formatter parses the same format without tzinfo. | No verified UTC offset, source timezone, transaction lifecycle stage or cross-bank clock synchronization. |

No paper, reference-code example or third-party dataset card is treated as an observed local field/count. The publisher's paper version/date is not the dataset release.

## Proposed mapping to review

Use **exact ordered raw headers and zero-based position**, never a dictionary keyed solely by column name:

| Position | Raw header | Proposed role |
|---:|---|---|
| 0 | Timestamp | event_time_raw |
| 1 | From Bank | sender_bank |
| 2 | Account, first occurrence | sender_account |
| 3 | To Bank | receiver_bank |
| 4 | Account, second occurrence | receiver_account |
| 5 | Amount Received | received_amount |
| 6 | Receiving Currency | received_currency |
| 7 | Amount Paid | paid_amount |
| 8 | Payment Currency | paid_currency |
| 9 | Payment Format | optional operational payment_format |
| 10 | Is Laundering | private evaluation label only |

All eleven header positions are required. An optional **value** does not make its column optional. Preserve original UTF-8/ASCII-compatible source and comma dialect. Proposal rejects a BOM for this exact no-BOM source binding; source-independent inspector BOM support stays unchanged.

Approve exactly one duplicate exception: literal `Account` at positions 2/4, only with the full eleven ordered headers and verified source binding. Every other duplicate, normalized collision, reorder, alias, missing/unknown/extra target-like column blocks processing pending review. `Account.1` is a possible library-generated name, not an observed raw header or a permitted automatic alias. The current inspector still reports the duplicate and does not implement this exception.

Keep both bank/account sides as exact strings with 1–120 characters and at least one non-whitespace character. Do not trim, remove padding/zeros, cast to integer or copy IBM's ambiguous plain concatenation: use the already proposed length-delimited qualified key. These tokens join history only; they are not predictors.

Use exact paid/received decimal strings and Decimal arithmetic. Proposed support: 13 integer digits, scales 0–6, maximum `9999999999999.999999`, nonnegative values including zero. **Design choices:** scale support 0–6 and allowing zero extend beyond observed scales 2/6 and no observed zeros. Reject negatives, nonfinite/exponent forms, leading plus/redundant integer zeros, missing money/currency and excessive digits; never round, convert FX or collapse the sides. Preserve all fifteen observed currency names exactly, with source-specific allowlist and maxLength **17**. New currencies require a reviewed mapping revision. Preserve reviewed payment formats; a missing format is null. Binary `1` positive / `0` negative is proposed; the publisher's exact binary-token definition remains unverified. Missing/other labels must not reject otherwise valid event facts or enter predictors.

Use one-based CSV record ordinal before filtering, excluding the header; multiline records count once. Establish the release/member namespace only after provenance review. Retain the existing proposed D/C distinct-domain digest scheme and full collision inputs. Dataset version binds raw hash, approved mapping hash and approved time-policy hash; those hashes remain unassigned here. Do not generate identities or import now.

## Timestamp decision: no source UTC claim

Keep import blocked by default. Two choices are ready for review:

1. **Documented interpretation:** obtain publisher documentation that defines the clock and its scope. Record an exact reference and policy; use `documented_source_timezone` only when actually documented. Current evidence does not satisfy this.
2. **Explicit educational convention:** approve `synthetic-common-wall-clock-fixed-offset-zero-v1`. Treat every recorded minute as one common synthetic analysis coordinate at fixed +00:00, set seconds to `00`, preserve raw text/minute ties, and use new `time_basis = assumed_utc_for_synthetic_benchmark`. This is an assumption about comparability, not a recovered source fact. It cannot establish real-world UTC chronology, settlement time or cross-bank synchronization. Do not derive offset from this workstation, bank/currency names or naive `.timestamp()` calls. Hash/version the approved policy, bind it to the dataset/run, and show the assumption in dataset UI/investigation/priority context. Actual `scored_at` remains execution time in real UTC.

Recommendation: present choice 2 as the concrete capstone convention for owner consideration, while retaining the block until an actual decision. Fixed offsets preserve relative ordering/windows only **under the assumed common clock**; they do not prove that clock model. The draft JSON has `selected_policy: null`; the optional schema patch is not part of the mandatory core patch.

## Exact v2 amendment proposal

[v2-contract-changes.json](v2-contract-changes.json) contains RFC 6902 operations with base hashes and test preconditions. They are applied **in memory only** by the review helper.

- Money.currency: `maxLength: 12` → **17**. Keep source text; backend/frontend/import mapping must agree. The source-specific allowlist is a mapping rule, while the public shape remains length-bounded text.
- CaseDetailV2: add **required envelope `dataset_version`**, referencing existing DatasetVersionId. Keep public TransactionV2 unchanged. Require equality among detail envelope, assessment, pinned list and completed run; check the internal canonical transaction's version at the repository boundary. Replace the API sentence that refers to a nonexistent public transaction.dataset_version. This makes detail version explicit for consumers without duplicating it on every public transaction.
- Strict end matching: replace terminal `$` in Instant, TransactionId, CaseId, RunId, DatasetVersionId and Money.amount patterns with `(?![\s\S])`. Correctly isolated probes show current ID/money patterns accept a final newline. Earlier probes retained root `oneOf` and incorrectly reported rejection; that evidence is corrected in the investigation/review records. Keep valid decimal/fractional timestamp forms.
- Offline contract: replace unconditional duplicate rejection with the exact source-bound `Account` occurrence exception above, retaining default rejection for everything else. This is a proposed contract amendment, not permission to bypass current validation.
- **Optional only after timestamp-convention approval:** append `assumed_utc_for_synthetic_benchmark` to TransactionV2.time_basis. Do not relabel an assumption as source_explicit_timezone or documented_source_timezone.

The detail shape after approval would add a field at the same level as `case_id`, for example `"dataset_version":"dv_example_1"`, equal to risk_assessment.dataset_version. The old detail example would then be invalid until updated. No example is a local transaction or a model result.

The candidate schema cannot express all cross-object equalities: the validation helper explicitly demonstrates that a syntactically valid mismatched version still passes JSON Schema. Later coordinated typed validators/decoders need negative cases for envelope/assessment/list/run/transaction mismatch, missing detail version, final-newline IDs/amounts, currency length 18, labels/extras, wrong snapshot, wrong time basis/policy and precision drift. These runtime checks are **not implemented** by the review probes.

V1 schema/models/decoder, three-case ordering and unconditional fixture banner stay as-is. The later v2 consumer migration must preserve server time/ID order, snapshot pinning/409/503 behavior, truthful dataset/scorer notices and explicit assumed-clock wording if selected. These are future coordinated implementation obligations, not work authorized by this continuation.

## Exact access and verification steps — not executed

No Kaggle account was needed for the public metadata investigation. Try retained acquisition evidence first: browser download history/version URL, original archive/manifest, or a genuine Kaggle cache record. A directory named `8` alone is not proof. Record the displayed version, member, acquisition provenance and license; do not share credentials or tokens.

If provenance cannot otherwise be recovered, the concrete proposal is to **verify/adopt a reproducible version-8 reference**, while keeping original acquisition history unknown. After authorizing a download, use a Kaggle client already configured through your own permitted authentication process. Current official [CLI documentation](https://github.com/Kaggle/kaggle-api/blob/main/docs/datasets.md) supports the final `/8` version component. Check local `kaggle --version`/help before running; do not install/update dependencies as part of this packet.

```powershell
# Future user-authorized steps from repository root; NOT RUN.
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/002-data-and-risk-scoring'
git check-ignore -v data/raw/release-verification/v8/probe.zip
kaggle datasets files ealtman2019/ibm-transactions-for-anti-money-laundering-aml/8 --csv
kaggle datasets download ealtman2019/ibm-transactions-for-anti-money-laundering-aml/8 --file HI-Small_Trans.csv --path data/raw/release-verification/v8
Get-ChildItem -LiteralPath data/raw/release-verification/v8
```

Use a **new, empty** destination; do not use force/overwrite or replace the original CSV. The current CLI documents large single files arriving as a ZIP. If `HI-Small_Trans.csv.zip` is returned:

```powershell
# NOT RUN: retain the archive and its hash; extract to a new directory.
Get-FileHash -LiteralPath data/raw/release-verification/v8/HI-Small_Trans.csv.zip -Algorithm SHA256
Expand-Archive -LiteralPath data/raw/release-verification/v8/HI-Small_Trans.csv.zip -DestinationPath data/raw/release-verification/v8/extracted
Get-FileHash -LiteralPath data/raw/release-verification/v8/extracted/HI-Small_Trans.csv -Algorithm SHA256
Get-FileHash -LiteralPath data/raw/HI-Small_Trans.csv -Algorithm SHA256
```

If a CSV is returned directly, hash that returned CSV instead. Compare the extracted/reference **CSV bytes**, not ZIP hash, to the existing digest above. A match proves compatibility with the pinned downloaded member; it does not prove which historical release was originally downloaded if releases reuse bytes. Preserve the version-specific response/URL, license metadata and hash evidence, then record an explicit reviewed adoption if using v8 as the namespace. A mismatch leaves the original untouched and the release gate open. Do not download patterns/accounts or any other dataset member for this step.

For missing semantics: open the version-specific [Kaggle page](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml/versions/8), inspect both Account column descriptions, Timestamp and binary label definition. IBM's linked [Box documentation](https://ibm.box.com/v/AML-Anti-Money-Laundering-Data/file/780515045707) is named IBM_Synthetic_AML-Data.pdf; accessing/downloading it may require your browser or account. If obtained, record its version/hash/page and whether it actually covers Kaggle v8 rather than the older Box release. Ask for documentation of generator clock/timezone, cross-bank clock comparability and what event Timestamp represents. If it remains silent, retain unknowns or obtain the explicit convention decision. No author/team messages have been sent.

## Decisions and real review record required

Ask the data/scoring producer, frontend/API owner, and affected investigation/priority owners to review **these exact proposal hashes and the unchanged base contract hashes**. No names are assigned here; reviewer/date/decision remain null. They need to decide: source/release adoption; strict positional exception; proposed monetary/optional-field/label rules; documented time vs explicit convention; currency bound/detail envelope/end-assertion amendments; and the coordinated v1-preserving consumer migration. Record actual findings and approval/rejection per owner under the Foundation shared-contract procedure.

One next step: review this packet, then choose retained provenance evidence or authorize the single-file pinned-reference verification and record the required owner decisions. T006 provenance, T007 mapping and T008 consumer gates cannot be closed from this proposal alone. Prompt 2, import and training remain unstarted.
