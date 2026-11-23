# Local contribution experiment addendum — 2026-11-23

The separately authorized branch experiment materializes 65 label-free native LightGBM sidecars under an ignored local path and records a distinct external SHA-256 pin. It reuses the frozen trusted loader/preprocessing/140 trees and leaves scoring, threshold, bridge and accepted v2 assessment unchanged. The full 32-column calculation remains local; only three grouped terms and their remainder enter the bounded sidecar. [Actual implementation and checks](../../evidence/tasks/002-003-local-contributions-implementation-2026-11-23.md) do not constitute Feature 003 contract approval. T257/T258 remain for accepted delivery.

# Implementation Plan: Dataset, Machine Learning and EDA

**Branch**: `feature/002-clean-start` (observed; unchanged)
**Date**: 2026-11-18
**Spec**: [spec.md](spec.md)

## Summary

Deliver the smallest useful data-to-prediction workflow over IBM synthetic HI-Small: verify and prepare source locally, derive strict-prior features, freeze temporal partitions/protocol, compare a small model set, expose an opt-in local scorer behind the foundation boundary, and then add bounded aggregate EDA. The implementation must not depend on data or model artifacts for fixture startup. Showcase replay remains gated/deferred.

## Technical Context

**Language/Version**: Python 3.14.x; TypeScript; Node.js 24.x as established by Feature 001.
**Primary Dependencies**: Existing FastAPI/Pydantic/pytest/Ruff and Vite/TypeScript/Vitest. Proposed data/model libraries require a compatibility spike against Python 3.14 and the existing lockfile before dependency resolution.
**Storage**: Raw source outside Git; proposed processed columnar Parquet snapshots plus JSON manifests; transient external-sort/window state only if benchmark proves necessary. No database is mandated.
**Testing**: pytest contract/unit/integration, Vitest UI/API decoders, typecheck/build; synthetic fixtures; separate provenance and authorized evaluation evidence.
**Target Platform**: Local Windows PowerShell workflow.
**Project Type**: Existing single-repository FastAPI + vanilla TypeScript application.
**Performance Goals**: Process approximately five million records within approved local memory/disk ceilings; final ceilings are an unresolved decision to freeze after a representative synthetic benchmark.
**Constraints**: No full data/model requirement for fixture mode; no cloud, database server, ML microservice, browser full-data processing, or tracked large artifacts.

## Architecture and Data Flow

```mermaid
flowchart LR
  A[IBM CSV] --> B[Byte checksum and schema validation]
  B --> C[Canonicalization and rejection manifest]
  C --> D[UTC ordering and strict-prior features]
  D --> E[Frozen chronological partitions]
  E --> F[Train-only preprocessing and bounded model fits]
  F --> G[Validation selection and threshold]
  G --> H[Frozen model plus metadata]
  H --> I[FastAPI Scorer adapter]
  I --> J[Versioned prediction API]
  J --> K[TypeScript UI]
  B --> L[Verified-source aggregate pipeline]
  C --> L
  L --> M[EDA aggregate API]
  M --> K
  E --> N[Restricted label audit]
  G --> O[Authorized frozen predictions]
  O --> P[Separately authorized test evaluation]
```

EDA branches from verified, authorized aggregate data. Scoring API has no target label. Evaluation labels and showcase records do not flow to the runtime scorer.

## Integration Points and Structure

Preserve current `backend/src/fraudlens/{scoring.py,contracts.py,main.py,settings.py,cases.py}` and frontend contract decoding. Proposed additions:

```text
backend/src/fraudlens/
  data/       # manifest, source mapping, bounded preparation, features, partitions
  training/   # frozen protocol, baselines, bounded search, evaluation gates
  scoring/    # artifact metadata/loader and Scorer adapter
  eda/        # aggregate computation and response models
backend/tests/{contracts,unit,integration}/
frontend/src/ # navigation/EDA view and typed API additions
frontend/tests/
data/{raw,processed,artifacts,eval}/  # ignored local outputs only
specs/002-data-and-risk-scoring/{contracts/,evidence plans in ../evidence/}
```

Exact module paths may follow existing import conventions, but no root contract copy or parallel API service is planned.

## Processing Approach

