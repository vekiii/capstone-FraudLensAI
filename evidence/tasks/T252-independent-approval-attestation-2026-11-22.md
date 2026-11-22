# T252 independent review and team approval attestation — 2026-11-22

## Record status

**User-reported disposition: APPROVED on behalf of the team. T252 remains open.** In this conversation the user states that they performed the T252 manual checklists and approve the reviewed scope on behalf of the whole team. They initially identified as an independent reviewer, but later identified as Isidora Popovic and answered a direct question about Feature 002 authorship with `i did all as a team`. This document records those statements as user attestations; it does not convert assistant-prepared summaries into reviewer actions or record separate approvals from unnamed team members.

The T252 acceptance record calls for actual reviewer scope and reproduction details. The conversation now includes one user-supplied Windows PowerShell SHA-256 result for a label-free test feature file. It does not provide the reviewer's personal name, exact elapsed review time, complete environment, remaining artifact/contract results, or a list of specific findings. The user-reported approval is recorded, but these missing details prevent marking T252 complete under the existing review gate. No duration is estimated.

## Review identity and scope

- **Reviewer/team representative:** Isidora Popovic, as supplied by the user in the later reply. This is one representative approval, not individual approvals by every team member.
- **Independence:** Git history in the reviewed `d46699f` ancestry attributes protocol, data and training work to `Isidora Popovic LUKOWA`, including `70f3019` (T212 temporal protocol), `937beec` (T219 partition hashes), `03c69c2` (T226 validation evaluation), and `14fede4` (IBM-day split/LightGBM pipeline). Asked directly whether those commits were hers and who independently reviewed them, the user replied `isidora popovic i did all as a team`; no separate reviewer or findings were named. The reply does not map every contribution individually, but it confirms substantial participation under the matching name. Isidora's team approval cannot supply nonauthor review for her own work. The prior T252 record also scoped the user's manual confirmation as not independent of her Feature 002 model work.
- **Team representation:** user expressly says the approval is on behalf of the whole team. No other team member is named and no separate individual responses are in this conversation; this record attributes the representative approval to the user.
- **Decision date:** 2026-11-22 (conversation date); exact time not supplied.
- **Review duration:** not stated in the conversation; not estimated.
- **Reviewed PR #3 candidate:** `d46699fbd11219ebc92c6ef002d4924a4c7d4b34`, as referenced by the T252 packet. `git ls-remote origin refs/pull/3/head` independently returned that same commit on 2026-11-22 at approximately 20:54 UTC; this is a point-in-time check, not a future-head guarantee.
- **Decision:** user-reported approval of all five T252 checklist areas, on behalf of the team, within the reviewed candidate and the limitations recorded below.

## Checklist scope and supporting repository evidence

The user states that they completed and approved each checklist area. The evidence links below are the repository support discussed in this conversation; they are technical records, not proof of the user's own execution.

| Review area | User-reported outcome | Supporting evidence and scope limits |
|---|---|---|
| Protocol and model choice | Approved, per user attestation | `specs/002-data-and-risk-scoring/protocol.md`; `evidence/tasks/T228.md`; `T229.md`; `T230.md`. Records bind the unweighted LightGBM model SHA-256 `3b4e4019312d60610dd0094c6697897a061611a60e7777ed7be35e133af9451c`, trusted manifest `c766e90159a70eff2d1f29d5ff425029af20ff123f1fad08e45f9fc416076d45`, and fixed threshold `0.2489517623052024`. The model was selected using validation; the records disclose later validation reuse for diagnosis/ranking. |
| Data provenance | Approved, per user attestation | `data/README.md`; `evidence/tasks/T203.md`; `T210.md`; source and feature manifests. The exact local source copy is hash-bound, while upstream Kaggle revision, acquisition date, listing terms, and publisher timezone remain unknown. Approval does not resolve these unknowns. |
| Metrics and claims | Approved, per user attestation | `evidence/tasks/T228.md`, `T229.md`, `T230.md`, `T251.md`. T230 records one authorized aggregate-only test result on 233,070 rows for 2022-09-06 00:00–11:12 UTC: TP/FP/TN/FN 44/21/232,831/174; precision 0.676923; recall 0.201835; F1 0.310954; AP 0.2745021334479726; ROC AUC 0.976155; Brier 0.000770. Threshold alerts: 65. P@20/50/100 are 18/20, 38/50, 52/100 over the whole partition. Probabilities are uncalibrated; validation was reused; the results are not deployment performance claims. The showcase prevalence exception means showcase is not an unbiased holdout. |
| Application behavior and limits | Approved, per user attestation | `evidence/tasks/T233.md`, `T236.md`, `T240.md`, `T242.md`, and the PR #3 Codex review. These report hash-gated artifact loading/fail-closed tests, fixture availability, label-free parity, frontend/backend regression, browser result/error states, and test-provider investigation behavior. The test-provider flow is not a live LLM evaluation or a human AML decision. |
| Independent reproduction | Approved, per user attestation; partial execution result supplied | T233/T236/T240/T242 and the Codex/Windows review records contain technical checks by their recorded contributors. The user supplied one matching PowerShell SHA-256 for the label-free test feature file (below). The conversation does not include their complete environment, remaining observed hashes, contract/parity result, or reproduction date/time. Existing T252 criteria require the actual scope and results to document second-person reproduction. |

