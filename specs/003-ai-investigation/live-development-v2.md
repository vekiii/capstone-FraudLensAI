# Live development protocol v2 — 2026-11-16

Scope: actual gpt-6-luna reports after reliability-v2, three freshly authored
synthetic DEVELOPMENT cases. Author: coding assistant; independent human review
of inputs/expectations is pending. This is neither a replacement for old outcomes
nor a new independent holdout or SC-003/SC-006 release evaluation.

The user authorized publication and live checks in the linked development prompt.
Operator cap:25 total transport attempts, at most8 for each of three cases and1
stateless batch judge. Connection failures count. SDK/HTTP hidden retries off;
existing application one transient retry/one repair remain within8,30s/request,
120s/attempt,4096 output tokens,48kB input and2MiB response. Judge: one request,
60s,8192 output tokens, no tools/retries/continuation, store=false. Stop on access
rejection; no repeated case after any saved/unknown dispatch and no budget reuse.

## Cases frozen before dispatch

1. DEV2-701: new exact EUR focal transfer with authored PARTIAL prior history,
   two prior events in different currencies. Include same-minute/future/focal
   events in the input history fixture to verify scope filtering; never pass them
   as allowed evidence. Preserve per-currency totals, cutoff and missing KYC.
2. DEV2-702: new smaller GBP transfer, unavailable history/customer context.
   Distinguish missing from empty; fixture score is not calibrated probability.
3. DEV2-703: new USD transfer with unavailable history and deliberately forced
   no-match procedure retrieval via a separately pinned high cutoff. This is an
   explicitly controlled no-guidance fixture, not evidence of retrieval quality.

Generation reads only new inputs/protocol/runtime corpus. Expectations in separate
reference.json never enter runtime/retrieval/continuations. Pin files/code/prompt,
model/settings and both candidate/control retrieval hashes BEFORE I/O. Hashing
reference bytes for freeze is allowed; parse references only after all reports are
sealed. Do not tune implementation/prompt/config between these executions.

## Outcomes and assessment

Preserve every failure, usage-known/unknown, durations, safe provider IDs, request
and tool traces and exact returned private provider items in ignored
evals/results/feature-003/development-v2/. Durable ledger reserves before I/O;
exclusive seals prevent overwrites. No automatic replay after ambiguous crash.

Reuse strict local report validation. Post-generation, a single stateless judge
rates each observational/procedural unit and each predeclared essential fact,
plus whole-report unsupported prose, critical errors and missingness. Use existing
rating validation/aggregation; failed reports stay in denominator, absent/invalid
judge results are unavailable, never passes. Same-model single-judge assessment
is automated development evidence, not independent human validation.

For development reporting retain >=90% factual support, >=80% essential coverage,
zero unsupported procedures/critical errors and correct missingness. Publish exact
denominators and all3 outcomes, including no-report/judge failures. Report <=90s
success and120s termination descriptively; do not claim the separate five-case
release target. No spend estimate without verified pricing. Preserve old failed
quality/retrieval/timing evidence. Source freeze belongs to this new revision.

After completion publish only safe aggregate evidence on the new branch and update
next_work.md. Local milan guide remains ignored as previously documented. No API
key, SQLite, raw model output or encrypted reasoning is committed.
