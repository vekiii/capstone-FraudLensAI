# Research: Simulation Lab and Decision Intelligence

## Replay and capacity

**Decision**: Use scenario-defined UTC window starts and one analyst-minute budget repeated at each start. At the start of each window, rank the currently available admitted alerts. Scan the order once and review each whole case that fits. Keep unreviewed alerts for later windows and admit late arrivals to the final backlog when they fall inside the horizon.

**Rationale**: The same windows and budgets make the three strategies directly comparable. The selection rule is easy to reproduce by hand and matches FR-002–004. Compare weighted priorities exactly using rational values derived from the input decimals and the positive whole-minute duration. Apply the shared arrival-time and ID tie-break after comparing the actual strategy values.

**Alternatives considered**: Continuous event scheduling and optimal budget allocation. Both change the experiment from comparing simple review policies and add scheduling choices that the MVP does not require.

## Assessment and reproducibility

**Decision**: Package synthetic scenario facts and evaluation outcomes separately. A replay returns its ordered selections before the outcome evaluator reads labels. Keep a versioned scenario fingerprint and export a small recipe that can be reopened through the same comparison endpoint.

**Rationale**: Budget and selection can be reproduced even when labels are unavailable. Hashing the selected scenario revision binds the exact input and outcomes used for the counts. Exporting a recipe meets the rerun requirement without a database, worker or user-specific server state. The recipe contains references and settings only.

**Alternatives considered**: Store server-side comparison records or ask the LLM to explain the preferred strategy. The run recipe supports the local workflow and deterministic score inputs already explain the ordering.

## Batch score source

**Decision**: Finish the bundled flow first. Add a Feature 02 reader after a producer-reviewed export satisfies the following gate.

- Export the complete scored population for one declared cohort and horizon before alert filtering, including scores below the operating threshold. Bind it to one completed, immutable run and retain the input digest, stable transaction IDs, dataset/scorer/feature versions and score kind. Record the source cohort size, the scoreable count and all coverage or warm-up exclusions. If a bounded interactive cohort is needed, declare its selection rule without using labels and retain every scored row in that cohort.
- Supply a documented historical availability time. Use event time only with explicit agreement that the replay simulates availability at event time, preserving the time basis and ties. Verify the historical feature cutoff and point-in-time input policy. The actual offline scoring timestamp records execution time.
- Keep outcome data separately authorized and keyed by dataset version and transaction identity. Join it after selections. Missing outcomes stay unknown. Freeze the scenario and policy before using held-out data for an evaluation.
- Reject partial or mixed runs and unexplained exclusions. A derived run is usable only if its lineage proves the exported score population is identical to the complete pre-policy source.

**Rationale**: The dataset case list reads the active run and returns up to 100 threshold-selected cases. It cannot supply the population for threshold comparisons or missed-positive counts. The producer contract already distinguishes a completed assessment set from its selected case snapshot. [Feature 02 dataset API](../002-data-and-risk-scoring/contracts/api.md) · [Data and scoring boundary](../002-data-and-risk-scoring/contracts/data-and-scoring.md)

**Alternatives considered**: Read the public case list or query whichever run is currently active. Both lose the frozen population and provenance the replay depends on.

## Web integration

**Decision**: Add a scenario catalog and a comparison endpoint through the existing application. Add the Simulation & Evaluation entry to the current vanilla TypeScript and Vite app. Keep the existing cases client and error mapping intact. Confirm the capstone frontend target during branch integration.

**Rationale**: The current frontend uses request cancellation and a generation guard against late results. The simulation view needs the same behavior when the analyst changes settings, starts another comparison or leaves the screen. A frontend-agnostic contract lets the team reuse the simulator if the React app on Feature 05 is selected later.

**Alternatives considered**: Build both frontends or adopt the Feature 05 app on this branch. One integration is sufficient for acceptance and avoids coupling Feature 04 to the Feature 05 merge.
