# T068–T072 reliability maintenance — 2026-11-16

Completed within the user-authorized maintenance scope, not full feature003
acceptance. [Original request](../../prompts/development/003-reliability-v2-2026-11-16.md).
[Design](../../specs/003-ai-investigation/reliability-v2.md).
Baseline cd98ea021a38b362b5766c4e23a1e55ec0ad0dcd, initially clean, feature03.
Private .env and existing milan files preserved. No new live provider calls,
installations, dependency/lock changes, producer changes or Git publication.

## Diagnosis and evidence limits

Original primary eight outcomes: two needs-information drafts, six failures:
**2 output_invalid, 4 budget_exhausted**. All eight terminal within 120 s.
Five demos: two needs-information outcomes, three failures:
**1 output_invalid, 2 budget_exhausted**; 2/5 succeeded within 90 s;
maximum 7496.290298 s violated the terminal-time target.
Original post-hoc automated quality remains **0/8**. No new evaluation is claimed.

Ignored live-v1, judge-v2 and retrieval-v1 archives are absent here. Exact invalid
fields/prose, token vs request/time-budget causes and the outlier's transport
timeline cannot be established from aggregate failure codes. A working model/key
does not itself resolve these application-level failures. Raw results were not
reconstructed; held-out reference text was not opened for these fixes.

| Reproducible code gap | Change | Limit of evidence |
|---|---|---|
| Repair only forwarded output_invalid | Fixed allowlisted reasons/hints and private reason audit; prompt v2 explains evidence types/references | Authored/mocked tests, not proof old drafts pass |
| Final request could gather tools without another chance to draft | tool_choice=none on last permitted request and single repair | Budgets unchanged, no measured live improvement |
| provider.aclose awaited outside time limit | Bound cleanup by remaining attempt time, at most 1 s; fixed timeout/failed audit | Cooperative asyncio, not proof of historical outlier cause |
| Cyrillic tokens did not resolve Latin glossary keys | Explicit sr_cyrillic_to_latin_v1 query policy and separate candidate | Known-word script equivalence, not full Serbian comprehension |

New attempts pin prompt v2; retries retain their parent's pinned prompt. Prompt v1,
old configuration and all saved attempt/report bindings remain unchanged.
Strict validation, one repair, 8 requests, 12 tools, 30 s per request and 120 s per
attempt remain. No raw exceptions/rejected prose/references enter repair feedback.
Legacy repair messages remain supported; unknown reasons reject before dispatch.
Cancellation is not swallowed by cleanup; a close error cannot replace a saved report.

Candidate uses the **existing demo heuristic cutoff 0.5**, not a retuned/evaluated
cutoff. It is explicitly unvalidated/opt-in; ordinary preparation without
--retrieval still uses the original demo config. Existing reviewed glossary terms
are reused unchanged. No added translations, stemming, automatic deployment or
held-out-based cutoff selection. Missing policy preserves legacy semantics;
unknown policy fails closed. Host suspension or blocked synchronous work cannot
be bounded by an in-process cooperative timeout.

## Actual RED → GREEN and checks

Python **3.14.7**, Node **24.20.0**, npm **11.19.0**, installed SDK **3.51.0**.
Scoped speckit-implement, explicit feature selection, prerequisites PASS.
Ordinary PowerShell script execution was blocked; child -ExecutionPolicy Bypass
-File succeeded without changing machine policy. Checklist16/16; no extension hooks.

Initial new tests: **17 failed / 4 passed**, exit1. One script fixture cutoff also
rejected the Latin synonym; changed the UNIT fixture to 0.0 to isolate conversion
(candidate remains0.5). First combined GREEN: 1 failed/75 passed; empty citations
hit schema validation before set validation. Corrected fixture to a valid unused
ID to isolate citation_set_mismatch; validator unchanged. Next **76 PASS**.
Final-request regression separately RED: **1 failed/21 deselected**, before code.
Combined GREEN after fix: **77 PASS**. External cleanup-cancellation regression
was then added and included in the complete suite.

