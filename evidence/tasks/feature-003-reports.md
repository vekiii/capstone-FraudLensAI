# T025/T026 report validation - 2026-11-14

Baseline 1a99c34, Phase 4. Executed RED: 27 failures on an importable
NotImplementedError boundary. GREEN: all 27 report checks PASS. Initial Ruff
reported 19 E701 formatting errors in the new tests; formatted new files and
reran backend Ruff successfully. No assertions weakened.

Checks cover closed draft/report schema, attempt/context ownership, duplicate/
unknown references, exact content hashes, procedure text/corpus/digest, claim and
evidence kinds, exact structured values/quotes, citation completeness, limitation
disclosure, typed hypotheses and limitation-only needs-information drafts.
Assigned report digest matches the repository's immutable report identity.

The deliberate valid-ID false-interpretation example passes structural checks
but remains semantic_review=not_reviewed. This demonstrates the limit rather
than claiming arbitrary prose truth is deterministically guaranteed. No actual
provider report or human quality rating performed.
