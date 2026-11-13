# Prompt 1 technical approval and pinned-source verification authorization

Received 2026-11-13 Europe/Belgrade. Original user instruction:

> Continue Prompt 1 and resolve all remaining technical and source-verification work within T006–T008. Do not perform or invent team review.
>
> Read AGENTS.md, next_work.md, the relevant tasks/evidence, and the complete review packet in specs/002-data-and-risk-scoring/proposals/.
>
> I approve the proposed technical direction, including:
> - Exact source-bound positional mapping of the two Account columns.
> - Currency length 17 with original source values preserved.
> - Required detail-envelope dataset_version and cross-object equality rules.
> - Strict terminal-pattern corrections.
> - The synthetic UTC+00 convention, explicitly recorded as an assumption, preserving raw timestamps and minute ties rather than claiming source UTC.
>
> I authorize downloading only HI-Small_Trans.csv from pinned Kaggle version 8 into a separate ignored directory and comparing its SHA-256 with the existing file. Preserve the existing CSV unchanged. Use existing tooling where possible; if necessary, use a temporary isolated download tool without changing project dependencies. If account access is required, give me the exact necessary step; never put credentials in files tracked by Git.
>
> If the CSV hashes match, record the verified v8 equivalence and adopt v8 as the reproducible reference, while retaining unknown original acquisition history. If they differ, preserve both files and report the mismatch without silently replacing the selected source.
>
> Verify the release-specific license and remaining source semantics, including binary label meaning. Distinguish documented facts from approved assumptions; do not invent unavailable evidence.
>
> Complete the technical mapping and contract amendments supported by the evidence and my approval. Update affected feature documentation, schemas, examples, inspection behavior/tests where applicable, and evidence consistently. Keep mapping/configuration explicitly pending team review and prevent its use for import until the required gates are satisfied. Preserve Foundation v1.
>
> Run the relevant checks for actual changes. Update tasks and next_work.md truthfully: completed technical work may be recorded, but T007/T008 must not be marked fully complete while required human review remains pending.
>
> Finish all independent work before returning. Report exactly what was resolved and any remaining external evidence or team-review requirements. Do not start Prompt 2, import, training, or application v2 integration. Do not commit or push.

This is user technical approval and scoped download authorization. It is not a record of producer/affected-consumer team review.
