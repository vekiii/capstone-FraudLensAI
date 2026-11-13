# Feature Specification: Evidence-backed AI Investigation

**Feature Branch**: `feature03`

**Feature Directory**: `specs/003-ai-investigation`

**Created**: 2026-11-13

**Status**: Draft; agent-reviewed for planning, not team acceptance or implemented behavior.

**Input**: Extend approved FraudLens AI with curated AML knowledge, controlled evidence tools, source-backed AI reports, saved investigation state, analyst review and meaningful evaluation. Work independently of feature 002 ML development. User reports an OpenAI key and describes the intended model as GPT-6 Luna; exact API identifier and access are unverified.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find and inspect procedures (Priority: P1)

An analyst searches the curated knowledge collection and inspects exact source passages, versions, jurisdiction and simulation status.

**Why this priority**: Useful and independently demonstrable without a model or provider key.

**Independent Test**: Search a reviewed corpus with fixed questions; inspect expected passages and no-match responses without language-model generation.

**Acceptance Scenarios**:

1. **Given** reviewed procedures, **When** searching for missing-information handling, **Then** relevant passages expose title, section, version, source and simulation status.
2. **Given** an out-of-coverage question, **When** searching, **Then** the system explicitly reports no adequate match instead of authoritative-looking weak evidence.
3. **Given** a report citing a superseded document, **When** opening its citation, **Then** the exact cited version and superseded status remain inspectable.

### User Story 2 - Prepare a grounded report (Priority: P1)

An analyst starts an investigation. The assistant gathers permitted evidence and procedures, then drafts a report distinguishing observations, hypotheses and missing information.

**Why this priority**: The LLM synthesizes evidence and guidance into a reviewable narrative rather than recalculating risk.

**Independent Test**: Investigate an authored case with a controlled provider; verify tool trace, evidence binding and invalid-output rejection. Separately evaluate actual-provider narratives.

**Acceptance Scenarios**:

1. **Given** a valid context and configured provider, **When** starting, **Then** actual permitted tool calls gather evidence and the report binds to the selected case snapshot and corpus version.
2. **Given** no occupation, device or source-of-funds facts, **When** drafting, **Then** these remain missing rather than inferred from a high score.
3. **Given** a rule score and partial/unavailable explanation, **When** drafting, **Then** the report preserves those limitations and invents neither calibrated probability nor contributions.
4. **Given** general guidance about suspicious patterns, **When** explaining a case, **Then** the guidance is not presented as proof of customer guilt.
5. **Given** an invented or other-case citation, **When** validating, **Then** the draft cannot become ready for review; a bounded repair or controlled failure is visible.

### User Story 3 - Continue and recover saved work (Priority: P1)

An analyst reopens an investigation after navigation or restart and explicitly retries failed work without losing history or mixing versions.

**Why this priority**: Reliable state makes the workflow repeatable instead of an ephemeral chat.

**Independent Test**: Interrupt after evidence collection, restart and reopen; test timeouts, duplicates, cancellation and source changes.

**Acceptance Scenarios**:

1. **Given** saved evidence, **When** reopening after restart, **Then** completed evidence remains available and provider continuation requires an explicit action.
2. **Given** timeout or invalid provider output, **When** the attempt ends, **Then** the reason and valid previous steps remain visible; partial prose is not shown as a completed report.
3. **Given** a scored-run switch, **When** requesting more evidence for an older run, **Then** mixed snapshots are refused; the old evidence is preserved and a new investigation requires explicit snapshot selection.
4. **Given** duplicate submissions with the same request identity, **When** processed, **Then** only one attempt starts. Intentional reruns use a new identity and preserve previous runs.

### User Story 4 - Review and record a human decision (Priority: P1)

An analyst opens citations and records escalation, closure or a request for more information with rationale.

**Why this priority**: AI supports judgment and never constitutes a final disposition.

**Independent Test**: Review a saved report, exercise all dispositions, reject missing rationale and stale revisions, and verify the original draft remains unchanged.

**Acceptance Scenarios**:

1. **Given** a validated draft, **When** reviewing, **Then** citations, missing facts and limitations are inspectable.
2. **Given** an empty rationale, **When** submitting disposition, **Then** the action is rejected without a final review event.
3. **Given** concurrent reviews, **When** one saves first, **Then** the stale second write conflicts rather than overwrites.
4. **Given** a saved decision, **When** reopening, **Then** actor, time, rationale and report revision are visible; no account intervention or regulatory submission occurs.

