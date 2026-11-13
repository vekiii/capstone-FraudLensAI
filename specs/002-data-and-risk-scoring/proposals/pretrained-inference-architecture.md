# Proposed pretrained inference architecture for Feature 002

**Status:** Design proposal, 2026-11-13. Team scope decision pending. This is not an approved change to the [specification](../spec.md), [plan](../plan.md), [research](../research.md), [tasks](../tasks.md), or benchmark protocol. No model was downloaded, loaded, invoked, fitted, or evaluated for this design.

## Decision boundary

The [artifact investigation](../../../evidence/tasks/feature-002-pretrained-model.md) found no pretrained model compatible with IBM HI-Small `history-v1`. ApexFi's pinned native LightGBM booster is a **conditional candidate for an isolated IEEE-CIS demonstration only**. Its `isFraud` target, 446 ordered inputs, fitted encodings, and graph-derived inputs do not match IBM `Is Laundering` or the FraudLens v2 score request. An IBM transaction cannot be sent through this adapter by renaming fields, substituting zeros, or converting bank accounts into cards. The team must choose the separate demonstration, find a genuinely IBM-compatible artifact under a new review, or retain the approved local-fitting path. No choice has yet been recorded.

The isolated demonstration would have its own offline command, input/result contract, artifact directory, and evidence. It would not produce IBM-backed `RiskAssessment` records, appear in v2 case delivery, or satisfy the IBM benchmark and model-delivery acceptance criteria. Existing Foundation v1 fixture startup/scoring and Phase 4 `rules-v1` scoring continue without a model package, artifact, network connection, or configuration change. Selecting the demonstration explicitly with a missing or incompatible artifact returns `unavailable` or `incompatible` with reasons and no score; it never falls back to rules while claiming `source=model`.

## Proposed local boundary

1. A separately selected offline IEEE-CIS command receives authentic, source-versioned IEEE transaction/identity examples and a local manifest path. Normal application startup never resolves that path. No download or network access occurs at inference time.
2. A preflight layer validates the local-root-contained artifact path, regular-file type, byte size, SHA-256, pinned revision, manifest version, expected native LightGBM format, runtime versions, and reviewed provenance **before** a native parser receives the file. It rejects unknown manifest fields and untrusted paths. The current `preprocessing_artifacts.pkl`, GNN weights, and stacker must not be deserialized or executed. Safe, reviewed, versioned primitive preprocessing data must first be specified and independently checked against the source; if that cannot be done, the candidate remains unavailable.
3. A source-specific feature builder verifies exact source names, row identity, source revision, dtypes, category domains, missingness, lookup coverage, transformation versions, and the full 446-position order before invoking the booster. The manifest binds both the semantic input-name order and the actual native `Column_0` through `Column_445` order. Authentically missing source values may follow only a documented, verified transformation; an absent mandatory field, unavailable card/device lookup, unsupported category, or unknown encoding fails closed. No value is fabricated to force a prediction.
4. The adapter accepts a label-free, immutable request and returns either a typed failure with reason codes or a prediction bound to the same source transaction ID and request digest. It rechecks ID, manifest and feature digests, finite output, declared output range, and unchanged request. Successful results identify `source=model`, `model_version`, manifest hash, source dataset/revision, feature schema hash, and output semantics. The raw booster response is retained as a raw model score. `uncalibrated_probability_estimate` is permissible only if the pinned native binary-objective response and its [0,1] transform are verified; it is never called a calibrated fraud probability without applicable calibration evidence. A raw margin cannot be silently labeled a probability. No decision threshold is inferred from the model score or IEEE leaderboard.
5. Labels, evaluation assignments, and holdout answers live in a separate offline store and are never part of the feature request, preprocessing lookup, artifact manifest, operational logs, or model input. Any future IEEE evaluation requires an approved source-specific protocol and known training-data exposure; it cannot reuse the IBM split manifest to claim independence. Explanations, if required, must be faithful to this actual booster/output scale or explicitly unavailable under an approved revised contract.

The current FraudLens `ScoreRequestV2` remains the IBM `history-v1` boundary. Its dataset-version, snapshot identity, cutoff, scoreable coverage, transaction-to-prediction identity, and label isolation rules are useful design constraints, but an IEEE example cannot be represented as a valid IBM request. A future IBM-compatible pretrained artifact would require a separate approved mapping and tests against that exact v2 contract.

## Proposed versioned artifact manifest