Retrospective confirmation: original provider/retrieval/workflow source loaded
using git show into an isolated Python process's memory, with original __file__
paths; no checkout/file mutations. Final23 tests against original behavior:
**18 failed / 5 passed**, exit1, 7.58s. This confirms final fixtures detect original
defects; it is not the chronological initial RED. First harness invocation hit
an original UTF-8 BOM before tests; utf-8-sig decoding corrected instrumentation,
not business behavior.

Executed commands from root (.cache parents created before pytest):

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
powershell -NoProfile -ExecutionPolicy Bypass -File .specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_investigation_reliability_v2.py -q --tb=short --basetemp=.cache/reliability-v2/red-tmp -o cache_dir=.cache/reliability-v2/red-cache
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_investigation_reliability_v2.py -q --tb=short -k last_provider_request --basetemp=.cache/reliability-v2/final-request-red-tmp -o cache_dir=.cache/reliability-v2/final-request-red-cache
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_investigation_reliability_v2.py backend/tests/unit/test_investigation_workflow.py backend/tests/unit/test_investigation_openai.py backend/tests/unit/test_investigation_retrieval.py backend/tests/integration/test_investigation_recovery.py -q --tb=short --basetemp=.cache/reliability-v2/green3-tmp -o cache_dir=.cache/reliability-v2/green3-cache
.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short --basetemp=.cache/reliability-v2/full-tmp -o cache_dir=.cache/reliability-v2/full-cache
.venv/Scripts/python.exe -m ruff check backend evidence/tasks/feature-003-reliability-diagnose.py evidence/tasks/feature-003-reliability-smoke.py
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-reliability-smoke.py
.venv/Scripts/python.exe -X utf8 evidence/tasks/feature-003-reliability-diagnose.py
git diff --check
```

Full backend **814 PASS in65.95s**, exit0 (791existing+23new). Ruff/diff PASS.
Actual isolated localhost HTTP/CLI smoke **8/8 PASS**, exit0,2.004s: real six-document
preparation; original three-case browsing; Latin/Cyrillic same IDs/scores; no-match;
queued creation with zero dispatches; CLI worker, three scoped tools, saved test
report, four authored provider turns and pinned candidate. It uses an absent
ENV_FILE, empty keys and isolated .cache store/free port, stops only its hidden
owned backend. **Zero real provider calls**. No manual UI/browser run claimed.
Frontend unchanged; its tests/typecheck/build were not rerun.

## Integrity and completion boundary

[Baseline manifest](feature-003-reliability-v2-baseline.json): LF-normalized hashes
for42 original source/config/protocol/input/reference/summary files. Diagnostic
hashes reference files without parsing their content. Exactly three expected
runtime files changed; all other39 match, including original prompt, glossary,
config, protocol, freezes and evaluation summaries. New files are explicit
additions. Original runtime remains available at baseline commit. Old frozen-source
audits must use that checkout, not claim the new revision is the old runtime.
Raw archive integrity cannot be freshly checked here; historical hashes remain.

Focused consistency review of v2 design/T068–T072: mechanics implemented/tested,
no weakened public/source/schema/evaluation contract, no runtime reference loader.
Local Milan guide `milan/feature03-provere-v2.md`: **144 lines**, explained PowerShell
commands, local automated/manual setup and separately marked optional paid checks.
Its CLI/API paths were exercised by smoke; browser actions/real calls remain
instructions. T068–T072 complete for this scope; human review pending.
Existing `.git/info/exclude` excludes `/milan`; the requested local guide is saved
there but not versioned. That existing exclusion was preserved. Shared quickstart
and executable smoke remain available in the repository for other contributors.

T062–T064 producer integration, T066 teammate reproduction/review and full feature
Converge T067 remain pending. Failed original quality/time criteria are preserved.
Fresh independent quality estimates need a new versioned protocol/fresh held-out
questions/scenarios. No replay of old batch or use of unused old call budgets.
Next: review v2 and scope/freeze a bounded development-only live test on new
synthetic input before fresh independent evaluation.
