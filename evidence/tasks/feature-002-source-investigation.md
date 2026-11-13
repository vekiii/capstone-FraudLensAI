# Prompt 1 continuation — independent T006–T008 investigation

Historical pre-download investigation. [Subsequent user-authorized resolution](feature-002-technical-resolution.md)
now verifies/adopts the matching v8 member, confirms binary semantics through
pinned publisher code, applies technical amendments and selects the explicit
assumed clock. Original snapshot timestamps/results below are retained; pending
team review remains real, while their earlier source-access/technical decisions
have been resolved. Do not treat this pre-download snapshot as current gate status.

2026-11-13 Europe/Belgrade; public snapshot retrieved around 05:36 local (04:36 UTC). [Original request](../../prompts/development/002-source-mapping-review-request-2026-11-13.md). Baseline branch `002-data-and-risk-scoring`, HEAD `63d33843bc6483d66362e10133ec21c261c76df1`; initial working tree clean. This revision supersedes the earlier session baseline only for this continuation. Read root AGENTS.md then next_work.md, explicitly selected `specs/002-data-and-risk-scoring`, reread T006–T008, audit/review, source/model/contracts and Foundation review procedure.

**Independent investigation/proposal preparation complete. Gates remain pending.** T006 lacks exact local-release binding; T007 mapping/clock/label decisions and T008 actual owner review are not complete. FR-001–004, FR-023, FR-026. Contributor: Codex session, not a human reviewer. Reviewer/date/approval remain unassigned; no independent reproduction or full feature acceptance claim.

## Primary evidence and its limits

Durable sanitized [metadata snapshot](feature-002-source-investigation.json) records HTTP status, exact public URLs, response SHA-256, UTC fetch times, selected publisher metadata and local source hash. [Reproduction helper](feature-002-source-investigation.py) reads only fixed public metadata/source-code URLs and the authorized local CSV hash; it reads no credentials and fetches no dataset members. It is an evidence script, not application behavior.