The manifest is a **proposed schema**, not an approved or populated artifact. An implementation would freeze a reviewed JSON instance and its canonical SHA-256 before inference, with at least:

| Field group | Required contents |
| --- | --- |
| Identity and provenance | `manifest_schema_version`, source URL, immutable source revision, artifact relative path, artifact byte size and SHA-256, model type/native format, stated license and reviewed reuse decision, target `IEEE-CIS isFraud`, known/unknown training population and exposure. |
| Feature contract | Source schema/version; all 446 ordered semantic names and order hash; native slot order/hash; dtype, units, categorical domain, missingness and required-field policy; derived frequency/graph lookup identities and coverage rules. |
| Preprocessing | Reviewed safe primitive mapping path/hash and exact transform version/order; learned-map origin and unknown-category behavior; explicit rejection if parity with the original fitted preprocessor cannot be established. No pickle path is an executable dependency. |
| Runtime and output | Supported OS/Python/LightGBM/NumPy versions; local resource limits; raw margin or binary response semantics, expected output domain, calibration status `none`, and absent threshold unless separately approved. |
| Audit | Manifest canonical hash, verification date/evidence, authorized input source, exact failure reason vocabulary, and test-vector provenance without private labels. |

The manifest must not claim train-only preprocessing: ApexFi's original categorical maps were reportedly fitted using the full IEEE dataset. That conflicts with the current Feature 002 protocol and needs an explicit scope/evaluation decision. The native LightGBM file alone does not solve preprocessing parity, licensing, dataset access, or training-exposure questions.

## Affected approved work and proposed replacement sequence

The [existing deviation record](pretrained-model-integration.md) maps T026–T036. T026–T028 remain completed historical work; T029–T036 remain open as written. In particular, T029's uncommitted draft is not a frozen or approved inference protocol. T030–T032 require bounded local fitting and validation-based candidate/threshold selection, which an unchanged pretrained model cannot fulfill. T033–T036 require a frozen holdout/reporting pipeline that cannot be claimed from an isolated demonstration. T037–T042 assume a locally trained, trusted artifact and matching frozen predictions; T062, T064–T066 and SC-003–005 require substantive IBM evaluation and review. No checkbox, benchmark claim, or holdout state changes through this proposal.

If the team approves an IEEE-only demonstration, propose these **new task IDs after specification review**; these are not current checklist items:

| Proposed sequence | Acceptance gate |
| --- | --- |
| PML-001 — Scope and rights decision | Record actual team approvers/date, chosen IEEE-only scope and schedule impact; resolve model/code/data licenses, training provenance/exposure, authentic example access, and safe preprocessing feasibility. Amend specification, plan, research, tasks, and contracts coherently before code. If any mandatory input cannot be produced authentically, stop. |
| PML-002 — Freeze manifest and example contract | Pin artifact and preprocessing hashes, all 446 ordered inputs, output semantics, runtime/resource limits, source-specific label separation, and prospective verification/evaluation procedure. Review canonical manifest and an authentic label-free example. |
| PML-003 — RED adapter and isolation tests | Test optional startup, trust preflight, schema/order/type/missingness/coverage, IDs, label exclusion, no fallback, score semantics, and failure reasons with controlled examples; fail for intended absent behavior. |
| PML-004 — GREEN offline adapter | Implement local-only verified native inference and reviewed safe preprocessing under fixed parameters. Keep Foundation fixture and Phase 4 rules regressions green. No API/UI or IBM v2 routing. |
| PML-005 — Limited IEEE demonstration evidence | Verify authentic example parity and provenance, exact output behavior, resources, security, and independent review. Any performance or calibration claim requires a separately approved, contamination-aware evaluation protocol. |

If the team instead chooses IBM-backed inference, PML-001 must identify a model whose target, complete features, preprocessing, and provenance are genuinely IBM-compatible; the IEEE candidate cannot satisfy that path. An approved scope exception or replacement task set must explicitly state what happens to the original T029–T036 and later IBM acceptance criteria. The existing benchmark protocol must not be rewritten to create retrospective compliance.

**Exact implementation gate:** recorded team approval of the material scope change **and** verified lawful source/data reuse, authentic complete IEEE inputs, a safe non-executable equivalent of mandatory fitted preprocessing, pinned artifact/manifest, and approved revised contracts/tasks. Until then, there is no permitted model integration implementation.

**Next task:** PML-001 decision and prerequisites review; record the actual team decision and resolve licensing/provenance, preprocessing parity, and authentic IEEE example coverage.
