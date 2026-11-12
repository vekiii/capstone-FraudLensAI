# Feature 002 technical decisions and evidence gates

Date: 2026-11-12. Status: planning decisions; no source data, model, or Feature 002
runtime has been executed. Read with [spec.md](spec.md), [plan.md](plan.md), and
the [adversarial review](../../prompts/development/002-review.md).

## Decision 1 — Scope and runtime

**Decision:** Keep the local FastAPI plus vanilla TypeScript/Vite application and
its three-case fixture mode. Ingestion, feature construction, model fitting,
evaluation, and run activation are local offline commands. The web API remains
read-only for analysts. No new screen, cloud service, streaming job, model
registry, or graph database is added.

**Rationale:** FR-021–025 require dataset-backed case browsing, not a data-management
web product. Offline commands make expensive or label-bearing operations easier
to separate from analyst requests.

**Alternatives:** Request-time import/scoring would mix runs and delay case reads;
new public write endpoints add scope and security work without a user journey.

## Decision 2 — Source audit is a hard gate

**Decision:** The first implementation slice inspects the locally supplied,
authorized IBM AML HI-Small file and records release, license reference, SHA-256,
encoding, headers, duplicate/unknown columns, row count, parsed time resolution
and span, label encoding/counts, amount/currency formats, and file size. The
reviewed mapping is versioned before importing the full file. No source column
name, timezone, numeric range, or class count is asserted in advance.

**Rationale:** No raw IBM file is present under data/. The public dataset
description does not establish the properties of the eventual local release.

**Alternatives:** Hard-code a remembered schema or silently infer missing
timezone/currency; both could yield plausible but invalid histories.

**Gate:** If required fields or a defensible time interpretation cannot be
established, stop that import and document the decision needed. The separate
authoritative Phase 2 assignment also remains unavailable; do not claim rubric
compliance until it is identified and traced.

## Decision 3 — Version and identity

**Decision:** A source row receives a one-based CSV record ordinal before any
validation or filtering. The declared release/namespace, source member, and
pre-filter ordinal form a stable event key. Public transaction/case IDs are
opaque, URL-safe, dataset-qualified digests of that key, independent of labels,
file hash, scorer, alert status, and accepted-row position. The import version
separately binds raw-file hash, mapping version, and time policy. Reject a
collision or a changed event fact under the same stable event key until the
source namespace is reviewed.

**Rationale:** Equal-valued rows can be distinct events; invalid labels must
not renumber or remove valid historical facts. A label-only file change may
change the import hash without changing event identity.

**Alternative:** Business-field hashing collapses equal-valued distinct events;
post-filter sequence IDs drift on rejection.

**Gate:** The actual source member/row-reference policy and multi-file handling
are frozen after the source audit. Stability is guaranteed for repeated import
of the same reviewed source/mapping, not arbitrary reordered files.

## Decision 4 — Canonical financial and time facts

**Decision:** Canonical operational records keep sender and receiver as separate
bank/account pairs, the source timestamp text and interpreted UTC event time,
and separate paid/received Decimal text with currency. Do not convert FX,
round to two decimals, parse money through binary float, invent an absent
currency, or infer missing personal context. The reviewed mapping defines
which fields are required, whether zero is supported, accepted scale/magnitude,
and timezone interpretation; rejected values have row reasons.

**Rationale:** Foundation v1 has only one two-decimal amount and UTC-Z time;
coercion would lose source facts.

**Alternative:** Broadly loosen v1 models; that would silently break their
meaning and frontend closed decoders.

## Decision 5 — Event validity and label eligibility

**Decision:** One row-accounting pass records event-valid versus event-rejected
and, for event-valid rows, supervised-label eligible versus ineligible. A
missing/invalid target does not remove valid event facts from label-free
history. Private labels are accessible only to fit/evaluation code. The
application repository and scorer request have no label field.

**Rationale:** Filtering events by target validity indirectly leaks label
quality into later features.

**Alternative:** Reject entire rows on label errors; rejected because it changes
the operational history for reasons unavailable at scoring time.

## Decision 6 — Local persistence and publication

**Decision:** Use one ignored, local SQLite store for source/import metadata,
canonical events, private evaluation labels, feature/run metadata, assessments
and case snapshots. Keep private-label reads in an offline evaluation module;
the application read repository projects only label-free tables/columns.
Stage each import/run with an incomplete state, validate counts and references,
mark complete, then switch a single active-run pointer in one SQLite transaction.
On failure, readers see the prior complete run or an explicit unavailable state.
The API never queries staging rows. On restart, validate the pointer and required
artifact manifest before serving it.

**Rationale:** SQLite is in the Python standard library, handles local millions
of rows more predictably than loading every record into one JSON object, and
provides an atomic local transaction. This is one application database, as the
approved project idea anticipated.

