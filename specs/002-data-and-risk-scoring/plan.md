# Implementation Plan: Data Ingestion and Risk Scoring

**Git branch:** initialization (the setup script's logical feature name is
002-data-and-risk-scoring; it did not switch branches)

**Date:** 2026-11-12

**Specification:** [spec.md](spec.md)
**Status:** Technical design drafted. Source-audit, affected-consumer review,
authoritative Phase 2 traceability, task generation, and implementation are pending.

## Summary

Feature 002 will import one declared local IBM AML HI-Small release, preserve
canonical transaction facts and provenance, replay strictly past-only features,
score with a real deterministic rules baseline and one selected explainable model,
evaluate both under a frozen chronological protocol, and publish a bounded
label-free case snapshot to the existing list/detail UI. The fixture journey
continues under its unchanged Foundation v1 contract.

The implementation has two execution paths. A local offline pipeline performs
source inspection, import, feature replay, model experimentation, evaluation,
and completed-run activation. The FastAPI application reads only a selected
completed run and serves an explicit v2 dataset contract; the existing fixture
path continues to use v1. This separates label-bearing evaluation work from
analyst requests and prevents request-time rescoring from mixing run versions.

The plan does not assert observed IBM field names, dataset statistics, model
performance, local dependency installation, or executed tests. The source audit
and local resource pilot below must fill those facts before the corresponding
code and experiments can proceed.

## Technical Context

| Topic | Planned choice and current evidence |
|---|---|
| Languages | Python 3.14.x backend/offline pipeline; TypeScript 7 and vanilla Vite frontend, matching current pyproject.toml and frontend/package.json. |
| Existing dependencies | FastAPI, Pydantic 2, Uvicorn, pytest, jsonschema, Ruff; Node 24, Vite, Vitest and TypeScript. Use existing lockfiles and locked installs. |
| New ML dependency | One locally verified, locked scikit-learn/NumPy/SciPy stack for the bounded candidates and AP/Brier metrics. No pandas, SHAP, AutoML or extra framework is required for the first run. Dependency version/install remains an implementation gate; research.md records current availability evidence. |
| Storage | One ignored local SQLite database plus ignored local model/evaluation artifacts. No production service or database migration framework. |
| Execution | Explicit local pipeline CLI for inspect, import, feature generation, protocol freeze, evaluate, score-run, activate-run and reproduce; read-only FastAPI for analyst browsing. |
| Target platform | Existing single-user Windows development environment; preserve offline fixture mode. Record any second teammate's actual environment separately. |
| Performance | Bounded default display of 100 alerts and existing case UI timeout behavior. No invented full-dataset runtime SLA; pilot 100,000 consecutive source rows, then freeze feasible memory/time budget before full processing or model search. |
| Scope | One initial IBM HI-Small release, one pooled synthetic benchmark view, one rules baseline, at most two simple model families, one selected model, existing list/detail screens. |
| Data status | No raw IBM source under data/ at planning time. The authoritative Phase 2 assignment requirements are also absent; the quality checklist is not a substitute. |

## Constitution Check

**Pre-research:** The requested feature fits the approved data/scoring stream
and Bootcamp modules 1–9. There is no proposed out-of-course technique.
The design honors the [constitution](../../.specify/memory/constitution.md).

| Principle | Design gate and status |
|---|---|
| I. Team-controlled scope | Pass in design: no GNN, transformer, open-web investigator, graph DB, cloud platform, new screen or automatic intervention. Any later extension needs recorded team decision. |
| II. Specify before implementation | Spec exists; this plan and supporting artifacts are being created. Reviewable tasks.md is still required before code changes. |
| III. Test-first business behavior | Every critical import, identity, temporal, scoring, metric and publication unit has an intended RED/negative/contract test in the verification section. No test is claimed run. |
| IV–VI. Purposeful AI, evidence, human authority | Arithmetic/validation/rules are deterministic; explanations cite actual features. No LLM facts, case disposition or account intervention. |
| VII. Independent evaluation | Private label role map; past-only replay; train-only fitting; validation-only selection/threshold; test labels joined only to frozen predictions. |
| VIII. Parallel contracts | V1 fixture contract stays strict; v2 data/scorer and snapshot contracts need producer/consumer review before dependent integration. |
| IX. Reproducible evidence | Source, mapping, feature, split, model, artifact, run, command, hardware and actual result manifests are planned. Human/peer checks remain pending. |
| X. Minimum complexity | One local database, offline pipeline, simple candidates and same UI journey. No unnecessary infrastructure. |

