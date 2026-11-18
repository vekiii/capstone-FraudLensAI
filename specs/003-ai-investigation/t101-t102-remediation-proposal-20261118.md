# T101/T102 remediation review — proposal, no new tasks

Actual reviewed run: original schema400 corrected; successor six-control calibration
returns valid structured ratings but exact gate2/6. Fresh external timing returns
2/5 useful drafts, all5 visibly terminal<=120; local20 p95.0032897000201046467s.
No429 observed; all27 timing calls HTTP200. Three timing cases fail strict semantic
selection on duplicate source IDs. A longer request timeout cannot fix that.

User now authorizes repeating interrupted batches and waiting on actual rate-limit
signals, within155 total. Operational retry permission does not make semantically
failed calibration into a pass, erase observed performance failures or authorize
changing private gold after seeing results. No new task is needed or added.

## Concrete calibration candidate for review

[`report-quality-v4-controls-v2-proposed`](../../evals/investigation/report-quality-v4-controls-v2-proposed/README.md)
contains all six actual public report/source/unit objects and separate proposed
private expectations. Known amount is explicit in every control, and every
repeated assertion has a unit. This addresses two observed evaluation confounders,
while invented funds/identity still fail critically and omission of human authority
still fails. Do not regrade original2/6 or claim this unexecuted draft passed.

Review is necessary because these are changed control inputs AFTER unblinding,
not a transport retry. The approved validation path requires new versions/reviewed
inputs and a new freeze before further acceptance. Old sources/prompt/model/gold
and results remain available unchanged. Eight quality scenarios were never sent
and no quality rating is currently valid; review the prospective held-out boundary
before reusing or authoring a successor pack. No old held-out outcome may be tuned.

## Proposed selector clarification, not activated

Keep current v6 source and accepted T095 results intact. The exact candidate
addition for a separately versioned prompt/profile is:

```text
Select each passage_id at most once. When several statements come from one
passage, return one item for that passage with one short contiguous quote.
Copy the quote literally from the supplied text, preserving whitespace and
line breaks. Do not combine separated sentences, paraphrase or normalize a
quotation. Verify the ID is unique and the exact quote occurs in that passage
before returning the selection.
```

This reinforces existing output constraints; it does not add a glossary, relax
matching, silently deduplicate/repair outputs or turn a failed provider call into
a successful no-match. No active prompt, policy hash, default/source schema or
validator has changed. Any activation needs a new version/freeze and relevant
development/retrieval checks; historical T095 acceptance remains bound to v6.
Do not infer new-policy retrieval quality from the old numeric result.

## Thirty-second hypothesis and criteria

One actual successful final drafting request took28.5124848s, another20.6338413s;
the earlier development call timed out at30s with no response/usage. The cap is
close enough to merit a controlled future comparison. Current failures are not
all timeout failures: three timing failures occur after4.4–6.7s semantic responses
with duplicate IDs. All timing attempts are visibly terminal in10.17–41.30s.

Proposed order: first address source-selection formatting and calibration isolation;
keep30/120 limits and90/120 acceptance targets during that work. If an increased
request cap is then reviewed, implement a separately versioned bounded setting
and actual fresh measurement; keep total120 and useful<=90 criteria unchanged.
The current schema/provider hard-cap30 is deliberate; no ad-hoc environment45/60
override or mid-batch change was made. Waiting is appropriate for actual transient
429/5xx, not a400 schema error or an invalid exact quote.

## Budget and decision

Actual total56 of155 attempts; one initial unknown usage and one400 remain counted.
The corrected six-control retry succeeded at transport, so further repetition
solely to hunt for favorable ratings is not proposed. No paid calls for this draft.
Future combined quality/performance revisions must allocate remaining99 requests
explicitly and preserve all first-attempt failures; cannot promise all conservative
stage maxima plus repeats will fit99. No budget increase/new task is inferred.

Recommended next step: review the six-control corrective draft and proposed
selector clarification as work inside T101/T102 before activating any changed
evaluation/source profile or spending on fresh holdout. Keep task markers open
and feature003 unclosed until the unchanged quality/performance criteria pass.