**Alternatives:** JSON-file overwrite risks partial/mixed state; distributed
transactions and a database migration framework are unnecessary. Schema
version checks and explicit recreation instructions suffice for this capstone.

## Decision 7 — Historical time semantics

**Decision:** Interpret source event time through the reviewed mapping, sort by
that event time, and process equal-timestamp groups together. For every event
at time t, compute features from event-valid observable facts in the half-open
rolling window [t minus 24 hours, t); only after the whole group is scored may
its facts enter later history. The first 24 hours from the observed source
start form context-only warm-up: those events can build history but are not
scored or used in benchmark denominators. Account cold start after full
coverage is a measured zero, distinct from incomplete coverage.

**Rationale:** This fixes boundary/tie ambiguity, prevents future leakage, and
avoids interpreting missing pre-source history as zero. Earlier held-out event
facts can support strictly later events; their labels cannot.

**Alternative:** Calendar-day windows or source-order processing; neither
matches the spec's point-in-time promise without additional semantics.

**Gate:** Confirm source span, timestamp granularity/timezone, and class
eligibility after warm-up. If the policy leaves an ineligible benchmark,
record a pre-experiment amendment; do not search windows by test outcome.

## Decision 8 — Initial features and rule baseline

**Decision:** The first feature catalog contains current paid amount/currency
and payment format if actually present, sender prior outgoing count, sender
distinct receivers, sender same-currency paid sum/count, receiver prior incoming
count, receiver distinct senders, and receiver same-currency received sum/count.
Use bank-qualified accounts for joins only. No raw or hashed entity/row IDs,
target copies, label-validity indicators, or full-file aggregates are predictors.

The initial rule baseline has three independent, label-free conditions within
the 24-hour window: sender outgoing count at least 3 (weight 0.35), receiver
incoming count at least 3 (weight 0.30), and current paid amount at least twice
the sender's prior same-currency mean when at least 3 such prior outgoing
events exist (weight 0.35). Its score is the sum of triggered weights in [0,1].
The assessment lists each fired rule, observed values, boundary, and version.
An unavailable amount comparison is marked unavailable, not fired. A measured
cold start may have score 0, but that score is not a verified low-risk finding.
Foundation fixture constants and its test adapter are excluded from evaluation.

**Rationale:** The rules can be hand-calculated from observable facts without
target labels or account-ID memorization. The weights/thresholds are a capstone
baseline design choice, not a bank policy or dataset-derived optimum.

**Alternative:** ID-derived constants are reproducible but not a meaningful
transaction baseline.

**Gate:** Freeze rule version and hand-computed examples before viewing
validation/test labels. If the actual source cannot provide a required
directional field, revise this policy explicitly before experiments.

## Decision 9 — Split, roles, and candidate budget

**Decision:** Define the scoreable benchmark view using observable event facts
after warm-up. Sort whole timestamp groups and choose boundaries nearest
70/15/15 by row count without splitting ties; deterministic earlier boundary
wins an equal-distance choice. Freeze exact IDs, times and counts before
joining labels. Check each outer partition has both classes and validation/test
each have at least 20 positives. If not, mark ineligible and amend before fit
without picking a window for favorable metrics.

Initial candidates are L2 logistic regression with C in {0.1, 1.0} and a
decision tree with maximum depth in {3, 5} and minimum leaf size in {100, 500}.
Use seed 42 and a predeclared AP tie tolerance of 1e-6; if AP and Precision@K
remain tied, prefer logistic regression, then the shallower tree. These are at
most six fits. Optional AutoML and calibration are deferred from the first
benchmark run. Fit imputers, encoders, scaling and candidate parameters on
training rows only. Unknown categories use a frozen unknown encoding; no
refit on validation/test. The resource pilot may justify a recorded
pre-experiment reduction of the training view or search budget, but never a
post-test change.

**Rationale:** Two simple explainable candidates match the approved scope.
Skipping optional calibration avoids a crowded short development period and
unsupported probability claims.

**Alternatives:** Random splits, full-file preprocessing, third model families
and repeated test feedback would invalidate or widen the experiment.

## Decision 10 — Validation operating point and final holdout

**Decision:** For each scorer separately, consider each unique validation score
as an inclusive threshold plus a no-alert threshold above the maximum. Keep
thresholds with at most 20 validation alerts, preserving whole score ties.
Choose the threshold with highest validation F0.5; on a tie choose fewer alerts,
then the higher threshold. A no-alert result can win and is reported honestly.
If precision is undefined because there are no predicted alerts, define F0.5
as zero for the selection procedure. Store the no-alert choice as a symbolic
policy value, not a nonfinite numeric threshold.
This is the same policy on rule/model score sets, not necessarily the same
numeric threshold. Freeze model, transforms, scorer-specific thresholds and
calibration status before test predictions. Test alert count may exceed 20;
report it, never retune on test. Mark the holdout consumed when its labels are
first joined to frozen predictions. Later use is exploratory.

