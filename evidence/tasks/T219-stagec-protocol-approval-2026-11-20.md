# FR-021 Stage C protocol approval — 2026-11-20

- Recorded at: 2026-11-20 19:34 CET (Europe/Belgrade).
- Decision source: explicit user instruction in this Codex chat on 2026-11-20; the user approves the exact canonical SHA-256 below and accepts the documented 0.1 s memory-sampling limitation.
- Approved file: `specs/002-data-and-risk-scoring/t219-training-protocol.ibm-day-60-20-20.macos-resource-review.candidate.json`.
- **Approved canonical SHA-256:** `90b2aaa07590f771343e30f7843078f2dbd71d26679040cdafc33a5fbe5c67cf`.
- Approved execution scope: the eight defined LightGBM configurations on prepared project data, with four worker threads, under the unchanged protocol and resource ceilings. The specified output is `data/eval/ibm-day-lightgbm-macos-resource-review-001`, or a new unique name if either it or its `.incomplete` sibling already exists.
- Explicit exclusions: no T230 evaluation, test/showcase label access, methodology change, model activation, commit or push. Frozen test predictions may be checked for integrity and structure only.
- The approved JSON is left byte-for-byte unchanged. Approval is external evidence and does not change its pending-human-review field or canonical digest.
- Execution remains conditional on immediately preceding read-only verification of the candidate, implementation hashes, prepared inputs and `uv.lock`, plus Python 3.14.10 and locked dependency versions. A mismatch stops execution; no expected hash may be adjusted.

The earlier [review evidence](T219-stagec-macos-resource-review-2026-11-20.md) describes the candidate and its limits. This record documents the later user decision, not a claim that training or T230 has completed.
