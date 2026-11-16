# Proposal 002: RAG verification and showcase website

**Status:** pending team decision. **Date:** 2026-11-16. This proposal does not authorize implementation. T047 is the decision-record task; T001 remains the overall Feature 005 scope gate.

## Proposal

Add an advisory RAG verification layer for persisted alerts and a four-route showcase site (`/`, `/data`, `/rag`, `/live`) to the proposed Feature 005 scope. The verifier would read committed, label-free assessment facts, retrieve from a reviewed and versioned corpus, and store a separately versioned verdict with citations. The site would display generated, provenance-bound data and use fixture/batch/live source badges. Neither component may change scores, alert decisions, or analyst authority.

## Expected benefit

- Give reviewers a clear, navigable explanation of the dataset, model, evidence retrieval and limitations.
- Demonstrate an end-to-end RAG call with checked citations and visible failure states.
- Let analysts inspect advisory context beside an alert without coupling the scoring worker to an LLM.
- Keep public-facing numbers tied to generated artifacts and labelled data sources.

## Schedule and resource impact

The proposed addition adds fourteen tasks (T047–T060) across corpus review, retrieval/indexing, verifier isolation, evaluation, API/dashboard integration, a separate showcase site, accessibility/performance review and acceptance. It adds dependencies for an approved vector store, embedding model and LLM provider, a reviewed corpus, a verifier role, site libraries, and external-data handling decisions. It increases Python and frontend dependency review, evaluation and integration effort. No reliable person-hour estimate or delivery date is recorded; the team must assess these before approval. T047 is a hard gate, and rejection or deferral leaves T001–T046 unchanged.

## Decisions requested

The team should record an attributed approve/reject/defer decision and decide:

1. Whether RAG and showcase work are in scope, with benefit, owner and schedule impact.
2. Vector store and embedding model.
3. LLM provider/model and whether synthetic data may leave the host.
4. Corpus author, licence, reviewer and update process.
5. Whether the site is a separate `web/` application or part of the existing dashboard, plus hosting.

## Decision record

**Decision:** pending. **Decision date:** not supplied. **Participants/approvers:** not supplied. **Conditions or objections:** pending. Do not replace these fields with inferred approval; complete them in T047 after the team discussion.
