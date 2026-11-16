# Proposed UTC daily capacity policy — awaiting team decision

**Status:** user-authorized local implementation, 2026-11-16. The proposed
policy is implemented only for a new isolated run; shared activation and
team review remain separate decisions. The original proposed diff below is
retained as the decision record. The implemented v2 response uses optional
policy/count fields to preserve legacy response shape.

## Why an amendment is required

The current [scoring contract](../contracts/data-and-scoring.md) defines every
score at or above the frozen threshold as an alert. The [API contract](../contracts/api.md)
defines `total_alerts` as *all threshold alerts* in a completed run. Selecting
only the highest 20 per UTC day would therefore change case membership and the
meaning of `total_alerts`. The current T029 protocol also preserves whole score
ties for threshold selection; a per-day ID tie break is a new operating policy.
It must have a new policy identity and a separate run before any shared use.

## Concrete proposed contract diff

```diff
--- a/specs/002-data-and-risk-scoring/contracts/data-and-scoring.md
+++ b/specs/002-data-and-risk-scoring/contracts/data-and-scoring.md
@@ score-run output and publication contract
-| score-run | Completed dataset, feature/scorer/artifact version and frozen threshold | Label-free staged ScoredRun and ReviewCaseSnapshot, completed after validation | Failure => no active pointer change |
+| score-run | Completed dataset, feature/scorer/artifact version, frozen threshold and optional approved alert-policy ID | Label-free staged ScoredRun and ReviewCaseSnapshot, completed after validation | Failure => no active pointer change |
+For policy `boosted_utc_daily_top20_v1`, first retain all finite scores >= the
+frozen boosted threshold. Partition candidates by the date of the approved
+fixed-offset-zero event coordinate. Within each date sort by score descending,
+then stable transaction ID ascending, and publish at most 20. A score tie at
+the daily boundary is resolved by ID; do not silently apply the T029
+whole-score-tie rule to this distinct operating policy. Preserve the raw
+threshold count, selected count, rejected-overflow count, policy ID and its
+digest in the immutable run metadata. Do not change an already completed run.
+A policy-selected alert is the only kind of ReviewCaseSnapshot served by the
+API. Scores and explanations of overflow transactions remain stored, but
+overflow transactions are not public cases for that run.
--- a/specs/002-data-and-risk-scoring/contracts/api.md
+++ b/specs/002-data-and-risk-scoring/contracts/api.md
@@ CaseListV2
-total_alerts counts all threshold alerts in the completed scored run;
+For a run using `boosted_utc_daily_top20_v1`, total_alerts counts selected
+published alerts; add `threshold_eligible_count`, `capacity_excluded_count`
+and `alert_policy_id` to the versioned list and health contracts. For legacy
+runs, preserve the existing total_alerts meaning and response shape.
--- a/specs/002-data-and-risk-scoring/spec.md
+++ b/specs/002-data-and-risk-scoring/spec.md
@@ FR-021/FR-022
+A separately approved daily-cap run may publish at most 20 threshold-eligible
+cases per complete UTC day, ranked by score then stable transaction ID. It
+must report discarded-overflow counts, day coverage and policy identity,
+while retaining all scored assessments for audit and comparison. The 100-item
+display limit applies after daily selection and remains a display bound only.
```

The exact public field placement and whether policy identity requires
`contract_version=3` need affected-consumer review before implementation.
The current v2 schema has strict fields, so the proposed new fields cannot be
added to live responses without updating JSON Schema, frontend types and tests.
The time basis is `assumed_utc_for_synthetic_benchmark`, not independently
verified source timezone. A partial source day must be marked separately;
the policy still caps whichever extant events it contains.

## Development diagnostic, separate from publication

The read-only diagnostic in `backend/src/fraudlens/daily_capacity_diagnostic.py`
and `evidence/tasks/feature-002-daily-capacity-check.py` tests this ranking
against the completed v3 score store without modifying its alert flags. Its
seven unit tests cover midnight boundaries, tied scores, >20 candidates,
inclusive threshold, invalid times and scores. Across existing v3 scores the
proposal retains 159 of 166 alerts, dropping four on 2 September and three on
9 September. Train/validation labels, queried only after selection, show 108
hits before and 106 after the proposed cap; the two lost development hits are
on 2 September. The 9 September development segment has eight threshold alerts,
all retained. No test labels enter this calculation. These are already
inspected development data, not an independent utility result.

## Decision required before implementation

The team must approve the policy ID, public count/schema semantics, treatment
of tied scores and partial days, and whether copying scores from the immutable
v3 run into a fresh policy run is acceptable. Such a copy would need a verified
source-run digest and a new run ID/store; it would not require new model
predictions, but the product has no approved command for it yet. The source v3
run and shared active run remain unchanged. The final acceptance still requires
a previously unseen compatible 24-hour period with at least five hits among
at most 20 alerts under the *frozen approved* policy.
