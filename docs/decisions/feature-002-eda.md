# Feature 002: dedicated EDA page proposal

**Status:** team approval reported by the user on 2026-11-21 (T243 / FR-038). The approved scope and planning impact are recorded below.

## Proposed scope

Add one separately navigable, read-only EDA page to the local FastAPI and vanilla TypeScript application. The page would show:

- source identity (exact local HI-Small source SHA-256 and data/summary version), synthetic origin, UTC coverage and the documented upstream release/timezone limits;
- source, accepted, rejected, warm-up and scoreable counts, with the denominator stated for each quality count/percentage;
- bounded distributions of sender and receiver bank **categories**, payment and receiving currencies, and payment format; no account identifiers;
- bounded UTC time buckets and transaction-count charts, each with a defined denominator; and
- amount distributions separated by currency and by paid/received side, with currency units, bucket definitions and denominators. No cross-currency total or conversion.

Only verified, label-free source/canonical fields and precomputed Python aggregates may feed the page. The browser receives a bounded versioned summary, never the full CSV, individual transactions, target labels, label-derived rates or restricted audit outputs. A missing or invalid aggregate is shown as unavailable; charts also need accessible text/table equivalents, loading, empty, malformed and retry states. Preserve existing fixture and prediction/results routes. Prefer native HTML/CSS/SVG over a new chart package unless a measured accessibility or compatibility need justifies it.

## Benefit and schedule impact

The page lets an analyst inspect source coverage and quality beside the risk workflow, and demonstrates that aggregate distributions and monetary units are traceable without exposing labels. It is a **fifth destination beyond the constitution's four-screen MVP**. Its implementation adds T244–T249: synthetic RED checks, Python aggregate and closed API contracts, a bounded endpoint, accessible navigation/charts and states, frontend decoder tests, and full regression/evidence. A planning estimate is **3–5 contributor days after approval and verified aggregate inputs**, including review and regressions; this is an estimate, not an observed duration or delivery commitment. It may shift other MVP work by the same capacity and requires a reviewer for the additional UI surface. If the team declines or defers, T247–T249 stay open/deferred and the existing four-screen scope is retained. Backend aggregate work T244–T246 is specified independently, but any public EDA route should be reviewed for consistency with the page decision before exposure.

## Decision and authorization

The proposal asked the team to approve the dedicated EDA page and its 3–5 contributor-day planning allowance, or defer it from the current MVP. The actual decision was required before T247 UI implementation.

**Actual team decision:** The user confirms that the team approved the additional dedicated EDA page as proposed, including the described scope and recorded 3–5 contributor-day planning impact. This is the user's report of the team decision; individual names, votes, reviewers and separate confirmations were not supplied or inferred. T247–T249 may proceed within this scope. This does not approve showcase replay, new training, test evaluation, label access or production deployment.
