# Execution evidence

Use [templates/task.md](templates/task.md) for task records in `evidence/tasks/`.
Link task/requirement IDs, original development prompts, code revision or working
diff, runtime/dependency/data versions, exact commands, exit codes and observed
results. Update the handoff after each task or coherent unit so another contributor
can continue from a checkout without conversation history.

Record RED → GREEN and regression for business behavior. RED must demonstrate the
intended missing behavior. For mechanical setup write “not applicable”; do not
invent failures. Distinguish passed, failed, not run, blocked and no tests collected.
Never treat absent tests as a passing suite. Planned commands are not execution.

Fixture checks verify synthetic contracts/behavior; they are not ML evaluation.
Model evaluation records additionally identify data/split/model versions and leakage
controls. Keep reference labels outside application inputs. Record manual checks
only when performed. Human review is `not_requested`, `pending` or `reviewed`;
name an actual reviewer and date only after review. Peer reproduction stays pending
until another teammate actually runs it (SC-001).

Development instructions belong in `prompts/development/`; versioned runtime
prompts belong in `prompts/app/`. Link them rather than conflating prompts with
execution evidence. Sanitize secrets and sensitive data before recording anything;
document redactions without preserving secret originals in Git. Keep logs small
and reviewed; generated local evaluation artifacts follow data/README.md.

For Feature 002, retain the original specification-generation prompt in
`prompts/development/002-dataset-ml-eda.md`. Record source verification, restricted
label-audit access, actual preparation/training commands, outputs, limitations and
human review as separate task evidence. Do not place raw/processed rows, model
artifacts, record-level labels, or holdout answers in this directory. Evidence for
documentation or ignore-policy setup must state that no data/model checks were run.

## Feature 002 current evidence index

- [T201–T208 task records](tasks/T201.md): evidence for source-policy setup, synthetic parser/validation contracts and the resumable canonical runner; follow the individual T201–T208 links in [tasks.md](../specs/002-data-and-risk-scoring/tasks.md).
- [T209 resource benchmark](tasks/T209.md) and [runner](tasks/T209-benchmark.py): four synthetic scale/skew runs and frozen preparation ceilings.
- [T203 source verification and local-copy decision](tasks/T203.md): measured source hash/header, IBM data-license statement, unknown Kaggle release/terms, and the user-directed content-addressed exception.
- [T210 real canonical ingestion](tasks/T210.md) and [runner](tasks/T210-ingest.py): exact command, 5,078,345 accepted rows, verified snapshot/quality hashes, runtime-ceiling review and deferred fields.
- [T211 temporal RED contracts](tasks/T211.md): twelve synthetic cases for UTC, strict prior-only history, 24-hour boundaries, currencies, bank-qualified identities and warm-up; GREEN is pending T213.
- [T212 frozen temporal protocol](tasks/T212.md): conditional project UTC convention, non-label precision scan, eleven-field feature order and train-only unknown-category policy.
- [T213 temporal feature kernel](tasks/T213.md): corrected exact-lower-edge test, synthetic GREEN/regression results, and full-source scaling limits.
- [T214 partition RED contracts](tasks/T214.md): six synthetic cases for half-open warm-up, whole-instant nearest boundaries and earlier ties; GREEN is pending T215.
- [T215 partition planner](tasks/T215.md): synthetic GREEN and backend regression; real-scale chronological pass remains gated.
- [T216 label-access RED contracts](tasks/T216.md): eleven synthetic cases for allowed aggregate shapes, refused record/showcase subrange access and audit logging; GREEN is pending T217.
- [T217 restricted aggregate audit](tasks/T217.md): synthetic GREEN, additional denial/encoding regressions and full backend checks; the later real audit is recorded under T218.
- [T218 frozen boundaries and real aggregate audit](tasks/T218.md): count-only UTC boundaries committed before label access, permitted partition/day totals, and the FR-018 showcase tolerance failure; training stopped pending a human decision.
- [T220 training boundary RED contracts](tasks/T220.md): ten synthetic cases for train-only preprocessing and sealed test/showcase labels; GREEN reached in T223.
- [T221 model-choice decision](tasks/T221.md): Phase 1 LightGBM proposal and the later user-reported team approval for the combined LightGBM/baseline/HistGradientBoosting grid, choice hash, schedule impact and remaining FR-021/provenance gates. No model fit or evaluation was run.
- [T222 locked ML compatibility and artifact decision](tasks/T222.md): Python 3.14/scikit-learn/LightGBM versions, synthetic native model roundtrip, locked regression check and trusted-local-artifact plan. No real fit or loader was run.
- [T223 train-only preparation and baselines](tasks/T223.md): T220 GREEN, synthetic prevalence/tree/L2 logistic checks, class weighting and train-only scaling. No real-source fit was run.
- [T224 candidate code and cross-family rule](tasks/T224.md): eight LightGBM and five HistGradientBoosting configurations, frozen later-selection rule, and mocked no-fit checks. Actual model training remains unrun by user instruction.
- [T225 validation evaluation RED contracts](tasks/T225.md): 25 fixed-score tests for thresholds, ranking, metrics, denominators, alert counts and invalid inputs; GREEN remains T226 work. No model fit.
- [Current handoff](../next_work.md), [data card](../data/README.md) and [protocol](../specs/002-data-and-risk-scoring/protocol.md): current status, local data limitations and next action.
- [2026-11-19 local commit receipt](tasks/session-commits-2026-11-19.md): reviewed file scope, commit identity, checks and publication status.

The raw CSV, snapshot, stage and quality report live in ignored `data/` paths and are not part of Git. No feature/model evaluation or authorized restricted label audit has been reported for T210.