1. Download/acquire manually or through documented source method only after checking terms; implementation MUST NOT commit source data.
2. Hash raw bytes before parsing. Read identifiers and source fields as text. Validate header count and positional schema before accepting rows.
3. Emit canonical rows and a rejection ledger in deterministic chunks. Use a temporary, resumable staging directory; publish only a complete manifest-bound snapshot. Revalidate staged chunks on resume.
4. Normalize time under a frozen assumption and sort deterministically by instant plus stable row identity. The preferred proposal is a columnar snapshot followed by an external/bounded chronological pass. Benchmark a library-supported streaming/external-sort implementation; do not assume all five million rows fit in memory.
5. For each timestamp group, query/update 24-hour state in two phases: calculate every row from strictly earlier state, then apply the entire group. Expire values outside the declared `[t−24h,t)` interval. Keep sender paid currency and receiver received currency aggregates separate.
6. Establish source-count development/showcase boundary and scoreable dev split using timestamp/counts only. Freeze IDs and hashes before restricted aggregate label audit.
7. Freeze the protocol and resource configuration before any real-data model fit. Training and app runtime are separate commands and artifact lifecycles.

### Resource and recovery design

Hard memory and disk ceilings remain a blocking decision. Before real ingestion, benchmark synthetic datasets with representative cardinality/skew and freeze maximum RSS, free-space reserve, chunk size, maximum runtime, and checkpoint cadence. The runner must check available disk before staging and fail with a controlled message. Checkpoint IDs include source hash, code/schema version, config hash, row range, and output hash. Interrupted or partial outputs are never treated as published data. Exact approved ceilings are recorded in the frozen protocol.

## Model and Evaluation Architecture

- Feature contract is frozen independently of labels as the exact eleven `hi-small-temporal-v1` fields, including current paid amount (`log1p`), payment currency and payment format with a reserved unknown bucket.
- Implementation sequence updated by the user's T223 instruction: train-only preparation and the three declared baselines first, then eight declared LightGBM configurations and five declared `HistGradientBoosting` comparisons. The current selection phase still ranks LightGBM only. The exact grid and budget are in [T221 model choices](t221-model-choices.json); the approval and schedule impact are recorded in [T221 evidence](../../evidence/tasks/T221.md), with the sequence update in [T223 evidence](../../evidence/tasks/T223.md).
- For the current phase, rank only the eight LightGBM fits on validation positive-class F1 at the selected threshold, then AP, P@20 and the frozen LightGBM simplicity/order tie-break. LightGBM uses validation binary log loss for early stopping only; no internal random validation split is permitted. The other families remain planned comparisons, with cross-family final selection deferred to a later reviewed decision.
- The later cross-family ranking rule is frozen in [T224 selection choices](t224-cross-family-selection.json) before results; activating it requires a separate reviewed decision. T224 implements candidate fits as callable code, with fit execution deferred at the user's request.
- Preprocessing, encoders and logistic scaling are fitted only on training. Frozen training rows alone receive the declared class weighting; no downsampling changes their population.
- Threshold selected on validation by positive-class F1 with higher-precision, then higher-threshold ties. Test and showcase remain sealed.
- Store model, preprocessing, metadata, feature order/version, runtime/library versions, source/protocol hashes, training code revision, random seed, validation metrics, threshold method/value, and artifact checksum as one compatibility unit.
- T222 selected LightGBM native text plus a versioned JSON manifest for the first serving path, restricted to trusted local artifacts with pre-load hash/version/feature checks. The scikit-learn comparison-model serving format remains deferred. Pickle/joblib must never load untrusted artifacts.
- Frozen predictions precede separately authorized test evaluation. Reports clearly label synthetic source and only claim the split actually measured.

## API and Frontend

Add narrow, read-only, versioned contracts; preserve current `/api/health` and `/api/cases` behavior. Recommended endpoints: `GET /api/transactions/{transaction_id}/risk`, `GET /api/model/results`, and bounded `GET /api/eda/summary` (with optional precomputed chart-series resources if needed). Transaction identifiers are opaque strings derived from stable canonical IDs, not foundation fixture `TX-###` syntax. Responses contain no target label. Validate closed schemas in Pydantic and TypeScript; return controlled eligibility/unavailable/not-found errors. Do not expose arbitrary query filtering over test/showcase label-bearing data.

Show prediction score, threshold status, feature/model version, synthetic-data notice, and defensible explanation. Show results only for their authorized partition. EDA chart summaries are computed on backend and bound by maximum points/categories; count denominators, UTC timezone and currency units are explicit. EDA route/page implementation is conditional on an approval record.

## Testing and Verification Strategy

