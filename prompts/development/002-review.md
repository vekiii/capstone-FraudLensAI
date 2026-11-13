Act as an independent Principal Software Architect, Senior ML Engineer, Product Requirements Analyst, and QA Lead.
Your task is to perform a rigorous, adversarial review of Feature 002: Data Ingestion and Risk Scoring.
First, locate and read:
- Feature 002 spec.md
- Phase 2 requirements.md
- Feature 002 specification quality checklist
- Project constitution and governing instructions
- original_idea.md
- Feature 001 specification and contracts
- Existing implementation and relevant tests
- Architecture and technical decision records
Discover the actual repository paths. Do not assume a file exists. Report missing references.
OBJECTIVE
Determine whether Feature 002 is complete, correct, internally consistent, implementable, testable, scientifically defensible, and aligned with Phase 2 requirements.
Do not assume that the existing specification checklist is correct.
AUDIT AREAS
1. Missing functional or nonfunctional requirements
2. Ambiguous, contradictory, or incomplete requirements
3. Requirements that cannot be tested objectively
4. Inconsistencies between spec.md and requirements.md
5. Conflicts with the project constitution
6. Conflicts with Feature 001 contracts or implementation
7. Missing user journeys, acceptance scenarios, and edge cases
8. Incorrect assumptions about the IBM AML dataset
9. Data leakage, temporal leakage, and evaluation leakage risks
10. Model selection, validation, calibration, and reproducibility
11. Scoring and explanation correctness
12. Dataset identity, deduplication, and provenance
13. Runtime reliability, error handling, and partial failures
14. Security, privacy, dependency, and artifact safety
15. Maintainability, implementation complexity, and scope creep
16. Missing decisions that must be made before implementation
17. Opportunities to simplify without sacrificing requirements
FOR EACH FINDING PROVIDE
- Severity: CRITICAL / HIGH / MEDIUM / LOW
- Category
- Exact file and line reference
- Relevant requirement ID, if applicable
- Explanation of the problem
- Concrete failure scenario
- Recommended correction
- Whether correction belongs in spec.md, requirements.md, plan.md, contracts, or tests
IMPORTANT RULES
- Be skeptical and actively look for defects.
- Do not invent requirements or claim an issue without evidence.
- Distinguish confirmed defects from potential risks and optional enhancements.
- Do not propose unnecessary enterprise infrastructure.
- Preserve the educational capstone scope.
- Do not modify files.
- Do not implement anything.
- Do not mark requirements complete merely because they are documented.
- Assess specification quality separately from implementation status.
FINAL OUTPUT
A. Executive summary
B. Overall readiness: READY / READY WITH CHANGES / NOT READY
C. Critical and high-severity findings
D. Medium and low-severity findings
E. Missing requirements
F. Contradictions and ambiguities
G. Recommended improvements ranked by impact
H. Questions requiring human decisions
I. Exact changes recommended before technical planning
Be rigorous. A superficial positive review is not acceptable.


answer:


## A. Executive summary

Feature 002 is a thoughtful and unusually careful draft: it explicitly separates synthetic fixture behavior from model results, protects holdout labels, calls for temporal features, acknowledges contract migration, and avoids claims of real-world predictive performance. The major risks are concentrated in decisions that determine whether its baseline, features, thresholds, and evaluation can produce reproducible, meaningful results.

The requested **“Phase 2 requirements.md” was not present** in the repository. A repository-wide file search found the Feature 002 quality checklist and Feature 001’s Phase 2 handoff, but no separate Phase 2 requirements document. The original project idea says a formal Bootcamp scoring rubric had not been provided ([original_idea.md:25–43](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/original_idea.md>)). I can assess alignment with the project’s stated Module 2 Python/API outcomes, but not certify compliance with an absent rubric.

The repository’s current implementation is Feature 001 only. Feature 002 has no plan, tasks, contracts, implementation, or tests. The findings below assess specification quality separately from that implementation status.

## B. Overall readiness: NOT READY

**Not ready for implementation.** The specification is a strong starting point, but important behavioral and evaluation choices remain open, and the checklist overstates how fully they are resolved. Resolve the high-severity findings below before technical planning is treated as settled. The missing Phase 2 requirements document also prevents a complete course-specific compliance check.

There are no confirmed conflicts with the constitution or Feature 001 that require abandoning the design. The main Feature 001 constraint is explicit: its contract only allows three-digit IDs, one two-decimal amount, one three-letter currency, and a single bounded score/explanation shape ([schemas.json](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/001-project-foundation/contracts/schemas.json:6>), [data-model.md](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/001-project-foundation/data-model.md:6>)). Feature 002 recognizes that migration; it must remain a reviewed, versioned contract change as the constitution requires.

## C. Critical and high-severity findings

**H1 — The rule baseline has no specified behavior.**
**Severity:** HIGH · **Category:** Product requirements / testability · **References:** [spec.md:46–70](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:46>), [spec.md:203–225](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:203>) · **Requirements:** FR-005–007, SC-002–004.

FR-007 requires a versioned rules baseline with documented thresholds, score, triggers, and cold-start behavior. The spec does not say which rules or observable indicators define that baseline. The independent test asks for “exact scores and reasons,” but there is no expected rule behavior against which to test them. The existing Feature 001 rules scorer is only a test adapter; its own decision record says its constant is illustrative, not an AML rule ([fixture-scoring.md:18–48](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/docs/decisions/fixture-scoring.md:18>)).

*Failure scenario:* Two implementations choose different “rule” scores and triggers, both pass generic finite-score checks, and their model comparisons are not comparable or reproducible.

*Correction and destination:* Define a small, label-free, observable rule policy and expected trigger/score semantics in `spec.md`; leave algorithm details and implementation in `plan.md`. Add hand-computed timeline, boundary, and cold-start tests. If rules are intended only as a nonpredictive placeholder, say so and do not call their comparison a meaningful risk baseline.

**H2 — Invalid labels can accidentally determine which event facts enter history.**
**Severity:** HIGH · **Category:** Data leakage / import semantics · **References:** [spec.md:40–42](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:40>), [spec.md:167–180](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:167>), [spec.md:191–213](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:191>), [spec.md:236–240](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:236>) · **Requirements:** FR-002, FR-006, FR-012.