### User Story 5 - Evaluate retrieval and report quality (Priority: P2)

A team member compares baseline retrieval with one bounded improvement, then evaluates real generated reports using independent evidence expectations.

**Why this priority**: Observable quality evidence is required for completion; P2 orders delivery, not whether evaluation is optional.

**Independent Test**: Run frozen evaluation packs; verify denominators, held-out isolation, per-case results and deterministic retrieval reproducibility.

**Acceptance Scenarios**:

1. **Given** two frozen configurations, **When** evaluating identical held-out questions, **Then** both results and failures are reported, including negative improvement.
2. **Given** a valid citation ID with unsupported interpretation, **When** reviewing quality, **Then** semantic support fails despite reference validation passing.
3. **Given** no provider access, **When** running controlled fixtures, **Then** results are labeled workflow verification, never real LLM quality evidence.

### Edge Cases

- Empty, oversized, malformed or unsupported-language queries; missing corpus or no adequate passages.
- Conflicting, historical, superseded or foreign-jurisdiction guidance; unclear publication dates and simulated policy.
- Corpus replacement, changed passage content or missing historical evidence during an investigation.
- Embedded instructions requesting secrets, other cases, permission changes, arbitrary tools or external actions.
- Same account identifier in different banks; requested account outside case scope; future or same-minute transactions.
- Unknown context versions, inconsistent IDs, unsupported score scales, truncated or unavailable history.
- Valid-looking invented citations, factual overclaims with valid citations and altered exact monetary values.
- Provider access failure, refusal, invalid output, rate limits, timeout, budget exhaustion and late responses.
- Restart in every active state, duplicate submission, cancellation and stale/concurrent review or browser response.
- Absence of case facts or procedures: neither is evidence of legitimacy or guilt.

## Requirements *(mandatory)*

### Functional Requirements

#### Context and ownership

- **FR-001**: Investigations MUST consume a versioned label-free `InvestigationContext` owned by feature 003. Feature 002 retains ownership of transactions, scored runs and explanations. Its meanings MUST be reused, not independently redefined. Actual producer and affected-consumer review is required before real dataset integration.
- **FR-002**: Contexts MUST identify source mode, case, transaction, immutable context revision, source snapshot, observation time, version provenance and history availability. Dataset contexts MUST preserve run/dataset/transaction equality, directional exact money/currency, raw time and time-basis assumptions, score kind/source, history cutoff/coverage and explanation availability. Unknown versions and inconsistent identities MUST fail closed.
- **FR-003**: Fixture and dataset adapters MUST be replaceable. Authored fixtures MUST be labeled; absent dataset/model support MUST NOT silently fall back to fixtures. Missing fixture metadata MUST remain unavailable, never fabricated. Feature 003 MUST NOT train, activate or modify scorers or change existing feature 001/002 response contracts.
- **FR-004**: Private laundering labels, evaluation answers, hidden reviewer notes and training artifacts MUST be excluded from prompts, retrieval, tools and analyst-facing investigation payloads. Case evidence MUST be allowlisted; the model MUST NOT receive arbitrary database/source-file access.

#### Knowledge and retrieval

- **FR-005**: The initial corpus `fraudlens-aml-knowledge-v1` MUST contain at least six reviewed thematic documents: three clearly simulated procedures (review/escalation, narrative/citation, missing/conflicting facts), one IBM field/limitation guide and at least two official-source sections. Each MUST record provenance, reuse terms, included sections, retrieval date, publication/version date or explicit unknown, jurisdiction, historical context and content digest. Six is the initial acceptance floor; expansion toward the original 10-20 target is optional.
- **FR-006**: Only deliberately ingested reviewed content MAY be searched; runtime open-web investigation is excluded. Foreign guidance MUST NOT be represented as Serbian law or simulated procedure as real bank policy. This is educational procedural support, not a regulatory compliance determination.
- **FR-007**: Passages MUST have stable document/section/version identities and inspectable exact text. Each investigation MUST pin its corpus/retrieval version and preserve passages actually used. Reindexing MUST NOT silently alter report evidence. Missing historical evidence MUST be disclosed and prevent claiming complete verifiability.
- **FR-008**: Search MUST return ranked passages with provenance or explicit no-adequate-match under a frozen retrieval policy. Analysts MUST inspect sources independently of generation. Search limits, unsupported inputs and truncation MUST be explicit.

