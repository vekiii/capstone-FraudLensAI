# Foundation decisions and contribution handoff

Initial setup: 2026-11-11, T003 (FR-001). Handoff updated: 2026-11-12,
T022 (FR-007/011). Architecture authority:
[plan](../../specs/001-project-foundation/plan.md),
[research](../../specs/001-project-foundation/research.md),
[approved product/workstream context](../../original_idea.md).
Current progress and limitations are in [next_work.md](../../next_work.md).

## Python environment
Use Python 3.14.x (`.python-version`, constrained to >=3.14,<3.15 in pyproject.toml).
Initial project runtime: CPython 3.14.3, Windows x86_64; uv 0.10.9.
Phase 5 uses CPython 3.14.7 in the repository-local `.venv`, with the same uv
version and lockfile. Patch releases may differ within the declared 3.14.x range;
record the interpreter actually used rather than relying on the machine's default.
`uv lock` generated uv.lock; subsequent installs use `uv sync --locked --group dev`.
The dev dependency group contains pytest, httpx, Ruff and jsonschema with format
extras for later JSON Schema date-time checks. Production dependencies are FastAPI,
Pydantic 2 and Uvicorn. At T003, server/routes/contracts did not yet exist; T019
delivered the fixture API/UI. The documented dev-group install is required for
this foundation, including jsonschema used by runtime contract validation.
Production-only dependency installation/packaging has not been validated.
No build backend is configured for this non-distributed local application.

Resolved direct dependencies, unchanged in phase 5 (transitive resolution: uv.lock):

| Dependency | Version | Group |
|---|---|---|
| fastapi | 0.162.4 | runtime |
| pydantic | 2.14.3 | runtime |
| uvicorn | 0.54.0 | runtime |
| pytest | 9.2.0 | dev |
| httpx | 0.28.1 | dev |
| ruff | 0.17.4 | dev |
| jsonschema | 4.26.0 | dev |

pytest reads pyproject.toml and adds backend/src to its import path. Ruff targets
Python 3.14 with import sorting and basic error/undefined-name rules. Backend
modules now live in `backend/src/fraudlens/`; tests are under `backend/tests/`.

In this restricted workspace the default uv cache is inaccessible. Session-only
workaround used here (the cache is ignored):

```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.cache/uv'
uv sync --locked --group dev
```

Initial sandbox network access to PyPI failed (socket access denied); authorized
execution outside the sandbox generated the lock and installed dependencies.
Locked sync, dependency imports, pytest config/import path and Ruff were checked.
pytest collection reported zero tests (exit 5), which is expected before T006 and
is not a passing behavior suite. See [handoff](../../evidence/tasks/phase-01-handoff.md)
for commands, results, runtime caveats and pending human review.

## Foundation boundaries and replacement points

The authoritative v1 wire contract is
[`specs/001-project-foundation/contracts/`](../../specs/001-project-foundation/contracts/api.md).
Do not introduce a competing root contract copy. Current replaceable boundaries:

| Boundary | Current implementation and injection | Consumer obligation |
|---|---|---|
| Transaction and assessment | Pydantic models in `backend/src/fraudlens/contracts.py`; JSON Schema in the feature; runtime decoders in `frontend/src/contracts.ts` | Closed objects, finite score in [0,1], explicit source/version/time, matching transaction identity; no labels in delivery |
| Scoring | Structural `Scorer.score(Transaction) -> RiskAssessment` in `scoring.py`; `FixtureScorer` is the default | Supply an adapter to `CaseService(fixture_path, scorer)` or `create_app(settings=..., scorer=...)`; do not modify service/routes to select a particular model |
| Case delivery | `cases.py`: `load_cases`, `score_case`, `CaseService`; `main.py` translates errors to HTTP | Preserve case/transaction identity, ordering and generic failures; validate upstream results and reject input mutation, never silently clamp or substitute a score |
| Fixture repository | `Settings.fixture_path` supplies a local JSON path; loaded lazily | Keep shipped data synthetic, small and label-free; tests may inject a temporary file without write/debug API routes |
| Frontend API and UI | `api.ts` decodes unknown responses; `mountCaseApp(root, client)` accepts a client | Maintain cancellation/stale-response behavior, explicit errors/retry and visible source labeling |

The test-only rules adapter in
[`test_scoring_boundary.py`](../../backend/tests/unit/test_scoring_boundary.py)
proves scorer replacement through list/detail delivery. It is not a production
rules implementation. [T020/T021 evidence](../../evidence/tasks/T020.md) records
19 initially passing checks and unchanged production scoring/delivery code.
An injected rules scorer does not add a supported `APP_MODE=rules` setting;
fixture remains the only application startup mode in this foundation.