**Post-design check:** Research, data model, contracts and quickstart retain
these boundaries. No constitution violation is proposed. The open gates are
evidence/approval dependencies, not exceptions: source audit, affected
consumer contract review, task generation, and human review. Phase 2 rubric
compliance cannot be checked until its authoritative document is supplied.

## Project Structure

Documentation for this feature:

    specs/002-data-and-risk-scoring/
        spec.md
        plan.md
        research.md
        data-model.md
        quickstart.md
        contracts/
            api.md
            data-and-scoring.md
            schemas.json
        tasks.md                 # later speckit-tasks output; not created here

Proposed source layout, using the existing project structure and keeping
Foundation modules intact:

    backend/src/fraudlens/
        contracts.py             # existing v1 fixture models
        cases.py                 # existing v1 fixture service
        scoring.py               # existing v1 fixture scorer seam
        settings.py              # add explicit dataset/scorer settings
        main.py                  # select v1/v2 read service
        data_contracts.py        # canonical + v2 typed models
        data_import.py           # source inspection, mapping, row accounting
        data_store.py            # local SQLite import/run repository
        feature_history.py       # pure timestamp-group replay
        rule_scoring.py          # versioned baseline
        model_scoring.py         # frozen model adapter
        evaluation.py           # split, fit, selection, metrics
        explanations.py         # exact local reasons/contributions
        pipeline_cli.py         # local offline commands
    backend/tests/
        contracts/              # v1 regression and v2 schema parity
        unit/                   # importer, identity, time, rules, metrics
        integration/            # persistence, publication, API modes
    frontend/src/
        contracts.ts            # add strict v2 union decoder; retain v1
        api.ts                  # send snapshot reference for v2 detail
        main.ts                 # keep v1 order; preserve v2 event-time order
        views.ts                # conditional source/score/explanation copy
    frontend/tests/             # v1 regressions and v2 UI/API behavior
    data/
        fixtures/               # existing small Foundation fixture
        mappings/               # reviewed small source mapping, after audit
        raw/                    # ignored locally acquired source
        processed/              # ignored SQLite database
        artifacts/              # planned ignored model/run artifacts; add ignore rule first
    evals/results/              # reviewed small reports; large local results ignored

The path names are the proposed module split for tasks.md, not evidence that
these modules already exist. Keep business logic separate from HTTP handlers.

## Architecture and execution flow

1. **Inspect source.** A local command hashes the unmodified file, checks
   license/source metadata and observes its actual CSV dialect, headers,
   encoding, field types, timestamp range/granularity, amount/currency forms,
   label values and resource size. It writes a small reviewable data card.
   Ambiguous headers, unknown target-like columns, missing required fields
   or unresolved timezone stop import rather than invoking heuristics.
2. **Freeze source mapping.** A reviewed mapping names required/optional source
   fields, aliases, bank/account direction, label meaning, timestamp policy,
   decimal/zero/currency handling, supported scale and source namespace.
   It has a version/hash. New source or mapping creates a new import version.
3. **Stage import.** Parse CSV records in streaming batches; assign source-row
   ordinal before rejection. Parse operational facts and private label
   eligibility independently. Store exact source amount/time text plus
   normalized sortable values. Account for every row and reject bad records
   with reason. Structural/file parsing failure leaves the import incomplete
   and inactive. A repeat of the same source/mapping is idempotent.
4. **Build point-in-time features.** Process event-valid rows by interpreted
   timestamp groups, irrespective of file order. For group time t, derive
   current and historical features from [t−24h,t); only then append that
   group's observable facts. No labels enter the feature builder. Record
   full/partial coverage and feature version. The first 24h of source
   coverage is context-only warm-up under the initial policy.
5. **Score rules independently.** Apply the frozen three-rule table in
   research.md to scoreable events. Return bounded scores, actual triggered
   conditions and explicit unavailable feature conditions. Do not use fixture
   constants as the baseline.
