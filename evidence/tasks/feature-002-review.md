# Feature 002 human review and reproduction (T252)

**Status:** pending human review and second-person reproduction. Prepared 2026-11-21; no reviewer, review date, reproduction command or outcome is inferred from this preparation.

## Review packet and requested scope

1. **Protocol and governance:** review the approved/executed FR-021 protocol and later exact local-copy exception in [`protocol.md`](../../specs/002-data-and-risk-scoring/protocol.md), the frozen `hi-small-temporal-v1` features and chronological partition boundaries, train-only preprocessing, the selected unweighted LightGBM hashes and fixed threshold. Distinguish the historical stopped audit and weighted model from the accepted local opt-in artifact.
2. **Data card and provenance:** review [`data/README.md`](../../data/README.md), [`T203`](T203.md), [`T210`](T210.md), source/snapshot/feature manifests and their checksums. Note the unknown upstream Kaggle revision/acquisition date, publisher timezone and listing terms; the exact local-copy exception does not fill these gaps.
3. **Validation and one authorized test result:** review [`T228`](T228.md), [`T229`](T229.md), [`T230`](T230.md), [`T251`](T251.md) and their aggregate reports against frozen model/prediction/threshold identities. Confirm denominators, partition and UTC period, confusion arithmetic, whole-partition P@K, uncapped daily alerts and uncalibrated score wording. Do not rerun T230 or use test results to tune.
4. **Application and limits:** inspect opt-in loader/risk contract evidence [`T233`](T233.md), [`T236`](T236.md), Stage E [`T242`](T242.md) and results route [`T240`](T240.md). Check that fixture mode works without artifacts, model errors remain controlled, no target labels enter runtime/UI and the risk score is not a final AML finding. Validation was reused for selection/diagnosis; the one test result is for this exact synthetic source/split, not deployment efficacy. The showcase prevalence exception prevents calling it an unbiased performance holdout.
5. **Independent reproduction:** a second contributor should run documented read-only hash/contract checks on their own verified local inputs and record exact environment, commands, observed hashes/results and any blockers. Source/label access must follow existing authorization; reproduction must not repeat the one-time T230 evaluation or access showcase labels under this task. A single contributor's existing setup or CI run is not second-person reproduction.

## Actual review record

| Item | Actual reviewer / date | Scope, commands, observed result |
|---|---|---|
| Human protocol/data-card/metrics/limits review | Pending | Pending |
| Second-person reproduction | Pending | Pending |
| Findings and disposition | Pending | Pending |

## Technical contribution — 2026-11-22

The [PR #4 Windows run](pr4-windows-review-2026-11-22.md) verified the transferred artifact hashes and frozen-score parity on exact commit `c0d59f2`. It exercised one local test-provider investigation and found a Windows SQLite activation failure in the offline publisher, a Windows SQLite test failure and an open manifest trust issue. The run did not repeat T230 or use record-level labels. An automated technical contribution supplies reproducible evidence for a future human reviewer. The entries above remain pending for an actual independent contributor's review, reproduction and disposition. T252 stays unchecked.

The follow-up fixed the SQLite failures and required an independent bridge manifest
digest in both runtime consumers. Windows checks again reproduced frozen-score
parity and the test-provider browser flow. [Fixes and execution evidence](pr4-windows-fixes-2026-11-22.md)
