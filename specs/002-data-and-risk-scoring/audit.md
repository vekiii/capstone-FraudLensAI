
# FraudLensAI — Current-Branch Architecture & ML Audit

> **Purpose:** Review the **actual checked-out Git branch and repository**. Produce an evidence-based assessment and a prioritized improvement plan for the intended product: **incoming transaction data → ML detection of potentially suspicious transactions → evidence collection → legal RAG assessment of potentially relevant laws → human review / downstream actions**.
>
> **Mode:** Read-only audit. **Do not implement, refactor, retrain, change configuration, download data, or commit files.** Return the report in Markdown. Do not assume the proposed RAG system exists.

## 1. Audit rules

1. Start at the repository root. Record the branch, commit SHA, working-tree state, project structure, and relevant execution/configuration entry points. Respect `AGENTS.md` and repository instructions.
2. Inspect **source code first**, then tests, specifications, manifests, quickstarts, `next_work.md`, and evidence reports. Differentiate implemented behavior from documentation claims.
3. Trace the pipeline end-to-end, following real functions, data schemas, CLI commands, artifacts, storage, API responses, and UI consumers. Cite exact `path:line` references for every substantial finding; include commands and results for checks actually run.
4. Classify every conclusion: **Verified in code**, **Verified by execution**, **Documented only**, **Not verifiable**, or **Not implemented**. Do not invent model metrics or legal capabilities. Mark missing ignored/local files explicitly.
5. Use existing small tests and safe read-only inspection when feasible. Do **not** execute multi-million-row imports, feature builds, full training, model deserialization from unknown sources, network calls, or expensive evaluations without explicit authorization. Never reveal raw transactions, secrets, private labels, or credentials in the report.
6. Favor the **smallest defensible changes**. Do not propose a rewrite, microservices, streaming, a feature store, a vector database, or new infrastructure without a demonstrated requirement.

## 2. Review scope and checks

| Area | Verify in the current branch |
|---|---|
| **A. Ingestion & data security** | CSV source/provenance, checksum and mapping, duplicate `Account` headers, type/date/currency validation, malformed input handling, deterministic IDs, duplicates, idempotency, partial failures, trust boundaries, input/SQL/prompt-injection risks. Determine whether ingestion is generic or tied to one IBM release. |
| **B. Data design & historical features** | Storage and copy costs; canonical schema, labels separated from inference data, joins/keys, event-time ordering, same-timestamp handling, 24-hour warm-up/cold start, missing histories, currency/amount consistency, look-ahead leakage, reproducibility, memory/disk/performance bottlenecks. |
| **C. ML models & prediction path** | Identify each implemented rules/model/notebook/pretrained artifact; which is actually used by `score-run`; loading security, model provenance, feature schema compatibility, preprocessing parity, version pinning, batch behavior, invalid/empty inputs, score semantics/calibration, explainability, and threshold logic. Distinguish **AML labels** from general **fraud** claims. |
| **D. Evaluation quality** | Train/validation/test isolation, time-based splits, label leakage, previously viewed test data, threshold selection, imbalance-aware metrics (PR-AUC, precision/recall, precision@K, alert volume), baseline comparison, reproducibility, and whether recorded performance supports a useful review queue. Do not call exploratory evidence an independent benchmark. |
| **E. Outputs & interfaces** | Trace predictions → score/alert/case tables → run activation → API → UI. Check stable IDs, schemas, status transitions, immutable run outputs, stale snapshots, error cases, explanations, provenance, and whether **zero-alert** results make the UI unusable. Distinguish predictions, investigative candidates, and confirmed findings. |
| **F. Target legal RAG workflow** | Determine what already exists versus what is missing for: flagged transaction → factual evidence package → ML explanation → jurisdiction-aware legal retrieval → grounded assessment → analyst review. Check availability of authoritative, versioned legal sources; citation/article validation; legal effective dates; missing-evidence handling; and human approval. A predicted flag must **not** become a statement that a law was broken. |
| **G. Operational quality** | Configurability, code modularity, tests/CI, repeatability on a clean checkout, dependency/secret management, trusted model artifact handling, logs/metrics, failure recovery, execution time, and local deployment complexity. |

## 3. Questions the report must answer

1. **What works today?** Give the observed end-to-end flow, identifying actual modules and entry points.
2. **What is broken, unsupported, overly coupled, or unnecessarily complex?** State the impact and evidence.
3. **Can a new CSV be scored with a trusted pretrained model without retraining?** If not, exactly what prevents this?
4. **What do the model's outputs mean and how useful are they?** Distinguish suspicion/ranking from proven fraud or money laundering. Address the currently documented zero-alert / top-20 findings **only after verifying their source and status**.
5. **What is needed to reach the target workflow?** Identify the minimum interfaces between detection, evidence assembly, legal retrieval, structured legal assessment, and human review.
6. **What should remain unchanged?** Highlight reliable existing components worth preserving.

## 4. Required report format (keep concise)

### A. Executive verdict (max 150 words)
- **Status:** Ready / Partially ready / Not ready for the intended ML → legal-RAG workflow.
- Top **3** findings, with evidence and confidence.

### B. As-built pipeline
- One compact Mermaid diagram showing **only implemented components**.
- A brief table: `Stage | Actual implementation (file:line) | Inputs → outputs | Status / concern`.

### C. Findings (max 10, most important first)
For each: `ID | Severity (P0 blocker / P1 high / P2 improvement) | Evidence (file:line or command result) | Impact | Specific fix | Confidence/status`.
- Do not classify a missing future RAG component as a bug in a feature that never promised it; classify it as a **target-state gap**.
- Separate **confirmed defects** from **architectural choices** and **unverified risks**.

### D. Recommended minimal target architecture
- One Mermaid diagram: `CSV/source → validation → features → trusted pretrained ML inference → suspicious-candidate selection → evidence package → legal RAG → structured assessment → human review/downstream consumer`.
- Specify minimal boundaries/contracts: transaction ID, dataset/model/feature/policy versions, score and its meaning, reason codes/evidence references, candidate status, applicable jurisdiction, cited legal provision/source/date, uncertainty/missing facts, and reviewer decision.
- Make explicit: **ML estimates risk; explanations describe supported signals; RAG maps evidence to potentially relevant law; a human makes consequential conclusions**.

### E. Prioritized improvement plan
- **Now (P0):** 1–3 must-fix blockers.
- **Next (P1):** 3–5 focused improvements.
- **Later (P2):** Only justified optimizations.
- For each item include `Change | Why | Affected files/modules | Verification / acceptance test | Relative effort (S/M/L)`.
- Prefer incremental reuse of the existing importer, `history-v1`, model/run controls, API, and UI when valid.

### F. Verification gaps and final decision
- List exactly what cannot be validated due to missing datasets, ignored model/prediction artifacts, unavailable execution environment, or insufficient evidence.
- Name the **next three concrete engineering actions** and the **one most important product decision** needed before implementation.

## 5. Acceptance criteria

- The audit references **the actual branch** and actual code locations, not generic advice.
- Every finding has evidence or is explicitly marked unverified.
- Model, rules, offline notebook, and future legal RAG are not conflated.
- The report checks ingestion, data leakage, prediction quality, output behavior, and downstream integration.
- Recommendations are actionable, ordered, minimal, and testable.
- **No repository files or data are modified during the audit.**
