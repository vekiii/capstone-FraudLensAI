# Offline materialized report-grading contract v4

This is an offline evaluator contract, not a new HTTP/worker/runtime report schema.
The user accepted the corrected rubric and validation path on 2026-11-17. Existing
API reports, generation prompts, old judges and prior raw results are untouched.

`judging_v4.project_packet(raw)` takes `scenario_id`, `role`
(`calibration|primary|secondary`), Boolean `failed`, `report`, `evidence`, `units`.
It explicitly projects:

- Report: six text sections `summary`, `observations`, `missing_information`,
  `limitations`, `recommended_checks`, `alternative_explanations`. Absent sections
  become empty strings. A custodian materializes structured runtime report content
  into these sections with exact wording, including all factual/procedural prose;
  this module does not silently adapt arbitrary runtime report objects.
- Evidence: unique `evidence_id`, exact `text`. The custodian must authorize these
  sources for that report/attempt before projection. No reference-answer metadata.
- Units: unique `unit_id`, `claim_kind` (`observation|procedure|essential_fact`),
  `text`, `location`, `evidence_refs`. Locations are report-relative JSON pointers;
  essential obligations may have empty location because an absent expected fact
  has no report span. Obligations are predeclared from sources before generation.
  Observation/procedure units require actual report locations. Every atomic claim
  and recommendation must be covered; extra unsupported prose is additional_issues.
- Fixed version4, neutral `assessment_fields`, disclosure policy and SHA-256
  `packet_id` over the public content excluding packet_id. Private metadata is
  excluded even if nested beside evidence or units. Authorized source/report prose
  remains untrusted text; semantic injection handling belongs to judge instructions.

The closed rating JSON schema is at
`evals/investigation/report-quality-v4/rating-schema.json`, exported from code.
It requires the exact packet_id, version4, exact unit set, three distinct checks,
critical_error, additional_issues and contradictions. Software validates every
pointer, evidence ID and verbatim witness quote. A false contradiction predicate
requires an actual quote pair; binding alone does not establish semantic conflict.
Missingness is derived as the conjunction, never accepted as a model field.
Uncertainty remains conservative. A valid citation ID alone never establishes truth.

`assess_calibration(packets, ratings, expectations)` requires precisely C1-C6 and
matches all unit judgments/critical flags, report criticalness, all three checks
and empty additional_issues. The custodian freezes private expectations before
actual outputs. Missing/duplicate/foreign/invalid controls fail, denominator six.

`aggregate(packets, ratings, scenario_order, calibration)` requires eight unique
predeclared scenarios and paired secondary packets for positions2,3,4,6,8. Peers
must see identical reports/evidence/units in isolated contexts. It recomputes the
calibration gate; it does not trust a passed Boolean. Missing/invalid ratings fail
their report slot and remain in original_ratings/invalid_ratings, all eight slots
retained. Unresolved predicate disagreement is retained even if both conjunctions
are false. Critical flags from a valid secondary survive a missing primary.

All numerical/disclosure/guidance gates in the approved validation path apply.
Invalid calibration gives quality_assessment_valid=false and quality_pass,
passing_reports and validated report passes=null; raw diagnostic passes are
explicitly unvalidated. Empty factual/essential denominators are unavailable.
Old deterministic support/coverage arithmetic is reused through normalization;
original_ratings always contains actual v4 inputs, not normalized legacy values.

CLI `--input` envelope fields: `packets`, `ratings`, `scenario_order`, `calibration`.
Ratings are lists of `{role, scenario_id, rating}`; duplicate rows are rejected.
Calibration has `packets`, the same rating-list representation, and `expectations`.
All packets are already projected/frozen (changed hashes/private extras rejected).
No input is sent anywhere. `--output` exclusively creates a new file; missing
output or existing destination fails. `--verify-controls PATH` checks committed
fixture hashes/schema and authored responses only, explicitly not model quality.

Before future actual-model work, freeze concrete sources/report/unit inventories,
model/settings/prompt/code hashes and private labels/role assignments; archive
every output/error before joining references. Obtain the separately scoped budget.
The module does not enforce the human custody process or independently verify
semantic truth. No new fresh live run, automatic old-run migration, production
quality claim or independent human/model evaluation is implied by T096 completion.
