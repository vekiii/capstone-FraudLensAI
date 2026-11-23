# Draft: Local LightGBM contributions for published model alerts

Base: `main`. Head: `feature/002-model-contributions`. **Draft only; Feature 003 contract review pending.** The user's explicit chat confirmation allowed a successful remote fetch and ancestor check before publication.

## Scope

- Compute native `pred_contrib` on the trusted frozen LightGBM and identical 32-column preprocessing, check additive raw log-odds and score reconstruction, and group all one-hot contributions into the 11 source features.
- Produce a separately pinned, versioned, opt-in sidecar with exact model, feature, case, assessment and context identities; expose bounded top-three/remainder through the API, new investigation evidence and a separate React view. Existing bridge publication and saved v2 reports remain unchanged.
- Clarify that the model really predicts on synthetic inputs while the LLM describes that prediction. Preserve the first LIVE report's failed factual review and the two later post-correction outcomes.
- Keep provider input at 48,000 bytes with explicit failure; no silent truncation. Add exact initial/repair boundary and audit regressions.

## Verification

- 65/65 published alerts retain exact score and status; maximum raw additive error `1.199040866595169e-13`, grouped sum error `1.7763568394002505e-15`, score reconstruction error `1.1102230246251565e-16`.
- Backend: 1,453 passed, 1 skipped (missing local authorized aggregate reports); React: 295 passed; typecheck, build, Ruff and diff checks passed. Initial and repair HTTP-body tests accept 48,000 bytes and reject 48,001 locally. Oversized repair ends with audited `budget_exhausted` and no new HTTP dispatch.
- Offline current-builder full drafting turns: row 1500153 `45,695 B`, row 2959955 `28,938 B`; actual post-correction LIVE maximum was `47,915 B`. The latter leaves 85 B headroom, a remaining limit for future continuations.
- Local read-only API/proxy GETs reopened both saved reports, all 11 cited evidence records and a copied test-provider opt-out report. Browser automation was disabled; user visual review is pending. No provider call was made during final review.

## Review requests for Feature 003 owner

1. Confirm separate sidecar v1 and `lightgbm_pred_contrib_log_odds_v1`, with log-odds wording, model/manifest/matrix/snapshot/context bindings, and fail-closed mismatch/unavailable semantics.
2. Confirm top-three deterministic ordering, full one-hot grouping including inactive columns, signed remainder, evidence digest and distinct `log1p` observed amount versus original money fact.
3. Confirm bounded provider projection and treatment of near-limit saved continuations without silently dropping facts, procedure text or citations.
4. Inspect the manual React URLs and the distinct `needs_information` and `ready_for_review` saved outcomes; decide whether the proposed contract can be accepted. This PR does not claim human acceptance or independent model evaluation.

Evidence: `evidence/tasks/002-003-final-local-review-2026-11-23.md`, `evidence/tasks/002-003-local-contributions-live-demo-2026-11-23.md`, `evidence/tasks/002-003-local-contributions-live-recheck-2026-11-23.md`, and `specs/003-ai-investigation/contracts/local-lightgbm-contributions-proposal-v1.md`.
