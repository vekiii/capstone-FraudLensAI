# Next work - FraudLens AI
Updated 2026-11-13 Europe/Belgrade. Historical specification-start HEAD: 33bcf62.
Current observed branch: 002-data-and-risk-scoring; HEAD: 63d3384.

## Current Prompt 1 technical resolution — 2026-11-13

**T001–T006 complete; T007/T008 technical work complete, actual team review pending.**
[Resolution and actual commands](evidence/tasks/feature-002-technical-resolution.md),
[current review hashes](evidence/tasks/feature-002-technical-resolution.json),
[user technical approval](prompts/development/002-technical-resolution-request-2026-11-13.md).

- Authorized download fetched only pinned Kaggle v8 HI-Small_Trans.csv into
  ignored data/raw/release-verification/v8-20261113-approved/. HTTP 200 text/csv;
  no account or extra tool/dependency install needed. Both CSVs are 475,664,283
  bytes and SHA-256 b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040.
  Original before/after hashes unchanged. Adopt v8 as the reproducible reference;
  original acquisition history remains unknown. [Receipt](evidence/tasks/feature-002-verify-v8.json).
- Publisher metadata identifies CDLA-Sharing-1.0 for version 8 at transfer time.
  IBM reference code supports Account directions and binary 1=laundering /
  0=non-laundering for these synthetic labels. [Semantics](evidence/tasks/feature-002-source-semantics.json).
  No source timezone, synchronization or lifecycle-stage fact was invented.
- [Technical mapping](data/mappings/ibm_hi_small_v1.json) binds exact headers,
  Account positions 2/4, source hash/member/v8 namespace, decimal/currency/label
  policy and the user-approved explicit synthetic UTC+00 analysis assumption.
  Raw timestamp text/minute ties are preserved. Configuration remains
  pending_team_review, executable_mapping=false and import_allowed=false; actual
  producing/affected-consuming review entries remain pending/null.
- Feature 002 schema/API/offline contract now contain currency length 17,
  required detail-envelope dataset_version and equality obligations, strict end
  assertions, exact source-bound duplicate exception and explicit assumed-clock
  discriminator. Examples/data model/spec/plan/research/quickstart are aligned.
  Foundation v1 application/schema/fixture/frontend/order/banner/locks unchanged.
- Inspect supports --mapping for read-only observation; generic inspection
  remains strict. Full mapped scan: 5,078,345 records, complete_parse=true,
  controlled exit 2 pending_team_review, import_allowed=false. No import command,
  model training, activation or v2 application/decoder integration exists here.
- RED: 21 intended mapping/schema failures in test bodies. GREEN: 57 targeted;
  after additional boundary/example checks, full backend **375 passed**, frontend
  **151 passed**, Ruff/typecheck/build passed. Existing Starlette/httpx warning only.
  No human review, independent teammate reproduction, model result or Phase 2
  assignment compliance inferred. No commit/push; current branch preserved.

One concrete next step: have the actual data/scoring producer, frontend/API and
affected investigation/priority owners review the current hash manifest and
record their real findings/decisions. Keep T007/T008 unchecked and import disabled
until the required gates are satisfied. Do not start Prompt 2 from this handoff
without its separate authorization. Absolute source clock/lifecycle claims would
still need publisher evidence; the approved analysis assumption resolves only
this prototype's coordinate policy.

## Prior Prompt 1 investigation/proposal handoff — 2026-11-13

Independent research and concrete proposal work is complete; T006–T008 remain
unchecked because provenance/decisions/review are still pending. [Investigation](evidence/tasks/feature-002-source-investigation.md),
[review packet](specs/002-data-and-risk-scoring/proposals/README.md),
[mapping draft](specs/002-data-and-risk-scoring/proposals/source-mapping.json),
[exact v2 patch proposal](specs/002-data-and-risk-scoring/proposals/v2-contract-changes.json).

- Public unauthenticated Kaggle metadata verifies current version 8 (2025-07-08)
  and CDLA-Sharing-1.0 on that listing. HI-Small member size matches the local
  475,664,283 bytes, but no publisher checksum was returned. Exact local release
  and original acquisition history remain unknown; v8 is a candidate reference.
