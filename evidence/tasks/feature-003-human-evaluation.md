# T059 blocked by T058 and actual raters - 2026-11-15

T052 pack approval is preserved; it is not evaluation of generated reports.
No actual report rating, reviewer assignment, score, signature/date invented.
No reviews.json containing synthetic/empty acceptance judgments was created.

Import format follows frozen rubric.rating_record_fields (all 17 required):
scenario_id, attempt_id, report_id, report_sha256, context_revision,
reviewer_identity, reviewed_at, role, claim_id, report_location, claim_text,
claim_kind, evidence_ids, judgment, reason, critical_error, essential_fact_id.
Use one record per rated claim/essential fact, explicit nulls for inapplicable IDs;
role primary/secondary. Exact report SHA binds the immutable artifact. Observations
use supported/unsupported/uncertain; procedures applicable/unsupported/uncertain;
essential facts present/missing/uncertain. Reasons must be actual human findings.
Preserve all originals; disagreements keep separate null resolution until an
actual resolution is recorded. Never silently overwrite the two ratings.

One actual primary reviewer rates all eight; a different teammate independently
rates the five already-preselected IDs in splits.json.second_review_subset (at
least four required). Do not select easier reports after seeing output. Ratings
must assess source fidelity and critical errors, not only schema/citation validity.
Zero observational claims means N/A; uncertain remains unsupported. Failed
provider/validation attempts remain in the denominator. Rater completeness/import
checks are not automatic scientific acceptance; current quality_acceptance is null.

Future real file: evals/results/feature-003/reviews.json. summarize-reviews takes
explicit --protocol, --reviews, --outcomes (sealed), --output. T059 unchecked;
complete T060/T061 remain blocked downstream.
