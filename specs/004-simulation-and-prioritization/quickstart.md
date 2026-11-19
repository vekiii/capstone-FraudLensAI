# Quickstart: Simulation Lab and Decision Intelligence

Start the backend and Vite with the commands below, then select Simulation & Evaluation. Run the bundled scenario with its defaults, or edit the risk score threshold and whole-minute budget per window before submitting. See the [default comparison evidence](../../evidence/tasks/feature-004-us1.md) and [settings verification](../../evidence/tasks/feature-004-us2.md). The recipe export, reopen and ranking inspection steps in the teammate walkthrough are scheduled for a later phase.

## Setup

Use Python 3.14, uv, Node 24 and npm. From the repository root in PowerShell:

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/004-simulation-and-prioritization'
uv sync --locked --group dev
npm.cmd --prefix frontend ci
```

Use the bundled scenario. The initial run requires no batch import, trained model, provider key or Docker service. See the [foundation quickstart](../001-project-foundation/quickstart.md#run-in-two-terminals) for local setup details.

## Test-first validation

1. For SC-001, write failing tests for the ordered selections and exact counts in the hand-calculated example below. Ensure the first failure reflects the missing replay behavior.
2. For SC-002, cover future arrivals, equality at a window start, exclusion at horizon end, carry-over, budget reset, a skipped oversized case, and zero budget. Verify each case is selected at most once per strategy. Include a case between the last window start and horizon end that is admitted into final backlog.
3. For SC-003, exercise an exact recipe rerun and a label-only change. Check that selections are identical after the label change. Check that bad digests and unavailable strategy versions fail as specified. Also cover invalid values, unknown outcomes and a legitimate empty scenario.
4. Run the complete backend and frontend suites for regression coverage. Add a frontend test where an older comparison returns after a new submission or navigation and confirm the older result is ignored.

```powershell
uv run --locked pytest backend/tests
uv run --locked ruff check backend
npm.cmd --prefix frontend run test -- --run
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend run build
```

## Hand-calculated comparison

Use one window starting at the horizon start. All five alerts become available at that start and all weights are 1. The table includes labels for offline evaluation.

| Alert | Score | Review minutes | Outcome |
| --- | --- | ---: | --- |
| A | 0.40 | 2 | Negative |
| B | 0.90 | 2 | Positive |
| C | 0.80 | 1 | Positive |
| D | 0.20 | 1 | Positive |
| E | 0.80 | 1 | Negative |

At threshold `0.30` and budget `2`, D is excluded and C precedes E on both strategies when those alerts tie.

| Strategy | Reviewed in order | Positives found | Missed by threshold | Missed in backlog | Reviewed negatives | Backlog |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| FIFO | A | 0 | 1 | 2 | 1 | 3 |
| Highest score | B | 1 | 1 | 1 | 0 | 3 |
| Weighted score per minute | C, E | 1 | 1 | 1 | 1 | 2 |

At budget `4`, FIFO reviews A and B, finds one positive and leaves two pending. Highest score reviews B, C and E, and weighted score per minute reviews C, E and B. Each finds two positives and leaves one pending.

## Browser walkthrough for SC-004

Start the backend and frontend in separate terminals.

```powershell
uv run --locked uvicorn fraudlens.main:app --app-dir backend/src --host 127.0.0.1 --port 8000
```

```powershell
npm.cmd --prefix frontend run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

1. Open [the local app](http://127.0.0.1:5173). Enter Simulation & Evaluation, choose the bundled scenario and confirm the source and assumptions.
2. Run the comparison at budget 2 and threshold `0.30`. Check the table against the result above. Expand a window to see the ranked candidates, reviewed order and the score, weight and estimated minutes for an alert.
3. Change the budget to 4 and explain the change in the number of positives found and the backlog. Download the recipe, refresh, reopen it and verify the same settings and results.
4. Supply a malformed recipe and check for a readable error. Return to Cases and open a known fixture case. Its score, provenance and navigation should behave as before.
5. Record the actual outcome, tool versions, scenario version and digest, settings and elapsed time. Identify the teammate who performed the walkthrough. Use the project's [evidence template](../../evidence/templates/task.md).

For direct HTTP validation, take the scenario reference from the catalog and submit the [comparison recipe](contracts/replay-v1.md#http-requests).