| Source | Actual finding | What it does not establish |
|---|---|---|
| [Kaggle view API](https://www.kaggle.com/api/v1/datasets/view/ealtman2019/ibm-transactions-for-anti-money-laundering-aml) | Dataset ID 2948142; currentVersionNumber 8; lastUpdated 2025-07-08T14:59:13.28Z; returned version note Update 2025-07-08; listing data license CDLA-Sharing-1.0. | Exact version downloaded on 2026-11-13, or identity of local bytes. Only one published version entry was returned; it is not a reconstructed full version history. |
| [Kaggle file-list API](https://www.kaggle.com/api/v1/datasets/list/ealtman2019/ibm-transactions-for-anti-money-laundering-aml) | Eighteen current members; HI-Small_Trans.csv has totalBytes 475664283, creationDate 2025-07-08T15:02:26.907Z. | No member checksum or column descriptions returned. Matching size/name is supporting evidence, not a hash/version match. Adding datasetVersionNumber=8 returned the same metadata; that alone does not prove the legacy endpoint honors the query. |
| [IBM README pinned at 366436e](https://github.com/IBM/AML-Data/blob/366436e605ac7713bf4eee8b4fbc45984d64427c/README.md) | Separates data CDLA-Sharing-1.0 from repository Apache-2.0 and links the same Kaggle distribution. GitHub API identifies last README change 2023-11-23. | Its Git commit is a documentation revision, not a dataset release. |
| [IBM formatter pinned at 31d5d45](https://raw.githubusercontent.com/IBM/Multi-GNN/31d5d4578c9f1b9bc89a890a5b344787ee39e6ee/format_kaggle_files.py) | Lines 60/63 pair bank fields with columns 2/4 for sender/receiver. Lines 41/42 parse minute text without tzinfo and call timestamp(). Public source hash fe320f4d… matches pinned retrieval. | No source timezone/offset or lifecycle-stage definition. Reference-code choices are not source facts or approval to use its float conversion, entity concatenation, row reordering or relative-time offset. Code was read, never executed on data. |
| [Publisher paper v2](https://arxiv.org/html/2306.16424v2) | Directed account-to-account transfers; transaction date/time features; Kaggle is the maintained distribution (Appendix G). | Paper version/date is not Kaggle release provenance. No timezone statement found in inspected text. Figure/sample values are not local observations. |
| [Python 3.14 datetime documentation](https://docs.python.org/3.14/library/datetime.html#datetime.datetime.timestamp) | Naive datetime timestamp conversion depends on assumed local time. | Calling timestamp() in the reference code does not prove that the generator emitted UTC. |

The version-8 **public listing license is now directly corroborated**, improving on the earlier README-only evidence. Applicability to this exact local file remains conditional on its release binding. This records publisher license identification, not an independent legal opinion.

The Kaggle description warns about transactions after its stated primary activity period and points to [discussion 427517](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml/discussion/427517). Its summary describes a tail containing laundering transactions. That is a publisher warning, **not a newly observed label/time relationship in this local file**. Description/member-count differences also show why the old narrative cannot serve as a v8 file manifest. Record this for the later prospective benchmark-view/eligibility review; do not trim dates, inspect holdout labels, revise splits or evaluate now.

## Timestamp and field conclusions

Local [complete audit](feature-002-source-audit.md) already establishes eleven exact headers, duplicate Account occurrences at 2/4 and timezone-free minute text. Independent IBM code now supports the account directions. No raw sample or row was used to infer direction; no raw/processed data was modified. No documented timezone, common-clock guarantee, booking/value/settlement interpretation or binary-label token definition was established from inspected publisher sources.

IBM's linked Box page is reachable as HTML outside the restricted web reader and names `IBM_Synthetic_AML-Data.pdf`, but no document text was obtained. A `timezone` key in that HTML belongs to visitor/viewer metadata, not the dataset. The older Box distribution must not be silently treated as current Kaggle documentation. Exact user-access steps and questions appear in the [review packet](../../specs/002-data-and-risk-scoring/proposals/README.md#exact-access-and-verification-steps--not-executed).

Retain `verified_local_release: null`, namespace null, source_timezone null and selected time policy null. Public v8 plus identical file size is a **candidate**, not a recovered release. A future pinned-member byte match can justify explicitly adopting a reproducible v8 reference without claiming to recover original acquisition history when versions reuse bytes.

## Concrete, unfrozen proposal and checks

[Review packet](../../specs/002-data-and-risk-scoring/proposals/README.md), [mapping JSON](../../specs/002-data-and-risk-scoring/proposals/source-mapping.json), [v2 JSON Patch proposal](../../specs/002-data-and-risk-scoring/proposals/v2-contract-changes.json). Exact file/candidate hashes are in [validation output](feature-002-proposal-validation.json); approved mapping/time-policy hashes remain null. The core proposal changes currency length to 17, adds required detail-envelope dataset_version, corrects strict terminal matching and proposes an exact source-bound positional duplicate exception. An optional separate patch enables an explicitly disclosed assumed clock only if owners approve it.

Corrected an earlier review-probe error: `{**schema, '$ref': ...}` retained the root response `oneOf`, invalidating standalone ID/Money probes. The new helper includes only `$schema`, `$defs` and the requested `$ref`. Correctly isolated probes confirm that valid IDs and decimal amounts pass, but current ID/money patterns accept a final newline. The proposed strict end assertions reject it. There is no claimed decimal-point or fractional timestamp defect: positive examples pass the corrected probes. Earlier reported ID-newline rejections are superseded.

Offline candidate probes pass all fifteen source currencies, reject length 18/empty/wrong-type currencies, require the new detail version, reject invalid version forms and label extras, validate the optional assumed-clock discriminator separately, and leave all actual contracts unchanged. They explicitly demonstrate that schema alone still accepts a syntactically valid cross-object version mismatch; runtime backend/frontend semantic enforcement is future work, not verified here.

## Commands and actual results

Repository root, existing CPython 3.14.7/jsonschema 4.26.0. No installs/lock updates.

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/002-data-and-risk-scoring'
git status --short
git branch --show-current
git rev-parse HEAD
git check-ignore -v data/raw/HI-Small_Trans.csv data/artifacts/feature-002-source-inspection.json
Get-FileHash data/raw/HI-Small_Trans.csv,specs/002-data-and-risk-scoring/contracts/schemas.json,specs/002-data-and-risk-scoring/contracts/api.md,specs/002-data-and-risk-scoring/contracts/data-and-scoring.md -Algorithm SHA256
.\.venv\Scripts\python.exe evidence/tasks/feature-002-source-investigation.py
.\.venv\Scripts\python.exe evidence/tasks/feature-002-proposal-validation.py
```

Git/boundary/hash commands exited 0. Local CSV hash unchanged (`b19d39f5…`); authoritative contract hashes match the prior review's exact hashes. Initial restricted-shell public HTTP probes received WinError 10013 (no metadata result). Read-only network escalation subsequently succeeded for public HTTP metadata/code without credentials. Web reader attempts for Kaggle/Box failed or returned no readable content; primary-source urllib retrieval provided the successful independent path. No automatic-review rejection occurred.

Public snapshot helper exited 0, five HTTP 200 results, with full-body response hashes in the JSON. Initial offline proposal helper exited 1 due to the root-union probe construction above; after correcting it and adding the demonstrated strict-end amendment, helper exited 0. These are document/design probes, **not application RED/GREEN**, model evaluation or consumer integration acceptance. The T004/T005 historical test runs are unchanged, not rerun or re-claimed for this documentation slice. Application/backend/frontend tests and browser checks not run here because no application or authoritative contract implementation changed.

Final verification: `.\.venv\Scripts\python.exe -m ruff check evidence/tasks/feature-002-source-investigation.py evidence/tasks/feature-002-proposal-validation.py` exited 0. A local Python document/inventory check passed for 15 changed/new evidence/proposal/handoff files, 77 local links, UTF-8, balanced code fences, JSON parsing, unchanged five completed task markers and all three gates still open. `git diff --check` exited 0. `git diff --exit-code HEAD -- backend frontend data .gitignore specs/001-project-foundation specs/002-data-and-risk-scoring/contracts uv.lock pyproject.toml .agents .specify` exited 0, verifying those tracked boundaries unchanged. Core patch has 17 operations (including test preconditions); the separately gated optional time patch has two. Candidate schemas exist in memory only; neither authoritative schema nor approved mapping was written.

No account access, dataset-member/PDF download, import, scoring, activation, training, message to owners/authors, branch change, commit or push. The full raw file was rehashed, not reparsed. Existing Foundation/inspection code, tests, raw bytes, fixture and locks preserved. One next step: review the concrete packet, supply retained provenance or authorize the single-file v8 reference verification, and record actual producing/affected-consuming owner decisions before freezing T007/T008.
