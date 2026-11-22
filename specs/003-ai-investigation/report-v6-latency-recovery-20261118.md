# Report v6 latency recovery, 2026-11-18

The failed request was the drafting turn after five successful calls. The ledger
has no HTTP response and no token usage for it. Two successful drafts used 2,971
and 1,995 output tokens, including 516 and 448 reasoning tokens. A transport or
provider cause more specific than a request deadline cannot be confirmed.

Use a separately frozen OpenAI semantic v8/report v6 run with explicit low report
reasoning effort and a 60-second maximum for the generation request. Preserve the
120-second attempt deadline, 90-second measured success target, 30-second selector
limit and 8,192 output tokens. Unknown outcomes remain counted and are never
replayed. Local provider and metered evaluation read the same saved settings.
No changes to scoring, inputs, passage selection, or judge rules.

User asked to iterate and perform final evaluation when the remedy passes. Keep
the last explicit total ceiling of 303, starting at 168. Allocate up to 24 requests
for four fresh development cases, 44 for retrieval, 48 for eight final generation
cases, six to repeat the unchanged judge controls because the previously qualified
raw calibration is unavailable locally, and 13 for final judging. The final six
calls are taken from the planned 54 generation allowance.
Final criteria and required sample counts are unchanged. Preserve every old result.

## Calibration correction and remaining 61 requests

The new v4 calibration was 5/6. C4 correctly found the invented assertion and
marked the report critical, but also marked the omitted disclosure obligation
critical. Refine judge instructions so omission stays a coverage/disclosure issue
and the actual assertion retains its critical flag. No thresholds, expected
ratings, rubric or old artifacts change. Run all six controls with the new prompt.

For the same v8 retrieval and v6 evidence contract, allow the generator to ask for
both existing read-only history tools in one provider turn via explicit saved opt-in.
Calls still execute individually with existing scope, schema, count and time guards.
The matching opt-in prompt addendum encourages grouping, with no change to eligible
sources, history facts, action permissions or limits. Test this wiring offline.
Use at most 42 final generation sends after six calibration requests, then 13
isolated final ratings. This fits 303 total from 242 already recorded. Missing
slots stay in the denominator. No automatic paid repeat beyond that ceiling.

## Source status and draft shape follow-up

A versioned opt-in generator profile carries the nonempty summary and observation
requirements into the provider schema once the actual case-facts tool has returned
an authorized evidence item. Local validation stays unchanged. The new prompt
states the required sections before drafting. Report generation and evaluation
retain their previous isolation, limits and thresholds.

The opt-in evaluation packet includes the projected search status applied after a
completed semantic selection. The persisted `insufficient` verdict with zero
selected passages yields `no_match` under the existing application projection.
This is a tool outcome, not a claim that no relevant procedure exists anywhere.
Future ratings use fresh cases. Previously exposed reports and ratings are saved.
