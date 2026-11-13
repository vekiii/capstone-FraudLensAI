# Feature 002 shared-contract review preparation

## Collective final v2 contract approval — 2026-11-13

[The user's confirmation](../../prompts/development/002-t007-t008-final-team-approval-2026-11-13.md) reports that the entire team reviewed and approved the final T008 v2 contracts, including the strict 64-lowercase-hex `DatasetVersionId`, with no blocking objections. This collective report is the review source and decision; no individual names, roles, or signatures were supplied or inferred. Reviewed state: uncommitted working diff on `002-data-and-risk-scoring` against HEAD `182d0b290c8819e602fc5d77e8df8e904228b032`; mapping M `a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57`, API SHA-256 `fbf7be0df60a9d7bf7e881d44d8727d5eadc64e758af7944150149700f17b13e`, offline contract SHA-256 `534de0c70a6ecbec69dd8734d6fec5830a9814da81fa508afe16a0f1dcca9918`, schema SHA-256 `bf487d84ccac1e315d0e20fece0d2a7f45990bce954ba40bf97cd54e43929f88`, and data-model SHA-256 `e8235e358c6d01fc13e3f5f9a8ad0600d2d98c44d4afda4aa75809aa3efa0987`. Read-only comparison with the preceding final-byte evidence found 5/5 matching values and no later edit. [Full approval and hash check](feature-002-t007-t008-team-review-2026-11-13.md#collective-final-byte-approval-conveyed-by-the-user).

T008 review gate is complete; Foundation v1 and the separate v2 field set remain as in the reviewed compatibility matrix below. Remaining consumer migrations are later implementation, **not unresolved review objections**: backend active-run/snapshot/dataset linkage, frontend strict v1/v2 decoding and list/detail equality, investigation and priority/simulation versioned operational adapters, and corresponding negative/v1 regression checks. Private labels remain outside those interfaces. The already documented 20 RED tests are only partial T009–T011 coverage. Earlier pending/proposal sections below are historical.

## Current Codex correction check — 2026-11-13

The [current working-diff verification](feature-002-t007-t008-team-review-2026-11-13.md#codex-correction-and-preparatory-red-verification--2026-11-13) tightens `DatasetVersionId` to `dv_` plus exactly 64 lowercase hex digits with an absolute end, aligns all three v2 API examples and tests, and leaves Foundation v1/v2 fields intact. Current API SHA-256 `fbf7be0df60a9d7bf7e881d44d8727d5eadc64e758af7944150149700f17b13e`, offline contract `534de0c70a6ecbec69dd8734d6fec5830a9814da81fa508afe16a0f1dcca9918`, schema `bf487d84ccac1e315d0e20fece0d2a7f45990bce954ba40bf97cd54e43929f88`; M is `a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57`. Targeted tests 34/34, existing backend 380/380, frontend 151/151 and Ruff passed (exit 0); exact commands are in the linked record. The previous hashes below are historical. The team's joint technical direction is unchanged; real final-byte producing/affected-consumer review, findings and remaining migrations are still pending. No individual approval is inferred. T008 remains open.

## Joint T008 technical decision — 2026-11-13

The user [relayed the team's joint technical decision](../../prompts/development/002-t007-t008-team-decision-and-red-request-2026-11-13.md) for the existing separate v2 design. It adopts the exact identity/hash recipe and external mapping review record, retains Foundation v1 behavior and the current v2 list/detail wire format, and sets component obligations without assigning people or claiming individual findings. The [separate T007/T008 record](feature-002-t007-t008-team-review-2026-11-13.md) contains rationale, reference commit `182d0b290c8819e602fc5d77e8df8e904228b032`, working diff, compatibility matrix, vectors and calculated SHA-256 values. Current working-file hashes pending final owner review: mapping M `e82903264382ae710b8b93ce43a3e37d954ec6a6629414e217b698664e6769d6`; API `8836ec9cf15f610d840384ca78247e549ed55ddafbaa971bcbdd008b27e3a1ed`; offline contract `534de0c70a6ecbec69dd8734d6fec5830a9814da81fa508afe16a0f1dcca9918`; JSON Schema `9e93f40da78381d280da52a2a6ea421837e14c7d46420ccc85a41f1b404c0fc7`.

Backend must later validate detail against the active complete run, snapshot and dataset version; frontend must strictly decode v1/v2 and check list/detail consistency. Investigation and priority/simulation must consume versioned operational data while preserving provenance, explanations and order. Private labels/eligibility remain outside those inputs and the API. The importer must use exact mapping currency names. These are reviewed **contract obligations**, not claims of completed v2 integration or individual stream approval. JSON Schema can check local shapes, required fields, patterns, bounds and closed objects; backend/frontend must check active-run state and cross-object/cross-response equality. Later integration must migrate backend typed models and service, frontend decoder/client/UI, and affected consumer adapters with negative and v1 regression tests. The user supplied no individual names, signatures, component-specific findings or second-person results, so none are attributed here. Earlier pending register and preliminary hashes below remain historical.

**Current technical state, 2026-11-13:** user-approved amendments are applied to
the Feature 002 API/offline/schema documents; [resolution](feature-002-technical-resolution.md)
and [current exact hash manifest](feature-002-technical-resolution.json) supersede
the old proposal/base hashes below for future team review. Currency length 17,
required detail-envelope dataset_version, strict endings, source-bound Account
positions and the explicit assumed-clock basis are technically resolved.
Mapping/configuration and T008 remain pending actual producer/affected-consumer
team review. No typed v2 API/decoder integration or human approval is claimed.
The remaining sections preserve the earlier review history and pending register.

T006–T008 continuation: [investigation and evidence correction](feature-002-source-investigation.md)
and [concrete review packet](../../specs/002-data-and-risk-scoring/proposals/README.md).
The proposal chooses currency maxLength 17 and a required detail-envelope dataset_version,
adds demonstrated strict-end pattern corrections, and separates an optional assumed-clock
enum amendment. All are unapproved proposals; current authoritative contracts remain unchanged.

2026-11-13 Europe/Belgrade. T008 **pending_consumer_review**, dependent T007 **pending_mapping_review**. This is agent document/code inspection and a proposal record, not completed owner review or approval. [Prompt/revision/environment](feature-002-implementation.md), [actual source audit](feature-002-source-audit.md). FR-003, FR-023, FR-026; no SC-008 acceptance claim.

Procedure: [Foundation shared-contract change review](../../docs/decisions/foundation.md#shared-contract-change-review), steps 1–4. This record performs proposal/impact documentation and independent regression checks. Producing and affected consuming owners have not supplied reviewer/date/decision; dependent integration remains gated. No authoritative schema, decoder, API or application behavior changed in this slice.

## Rationale and compatibility matrix

Observed IBM-shaped source facts cannot be represented faithfully by Foundation fixture v1. Keep v1 strict; proposal is separate dataset v2 and coordinated discriminated decoding. Successful inspection does not mean the source mapping or v2 design has been approved.

| Boundary | Foundation v1 implementation/contract | Proposed v2 / migration requirement |
|---|---|---|
| IDs | Backend `contracts.py`: full-match TX-000 / CASE-000 form; Foundation schema and frontend decoder also fixed 3 digits. | D/C plus 32 lowercase hex digits, reviewed namespace/member/ordinal identity; separate v2 validators and URL/detail dispatch. No widened v1 IDs. |
| Parties | One sender/receiver account string, 1–120 characters. | Separate bank/account objects; qualify joins without losing either side. Duplicate local `Account` names require mapping decision first. |
| Money | One amount, exact two decimals; currency exactly 3 uppercase letters; matching strict frontend decoder. | Separate paid/received Decimal strings and source currency names; actual source has 6-place values and 17-character currency names. **Draft v2 maxLength 12 blocks observed values.** |
| Time | UTC-Z string; fixture `scored_at` deliberately repeats event time. | Preserve raw timestamp, reviewed interpreted UTC, feature exclusive cutoff, actual execution time. Actual source is minute text with no timezone, so import remains blocked. |
| Scoring | `Scorer.score(Transaction)` plus FixtureScorer; service revalidates identity/mutation/finite scores. Existing test-only rules replacement is not the baseline. | Separate label-free ScoreRequestV2 and run/feature/artifact validation; explanations and score_kind. No v1 seam changes here. |
| List ordering | `cases.load_cases` sorts case_id; frontend main.ts sorts again by case_id. | Select latest 100 by descending event time/ascending transaction ID, display ascending time/ID, preserve server v2 order and count/truncation metadata. Keep v1 sorting. |
| Detail/snapshot | v1 list has only items, detail has no snapshot query; identity checked. | List snapshot_ref, detail pins active completed run; 409 stale_snapshot, 503 run_unavailable. No mixed versions. Client signature/strict error handling must migrate together. |
| Decoding | Frontend contracts.ts closedObject requires exact keys at every level; rejects new fields, unknown error codes, mismatched IDs. | Per-response discriminator dispatch; strict v2 union decoder, semantic/schema parity corpus, no fallback or reliance on prior health. Dataset payload cannot enter current v1 decoder. |
| Banner | `views.ts` unconditionally appends “Demonstracioni podaci — sintetički skor, bez ML predikcije” before rendering the journey. | Keep fixture notice in v1; distinguish IBM synthetic data from authored fixture and actual rules/model source in v2. A model run cannot retain “no ML prediction” copy. |
| Labels | Existing schema/models/decoder are closed and label-free. | Maintain label exclusion through canonical projection, requests, explanations, API, UI and investigation/priority inputs. Aggregate source-label counts are private audit evidence only. |

Exact source evidence: `[2,4]` duplicate header indices; timestamp no zone in every record; observed 2/6 money scales; `Australian Dollar` (17) and `Canadian Dollar` (15). No proposed limit derived from a paper/sample.

## Unresolved decisions and concrete proposal

1. **Currency bound:** Draft schema Money.currency maxLength 12 contradicts preserving the local source names. Propose a reviewed source-supported bound of at least 17 with exact source text, or an explicit reversible mapping with separately retained source currency. No truncation, assumed ISO conversion, or schema edit performed. Must align data mapping, JSON Schema, backend typed models, frontend decoder, examples and negative tests before integration.
2. **Duplicate headers:** Draft offline contract blocks duplicates after normalization. Actual source contains duplicate `Account`. Proposed occurrence/index mapping must be bound to the exact ordered header and source hash and approved as an explicit contract decision; no bypass implemented. IBM's reference formatter now supports sender position 2 / receiver position 4; namespace and approval of the exception remain pending.
3. **Detail version wording:** api.md says assessment.dataset_version matches “the transaction and list”, but public TransactionV2 has no dataset_version (schema and example agree on its absence). Proposed clarification: compare assessment.dataset_version to the pinned list/run repository context, or explicitly review a version field on the detail envelope. Choose one before parity tests/runtime implementation; do not pretend that a missing transaction property exists.
4. **Source/time policy:** No exact acquired release or timezone evidence. No source namespace, mapping hash or UTC policy can be frozen. Upstream license statement verified; applicability to exact local release still pending.
5. **Semantic parity:** Schema alone cannot express all cross-object identity/count/run/score-kind/explanation-scale/additivity invariants. Plan coordinated backend/frontend semantic tests, 409/503 client behavior and persistent v1 regressions under T049–T058. Explanation base/remainder nullability is a shape allowance, not permission to claim an unchecked reconstruction.

## Exact reviewed input hashes (SHA-256)

“Reviewed” here means agent inspection inputs, **not owner signoff**. No contract hashes are approved/frozen. Paths relative to repository root; checked using `Get-FileHash ... -Algorithm SHA256` (exit 0).

```text
019ccaa1ef6e3f136ea34e918b67d20892928a2954ab589371e66f020feb474d  specs/002-data-and-risk-scoring/contracts/api.md
d77ee191d8c448795c4c60895a6a71b97298d777fe6449c750feb8d7fb51fdd6  specs/002-data-and-risk-scoring/contracts/data-and-scoring.md
de826ba607d9b0852c75d985b1fae11eef20b7d623a209c79edc5b8c661a7154  specs/002-data-and-risk-scoring/contracts/schemas.json
91ad48978f5a16e28532dc38027457376e3237b2a67e528c70a667489084b6c3  specs/001-project-foundation/contracts/api.md
4578ec30ed2e8a9c8d6624b52deb1e059b78771cbd93bbf4950c4ccfa6a21034  specs/001-project-foundation/contracts/schemas.json
fe14f9e32021d3874c36bfe3761498ad36b67e7e9ff7f3ff50bb905bd0f07ceb  backend/src/fraudlens/contracts.py
9974996e29ceabe152f99e2c9b5b0259b719cf501d9b1e6e0e6a590344eb980d  frontend/src/contracts.ts
f96cee5d5d23d7c9ad6beea50a4e44490222de4b3e610287c6a9db29f9b47f05  backend/src/fraudlens/cases.py
20b922d3fdecb34272469c0456c3db90e71c6e4ea89b6e2073c6a1a53fd14096  frontend/src/main.ts
88806c30d6b049cfe0c1f75107244e5417cbb06644deadbe3230c845af585d78  frontend/src/views.ts
```

## Producer and affected-consumer review register

Responsibility streams are from the Foundation procedure; they do not assign named humans.

| Required owner/consumer | Review required | Actual reviewer/date/decision |
|---|---|---|
| Data/scoring producing owner (A) | Source provenance, mapping/time/money/identity, canonical/ScoreRequest/assessment schema, label isolation. | Approved by collective team decision conveyed by user, 2026-11-13 |
| Frontend/API consuming owner | v1/v2 decoder and endpoint compatibility, currency bound, event ordering, snapshot/error behavior, truthful banner. | Approved by collective team decision conveyed by user, 2026-11-13 |
| Investigation consumer (C) | Label-free directional facts, source/run/time/coverage/explanation identity; future investigation inputs. | Approved by collective team decision conveyed by user, 2026-11-13 |
| Priority/simulation consumer (D) | Score meaning/threshold/run compatibility, stable identities, observable ordering and snapshot counts; no label inputs. | Approved by collective team decision conveyed by user, 2026-11-13 |

No owner contact/messages were sent. At the time this original review was written, approvals were pending; the later collective team approval is recorded in the dated update below. Foundation's earlier accepted review did not approve Feature 002.

## Checks and integration state

Read Foundation v1 API/schema, backend models/service/scorer/settings/routes, frontend strict decoders/client/main/views and existing unit/contract/integration/UI tests. Static `Draft202012Validator.check_schema` passed on unchanged v2 (exit 0). **Correction:** the earlier standalone probes retained the root response union, so their reported ID-newline rejections were invalid. Correctly isolated continuation probes accept valid ordinary IDs/decimals, reject Australian Dollar/Canadian Dollar specifically for currency maxLength, and demonstrate final-newline ID/money acceptance. The exact candidate fixes and passing review probes are in the [investigation](feature-002-source-investigation.md). Historical application regressions remain in the [ledger](feature-002-implementation.md); they were not rerun for this documentation continuation.

No v2 implementation, contract amendment, mapping freeze or dependent breaking integration performed. T008 stays unchecked and `pending_consumer_review`; T007 must be resolved first. Human review and independent reproduction pending. One next step: supply release provenance and obtain actual producer/affected-consumer decisions for the four blockers above before import/integration.


## Historical remote collective-approval publication — 2026-11-13

This section came from the three remote documentation commits ending at `6952f1d` and records the earlier collective approval convention. Its referenced intermediate mapping digest `27445724…439699` and technical-resolution contract hashes are historical review inputs. The later [final-byte approval](#collective-final-v2-contract-approval--2026-11-13) pins the current v2 files and M `a816260a…093e57`; the T015 import boundary uses that exact current mapping hash. Remote authorship remains in branch history.

The user confirms the team works jointly on project code and documentation and that one member?s approval represents the team. The user explicitly approved T007 and T008; this is recorded as collective project-team approval conveyed by the user. Individual owner names are not asserted.

- T007 mapping review: approved collectively on 2026-11-13; approved mapping SHA-256: `27445724712e9bca6f0d22ac991a2f923a18d5df33fc79a41c852244cd439699`.
- T008 producer/consumer contract review: approved collectively on 2026-11-13; the reviewed Feature 002 contract hashes remain the ones in the technical-resolution manifest. The v1 compatibility boundary is preserved.
- This collective approval closes the T007/T008 review gates. Import remains disabled pending implementation of an import command; no runtime importer or v2 application integration is claimed.
