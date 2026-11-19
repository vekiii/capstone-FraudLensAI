# Feature Specification: Simulation Lab and Decision Intelligence

**Feature Branch**: `004-simulation-and-prioritization`

**Created**: 2026-11-18

**Status**: Implementation and acceptance complete for the bundled synthetic scenario. [Acceptance matrix](../../evidence/tasks/feature-004-acceptance.md)

**Input**: Compare alert review strategies under limited analyst capacity by replaying a frozen synthetic alert stream. See [the approved product idea](../../original_idea.md#8-decision-intelligence-i-simulation-lab).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Compare review strategies (Priority: P1)

An analyst selects a scenario and compares which alerts would be reviewed first and which remain pending under the same review capacity.

**Why this priority**: The analyst can see how the chosen order affects the cases reached with limited time.

**Independent Test**: Replay a small labeled scenario and compare each strategy's selection and outcome counts with a hand-calculated result.

**Acceptance Scenarios**:

1. **Given** three simultaneous alerts A, B and C in stable ID order, scores 0.40, 0.90 and 0.80, respective review costs of 2, 2 and 1 minutes, equal weights, a zero score threshold and a one-window budget of 2 minutes, **When** the analyst compares the three strategies, **Then** FIFO reviews A, highest score reviews B, and weighted score per minute reviews C.
2. **Given** A has a negative label and B and C have positive labels, **When** outcomes are shown for that selection, **Then** FIFO reports zero positives found, two positives missed and one reviewed negative, while each other strategy reports one positive found, one positive missed and zero reviewed negatives. Each strategy leaves two admitted alerts pending.

### User Story 2 - Explore capacity and threshold (Priority: P2)

An analyst changes the review budget or score threshold and sees how the change affects review coverage and backlog.

**Why this priority**: The analyst can compare trade-offs before choosing an advisory ordering.

**Independent Test**: Replay one stream with two review windows and change one control at a time.

**Acceptance Scenarios**:

1. **Given** one alert arrives before a window starts and another arrives during it, **When** both meet the threshold, **Then** only the first may be selected in that window and the second is first eligible in the next window.
2. **Given** one positive is below the threshold and another is admitted but still pending at the end, **When** the analyst inspects the results, **Then** two positives are reported missed, with one attributed to the threshold and one to the final backlog.
3. **Given** a 2-minute budget with a 3-minute alert ranked first and a 1-minute alert ranked second, **When** the window starts, **Then** the first remains pending and the second is reviewed.

### User Story 3 - Reproduce and explain a run (Priority: P3)

A reviewer reruns a saved comparison and sees why each strategy ordered its alerts as shown.

**Why this priority**: The team can demonstrate the experiment and verify its findings independently.

**Independent Test**: Repeat a saved run on its frozen input, then repeat it after changing labels alone in a separate scenario.

**Acceptance Scenarios**:

1. **Given** the same frozen input, settings and strategy versions, **When** the reviewer reruns the comparison, **Then** ordered selections, counts and reported backlog match exactly.
2. **Given** two scenarios whose only difference is their outcome labels, **When** they are replayed with identical settings, **Then** both produce the same order and selections and only label-based outcome counts may differ.
3. **Given** a weighted ordering result on a fixture, **When** the reviewer inspects a selected alert, **Then** they can see its score, weight and review duration, the source of the score and which values are simulation assumptions.

### Edge Cases

- The first review window starts at the inclusive start of the replay horizon. An alert arriving exactly at a window start is eligible in that window. Alerts arriving after the last window starts and before the replay horizon ends can enter final backlog but cannot be reviewed. The end of the horizon is exclusive.
- Equal strategy values are broken by earliest alert availability and then ascending stable alert ID. Every strategy uses the same tie rule.
- A zero capacity leaves all admitted alerts pending. An empty scenario returns zero counts. A score equal to the threshold qualifies.
- Duplicate IDs, missing or invalid score, nonpositive weight or review duration, inconsistent time windows and invalid settings produce a clear validation error.
- A scenario with missing labels can still rank and count reviews and backlog. It shows known positives and negatives, counts unknown outcomes and makes incomplete label coverage visible. With no known labels, label-based metrics are unavailable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Analysts MUST be able to select a frozen scenario and see its source, covered time range, score provenance and simulation assumptions. A bundled synthetic scenario MUST support the complete flow independently of Feature 02.
- **FR-002**: Analysts MUST be able to set a score threshold and a nonnegative review budget in minutes per window. Each strategy MUST use the same frozen alerts, threshold, window boundaries and budget for a comparison.
- **FR-003**: The replay MUST admit only alerts at or above the threshold within the horizon and rank only pending alerts available at the start of each window. Reviewed alerts MUST leave the queue after that window. Unreviewed alerts MUST carry forward. Start each window with its configured budget.
- **FR-004**: The comparison MUST support FIFO by availability, descending score and descending `score × scenario weight / estimated review minutes`, with the documented tie rule. Each strategy scans its ranked queue once per window, reviews whole cases that fit the remaining budget and leaves cases that do not fit pending.
- **FR-005**: The comparison MUST report per strategy the number reviewed, known positives found, known positives missed by threshold or backlog, reviewed negatives, final admitted backlog and unknown labels. Known positives missed MUST count every known positive in the horizon that was never reviewed. Unknown label counts MUST cover both the scenario horizon and the reviewed subset.
- **FR-006**: All ranking and selection MUST use only facts available by the decision time. The replay MUST consult outcome labels only when computing outcome metrics after selection.
- **FR-007**: The system MUST retain scenario identity and version, provenance, threshold, budget, boundaries, strategy versions and any generation seed that applies. These values MUST be available to reproduce a run and identify the settings behind its results.
- **FR-008**: Analysts MUST be able to inspect recommended review order and its inputs. Scores, scenario weights and time estimates MUST be clearly labeled. Any positive outcome label MUST be presented as a benchmark outcome. Recommendations MUST leave final decisions with the analyst and keep simulation activity isolated from case dispositions and stored scores.
- **FR-009**: Invalid comparisons MUST surface a readable error and produce no results. Legitimate empty runs and incomplete label coverage MUST use the behavior defined under Edge Cases.

### Key Entities

- **Scenario**: Frozen stream, source version, time range, review windows and documented assumptions.
- **Alert**: Stable ID, availability time, score and source, scenario weight and review duration. Evaluation outcome is associated separately by stable ID.
- **Comparison run**: Scenario reference, threshold, per-window capacity, strategy versions, ordered selections and measured outcomes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All three strategies match the expected order and outcome counts on a hand-verified scenario including ties and an alert below the threshold.
- **SC-002**: Across all three strategies and each review window, reviewed minutes stay within the configured budget and every selected alert is available at the window start and reviewed at most once per run.
- **SC-003**: Two replays of the same complete run inputs yield identical selections and counts. A label-only variation yields identical selections across all three strategies.
- **SC-004**: A teammate can complete one bundled scenario comparison, change the budget and identify the resulting differences in positives found and backlog. The walkthrough requires only the bundled scenario data.

## Assumptions

- The first version uses fixed, scenario-defined review windows and estimates analyst capacity in whole review minutes. The Scenario explains the origin of weights and durations. Recommendations use a heuristic score and carry no calibrated probability or expected financial loss claim.
- Feature 02's published historical score output is the intended later scenario source. Integrating that source depends on a compatible frozen export with stable IDs, availability and score provenance. The bundled scenario is the first acceptance input.
- Feature 04 fits within the approved Simulation Lab and Decision Intelligence scope. It covers historical comparisons and advisory ordering. Live streaming, model training, LLM-assisted ranking and automated operational actions are outside this feature.
