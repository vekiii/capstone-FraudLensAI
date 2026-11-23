# Repair payload within the existing limit

User authorization: commit completed work, then make repair fit the existing
48,000-byte ceiling. Maintenance of FR-013–020/024, not a new evaluation gate.

The preserved DEV4-742 repair measured 49,925 bytes. Its provider report schema
inlines the identical Claim object five times (5,801 bytes total). Represent the
five occurrences by one local `$defs/Claim` and `$ref` entries, a supported
Structured Outputs representation. The expanded schema must equal the previous
provider schema, including all required fields, closed objects, enums and bounds.
Local semantic/conditional/uniqueness validation remains unchanged.

Keep the initial context, every tool call/result, exact evidence/provenance,
invalid draft and opaque reasoning items unchanged and in order. Use the shared
schema consistently from the first turn; no mid-conversation schema switching,
truncation, schema fallback or extra provider requests. Preserve the existing
transport guard and all lower configured ceilings. Larger histories can still
exhaust the limit and must fail before sending.

Validation: intended failing SDK regression with authored large continuation;
schema expansion equivalence and negative constraints; workflow single-repair
accept/reject and accounting; exact offline reconstruction of the preserved
development failure, measured through the real SDK with a mocked transport.
Keep old outputs/scores frozen; offline replay is not LLM quality evaluation.
No new live evaluation batch is needed for this unit. After offline checks, use
the existing synthetic-only provider probe once (maximum two actual transports,
no retries) to verify that the configured model accepts the shared schema. This
separate capability check uses no case/evaluation data and makes no quality claim.
Preserve a hash-verified pre-change runtime snapshot for old source audits. Run
full backend/Ruff and record evidence, including probe failure/unknown usage.

Primary documentation consulted 2026-11-16:

- [Structured Outputs definitions](https://developers.openai.com/api/docs/guides/structured-outputs#definitions-are-supported)
- [Reasoning continuation](https://developers.openai.com/api/docs/guides/reasoning#keeping-reasoning-items-in-context)

The docs support definitions and preserving original ordered continuation. The
49,925 → 46,148 byte estimate is our offline measurement, not a provider claim.
