# FR-021 second candidate approval — 2026-11-20

- Recorded 2026-11-20 19:50 CET (Europe/Belgrade).
- Decision source: explicit user instruction in this Codex chat on 2026-11-20.
- **Approved candidate:** `specs/002-data-and-risk-scoring/t219-training-protocol.ibm-day-60-20-20.macos-preflight-schema-review.candidate.json`.
- **Approved canonical SHA-256:** `1ebac4f24aa198cfd1de70b96204676cb3fbd0cc07786296944c6ade0214f6be`.
- Approved scope: **one second attempt** at the same eight LightGBM configurations on the prepared project data, using four threads, unchanged methodology and the candidate's existing resource ceilings. Proposed output: `data/eval/ibm-day-lightgbm-macos-preflight-schema-review-002`, or a new unique name if that output or its `.incomplete` sibling exists.
- Accepted documented limits: 0.1 s memory sampling may miss shorter spikes; historical source data and the parent feature manifest are not locally available to independently reproduce preparation.
- Preconditions: immediately preceding read-only verification of the exact protocol, all bound implementation hashes, prepared data, `uv.lock` and actual Python 3.14.10 runtime; any mismatch stops the attempt without code/hash adjustments. Preserve local changes, prior protocol and first `.incomplete` diagnostic. No parallel copy or automatic retry.
- Explicit exclusions: no T230, test/showcase label access, model activation, methodology or parameter changes, commit or push. Test predictions may be inspected only for integrity and structure, never joined to labels or evaluated.
- The approved JSON is left byte-for-byte unchanged. This decision is separate from the first-candidate [approval](T219-stagec-protocol-approval-2026-11-20.md), which covered only the failed first attempt. The JSON field `candidate_pending_explicit_human_review` remains as written; this external record provides the approval for the exact digest above.

The [new-candidate review evidence](T228-stagec-preflight-schema-remediation-2026-11-20.md) documents the code, real-input no-fit preflight and remaining limits. This record does not claim a completed fit or evaluation.