## Ownership: foundation versus subsequent product work

Letters identify responsibility streams, not assigned individuals. No teammate
names or completed human reviews are inferred. The temporary foundation split in
the [tasks](../../specs/001-project-foundation/tasks.md) is:

| Foundation stream | Responsibility |
|---|---|
| A | Backend, API and shared contract implementation/review |
| B | Synthetic data, fixture loading and validation |
| C | Frontend API boundary, case journey and UI checks |
| D | Tooling, actual execution evidence and handoff |

After foundation, use the four product workstreams approved in original_idea.md
section 12. Each stream owns its tests/evaluation and relevant frontend/backend
work; integration and the entire frontend must not fall to one person.
The rotation A → B → C → D → A is a proposed review allocation, not a claim
that anyone has reviewed the current changes.

| Product owner | Planned spec | Deliverable and boundary | Dependencies |
|---|---|---|---|
| A: data and scoring | 002 — data ingestion and risk scoring | Import/map transactions, audit data/license/splits, features, baseline/model and explanations behind the scorer contract | Reviewed canonical transaction/assessment contracts; labels stay in permitted training/evaluation paths |
| B: knowledge and RAG | 003 — knowledge ingestion and retrieval | Curated source manifest, ingestion/index, retrieval/citations and retrieval evaluation | Source provenance and a reviewed retrieval contract; does not depend on a trained scorer |
| C: AI investigation | 004 — case investigation and analyst review | Provider adapter, controlled evidence tools, stateful workflow, cited report, human disposition and audit | Case/scoring facts from A and procedures from B through reviewed contracts; clearly marked synthetic adapters can support development before live integrations |
| D: priorities and simulation | 005 — priority queue and simulation | Deterministic ranking/capacity, historical replay and comparisons under explicit simulation assumptions | Versioned scoring/case inputs and capacity assumptions; holdout labels remain outside operational inputs |

Only `001-project-foundation` currently exists in specs/. The names/IDs above are
handoff targets, not generated specifications or implemented features. Start by
specifying `002-data-and-risk-scoring`; each subsequent feature needs its own
specification, plan, contracts and tasks before product implementation.
Review shared inputs early so B/C/D can work against agreed fixtures/adapters
without waiting for A's ML training. Live model/provider/retrieval integration
and quality evaluation remain separate acceptance work; a fixture pass does not
prove those capabilities. New investigation/retrieval/simulation payloads are
future design work, not silently added fields in the foundation contract.

## Shared-contract change review

1. The proposing stream records the requirement, rationale, affected producers/
   consumers, compatibility impact and proposed contract version in the relevant
   feature or decision record.
2. The producing owner and affected consuming owners review that change before
   dependent integration. Record actual review status, reviewer and date when
   review happens; leave them pending otherwise.
3. Update the authoritative schema/API description and all affected validators,
   decoders, adapters and negative/contract tests together. For foundation v1,
   the source is its feature contracts/ directory. Do not loosen closed objects,
   identity/score checks or label exclusion to accommodate an invalid adapter.
4. Run relevant regressions and link actual commands/outcomes and unresolved
   consumer migrations in evidence. Review a compatibility/version strategy
   before a breaking change; routine implementation inside an agreed contract
   needs no repeated scope approval.

## Out-of-course proposals and approval record

Constitution I requires explicit team approval before out-of-course work such
as GNNs, transformer training, multi-agent product orchestration, open-web
investigation or graph databases. Record the proposal in the relevant feature or
decision file with: responsible stream, capability and course fit, expected
benefit, simpler alternatives, effort/schedule impact, affected dependencies and
contracts, decision state (pending/approved/rejected/deferred), and the actual
team decision/participants/date/reference once known. Pending is not approval;
do not implement the extension while that decision is unresolved.

This record grants no new scope exception. Routine authorized work within the
approved MVP proceeds without renewed permission. Preserve human final decisions
and keep automatic account interventions/regulatory submissions outside the MVP.

## Handoff evidence and remaining acceptance

Original instructions and amendments are indexed in
[`prompts/development/001-foundation.md`](../../prompts/development/001-foundation.md).
Actual checks and limitations follow [evidence conventions](../../evidence/README.md).
Each implementation handoff updates tasks.md, its evidence and next_work.md;
documents must distinguish planned work from implemented/verified behavior.
Human review and independent second-person reproduction remain pending until
actual participants record them (T025/SC-001). Phase 6 still owns the final
FR/SC review, full validation and convergence; phase 5 is not foundation completion.