#### AI investigation and safety

- **FR-009**: The assistant MUST be able to request only bounded read operations `get_case_facts`, `get_account_history` and `search_procedures`. Actual validated calls, result references and outcomes MUST be recorded. Template-only narration MUST NOT be labeled tool-using AI investigation.
- **FR-010**: Application-bound case/access scope MUST NOT be chosen by the model. Tool scope, arguments and limits MUST be checked before execution. Arbitrary URLs, SQL, paths, code execution, account actions and regulatory submission MUST be unavailable. Invalid requests MUST NOT execute.
- **FR-011**: History MUST use bank-plus-account identity and permitted activity strictly before the context cutoff, excluding the focal event. Coverage, lookback, simulated shared-bank view and truncation MUST be explicit. Same-minute ties MUST follow feature 002's strict cutoff convention. Unavailable history MUST NOT be reported as empty. Aggregates MUST be deterministic; different currencies MUST NOT be summed without approved conversion.
- **FR-012**: Instructions inside documents, case data or tool output MUST be treated as untrusted content, incapable of changing permissions, tools, budgets, workflow or provider configuration or exposing secrets. Model output MUST remain untrusted until validation and be displayed as safe literal text.
- **FR-013**: Reports MUST include summary, observed facts, risk indicators, alternative explanations, missing information, recommended checks, limitations and citations. Observed facts MUST cite authorized case evidence; procedural recommendations MUST cite applicable retrieved guidance. Hypotheses MUST be tentative and cite their premises. No supported alternative explanation MUST be stated as absence rather than an invented benign story.
- **FR-014**: Reports MUST preserve exact money, currencies, IDs, time assumptions, score meaning and explanation limitations. Risk scores or general typologies MUST NOT prove guilt, occupation or source of funds. The assistant MUST NOT fabricate contributions or convert rule scores into calibrated probabilities.
- **FR-015**: Before ready-for-review, validate structure, required fields, context binding, evidence kinds and citation references against evidence actually available to that run. Unknown/mismatched references and altered quoted numerical facts MUST be rejected. Structural/reference validity MUST be distinguished from semantic faithfulness; valid IDs alone MUST NOT be advertised as proof of faithful interpretation.
- **FR-016**: Missing facts or adequate guidance MUST produce visible limitations. If a defensible useful draft is impossible, the outcome MUST be `needs_information`; a limited grounded draft MAY be ready-for-review with explicit gaps. Unsupported interpretations discovered in review MUST be recorded as defects.
- **FR-017**: Real provider use MUST be server-side and replaceable for tests. Record provider, requested model ID, returned model ID when supplied, prompt version and generation settings without credentials. Missing access or required capabilities MUST produce explicit errors, never silent provider/model substitution or fixture output labeled as live AI.
- **FR-018**: Attempts MUST have finite recorded limits: initially 8 provider requests including repairs/retries, 12 executed tool calls, 5 passages per search, 50 history events per result and 120 seconds total elapsed time. Allow at most one schema/reference repair and one transient-provider retry within those same limits; never retry rejected credentials/access automatically. Planning MUST freeze per-request/output limits before live use. Exhaustion MUST end visibly, never loop. Reopening MUST NOT spend provider budget.

#### State, review and experience

- **FR-019**: Persist states `created`, `gathering_evidence`, `drafting`, `ready_for_review`, `needs_information`, `failed`, `cancelled`, `reviewed`. Only validated drafts enter ready-for-review. Explicit retry creates a linked attempt retaining previous outcomes. Reviewed reports MUST NOT be overwritten by reruns.
- **FR-020**: Persist context/corpus/prompt/provider identities, step outcomes, reports, timestamps, used budgets and controlled failure reasons. Restart MUST expose interrupted work and allow explicit continuation using completed validated evidence; it MUST NOT assume interrupted provider calls were free or unexecuted. Repeated request identities MUST NOT duplicate attempts; late responses MUST NOT resurrect ended attempts.
- **FR-021**: Display reports, evidence, source/score distinctions, progress, missing facts and recovery actions within the existing case/investigation screen; source browsing belongs to the agreed knowledge screen. Original fixture browsing MUST work without provider/corpus/model. Navigation and stale asynchronous responses MUST NOT mix cases.
- **FR-022**: Only an explicit analyst action MAY record `escalate`, `close` or `request_more_information` with nonempty rationale, actor, timestamp and report revision. An identified local demo analyst is sufficient; enterprise authentication is not implied. AI prose MUST NOT execute disposition. Ready drafts may be reviewed; needs-information runs require a saved limitations draft and permit only request_more_information. Failed/cancelled runs cannot receive report disposition.
- **FR-023**: Preserve original drafts/evidence and separate analyst corrections. Detect stale revisions and reject concurrent overwrites. Corrections to reviewed decisions require linked revisions, never deletion of prior events. Human actions MUST remain distinct from machine validations; no approval/signature is inferred.
- **FR-024**: Credentials MUST remain outside Git, frontend, reports and logs. Only approved synthetic/authored case data may leave the backend for the provider. Stable case-scoped aliases SHOULD replace account IDs outbound while retaining local evidence resolution. Planning MUST define the outbound allowlist. Real customer data, production banking and a new role-management system are excluded.