- IBM's pinned official formatter supports sender Account at index 2 paired with
  From Bank and receiver Account at index 4 paired with To Bank. It parses naive
  minute timestamps and does not establish a source timezone or clock semantics.
- Mapping draft requires exact source-bound ordered-header/Account occurrence
  validation, separate sides, exact Decimal/source currencies, proposed 13 integer
  digits/scales 0–6/zero support and pre-filter CSV ordinal identity. Namespace,
  selected time policy, approved mapping/time hashes and reviewers remain null.
- Core v2 proposal: currency maxLength 17; required detail-envelope dataset_version;
  strict terminal-pattern fixes. Optional separate assumed_utc_for_synthetic_benchmark
  basis requires an explicit team decision; it is not a source UTC fact. Default
  import block remains. Public transaction version is checked internally and via
  detail/assessment/list/run equality; future semantic validators remain unimplemented.
- Corrected prior standalone-schema probe construction (root oneOf was retained).
  Proper probes demonstrate current ID/money final-newline acceptance and the
  candidate fix. Review probes pass; [exact hashes/results](evidence/tasks/feature-002-proposal-validation.json).
- No account access, dataset/PDF download, product/authoritative contract changes,
  import, training, activation or messages. No application tests rerun in this
  documentation slice; prior 346/151 results below remain historical. No commit/push.
  Baseline was clean at 63d3384; branch and existing work preserved.

One concrete next step: review the packet and supply retained provenance, or
authorize its single-file pinned-v8 verification, then record actual producer and
affected-consumer decisions before freezing mapping/contracts. Exact download,
hash comparison and missing-document steps are in the packet and were not run.

## Initial Feature 002 inspection handoff — 2026-11-13

This update supersedes planning-era source-absent/not-implemented statements below
for the inspection slice only. T001–T005 complete; T006 partial on source provenance;
T007 `pending_mapping_review`; T008 `pending_consumer_review`. [Implementation ledger](evidence/tasks/feature-002-implementation.md),
[source audit](evidence/tasks/feature-002-source-audit.md), [contract review](evidence/tasks/feature-002-contract-review.md).

- Read-only streaming `fraudlens.pipeline_cli inspect` and 36 authored inspection
  tests implemented. Only inspect is available; no import/model/run/v2 integration.
  Artifact ignore rule added and checked before local report generation.
