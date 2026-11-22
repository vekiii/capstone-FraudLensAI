# Request timeout and quota follow-up v3 — 2026-11-16

User authorizes continued timeout diagnosis/repair and additional live checks;
reported several-hour reset is unverified account information, not permission to
assume that every error is quota or that a specific reset time is known.
Baseline feature03-reliability-v2 at46a15ed, initially clean. Scoped maintenance
of FR-017–020/024/028, no public contracts, model, prompt or limit changes.

## Diagnosis and design

Saved DEV2-701 dispatch5 entered transport but no headers returned for29.987s;
attempt ended37.971s,5 requests. This supports expiration of the30s request timer,
not8-request/120s exhaustion; provider/network cause and usage remain unknown.
Do not replay DEV2-701 or change its sealed failure.

SDK APITimeoutError currently maps to retryable provider_failure, while the
asyncio provider/workflow deadline maps to fatal budget_exhausted. Normalize a
single-request timeout to retryable provider_failure only while the absolute
attempt deadline and request slots permit the existing one transient retry.
Persist first dispatch as unknown before retry. A total-attempt deadline remains
budget_exhausted, no retry; no hidden SDK retries or automatic restart/reopen spend.
Retrying an unknown provider outcome can incur extra spend; no exactly-once claim.

Add private allowlisted diagnostics (reason, HTTP status, known provider error
code), never exception text, raw error body or arbitrary headers. Keep the closed
public Failure shape/codes unchanged. Distinguish request_timeout, attempt_timeout,
connection_error, rate_limit, quota_exhausted and generic HTTP errors. Known billing,
credit/usage/spend errors or insufficient_quota type are nonretryable; ordinary
rate-limit/server transients retain one retry with existing <=2s backoff ceiling.
Record diagnostics on dispatch/failure/retry audit events; no schema migration.

Official sources checked for classification:
https://developers.openai.com/api/docs/guides/error-codes
https://help.openai.com/en/articles/6614457-troubleshooting-api-usage-and-spend-limits
Installed SDK exception attributes verified locally, no dependency upgrade.

## Verification and live boundary

RED→GREEN: actual SDK timeout over MockTransport; successful one-time recovery;
repeated timeout; no time/slot remaining; unknown outcome accounting; quota vs
rate-limit codes including credit_balance_exhausted; canary privacy; old recovery
and cancellation behavior. Full backend/Ruff, no frontend changes planned.

New development-v3 pack uses3 fresh synthetic cases, separate references, immutable
source/protocol freeze and a separate max25 ledger (8/case+1 stateless batch judge).
Reuse tested v2 runner functions through an explicit adapter; do not modify v2
runner/inputs/results or spend its unused attempts. One batch only, no tuning
between outcomes. Stop dispatching further cases after reported credit/quota or
access rejection. No hours-long automatic waits or speculative billing diagnosis.
These are authored development checks, not a new independent holdout, a comparable
before/after study or completion of original failed release criteria.

Record actual diagnostics/usage/latencies, limitations and pending human/producer
review. Existing old source-hash audits require their baseline checkout after
runtime changes. No automatic commit/push in this follow-up.