#### Evaluation and evidence

- **FR-025**: Before tuning, freeze a corpus manifest and at least 30 retrieval questions (10 development, 20 held-out) and 12 investigation scenarios (4 development, 8 held-out). References MUST be independently authored and reviewed by a teammate other than the author. Expected evidence, relevance judgments, rubric and split IDs MUST remain outside retrieval/model inputs. Optional SARSum benchmarking MUST remain separate and never become IBM case history or a completion dependency.
- **FR-026**: Compare one retrieval baseline and one bounded improvement on identical held-out questions/corpus. Report Recall@5, MRR@5 and no-answer outcomes with per-question counts and evidence, including regressions. Do not tune on held-out questions. Retrieval relevance, workflow correctness and report faithfulness MUST remain separate results.
- **FR-027**: Evaluate actual-provider reports for factual support, procedural applicability, unsupported claims, essential-fact coverage, missing-information handling and citation correctness. One human reviewer MUST assess all eight held-out reports and another independently at least four, recording disagreement and resolution. An LLM judge MAY supplement but not replace humans. At least 12 separate negative/security scenarios MUST exercise injection, unauthorized cases/tools, label exclusion, invalid citations, budget/time limits and stale state. Test-provider checks MUST NOT count as live report evaluation.
- **FR-028**: Record corpus/context/prompt/retrieval/provider versions, settings, tool trace, duration, token usage if returned (otherwise unknown), failures and review identities for evaluated runs. Actual spend MUST NOT be inferred without verified pricing. Reproduce deterministic stages; disclose generation variability rather than promising identical prose. Preserve prompts, commands, outcomes and unrun checks through project evidence conventions.

### Key Entities *(include if feature involves data)*

- **InvestigationContext**: Immutable versioned label-free boundary referencing feature 002 facts/assessment meanings and explicitly unavailable fixture fields.
- **KnowledgeDocument / Passage**: Reviewed content, provenance, reuse terms, jurisdiction, dates, simulation status and versioned section identity/digest.
- **EvidenceItem**: Run-bound authorized case observation/history or procedure passage. Evidence kinds remain distinct: guidance cannot prove case facts.
- **InvestigationRun / Attempt**: Context/corpus/provider/prompt binding, state, budgets, persisted steps and linked retry history.
- **InvestigationReport**: Immutable draft revision with typed claims, citations, limitations and validation results.
- **AnalystReview**: Explicit human correction/disposition, rationale, actor and report revision with immutable audit history.
- **EvaluationPack / Result**: Private frozen references, configurations, measured outcomes, review judgments and failure denominators.

## Success Criteria *(mandatory)*

### Measurable Outcomes

These are release targets, not observed results. Missed targets MUST remain visible; they leave the corresponding quality criterion incomplete rather than justify tuning held-out answers.

