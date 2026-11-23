# Reliability follow-up v2 — 2026-11-16

User-authorized scope: diagnose report failures, time limits and Serbian retrieval,
fix reproducible defects, and write a PowerShell guide under milan (<200 lines).
This is maintenance of FR-007–008, FR-013–018, FR-024–028 and SC-002–006/008.
No producer integration, model switch, new provider calls or acceptance waiver.

## Evidence and evaluation boundary

Baseline checkout: cd98ea021a38b362b5766c4e23a1e55ec0ad0dcd, initially clean.
The committed live/judge/retrieval summaries are available; ignored raw live-v1,
judge-v2 and retrieval-v1 execution archives are absent on this machine. Therefore
aggregate failure codes are observations, not diagnoses of individual drafts or
proof of the cause of the 7496.290-second outlier. Do not reconstruct raw results.

Preserve original protocol, freeze, inputs/references, scores, prompts and result
summaries. Git baseline above retains the original runtime source. Changes below
are a post-evaluation development revision, not the previously frozen runtime.
Historical source-hash audits must use that baseline, not the changed checkout.
Use authored unit/development cases, never held-out reference text for fixes.
New independent quality claims require a new versioned protocol and fresh held-out
questions/scenarios, plus actual provider execution under a separate bounded scope.

## Design

1. Report repair: retain strict local validation and the one-repair/request caps.
   Give the model a fixed allowlisted validation code and corrective instruction,
   never raw exceptions, rejected prose, private fields or evaluator references.
   Record the safe code in the existing private repair audit event. Schema and
   unknown errors receive a generic shape instruction. Legacy repair messages
   remain accepted. Add structural guidance in a new application prompt v2;
   new attempts pin its bytes/hash; retries retain their parent's pinned prompt.
   Reserve the last permitted provider request for drafting (`tool_choice=none`),
   and use the same restriction on the single repair. Do not increase budgets.
2. Deadline/cleanup: provider cleanup currently sits outside the request/attempt
   timeout. Bound asynchronous cleanup by the remaining attempt time (at most
   one second), preserving terminal results when close fails or times out.
   Record only fixed cleanup statuses. This addresses a reproducible cleanup gap,
   not the unproven historical outlier cause. Cooperative asyncio cancellation
   cannot bound a blocked event loop, suspended host or terminated process.
3. Serbian search: add an explicit opt-in, versioned Cyrillic-to-Latin policy to
   glossary lookup. Reuse reviewed translations; add no synonyms/stemming. Reject
   unknown policy names. Preserve legacy scoring and cutoffs when absent.
   Supply a separate development candidate configuration using the existing demo
   heuristic cutoff 0.5, explicitly uncalibrated/unvalidated. No replacement of the
   original demo config or frozen evaluated baseline, no automatic deployment.
4. Regression: test actual SDK serialization over MockTransport, one-repair
   failure, privacy canaries, cancelled cleanup, script equivalence and no-match.
   Run complete backend/Ruff and a local isolated test-provider journey. Frontend
   changes are not planned; fresh frontend checks only if implementation touches it.

## Completion boundary

Passing regression demonstrates these mechanics only. Original quality targets
remain FAILED. T062–T064 producer integration, T066 teammate reproduction/review
and T067 final convergence remain pending. Human review of this maintenance is
pending too. No commit/push, old batch replay or API spending is part of this work.