## Known limitations accepted within this reported approval

The approval does not change the recorded facts that the scores are uncalibrated, validation was reused for selection/diagnosis, source provenance is incomplete, T230 is one result for a specific synthetic source and split, and showcase is not an unbiased holdout. The documented app/API is a local single-user workflow; the evidence is not a production readiness claim. No new test evaluation, training, label access, showcase replay, or live provider call was performed for this record.

## Reviewer-supplied Windows hash and renewed approval

After a PowerShell `Get-FileHash -Algorithm SHA256 -LiteralPath` check was suggested for the original checkout's `data/processed/t219-ibm-day-60-20-20-v1/test.jsonl`, the user pasted a result table with algorithm `SHA256`, hash `693320617CD8FF05C3BA177FCF9E3447BD2F7B92C5B29736FCE304D60023C9E0`, and a path column truncated by PowerShell's display. The digest matches the T219 frozen label-free test-feature SHA-256 `693320617cd8ff05c3ba177fcf9e3447bd2f7b92c5b29736fce304d60023c9e0`. The exact execution time and complete environment were not supplied. This is a user-reported result for one file; earlier assistant-side rehashes are separate technical observations.

The user then stated, "everythign is approved by me in the name of the team". This renews the representative approval attestation without adding named individual team approvals. In the separate T252 worktree at commit `d46699f`, the ignored feature files, frozen model/prediction files and T230 aggregate report were still absent when checked by Codex. No user-run parity or report-hash result has been supplied, so this single source-file hash does not establish complete independent reproduction.

## Follow-up identity and reproduction response

Asked for the reviewer's name and which Feature 002 work they personally authored, the user replied `isidora as a team`. This identifies the team representative by first name but does not answer the authorship question. Asked whether the remaining frozen model/prediction/report hashes and `T233-parity.py` had been completed, with a request to paste observed results or list missing files, the user replied `yes`. Record that as a claim of completion, not as observed hash or parity results. A fresh local check of the separate Windows T252 worktree still found the ignored model, prediction, aggregate report and test feature file absent; the conversation does not identify a different checkout or provide the actual outputs. No assumption is made about what Isidora ran elsewhere.

In a later direct follow-up, the user answered the authorship question `isidora popovic i did all as a team`. Asked again for the actual remaining SHA-256 and parity outputs, the user asked `how do i get that sha`. The actual model, prediction, manifest, T230 report and parity results remain unprovided. A fresh check found the frozen model/prediction and T230 aggregate report absent in both available Windows checkouts; the T219 manifest and label-free test feature file exist only in the original checkout. Their absence prevents computing those missing digests from the files currently available here. No claim is made that the user did or did not run checks in another environment.

## Open closure items

1. Obtain the original ignored frozen model/prediction directory and existing aggregate T230 report through the approved team transfer, then record actual checkout/environment, read-only commands, observed hashes/contract results and reproduction date. The replies `yes` and `how do i get that sha` do not supply these results.
2. Obtain and record a separate nonauthor's review, findings and disposition for the Feature 002 protocol, data, training and related metrics work that Isidora contributed to.
3. Keep review duration as `not recorded` unless the reviewer supplies a truthful measured/remembered duration.
4. Recheck the PR #3 head before applying the approval to any commit later than the recorded candidate; the 2026-11-22 remote check matched `d46699f`.

**Task status: T252 remains unchecked; this is not a closure waiver.** T233, T236, T240, and T242 retain their previously recorded technical completion evidence.