The import requirements say invalid labels are an edge case and rows are accepted or rejected, while historical features use available observations and labels are confined to fit/evaluation. They do not specify whether a row with valid transaction fields but a missing or malformed target label remains eligible as **label-free event history**. IBM describes the benchmark labels as synthetic transaction labels; they are evaluation annotations, not an operational field ([IBM AML-Data README](https://github.com/IBM/AML-Data/blob/main/README.md)). The spec’s own rule that label perturbations must not alter earlier features is not enough if label validity changes row inclusion.

*Failure scenario:* A valid transfer with a malformed target label is rejected wholesale, then disappears from later account history. A later score changes because of label quality, even though the observable transfer facts are unchanged.

*Correction and destination:* In `spec.md`, distinguish event-row validity from supervised-label eligibility. Define which fields are required for operational history, and require label perturbation or label removal to leave import identity and label-free histories unchanged. Add controlled tests for missing/invalid labels with otherwise valid events.

**H3 — Time semantics and warm-up policy are not sufficiently settled for the core temporal evaluation.**
**Severity:** HIGH · **Category:** Temporal leakage / scientific validity · **References:** [spec.md:59–67](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:59>), [spec.md:175–177](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:175>), [spec.md:210–213](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:210>), [spec.md:370–382](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:370>) · **Requirements:** FR-006, FR-010, FR-012.

The spec itself lists missing timezone and distinct event, scoring-as-of, and execution times, but it does not define the timezone interpretation, warm-up coverage behavior, or how to represent features when one-day history is unavailable. This matters because the paper describes HI-Small as roughly five million transactions over only ten days, with about 3,600 laundering transactions ([dataset statistics in the authors’ paper](https://arxiv.org/html/2306.16424v2)). A one-day lookback therefore spans a substantial share of the dataset’s duration. The paper’s reported benchmark uses a different 60/20/20 temporal split; that does not make the spec’s 70/15/15 choice wrong, but the project should justify and freeze its own protocol.

*Failure scenario:* One implementation treats naive timestamps as UTC, another as local time, or one silently treats the first day’s missing history as zero. They produce different splits and features while appearing to follow the current text.

*Correction and destination:* Specify the event-time interpretation, as-of boundary, treatment of ties, warm-up interval, and missing-history representation. Require the data audit to report timestamp resolution, coverage, ties, and observed split boundaries before the protocol is frozen. Put executable mechanics in `plan.md`; cover boundary and cold-start cases in tests.

## D. Medium and low-severity findings

**M1 — The alert threshold can pass by selecting no alerts.**
**Severity:** MEDIUM · **Category:** Evaluation / acceptance testability · **References:** [spec.md:247–260](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:247>), [spec.md:383–387](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:383>) · **Requirements:** FR-014, FR-016; SC-004.

“Choose a threshold for at most 20 validation alerts” permits a threshold producing zero alerts. The spec also explicitly allows zero alerts. That is honest reporting, but it means a threshold can satisfy the rule without demonstrating that the scoring pipeline can deliver useful cases.

*Failure scenario:* A threshold of 1.0 produces no alerts, no errors, and an empty case list; threshold acceptance passes without the alert-selection policy being exercised.

*Correction and destination:* State whether the goal is exactly K alerts subject to deterministic tie-breaking, the maximum achievable count, or another explicit operating rule. Keep a genuine zero-alert outcome valid when the data warrants it, but require tests that distinguish it from an arbitrary threshold choice. Update `spec.md` and the evaluation tests.

**M2 — “Uncertainty limits” are required but not operationalized.**
**Severity:** MEDIUM · **Category:** Scientific defensibility · **References:** [spec.md:231–235](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:231>), [spec.md:261–267](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:261>) · **Requirements:** FR-011, FR-017.

FR-011 asks for uncertainty limits, but the spec names no method or reporting rule. This matters for Precision@20 and Recall@20, where small changes in a handful of labels can change the result materially. Transactions are also temporally and account-linked, so treating all rows as independent observations may overstate confidence.

*Failure scenario:* The report prints precise-looking point metrics on a single ten-day synthetic sequence and calls them stable, with no indication of their sampling or dependence limits.

*Correction and destination:* In `plan.md`, predeclare whether to report only exact counts and qualitative limitations, or a suitable uncertainty/sensitivity method. Document dependence and the short observation horizon; do not imply that a simple row-wise interval establishes independent real-world performance.

**M3 — Import and run atomicity are implied, not testable.**
**Severity:** MEDIUM · **Category:** Reliability / partial failures · **References:** [spec.md:38–42](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:38>), [spec.md:222–224](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:222>), [spec.md:282–289](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:282>) · **Requirements:** FR-009, FR-021; SC-001, SC-007.

The spec prohibits partial publication and requires restart-reproducible runs, and lists interrupted runs as an edge case, but never says what state survives interruption or how a completed run becomes visible atomically.

*Failure scenario:* Scoring fails halfway through a batch; some cases are visible while the run is marked failed or is later retried, producing mixed run versions.

*Correction and destination:* Define a simple local staging/complete/publish boundary and retry behavior in `plan.md`, with failure injection tests. No distributed transaction system is warranted for the stated local single-user scope.

**M4 — Trusted artifact loading has a security boundary but no verification rule.**
**Severity:** MEDIUM · **Category:** Artifact safety / supply chain · **References:** [spec.md:268–271](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:268>), [spec.md:318–320](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:318>) · **Requirements:** FR-018.

The spec says to use trusted local artifacts and not load arbitrary uploaded models, which is sensible. It does not define how an artifact becomes trusted or how its integrity and compatibility are checked before loading. The risk depends on the serialization format and local workflow, so this is a planning decision rather than evidence of a current vulnerability.

*Failure scenario:* A stale or replaced local artifact is loaded under the expected model version, or an unsafe serialization format executes code when deserialized.

*Correction and destination:* In `plan.md`, define a minimal trusted artifact workflow: source, hash, schema/version compatibility, and an appropriate safe format or explicit trust boundary. Add mismatch/corruption tests. No model registry is needed.

**M5 — The quality checklist claims more closure than the specification supports.**
**Severity:** MEDIUM · **Category:** Requirements quality / review gate · **References:** [requirements.md:17–32](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/checklists/requirements.md:17>), [requirements.md:45–53](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/checklists/requirements.md:45>).

It marks all requirements testable and says there are no critical unresolved product choices, but the rules and threshold behaviors above are not objectively testable as written. The checklist itself notes that exact source schema/counts and numeric planning settings are future work, and human review is pending. Those are valid deferrals; the problem is the checked claims of complete closure.

*Failure scenario:* Planning begins on the assumption that the spec has already passed a completeness gate, so missing behavior becomes an unreviewed implementation choice.

*Correction and destination:* Revisit the affected checklist statements after resolving the product-level decisions; keep planning-level implementation choices explicitly deferred. Do not treat checklist completion as evidence that Feature 002 works.

**M6 — Local resource and completion-time limits are not measurable.**
**Severity:** LOW · **Category:** Nonfunctional requirements / capstone scope · **References:** [spec.md:383–393](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:383>), [spec.md:407–415](</C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:407>).

The feature depends on local compute and a multi-million-row dataset, but no rough runtime or memory budget is stated. This is not a reason to add infrastructure; it does affect whether an ordinary team machine can complete import, features, and evaluation within the capstone schedule.

*Failure scenario:* A technically correct implementation exhausts memory or takes too long on a teammate’s machine, blocking reproduction.

*Correction and destination:* During planning, benchmark a small representative sample and record a modest target environment/resource budget; use a simple streaming or bounded sample strategy if needed. Put this in `plan.md` and reproduction evidence.

## E. Missing requirements

1. **Phase 2 source requirements:** no standalone `Phase 2 requirements.md` exists in the repository. The only Feature 002 “requirements” artifact is its checklist. The project context provides high-level Module 2 (Python/API) outcomes, not an authoritative detailed rubric. Obtain or identify the actual course requirements before claiming full compliance.
2. **Rules policy:** define observable indicators, score construction, thresholds, currency treatment, cold-start behavior, and deterministic reason semantics.
3. **Timestamp semantics:** define timezone interpretation, event/as-of ordering, warm-up interval, and missing-history behavior after inspecting the acquired release.
4. **Label-independent event eligibility:** specify whether valid transaction facts with absent/invalid labels may still support operational history.
5. **Threshold operating policy:** define what “at most K alerts” means and how to choose a threshold without letting zero alerts pass trivially.
6. **Partial-run behavior:** specify when imported data or scored cases become visible and how retries avoid mixed or duplicate results.
7. **Statistical reporting:** define what “uncertainty limits” means for the selected metrics and short, dependent timeline.
8. **Artifact trust rule:** define integrity/compatibility checks and safe model loading at the plan boundary.
9. **Practical resource target:** set a local-machine budget sufficient for import and repeatable evaluation, or explicitly permit a documented reduced development view while retaining the defined benchmark protocol.

## F. Contradictions and ambiguities

- **Actual internal contradiction:** The checklist says FR-001–026 are testable and no critical open questions remain, while the rule and threshold behavior are not specified enough to derive unique expected results.
- **Potential data-policy conflict:** FR-002 rejects malformed-label rows while FR-006 requires historical facts to remain label-free. Unless operational-event validity and label validity are distinct, changing a label can change which event facts enter history.
- **Unresolved temporal interpretation:** The spec notes timezone-naive timestamps and separate event/scoring/execution times but does not settle how those values are interpreted. The paper describes HI-Small as a ten-day dataset, making the one-day lookback and boundary policy consequential ([authors’ dataset table](https://arxiv.org/html/2306.16424v2)).
- **Not a contradiction, but a required migration:** Feature 001 only supports `TX-###`/`CASE-###`, a single amount/currency, and its current explanation/provenance shape. FR-023 correctly requires reviewed migration; do not implement Feature 002 by silently broadening those validators.
- **Not inherently wrong, but must be justified:** Project 70/15/15 differs from the authors’ 60/20/20 temporal split. The project’s choice is allowed; record why it suits this capstone and verify actual timestamp-group boundaries before freezing it.
- Constitution alignment is otherwise sound: one explainable model, bounded comparison, no label exposure to operations, local synthetic data, human authority, and no unsupported production claims.

## G. Recommended improvements ranked by impact

1. Specify a deterministic, label-free rule baseline with hand-checkable expected outcomes.
2. Define temporal semantics and warm-up behavior after auditing the exact acquired data.
3. Separate event facts from labels so label quality cannot alter operational history.
4. Define a meaningful validation threshold policy and its tie behavior.
5. Decide how to report uncertainty and the limitations of this short synthetic timeline.
6. Define atomic local import/run publication and artifact trust checks in the technical plan.
7. Add a reproducible resource target and a policy for insufficient data or compute.
8. Reassess the checklist claims after the spec changes and human review.

## H. Questions requiring human decisions

1. Where is the authoritative Phase 2 requirements document, if it exists outside this repository? Which rubric/version governs?
2. What rules are the team willing to present as a transparent comparison baseline, and which observable transaction fields may those rules use?
3. Should rows with valid transfer facts but missing/invalid labels remain available for label-free history, while being excluded from supervised fitting/evaluation?
4. After the data audit, how should timezone-naive event times and initial one-day warm-up be represented?
5. Is the alert policy “take the highest-ranked K validation items,” “threshold for at most K,” or another capacity rule?
6. What local hardware and time budget can the team reasonably promise for reproducing the 5M-row experiment?
7. Does the team want a model run to be an acceptance requirement if data/compute or minimum class eligibility makes training infeasible? The current text calls such a run incomplete, while also promising a usable rules baseline.

## I. Exact changes recommended before technical planning

1. In `spec.md`, add the missing rules behavior at the outcome level and clarify label-independent event handling.
2. Add a temporal decision section to `spec.md` for event-time normalization, warm-up, feature availability and per-transaction as-of semantics; keep exact parser and partition implementation details in `plan.md`.
3. Replace the ambiguous threshold statement with an explicit operating-point rule and acceptance tests that cover ties, fewer than K rows, zero positives, and genuine zero-alert outcomes.
4. Define the minimum uncertainty reporting requirement or state explicitly that only counts and qualitative limits are claimed.
5. Revise only checklist assertions that currently overclaim closure; state that human review is pending and implementation/evaluation are not complete.
6. Confirm whether the missing Phase 2 rubric exists; if supplied, map each relevant criterion to specific Feature 002 requirements and acceptance evidence.
7. Then use `plan.md` to set exact source hash/license audit, split manifest, numeric tolerances, atomic publication, artifact format/trust, dependency/resource budgets and test fixtures. Keep these as planning choices where the spec already defines the required behavior.

No files were changed. The current working tree still contains the prior contribution-report documentation changes. Feature 002 itself remains specification-only.

The primary-source review confirms the dataset is synthetic and distributed under CDLA-Sharing-1.0 despite the repository’s Apache-2.0 license, so the acquired data’s license must be recorded and the raw data kept out of Git ([IBM AML-Data README](https://github.com/IBM/AML-Data/blob/main/README.md)). The authors report HI-Small at five million transactions across ten days, with roughly 3,600 laundering-labeled transactions ([paper dataset table](https://arxiv.org/html/2306.16424v2)).


question :
Perform a full bidirectional requirements traceability audit for Feature 002.
Read:
- Phase 2 requirements.md
- Feature 002 spec.md
- original_idea.md
- Project constitution
- Feature 001 contracts and relevant decisions
Treat requirements.md as a requirements source, while respecting any higher-priority governance documents. Report conflicts instead of silently choosing one document.
TASK 1: REQUIREMENT COVERAGE
Extract every relevant Phase 2 requirement, including implicit constraints and mandatory acceptance conditions.
For each requirement, identify:
- Source file and exact location
- Requirement description
- Matching Feature 002 requirement ID
- Matching acceptance scenario
- Matching success criterion
- Coverage status: FULL / PARTIAL / MISSING / CONFLICTING
TASK 2: REVERSE TRACEABILITY
Review every Feature 002 functional requirement FR-001 through FR-026.
Determine whether each requirement:
- Comes from the stated project goals
- Supports a user journey
- Is necessary for correct implementation
- Adds unsupported scope
- Duplicates another requirement
- Conflicts with Phase 2 requirements
TASK 3: SUCCESS CRITERIA
Review SC-001 through SC-009.
For each success criterion, verify that:
- It has corresponding functional requirements
- It has measurable acceptance conditions
- It is feasible within project constraints
- It can be independently verified
- Required evidence is clearly defined
TASK 4: CONSISTENCY
Identify inconsistent terminology, assumptions, data definitions, scoring semantics, and workflow expectations.
Pay special attention to:
- Dataset acquisition and provenance
- Rule-based baseline versus ML model
- Feature generation and point-in-time correctness
- Dataset-backed application integration
- Explainability requirements
- Evaluation methodology
- Fixture compatibility
- Phase boundaries and exclusions
OUTPUT
1. Bidirectional traceability matrix
2. Missing requirements
3. Partially implemented requirements in the specification
4. Unsupported or unnecessary requirements
5. Contradictions requiring resolution
6. Proposed exact additions or revisions
7. Final coverage percentage with calculation methodology
Do not change any files.
Never treat vaguely related statements as full coverage.


asnwer:
# Feature 002 bidirectional traceability audit

## A. Executive summary and readiness

**Overall readiness: NOT READY for final Phase 2 coverage sign-off.** The repository contains no standalone **Phase 2 requirements.md** matching the requested requirements source. I found the Feature 002 and Feature 001 quality checklists, but those are not Phase 2 requirements. `original_idea.md` also says the official Bootcamp assessment rubric was not supplied (lines 25–27). I therefore cannot extract every Phase 2 requirement or honestly claim a Phase 2 coverage percentage.

I completed the reverse trace for all 26 Feature 002 functional requirements against the available approved idea, constitution, and Feature 001 contracts and decisions. The spec is **not implementation evidence**: `next_work.md` says Feature 002 is specified, with no data audit, model training, contracts, tasks, or product implementation yet. The local Feature 002 checklist itself says human feature review is pending and exact source schema/counts and planning settings remain future work (checklist lines 50–53).

**Coverage figures, with limits:**

- **Phase 2 requirements coverage: N/A.** There is no available Phase 2 requirements source from which to define a denominator.
- **Available-goal traceability across 26 FRs:** 17 full, 8 partial, 1 unsupported. Conservative full-only coverage is **17/26 = 65.4%**. If a partial link is scored as one-half, weighted traceability is **21/26 = 80.8%**. These figures measure the audit’s link judgments to *available* sources; they do not substitute for Phase 2 coverage or imply implementation.
- The repository contains no Feature 002 plan, tasks, contracts, or implementation to inspect, so coverage here means **specified traceability only**.

## 1. Bidirectional traceability matrix

The “Phase 2 match” column is **unverifiable for every row** because that source is missing. The source column identifies available governing basis. Acceptance scenarios (AS) and success criteria (SC) refer to IDs in `specs/002-data-and-risk-scoring/spec.md`.

| Feature 002 requirement | Available source and reverse-trace judgment | Journey / acceptance scenario | SC | Phase 2 match |
|---|---|---|---|---|
| FR-001 | `original_idea.md` §3.1 lines 47–59 calls for IBM HI-Small, a data card, source/version/license and verification; Constitution scope lines 52–57 bounds the project. **FULL** | US1 AS1, AS5 | SC-001, SC-009 | Unverifiable |
| FR-002 | `original_idea.md` §3.1 lines 55–59 requires checking the acquired file and recording data limitations; the spec adds exhaustive row accounting and detailed quality reporting. **PARTIAL** | US1 AS1, AS5 | SC-001 | Unverifiable |
| FR-003 | `original_idea.md` §7 lines 187–195 explicitly requires bank-qualified identity, currency-safe aggregation, time-correct data and label separation; absent attributes must not be invented (lines 116–119). **FULL** | US1 AS2–3; US2 AS1–3 | SC-001–002 | Unverifiable |
| FR-004 | Stable source-derived identities and preserving distinct equal-value events are specific design elaborations; necessary for idempotent import and consistent cases, but not directly stated as such in the available idea. **FULL for implementation necessity; source support is inferential** | US1 AS4; US5 AS1, AS3 | SC-001, SC-007 | Unverifiable |
| FR-005 | `original_idea.md` §4 lines 106–118 and §7 lines 187–195 call for deterministic historical features, feature contributions, and no invented context; excluding opaque IDs as predictors is a sound leakage safeguard not stated as an explicit idea requirement. **FULL** | US2 AS1, AS3 | SC-002 | Unverifiable |
| FR-006 | `original_idea.md` §7 lines 187–195 explicitly requires point-in-time history and label separation. Tied-event ordering rules sharpen that requirement. **FULL** | US2 AS1–2 | SC-002, SC-005 | Unverifiable |
| FR-007 | `original_idea.md` §7 lines 170–183 specifies documented baseline rules before ML; Constitution IV requires deterministic calculations. Exact bounded-score and cold-start semantics are design details. **FULL** | US2 AS3–4; US3 AS5 | SC-003 | Unverifiable |
| FR-008 | `original_idea.md` §5 lines 151–155 calls for versioned scorer output and visible source; Constitution VIII requires distinguishable fixture/rules/model outputs. **FULL** | US2 AS4; US4 AS1 | SC-003, SC-006 | Unverifiable |
| FR-009 | Constitution IV, VII and VIII require deterministic validation, label isolation, and explicit replaceable boundaries. No silent scorer substitution is consistent with truthful source provenance. **FULL** | US4 AS4; US5 AS5 | SC-003, SC-007 | Unverifiable |
| FR-010 | `original_idea.md` §7 lines 187–195 explicitly sets chronological train/validation/test, initially 70/15/15, with no future fitting and unchanged test prevalence. **FULL** | US3 AS1 | SC-004–005 | Unverifiable |
| FR-011 | The idea requires checking that partitions have enough positives (§7 lines 187–188), but does **not** set “at least 20” per validation and test. FR-011 labels this a capstone guardrail; the number is a new policy choice. **PARTIAL** | US3 AS5 | SC-004–005 | Unverifiable |
| FR-012 | `original_idea.md` §7 lines 187–195 and Constitution VII lines 33–36 explicitly require labels outside prediction/investigation inputs and protect the holdout. **FULL** | US3 AS2; US5 AS1–2 | SC-005, SC-007 | Unverifiable |
| FR-013 | `original_idea.md` §7 lines 170–183 says to bound candidates and AutoML; §7 lines 187–192 defines time split and preprocessing. Freezing seed, subpartitions, tie-breaks and K is additional protocol detail. **PARTIAL** | US3 AS2–3 | SC-004–005 | Unverifiable |
| FR-014 | The idea supports validation-only selection, calibration care, and explainability (§7 lines 181–190, 203–205); the precise AP/P@K/tie-break and calibration rules are further decisions. **PARTIAL** | US3 AS2–3 | SC-004–005 | Unverifiable |
| FR-015 | `original_idea.md` §7 lines 187–192 says not to tune on test; Constitution VII lines 33–36 prohibits holdout tuning. Treating a consumed holdout as no longer unseen is a necessary elaboration. **FULL** | US3 AS3–4 | SC-004–005 | Unverifiable |
| FR-016 | The idea requires repeatable evaluation and comparisons (§2 lines 29–41; §7 lines 170–192), but the exact listed metrics, K semantics, stable tie order and Brier diagnostics are not prescribed there. **PARTIAL** | US3 AS4 | SC-004 | Unverifiable |
| FR-017 | `original_idea.md` §3.1 lines 55–59 and §7 lines 193–195 require honest synthetic-data limitations; Constitution V and IX require verifiable claims and honest evidence. **FULL** | US3 AS4–5 | SC-004, SC-009 | Unverifiable |
| FR-018 | Reproducibility is explicit in `original_idea.md` §2 lines 29–41 and Constitution IX lines 43–46. Trusted-artifact loading and exact local artifact policy are design details that still need technical definition. **PARTIAL** | US3 AS2–4; US4 AS1 | SC-004, SC-009 | Unverifiable |
| FR-019 | `original_idea.md` §4 lines 106–120 explicitly requires model contributions and checkable facts; Constitution V requires evidentiary support. **FULL** | US4 AS1–3 | SC-006 | Unverifiable |
| FR-020 | `original_idea.md` §4 lines 116–120 prohibits unsupported facts and distinguishes case evidence from procedural sources; Constitution IV–V prohibits LLM-created facts. **FULL** | US4 AS2–4 | SC-006 | Unverifiable |
| FR-021 | `original_idea.md` §5 lines 128–155 supports versioned scoring-to-case delivery; §6 line 166 says one alert per transaction. Stable run publication and restart reproduction elaborate that boundary. **PARTIAL** | US5 AS1–3 | SC-006–007 | Unverifiable |
| FR-022 | A bounded review interface fits the local capstone, but the **100-alert limit**, ordering and truncation contract have no direct source in the idea or constitution. The cap is an unsupported numeric product choice. **UNSUPPORTED as written** | US5 AS2–3 | SC-007 | Unverifiable |
| FR-023 | Constitution II and VIII and `docs/decisions/foundation.md` lines 114–129 require reviewed, versioned contract migration and coordinated consumer changes. Feature 001 schemas impose fixed three-digit IDs and two-decimal amounts (`schemas.json` lines 6–45, 93–117). **FULL** | US1 AS3; US5 AS4–5 | SC-008 | Unverifiable |
| FR-024 | Constitution VIII requires fixture/rules/model distinction; `docs/decisions/fixture-scoring.md` lines 18–48 says fixture scores are illustrative, not AML scores or probabilities. **FULL** | US4 AS1; US5 AS4 | SC-003, SC-007–008 | Unverifiable |
| FR-025 | The idea’s scorer boundary allows fixture/rules before a model and later replacement (§5 lines 151–155); Constitution VIII requires replaceable adapters. Explicit no-fallback behavior is a compatible integrity safeguard. **PARTIAL** | US4 AS4; US5 AS5 | SC-003, SC-007 | Unverifiable |
| FR-026 | Constitution II–III, IX–X and `original_idea.md` §10 lines 223–239 require specification/task traceability, test-first behavior, evidence and human review. **FULL** | Cross-cutting; US1–US5 | SC-001–009 | Unverifiable |

## 2. Success criteria review

Every SC below is measurable as written, but the acceptance condition is **not yet verified**: the feature has no implementation or execution evidence. “Evidence” describes what would be needed to verify it.

| SC | Corresponding FRs | Measurability / independent verification | Feasibility and evidence needed |
|---|---|---|---|
| SC-001 | FR-001–004, 026 | Clear 100% row accounting and zero duplicate identities; testable with a fixed source sample and repeat import. | Feasible. Needs acquired-source manifest/hash, import report, and test results for rejected rows, precision, banks, currencies and duplicate cases. |
| SC-002 | FR-005–007, 026 | “Zero unintended changes” is testable, but the expected feature definitions and exact temporal semantics must first be frozen. | Feasible on hand-checked timelines. Needs feature catalog, fixtures, perturbation tests for future rows/labels/ties, and rule output evidence. |
| SC-003 | FR-007–009, 024–025 | Distinct sources and a model assessment versus fixture constants are objectively inspectable. | Rules are feasible independently. Model condition depends on valid artifacts and successful training; evidence must show rule/model modes separately and no fallback. |
| SC-004 | FR-010–011, 013–018 | Metrics, counts and repeatability have measurable outputs; “within a predeclared numeric tolerance” is incomplete until the tolerance and determinism scope are chosen. | Feasible only if data eligibility, dependencies and compute permit. Needs frozen protocol, run manifests, metrics, versions, seeds, predictions and independent rerun comparison. |
| SC-005 | FR-006, 010, 012–015 | Leakage checks and holdout separation are testable, but exact permitted label joins, time cutoffs and evaluator access boundaries need operational definition. | Feasible with split manifests, feature lineage, label-access tests and evidence that holdout results did not affect selection. |
| SC-006 | FR-019–021, 026 | Matching IDs, supported/unavailable explanations and five independently checked samples are countable. The “predeclared label-free sampling rule” must be specified before choosing examples. | Feasible. Needs review records identifying reviewer/date, selected sample rule and factual/method comparison; no test-label-based selection. |
| SC-007 | FR-021–025 | Bounded snapshot, list/detail match, label exclusion, empty and missing-artifact states are objectively testable. | Feasible after contract/UI design. Needs API/UI tests, payload label scans, provenance checks and failure-state evidence. |
| SC-008 | FR-023–026 | Existing fixture regression and large-value boundary conditions are explicit. | Feasible, but contract migration is pending. Needs foundation regression results and tests proving identifiers, precision and currency values survive the new contract. |
| SC-009 | FR-001, 010–018, 026 | Another teammate reproduction is independently observable. “Without conversation history” is clear in intent, but required commands/environment prerequisites must be documented. | Feasible if licensed data and local compute are available. Needs a second-person run record with source version, commands, environment, outputs and limitations. |

**Scientific feasibility note:** IBM documents the dataset as synthetic and distinguishes the data license (CDLA-Sharing-1.0) from the repository’s Apache-2.0 license. The specification correctly requires inspecting the actual acquired release rather than assuming paper counts. The paper’s published HI-Small summary differs from later circulated file counts; this supports FR-001/002’s provenance and audit requirements. [IBM AML-Data README](https://github.com/IBM/AML-Data/blob/main/README.md), [dataset authors’ paper](https://arxiv.org/html/2306.16424v2).

## 3. Missing requirements

These are traceability or specification gaps, not claims that the feature must expand in scope:

1. **The Phase 2 requirements source is missing.** Provide the exact file or authoritative source and version before claiming Phase 2 coverage. The current quality checklist is not a substitute.
2. **Bootcamp module/rubric mapping is not auditable.** `original_idea.md` §2 identifies Module 2 evidence as API contracts and integration tests, but says the detailed official scoring rubric was not provided. The feature spec should not claim full course compliance without that rubric or mentor confirmation.
3. **Exact source semantics remain unverified.** The spec says this work is future data audit (lines 370–372), but before planning implementation it needs observed column names, types, nullability, timestamp timezone/granularity, label semantics and exact file/release identity.
4. **Acceptance evidence is not fully operationalized.** SC-004’s numeric tolerance, SC-006’s sampling rule, SC-009’s reproduction environment/commands, and FR-011’s 20-positive rule need decisions before corresponding runs.
5. **Scored-run atomicity and recovery need a concrete contract.** The spec prohibits partial publication and mentions interrupted runs/stale assessments, but does not define run states, commit boundary, recovery, or how readers distinguish a completed run from an interrupted one.
6. **Risk-score semantics and threshold behavior need one canonical definition.** The spec distinguishes scores from probabilities, but implementation planning must define whether the rule score and model score share a scale, how thresholds apply across sources, and how the UI labels each.
7. **History warm-up and evaluation windows need reconciliation.** The one-day lookback default and “available coverage” are present, but the relationship between warm-up rows, benchmark eligibility, split boundaries and reported denominators must be specified.

## 4. Partially specified or unsupported requirements

The spec is detailed, but several requirements still lack enough operational definition for objective implementation:

- **FR-002:** “Structural ambiguity blocks import” needs an explicit list of blocking conditions versus reportable row-level errors.
- **FR-005/006:** Feature definitions, precise aggregation windows, missing-history semantics, and visibility scope remain future planning decisions. The strict-timestamp tie policy is clear; the overall feature catalog is not yet written.
- **FR-007:** “Documented thresholds,” score construction and cold-start behavior are required, but no baseline rules or score mapping are defined.
- **FR-011:** The ≥20 positive examples per validation/test partition is labeled a guardrail, not statistical adequacy, but no rationale or fallback decision owner is given. It may block the named dataset view.
- **FR-013/014:** Candidate algorithms, numeric AP tie tolerance, calibration procedure, threshold tie policy and exact training/search budget remain unset.
- **FR-016/SC-004:** Repeatability tolerance and whether comparisons are row-level prediction equality or metric-only agreement are not fixed.
- **FR-018:** “Trusted local artifacts” does not define how artifact provenance/trust is established. Avoid arbitrary user-uploaded artifacts, but specify the local boundary and validation.
- **FR-021:** “Completed scored run” and restart reproducibility need an explicit persistence/run lifecycle contract.
- **FR-022:** The 100-alert cap lacks a stated basis. It is a new application behavior, not derived from a source requirement.
- **FR-026:** “Original prompts” and human review are required by governance, but the precise evidence checklist and approver recording format should be defined by the project conventions.

These items may properly be decided during planning, as the spec says (lines 365–369, 413–415), but they are not implementation-ready details yet.

## 5. Contradictions and terminology needing resolution

1. **No demonstrable Phase 2 conflict check is possible.** The requested requirements file is absent; any claim of consistency with it would be invented.
2. **FR-011 introduces a new numeric eligibility gate.** The idea says to check that there are enough positives, without setting 20. The spec calls 20 a capstone guardrail, so this is not a direct governance conflict, but it needs approval or an explicit rationale before experiments.
3. **FR-022 introduces an arbitrary 100-alert display cap.** It may be a reasonable capstone simplification, but neither the approved idea nor governing source sets that number. The original idea’s “30 cases” is an example for a later simulation question, not support for a 100-alert UI cap.
4. **Feature 001 is not dataset-compatible without reviewed migration.** Foundation v1 requires `TX-###`/`CASE-###`, UTC-Z timestamps, a single amount with exactly two decimals, one currency, and closed response objects. Feature 002 needs source-qualified identities, separate paid/received amounts and currencies, precision preservation and richer provenance. FR-023 correctly flags migration; this cannot be treated as backward-compatible by default.
5. **Fixture, rules, model, risk score, and probability must remain distinct.** The current fixture scorer uses ID-derived illustrative constants and copies the event timestamp into `scored_at`; it is explicitly not an AML rule or probability (`fixture-scoring.md` lines 18–48). Feature 002 correctly identifies this difference in FR-008/024. The final contract/UI must preserve it.
6. **“Dataset-backed” is not the same as label-free ingestion.** Training/evaluation requires labels, while operational features, scoring, explanations, cases and UI must not expose target labels. FR-012 and US5 distinguish these roles, but the planned data model must make the boundary explicit.
7. **History updates after a held-out event need a precise event-time rule.** FR-006 permits a held-out event’s unlabeled facts to enter later history after its event time passes. The implementation must ensure no same-time event or label enters, and must state whether this is simulated online replay or static offline feature generation.
8. **Approximate dataset facts are not authoritative source facts.** `original_idea.md` cites roughly five million rows and calls for verifying the acquired file. IBM’s README and dataset paper describe a synthetic benchmark; actual release counts and schemas must come from the acquired artifact’s manifest/audit, not copied assumed values.

## 6. Recommended exact additions or revisions

These are proposed edits only; no files were changed.

1. **Add the Phase 2 source to the repository or identify its authoritative location.** Record title, version/date and exact file. Add a mapping table with each source requirement ID, exact location, Feature 002 FR, AS and SC, and status. Until then, label Phase 2 coverage “not assessed.”
2. **Resolve FR-011 before the plan freezes the evaluation protocol.** Either retain “20 positives” with a named rationale/decision record and explicit behavior when ineligible, or change it to “predeclare an adequacy rule and report insufficient evidence when unmet,” without inventing a numeric gate.
3. **Resolve FR-022.** Either justify the 100-alert limit as an approved local-demo bound and define truncation/count semantics, or make the bound a planning decision based on observed runtime and keep the acceptance condition as a configurable, disclosed bound.
4. **Add a normative “label roles and access” table.** For each pipeline stage—import, feature generation, fitting, validation, test evaluation, explanations, case publication, UI—list permitted label access and output fields. This will make FR-012, FR-020, FR-021 and SC-005/007 independently auditable.
5. **Define failure/publication lifecycle.** Add run states and transitions such as `created → validating → scoring → completed` or `failed`; specify when results become visible, whether a failed run can leave prior active results intact, and how replay identifies its exact artifacts.
6. **Define score semantics before app migration.** State whether model scores are raw ranking scores or probabilities, whether rules are ordinal/bounded risk scores, which threshold belongs to which scorer version, and how the UI labels them. Keep fixture source explicitly illustrative.
7. **Add objective evidence requirements to the planning artifacts.** Freeze tolerance and comparison level for SC-004; predeclare label-free sample selection for SC-006; document exact commands, dependencies and source prerequisites for SC-009.
8. **Keep FR-023 as a hard migration gate.** Update the canonical Feature 001 API/schema and all validators/decoders only through reviewed, versioned contract changes with negative and regression tests. Do not silently widen v1 or map distinct currency/precision fields into its single amount field.
9. **Correct the quality checklist after this review.** In particular, its claims that all requirements are testable and no critical choices remain (checklist lines 17–32) are too strong while rules, source schema, eligibility threshold, tolerance and run lifecycle are undefined. Its own lines 50–53 correctly state that no implementation or human review has occurred.

## 7. Final coverage calculation

**Phase 2 coverage is N/A**, not zero and not 100%: no Phase 2 requirements source or denominator was present in the repository. The only phase-related statement available in `original_idea.md` says the formal rubric was not supplied.

For the requested reverse trace, I classified each of the 26 FRs against the available project-goal/governance documents:

- FULL: 17
- PARTIAL: 8
- UNSUPPORTED: 1 (FR-022’s exact 100-alert bound)
- CONFLICTING with available governance: 0

Conservative full-only traceability: **17 ÷ 26 = 65.4%**.
Weighted traceability, counting PARTIAL as 0.5: **(17 + 8×0.5) ÷ 26 = 80.8%**.

These percentages are judgments about documented source links, not implementation completion. No acceptance test, data audit, trained model, UI behavior or teammate reproduction was verified in this audit.



question
Act as a Principal Requirements Engineer, Senior ML Architect, and independent Technical Reviewer.
You have just completed the first adversarial specification audit of Feature 002: Data Ingestion and Risk Scoring.
Your review identified:
- H1: Undefined rule-based baseline behavior
- H2: Label validity potentially affecting event history
- H3: Ambiguous temporal and warm-up semantics
- M1: Ambiguous alert threshold policy
- M2: Undefined uncertainty reporting
- M3: Incomplete atomic publication semantics
- M4: Undefined model artifact trust verification
- M5: Overstated specification checklist readiness
- M6: Undefined local resource constraints
I want a SECOND-LEVEL REVIEW of those findings.
Do not assume your first review was completely correct.
STEP 1 — VALIDATE THE FINDINGS
Reread:
- Feature 002 spec.md
- Its quality checklist
- original_idea.md
- Project constitution
- Feature 001 specifications and contracts
- Existing architecture and implementation
- Any available Phase 2 requirements document
For each finding:
1. Verify whether the issue genuinely exists.
2. Identify existing requirements that partially address it.
3. Determine whether it is a real specification defect.
4. Determine whether it belongs in the technical plan.
5. Identify whether a human decision is required.
6. Consider the smallest possible correction.
7. Reassess severity independently.
Do not repeat the original findings uncritically.
STEP 2 — VERIFY PHASE 2 REQUIREMENTS
Your first audit reported that a standalone Phase 2 requirements.md was missing.
Search the repository, accessible documentation, and relevant references again.
Distinguish:
- Feature 002 quality checklist requirements.md
- An actual Phase 2 assignment requirements.md
- Feature 001 Phase 2 handoff documentation
- Requirements contained in original_idea.md
Do not treat the specification checklist as the official Phase 2 assignment.
If the authoritative requirements are unavailable, report that clearly. Do not invent rubric requirements or claim compliance.
STEP 3 — PROPOSE PRECISE CORRECTIONS
For each confirmed issue, provide:
- Existing requirement ID
- Exact current wording
- Proposed revised wording
- Reason for the change
- New acceptance criteria if necessary
- Whether the proposed change introduces new scope
- Whether it conflicts with another requirement
Pay special attention to:
A. A meaningful deterministic label-free rules baseline.
B. Separation of valid observable transaction facts from supervised-label eligibility.
C. Temporal cutoffs, timestamp assumptions, tied timestamps, historical coverage, and warm-up handling.
D. A reproducible alert operating-point policy that preserves the possibility of genuine zero-alert outcomes.
E. Defensible uncertainty and evaluation limitations.
STEP 4 — AVOID OVERENGINEERING
Do not introduce:
- Distributed systems
- Streaming infrastructure
- Cloud infrastructure
- Model registry platforms
- New complex ML architectures
- Additional application screens
- New LLM or RAG features
- Unnecessary frameworks
- Enterprise-only operational requirements
Keep the existing educational capstone scope.
Do not move technical implementation details into the product specification unless they define essential observable behavior.
STEP 5 — CLASSIFY ALL PROPOSED CHANGES
Use these categories:
A. REQUIRED BEFORE PLANNING
B. REQUIRED DURING PLANNING
C. OPTIONAL IMPROVEMENT
D. ALREADY SUFFICIENTLY COVERED
E. REJECT / OVERENGINEERING
STEP 6 — CHECK CONSISTENCY
Ensure proposed corrections do not contradict:
- FR-001 through FR-026
- SC-001 through SC-009
- Existing acceptance scenarios
- Existing project constraints
- Feature 001 compatibility requirements
- Temporal and label-leakage protections
STEP 7 — OUTPUT
Produce:
1. Validated findings matrix
2. Reclassified severity and priority
3. Exact proposed specification edits
4. Additional acceptance scenarios
5. Technical planning decisions to defer
6. Open human decisions
7. Unnecessary recommendations to discard
8. Recommended minimum patch set
9. Revised readiness assessment
IMPORTANT:
Do not modify any files yet.
Do not implement code.
Do not download datasets.
Do not train any models.
Do not mark any tests as passed.
Do not invent observed dataset characteristics.
I want to approve a minimal, evidence-based change set before the specification is edited.


asnwer
# Second-level review: Feature 002

**No files were changed, no code or tests were run, and no dataset was downloaded.** I reread the current Feature 002 spec and checklist, project handoff, original idea, constitution, Feature 001 contracts and decisions, and the relevant implementation and tests.

## 1. Validated findings matrix

| Finding | Does it genuinely exist? | Existing coverage and gap | Reassessed severity / disposition |
|---|---|---|---|
| **H1 — Undefined rule baseline** | **Yes, as a product-spec gap.** US2 promises a “meaningful comparison baseline” and a hand-checkable test (spec lines 48–56); FR-007 requires deterministic rules, thresholds, bounded score, reasons and cold-start behavior (lines 214–216). But it does not say what data the rules use or prevent an arbitrary, non-meaningful rule from satisfying the requirement. The existing implementation’s “rules scorer” is explicitly test-only and illustrative; it is not an AML baseline (`backend/tests/unit/test_scoring_boundary.py`, `docs/decisions/foundation.md` lines 70–76). | FR-007 and SC-003 partially address this; neither requires a rule set based on observable transaction/history features rather than labels or identifiers. The exact rules and numeric thresholds belong in the plan, but the spec should define what qualifies as a baseline. | **HIGH. A — Required before planning.** Otherwise it is possible to plan a baseline that is technically deterministic but scientifically meaningless. |
| **H2 — Label validity affecting event history** | **Yes, as a real leakage/selection risk.** FR-006 says exclude target labels, and SC-002 requires label perturbations not to change earlier features/rule scores. But the spec does not distinguish a transaction’s observable facts from whether its target label is valid for supervised learning. If an invalid or missing label causes the entire event row to be rejected, later history can change based on label validity. | FR-002 accounts for source rows and lists invalid labels as an edge case; FR-012 separates label roles. They do not specify that a structurally valid event can remain available for label-free history when its label is missing/invalid. | **HIGH. A — Required before planning.** Clarify event-fact inclusion separately from supervised-label eligibility. |
| **H3 — Temporal and warm-up semantics** | **Partially.** Spec already requires strictly earlier timestamps, exclusion of timestamp ties, whole timestamp groups in splits, preserved timezone assumptions, a default one-day lookback and a declared coverage/warm-up interval (FR-003, FR-006; assumptions lines 370–382). It also lists missing timezone, ties and incomplete history as edge cases. So the original finding overstated the absence of temporal rules. | The actual source timezone/granularity is intentionally unknown until the data audit. The meaning of one-day lookback at boundaries, timezone normalization, cutoff representation, and how warm-up rows affect partitions/denominators remain unresolved. These depend on observed data and belong primarily in planning. | **MEDIUM. B — Required during planning.** No broad spec rewrite needed; make the plan resolve exact timestamp and coverage semantics and add acceptance coverage for incomplete history. |
| **M1 — Alert threshold ambiguity** | **Partially.** FR-013 freezes K and a threshold procedure; FR-014 says threshold tuning is validation-only; US5 AS2 and an edge case explicitly allow zero alerts. The assumption sets K to 20 and permits fewer alerts when ties prevent an exact count (lines 383–387). The spec does not, however, state how a threshold is selected or clearly distinguish a threshold policy from top-K retrieval. | Existing coverage already preserves zero-alert outcomes and prohibits label-based selection. The missing point is a predeclared deterministic threshold-selection rule; “at most 20” alone does not determine one. | **MEDIUM. A — Small clarification before planning.** Say no minimum alert count is required and define the operating-point rule in the plan. |
| **M2 — Uncertainty reporting** | **Partially.** FR-011 requires “uncertainty limits”; FR-017 requires evaluation limitations; FR-020 distinguishes uncertainty from observed facts/contributions. The spec does not say what the report must do when uncertainty is not quantified. | These requirements already prohibit overclaiming in principle. The gap is whether uncertainty means a quantitative estimate or a candid limitation statement, and how absence of a reliable estimate is reported. A particular statistical method should be a planning decision, not invented in the spec. | **MEDIUM. A — Clarify report behavior before planning; B — choose any estimation method during planning.** Require explicit reporting without mandating confidence intervals or a specific technique. |
| **M3 — Atomic publication semantics** | **No material product-spec defect confirmed.** FR-009 forbids partial publication; FR-021 says publish a completed run; US5 AS3 requires repeated/concurrent runs not to create list/detail disagreement. | Observable behavior is covered. The internal mechanism for achieving it—such as a local single-user completed-run pointer or snapshot swap—is an implementation/planning decision. | **LOW. D/B — Already sufficiently covered behaviorally; decide the simplest mechanism during planning.** Do not add distributed transactions or service infrastructure. |
| **M4 — Artifact trust verification** | **Not a major spec gap.** FR-018 requires trusted local artifacts, versioned metadata and hashes, and rejects arbitrary user uploads. | The desired boundary is present; how the local loader checks the artifact against recorded metadata is not. That is a technical plan/contract detail. | **LOW. D/B — Keep the requirement; specify local hash/provenance checks during planning.** No model registry or external artifact service. |
| **M5 — Checklist readiness overstatement** | **Yes, a documentation inconsistency.** Checklist lines 17 and 48 claim defaults/planning decisions are explicit and no critical questions remain, while lines 50–53 say numeric planning settings and source schema/counts remain future work and human review is pending. | The checklist correctly says it does not mean the feature works. But the “no critical unresolved” wording is too strong given FR-007’s unspecified baseline behavior and the threshold/label-history clarifications above. | **LOW. A — Revise checklist wording alongside spec changes.** Do not mark it as human-approved or implementation-complete. |
| **M6 — Local resource constraints** | **Mostly no.** FR-017 requires reporting actual resource conditions; assumptions require local operation and timeboxed training, and dependencies require permitted local compute (lines 388–408). No performance SLA is promised. | The plan still needs a feasible processing/training budget based on the actual environment. That is an execution planning issue, not a reason to add a product-level runtime or memory guarantee. | **LOW. B/D — Document observed hardware, timebox and any reduced training view in the plan/report.** Do not add infrastructure or hard caps without evidence. |

## 2. Phase 2 source verification

The repository search found:

- `specs/002-data-and-risk-scoring/checklists/requirements.md`: Feature 002’s **quality checklist**, not a course assignment.
- `specs/001-project-foundation/tasks.md`: a heading “Phase 2: Foundational (Blocking Prerequisites)” for Feature 001 workflow stages, not the Bootcamp’s Phase 2 requirements.
- `original_idea.md` §2: a summary of course modules and evidence expectations. It explicitly says the detailed official assessment rubric was not supplied (lines 25–27).
- No standalone Phase 2 assignment `requirements.md` or referenced course PDF was found in the repository.

The public SITA page describes the Bootcamp curriculum, including Python/API fundamentals, but I found no Feature 002-specific or Phase 2 assignment requirements there. It cannot substitute for the missing rubric. [SITA AI Bootcamp curriculum](https://sita.org.rs/ai-bootcamp/)

**Conclusion:** authoritative Phase 2 assignment requirements remain unavailable. I cannot establish compliance or report a Phase 2 coverage percentage. The Feature 001 “Phase 2” handoff and Feature 002 checklist must not be treated as that source.

## 3. Exact proposed specification edits

These are proposed wording only; I have not applied them.

### A. Required before planning

**1. FR-007 — define what qualifies as a meaningful rules baseline**

Current wording:

> “Provide a versioned deterministic rule baseline with documented thresholds, finite bounded score, triggered reasons and cold-start behavior, usable before ML exists. Changing only labels or future events MUST NOT alter its prior features or scores.”

Proposed wording:

> “Provide a versioned deterministic rule baseline usable before ML exists. Rules MUST use only label-free observable transaction facts and permitted historical features; transaction, account, case, source-row and target-label identifiers MUST NOT determine a rule outcome. Each rule MUST have a documented condition, threshold, score or score contribution, reason, and cold-start behavior. The concrete rule set and numeric values MUST be fixed before evaluation. The result MUST identify the rule version and actual triggered conditions. Changing only labels or future events MUST NOT alter prior features or rule scores.”

**Reason:** it makes the baseline meaningfully tied to observable risk indicators while leaving rule design and numeric thresholds to the plan.
**New scope:** no; this narrows implementation to the already promised rules baseline.
**Conflict:** none identified.

**2. FR-002 / FR-006 — separate observable event facts from label eligibility**

Add to FR-002 after its row-accounting requirement:

> “For a source row whose required event fields are valid but whose target label is missing or invalid, report the label as ineligible for supervised use separately from event-row validity. Do not discard otherwise valid label-free event facts from operational history solely because of target-label validity. Exclude the label itself from operational projections and scoring.”

Add to FR-006:

> “Supervised-label eligibility MUST NOT determine whether otherwise valid, label-free event facts are available to historical features. Training and evaluation eligibility is recorded separately from event-fact availability.”

**Reason:** prevents labels from indirectly controlling feature history through row filtering. Invalid event facts may still be rejected; this change concerns valid event facts with unavailable or invalid labels.
**New scope:** no; it clarifies existing label isolation and history requirements.
**Conflict:** none identified. It reinforces FR-012 and SC-005. Update row-accounting definitions so event acceptance and label eligibility are not conflated.

**3. FR-014 / acceptance scenario — preserve a genuine zero-alert outcome**

Add to FR-014:

> “The frozen threshold procedure MUST use validation data only and MUST NOT require at least one alert. A zero-alert result is valid when no score meets the predeclared operating-point rule. Fixed-budget Precision@K/Recall@K rankings are reported separately from threshold-generated alerts.”

Add a scenario to US3 or US5:

> “Given a frozen validation-only threshold procedure and a scoring population in which no event meets its rule, when the run is evaluated and published, then zero alerts are reported, the empty review state is shown, and no alert is manufactured to fill K.”

**Reason:** existing language already permits zero alerts, but the rule must not silently become “always select the top K.” The plan can choose the exact threshold method.
**New scope:** no; it makes existing zero-alert and threshold requirements consistent.
**Conflict:** none with FR-013, FR-016, US5 AS2 or the K cap, provided top-K metrics remain distinct from threshold alerts.

**4. FR-011 — make uncertainty reporting observable without mandating a method**

Replace “Report exact counts and uncertainty limits” with:

> “Report exact counts and state the uncertainty or evaluation limitations relevant to interpreting the result. If uncertainty is not quantitatively estimated, say so and explain the limitation; do not imply statistical precision that was not measured.”

**Reason:** “uncertainty limits” alone is not an objectively verifiable reporting behavior.
**New scope:** no; it sets a reporting honesty requirement, not a statistical method.
**Conflict:** none with FR-017 or the educational scope.

### B. Required during planning

**5. Temporal and warm-up semantics — no broad spec edit proposed.**

Resolve in the plan using the observed source characteristics:

- Timestamp parsing and any timezone assumption; reject or explicitly handle absent/ambiguous timezone data rather than silently assigning one.
- Exact feature cutoff: strictly earlier event time, with all tied timestamps receiving the same earlier-history snapshot.
- Meaning of the one-day lookback and its boundary convention.
- Coverage/warm-up representation and how rows lacking full history are treated in each partition and denominator.
- Whether history is replayed in event-time order and how held-out event facts enter later history without labels.

Add one plan-level acceptance case: an event with incomplete prior coverage and an equal-time peer must receive the documented coverage state and must not include the peer or later events in its history.

**Reason:** actual timestamp precision and timezone behavior are not yet observed. Choosing those in the product spec before the audit risks inventing data facts.
**New scope:** no.

**6. Atomic publication and artifact verification — plan details only.**

For M3, define the smallest local completion behavior: readers see either the previous completed snapshot or the new completed snapshot; incomplete runs are not published. Specify the restart and repeated-run check.

For M4, require the plan to define a local artifact manifest and verify recorded hashes before use. Keep artifacts local/ignored as already specified. No registry, cloud store, or user-upload feature.

**Reason:** desired behavior is already present; implementation mechanics are not.
**New scope:** no.

**7. Resource limits — plan/report only.**

Record the machine/runtime actually used, execution time, memory or other resource facts available, and any reduced training view. Decide a timebox before model experimentation. Do not promise full-scale interactive processing or add a hard runtime SLA without evidence.

**Reason:** FR-017 and the local-compute dependency already require honest reporting.
**New scope:** no.

### C. Checklist wording

Replace checklist line 17’s “defaults and planning decisions are explicit” with:

> “Product-level defaults and unresolved choices needed before planning are explicit; remaining technical decisions are identified for the plan.”

Replace line 48’s “No critical unresolved product questions were found” with:

> “The specification has outstanding decisions listed for the technical plan; human product review is pending.”

**Reason:** align the checklist’s readiness claims with its own lines 50–53 and with the FR-007/M1 clarifications.
**New scope:** none.

## 4. Classification of recommendations

| Category | Recommendation |
|---|---|
| **A. REQUIRED BEFORE PLANNING** | Clarify what constitutes a meaningful label-free rules baseline; separate event-fact validity from label eligibility; explicitly preserve zero-alert outcomes and distinguish threshold alerts from top-K metrics; make uncertainty reporting objectively checkable; correct checklist readiness wording. |
| **B. REQUIRED DURING PLANNING** | Resolve actual timestamp/timezone/lookback/warm-up semantics after data audit; choose the concrete threshold procedure using validation only; select any uncertainty estimation method or state that none is used; specify minimal local atomic publication, hash verification and resource/timebox evidence. |
| **C. OPTIONAL IMPROVEMENT** | Add a compact label-role table by pipeline stage if FR-002/006/012 wording still leaves implementers unsure. This is helpful, but the minimal edits above may suffice. |
| **D. ALREADY SUFFICIENTLY COVERED** | No partial publication; completed-run-only publication; local artifacts and hashes; zero-alert empty state; label-free feature constraints in principle; reporting actual resource conditions. These need planning detail, not new product scope. |
| **E. REJECT / OVERENGINEERING** | Distributed or streaming systems, cloud infrastructure, model registry, additional application screen, hard production SLAs, complex statistical infrastructure, or new ML/RAG/LLM capabilities. None is justified by the findings. |

## 5. Consistency and minimum patch set

The proposed edits preserve the current FR/SC structure and project boundaries. They do not alter the fixture contract or authorize implementation. The contract migration remains governed by FR-023 and Feature 001’s review process; Feature 001 currently uses fixed three-digit IDs, UTC-Z timestamps and a single two-decimal amount, so dataset compatibility still requires explicit reviewed migration.

**Recommended minimum patch set before planning:** update FR-007; clarify FR-002 and FR-006; add the no-forced-alert condition to FR-014 and an acceptance scenario; clarify FR-011 uncertainty reporting; correct checklist lines 17 and 48. Defer timestamp interpretation, run publication mechanics, artifact hash procedure, and local resource budgets to the plan.

## 6. Open human decisions

1. What observable transaction/history indicators should the baseline rules represent? The plan can propose concrete rules, but the team should review them before evaluation.
2. Should valid event facts with missing/invalid labels remain available for label-free historical context? The proposed minimal correction says yes, while excluding those labels from supervised use.
3. What validation-only operating-point objective should determine the alert threshold? The requirement should permit zero alerts and keep top-K retrieval metrics separate.
4. Is the team satisfied with reporting uncertainty limitations when a quantitative estimate is not defensible, rather than requiring confidence intervals?

## 7. Revised readiness

**READY WITH CHANGES for technical planning after the minimum patch set.** The first review overstated several findings: temporal behavior, zero-alert handling, partial publication, artifact locality/hash tracking, and resource reporting already have meaningful coverage. The material spec gaps are narrower: what makes the rules baseline meaningful, whether label eligibility can remove observable events from history, how to make the alert operating point reproducible without forcing alerts, and what uncertainty reporting must say. The authoritative Phase 2 assignment requirements remain unavailable, so course-specific compliance remains unassessed.

Act as a Principal Requirements Engineer, Senior ML Architect, and independent Technical Reviewer.
You have just completed the first adversarial specification audit of Feature 002: Data Ingestion and Risk Scoring.
Your review identified:
- H1: Undefined rule-based baseline behavior
- H2: Label validity potentially affecting event history
- H3: Ambiguous temporal and warm-up semantics
- M1: Ambiguous alert threshold policy
- M2: Undefined uncertainty reporting
- M3: Incomplete atomic publication semantics
- M4: Undefined model artifact trust verification
- M5: Overstated specification checklist readiness
- M6: Undefined local resource constraints
I want a SECOND-LEVEL REVIEW of those findings.
Do not assume your first review was completely correct.
STEP 1 — VALIDATE THE FINDINGS
Reread:
- Feature 002 spec.md
- Its quality checklist
- original_idea.md
- Project constitution
- Feature 001 specifications and contracts
- Existing architecture and implementation
- Any available Phase 2 requirements document
For each finding:
1. Verify whether the issue genuinely exists.
2. Identify existing requirements that partially address it.
3. Determine whether it is a real specification defect.
4. Determine whether it belongs in the technical plan.
5. Identify whether a human decision is required.
6. Consider the smallest possible correction.
7. Reassess severity independently.
Do not repeat the original findings uncritically.
STEP 2 — VERIFY PHASE 2 REQUIREMENTS
Your first audit reported that a standalone Phase 2 requirements.md was missing.
Search the repository, accessible documentation, and relevant references again.
Distinguish:
- Feature 002 quality checklist requirements.md
- An actual Phase 2 assignment requirements.md
- Feature 001 Phase 2 handoff documentation
- Requirements contained in original_idea.md
Do not treat the specification checklist as the official Phase 2 assignment.
If the authoritative requirements are unavailable, report that clearly. Do not invent rubric requirements or claim compliance.
STEP 3 — PROPOSE PRECISE CORRECTIONS
For each confirmed issue, provide:
- Existing requirement ID
- Exact current wording
- Proposed revised wording
- Reason for the change
- New acceptance criteria if necessary
- Whether the proposed change introduces new scope
- Whether it conflicts with another requirement
Pay special attention to:
A. A meaningful deterministic label-free rules baseline.
B. Separation of valid observable transaction facts from supervised-label eligibility.
C. Temporal cutoffs, timestamp assumptions, tied timestamps, historical coverage, and warm-up handling.
D. A reproducible alert operating-point policy that preserves the possibility of genuine zero-alert outcomes.
E. Defensible uncertainty and evaluation limitations.
STEP 4 — AVOID OVERENGINEERING
Do not introduce:
- Distributed systems
- Streaming infrastructure
- Cloud infrastructure
- Model registry platforms
- New complex ML architectures
- Additional application screens
- New LLM or RAG features
- Unnecessary frameworks
- Enterprise-only operational requirements
Keep the existing educational capstone scope.
Do not move technical implementation details into the product specification unless they define essential observable behavior.
STEP 5 — CLASSIFY ALL PROPOSED CHANGES
Use these categories:
A. REQUIRED BEFORE PLANNING
B. REQUIRED DURING PLANNING
C. OPTIONAL IMPROVEMENT
D. ALREADY SUFFICIENTLY COVERED
E. REJECT / OVERENGINEERING
STEP 6 — CHECK CONSISTENCY
Ensure proposed corrections do not contradict:
- FR-001 through FR-026
- SC-001 through SC-009
- Existing acceptance scenarios
- Existing project constraints
- Feature 001 compatibility requirements
- Temporal and label-leakage protections
STEP 7 — OUTPUT
Produce:
1. Validated findings matrix
2. Reclassified severity and priority
3. Exact proposed specification edits
4. Additional acceptance scenarios
5. Technical planning decisions to defer
6. Open human decisions
7. Unnecessary recommendations to discard
8. Recommended minimum patch set
9. Revised readiness assessment
IMPORTANT:
Do not modify any files yet.
Do not implement code.
Do not download datasets.
Do not train any models.
Do not mark any tests as passed.
Do not invent observed dataset characteristics.
I want to approve a minimal, evidence-based change set before the specification is edited.


# Second-level review: Feature 002

**No files were changed, no code or tests were run, and no dataset was downloaded.** I reread the current Feature 002 spec and checklist, project handoff, original idea, constitution, Feature 001 contracts and decisions, and the relevant implementation and tests.

## 1. Validated findings matrix

| Finding | Does it genuinely exist? | Existing coverage and gap | Reassessed severity / disposition |
|---|---|---|---|
| **H1 — Undefined rule baseline** | **Yes, as a product-spec gap.** US2 promises a “meaningful comparison baseline” and a hand-checkable test (spec lines 48–56); FR-007 requires deterministic rules, thresholds, bounded score, reasons and cold-start behavior (lines 214–216). But it does not say what data the rules use or prevent an arbitrary, non-meaningful rule from satisfying the requirement. The existing implementation’s “rules scorer” is explicitly test-only and illustrative; it is not an AML baseline (`backend/tests/unit/test_scoring_boundary.py`, `docs/decisions/foundation.md` lines 70–76). | FR-007 and SC-003 partially address this; neither requires a rule set based on observable transaction/history features rather than labels or identifiers. The exact rules and numeric thresholds belong in the plan, but the spec should define what qualifies as a baseline. | **HIGH. A — Required before planning.** Otherwise it is possible to plan a baseline that is technically deterministic but scientifically meaningless. |
| **H2 — Label validity affecting event history** | **Yes, as a real leakage/selection risk.** FR-006 says exclude target labels, and SC-002 requires label perturbations not to change earlier features/rule scores. But the spec does not distinguish a transaction’s observable facts from whether its target label is valid for supervised learning. If an invalid or missing label causes the entire event row to be rejected, later history can change based on label validity. | FR-002 accounts for source rows and lists invalid labels as an edge case; FR-012 separates label roles. They do not specify that a structurally valid event can remain available for label-free history when its label is missing/invalid. | **HIGH. A — Required before planning.** Clarify event-fact inclusion separately from supervised-label eligibility. |
| **H3 — Temporal and warm-up semantics** | **Partially.** Spec already requires strictly earlier timestamps, exclusion of timestamp ties, whole timestamp groups in splits, preserved timezone assumptions, a default one-day lookback and a declared coverage/warm-up interval (FR-003, FR-006; assumptions lines 370–382). It also lists missing timezone, ties and incomplete history as edge cases. So the original finding overstated the absence of temporal rules. | The actual source timezone/granularity is intentionally unknown until the data audit. The meaning of one-day lookback at boundaries, timezone normalization, cutoff representation, and how warm-up rows affect partitions/denominators remain unresolved. These depend on observed data and belong primarily in planning. | **MEDIUM. B — Required during planning.** No broad spec rewrite needed; make the plan resolve exact timestamp and coverage semantics and add acceptance coverage for incomplete history. |
| **M1 — Alert threshold ambiguity** | **Partially.** FR-013 freezes K and a threshold procedure; FR-014 says threshold tuning is validation-only; US5 AS2 and an edge case explicitly allow zero alerts. The assumption sets K to 20 and permits fewer alerts when ties prevent an exact count (lines 383–387). The spec does not, however, state how a threshold is selected or clearly distinguish a threshold policy from top-K retrieval. | Existing coverage already preserves zero-alert outcomes and prohibits label-based selection. The missing point is a predeclared deterministic threshold-selection rule; “at most 20” alone does not determine one. | **MEDIUM. A — Small clarification before planning.** Say no minimum alert count is required and define the operating-point rule in the plan. |
| **M2 — Uncertainty reporting** | **Partially.** FR-011 requires “uncertainty limits”; FR-017 requires evaluation limitations; FR-020 distinguishes uncertainty from observed facts/contributions. The spec does not say what the report must do when uncertainty is not quantified. | These requirements already prohibit overclaiming in principle. The gap is whether uncertainty means a quantitative estimate or a candid limitation statement, and how absence of a reliable estimate is reported. A particular statistical method should be a planning decision, not invented in the spec. | **MEDIUM. A — Clarify report behavior before planning; B — choose any estimation method during planning.** Require explicit reporting without mandating confidence intervals or a specific technique. |
| **M3 — Atomic publication semantics** | **No material product-spec defect confirmed.** FR-009 forbids partial publication; FR-021 says publish a completed run; US5 AS3 requires repeated/concurrent runs not to create list/detail disagreement. | Observable behavior is covered. The internal mechanism for achieving it—such as a local single-user completed-run pointer or snapshot swap—is an implementation/planning decision. | **LOW. D/B — Already sufficiently covered behaviorally; decide the simplest mechanism during planning.** Do not add distributed transactions or service infrastructure. |
| **M4 — Artifact trust verification** | **Not a major spec gap.** FR-018 requires trusted local artifacts, versioned metadata and hashes, and rejects arbitrary user uploads. | The desired boundary is present; how the local loader checks the artifact against recorded metadata is not. That is a technical plan/contract detail. | **LOW. D/B — Keep the requirement; specify local hash/provenance checks during planning.** No model registry or external artifact service. |
| **M5 — Checklist readiness overstatement** | **Yes, a documentation inconsistency.** Checklist lines 17 and 48 claim defaults/planning decisions are explicit and no critical questions remain, while lines 50–53 say numeric planning settings and source schema/counts remain future work and human review is pending. | The checklist correctly says it does not mean the feature works. But the “no critical unresolved” wording is too strong given FR-007’s unspecified baseline behavior and the threshold/label-history clarifications above. | **LOW. A — Revise checklist wording alongside spec changes.** Do not mark it as human-approved or implementation-complete. |
| **M6 — Local resource constraints** | **Mostly no.** FR-017 requires reporting actual resource conditions; assumptions require local operation and timeboxed training, and dependencies require permitted local compute (lines 388–408). No performance SLA is promised. | The plan still needs a feasible processing/training budget based on the actual environment. That is an execution planning issue, not a reason to add a product-level runtime or memory guarantee. | **LOW. B/D — Document observed hardware, timebox and any reduced training view in the plan/report.** Do not add infrastructure or hard caps without evidence. |

## 2. Phase 2 source verification

The repository search found:

- `specs/002-data-and-risk-scoring/checklists/requirements.md`: Feature 002’s **quality checklist**, not a course assignment.
- `specs/001-project-foundation/tasks.md`: a heading “Phase 2: Foundational (Blocking Prerequisites)” for Feature 001 workflow stages, not the Bootcamp’s Phase 2 requirements.
- `original_idea.md` §2: a summary of course modules and evidence expectations. It explicitly says the detailed official assessment rubric was not supplied (lines 25–27).
- No standalone Phase 2 assignment `requirements.md` or referenced course PDF was found in the repository.

The public SITA page describes the Bootcamp curriculum, including Python/API fundamentals, but I found no Feature 002-specific or Phase 2 assignment requirements there. It cannot substitute for the missing rubric. [SITA AI Bootcamp curriculum](https://sita.org.rs/ai-bootcamp/)

**Conclusion:** authoritative Phase 2 assignment requirements remain unavailable. I cannot establish compliance or report a Phase 2 coverage percentage. The Feature 001 “Phase 2” handoff and Feature 002 checklist must not be treated as that source.

## 3. Exact proposed specification edits

These are proposed wording only; I have not applied them.

### A. Required before planning

**1. FR-007 — define what qualifies as a meaningful rules baseline**

Current wording:

> “Provide a versioned deterministic rule baseline with documented thresholds, finite bounded score, triggered reasons and cold-start behavior, usable before ML exists. Changing only labels or future events MUST NOT alter its prior features or scores.”

Proposed wording:

> “Provide a versioned deterministic rule baseline usable before ML exists. Rules MUST use only label-free observable transaction facts and permitted historical features; transaction, account, case, source-row and target-label identifiers MUST NOT determine a rule outcome. Each rule MUST have a documented condition, threshold, score or score contribution, reason, and cold-start behavior. The concrete rule set and numeric values MUST be fixed before evaluation. The result MUST identify the rule version and actual triggered conditions. Changing only labels or future events MUST NOT alter prior features or rule scores.”

**Reason:** it makes the baseline meaningfully tied to observable risk indicators while leaving rule design and numeric thresholds to the plan.
**New scope:** no; this narrows implementation to the already promised rules baseline.
**Conflict:** none identified.

**2. FR-002 / FR-006 — separate observable event facts from label eligibility**

Add to FR-002 after its row-accounting requirement:

> “For a source row whose required event fields are valid but whose target label is missing or invalid, report the label as ineligible for supervised use separately from event-row validity. Do not discard otherwise valid label-free event facts from operational history solely because of target-label validity. Exclude the label itself from operational projections and scoring.”

Add to FR-006:

> “Supervised-label eligibility MUST NOT determine whether otherwise valid, label-free event facts are available to historical features. Training and evaluation eligibility is recorded separately from event-fact availability.”

**Reason:** prevents labels from indirectly controlling feature history through row filtering. Invalid event facts may still be rejected; this change concerns valid event facts with unavailable or invalid labels.
**New scope:** no; it clarifies existing label isolation and history requirements.
**Conflict:** none identified. It reinforces FR-012 and SC-005. Update row-accounting definitions so event acceptance and label eligibility are not conflated.

**3. FR-014 / acceptance scenario — preserve a genuine zero-alert outcome**

Add to FR-014:

> “The frozen threshold procedure MUST use validation data only and MUST NOT require at least one alert. A zero-alert result is valid when no score meets the predeclared operating-point rule. Fixed-budget Precision@K/Recall@K rankings are reported separately from threshold-generated alerts.”

Add a scenario to US3 or US5:

> “Given a frozen validation-only threshold procedure and a scoring population in which no event meets its rule, when the run is evaluated and published, then zero alerts are reported, the empty review state is shown, and no alert is manufactured to fill K.”

**Reason:** existing language already permits zero alerts, but the rule must not silently become “always select the top K.” The plan can choose the exact threshold method.
**New scope:** no; it makes existing zero-alert and threshold requirements consistent.
**Conflict:** none with FR-013, FR-016, US5 AS2 or the K cap, provided top-K metrics remain distinct from threshold alerts.

**4. FR-011 — make uncertainty reporting observable without mandating a method**

Replace “Report exact counts and uncertainty limits” with:

> “Report exact counts and state the uncertainty or evaluation limitations relevant to interpreting the result. If uncertainty is not quantitatively estimated, say so and explain the limitation; do not imply statistical precision that was not measured.”

**Reason:** “uncertainty limits” alone is not an objectively verifiable reporting behavior.
**New scope:** no; it sets a reporting honesty requirement, not a statistical method.
**Conflict:** none with FR-017 or the educational scope.

### B. Required during planning

**5. Temporal and warm-up semantics — no broad spec edit proposed.**

Resolve in the plan using the observed source characteristics:

- Timestamp parsing and any timezone assumption; reject or explicitly handle absent/ambiguous timezone data rather than silently assigning one.
- Exact feature cutoff: strictly earlier event time, with all tied timestamps receiving the same earlier-history snapshot.
- Meaning of the one-day lookback and its boundary convention.
- Coverage/warm-up representation and how rows lacking full history are treated in each partition and denominator.
- Whether history is replayed in event-time order and how held-out event facts enter later history without labels.

Add one plan-level acceptance case: an event with incomplete prior coverage and an equal-time peer must receive the documented coverage state and must not include the peer or later events in its history.

**Reason:** actual timestamp precision and timezone behavior are not yet observed. Choosing those in the product spec before the audit risks inventing data facts.
**New scope:** no.

**6. Atomic publication and artifact verification — plan details only.**

For M3, define the smallest local completion behavior: readers see either the previous completed snapshot or the new completed snapshot; incomplete runs are not published. Specify the restart and repeated-run check.

For M4, require the plan to define a local artifact manifest and verify recorded hashes before use. Keep artifacts local/ignored as already specified. No registry, cloud store, or user-upload feature.

**Reason:** desired behavior is already present; implementation mechanics are not.
**New scope:** no.

**7. Resource limits — plan/report only.**

Record the machine/runtime actually used, execution time, memory or other resource facts available, and any reduced training view. Decide a timebox before model experimentation. Do not promise full-scale interactive processing or add a hard runtime SLA without evidence.

**Reason:** FR-017 and the local-compute dependency already require honest reporting.
**New scope:** no.

### C. Checklist wording

Replace checklist line 17’s “defaults and planning decisions are explicit” with:

> “Product-level defaults and unresolved choices needed before planning are explicit; remaining technical decisions are identified for the plan.”

Replace line 48’s “No critical unresolved product questions were found” with:

> “The specification has outstanding decisions listed for the technical plan; human product review is pending.”

**Reason:** align the checklist’s readiness claims with its own lines 50–53 and with the FR-007/M1 clarifications.
**New scope:** none.

## 4. Classification of recommendations

| Category | Recommendation |
|---|---|
| **A. REQUIRED BEFORE PLANNING** | Clarify what constitutes a meaningful label-free rules baseline; separate event-fact validity from label eligibility; explicitly preserve zero-alert outcomes and distinguish threshold alerts from top-K metrics; make uncertainty reporting objectively checkable; correct checklist readiness wording. |
| **B. REQUIRED DURING PLANNING** | Resolve actual timestamp/timezone/lookback/warm-up semantics after data audit; choose the concrete threshold procedure using validation only; select any uncertainty estimation method or state that none is used; specify minimal local atomic publication, hash verification and resource/timebox evidence. |
| **C. OPTIONAL IMPROVEMENT** | Add a compact label-role table by pipeline stage if FR-002/006/012 wording still leaves implementers unsure. This is helpful, but the minimal edits above may suffice. |
| **D. ALREADY SUFFICIENTLY COVERED** | No partial publication; completed-run-only publication; local artifacts and hashes; zero-alert empty state; label-free feature constraints in principle; reporting actual resource conditions. These need planning detail, not new product scope. |
| **E. REJECT / OVERENGINEERING** | Distributed or streaming systems, cloud infrastructure, model registry, additional application screen, hard production SLAs, complex statistical infrastructure, or new ML/RAG/LLM capabilities. None is justified by the findings. |

## 5. Consistency and minimum patch set

The proposed edits preserve the current FR/SC structure and project boundaries. They do not alter the fixture contract or authorize implementation. The contract migration remains governed by FR-023 and Feature 001’s review process; Feature 001 currently uses fixed three-digit IDs, UTC-Z timestamps and a single two-decimal amount, so dataset compatibility still requires explicit reviewed migration.

**Recommended minimum patch set before planning:** update FR-007; clarify FR-002 and FR-006; add the no-forced-alert condition to FR-014 and an acceptance scenario; clarify FR-011 uncertainty reporting; correct checklist lines 17 and 48. Defer timestamp interpretation, run publication mechanics, artifact hash procedure, and local resource budgets to the plan.

## 6. Open human decisions

1. What observable transaction/history indicators should the baseline rules represent? The plan can propose concrete rules, but the team should review them before evaluation.
2. Should valid event facts with missing/invalid labels remain available for label-free historical context? The proposed minimal correction says yes, while excluding those labels from supervised use.
3. What validation-only operating-point objective should determine the alert threshold? The requirement should permit zero alerts and keep top-K retrieval metrics separate.
4. Is the team satisfied with reporting uncertainty limitations when a quantitative estimate is not defensible, rather than requiring confidence intervals?

## 7. Revised readiness

**READY WITH CHANGES for technical planning after the minimum patch set.** The first review overstated several findings: temporal behavior, zero-alert handling, partial publication, artifact locality/hash tracking, and resource reporting already have meaningful coverage. The material spec gaps are narrower: what makes the rules baseline meaningful, whether label eligibility can remove observable events from history, how to make the alert operating point reproducible without forcing alerts, and what uncertainty reporting must say. The authoritative Phase 2 assignment requirements remain unavailable, so course-specific compliance remains unassessed.


Perform a definitive Phase 2 compliance and specification alignment review.
IMPORTANT CONTEXT
Previous audits could not find the authoritative Phase 2 requirements.md and therefore could not verify Phase 2 compliance.
First, identify the actual Phase 2 requirements document.
Do not confuse it with:
specs/002-data-and-risk-scoring/checklists/requirements.md
That file is a specification quality checklist.
If the authoritative Phase 2 requirements document is still unavailable, stop the compliance assessment and report exactly what is missing. Do not substitute original_idea.md or infer course requirements.
If found:
1. Read every Phase 2 requirement.
2. Read Feature 002 spec.md.
3. Read original_idea.md and the project constitution.
4. Read relevant Feature 001 contracts.
Build a strict bidirectional traceability matrix.
For each Phase 2 requirement, identify:
- Exact source and section
- Matching Feature 002 requirement IDs
- Acceptance scenarios
- Success criteria
- Required verification evidence
- FULL / PARTIAL / MISSING / CONFLICTING coverage
Then independently review every Feature 002 requirement.
Determine whether it:
- Is mandated by Phase 2
- Is supported by the project goals
- Is a justified engineering safeguard
- Is an optional project design choice
- Introduces unnecessary scope
- Conflicts with another requirement
IMPORTANT
Do not classify a requirement as invalid merely because the original idea did not prescribe its numeric value.
Distinguish:
- Missing required behavior
- Legitimate design elaboration
- Unapproved product decision
- Technical planning detail
- Implementation evidence not yet available
Pay particular attention to FR-007, FR-011, FR-014, FR-021, and FR-022.
OUTPUT
A. Verified Phase 2 coverage matrix
B. Missing mandatory requirements
C. Conflicting requirements
D. Justified project-specific requirements
E. Unnecessary requirements
F. Exact proposed minimal corrections
G. Final specification readiness assessment
Do not edit files.
Do not implement code.
Do not invent requirements or claim tests have passed.

I **could not identify an authoritative Phase 2 requirements document**, so I stopped before assessing Feature 002 compliance, as requested. No files were changed.

The workspace contains:

- `specs/002-data-and-risk-scoring/checklists/requirements.md` — Feature 002’s specification quality checklist, not course requirements.
- `evidence/tasks/phase-02-handoff.md` and `prompts/development/001-foundation-phase-02.md` — records of Feature 001’s T006–T007 implementation phase, not the Bootcamp assignment.
- `original_idea.md` §2 — a module summary that explicitly says the detailed official scoring rubric was not supplied.
- The public [SITA AI Bootcamp page](https://sita.org.rs/ai-bootcamp/), which describes the curriculum but does not provide the requested Phase 2 requirements document.

**Missing:** the authoritative Phase 2 assignment `requirements.md` (or its equivalent), including its source/location and governing version. Without it, there is no reliable requirement set for the requested traceability matrix or compliance verdict.


Act as a Senior Machine Learning Research Engineer specializing in financial transaction anomaly detection, temporal validation, and reproducible ML evaluation.
Perform an adversarial scientific review of Feature 002.
Read the complete specification, Phase 2 requirements, and relevant available implementation.
Your objective is to find situations where the system could appear correct, produce believable metrics, and still be scientifically invalid.
INVESTIGATE
1. Point-in-time feature correctness
2. Future-event leakage
3. Target label leakage
4. Entity and account identity leakage
5. Train/validation/test contamination
6. Timestamp tie handling
7. Split-boundary history construction
8. Rolling-window and warm-up behavior
9. Training-only preprocessing
10. Categorical encoding and unseen values
11. Class imbalance and positive-count eligibility
12. Model and baseline comparison fairness
13. Threshold tuning
14. Precision@K and Recall@K correctness
15. Average Precision interpretation
16. Calibration leakage and reliability evaluation
17. Hyperparameter selection bias
18. Repeated holdout evaluation and implicit test tuning
19. Local explanation faithfulness
20. Model artifact reproducibility
21. Synthetic-to-real-world generalization claims
22. Benchmark observation scope versus actual deployment assumptions
SPECIFIC QUESTIONS
- Can held-out transaction facts legitimately contribute to historical features without revealing labels?
- Are train, validation, calibration, and test roles completely unambiguous?
- Can equal timestamps cause temporal contamination?
- Can an account identifier act as a hidden predictive proxy?
- Can the training process accidentally see future data through aggregate statistics?
- Can model selection be influenced by final test results indirectly?
- Can the validation threshold procedure create unexpected alert counts?
- Does the baseline receive a fair comparison on the same records?
- Are explanations faithful to the actual score scale?
- Can duplicated or source-derived fields expose the target label?
- Does a 20-positive eligibility guardrail provide enough evidence for the claimed metrics, and are its limitations stated correctly?
- Are there realistic cases where the declared protocol cannot produce a valid result?
FOR EVERY ISSUE
Explain:
- The invalid assumption
- A minimal counterexample
- Potential effect on results
- Severity
- Exact specification location
- Recommended requirement change
- Required regression or scientific validation test
OUTPUT
A. Scientific validity verdict
B. Confirmed methodological defects
C. Potential leakage pathways
D. Ambiguous evaluation decisions
E. Required safeguards
F. Recommended specification changes
G. Tests that would expose each issue
Do not train models, modify code, or change documentation.
Do not suggest complex models merely because they are more advanced.
The goal is scientific validity, not higher benchmark scores.


# A. Scientific validity verdict

**Feature 002 is not yet scientifically evaluable.** It is a specification, not an implemented ingestion/scoring pipeline: there is no Feature 002 plan, code, test suite, acquired IBM data, or model run. The current implementation is the Foundation fixture scorer, whose scores are transaction-ID-derived illustrative constants; the “rules scorer” in tests is also explicitly a constant, test-only adapter. Neither is an AML baseline. See [fixture scoring decision](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/docs/decisions/fixture-scoring.md:18) and [test scoring boundary](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/backend/tests/unit/test_scoring_boundary.py:18).

The specification already has strong safeguards: chronological partitions with ties kept together, point-in-time history, label separation, training-only preprocessing, bounded model selection, holdout freezing, explicit score/probability distinctions, and synthetic-data limitations. Those requirements make a defensible protocol possible, but several details still allow a plausible-looking result to be invalid if implemented carelessly.

I found no authoritative Phase 2 assignment requirements document. The available `requirements.md` files are Feature 001/002 quality checklists; `evidence/tasks/phase-02-handoff.md` documents Feature 001 T006–T007. So this review assesses scientific validity against the Feature 002 spec and available project artifacts, **not Phase 2 compliance**. The current handoff also says Feature 002 is unimplemented and no dataset has been downloaded or audited.

# B. Confirmed methodological defects and material specification gaps

“Confirmed” below means a gap exists in the current specification or evidence. It does **not** mean an implementation has already leaked data.

| Issue | Minimal counterexample and possible effect | Severity and exact location | Recommended requirement change | Required validation |
|---|---|---|---|---|
| **Event facts and label eligibility can be conflated** | A row has valid timestamp, accounts and amounts but a missing/invalid laundering label. An importer rejects the whole row; future account-history counts then differ because the label was unavailable. This makes feature history depend indirectly on label validity. | **HIGH, specification gap.** [FR-002, FR-006, FR-012](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:191); [SC-002](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:334). | Clarify that valid label-free event facts remain eligible for operational history even when their target label is missing/invalid; record supervised-label eligibility separately. | Change only the label on a valid event, or mark its label invalid: prior/later label-free features must remain identical; that row must not enter supervised fit/evaluation. |
| **Held-out facts are allowed in later history, but the scoring timeline needs a precise contract** | A test event occurs at 10:00. A later event is scored at 11:00. Using the 10:00 event’s facts in the 11:00 history is legitimate if those facts are observable by then; using its target label, using any event tied at 11:00, or using an event later than 11:00 is not. | **MEDIUM, partly covered.** [FR-006](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:210); [US2 AS1–2](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:58); [assumptions](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:375). | State explicitly that feature construction is a replay “as of” each event time: prior observed facts from earlier partitions may be context, but labels are never context; same-time and future facts are excluded. | Verify a test event’s facts affect only strictly later event features, never its own or same-time features; labels never affect any feature snapshot. |
| **“One-day lookback” and warm-up boundaries remain underspecified** | If lookback means the previous rolling 24 hours, an event at exactly `t−24h` may be included or excluded depending on the boundary rule. If it means the previous calendar day, results differ. At the beginning of the dataset, the prior day may not be present. | **MEDIUM, planning detail.** [FR-003, FR-005–006](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:195); [assumptions](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:375). | No product-level numeric change needed yet. In the plan, define timezone interpretation, exact cutoff inclusion, warm-up coverage state, and handling of missing source timezone. Do not silently assign a timezone. | Boundary timeline tests at just before, exactly at, and just after the lookback cutoff; a missing-timezone case; a warm-up case with incomplete coverage. |
| **Baseline/model threshold comparison is not fully specified** | A rule score is an ordinal value and a model output may be a different scale. Reusing one numeric threshold for both can produce different alert volumes for scale reasons, not quality. Conversely, forcing each to return exactly 20 alerts hides genuine zero-alert cases. | **HIGH, evaluation ambiguity.** [FR-014, FR-016](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:247); [K/threshold assumption](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:383); [US5 AS2](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:151). | Require the same predeclared, validation-only **operating policy** for each scorer, with scorer-specific thresholds as needed. State that zero alerts are valid and separate threshold-generated alerts from top-K ranking metrics. | Use deliberately different rule/model score scales and a no-alert case. Verify thresholds are selected only on validation, zero is retained, and both scorers are evaluated on identical test rows. |
| **Tie-breaking by stable identity can make P@K depend on record ordering** | All rows at the K boundary have the same score. If the stable ID is derived from CSV row order and row order happens to group positives first, P@K can look better than the score ranking warrants. | **MEDIUM, potential metric bias.** [FR-016](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:255). | Keep deterministic tie handling, but report the boundary tie group and make clear that the ID-based convention is for reproducibility, not model discrimination. Consider reporting the range of P@K possible within a boundary tie. | Construct a score tie spanning K; permute input row order and vary labels among tied rows. Confirm results are stable, tie counts are reported, and the model is not credited for distinctions it did not make. |
| **Validation threshold selection is not yet a reproducible rule** | “At most 20 alerts” permits many thresholds. One implementation could select a threshold for high precision; another could choose the 20th score. Both obey the cap but produce different alert behavior. | **MEDIUM, plan-blocking decision.** [FR-013–015](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:241); [assumption](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:383). | Before experiments, define the validation-only operating-point objective and tie behavior. Do not infer a “best” threshold after inspecting test results. | On a small known score/label set, independently derive the chosen threshold and alert count; verify identical protocol runs match and zero-alert thresholds remain possible. |
| **Twenty positives is an eligibility guardrail, not adequate evidence** | With 20 positive test cases, recall changes in 5-point increments when one case changes. Precision and AP can likewise be volatile. A result may satisfy FR-011 but still be too uncertain for a strong performance claim. | **MEDIUM, limitation already partly stated.** [FR-011](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:231); [SC-004](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:340). | Retain the guardrail but explicitly prohibit treating it as a precision guarantee. Report denominators and either a defensible uncertainty estimate or “not quantified” with the reason. No specific interval method need be mandated in the spec. | Test reporting with 20 positives and verify it states the counts, estimate granularity/uncertainty limitation, and makes no unsupported adequacy claim. |
| **Repeated holdout analysis can become implicit test tuning** | The team runs one frozen model, sees test AP, changes features, evaluates the same test again, then reports only the best test result. FR-015 says the consumed holdout cannot be called unseen, but does not explicitly require later runs to be marked exploratory and excluded from confirmatory claims. | **MEDIUM, process safeguard.** [FR-015](C:/Users/IsidoraPopovicLUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:252); [SC-005](C:/Users/IsidoraPopovicLUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:344). | Add that once holdout results are disclosed, subsequent use of that holdout is exploratory and cannot support a fresh confirmatory estimate; a new untouched holdout would be required for that claim. | Simulate a second protocol after test reveal; verify the manifest/report flags the holdout as consumed and rejects “unseen test” status. |
| **Feature allowlisting is strong, but proxies still need lineage checks** | A raw account ID is excluded, yet a hashed account ID, row number, label-derived suffix, duplicated `Is Laundering` column, or account-wide statistic computed using all rows could still encode identity/target/future information. | **HIGH risk if feature construction is careless; spec has partial safeguards.** [FR-004–006](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:199); [FR-012–013](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:236); [edge cases](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:181). | Require a feature lineage/allowlist audit that rejects target copies, source-row ordering and identifier-derived predictors. Preserve account IDs for joins, but do not silently include them or high-cardinality encodings as predictors. | Add a synthetic duplicate-label column and ID proxy to a fixture; feature validation must reject them. Renaming/permuting identifiers while preserving transaction relationships must not change model scores unless an explicitly approved identity feature exists. |
| **Training-only preprocessing is required, but all learned transforms need coverage** | A category encoder, missing-value imputer, scaler, feature selector or normalization statistic is fit on train+validation+test. The score may look plausible while incorporating future distribution information. | **Potential defect path; requirement is present.** [FR-012](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:236); [FR-005](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:204). | No new high-level requirement needed; plan and tests must cover every learned transform and unknown category handling. This is a classic leakage route; preprocessing must be fit on train and applied unchanged to later partitions. [scikit-learn guidance](https://scikit-learn.org/stable/common_pitfalls.html) | Instrument each `fit`/`fit_transform` call to prove it receives only training rows; include a category found only in validation/test and verify deterministic unknown handling. |
| **Calibration and uncertainty can be misrepresented** | A calibration model is fit and evaluated on the same examples, or Brier score alone is presented as proof of calibration. | **MEDIUM, partially guarded.** [FR-014, FR-016](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:247); [FR-020](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:278). | Freeze calibration data roles and evaluate calibration only on data not used to fit the calibrator. Describe Brier as a probability scoring metric, not calibration-only evidence; include reliability diagnostics only when sample support permits. | Tests/manifests verify disjoint calibrator fit/evaluation IDs. Report includes calibration status and does not claim calibrated probabilities if calibration was not evaluated. Brier alone cannot isolate calibration from resolution and uncertainty. [scikit-learn calibration guide](https://scikit-learn.org/stable/modules/calibration.html) |
| **Explanation correctness is required but its faithfulness test is broad** | A system displays the top three features from an explainer on log-odds while the UI displays a calibrated probability, or displays a local explanation computed for a different transform/run. The narrative can look credible yet not explain the displayed score. | **MEDIUM, spec recognizes scale but needs evidence.** [US4 AS2–4](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:122); [FR-019–020](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:274); [SC-006](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:348). | Define the explained output precisely (raw margin, raw score, or calibrated probability), bind the explanation to the exact scorer/run/feature snapshot, and verify method-specific faithfulness. | Known-model examples: verify the explanation reconstructs the declared output within the method’s stated tolerance; test that changing one feature changes its contribution consistently; reject mismatched run/transaction IDs. |
| **Baseline is not currently an empirical baseline** | The current foundation scorer rotates constants by transaction ID; the injected test rules scorer always returns 0.23. Comparing either against an ML model could produce metrics, but they would not measure meaningful AML rules. | **HIGH if mistaken for baseline; implementation is explicitly not a baseline.** [FR-007 and SC-003](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:214); [implementation](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/backend/src/fraudlens/scoring.py:27); [test adapter](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/backend/tests/unit/test_scoring_boundary.py:18). | Do not count Foundation fixture behavior as rule baseline performance. Before evaluation, define deterministic rules over label-free observable facts/history, with frozen conditions, thresholds, reasons and versions. | Hand-calculated timeline tests show each rule trigger/non-trigger, exact score/reason, label/future invariance, and identical evaluation rows for baseline and model. |

# C. Potential leakage pathways

The following are plausible failure modes to test; none was observed in a Feature 002 implementation because none exists yet.

- **Future-event aggregates:** compute an account’s total transaction count over the entire file, then attach it to each row. A past event then contains future knowledge. FR-006 and SC-002 prohibit the outcome, but require a test proving it.
- **Target copies and derived columns:** a duplicate label field, target-derived transaction ID, source row order, or feature engineered from label status enters the allowlist. FR-004/005/012 and the edge cases cover parts of this.
- **Entity memorization:** account IDs or deterministic hashes are encoded as predictors. This is invalid for unseen-account claims, though past account history can be legitimate for the stated known-account temporal task. FR-005 prohibits IDs as predictors; FR-017 requires seen/unseen coverage, so do not overstate this as an automatic flaw.
- **Timestamp ambiguity:** source timestamps without timezone, timestamp rounding, or sorting by row order can put future or same-time events into histories. FR-003/006 and edge cases address this, but the plan must decide source-specific handling.
- **Global preprocessing:** imputation, category vocabulary, normalization, feature selection, sampling or aggregate statistics are fit across partitions. FR-012 prohibits learning from future partitions; tests must confirm that all transforms obey it.
- **Selection through test feedback:** repeated test runs influence feature/candidate changes. FR-015 recognizes consumed holdouts, but run records must expose consumption and prevent confirmatory claims from reused test data.
- **K-boundary ties:** identity-based sorting is reproducible but may favor records if IDs correlate with source order, time or labels. A tie convention cannot create information the model did not provide.
- **Label-validity filtering:** discarding otherwise valid facts because their labels are invalid changes the history process; this is the clearest missing separation in the current requirements.

# D. Ambiguous evaluation decisions

1. **Train/validation/calibration/test roles:** FR-013/014 defer development subpartitions but do not require one explicit role table. The plan must state which rows and labels can be used for fitting, model selection, calibration fitting, calibration assessment, threshold choice, final metric computation, and application scoring.
2. **“Test labels unavailable to scoring”:** the model/scorer must never receive test labels. The evaluator must eventually join test labels to frozen predictions to calculate metrics. Specify that separation so “unavailable” does not preclude evaluation.
3. **Eligibility after protocol freeze:** if the split fails the 20-positive gate, FR-011 says revise before fit/selection. Record the amendment and do not repeatedly inspect outcomes to find a favorable time window.
4. **Per-scorer threshold policy:** thresholds cannot be assumed numerically comparable across rule and model scores. Define the same operating policy, not necessarily the same number.
5. **Average Precision:** FR-013 correctly distinguishes AP from trapezoidal PR area. The plan should name the implementation/version and positive label. AP is ranking performance, not probability calibration; the official implementation is non-interpolated and may differ from trapezoidal area. [scikit-learn AP definition](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html)
6. **Precision@K/Recall@K:** FR-016 has the right denominator intent. Pin down K as `min(configured K, population size)`, define ties at K, and report all positive counts. Recall@K denominator must include every positive in that test population, not only alerts.
7. **Calibration:** FR-014 guards against calibrating and judging on the same fitted examples. Plan should make all calibration fit/evaluation roles explicit and avoid treating Brier alone as calibration proof.
8. **Twenty-positive gate:** FR-011 already says this is not statistical adequacy. Keep that caveat prominent; eligibility means “metrics can be computed under the capstone rule,” not “the estimate is precise.”
9. **Model selection and repeated testing:** bounded candidates and frozen test selection are good safeguards. Make any test reuse exploratory, not confirmatory.
10. **Dataset/deployment scope:** the spec explicitly uses a synthetic pooled multi-bank view and says this is not one bank’s visibility (assumptions lines 373–374), and forbids production generalization claims (FR-017). The authors’ paper describes HI-Small as synthetic and reports a 10-day span, about 5 million transactions and 3.6K laundering transactions; the acquired file still must be independently verified before relying on these figures. A short synthetic temporal holdout cannot establish long-term or real-bank generalization. [Authors’ dataset paper, Table 4](https://arxiv.org/html/2306.16424v2)

# E. Required safeguards

- Separate **event-row validity** from **supervised-label eligibility**.
- Materialize features at a declared per-event as-of cutoff; enforce strict earlier-than semantics and common history for timestamp ties.
- Permit earlier held-out event facts to inform later test events only when those facts would already be observable; never expose their labels.
- Freeze time split, benchmark view, preprocessing, candidate budget, selection metric, threshold policy, K and calibration roles before experiments.
- Fit all learned preprocessing only on training data; map unseen categories using a documented policy.
- Keep identifiers for joins/provenance only; audit the complete feature lineage for raw IDs, proxies, duplicate target fields and full-dataset aggregates.
- Compare baseline and model on identical eligible rows, while using a consistent operating policy suited to each scorer’s score scale.
- Report AP definition, prevalence, class counts, denominators, P@K/Recall@K, tie handling and uncertainty limits; do not characterize 20 positives as statistically sufficient.
- Freeze predictions before revealing final labels; record if the holdout is consumed.
- Bind every explanation to its score scale, exact feature snapshot, scorer version and run.
- Reproduce the frozen evaluation from source hash, code/dependency versions, split manifest, seeds, features and artifact hashes.
- Do not claim real-world, unseen-bank, or long-term performance from this synthetic benchmark.

# F. Recommended specification changes

These are the minimum scientific clarifications I recommend before implementation planning:

1. **FR-002 / FR-006 — label validity and event facts:** add that missing/invalid target labels make a row ineligible for supervised fit/evaluation but do not remove otherwise valid label-free event facts from historical context. Keep the target field out of operational features and case payloads.
2. **FR-006 / SC-002 — point-in-time test:** state that historical features are reconstructed at each event’s as-of time. Earlier held-out facts may update later context after becoming observable; same-time and later facts and all labels are excluded.
3. **FR-013–016 / US5 AS2 — operating point and fairness:** require a predeclared validation-only operating policy applied separately to each scorer; allow zero alerts; distinguish threshold alerts from top-K ranking metrics. Document boundary ties in P@K.
4. **FR-011 / SC-004 — uncertainty:** preserve the 20-positive condition as a guardrail only. Require class counts and either a justified uncertainty estimate or an explicit statement that uncertainty was not quantified; prohibit interpreting eligibility as adequacy.
5. **FR-015 — holdout use:** add that any reuse after test results are revealed is exploratory and cannot support a new confirmatory claim on that same holdout.
6. **FR-019 / SC-006 — explanation faithfulness:** require the reported contribution method and output scale, bind the explanation to the assessment’s exact run/features, and include method-appropriate fidelity checks.
7. **Plan-level, not product-spec expansion:** define timestamp timezone/cutoff/warm-up, categorical unknown handling, per-scorer threshold selection, metric implementation, calibration role map, and local artifact manifest before experiments.

These changes do not require a more complex model or new infrastructure.

# G. Tests that would expose the issues

The following are required scientific/contract tests; **none were run in this review**:

1. **Label perturbation:** changing only labels leaves canonical event facts and feature snapshots unchanged; invalid-label events remain available for label-free history but not supervised targets.
2. **Future invariance:** append a future transaction and verify all earlier features/scores are unchanged, including global/category/account aggregates.
3. **Tie invariance:** permute input order within a timestamp; each tied event gets identical prior context and no tied event enters another’s history.
4. **As-of replay:** verify earlier validation/test facts can affect strictly later events, but not earlier or same-time events, and their labels never affect features.
5. **Window/warm-up boundaries:** check exactly-at and around the lookback cutoff, missing timezone, and insufficient history.
6. **Split manifest:** assert chronological non-overlapping whole-timestamp partitions, exact membership, frozen protocol hash, and correct positive/negative counts.
7. **Train-only transforms:** instrument preprocessing fits to reject validation/test IDs; include a category present only in validation/test.
8. **Identifier/target proxy audit:** inject target duplicate fields, row number and hashed account identifiers; verify the feature allowlist rejects them. Rename/permute IDs while keeping legitimate relational history intact and verify no hidden identifier dependence.
9. **Eligibility failure:** missing class or fewer than 20 positives yields an explicit ineligible report; no metric success or cherry-picked replacement split is emitted.
10. **Metric hand calculations:** small synthetic examples verify AP, P@K, Recall@K, threshold confusion counts, prevalence and denominators, including tied scores and K larger than the population.
11. **Baseline/model fairness:** both scorers receive the exact same eligible events and labels only at evaluation; each uses a predeclared validation-only threshold policy; zero alerts remain zero.
12. **Calibration isolation:** calibrator fit IDs are disjoint from calibration evaluation IDs; test predictions are frozen before test labels are joined.
13. **Holdout consumption:** after final labels are revealed, a second run on that holdout is visibly marked exploratory and not “unseen.”
14. **Explanation faithfulness:** known examples verify method, direction, explained output scale, run/transaction match and method-specific reconstruction tolerance.
15. **Reproduction and artifact integrity:** clean local reproduction matches predictions/metrics under the declared tolerance; altered artifact hashes fail closed.

A ranking result should be reported as an estimate on the declared synthetic temporal population, with its class counts and uncertainty limits—not as proof of performance in a real bank.


Act as a Senior Data Engineer and Database Reliability Engineer.
Review Feature 002's data ingestion, normalization, transaction identity, historical feature generation, and publication requirements.
Use the specification and Phase 2 requirements as primary inputs.
Inspect actual source schemas only if source files are available. Never invent observed dataset properties.
TASK
Find every reasonable boundary condition, failure mode, or consistency problem that is missing or ambiguously specified.
Analyze:
DATA INGESTION
- Incorrect column mapping
- Duplicate or ambiguous headers
- Missing and extra fields
- Invalid data types
- Empty and malformed files
- Unexpected encodings
- Large files and resource exhaustion
- Interrupted imports
- Partial writes
- Reimport idempotency
- Conflicting dataset versions
IDENTITIES
- Duplicate source rows
- Equal-valued but distinct transactions
- Stable transaction IDs across repeated imports
- Identity stability after rejected rows
- Account IDs repeated across banks
- Sender and receiver direction
- Transaction and case identity collisions
FINANCIAL VALUES
- Decimal precision
- Numeric overflow
- Invalid and negative amounts
- Currency distinctions
- Paid versus received amounts
- Missing currency codes
- Unsupported conversion assumptions
TIME
- Missing timezone
- Timestamp precision
- Equal timestamps
- Out-of-order input records
- Historical window boundaries
- Missing historical coverage
- Event time versus scoring time
- Deterministic replay
PUBLICATION
- Interrupted scoring runs
- Mixed run versions
- Partial snapshot publication
- Stale assessments
- Restart consistency
- Deterministic case selection
- Empty alert results
- Snapshot truncation
For every potential issue, determine whether existing FRs and acceptance criteria already cover it adequately.
OUTPUT
1. Missing edge cases ranked by severity
2. Ambiguous data contracts
3. Invariant violations that could occur
4. Additional requirements actually needed
5. Exact acceptance tests to add
6. Issues best deferred to technical planning
7. Unnecessary complexity to avoid
Do not edit files.
Prioritize correctness and reproducibility over premature infrastructure optimization.



I reviewed the Feature 002 specification, Feature 001 contracts and relevant implementation. **Feature 002 has no implementation or tasks yet**, and `data/` contains only the Foundation fixture files; there is no IBM source file to inspect. I again found no authoritative Phase 2 requirements document. The only matching files are feature-quality checklists and the Feature 001 phase handoff, so I cannot use them as course requirements or claim Phase 2 alignment.

The spec already covers many of the requested risks. The gaps below are specification or planning concerns, not claims that an implemented importer currently fails. No tests were run.

## 1. Missing edge cases ranked by severity

| Severity | Area and location | Existing coverage | Remaining gap or failure mode |
|---|---|---|---|
| **High** | **Column mapping and unknown fields** — FR-002, US1 AS1/5, edge cases at [spec.md:167–168](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:167) | Schema/field mapping, structural ambiguity, missing fields, unexpected columns and duplicate headers are mentioned. | No default behavior is defined for unexpected fields: reject, ignore, or accept? Silently accepting an unreviewed column could introduce a target duplicate or change a mapping. Also no explicit handling of case/whitespace/BOM differences in headers. |
| **High** | **Import completion and partial writes** — FR-002, FR-004, FR-009, US1 AS4/5 | Row accounting, idempotent reimport, controlled failures and no partial *publication* are required. | Import failure after some rows are persisted could leave a partial dataset that looks usable. “No partial publication” in FR-009 is under scoring requirements; it does not clearly define import commit behavior. No recovery/rollback behavior is stated. |
| **High** | **Transaction identity after rejection or source change** — FR-004, US1 AS4, SC-001, edge cases at [spec.md:169–172](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:169) | Stable provenance-and-row identities, idempotency, distinct equal-valued rows and collision rejection are explicit. | If IDs are assigned from accepted-row position after filtering, one rejected row can renumber later events. “Row identity” should mean a stable source-row reference assigned before rejection, not the post-filter ordinal. |
| **High** | **Conflicting source versions/configurations** — FR-001, FR-004, FR-018 | Release, hash and dataset version are recorded; different releases must not silently mix. | The spec does not say whether a changed mapping/import configuration creates a separate import version, and how the active dataset is selected if multiple versions are present. |
| **High** | **Amounts, precision and overflow** — FR-002/003, US1 AS3, edge cases at [spec.md:171–175](C:/Users/IsidoraPopovicLUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:171) | Preserve decimal precision, currencies and separate paid/received amounts; do not invent conversions; negative amounts are an edge case. | No rule covers parser overflow, non-finite numeric input, unsupported decimal magnitude/scale, blank currency, or whether zero is valid. A numeric cast or fixed-scale field could silently round or overflow. Exact source behavior must be learned from the acquired file, not assumed now. |
| **Medium** | **File-level parsing failures** — FR-002, US1 AS5 | Incompatible schema, malformed rows, duplicate headers and no eligible records are covered. | Empty files, header-only files, unexpected encodings, truncated final records, invalid byte sequences and parser failure midway are not explicit. It must be clear whether the import is rejected, partially accepted, or marked incomplete. |
| **Medium** | **File ordering and timestamps** — FR-003, FR-006, FR-010, US2 AS1/2, edge cases at [spec.md:175–177](C:/Users/IsidoraPopovicLUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:175) | Strictly earlier history, ties grouped together, original timestamps and timezone assumptions are required. | Out-of-order source rows are not named as an edge case. The contract should say event time—not source order—determines temporal history and split order. Timestamp precision and treatment of absent timezone are left for the data audit and plan. |
| **Medium** | **Rolling window and warm-up boundary** — FR-005/006 and assumptions at [spec.md:375–382](C:/Users/IsidoraPopovicLUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:375) | One-day lookback and a declared coverage/warm-up interval are stated. | The one day could mean a rolling 24 hours or a calendar day; inclusion at the exact boundary is unspecified. A warm-up row may have incomplete coverage, but the effect on feature values, eligibility and denominators is not defined. |
| **Medium** | **Case identity and changing alert status** — FR-004, FR-021, US5 AS3 | Case identity should be stable across reruns/scorer versions; each threshold-triggering transaction gets a case. | If a transaction crosses the threshold under one scorer version but not another, it is unclear whether its case persists, disappears from the active snapshot, or remains as historical state. That affects “stable case identity” and list/detail consistency. |
| **Medium** | **Interrupted/mixed scoring runs and stale state** — FR-009, FR-021, US5 AS3, edge case at [spec.md:180](C:/Users/IsidoraPopovicLUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:180) | Completed-run publication, no partial publication, exact run metadata and protection against mixed/concurrent versions are covered. | The externally observable outcome is mostly specified, but not what happens to the previous active snapshot after a failed new run, or how stale cached assessments are invalidated. Define only the simple local behavior in planning. |
| **Medium** | **Snapshot truncation** — FR-022, SC-007 | At most 100 alerts, ordering, total/display counts, selected time range and truncation must be reported. | It does not say how the 100 rows are chosen when more than 100 alerts qualify. With chronological ascending display, the oldest could crowd out recent alerts. “Selected time range” does not define the selection rule. |
| **Low** | **Large files/resource exhaustion** — FR-017 and assumptions at [spec.md:391–408](C:/Users/IsidoraPopovicLUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:391) | Local resource conditions are reported; local compute is a dependency; training is timeboxed in the plan. | No file-size or runtime guarantee is set. That is acceptable for this capstone; the plan should document actual resource feasibility and fail clearly, not introduce a premature infrastructure requirement. |

## 2. Ambiguous data contracts

**Source rows and labels.** FR-002 says every source row is accepted or rejected and lists invalid labels as an edge case. It does not distinguish whether a valid transaction with a missing/invalid label is rejected as an event or merely ineligible for supervised training/evaluation. This can make future transaction history depend on target-label quality. Event-fact validity and label eligibility need separate accounting.

**Headers and columns.** “Structural ambiguity blocks import” is a sound safeguard, but the required/optional field set, allowed aliases, header normalization, and behavior for unknown fields should be determined after inspecting the actual source. For safety, unknown fields should not silently become features; ambiguous or target-like mappings should block the import pending review.

**Financial values.** FR-003 correctly requires original precision and currency preservation. The new canonical contract must say how amounts are represented without binary floating-point conversion, how missing/invalid currency is handled, and what numeric range is supported. Do not choose source precision, currency rules or a maximum amount without the actual file and reviewed contract.

**Identity namespace.** FR-004 should define source-row identity before row filtering. A reasonable invariant is source release/content version + stable physical source-row reference + import mapping version. Whether a content hash or release ID is part of the transaction namespace is a design choice, but switching versions must not silently mix or overwrite cases.

**Foundation compatibility.** Feature 001’s contract uses `TX-###`/`CASE-###`, UTC-Z timestamps, one amount with exactly two decimals, and one currency; see [schemas.json](C:/Users/IsidoraPopovicLUKOWA/OneDrive%20-%20LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/001-project-foundation/contracts/schemas.json:6). Feature 002 explicitly requires broader identities, precision and paid/received currencies. FR-023 correctly makes contract migration and consumer review a gate. Do not coerce the dataset into Foundation v1 by truncating identifiers or amounts.

## 3. Invariant violations that could occur

These are the key “looks successful but is wrong” cases:

- **Partial import reported as complete:** process crashes after writing some rows; import report/active dataset reflects only the prefix. A retry may silently duplicate or omit rows.
- **Renumbered transactions:** rejected rows are removed before identity assignment, shifting row ordinals and changing otherwise stable IDs on reimport.
- **Distinct events deduplicated:** importer treats identical field values as duplicates, even though equal-valued rows can represent distinct transfers. FR-004 already prohibits this.
- **Wrong bank or direction:** account tokens are not bank-qualified or sender/receiver are swapped. US1 AS2 and FR-003 already address these.
- **Financial values altered:** amount is parsed through float, rounded to two decimals, overflowed, or combined across currencies. FR-003 and the US1 boundary scenario cover the intent; add explicit no-rounding/overflow tests after actual schema discovery.
- **Temporal history uses file order:** an out-of-order row or same-time row contributes to an event’s history. Strict earlier-than and tied-time requirements prohibit it, but the tests should include both conditions.
- **History silently starts with zero:** event occurs before sufficient source coverage and the system reports low activity rather than incomplete coverage. US2 AS3 and FR-005/006 require missing coverage handling; test exact warm-up boundaries.
- **Mixed publication versions:** new scorer results are written while old list/detail state remains partly visible. FR-009/021 and US5 AS3 cover the required outcome; the plan must provide one local atomic publication mechanism.
- **Old cases appear current:** a rerun changes the active run but cached assessment data remains from a prior feature/scorer version. FR-008/021 require versioned run identity; define cache invalidation/active snapshot semantics in planning.
- **Misleading truncated snapshot:** total count is correct but the selected 100 records are unspecified, so the UI’s shown cases may not represent the intended time range. FR-022 needs a deterministic selection rule.

## 4. Additional requirements actually needed

I recommend only a few narrow additions:

1. **Separate event validity from label eligibility.** Otherwise the label can indirectly alter historical features.
2. **Import completeness semantics.** A failed or interrupted import must not become the active dataset; retries must be safe.
3. **Identity-before-filtering semantics.** Rejected rows must not renumber accepted rows; reimport of the same source/version/configuration preserves IDs.
4. **Unknown-column behavior.** Do not silently map unexpected fields or use them as predictors; require an explicit mapping decision.
5. **Deterministic choice of displayed snapshot rows.** FR-022 reports truncation but does not specify which records are retained.

The rest—encoding support, parser implementation, memory strategy, decimal library choice, local checkpointing, cache mechanism and storage transaction strategy—belongs in the technical plan unless the team wants a product-level guarantee.

## 5. Exact acceptance tests to add

These tests can use synthetic source-shaped fixtures; that demonstrates behavior, not dataset representativeness.

1. **Header mapping:** duplicate names, whitespace/BOM/case variants, reordered columns, missing required columns, unexpected columns, and an extra label-like column. Verify ambiguous mapping blocks import and unknown fields are never silently used.
2. **Empty/malformed inputs:** zero-byte file, header-only file, invalid encoding, truncated record, malformed quote and parser failure after several valid rows. Verify controlled failure and no active partial import.
3. **Interrupted import/retry:** inject a failure after N rows, retry the identical source/configuration, and verify the final accepted IDs/counts match a clean import exactly with no duplicates.
4. **Rejected-row identity stability:** include one invalid row before valid rows; compare IDs with a version where the invalid row is absent. Verify valid source-row IDs do not shift due to filtering.
5. **Reimport and version separation:** import same source/config twice—zero duplicate event/case identities. Change source hash or mapping version—require a distinct recorded version and reject silent mixing.
6. **Duplicate semantics:** two equal-valued events in distinct source rows remain distinct; the same source row reimported twice remains one identity.
7. **Bank/direction identity:** same account token at two banks produces distinct parties; reversing sender and receiver changes the directed event.
8. **Financial values:** valid high precision, large magnitude, negative, zero, malformed decimal, overflow/non-finite parse, missing currency, invalid currency, differing paid/received amounts/currencies. Verify exact preservation or explicit row rejection—never rounding or invented conversion.
9. **Out-of-order and timestamp ties:** shuffle rows; results must be identical. Same-timestamp events share the same strictly-earlier history; no tie contributes to another.
10. **Lookback/warm-up boundaries:** events just outside, exactly at and just inside the declared window; initial incomplete coverage is represented explicitly, not converted to zero history.
11. **Event-time replay:** an earlier held-out transaction’s facts may affect a strictly later score, but never its own or same-time feature snapshot; changing its label does not change any features.
12. **Scoring-run interruption:** fail mid-scoring and verify the previous completed snapshot remains active, or no snapshot is active if none existed; never expose a mixed run.
13. **Mixed/stale versions:** publish two scorer versions, restart, and verify list/detail return the same active run/version; stale cached assessments are not served.
14. **Zero-alert and truncation:** zero threshold matches yields an empty snapshot. More than 100 matches yields a deterministic chosen set and correct total/display/truncation/time-range fields.

## 6. Issues best deferred to technical planning

- Actual column names, aliases, source types, label mapping, timestamp precision and observed currencies: **must wait for the locally acquired source audit**. No IBM raw file is present, so these properties are unknown.
- File encoding and parser behavior, including whether streaming is needed for the actual file size.
- Decimal implementation and any maximum representable magnitude/scale.
- Exact import identity scheme and how mapping/configuration versions are recorded.
- Local atomic import/publication mechanism and retry behavior.
- Cache invalidation and active-run pointer semantics.
- Exact warm-up and lookback boundary definitions after timestamp granularity is observed.
- Which 100 records form the default snapshot when more qualify, consistent with the intended user journey.
- Resource/timebox strategy based on the actual local machine; no performance target is currently promised.

## 7. Unnecessary complexity to avoid

Do not add distributed transactions, streaming infrastructure, cloud storage, queues, a database migration framework, model registry, universal multi-format ingestion, elaborate recovery orchestration, or production-grade concurrency controls. The spec assumes local single-user operation. A local staging area plus a clear “complete or not active” boundary, deterministic IDs, a source manifest and reproducible tests are enough for this feature’s stated scope.



Act as a Principal Software Architect performing a compatibility and implementation-readiness review.
Read:
- Feature 002 spec.md
- Phase 2 requirements.md
- Feature 001 specification
- Existing API/data contracts
- Current source code
- Current tests
- Foundation architecture decisions
- Project constitution
Do not assume documented contracts perfectly describe the actual implementation. Inspect both.
OBJECTIVE
Identify incompatibilities between the planned Feature 002 behavior and the existing foundation.
FOCUS ON
1. Existing transaction schema
2. Existing assessment schema
3. Fixed-width IDs versus dataset IDs
4. Amount and currency representations
5. Timestamp semantics
6. Data validation rules
7. Case list and detail consistency
8. Provenance and explanation objects
9. Fixture compatibility
10. Model and rule scorer replacement
11. Run selection and persistence
12. Error handling and explicit mode selection
13. Compatibility with future investigation components
14. Existing UI assumptions
15. Existing tests and migration requirements
FOR EACH INCOMPATIBILITY
Report:
- Current behavior with file and symbol reference
- New required behavior
- Why the existing contract is insufficient
- Impacted producers and consumers
- Whether a breaking contract change is required
- Suggested migration approach
- Tests needed to preserve Feature 001
Also investigate whether Feature 002 introduces unnecessary architectural complexity.
Explicitly look for situations where a simpler design could satisfy the same requirements.
OUTPUT
A. Compatibility matrix
B. Breaking changes
C. Missing contract decisions
D. Migration dependencies
E. Regression risks
F. Simplification opportunities
G. Recommended implementation order
Do not change code or documentation.
Do not begin implementation.


## A. Compatibility matrix

**Readiness: not ready for implementation without a contract and persistence design.** Feature 002 identifies the Foundation migration in FR-023, but the spec does not yet define the target wire contracts or how a completed run becomes the stable source for list and detail responses. The scorer injection seam is reusable; the fixture-shaped transaction, assessment, and case contracts around it are not.

I could not locate an authoritative Phase 2 assignment `requirements.md`. The available [Feature 001 Phase 2 handoff](<C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/evidence/tasks/phase-02-handoff.md:1>) is task evidence, not the assignment requirements, and Feature 002’s checklist is a specification-quality checklist. So this review compares the Feature 002 spec with the Foundation artifacts and implementation; it cannot certify Phase 2 compliance. The repository also has no Feature 002 plan, contracts, tasks, or implementation yet.

| Area | Foundation behavior and evidence | Feature 002 behavior | Compatibility |
|---|---|---|---|
| Transaction IDs and case IDs | Backend validates `TX-###` and `CASE-###` in [contracts.py](<C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/backend/src/fraudlens/contracts.py:22>); the shared schema and API also constrain these formats. Case lookup is by `CASE-###`. | FR-004 requires stable, dataset-qualified identities; FR-021 requires one review case per triggering transaction. The spec explicitly anticipates more than 999 records. | **Breaking change.** Both Pydantic and frontend decoders reject dataset identities that do not fit the Foundation patterns. `CASE-###` also cannot identify an unbounded set of alerts. |
| Amount and currency | `Transaction` has one nonnegative, two-decimal `amount` string and one three-letter `currency`; see [contracts.py](<C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/backend/src/fraudlens/contracts.py:45>) and the [data model](<C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/001-project-foundation/data-model.md:7>). | FR-003 and FR-005 require preserving paid/received amounts and currencies, precision, and currency-grouped features. FR-023 flags this as a migration concern. | **Breaking change.** The Foundation representation cannot preserve two directional values/currencies or other precision. The spec does not settle the exact canonical/API representation or missing-value rules. |
| Timestamp semantics | Foundation requires a UTC timestamp ending in `Z`; the fixture scorer copies event time into `scored_at`. See [contracts.py](<C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/backend/src/fraudlens/contracts.py:35>) and [scoring.py](<C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/backend/src/fraudlens/scoring.py:28>). | FR-003, FR-006, FR-008, and FR-021 distinguish source/event time, history cutoff, scoring time, and run identity; the spec also requires preserving source time assumptions. | **Partial compatibility.** The Foundation’s single UTC event timestamp works for fixtures, but does not represent source precision/timezone assumptions, feature as-of time, actual scoring time, or a run’s temporal context. |
| Assessment and explanation | `RiskAssessment` has one score, source, scorer version, `scored_at`, and a bounded explanation string. `Source` allows fixture/rules/model. See [contracts.py](<C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/backend/src/fraudlens/contracts.py:54>) and the [JSON schema](<C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/001-project-foundation/contracts/schemas.json:53>). | FR-008, FR-019, and FR-020 need run/data/feature provenance, observed values, explanation method and output scale, and distinct uncertainty/context. | **Breaking or additive contract change.** The closed Foundation schema and frontend decoder cannot carry structured explanation and provenance objects. A string can carry prose but cannot reliably link a contribution to a feature, value, method, or run. |
| Case list and detail | The API returns a list of `CaseSummary` rows and a `CaseDetail` by case ID. List ordering is ascending case ID, with no pagination or snapshot metadata. See [api.md](<C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/001-project-foundation/contracts/api.md:10>). | FR-021 and FR-022 require publishing a selected completed run, one case per triggering transaction, and a bounded alert snapshot ordered by event time and stable identity, with counts/truncation. | **Breaking semantic change.** Existing ordering, identity, and list shape do not express run selection, total alert count, or truncation. |
| Scorer replacement | The structural `Scorer.score(Transaction) -> RiskAssessment` seam and app/service injection exist; see [foundation decision](<C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/docs/decisions/foundation.md:65>) and [main.py](<C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/backend/src/fraudlens/main.py:43>). | FR-007 defines a rule baseline; FR-014/016 compare it with a selected model; FR-021 publishes a selected run. | **Reusable seam, insufficient contract.** Current scorer receives only a Foundation transaction and returns a Foundation assessment. It has no history snapshot, feature schema, or run context. The tests exercise fixture/test scorer injection, not a production rules or model path. |
| Run selection and persistence | `CaseService.list_cases()` scores every fixture case on each read; `get_case()` scores again. See [cases.py](<C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/backend/src/fraudlens/cases.py:111>). No run store is present. | FR-015 freezes a selected model/protocol; FR-018 stores reproducibility metadata; FR-021 requires explicit selection, restart reproducibility, and consistent publication. | **Missing capability.** Recomputing at request time does not guarantee list/detail consistency across scorer changes or restart, and there is no completed-run selection or persistence boundary. |
| Runtime modes and errors | `Settings.mode` and `Health.mode` accept only `fixture`; startup tests reject other modes. See [settings.py](<C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/backend/src/fraudlens/settings.py:9>) and [contracts.py](<C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/backend/src/fraudlens/contracts.py:80>). API exposes generic controlled errors. | FR-009 and FR-025 require explicit failure, no silent fixture fallback, and explicit fixture/rules/model use. | **Breaking configuration/API change.** The current application cannot explicitly select a non-fixture runtime. The spec also leaves unclear whether “mode” means data source, scorer, or both. |
| Validation and fixtures | Backend and frontend strictly validate closed contracts; fixture data is small and uses Foundation IDs and values. Case/detail identity is checked in [contracts.ts](<C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/frontend/src/contracts.ts:132>) and [api.ts](<C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/frontend/src/api.ts:115>). | FR-023 and SC-008 require fixture compatibility and Foundation regression coverage. | **Compatible only if fixture behavior remains separately supported.** Replacing the shared transaction schema in place risks breaking the current fixture path and its strict decoders. |
| UI assumptions | Frontend displays one amount/currency, score on a 0–1 scale, source/version/time, and a string explanation; health is fixture-only. See [views.ts](<C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/frontend/src/views.ts:54>) and [contracts.ts](<C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/frontend/src/contracts.ts:41>). | FR-019/020/022/024 require structured explanation and provenance, bounded snapshot metadata, and truthful fixture-vs-dataset labeling. | **UI migration required.** Existing fixture-specific copy and score presentation cannot accurately describe every model/rule assessment or a truncated run snapshot. |

## B. Breaking changes

1. **Transaction and case identity.** Foundation’s fixed-width IDs are enforced in backend, JSON Schema, and frontend. Feature 002’s dataset-qualified IDs cannot be passed through unchanged. Do not silently truncate IDs or assign unstable sequential IDs; both would risk collisions or identity changes after reimport. FR-004 requires a stable identity algorithm, but the actual public identifier format and `case_id` relationship remain undecided.

2. **Transaction payload.** One amount/currency pair and two-decimal precision are incompatible with FR-003’s separate paid/received values and currencies. A Foundation transaction should not be overloaded with synthetic defaults or conversion assumptions to make dataset records fit.

3. **Assessment/detail payload.** Feature 002 needs a scored result tied to a specific dataset, feature version, run, and assessment context. The existing assessment’s one timestamp and free-text explanation are insufficient. Because backend and frontend schemas forbid unexpected fields, adding fields in place is a coordinated contract change, not a transparent extension.

4. **Case-list semantics.** Foundation’s case-ID order and bare `items` response conflict with event-time ordering plus alert count/truncation metadata. Consumers must be updated together.

5. **Runtime mode.** `fixture` is the only valid configured and health-reported mode. Feature 002 cannot be enabled just by injecting a scorer; explicit dataset/rules/model operation requires new configuration and response semantics.

The least disruptive migration is to **preserve the existing fixture contract and fixture journey** while defining a versioned Feature 002 contract for dataset-backed results. FR-023 already requires a migration review, but it does not specify versioning, the representation, or rollout compatibility. A contract version or explicit response discriminator is needed so strict clients can distinguish Foundation fixture payloads from Feature 002 payloads.

## C. Missing contract decisions

Resolve these in the Feature 002 plan/contracts before implementation:

- **Source and scorer selection:** Are `fixture`, `rules`, and `model` modes scorer choices, data-source choices, or combined configurations? The IBM dataset is a data source, while rules/model are scorers; treating them as one enum leaves configurations such as dataset + rules ambiguous.
- **Canonical transaction shape:** Specify directional amount/currency fields, decimal precision, optional/missing values, timestamp source/normalized forms, timezone assumptions, and how these map to the Foundation fixture transaction.
- **Stable IDs:** Define the source fields/provenance used to generate IDs, collision handling, stability across import order/rejected rows/reimport, and whether case identity is the transaction identity or a separate stable key.
- **List/detail contract:** Define run selection, snapshot identity, list order, alert counts, truncation indicator, and how a list row resolves to exactly the detail from that same run.
- **Scorer boundary:** Decide whether scoring accepts one Foundation transaction, a canonical transaction plus historical feature snapshot, or a run-level batch/context. The existing interface cannot express FR-006/008/021 inputs and provenance directly.
- **Persistence/publication:** Choose the smallest local mechanism that provides immutable completed runs and atomic activation, survives restart, and prevents list/detail from mixing runs. The spec requires this behavior but no storage contract or plan exists.
- **Failure mapping:** Keep public errors generic as Foundation requires, but define where import rejection details and run failures are visible to the local operator without exposing paths or labels in application responses.
- **Future consumers:** Feature 001 requires shared contracts and later workstream coordination; Feature 002 should publish sample versioned schemas and label-free examples for downstream investigation consumers.

No source schema or raw dataset is available in the repository, so actual IBM field mapping and observed data characteristics remain unverified. The spec itself notes the raw file was absent at specification time in [spec.md](<C:/Users/IsidoraPopovicLUKOWA/OneDrive - LUKOWA/Documents/sita-capstone/capstone-FraudLensAI/specs/002-data-and-risk-scoring/spec.md:370>); those assumptions must be checked when the authorized local source is available.

## D. Migration dependencies

The change crosses these producers and consumers:

- Backend contract models and validation in `backend/src/fraudlens/contracts.py`
- Public JSON schemas and API examples in `specs/001-project-foundation/contracts/`
- Settings, health, case lookup, and service behavior in `backend/src/fraudlens/{settings.py,main.py,cases.py}`
- Frontend wire decoders and API identity checks in `frontend/src/{contracts.ts,api.ts}`
- List/detail views and fixture/model labeling in `frontend/src/views.ts`
- Fixture files and fixture scoring in `data/fixtures/cases.json` and `backend/src/fraudlens/scoring.py`
- Contract, API, startup, fixture, scorer-boundary, list/detail, and UI regression tests

The current tests cover Foundation contracts and fixture delivery, not Feature 002 data ingestion, persistent run selection, or model/rule scoring. The Phase 2 handoff also records incomplete peer reproduction and review; it does not establish that Feature 002 behavior exists.

## E. Regression risks

- A broad replacement of `Transaction` or the ID validators breaks the existing fixture contract and frontend decoder.
- New frontend fields without synchronized backend schemas, or vice versa, cause strict decoding failures.
- Case IDs generated from row position can change after a rejected row or changed import order, breaking saved links and list/detail identity.
- Recomputing assessments during list and detail requests can make results disagree if the selected run or scorer changes between calls.
- Returning the “latest” run implicitly can mix cases from different runs or activate a partial run after failure.
- Retaining the current fixture banner/source presentation for dataset records would misstate the provenance and meaning of their scores.
- Updating only API types while leaving Feature 001’s JSON schema and contract tests unchanged creates contradictory contracts for downstream contributors.

Preserve regression checks for the three Foundation fixture cases, malformed/unknown IDs, list/detail agreement, controlled errors, explicit fixture health, scorer injection, and frontend navigation. Add separate tests for dataset contract decoding and run consistency rather than weakening those existing checks.

## F. Simplification opportunities

- Keep the current three case API operations and list/detail journey; Feature 002 does not require new analyst screens.
- Keep the Foundation scorer interface for fixture compatibility, but add the minimum context-bearing boundary needed for dataset assessment. Avoid forcing every Foundation caller to adopt model-specific inputs.
- Represent Feature 002’s named entities as plain versioned data contracts and local artifacts where adequate; the spec does not require a database, service layer for each entity, registry, or distributed job system.
- Use one immutable local completed-run snapshot and an atomic selection step if that satisfies restart and consistency requirements. A local single-user capstone does not justify distributed locking or infrastructure.
- Keep ingestion and evaluation as offline/local operations unless the plan establishes a specific user-facing need. The existing API is read-only and the specification calls for publication into browsing, not a general dataset-management API.

## G. Recommended implementation order

1. **Resolve the missing Phase 2 source** before claiming course compliance; keep that assessment separate from architecture readiness.
2. **Write the Feature 002 plan and versioned contracts**: canonical transaction, assessment/explanation, list/detail snapshot, health/runtime selection, and stable identity. Confirm compatibility against Feature 001 before coding, as the Foundation governance requires.
3. **Define local run publication and failure semantics**: completed-run identity, immutable snapshot, atomic activation, and restart behavior.
4. **Implement ingestion and identity against an available, authorized source**, recording the actual source schema and observed constraints rather than relying on assumed IBM fields.
5. **Implement historical features and label-free rule scoring** behind the planned boundary; test ties, missing history, and distinct account/bank identities.
6. **Implement evaluation and model artifact handling** after data/feature contracts are stable; keep evaluation labels out of operational inputs.
7. **Adapt API and UI together**, preserving the fixture contract and truthful source labeling.
8. **Run Foundation regression tests plus new contract, publication, and scientific-validity tests** before calling the feature implementation-ready.

No files were changed, and no code or tests were run for this review.