6. **Freeze benchmark protocol.** Choose the observable scoreable view, whole
   timestamp 70/15/15 boundaries, exact membership, positive-count eligibility,
   train/validation/test role map, feature allowlist/lineage, candidate grids,
   AP tie tolerance, K=20, threshold policy, seed, resource budget and artifact
   versions. Freeze manifest before any fit or validation metric. If eligibility
   fails, mark the run ineligible and amend prospectively.
7. **Fit and select.** Fit every learned transform and candidate on permitted
   training rows. Validation labels select candidate by AP, then Precision@K,
   then the fixed simplicity preference; per-scorer thresholds use the
   validation-only F0.5 policy from research.md. Calibration and AutoML are
   deferred for the initial run. Keep category handling fixed for later rows.
8. **Evaluate once.** Freeze candidate, transformations, thresholds and
   predictions before joining test labels. Calculate AP, K metrics, threshold
   confusion/precision/recall, prevalence, alert rate, tie disclosure and
   probability-output Brier/reliability diagnostics on identical eligible
   test IDs for rules and model. Record uncertainty as unquantified with
   reason unless a suitable method was predeclared. Mark holdout consumed
   at first disclosure and later analyses exploratory.
9. **Stage and publish a run.** Create label-free assessments for the selected
   scorer and validate every identity, score, explanation, feature/artifact
   reference and threshold. Materialize one stable case per alert. Select
   the most recent 100 alerts, tie by stable transaction ID, then display
   ascending event time/ID. In one local transaction mark a complete run
   active. Failure leaves the prior complete active run intact. Case API
   reads only active complete state and never rescoring at request time.
10. **Serve and review.** The existing case list/detail journey renders a
   discriminated v1 fixture or v2 dataset response. Dataset list supplies
   a snapshot reference; detail requires it and rejects stale selection.
   Data source, scorer source, score meaning, feature coverage, run/version
   and explanation are truthful. Public payloads contain no target label.

## Interface and persistence decisions

- [Data model](data-model.md) defines entities, field validation, privacy
  boundaries, relationships and staging/completion state transitions.
- [Data/scoring contracts](contracts/data-and-scoring.md) define offline command,
  ScoreRequest, feature and run interfaces; [API contract](contracts/api.md)
  and [JSON Schema](contracts/schemas.json) define v2 public delivery.
- APP_MODE=fixture retains current behavior. APP_MODE=dataset requires an
  explicit APP_SCORER=rules or model and a matching complete active run.
  Absence/mismatch fails explicitly; no automatic fixture fallback.
- Foundation v1 GET paths and bodies remain valid in fixture mode.
  Dataset mode uses the same GET paths with a v2 discriminator. No public
  import/train/activation endpoint is introduced.
- SQLite schema versions are checked at open. The plan uses local creation
  and explicit recreation instructions instead of a migration framework.
  Staging status and a single active pointer ensure atomic visibility.
- Model loading verifies local path containment, manifest/source/feature
  compatibility and artifact hash before trusted deserialization. The app
  does not accept uploaded artifacts.
- The v2 public shape contains a dataset source separate from score source,
  directional money, event/as-of/scored times, run/feature versions, structured
  explanation and list count/truncation metadata. A snapshot reference pins
  list/detail; a stale selection is a controlled error.

## Test and evidence strategy

Critical business behavior follows RED → GREEN → REFACTOR. A RED test must
fail for the intended missing behavior. Mechanical setup and documentation
need no artificial failure. Every unit records commands, exit codes, source/
artifact versions and limits in evidence/tasks/. Fixture tests are contract
behavior checks, not model evaluation.

| Unit and IDs | Required negative/positive proof before marking complete |
|---|---|
| Import/provenance, FR-001–004, SC-001 | Duplicate/ambiguous headers, extra target-like field, missing field, empty/truncated/invalid-byte files, partial parse, high-precision/zero/invalid money, bank direction, equal-valued distinct rows, invalid label with valid facts, source/mapping change, interrupted retry and 100% row accounting. |
| Time/features, FR-005–006, SC-002 | Shuffled rows, tied timestamps, future append, label perturbation, held-out past facts, exact window cutoff, cold start versus incomplete coverage, same-currency aggregation and proxy/target feature rejection. |
| Rules/assessment, FR-007–009, SC-003 | Hand-calculated trigger/non-trigger and reasons, frozen weights, identifier invariance, nonfinite/out-of-range/mismatched score rejection, no fixture fallback. |
| Split/fit/selection, FR-010–015, SC-004–005 | Whole-tie chronology, exact manifest and eligible counts, insufficient positives, train-only fit instrumentation, unknown category, AP/P@K tie and model preference, scorer-specific threshold policy, no-alert outcome and consumed holdout. |
| Evaluation/explanation, FR-016–020, SC-004–006 | Hand-calculated AP, K/min denominator, Recall@K all positives, boundary tie, confusion/alert counts, equal test IDs, Brier status, additive explanation fidelity and wrong scale/run rejection. |
| Run/API/UI, FR-021–025, SC-007–008 | Mid-run failure leaves old snapshot, restart, active switch, stale token, stable case identity, zero alerts, latest-100 selection, v2 strict decode, no labels, truthful source banners, all v1 fixture and error/UI regressions. |
| Reproduction, FR-026, SC-009 | Full recorded commands and hashes, clean second-person import/score/evaluation, observed numeric tolerance and honest unrun/failed states. |