- **SC-001**: All six initial documents have reviewed provenance. Every citation in reviewable reports resolves to the exact used evidence/version. All applicable acceptance examples disclose simulated, historical, missing-source and jurisdiction limitations (FR-005-008, FR-015).
- **SC-002**: On 20 held-out retrieval questions, at least one frozen configuration achieves macro Recall@5 >= 0.80 and MRR@5 >= 0.70 on answerable questions. Include at least four no-answer questions; all four explicitly report insufficient coverage. Predeclare relevant-passage sets; exclude no-answer questions from recall/MRR and report their separate denominator. Publish both configurations, including negative improvement (FR-025-026).
- **SC-003**: At least seven of eight actual-provider held-out reports achieve both >=90% supported factual claims and >=80% essential-fact coverage under the frozen human rubric. All eight contain zero unsupported critical claims (guilt, invented identity/source of funds, altered money/time, fabricated contributions or unauthorized actions). No-adequate-guidance cases produce zero unsupported procedural recommendations. Zero factual claims is not automatically a perfect report; applicable coverage/no-answer rubrics govern (FR-013-017, FR-027).
- **SC-004**: All deterministic acceptance checks and the minimum 12-scenario safety pack reject unknown citations, other-case access, label leakage, injected tool instructions, stale writes and exhausted limits, with zero unauthorized tool executions or automatic dispositions (FR-004, FR-009-012, FR-015, FR-018, FR-022-024).
- **SC-005**: All specified restart/retry/duplicate/cancellation/concurrent-review examples preserve case/version binding and audit history without duplicate accepted decisions or silent provider requests on reopen. All three allowed dispositions can be saved and reopened with required rationale (FR-019-023).
- **SC-006**: On five frozen ordinary live demonstration cases, at least four produce a validated draft or explicit needs-information outcome within 90 seconds; every attempt terminates visibly by 120 seconds, including provider failures in the denominator. On 20 local knowledge searches, measured 95th-percentile completion time is <=2 seconds on the recorded demonstration machine (FR-008, FR-018, FR-021, FR-028).
- **SC-007**: The fixture investigation journey works with an explicitly labeled test provider before ML completion. Original three-case browsing works with no provider/corpus/model. Dataset-context examples pass contract checks and affected-consumer review; real producer integration remains pending until actually exercised (FR-001-003, FR-021).
- **SC-008**: Evidence contains frozen evaluation packs, both retrieval configurations, all held-out report outcomes, required human reviews, a real tool trace, failures/usage and reproduction instructions. No fixtures, historical checks or unexecuted model access are labeled current live evaluation (FR-025-028).

## Assumptions

### Scope

- This local educational AML prototype stays within Bootcamp modules 1-9 and the four approved screens. This feature delivers knowledge, investigation and explicit human review. ML development, priority optimization and Simulation Lab remain separate. No autonomous account actions, regulatory submissions, open-web investigation, graph database or multiple autonomous agents.
- Default UI/report language is Serbian; English sources retain original cited text. Exact amounts, currencies, names and identifiers do not become new facts through translation. Include cross-language questions in the frozen evaluation pack.
- Corpus preparation is local team work, not a public upload/scraping platform. Versioned evidence is retained for the lifetime of the demonstration; real-customer retention policies are outside this synthetic-only scope.

### Parallel work and integration

- Feature 003 owns context, evidence tools, retrieval, report/state/review. Feature 002 owns import, history/features, scoring/artifacts, scored-run publication and its existing API/UI migration. Do not duplicate its outstanding tasks or modify its contracts unilaterally.
- Starting main is `0fbe31315052542575b22515c83b0a062efeaa31`; local feature 002 documents are older than reviewed `origin/model-implementations` snapshot `2dd815d85bfc9c2fc70a28baef9c142d551e57e0`. Planning MUST reconcile the current producer contract without importing unfinished ML code. Historical handoff entries do not prove current behavior.
- Feature 003 proposes InvestigationContext; the actual producer and affected consumers review its shape, time/currency/identity semantics and score/explanation fidelity before dataset integration. Missing history interfaces remain explicit dependencies, not permission for arbitrary database queries.
- Authored v1 contexts need not extend the original closed fixture responses. Dataset contract examples support adapter tests but are not actual IBM evidence or successful inference.
- Exact schemas, error shapes, provider request/output limits, storage mechanics and task dependencies belong to Plan/Tasks, which MUST precede implementation. The spec records required behavior, not their completed design.

### OpenAI access

- User reports an email naming the OpenAI project `Nećeš razbojniče` and providing a key. The project name is organizational context, not a model ID or access guarantee. No credential was requested, inspected or used during specification.
- User interprets Luna6 as GPT-6 Luna. This is the intended model description, not a verified API identifier or claim of supported capabilities. Verify project-accessible model ID and required tools/structured-output behavior during integration; do not guess or hardcode a model ID from the email.
- Work may proceed with an explicitly labeled test provider. Live quality acceptance remains incomplete without actual provider access, reviewed sources and required human evaluation. Provider errors do not justify silent model substitution.
- This spec establishes no regulatory deadlines, legal duties or provider pricing. Source selection/context is reviewed at ingestion; procedural applicability is separately evaluated during human report review.
