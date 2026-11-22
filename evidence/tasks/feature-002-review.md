# Feature 002 human review and reproduction (T252)

**Status:** Isidora Popovic, self-identified as team representative and Feature 002 contributor, attests on 2026-11-22 that the T252 manual checklist is complete and the reviewed scope is approved on behalf of the team. [The approval attestation](T252-independent-approval-attestation-2026-11-22.md) records six matching user-reported Windows SHA-256 outputs and a successful `T233-parity.py` rerun from the reviewed checkout. T252 remains open because separate nonauthor review of Isidora's Feature 002 work is not recorded. No duration or unreported finding is inferred.

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

### Scope separation

The [Codex technical review](pr3-final-codex-technical-review-2026-11-22.md) independently ran automated tests, artifact hash/parity checks, aggregate-only arithmetic and a fresh HTTP/test-provider worker flow on `d46699fbd11219ebc92c6ef002d4924a4c7d4b34`. It explicitly did **not** perform a browser check because local browser use was disabled in Work settings. The user's later manual confirmation covers the application/results/limitations she reports and does not retroactively turn Codex HTTP checks into Codex browser checks. Neither record is a live LLM evaluation or a human AML decision.

## Technical contribution — 2026-11-22

The [PR #4 Windows run](pr4-windows-review-2026-11-22.md) verified the transferred artifact hashes and frozen-score parity on exact commit `c0d59f2`. It exercised one local test-provider investigation and found a Windows SQLite activation failure in the offline publisher, a Windows SQLite test failure and an open manifest trust issue. The run did not repeat T230 or use record-level labels. An automated technical contribution supplies reproducible evidence for a future human reviewer. The user now attests that the protocol/data-card/model-metrics review and second-person reproduction are complete and approved. The actual reproduction record and reviewer-independence boundary remain undocumented; T252 stays unchecked pending those details.

The follow-up fixed the SQLite failures and required an independent bridge manifest
digest in both runtime consumers. Windows checks again reproduced frozen-score
parity and the test-provider browser flow. [Fixes and execution evidence](pr4-windows-fixes-2026-11-22.md)


## User-reported checklist completion and approval — 2026-11-22

[Approval attestation](T252-independent-approval-attestation-2026-11-22.md) records the user's statement that they performed and approved the full checklist on behalf of the team. The exact duration, independent reproduction details, and reviewer/contributor boundary were not provided in the conversation. T252 remains unchecked until its evidence criteria are documented; no task marker is changed to bypass the gate.