Before calling SC-004 complete, the actual locally acquired IBM release must
pass the frozen protocol and the substantive comparison must run. Small
source-shaped fixtures establish behavior only. No model metric or second-person
result can be inferred from this plan.

## Planned verification commands

The [quickstart](quickstart.md) distinguishes commands available now from
planned commands after implementation. At each task boundary, run targeted
pytest/Vitest checks; before a feature handoff run locked backend tests,
Ruff, frontend tests, typecheck/build and contract/schema checks. Record
actual outcomes, not expected ones. Run the source audit and evaluation
only with an authorized local file and private label access.

## Implementation sequence and handoffs

1. **Gate 0 — review and source evidence:** identify the Phase 2 assignment
   if available; audit the local source and license; complete mapping/time/
   amount/identity decisions and the resource pilot. Add a Git ignore rule
   for local model/run artifacts before producing them; verify raw and
   processed paths remain ignored. Record unresolved compliance separately
   if the assignment remains unavailable.
2. **Gate 1 — contracts before consumers:** affected producers/consumers
   review v2 canonical, scoring, API, error and snapshot contracts under
   docs/decisions/foundation.md. Record actual participants/date; do not
   claim review in advance. Create tasks.md with requirement/SC mapping.
3. **Slice A — import and local store:** build/verify inspection, row
   accounting, label isolation, identities, staged import and idempotency.
4. **Slice B — history and rules:** build/verify replay, feature catalog,
   coverage, concrete baseline and its explanations. This provides a
   working non-ML path for other contributors.
5. **Slice C — protocol and model:** freeze partitions/roles/search;
   verify train-only transforms, bounded candidate selection and holdout
   controls; run real evaluation only after source eligibility.
6. **Slice D — publication and UI:** build/verify immutable completed
   snapshots, v2 API/decoders and case list/detail; preserve fixture v1.
7. **Slice E — convergence and reproduction:** inspect FR/SC coverage,
   run actual regressions/scientific checks, record limitations and obtain
   independent teammate reproduction and human review.

The companion [Codex prompts](../../prompts/development/002-implementation-prompts.md)
are copy-ready instructions for task generation and these slices; they do
not mark any task or gate complete.

## Risks and explicit stop conditions

- **Source unavailable or unsuitable:** Import, observed mapping, substantive
  model evaluation and SC-004/009 remain pending. Do not substitute fixtures
  as IBM evidence or invent class counts.
- **Timezone/precision ambiguity:** Stop import until mapping is reviewed;
  no silent UTC/FX/rounding assumptions.
- **Eligibility after warm-up or split fails:** Record exact counts and
  prospective amendment before fitting; no favorable-window search after
  seeing test outcomes.
- **Dependency/resource failure:** Record local version/install/pilot result.
  Preserve agreed Python/runtime; narrow only the declared training view
  or search budget prospectively, or report incomplete delivery.
- **Contract incompatibility:** Preserve v1 fixture and closed validation;
  resolve v2 schema/producer/consumer mismatch before integration.
- **Artifact/run mismatch:** Fail closed. The previous completed snapshot
  remains active; never publish a partial or mixed run.
- **Human/Phase 2 evidence absent:** Do not claim team review, independent
  reproduction or course compliance.

## Complexity Tracking

No constitution exception is requested. SQLite, a bounded two-family
comparison, offline pipeline commands and a versioned v2 case contract
are the minimum design needed for the specified local capability.
