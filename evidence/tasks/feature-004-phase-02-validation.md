# Feature 004 T002-T004 validation - 2026-11-18 Europe/Belgrade

Status: **complete**, stop before T005. Branch 004-simulation-and-prioritization,
HEAD 734c433cbd9aff487d81752514a9f08237320889; initially clean worktree.
[Exact original prompt](../../prompts/development/004-simulation-phase-02.md),
[tasks](../../specs/004-simulation-and-prioritization/tasks.md),
[contract](../../specs/004-simulation-and-prioritization/contracts/replay-v1.md),
[data model](../../specs/004-simulation-and-prioritization/data-model.md).
Traces FR-001 (frozen inputs/provenance), FR-006 (outcome separation), FR-007
(repeatable identity), and foundational validation for SC-003.
No replay/metric acceptance or simulation browser claim is made.

AGENTS then next_work read first. Scoped speckit-implement; explicit
SPECIFY_FEATURE_DIRECTORY=specs/004-simulation-and-prioritization; prerequisites
exit0 to correct absolute feature directory. Checklist16/16, markers unchanged;
extensions.yml absent, no pre/post hooks. No agents or dependency installation.
Python3.14.3, uv0.10.9; existing locked dependencies. Commands from repository
root D:\AIBootcamp\capstone with UV_CACHE_DIR=.cache/uv.

## T002 authored fixture

Two separate JSON files under data/fixtures/simulation: facts contain A-E scores
0.40/0.90/0.80/0.20/0.80, costs2/2/1/1/1, unit weights, threshold0.30/budget2;
outcomes contain only matching ID/version plus A/E negative, B/C/D positive.
UTC horizon 2026-01-01T00:00:00Z to 01:00:00Z and one start at00:00 are authored
deterministic assumptions, not observed data. Source bundled_synthetic,
data_version authored-v1, illustrative-v1 fixture scorer, equal-weight/duration
assumptions and generation_seed null explicitly recorded. C/E tie preserved.
During preparation the digest was unset, never claimed valid; after T004 it was
computed by the implemented canonical function and written as:

`894136f422d013cf0d1d52820acf26e3a3a95076a4b8ab044c4e24faf4105198`

Actual Catalog.resolve('review-capacity-demo',1) succeeds: 5 facts, 5 separate
private outcomes, label-free metadata. Recomputed fingerprint equals declared.

## T003 RED and T004 GREEN

Minimal importable stubs allowed actual assertions. First invocation had a
SyntaxError in a test decorator; corrected before business RED. That collection
error is NOT RED evidence. Second invocation: **53 failed / 1 passed**, exit1:
missing validation DID NOT RAISE, constant fingerprint failed sensitivity, stub
catalog lacked resolution. No artificial damage to existing behavior.

Implemented strict Pydantic nested models (closed/frozen/strict, boolean/numeric
coercion refused), valid calendar/UTC, exact Decimal range comparison, JS-safe
integer bounds, ordered 1-12 windows, <=250 unique alerts and resolved assumption
references. Separate outcomes validate identity/foreign/duplicate IDs. Initial
GREEN **54 PASS**; added trailing-newline-ID, resolved-root boundary and returned
copy isolation checks: final **56 contract tests PASS**. Ruff initially reported
import/unused-variable/compact test statement style; formatting and local fixes
resolved all without weakening assertions.

Fingerprint hashes both validated sets after decimal text normalization (no
Decimal context rounding), six-digit UTC, sorted object keys and unordered
alerts/outcomes/assumptions; excludes its own field and defaults absent seed to
null. High-precision weight sensitivity tested beyond default Decimal precision.
Catalog performs identity lookup only, never caller paths; resolved read paths
stay inside trusted root. Duplicate JSON members/nonfinite literals rejected;
changed declared hashes/conflicting revisions fail safely. Returned copies
prevent consumer mutations changing stored facts/private outcomes. Metadata
explicitly excludes alerts; replay can receive facts independently of the
explicit evaluation_outcomes boundary. Future code must still join labels only
after selection; no replay function exists yet.

## Executed commands and regression

Every pytest invocation created a unique absolute parent under .cache first.
Actual suffixes: 004-p2-red-<guid>, 004-red-<guid>, 004-green-<guid>,
004-final-<guid>, 004-full-<guid>; temporary directories ignored. Commands:

```powershell
$env:SPECIFY_FEATURE_DIRECTORY='specs/004-simulation-and-prioritization'
$env:UV_CACHE_DIR=Join-Path $PWD '.cache/uv'
$t=Join-Path $PWD ('.cache/004-final-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $t | Out-Null
uv run --locked pytest backend/tests/contracts/test_simulation_contracts.py --basetemp "$t/tmp" -o "cache_dir=$t/cache" -q --tb=short
# RED: exit1,53failed/1passed; first GREEN: exit0,54passed
uv run --locked pytest backend/tests/contracts/test_simulation_contracts.py backend/tests/integration/test_startup.py --basetemp "$t/tmp" -o "cache_dir=$t/cache" -q --tb=short
# Final: exit0,64passed (56 contracts + 8 startup),0.61s
# Full run used its own fresh 004-full-<guid> parent:
uv run --locked pytest backend/tests --basetemp "$t/tmp" -o "cache_dir=$t/cache" -q --tb=short
# exit0,366passed,2.68s
uv run --locked ruff check backend
# exit0,All checks passed
git diff --check
```

One unchanged Starlette/httpx deprecation warning in backend regression. No
lockfile, shared instructions, original Cases code/contracts/fixtures or frontend
changes. No provider, dataset, DB/ML/Feature02/Feature05 integration, API route or
UI implementation. Frontend/browser not run because untouched/outside phase.
Human review **pending**, second-person reproduction **pending**, no invented
reviewer/signature. This is synthetic contract/regression evidence, not model
evaluation. Next separately scoped phase: T005-T011.
