# Feature 002 shared-contract review preparation

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
| Data/scoring producing owner (A) | Source provenance, mapping/time/money/identity, canonical/ScoreRequest/assessment schema, label isolation. | Pending / not supplied / no approval |
| Frontend/API consuming owner | v1/v2 decoder and endpoint compatibility, currency bound, event ordering, snapshot/error behavior, truthful banner. | Pending / not supplied / no approval |
| Investigation consumer (C) | Label-free directional facts, source/run/time/coverage/explanation identity; future investigation inputs. | Pending / not supplied / no approval |
| Priority/simulation consumer (D) | Score meaning/threshold/run compatibility, stable identities, observable ordering and snapshot counts; no label inputs. | Pending / not supplied / no approval |

No owner contact/messages sent. The user's provenance clarification is evidence of acquisition, not mapping/contract approval. Foundation's earlier accepted review does not approve Feature 002.

## Checks and integration state

Read Foundation v1 API/schema, backend models/service/scorer/settings/routes, frontend strict decoders/client/main/views and existing unit/contract/integration/UI tests. Static `Draft202012Validator.check_schema` passed on unchanged v2 (exit 0). **Correction:** the earlier standalone probes retained the root response union, so their reported ID-newline rejections were invalid. Correctly isolated continuation probes accept valid ordinary IDs/decimals, reject Australian Dollar/Canadian Dollar specifically for currency maxLength, and demonstrate final-newline ID/money acceptance. The exact candidate fixes and passing review probes are in the [investigation](feature-002-source-investigation.md). Historical application regressions remain in the [ledger](feature-002-implementation.md); they were not rerun for this documentation continuation.

No v2 implementation, contract amendment, mapping freeze or dependent breaking integration performed. T008 stays unchecked and `pending_consumer_review`; T007 must be resolved first. Human review and independent reproduction pending. One next step: supply release provenance and obtain actual producer/affected-consumer decisions for the four blockers above before import/integration.