- Local authorized `data/raw/HI-Small_Trans.csv`: 475,664,283 bytes;
  SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`;
  5,078,345 records; label tokens 0=5,073,168 and 1=5,177. These are source counts,
  not event-valid/supervised/model metrics. User supplied acquisition date/source;
  exact Kaggle release remains unknown. IBM upstream data-license statement
  verified; applicability to the exact acquired release remains pending.
- Duplicate `Account` headers at positions 2/4; minute timestamps without timezone;
  amount scales 2/6; currency names reach 17 characters, exceeding proposed v2
  maxLength 12. Mapping/namespace/time-policy hashes not frozen; no mapping file
  created. Contract review records a separate detail-version wording inconsistency.
- Actual source scan returned controlled exit 2 (`duplicate_headers`,
  `provenance_incomplete`), with complete observations; source hash verified unchanged.
  Small sanitized evidence is prepared for Git; full report remains ignored/local.
- Initial RED: 30 intended missing-inspector failures in test bodies. GREEN: 30,
  then 36 inspection tests after extra form/option assertions. Lexical-summary
  follow-up: 2 RED/34 passing, then 36 GREEN. Final backend 346 passed; frontend
  151 passed; Ruff/typecheck/build passed. Existing Starlette/httpx warning remains.
  Foundation v1 code, schema, fixture and frontend unchanged.
- Phase 2 source lookup complete, compliance `pending_requirements_unavailable`.
  Human code/mapping/contract review and independent reproduction pending.
  No download, training, substantive evaluation, browser run, commit or push.

One concrete next step: obtain exact acquired-release evidence and actual
producer/affected-consumer decisions for duplicate-header direction, timezone,
currency bounds and detail-version wording before starting import.

## Current state
Feature 001-project-foundation completed/accepted in its local synthetic-demo scope:
T001-T028 checked. Vedran Mitic confirms joint setup verification and human
code/contracts/evidence review by all team members. No individual signatures or
separate-machine installations claimed. Historical pending entries superseded.
- Peer results: 310 backend passed (exit 0), 151 frontend passed, Ruff,
  typecheck/build, health/UI/retry and 404/422 results recorded.
- Project Python 3.14.3; system py 3.14.7; Node 24.20.0; npm 11.19.0; uv 0.10.9.
- Prior temp permission errors resolved through unique workspace temp/cache paths.
- Known Starlette/httpx warning remains, no outstanding failure reported.
- Evidence: evidence/tasks/peer-reproduction.md, human-review.md,
  phase-06-handoff.md and foundation-validation.md. Browser evidence remains the
  historical T019 run; no new browser/test run during acceptance recording.

Feature **002-data-and-risk-scoring planning history** (current inspection progress above):
- [Specification](specs/002-data-and-risk-scoring/spec.md): import/provenance, historical
  features and rules, bounded ML comparison, local explanations and dataset-backed case review.
- [Quality checklist](specs/002-data-and-risk-scoring/checklists/requirements.md): agent
  document review recorded; human, Phase 2, technical-plan and implementation gates
  remain open. No unresolved clarification markers.
- [Specification evidence](evidence/tasks/feature-002-specification.md) and
  [original request](prompts/development/002-data-and-risk-scoring-specification.md).
- [Technical plan](specs/002-data-and-risk-scoring/plan.md),
  [research decisions](specs/002-data-and-risk-scoring/research.md),
  [data model](specs/002-data-and-risk-scoring/data-model.md),
  [v2 contracts](specs/002-data-and-risk-scoring/contracts/api.md),
  [quickstart](specs/002-data-and-risk-scoring/quickstart.md) and
  [Codex prompts](prompts/development/002-implementation-prompts.md) are drafted.
  [tasks.md](specs/002-data-and-risk-scoring/tasks.md) now contains the generated
  implementation plan. Source audit, mapping approval, affected-consumer contract
  review, implementation and actual Feature 002 verification remain pending.
- [Adversarial review transcript](prompts/development/002-review.md) is reflected in the
  revised specification: label-independent event history, meaningful rule baseline,
  temporal/threshold/evaluation safeguards, import/run completion, contract migration,
  acceptance scenarios and a proposed contributor code/task handoff. See
  [revision evidence](evidence/tasks/feature-002-specification.md).
- Authoritative Phase 2 assignment requirements remain unavailable; the checklist
  is not that source and no Phase 2 compliance claim is made.
- No IBM dataset downloaded/audited, no model trained, no dependencies or product code changed.
- Defaults: chronological 70/15/15, strict past-only history, label-free operational data,
  one deployed explainable model compared to rules. AutoML is optional and bounded.
- Foundation's fixed-size IDs and amount/currency limits require explicit reviewed contract
  migration; do not relax validators or lose source precision silently.
- The preceding planning request authorized technical planning and future
  prompts only. No Feature 002 implementation was performed by that unit.

## Historical next step before the inspection slice
Start Feature 002 T001: create the implementation evidence ledger with the actual
working revision, original implementation prompt and environment after reading
AGENTS.md and this handoff. The next implementation slice is source-independent
inspection; its RED/GREEN tasks are T004–T005 after the setup/ignore prerequisites.
Use [tasks.md](specs/002-data-and-risk-scoring/tasks.md) for exact dependencies.
Select specs/002-data-and-risk-scoring explicitly in each PowerShell session.
The current request authorizes planning-to-tasks only; implementation requires a
later work request. No automatic commit/push is authorized for this unit.
Preserve existing local changes and the Foundation v1 fixture checks.

## Contribution evidence report added 2026-11-12

- Added [consolidated evidence and contribution plan](evidence/tasks/project-evidence-plan-2026-11-12.md),
  with the complete 19-commit ledger through f63bffe, three identifiable contributors,
  task-level attribution, shared T019 credit and future evidence/time capture plan.
- [Reproducible calculation](evidence/tasks/project-evidence-calculations-2026-11-12.json)
  gives 10.76 provisional person-hours centrally, 7.17–14.34 under explicit
  publication-window assumptions. These are not measured hours or confidence bounds.
  No work/hours assigned to an unnamed fourth member, per current user clarification.
- Documentation only; no application tests/browser runs, feature implementation,
  acceptance marker changes or Git commit/push. Historical runtime/test results above
  remain unchanged. See report for source limitations and participant confirmation needs.
- Audit verification passed: calculation script; 19-row Git/date/author reconciliation;
  independent arithmetic; 43 local links; UTF-8/fences/whitespace/helper syntax;
  historical test-count reconciliation. Source inventory covers 69 pinned files.
- This contribution report does not authorize implementation; the current next
  development step is Feature 002 task generation described above.

## Feature 002 technical-plan handoff added 2026-11-12

- See [planning evidence](evidence/tasks/feature-002-technical-plan.md) and
  [original request](prompts/development/002-technical-plan-request-2026-11-12.md).
  The plan and supporting research/data/API/scoring contracts, JSON Schema,
  quickstart and eight future Codex prompts are documentation proposals.
- The current shell lacks an invokable Python 3.14 and `jsonschema`; JSON parse,
  internal schema references, example arithmetic and 52 local Markdown links
  were checked with Python 3.13.3. `git diff --check` passed. No application
  tests or IBM import/model run occurred.
- `data/artifacts/` is not yet ignored by Git. The first implementation slice
  must add/check that ignore rule before artifact generation. Raw/processed
  paths are already ignored. Source audit, Phase 2 document, contract review,
  tasks, human review and independent reproduction are open.
- This handoff preserves existing local edits and makes no Git commit/push.

## Documentation publication request — 2026-11-12

- The user explicitly requested commits and a push for all pending documentation;
  see the [original publication request](prompts/development/002-publication-request-2026-11-12.md).
  That instruction supersedes earlier no-commit/no-push statements for this
  session. It does not expand Feature 002 implementation scope.
- The [contribution report addendum](evidence/tasks/project-evidence-plan-2026-11-12.md)
  names the four publication commits and their distinct contents. The historical
  19-commit time calculation remains pinned and does not count unmeasured hours
  from these documentation commits.
- Verify the current local/remote branch state with Git. The concrete next
  development step remains Feature 002 tasks.md generation and source/contract
  audit; human, Phase 2, dataset and implementation gates remain open.

## Feature 002 task-generation handoff added 2026-11-13

- Generated [tasks.md](specs/002-data-and-risk-scoring/tasks.md) using the local
  speckit-tasks skill: 67 unchecked tasks, explicit dependencies, RED before GREEN,
  five story increments and separate source audit, mapping and consumer gates.
  Coverage tables allocate every FR-001–026 and SC-001–009 to work, tests and
  future evidence. They do not establish requirement satisfaction.
- [Task-generation evidence](evidence/tasks/feature-002-task-generation.md) records
  inputs, commands, execution-policy/launch limitations and unrun work.
  [Static inspection inventory](evidence/tasks/feature-002-task-plan-validation.json)
  records 35 requirement rows, 23 existing paths and 51 explicitly planned paths;
  no document-order/coverage-reference/undeclared-path issues were reported.
  The [inspection script](evidence/tasks/feature-002-task-plan-validation.ps1)
  only reads planning text and file metadata; it does not run application checks.
- IBM source is absent under data/: T006 remains pending_source_unavailable;
  mapping T007 and dependent source work remain pending. T008 requires actual
  producer/consumer review. Phase 2 remains pending_requirements_unavailable;
  human explanation/code review and independent reproduction remain pending.
- No application/lockfile/v1 contract changes, dependency installs, downloads,
  import, training, model metrics, backend/frontend tests or browser runs occurred.
  Historical Foundation evidence is unchanged. No commit, push or branch switch
  was issued. The 2026-11-12 publication request above is historical; this unit
  follows the current explicit no-commit/no-push instruction.