- RED → GREEN → REFACTOR for new business behavior; demonstrate RED is the intended missing behavior.
- Synthetic unit tests for parsing, duplicate headers, identity, decimal/currency checks, UTC equivalence, ties, exact 24h interval, warm-up, restart/hash, partitions and score validity.
- Contract/security-negative tests for labels, arbitrary test/showcase queries, invalid payloads, artifact mismatch, unsupported runtime and fixture fallback.
- Real-source provenance checks are separate from synthetic tests; no source/model quality claim without actual relevant run.
- Authorized model-development experiments and separately authorized holdout evaluation are distinct evidence records.
- Frontend contract/integration checks verify safe text rendering, no labels, units, empty/error/retry and bounded data.
- Human review/reproduction is recorded separately; one setup is not second-person reproduction.

## Constitution Check

**Pre-design**: PASS with gates. Work is within the approved AML educational concept and existing architecture. Human authority, label isolation, replaceable scorer, deterministic arithmetic, traceable contracts, local artifacts, and honest synthetic-data claims are preserved. No GNN, transformer, graph database, RAG, external provider, intervention, or service infrastructure is introduced.

**Post-design**: PASS subject to explicit blockers: (1) team approval for dedicated EDA page and its schedule impact; (2) approval before applying proposed +10% relative validation AP feature admission; (3) protocol decisions and resource ceilings before data/model execution; (4) separate explicit authorization before test labels are accessed. These gates do not authorize implementation by themselves.

## Open Decisions

| Decision | Options | Recommendation | Implementation impact | Required before |
|---|---|---|---|---|
| Timezone-naive timestamp | Source-declared zone; explicit project UTC assumption; reject pending clarification | Treat as UTC only if documentation leaves it unspecified, record assumption; otherwise stop | Changes canonical instants, warm-up, feature windows and every temporal boundary | Ingestion |
| Current-transaction features | Amount only; amount + currency + format; omit current fields | Amount `log1p` + payment currency + format; freeze before experiments | Changes feature schema, preprocessing and model artifact compatibility | Feature generation |
| Resource ceilings | Measured developer-machine limits; fixed team baseline | Benchmark and record RSS, disk reserve, runtime, chunk and checkpoint limits | Determines storage engine, chunk sizes, sort strategy and whether full source run is feasible | Full ingestion |
| Model candidate grid | Decision recorded 2026-11-20 | Eight LightGBM, five HistGradientBoosting and three baseline configurations in [T221 choices](t221-model-choices.json); current phase ranks LightGBM only | Up to 8 LightGBM fit-hours now; 15 fit-hours if all declared families are later run, plus preparation, evaluation and integration | Full FR-021 protocol approval before fitting |
| Threshold objective | Decision recorded 2026-11-20 | Validation positive-class F1, then precision and higher-threshold ties | Changes review status and alert volume in API/UI and evaluation | Full FR-021 protocol approval before fitting |
| Artifact format | Decision for first LightGBM path recorded in T222 | Native LightGBM text plus versioned JSON manifest, trusted local path and pre-load hash/version/feature checks; scikit-learn serving format deferred | No pickle/joblib loading or network retrieval; later T227 loader must enforce checks | Runtime integration |
| EDA page | Approve dedicated route; defer to existing screen | Approve only with written benefit and schedule impact; no approval asserted here | Adds a separately navigable UI destination, tests, chart/accessibility work and delivery time | EDA UI |
| Feature admission margin | Decision recorded 2026-11-20 | Exact frozen eleven features; no validation-driven admission experiment | Keeps feature schema fixed | Any feature experiment requires a new reviewed decision |
| Class strategy | Decision recorded 2026-11-20 | Train-only class weighting using training negative/positive ratio; constant baseline unweighted | Natural validation/test/showcase prevalence retained | Full FR-021 protocol approval before fitting |

## Complexity Tracking

### Frozen local contributions proposal — 2026-11-23

The isolated, non-serving prototype in `backend/src/fraudlens/scoring/local_contributions.py` reuses `ModelScorer` and its verified manifest/Booster. It verifies the manifest's 32-column order against the frozen preprocessor, evaluates native probability, raw margin and `pred_contrib` on one matrix with all 140 trees, and groups the 32 additive terms into the 11 source features. It does not modify scoring, threshold, artifacts or the published bridge. Numerical results, RED/GREEN and limitations: [execution record](../../evidence/tasks/002-local-contributions-2026-11-23.md). A distinct Feature 003 contract remains [proposed for owner review](../003-ai-investigation/contracts/local-lightgbm-contributions-proposal-v1.md).

No infrastructure expansion requested. A columnar format and bounded temporal state are justified by source volume; select the simplest option that meets measured resource constraints. Do not introduce SQLite, database services, or a charting package by default.
