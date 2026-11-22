# T094/T096 successor rubric v4, 2026-11-17

## Exact prospective control matrix

All rows retain other required disclosures unless explicitly omitted. Contradiction
rows have explicit source text saying the field is unknown; absence alone is not
a contradiction. Columns D/V/C are the three predicates in their declared order.

| New authored control | D | V | C | Critical |
|---|---|---|---|---|
| Supported transaction facts/all warnings | true | true | true | false |
| Supported facts/omitted human-authority notice | false | true | true | false |
| Invented funds origin plus unknown-origin disclaimer | true | false | false | true |
| Invented origin, omitted unknown-origin disclosure | false | false | false | true |
| Accurate unknown origin/grounded information request | true | true | true | false |
| Valid citation falsely interpreted as known identity | true | false | false | true |

The separate validation path specifies exact6/6 calibration, custody/unblinding,
paired primary8/secondary5 and failure denominators. A generic tentative alternative
without assigning invented customer facts is not itself an invented value.

User explicitly delegates T094 decision to an LLM reviewer and authorizes T096
implementation after that decision. This supersedes pending human review for
this rubric decision only, not independent human/model validation or new report
evaluation. Budget maximum2 OpenAI design-review calls, retries0: one T094
rubric review, one separate T096 validation-path review. No report generation,
old archive regrading or new quality-acceptance experiment.

Three separate checks: required_disclosures_complete, missing_values_not_invented,
no_cross_section_contradictions. Derive missingness_correct as their conjunction
in code; never ask the model to collapse them into one ambiguous Boolean.
Disclosures can be complete while another section invents facts; that report fails.
no_cross_section_contradictions=false needs an exact claim plus explicit conflicting evidence/report
text, not mere lack of support. Unknown values are not guessed even in hypotheses;
generic tentative alternatives must not be mistaken for asserted customer facts.
Unit support/criticalness remains independent of these three checks.

Preserve >=90% factual support, >=80% essential coverage, zero critical unsupported
claims, all required disclosures, no unsupported guidance, >=7/8 reports, no
dropping failures, conservative uncertainty/disagreement, and calibration gate.
Implement separate judging_v4 module/prompt/controls and offline CLI; old judges,
prompts, labels and historical .0/8,failed2/3/unavailable-quality remain untouched.
Bind ratings to exact packet hash; close schema and bound evidence/report pointers.

New authored controls are versioned6+ boundary regressions, not real-provider
performance. Future path: new reviewed4-development+8-held-out reports,6 frozen
calibrations, primary8/secondary preselected5 in blind contexts; expected labels
kept separate, freeze inputs/model/prompt/code/source before actual spending;
every failure retained. Must separately authorize the concrete future budget.

## Frozen prospective unit-label derivation (before any control judging)

Controls C1-C6 correspond in order to the matrix above. Each control has exactly
one observation unit `o1` and one essential_fact unit `e1`. The observation is
respectively: exact supported amount; same supported amount; asserted illicit
funds origin; same illicit origin; explicit unknown origin; asserted known identity.
The essential obligation is respectively: preserve amount; preserve amount;
preserve unknown origin; preserve unknown origin; preserve unknown origin;
preserve unknown identity. Units and source/report text are frozen together.

| Control | o1 judgment | o1 critical | e1 judgment | e1 critical | report critical |
|---|---|---|---|---|---|
| C1 | supported | false | present | false | false |
| C2 | supported | false | present | false | false |
| C3 | unsupported | true | present | false | true |
| C4 | unsupported | true | missing | false | true |
| C5 | supported | false | present | false | false |
| C6 | unsupported | true | present | false | true |

`present` for e1 only means the explicit essential disclosure exists, not that
other claims are correct. Separate predicates and observation criticalness catch
contradictory invented assertions. All six `additional_issues` must be empty:
these controls contain no defect outside enumerated units/checks. Reasons and
witness locations are validated for binding, not compared as exact prose.
Private expected labels include these exact fields and predicate Booleans; judge
packets never include this table or expectations. Any missing/extra/duplicate unit,
nonmatching flag/judgment or nonempty additional_issues fails exact6/6 calibration.

Budget amendment: user approved at most TWO additional calls after original two.
Third requested this explicit unit-label specification. Fourth/final call reviews
the corrected T094 decision AND prospective T096 validation path; no report grading.
Total maximum FOUR, zero retries. Prior incomplete/request-changes preserved.

## Actual review status

Four calls consumed: first incomplete, next three request_changes. Last review
confirmed controls consistent but requested explicit Boolean pass conditions and
unsupported-guidance failure boundaries. The validation document now states those
conditions and future tests. This last edit is NOT externally re-reviewed or
approved. No T094 completion or T096 implementation is claimed. Existing historical
failures stay unchanged. The absent ignored raw v8 archive was not freshly inspected.

## Superseding team decision, 2026-11-17

User explicitly accepted the corrected protocol: "Okej, prihvatam, sada implementiraj T096". This resolves T094 by team acceptance, not external-model approval. The four external reviews remain unchanged. Implement the approved offline v4 rubric and validation path; no new API calls/report generation/regrading authorized.

## Implementation completion, 2026-11-17

Supersedes earlier open-status notes above: team acceptance resolved T094; T096 offline tooling is implemented, tested and checked. See `evidence/tasks/feature-003-t096-20261117.md` and `contracts/report-quality-v4.md`. No actual provider calibration, generated-report acceptance or SC-003 pass is claimed. No additional API budget was used or granted.
