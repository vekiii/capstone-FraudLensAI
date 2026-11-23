# Reliability branch merge preparation — 2026-11-16

User explicitly requires joint confirmation before merging into feature03.
No merge, checkout, reset, rebase or target-branch update performed.

## Target and non-mutating preview

At review, local feature03 and remote origin feature03 both resolve to
`cd98ea021a38b362b5766c4e23a1e55ec0ad0dcd`. Preparation HEAD on reliability branch:
`dd140af841febd49e4df8a9cab17d6d5fb9be9a8`.
Target is an ancestor of the reliability branch: merge can fast-forward with no
divergent changes. Preview with `git merge-tree --write-tree --messages feature03 HEAD`
returned tree `d4fd5aa9e7dbf2463965752ab898c9622efa1c9e`, exactly HEAD's tree,
exit0 and no conflicts. Only unreachable Git tree objects can be written by this
preview; target refs/index/worktree do not change. Quote `'HEAD^{tree}'` in PowerShell.
Final docs/result commits retain the same ancestry; recheck before real merge
because another teammate could advance the target later.

## Focused code review

Reviewed branch delta against feature03 for provider, workflow, report validation,
safe repair hints, notice policy, opt-in retrieval normalization and offline judge
calibration. No blocking defect found within that reviewed scope. This is agent
self-review, not a teammate's human review or full T067 Converge.

- Provider schema sharing preserves expanded old constraints; byte guards include
  prompt/schema and full ordered private continuation. No evidence truncation.
- Fixed allowlisted validation feedback contains no raw rejected values/errors.
  Closed tool/projection/source validators remain. Local exact-value/quote/citation
  checks precede versioned notice membership. Neither implies semantic approval.
- Request timeout may consume one bounded retry; total deadline still terminates.
  Known quota/credit errors are nonretryable, unknown billing usage retained.
  SDK retry disabled, retry-after bounded and all existing request/tool/time caps
  retained. Transport cleanup is cooperative and bounded; host suspension remains
  a practical limit, not an explanation proven for the old latency outlier.
- New attempts pin notice policy/instructions; retries inherit parent binding,
  old reports remain immutable. Missing literal repairs once or fails. Raw model
  output is never auto-rewritten with boilerplate. A semantically equivalent
  paraphrase can still consume a repair under the deliberate literal protocol.
- Script normalization requires an explicit separate retrieval configuration.
  Existing production/default retrieval and old measured results are unchanged;
  the development configuration is still explicitly unvalidated for release.
- Calibration/expected labels remain in offline evaluation; new diagnostic wrapper
  runs only in explicit evidence scripts. Two ordinary cases retain failures in
  denominator; controlled cases are excluded from ordinary quality scores.

Frontend, public wire schemas, API composition, dependency/lock files, .env example
and producer/dataset contracts are unchanged relative to feature03. No migration
or feature002 adapter is included. The large branch diff includes frozen authored
inputs, historical evidence and tests; those are not additional product features.

## Regression and unresolved gates

Current tree: backend919 tests PASS69.01s, frontend186 PASS, frontend typecheck/
build PASS, Ruff/diff PASS. Full backend includes contract/recovery/safety checks.
Browser/process journeys were not rerun in this unit (frontend/API shapes unchanged);
their historical checks remain distinguished. Live final outcomes recorded in
[final live evidence](feature-003-final-live-v8.md).

Original failed held-out report/retrieval/latency findings remain failures.
Small authored template checks and same-model calibration do not replace fresh
independent evaluation. T062 current producer/consumer review, T063 actual adapter
RED beyond authored guards, T064 dataset integration, T066 real teammate
reproduction/human review and T067 full feature convergence remain pending.

These gates prevent claiming feature03 complete. They do not require discarding
tested reliability improvements or prolonging this child branch indefinitely.
The merge decision is for bringing scoped fixes back to ongoing feature03 work.
All final results/limitations must be reviewed together before the actual merge.

Final live check: all3 reports valid, actual notice-omission recovery succeeded,
18HTTP200 and no runtime/source change. Calibration2/3 failed on a missingness
interpretation disagreement (the fabricated critical allegation WAS detected),
so no accepted automated quality score. This is an unresolved evaluation gate,
not a newly observed code/merge conflict. Recommendation: ready for joint review
of bringing scoped reliability fixes into unfinished feature03; semantic quality
must remain pending and is not a condition silently declared satisfied. User
has not authorized the merge itself. Do not start another experimental round
or change control labels to hide the disagreement.

## Merge executed after explicit authorization

User subsequently approved: "dobro, mozes uraditi merge", followed by "i push".
Rechecked clean worktree and remote refs immediately before merging. Both local
and remote feature03 still at cd98ea021a38b362b5766c4e23a1e55ec0ad0dcd;
reliability branch at920296436643e2c25ca27fc19441ecedf7e078c6.

Switched to feature03 and ran `git merge --ff-only feature03-reliability-v2`:
successful fast-forward to9202964, no conflicts or content reconciliation.
`git diff --exit-code feature03-reliability-v2 HEAD` returned0: resulting tree is
exactly the previously tested/reviewed source tree (919 backend/186 frontend/
typecheck/build/Ruff checks above). No additional code changes or live calls.
Post-merge offline source/artifact audit rechecked; full suites need no repeated
run for this identical tree. Updated handoff/evidence in a documentation-only
follow-up commit, then publishing feature03 as explicitly requested. No branch
deletion or force push. Verify the final remote identity after push.

This merge brings reliability fixes into ongoing feature03 development. It does
not close T062–T067/T094, original failed targets or the unconfirmed model-quality
gate. Explicit user merge authorization is not a substitute for missing teammate
reproduction, producer review or independent evaluation.
