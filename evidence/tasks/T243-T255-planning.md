# T243–T255 remaining-work preparation — 2026-11-21

Prompt: [`002-T243-T255-remaining-work.md`](../../prompts/development/002-T243-T255-remaining-work.md). Scope: inspect all open Feature 002 tasks; prepare the T243 EDA decision, T252 human-review packet, T253 showcase contract and T254/T255 approval plan. No EDA or replay implementation was requested by this evidence record.

## Status and dependencies

The full current `tasks.md` was read. At start, exactly T243–T249 and T252–T255 were unchecked. T243 needs explicit team approval for the fifth UI destination before T247; T244–T246 backend aggregate work is specified independently, with T244 RED before T245/T246. T248 frontend checks follow the EDA contract/view; T249 full regression follows the completed Stage F work. T252 needs actual human reviewers and second-person reproduction. T253 is a design-only contract. T254 and T255 need a separate replay scope approval; T254 synthetic tests precede T255 implementation. The already checked T250/T251/T240 aggregate-results chain is a dependency for the review packet, not an invitation to repeat T230. Later in this unit, T244/T245 were completed and T246 was implemented against synthetic input but left open pending a trusted full-source summary; see their separate evidence.

## Prepared work

- [`feature-002-eda.md`](../../docs/decisions/feature-002-eda.md) records the proposed page, allowed label-free aggregate content, benefit, estimated 3–5 contributor days and explicit pending team decision. T243 remains open; no EDA UI approval was inferred.
- [`feature-002-review.md`](feature-002-review.md) lists the exact protocol, data-card, validation/test, app and limitation evidence for actual reviewers. T252 remains open; no reviewer/date or reproduction result was invented.
- [`showcase.md`](../../specs/002-data-and-risk-scoring/showcase.md) specifies strict preceding-24-hour development context, stable UTC/source-row order, same-instant two-phase feature computation, frozen model/threshold, no-label output and uncapped daily alerts. This is T253's document deliverable only; no replay or label read occurred.

## Concrete replay proposal for separate review

**Decision required:** team approves or defers a later **local, synthetic-data chronological showcase demonstration**. Approval should identify reviewer/date, benefit (demonstrate continuity from frozen development facts to later events), schedule allowance and exact allowed inputs/outputs. Recommend a separate **2–4 contributor-day estimate after verified label-free showcase access and T254 RED tests**; this is planning, not an observed duration. The model acceptance, T230 test evaluation and T253 design do not authorize replay.

If approved: (1) verify source, boundary, feature, model and trusted-manifest hashes and label-free showcase/context input availability; (2) implement T254 synthetic context-edge, same-instant/order, fixed-threshold, no-label and >20-alert RED tests and confirm expected failures; (3) implement T255 bounded, read-only chronological replay with exact context and no ground truth, recording actual review; (4) run relevant regression and inspect output for leaked labels. A missing source/context or hash mismatch is a stop, never a fixture substitution. No model fitting, threshold change, test evaluation, metric computation from showcase labels, or automatic intervention is proposed. T254/T255 stay unchecked until approval and actual work.

## Commands and observations

- `cat AGENTS.md`; `sed -n '1,32p' next_work.md`; `sed -n '1,100p' specs/002-data-and-risk-scoring/tasks.md`; `sed -n '101,150p' specs/002-data-and-risk-scoring/tasks.md`: read governing instructions, latest handoff and all task lines.
- `sed -n '1,170p' specs/002-data-and-risk-scoring/spec.md`; `sed -n '1,130p' specs/002-data-and-risk-scoring/plan.md`; `sed -n '1,130p' specs/002-data-and-risk-scoring/data-model.md`; `sed -n '1,130p' specs/002-data-and-risk-scoring/contracts/api.md`: inspected FR-035–039 and design boundaries.
- `rg -n '^- \\[ \\]' specs/002-data-and-risk-scoring/tasks.md`: the first search also included section/ID patterns and found the eleven open tasks; no code tests, data scans, model evaluations or browser checks were run for this documentation work.

**Limitations:** EDA team decision is pending; T246–T249 remain open. The current local `data/processed/` listing lacks a precomputed EDA summary; a future aggregate publisher must use verified label-free input and avoid reading target values. Human review/reproduction and replay approval are pending. No commit or push was made.
