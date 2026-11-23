# Execution evidence

[T252 governance reconciliation](tasks/T252-governance-reconciliation-2026-11-22.md) verifies team approval, Git authorship, frozen hashes and aggregate arithmetic, and limits the open T252 record to its own actual reviewer/reproduction criteria; no Vedran-specific or project-wide gate is found. [The earlier approval attestation](tasks/T252-independent-approval-attestation-2026-11-22.md) preserves Isidora's checklist, Windows hashes and parity output.

[Codex tehnički pregled završnog PR #3 kandidata](tasks/pr3-final-codex-technical-review-2026-11-22.md) bilježi tačan merge commit, izolovanu Mac reprodukciju, hash/paritet/regresiju, HTTP test-provider tok i ograničenje browser alata. [T252 je završen 23. novembra](tasks/feature-002-review.md#independent-review-and-t252-closure--2026-11-23) nakon što je Milan potvrdio nezavisni pregled Feature 002 i lično Windows T233 izvršavanje za `d46699f`.

The [2026-11-22 model–RAG integration handoff](tasks/model-rag-handoff-2026-11-22.md) records the frozen Feature 002→003 mapping, versioned bridge contract, user-conveyed Feature 003 acceptance, the user's Feature 002 role confirmation, and T103–T109 implementation evidence. The earlier proposal and pre-implementation evidence in that record remain historical. T252 independent review remains open.

The [project evidence and contribution plan as of 12 November 2026](tasks/project-evidence-plan-2026-11-12.md)
consolidates the historical work, named contributors, validation and provisional
time calculation. Its estimates are separate from measured working hours; source
task records remain authoritative for the original execution details.

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

- [Model–RAG integration handoff, 2026-11-22](tasks/model-rag-handoff-2026-11-22.md): separate PR #3 worktree, hash-verified frozen artifact transfer, exact score/HTTP parity, real React fixture/model/results/EDA checks, subsequent Feature 002/003 bridge implementation and owner decisions, and the user-reported [Feature 006 exclusion decision](../prompts/development/2026-11-22-model-rag-feature006-decision.md). No live provider call, merge or T252 completion.
- [T243 EDA decision proposal and T252–T255 preparation](tasks/T243-T255-planning.md): fifth-screen benefit/schedule/allowed-aggregate proposal, human-review packet, completed design-only T253 showcase contract, and separately gated replay plan. The later [user-reported team approval](tasks/T243.md) unlocked Stage F UI; no human reproduction or replay is claimed.
- [T244 synthetic EDA RED tests](tasks/T244.md): five expected missing-module failures for aggregate correctness, bounds, denominators, currency separation and refusal of label-bearing input; T245 later turned them GREEN.
- [T245 Python EDA aggregates](tasks/T245.md) and [T246 endpoint history](tasks/T246.md): bounded closed label-free summaries and a hash-pinned read-only route passed synthetic checks before the later full-source publication below.
- [T246 label-free T210 preparation](tasks/T246-label-free-preparation-2026-11-21.md): inspected the existing byte-stripping boundary, prepared an exact-hash-gated offline publisher and synthetic negative/label-independence tests. No full-source pass or live summary was run.
- [T246 full-source publication](tasks/T246-full-source-eda-2026-11-21.md): one authorized full T210 label-free aggregation, exact provenance/hash and count checks, bounded currency-separated summary, real local HTTP 200, controlled missing/tampered 404, resource receipt and test results. T252 remains pending.
- [T247 EDA route and browser checks](tasks/T247.md), [T248 decoder and RED/GREEN states](tasks/T248.md), and [T249 full regression](tasks/T249.md): team-approved accessible EDA page uses only the trusted bounded summary; 632 backend and 229 frontend tests, typecheck/build, Ruff and diff check passed. T252 human review remains open.
- [T250 access tests](tasks/T250.md), [T251 authorized aggregate API](tasks/T251.md) and [T240 live results UI](tasks/T240.md): expected RED, exact report/model/prediction/approval hash gates, bounded validation/test results, controlled negative states, full regression and browser evidence. Human review/reproduction remains T252.
- [Stage E T237–T242](tasks/T242.md): decoder RED/GREEN, typed risk API and separate canonical-ID UI, safe rendering and browser checks. [T237](tasks/T237.md), [T238](tasks/T238.md), [T239](tasks/T239.md), [T241](tasks/T241.md). T240 was completed after T251 above.

- [T230 one-time authorization](tasks/T230-authorization-2026-11-21.md), [first blocked receipt](tasks/T230-snapshot-receipt-2026-11-21.md), [completed snapshot and single evaluation](tasks/T230-snapshot-completion-and-evaluation-2026-11-21.md), and [T230 summary](tasks/T230.md): supplemental original completion files passed exact hashes and the full verifier; the frozen unweighted model's sealed predictions received one authorized aggregate test evaluation. Report SHA-256 `5027dae9354796718a080086a6cadc0319d1b376336ad4dac8d93b4e534d9cdb`; no application acceptance or showcase-label parse.
- [T229 unweighted freeze decision](tasks/T229-unweighted-freeze-decision-2026-11-20.md) and [completed label-free export](tasks/T229-unweighted-freeze-export-2026-11-20.md): exact existing model/threshold choice, original train-only vocabulary, new trusted artifact and lineage, 233,070 sealed test scores, full hashes and original-workstation transfer requirements. The [T229 summary](tasks/T229.md) distinguishes this freeze from the historical weighted one; later T230 execution is recorded above.
- [T224 Stage C cross-family approval](tasks/T224-stagec-cross-family-approval-2026-11-20.md) and [completed execution](tasks/T224-stagec-cross-family-execution-2026-11-20.md): exact-hash authorization, prelaunch verification, one completed seven-fit plus constant run, ten-entry validation ranking including both existing LightGBM references, independently checked metrics and full output hashes. No new holdout prediction or T230.
- [T224 Stage C cross-family preparation](tasks/T224-stagec-cross-family-preparation-2026-11-20.md): reconciled T219 `protocol.md` and checkbox, exact baseline/HGB plan, pending FR-023 candidate canonical hash, existing LightGBM lineage, frozen selection and instability rules, RED/GREEN synthetic tests, resource limits and future-only command. No project fit or holdout use.

The [T228 transfer record](tasks/T228-transfer.md) identifies the request, recorded Git author, Codex packaging work, observed archive checks, and pending colleague reproduction. The generated data archive is local and ignored by Git; its [checksum](../T228-colleague-transfer-2026-11-20.zip.sha256) is committed. The [macOS colleague guide](tasks/T228-colleague-macos-guide.md) gives the setup and run steps. The first approved FR-021 attempt stopped before fitting; the separately approved second attempt completed and froze test predictions without reading test labels. See the current records below.

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
- [T226 validation evaluation](tasks/T226.md): T225 GREEN plus NumPy and tied-score regressions, positive-class threshold and uncapped daily counts, all on fixed scores without fitting.
- [T227 artifact integrity](tasks/T227.md): native-text writer, independently anchored manifest digest, metadata/version/path validation and no deserialization; synthetic byte checks only.
- [T228 task evidence](tasks/T228.md) and [local training handout](tasks/T228-local-runbook.md): historical no-fit implementation checks plus a link to the later completed Stage C experiment; the old command in the handout is historical and is not the approved second command.
- [Current handoff](../next_work.md), [data card](../data/README.md) and [protocol](../specs/002-data-and-risk-scoring/protocol.md): current status, local data limitations and next action.
- [Model–RAG bridge implementation and browser proof](tasks/model-rag-handoff-2026-11-22.md): user-conveyed Feature 003 acceptance and user-stated Feature 002 owner decision, validated additive binding, T210 label-free publication, backend/React adapter, exact frozen-score parity, test-provider evidence and isolated test decision; T103 is complete, T252 independent review remains open. Local browser screenshot remains outside Git.
- [2026-11-19 local commit receipt](tasks/session-commits-2026-11-19.md): reviewed file scope, commit identity, checks and publication status.

The raw CSV, snapshot, stage and quality report live in ignored `data/` paths and are not part of Git. No feature/model evaluation or authorized restricted label audit has been reported for T210.

The [Stage C Mac receipt](tasks/T228-stagec-mac-receipt-2026-11-20.md) records this colleague's independent transfer checks, locked environment, no-fit tests, and blockers; it does not claim protocol approval or a model fit.

The [Stage C Mac remediation](tasks/T228-stagec-mac-resource-remediation-2026-11-20.md) records isolated Python 3.14.10 installation, resource watchdog RED/GREEN checks, exact implementation hash changes, residual limitations and the pending protocol review. No fit or model evaluation occurred.

The [revised FR-021 Mac resource candidate review](tasks/T219-stagec-macos-resource-review-2026-11-20.md) records the HEAD diff audit, atomic incomplete-output fix, one small synthetic compatibility fit, new candidate canonical/file digests, read-only manifest and implementation verification, unchanged methodology and pending human decision. The [read-only verifier](tasks/T219-stagec-review-verify.py) can repeat the candidate checks without parsing record labels or running training.

The earlier [exact-hash approval](tasks/T219-stagec-protocol-approval-2026-11-20.md) covered the first attempt only. The [T228 first attempt](tasks/T228-stagec-approved-fit-attempt-2026-11-20.md) records its failed command, absent top-level feature metadata and retained `.incomplete` status; no fit occurred. The [first operational instruction](../prompts/development/002-T228-stagec-approved-fit.md) preserves that scope and command.

The [T228 manifest-schema remediation and real-input no-fit preflight](tasks/T228-stagec-preflight-schema-remediation-2026-11-20.md) records the publisher/runner hash contract, RED/GREEN and 84 focused passing tests, protected full train/validation preparation, exact no-fit output hashes and the new candidate with canonical SHA-256 `1ebac4f24aa198cfd1de70b96204676cb3fbd0cc07786296944c6ade0214f6be`. The [development instruction](../prompts/development/002-T228-stagec-preflight-schema-remediation.md) preserves its scope. Its pending-review state and no-fit statements describe the period before the separate second approval and experiment.

The later [second exact-hash approval](tasks/T219-stagec-second-protocol-approval-2026-11-20.md), [T228 completed second experiment](tasks/T228-stagec-second-fit-2026-11-20.md) and [T229 frozen model/predictions](tasks/T229.md) record the successful eight-candidate validation run, selected artifact reload, full output hashes, resource use and structural-only test-prediction check. The [second operational instruction](../prompts/development/002-T228-stagec-second-approved-fit.md) preserves the exact command. Validation results are measured; test performance remains unmeasured and T230 is not authorized.

The separate [T228/T229 validation audit](tasks/T228-stagec-validation-audit-2026-11-20.md) reconstructs the selected threshold, confusion matrix, validation metrics and ranking from frozen scores and validation labels, verifies native model probabilities, records score saturation and the 14,796-way top tie, and identifies candidate outputs and histories that were not retained. It did not fit or change the frozen experiment; test/showcase labels and T230 remain untouched.

The [Stage C numerical diagnosis and proposed controlled study](tasks/T228-stagec-numeric-diagnostic-2026-11-20.md) traces the selected artifact's class weighting, unweighted initialization, tiny-Hessian leaf updates and raw-margin saturation across four retained trees. It reports separate post-hoc raw-score validation AP/P@20, input-range checks, LightGBM source/documentation findings and an unapproved five-arm train/validation-only experiment with full per-arm retention. The [original request](../prompts/development/002-T228-stagec-numeric-diagnostic.md) is preserved. No new fit or official metric change occurred.

The [five-arm numeric diagnostic preparation](tasks/T228-stagec-numeric-diagnostic-preparation-2026-11-20.md) records the standalone runner, fixed one-factor variants, hash-bound pending-review protocol, synthetic RED/GREEN and 58 passing relevant tests, exact canonical/file hashes and unchanged frozen output hashes. The [development request](../prompts/development/002-T228-stagec-numeric-diagnostic-preparation.md) preserves scope. No project-data diagnostic fit was run.

The [exact-hash diagnostic approval](tasks/T228-stagec-numeric-diagnostic-approval-2026-11-20.md) and [completed five-arm execution](tasks/T228-stagec-numeric-diagnostic-execution-2026-11-20.md) record one authorized train/validation-only run, prelaunch hash/runtime/input gates, complete status, five model reloads, independently reproduced saved validation metrics, full output hashes and interpretation. The [operational instruction](../prompts/development/002-T228-stagec-numeric-diagnostic-execution.md) preserves scope. The control reproduces the frozen model and scores byte for byte. No new test predictions, test/showcase label access, T230 or model activation occurred; validation is reused and not independent evidence of generalization.

The [Stage C task reconciliation](tasks/T228-stagec-task-reconciliation-2026-11-20.md) maps the exact T219 and T220–T230 actions to evidence, explains why T228/T229 are now checked, why T219/T230 remain open, what FR-023 baseline/cross-family results are still missing, and how the existing unweighted native model could be formally considered without refitting. The [original request](../prompts/development/002-T228-stagec-task-reconciliation.md) is preserved. This was a read-only model/code review plus documentation update; no test prediction, test/showcase label access, T230, fit or activation occurred.
## Stage D local opt-in model integration

- [User acceptance and scope](tasks/T231-stage-d-acceptance-2026-11-21.md), [T231 RED/API tests](tasks/T231.md), [T232 contracts](tasks/T232.md), [T233 loader/parity](tasks/T233.md), [T234 opt-in/errors](tasks/T234.md), [T235 endpoint](tasks/T235.md), and [T236 backend regression](tasks/T236.md): frozen unweighted LightGBM and threshold are used only for the local opt-in model route. Eight ID-only sampled offline scores and one HTTP score matched exactly; full backend suite passed 599. Fixture mode stays default. No model fit, new T230 evaluation, showcase-label access, frontend, results API, EDA, commit or push.
