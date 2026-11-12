# FraudLens AI Constitution

## Core Principles

### I. Team-Controlled Scope
Work MUST stay within the agreed MVP and Bootcamp modules 1–9. Any out-of-course technique
or functionality MUST receive explicit team approval before implementation, with benefit and
schedule impact recorded. Routine choices within approved scope require no renewed approval.

### II. Specification Before Implementation
Each feature MUST define behavior, boundaries, acceptance criteria, plan and reviewable tasks
before application implementation. Tasks MUST trace to requirements.

### III. Test-First Business Behavior
Critical behavior MUST follow RED → GREEN → REFACTOR. The initial test MUST fail for the
intended missing behavior, not an unrelated environment problem. Contracts, negative cases and
relevant regression checks MUST accompany implementation. Mechanical scaffolding requires no
artificial failing tests.

### IV. Purposeful AI
Arithmetic, validation, permissions and priority calculation MUST use deterministic code.
LLMs may connect textual evidence, procedures and alternative explanations into narratives.
LLM output MUST NOT create facts or permissions.

### V. Verifiable Claims
Case claims and procedural recommendations MUST reference appropriate evidence. Missing facts
MUST remain missing. A valid citation identifier alone MUST NOT count as faithful interpretation.

### VI. Human Decision Authority
An analyst MUST make final case dispositions. AI recommendations MUST remain reviewable.
Automatic account interventions and regulatory submissions are outside the approved MVP.

### VII. Independent Evaluation
Ground-truth labels and reference answers MUST stay outside prediction inputs, investigation
tools and retrieval context. Evaluation MUST prevent future leakage. Final holdout data MUST
NOT be used for tuning. Fixture checks MUST NOT be reported as model evaluation.

### VIII. Parallel Development Through Contracts
Components MUST use explicit versioned contracts and replaceable adapters. Work MUST NOT wait
for trained ML or provider access where labeled fixtures exercise the same boundary.
Fixture, rule-based and model outputs MUST remain distinguishable.

### IX. Reproducibility and Honest Evidence
The team MUST preserve relevant original development prompts, application prompt versions,
dependency/data versions, executed commands, outcomes and limitations. Evidence MUST describe
actual execution. Secrets MUST NOT enter Git, browser code or evidence logs.

### X. Minimum Necessary Complexity
Only complexity needed for the approved feature may be implemented. Each member MUST own
a demonstrable area, its checks and explanation. AI-generated work still requires human review.

## Scope and Boundaries
This is an educational AML investigation and triage prototype, initially using IBM AML HI-Small
and curated knowledge. A laundering label is not a legal finding; transfer amount is not bank
loss. The full MVP has four agreed screens; foundation establishes only local fixture browsing.
GNNs, transformer training, multi-agent product orchestration, open-web investigation and graph
databases are excluded without team approval. Course game examples are not product requirements.

## Development Workflow
Use Specify → Plan → Tasks → Implement → Converge with clarification and quality review as
needed. Version shared instructions, contracts and specifications. Exclude secrets, large data
and local state from Git. Accepted work MUST link requirements, actual checks and review.
Review shared boundaries before dependent parallel work. Select one explainable model for the
MVP; timebox comparative ML and AutoML experiments separately.

## Governance
These principles were explicitly approved by the team on 2026-11-11. Amendments MUST record
reason, approval and affected artifacts. MAJOR changes redefine/remove principles, MINOR adds
or expands rules, PATCH clarifies wording. Check compliance before planning and after design;
unresolved violations block affected work. User instructions retain precedence.

**Version**: 1.0.0 | **Ratified**: 2026-11-11 | **Last Amended**: 2026-11-11