**Rationale:** This is a deterministic, label-aware development choice within
the declared validation role. It separates capacity-limited threshold alerts
from label-free top-K ranking metrics and preserves genuine zero-alert results.

**Alternative:** Choose the twentieth score or force exactly K alerts; that
would manufacture cases and confuse ranking with an alert policy.

## Decision 11 — Metrics, uncertainty, and explanations

**Decision:** Use non-interpolated Average Precision with positive label 1;
report AP, K=min(20, eligible row count), Precision@K, Recall@K against all
positives, K-boundary tie group, prevalence, confusion counts, threshold
precision/recall and alert rate for rules/model on identical eligible IDs.
Use stable transaction ID only to resolve ranking ties; state that the tie
convention adds no discrimination. Report exact counts and that uncertainty
is not quantified unless a suitable dependence-aware method is declared
before test disclosure. Do not present 20 positives as precision evidence.
For model outputs obtained from positive-class probability estimates, report
Brier score and a reliability table when bins have sufficient support; if
they do not, state that reliability is not estimable. Label these outputs
uncalibrated estimates until an independent calibration procedure is run
and evaluated. Neither Brier nor a reliability plot alone proves calibration.
Rules remain ordinal risk scores and receive no Brier score.

For the linear model, explain raw log odds with intercept, top three feature
contributions and a remainder; identify the displayed score transform and
label the top three as partial. For the tree, explain the path's change in
positive-class leaf score from root to leaf, with base/remainder and exact
reconstruction. Rule explanations list actual conditions/values. Reject
run/feature/output-scale mismatches.

**Rationale:** The output scale, denominators and explanation identity are
independently checkable; a credible-looking chart is insufficient.

**Evidence:** Official [scikit-learn AP definition](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html)
distinguishes non-interpolated AP from trapezoidal PR area. Its
[calibration guide](https://scikit-learn.org/stable/modules/calibration.html)
explains that Brier reflects more than calibration alone.

## Decision 12 — Dependency and artifact trust

**Decision:** Preserve Python 3.14.x and the existing locked foundation stack.
Add a small locked ML dependency set only after checking a local Python 3.14
install and test. As of this planning date, [scikit-learn 1.9.1 on PyPI](https://pypi.org/project/scikit-learn/)
lists CPython 3.14 Windows wheels; this is availability evidence, not a local
installation result. No pandas/AutoML/SHAP dependency is required for the first
implementation. Store model binaries only under an ignored local artifact
directory; load only artifacts produced by the reviewed local workflow after
path containment, SHA-256, scorer/schema/dependency-version checks. If using
pickle-derived serialization, treat it as executable and never load an
uploaded or untrusted file. Fixture and rules paths need no model binary.

**Alternative:** New model registry or upload path adds scope; manual JSON model
serialization may be safer but requires extra inference implementation and
parity tests. Reconsider only if the local trust boundary is inadequate.

## Decision 13 — API migration and UI

**Decision:** Keep Foundation v1 fixture responses and strict validators. In
dataset mode, the same GET case paths return an explicitly discriminated v2
response with dataset and scorer sources separate, directional amounts,
structured explanation, run/feature/time metadata, and bounded-list counts.
The v2 list returns a snapshot reference. Detail requires that reference;
if it does not identify the active complete snapshot, return a controlled
stale-snapshot response rather than silently mixing runs. V2 case order is
event time ascending then transaction ID, after selecting the most recent 100
alerts. Frontend preserves v1 fixture sorting/banner and handles v2 ordering
and truthful provenance separately. No target labels appear in public shapes.

**Rationale:** Existing backend and frontend objects are closed and v1 IDs,
amounts, health and explanation text cannot represent the dataset path.

**Alternative:** Widening v1 in place would obscure compatibility failures.

## Decision 14 — Reproduction and resource pilot

**Decision:** Before full processing, run a consecutive 100,000-row pilot (or
the whole file if smaller) with full import/feature semantics. Record machine,
Python/dependencies, wall time, peak memory estimate, database/artifact size,
row/rejection counts and projected full-run feasibility. Set a local timebox
and memory ceiling before model search; if exceeded, retain full chronological
validation/test and history while reducing only a declared training view.
Report inability to complete if even the full evaluation view cannot run.
Reproduction records source/mapping/protocol/artifact hashes, exact split IDs,
seeds, predictions, metrics, commands and limits. Another teammate performs
the independent run; the author cannot self-certify it.

**Rationale:** No source size or reference-machine measurements exist yet;
an invented performance SLA would be misleading.

## Alternatives explicitly excluded

Distributed/streaming infrastructure, public import/training endpoints,
cloud storage, model registry, graph database, GNN/transformer training,
LLM scoring, new investigation screens, automatic account action, and
production-generalization claims are outside this plan.
