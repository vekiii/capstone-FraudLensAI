# Feature 002 human review and reproduction (T252)

**Status:** T252 is complete for executable candidate `d46699f`. Milan Gavrić confirmed his scoped Feature 002 review and his own Windows T233 run on 2026-11-23. The [closure record](#independent-review-and-t252-closure--2026-11-23) links his confirmation to the prior Windows evidence and the fresh technical follow-up. The 2026-11-22 entries preserve the earlier team and author-side confirmations.

## Review packet and requested scope

1. **Protocol and governance:** review the approved/executed FR-021 protocol and later exact local-copy exception in [`protocol.md`](../../specs/002-data-and-risk-scoring/protocol.md), the frozen `hi-small-temporal-v1` features and chronological partition boundaries, train-only preprocessing, the selected unweighted LightGBM hashes and fixed threshold. Distinguish the historical stopped audit and weighted model from the accepted local opt-in artifact.
2. **Data card and provenance:** review [`data/README.md`](../../data/README.md), [`T203`](T203.md), [`T210`](T210.md), source/snapshot/feature manifests and their checksums. Note the unknown upstream Kaggle revision/acquisition date, publisher timezone and listing terms; the exact local-copy exception does not fill these gaps.
3. **Validation and one authorized test result:** review [`T228`](T228.md), [`T229`](T229.md), [`T230`](T230.md), [`T251`](T251.md) and their aggregate reports against frozen model/prediction/threshold identities. Confirm denominators, partition and UTC period, confusion arithmetic, whole-partition P@K, uncapped daily alerts and uncalibrated score wording. Do not rerun T230 or use test results to tune.
4. **Application and limits:** inspect opt-in loader/risk contract evidence [`T233`](T233.md), [`T236`](T236.md), Stage E [`T242`](T242.md) and results route [`T240`](T240.md). Check that fixture mode works without artifacts, model errors remain controlled, no target labels enter runtime/UI and the risk score is not a final AML finding. Validation was reused for selection/diagnosis; the one test result is for this exact synthetic source/split, not deployment efficacy. The showcase prevalence exception prevents calling it an unbiased performance holdout.
5. **Independent reproduction:** a second contributor should run documented read-only hash/contract checks on their own verified local inputs and record exact environment, commands, observed hashes/results and any blockers. Source/label access must follow existing authorization; reproduction must not repeat the one-time T230 evaluation or access showcase labels under this task. A single contributor's existing setup or CI run is not second-person reproduction.

## Actual review record

| Item | Actual reviewer / date | Scope, commands, observed result |
|---|---|---|
| Manual application flow, results and limitations | User-provided confirmation, 2026-11-22; no personal name inferred | The user states she completed the agreed checklist, found the reviewed local test-provider application flow and results satisfactory and had no objections. Bound to the reviewed session at commit `d46699fbd11219ebc92c6ef002d4924a4c7d4b34` from the [Codex Mac evidence](pr3-final-codex-technical-review-2026-11-22.md). The user did not supply individual clicks, commands, screenshots or a claim of a newer commit; none are inferred. |
| Independent human protocol, data-card, model metrics and limits review | Isidora Popovic's team-representative approval attested (2026-11-22; duration not supplied) | Isidora states the checklist is complete and approved on behalf of the team. Her reply to the direct authorship question confirms participation, while Git history attributes reviewed Feature 002 protocol/data/training commits to the matching author name `Isidora Popovic LUKOWA`. A different nonauthor's review and findings for her work are still required. See the [attestation](T252-independent-approval-attestation-2026-11-22.md). |
| Windows reproduction check and disposition | Isidora reports six matching hashes and successful parity on 2026-11-22 | Isidora supplied SHA-256 outputs for frozen model, manifest, predictions, T230 aggregate report, T219 manifest and label-free test features in the temporary `d46699f` checkout. Her first `T233-parity.py` run returned HTTP `503` because train/validation feature partitions were missing. Codex verified and added those label-free files, then separately observed 8/8 offline and 1/1 HTTP parity. Isidora's subsequent run printed the same success counts and eight selected source rows; the deprecation warning persisted. This author-side check does not replace the required nonauthor review/reproduction. See the [attestation](T252-independent-approval-attestation-2026-11-22.md); keep T252 open. |
| Reported Vedran approval, scope pending | Earlier chat reply on 2026-11-22: `it is vedran and he approved everyhting`; later user clarification says they are the team representative, not Vedran | This is a relayed approval report, not Vedran's personal T252 attestation. The record lacks his reviewed commit, checklist findings and own read-only commands/results. Git `Veki` authored initial Feature 002 specification commit `f63bffe`; that does not establish authorship of Isidora's later protocol/data/model work. No Vedran-specific sign-off is required by written governance. See the [reconciliation](T252-governance-reconciliation-2026-11-22.md). |

### Scope separation

The [Codex technical review](pr3-final-codex-technical-review-2026-11-22.md) independently ran automated tests, artifact hash/parity checks, aggregate-only arithmetic and a fresh HTTP/test-provider worker flow on `d46699fbd11219ebc92c6ef002d4924a4c7d4b34`. It explicitly did **not** perform a browser check because local browser use was disabled in Work settings. The user's later manual confirmation covers the application/results/limitations she reports and does not retroactively turn Codex HTTP checks into Codex browser checks. Neither record is a live LLM evaluation or a human AML decision.

## Technical contribution — 2026-11-22

The [PR #4 Windows run](pr4-windows-review-2026-11-22.md) verified the transferred artifact hashes and frozen-score parity on exact commit `c0d59f2`. It exercised one local test-provider investigation and found a Windows SQLite activation failure in the offline publisher, a Windows SQLite test failure and an open manifest trust issue. The run did not repeat T230 or use record-level labels. An automated technical contribution supplies reproducible evidence for a future human reviewer. The user now attests that the protocol/data-card/model-metrics review and second-person reproduction are complete and approved. The actual reproduction record and reviewer-independence boundary remain undocumented; T252 stays unchecked pending those details.

The follow-up fixed the SQLite failures and required an independent bridge manifest
digest in both runtime consumers. Windows checks again reproduced frozen-score
parity and the test-provider browser flow. [Fixes and execution evidence](pr4-windows-fixes-2026-11-22.md)


## User-reported checklist completion and approval — 2026-11-22

[Approval attestation](T252-independent-approval-attestation-2026-11-22.md) records the user's statement that they performed and approved the full checklist on behalf of the team. The exact duration, independent reproduction details, and reviewer/contributor boundary were not provided in the conversation. T252 remains unchecked until its evidence criteria are documented; no task marker is changed to bypass the gate.

## Final collective approval decision — 2026-11-22

The user again explicitly confirms that the entire team has reviewed and approved the project, including T252, and instructs us to record this as a **collective team decision communicated by its representative**. This confirms team approval of the reviewed work; it is not a claim that the representative is Vedran or that an unrecorded individual performed specific checks. The decision is associated with the reviewed executable candidate `d46699fbd11219ebc92c6ef002d4924a4c7d4b34`; no approval of a later executable revision is inferred.

The [governance reconciliation](T252-governance-reconciliation-2026-11-22.md) at `0600c36` records contributor attribution and the absence of a Vedran-specific or project-wide T252 execution gate. The [Windows attestation](T252-independent-approval-attestation-2026-11-22.md) records six matching frozen-input hashes and Isidora's 8/8 offline, 1/1 HTTP parity output. [T229](T229.md) and [T230](T230.md) bind the selected unweighted LightGBM, fixed threshold and one aggregate test result; [T233](T233.md), [T236](T236.md), [T240](T240.md), [T242](T242.md) and [T251](T251.md) document the local application contracts and limits. These existing checks are reused; no new model evaluation or application test was run for this decision.

**T252 task disposition: open, with collective approval recorded.** The written [task](../../specs/002-data-and-risk-scoring/tasks.md) requires actual human reviewer scope and reproduction; item 5 of this packet calls for a second contributor's read-only checks, environment, commands and observed results. The existing author-side and Codex technical records do not identify that second human contributor's own checks or findings. The final instruction expressly says not to claim an unverified reproduction. No named person's personal attestation is required, and this bounded record gap does not block unrelated authorized work. The one next step for T252 is to attach the actual second contributor's scoped review and reproduction record, then mark the task complete if it meets this criterion.

## PR #5 technical follow-up — 2026-11-23

[Milan's request](../../prompts/development/2026-11-23-pr5-t252-review.md) starts the PR review and asks to close T252 before merging. GitHub reported PR #5 open and mergeable between review head `f25345f` and integration base `d46699f`. The 12 changed files are documentation, and `git diff --check d46699f..f25345f` passed. The governance commit reference above now uses the reachable replacement SHA `0600c36` after the attribution correction.

| Technical check | Observed result |
| --- | --- |
| Reviewed executable inputs | The existing ignored `.cache/pr4-win-fixed` snapshot matched the clean integration checkout on 86 compared files covering `backend/src`, locked configuration, T233 and T230 evidence inputs. The T233 script also matched its Git blob at `d46699f`. |
| `Get-FileHash -Algorithm SHA256` | All eight frozen inputs matched the expected values for the model, trusted manifest, sealed prediction CSV, T230 aggregate, T219 manifest and the three label-free T219 partitions. Expected hashes are in the [Windows attestation](T252-independent-approval-attestation-2026-11-22.md). |
| `T233-parity.py` on Windows with the existing Python 3.14.10 environment | Exit 0 with **8/8 exact offline scores and 1/1 HTTP score match**. The command also checked that fixture case listing returned 200. |
| T230 aggregate arithmetic and identity | Ten named Python assertions passed for counts, precision, recall, F1, sealed prediction hash, threshold, label-write flag and top-K denominators. The existing aggregate contains 233,070 rows and 218 positives. Precision 0.676923, recall 0.201835 and F1 0.310954 match the recorded values. An initial PowerShell assertion failed, so the check was repeated from the same verified JSON using Python and individually reported assertions. |

To reproduce the parity check from the main checkout in PowerShell, use the recovered Windows snapshot and interpreter.

```powershell
Push-Location '.cache/pr4-win-fixed'
try {
    $env:PYTHONPATH = (Resolve-Path 'backend/src').Path
    $env:INVESTIGATION_ENABLED = 'false'
    & '..\pr4-win-c0d59f2\.venv-31410\Scripts\python.exe' -B evidence/tasks/T233-parity.py
} finally {
    Pop-Location
}
```

Codex performed the fresh technical checks. This follow-up reused the existing report and prepared artifacts for read-only checks. The live-provider run remains a separate demo requirement.

## Independent review and T252 closure — 2026-11-23

Milan Gavrić confirmed that he personally reviewed the Feature 002 protocol, data card, T230 aggregate metrics and limitations at `d46699f`. When asked to distinguish executing the Windows check from observing it or reading the recorded output, he confirmed **“Лично сам покренуо T233”**. He reported no further findings in his reply. The [reviewer replies](../../prompts/development/2026-11-23-pr5-t252-review.md#reviewer-confirmation) preserve his wording and the scope of the questions.

- **Independence.** Milan's integration and Windows bridge fixes (`f68d2cd`, `40ce7e3`) were his own contributions. His independent review here covers Feature 002's model protocol, data, metrics and limitations. The Git history of the protocol, data card and training implementation records other authors.
- **Reproduction.** The linked [Windows evidence](pr4-windows-fixes-2026-11-22.md) identifies the locked Python 3.14.10 environment, the already verified frozen inputs and the `T233-parity.py` command. That run recorded **8/8 exact offline scores and 1/1 HTTP score match**. The script uses sealed predictions and label-free features and verifies their frozen identities. Codex separately reproduced the same output in this follow-up. Milan did not supply a new transcript or duration with his confirmation.
- **Disposition.** The earlier collective approval, Milan's scoped nonauthor review and his personal Windows T233 execution cover the remaining T252 evidence requirement. The frozen LightGBM, threshold and existing T230 aggregates identify the reviewed scope. The final demo still requires a separate live-provider run on the integrated candidate.
