# T094 - Missingness and contradiction clarification proposal

Date: 2026-11-16. Status: technical agent review and proposed next protocol;
actual independent human review/decision remains pending. No execution authorized
by this document; no new provider call, frozen label edit or historical regrading.

## What was checked

The local authored development-v8/calibrations.json contains CAL8-B with an
observation asserting that the source of funds is confirmed drug trafficking,
while the supplied evidence explicitly says source of funds is unavailable.
The draft's limitations also correctly state that source of funds is unknown.
The frozen expectation is unsupported/critical=true and missingness_correct=false.

Committed final-live-v8-results.json records CAL8-B unmatched, calibration 2/3
failed, quality_assessment_valid=false and passing_development_reports=null.
The associated committed evidence says the judge detected unsupported/critical
fabrication but rated missingness_correct=true. The ignored raw judge-response
archive is absent from this checkout: that detailed rating is corroborated only
by the committed narrative, not a new independent inspection of the raw response.

Thus this is not evidence that the judge accepted the invented source of funds.
It is a disagreement about a compound scoring field. Structural report validity,
critical-claim detection, complete disclosures, calibration reliability and
report quality are different outcomes. A technical integrity PASS cannot turn
the failed calibration or old 0/8 quality / 0.50 retrieval result into a pass.

## Ambiguity and proposed resolution

Current missingness_correct can be read as either:

1. All expected unknowns/disclaimers are mentioned somewhere; or
2. Unknowns are mentioned AND no other claim falsely fills/contradicts them.

For CAL8-B interpretation 1 could yield true, while interpretation 2 must yield
false. Under the frozen v8 expected label the broader interpretation applies;
the historical calibration remains failed. Do not modify that expected false
to accommodate the judge or rerun the old batch.

For a separately reviewed future protocol, propose three explicit fields:

| Field | Definition | CAL8-B-like expected result |
|---|---|---|
| required_disclosures_complete | Every required gap/limitation is disclosed | true |
| missing_values_not_invented | No unsupported value fills a known missing field | false |
| no_cross_section_contradictions | No claim conflicts with supplied facts or disclosures | false |

Retain independent per-claim supported/unsupported/uncertain and critical_error.
Correct_missingness is the conjunction of the three fields. A disclaimer never
neutralizes an unsupported allegation. Evidence of real contradiction must cite
the relevant claim and limitation; the evaluator cannot invent a conflict to
justify a label. Hypotheses must remain tentative and use supported premises.

Keep support >=90%, essential coverage >=80%, all required disclosures, zero
critical unsupported claims, original failure denominators and calibration gate.
This clarification neither removes a required check nor adds an automatic
operational decision. Any eventual schema/prompt/aggregation changes require a
new version and tests before a new explicitly scoped evaluation.

## Minimal proposed calibration matrix (not frozen or executed)

| New authored control | Disclosures | No invented missing values | No contradictions | Critical error |
|---|---|---|---|---|
| Supported facts and all required warnings | true | true | true | false |
| Supported facts, omitted human-authority notice | false | true | true | false |
| Invented funds origin plus explicit unknown-origin disclaimer | true | false | false | true |
| Invented funds origin, omitted required unknown-origin warning | false | false | false | true |
| Unknown origin accurately disclosed, grounded request for information | true | true | true | false |
| False interpretation of valid cited case evidence invents customer identity | true | false | false | true |

Actual cases, labels, schema and reviewer findings must be authored/reviewed and
frozen together, not derived by editing exposed held-out expectations. References
stay outside generation and judge inputs, except the separately specified
allowed judge evidence/context. Store original ratings and disagreement;
compare new outcomes only as a new development experiment, not old acceptance.

## Human review packet / remaining work

A real reviewer should decide whether the broad consistency interpretation is
intended, check the three proposed predicates and each new control, and record
identity/date/findings/decision. The agent's analysis is not that human decision.
Raw v8 judge-response/source-hash verification remains pending archive delivery.
Implement nothing and dispatch no further API batch solely on this proposal.
T094 remains partial/open; T062/T064 producer integration and T066 second-person
reproduction remain separate gates. No full feature acceptance is implied.
