# T101 authorized continuation and calibration wire correction — 2026-11-18

## Authorization and immutable inputs

User annotated "Predlažem nastavak samo tri neposlata slučaja" with "u redu radi
tako". Continued only DEVQ1-02/03/04, max24 new requests, retaining failed DEVQ1-01
and its6 actual attempts. Same `gpt-6-luna`, prompts, semantic v6 source/policy,
source contexts, validators,30s request/120s attempt and8-request/12-tool limits.
Original separate115 T101+40 T102=155 maximum remains. No new tasks/commit/push/
merge/training. Root AGENTS/next_work read; explicit feature003 Spec-kit selection;
requirements checklist remains16/16, no extensions/hooks or marker changes.

Fresh continuation folder under ignored
`evals/results/feature-003/acceptance-live-20261118/development-continuation/`.
Its exclusive input file contains exactly the three previously frozen undispatched
objects. Freeze pins original runtime sources, new input bytes, prior immutable
ledger and continuation proposal. Source pins matched before and after execution.
Freeze SHA `ef045b36b3b2011769f3185756fbab2cb08399bc3f43b88d47bf4146827cd297`.
New hash-bound approval records the actual continuation decision; original ledger
was neither reset nor changed. API/worker and external observer run as separate
hidden processes via the prepared supervisor, with a fresh idle queue.

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe .cache/t101-live-supervisor.py --batch evals/results/feature-003/acceptance-live-20261118/development-continuation
```

## Actual development outcomes and exact rejection reasons

| Slot | First GET-visible seconds | State | Locally validated report |
| --- | ---: | --- | --- |
| DEVQ1-01, retained prior run | 45.65846850001253 | failed | no |
| DEVQ1-02 | 14.05758100003004 | failed | no |
| DEVQ1-03 | 10.480558699986432 | failed | no |
| DEVQ1-04 | 21.924909299996216 | needs_information | yes |

Continuation consumed **16 actual transport requests**, all HTTP200 with complete
saved responses; known usage **44526 tokens**. No new unknown TRANSPORT delivery
outcome. Combined development: **22 attempts**,21 complete+the original1unknown;
known usage58438 tokens plus unknown first-batch sixth usage, never counted as zero.

DEVQ1-02: semantic selector returned five entries but repeated two passage IDs.
All quote texts were exact; two duplicate IDs violated the existing unique-source
contract. DEVQ1-03: selected three distinct known sources, but the third quote was
not an exact substring. Both selections were correctly rejected by unchanged
`validate_selection`; neither was silently deduplicated, normalized or published.
Their reports are absent and failures remain in the four-slot development record.
Application maps these parsing failures to context_unavailable/outcome_unknown=true;
the complete transport archive establishes the provider responses were received.
Do not confuse that generic application flag with a new network timeout.

DEVQ1-04: actual semantic insufficient result with selected=[], then a locally
validated needs_information report. It preserves129.56EUR/TX-904/source event time,
score.34 as illustrative fixture/nonprobability, unavailable histories, customer
unknowns and final human authority. It asserts no Portuguese legal deadline and
has no recommended procedure. This is software source/reference validation and
offline development inspection, **not calibrated semantic report-quality PASS**.

No development replay or replacement. One of four development slots has a saved
validated report. Before any held-out evaluation, this actual low readiness and
the two strict selector failures must remain visible; no favorable subset claim.

## Actual calibration attempt — API rejection, no model rating

After development inspection, prepared the six frozen public v4 controls and
their separate private expectation hash. Original user approval covers6 actual
calibration calls in T101; created a separate stage-specific hash-bound record,
with all22 prior actual requests explicitly accounted. A future judge driver was
first tested with four mock-only integrations: six isolated public packets/no
private expectation load, invalid packet binding retained, quota stop/no hidden
SDK retry and missing approval zero dispatch. All4 passed with mock transport,
not real calibration results.

Started the approved actual six-control stage:

```powershell
.venv/Scripts/python.exe evidence/tasks/feature-003-t101-judge-live-20261118.py prepare --batch evals/results/feature-003/acceptance-live-20261118/calibration
.venv/Scripts/python.exe evidence/tasks/feature-003-t101-judge-live-20261118.py run --batch evals/results/feature-003/acceptance-live-20261118/calibration --approval evals/results/feature-003/acceptance-live-20261118/calibration/approval.json
.venv/Scripts/python.exe evidence/tasks/feature-003-t101-judge-live-20261118.py assess --batch evals/results/feature-003/acceptance-live-20261118/calibration
```

First request C1 returned **HTTP400 invalid_json_schema**: uniqueItems is not
permitted in report_locations of required_disclosures_complete. Driver error:
the original local v4 JSON schema was passed directly instead of compiling the
provider-compatible subset. The existing application report compiler already
omits uniqueItems and enforces it locally; the new judge driver missed that step.
This was a request-construction defect, not evidence of model misgrading.

Ledger stopped automatically on400, **one actual attempted request, zero ratings,
five controls not dispatched**. No SDK retry/fallback/probe. Offline assess retains
all6 control slots with passed=false/unmatched; **zero valid ratings of six**, not
a claim that the model semantically got six answers wrong. Quality assessment is
unavailable. No eight held-out reports, paired judges or T102 live batch started.
Actual overall count is now **23 requests**, including this400 and original unknown.
Calibration usage is absent; no dollar-cost or zero-billing assertion.

Original freeze SHA:
`9ff14aefd0fc8b220494802ee03102a6658697f708aaa15370224d7fdbade7cb`.
Exact executed judge source saved as calibration/runner-original.py BEFORE fixing;
its hash and original raw request/response/error/freeze/ratings/assessment remain.
No old result was regraded or overwritten.

## Offline correction, no paid retest

Added a mock that rejects uniqueItems exactly as the actual API did. Intended
RED:1failed/4passed, first call400 instead of six completed controls. Corrected
only the operational judge wire-schema compiler: recursively omit uniqueItems,
preserve closed shapes/required fields/enums, validate each returned rating with
the unchanged full original RATING_SCHEMA and v4 binding predicates. No prompt,
rubric, expected control, runtime source contract or acceptance threshold changed.
Future preparation saves/hashes both local and wire schemas separately.

GREEN5 mock-driver tests, including duplicate report_locations still rejected by
the original local validator and original schema deep-equality unchanged. Combined
judge/helper/observer/v4 regression **75PASS3.67s**, Ruff/format/diff PASS. No full
backend rerun this unit; production runtime unchanged from earlier1112PASS.
No actual-provider validation of the corrected wire schema yet. An initial
diagnostic command lacked PYTHONPATH and failed import; corrected process-local
PYTHONPATH, then exact quote/ID checks succeeded. No data/source change needed.

## Decision boundary within existing T101/T102

Corrected code is ready for a newly frozen calibration attempt; it must not replay
or reset the stopped calibration folder. Proposed six new actual calibration
requests, same model/judge prompt/control sources/local rubric. The failed API
attempt remains counted: calibration would total7 attempts, requiring explicit
reallocation of one call from unused development allowance. Original T101115 and
total155 caps need not increase: development22+calibration7+quality64+paired13=106;
with timing40, full maximum146<=155. No new task is proposed.

Concrete offline proposal saved at
`evals/results/feature-003/acceptance-live-20261118/calibration-wire-fix-proposal.json`.
The corrected six-packet stage is actually prepared, not an executable placeholder:
`calibration-wire-v2/`, freeze SHA
`06160f1296cf881f2a538b154c91180e7e587dfaa5c740fc1f2b559d7fd802e8`.
All pinned hashes verified, dispatch ledger0 rows, no approval.json. The sibling
`calibration-wire-fix-ready.json` records exact stage/hash/cap/reallocation scope.
No new-calibration authorization record or dispatch after the400 stop. Discuss
this retry decision with the user. Known selector contract failures also need a
decision before burning fresh holdout; no unapproved prompt/policy change or
automatic retrieval reevaluation was introduced. Feature003 remains unready.

[Machine-readable actual outcomes](feature-003-t101-continuation-20261118-results.json).
