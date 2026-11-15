# T062 producer/consumer reconciliation — 2026-11-15

Status: **partial; actual human producing/affected-consuming review pending**.
Authorization to execute Phase 8 does not approve changed source semantics.

## Reproducible source comparison

Checkout feature03 at 0829296f2824764c3773f6c8e90eb94d39843455; initially clean.
Producer code is absent from this checkout. Locally available remote-tracking
snapshot `origin/model-implementations` resolves to
`d9bd8a2e3629a2d3939fc5507583f310428c53ac`. No fetch, branch change, merge,
producer import, database access or IBM/model execution was performed. This is
the current **locally available** snapshot, not a claim about newest upstream.

Run `.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-producer-audit.py`.
[Machine-readable comparison](feature-003-producer-audit.json) records normalized
hashes and source function signatures/line numbers. Pinned source remains
`2dd815d85bfc9c2fc70a28baef9c142d551e57e0`; its schema SHA256 LF remains
`bf487d84ccac1e315d0e20fece0d2a7f45990bce954ba40bf97cd54e43929f88`.
Current source schema SHA256 LF:
`3bb54c0bcad5f4683db8ee6ef1e663749993a25ab144869190ce0182ac6f7ab2`.

Only parsed schema difference: `/$defs/ExplanationAvailable/properties/method/enum`
adds `boosted_sequential_probability` after rules, linear_log_odds, tree_path.
Case/run/dataset/transaction identities, directional money/time and other schema
definitions are unchanged. The investigation validator deliberately still uses
the pinned enum and scale mapping; no new method/scale approval is inferred.
An unchanged schema is not proof of unchanged runtime semantics.

Current main imports its V2 boundary from `data_contracts.py`, also hashed in
the audit. Its CaseDetailV2 validation maps the new method to
`positive_class_estimate`, and checks score-source/method consistency and
transaction/assessment time equality. That is an observed producer claim, not
consumer approval or proof of probability calibration. Investigation's existing
pin still rejects the new method rather than silently renaming/scaling it.

## Available source interfaces and unresolved history boundary

At the producer SHA above:

| Interface | Observed source meaning | Integration consequence |
|---|---|---|
| main.py case_detail (149) | GET case with optional snapshot, dataset branch calls RunStore.detail_active | Consumer must pin run; switched run yields 409 stale_snapshot. |
| data_store.py RunStore.active_metadata (952), detail_active (979) | Read completed active run for score_source; matching run required; returns closed public detail | Proposed case port must preserve this behavior and avoid mixed-run reads. |
| data_store.py operational_events (413) / iter_canonical_events (484) | Label-free operational facts for complete dataset; full dataset enumeration | These are not a reviewed bounded account-history service. Do not grant runtime tools arbitrary store access. |
| feature_history.py iter_feature_snapshots | Sliding 24-hour scoring features, not a seven-day investigation evidence list | Never equate scoring coverage with seven-day evidence coverage. |
| data_store.py private_labels | Separate offline-evaluation role | Must never be called by investigation adapters. |

There is no exposed account-history HTTP route in inspected main.py. The source
offers useful internal label-free iteration, but actual history adapter needs an
agreed bounded read port/ownership and explicit coverage metadata. No claim that
this absence prevents future producer-side implementation; no producer DB/scorer
change is authorized by this reconciliation.

## Concrete review packet / decision requested

Producer and affected consumer should inspect these exact SHA-pinned sources
with `git show <SHA>:<path>` (no checkout/merge required) and this comparison.
Record actual names, date, reviewed SHA, findings and approve/reject/request-change:

1. Whether to retain the existing three supported methods and truthfully reject
   the new method, or propose an explicit newly versioned snapshot/scale mapping.
   Do not silently replace producer-v2.snapshot.json or old report bindings.
2. Case port returning unchanged public CaseDetailV2 for case/run/score source;
   exact paid/received decimal strings and currencies, raw minute and synthetic
   UTC assumption, score kind/source and partial/unavailable explanation status.
3. Separate label-free history port scoped to dataset/run, bank AND account,
   strict pre-minute cutoff, seven-day investigation window, focal exclusion,
   maximum 50 returned events with exact eligible count, truncation, per-currency
   totals and honest unavailable/incomplete/full coverage. No full dataset sent
   to the provider. Resolve disagreement with 24-hour scoring history explicitly.
4. Read-only access, no private label/reference imports, source-switch rejection
   and historical archived evidence retained. Agree actual producer smoke setup
   and identify rules/model run availability; no fabricated trained output.

Actual producing reviewer: **pending**. Actual affected-consuming reviewer:
**pending**. Date/decision: **pending**. This document is agent source analysis,
not a human signature or approval. T062 remains unchecked. Authored contract
regressions can run now; actual adapter RED/GREEN and real producer smoke remain
dependent (T063/T064). See [Phase 8 handoff](feature-003-phase-08-handoff.md).
