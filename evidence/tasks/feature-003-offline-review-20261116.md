# Offline reproduction and technical review - 2026-11-16

Scope: [original request](../../prompts/development/003-offline-reproduction-review-2026-11-16.md).
Initial branch feature03, HEAD 1f3a09d, clean worktree. Read AGENTS/next_work,
Phase 8 tasks/reproduction/quickstart, current reliability handoff and v8 evidence.
No merge, install, model call, completed builder/batch replay or actual .env read.
All results here are agent-executed, not another teammate's manual reproduction.

## Reproduction issue found and corrected

Full backend initially: **918 passed, 1 failed**, exit 1, 98.13 s.
test_prepare_pins_actual_prompt_and_policy_without_opening_expectations depended
on ignored historical evals/results/feature-003/development-v2/audit.json, absent
from this checkout. This is a test reproducibility defect; it is not evidence
that the saved real v8 artifact audit failed, or an intended business RED.

Changed only backend/tests/unit/test_investigation_final_live_v8.py: its unit
preparation supplies an independently hashed authored temporary prior artifact
while retaining actual runtime/prompt hashes, secret-free settings and the guard
against opening expected labels. Added changed/missing-artifact cases; they must
still fail the actual production preparation check. Never fabricated the missing
old archive, skipped the test or bypassed production hash validation.
Targeted module **10 passed**, exit 0. Full final suite result recorded below.
Actual production live replay remains forbidden/unattempted.

### Final fresh regression

Existing Python 3.14.3, Node 24.20.0; no installs. A unique absolute .cache parent
was created for each pytest invocation. Actual commands:

```powershell
.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short --basetemp <unique-workspace-path>/temp -o cache_dir=<unique-workspace-path>/cache
# 921 passed, 102.23 seconds, exit 0; no exclusions/skips/xfails.
.venv/Scripts/python.exe -m ruff check backend
# All checks passed, exit 0.
npm.cmd --prefix frontend test -- --run
# 186 passed, 9 files, exit 0.
npm.cmd --prefix frontend run build
# TypeScript typecheck and production Vite build pass, exit 0.
git diff --check
# Exit 0.
```

Only production-independent unit-test setup changed; backend/src, frontend,
public contracts, runtime dependencies and frozen v8 inputs/results have no
tracked diff. Final netstat check found no owned service listening on 8000,
5174 or 9228; three browser components report owned_process_cleanup=PASS.
Existing 5173 service was preserved. Fresh component manifests bind actual
verifier source/generated hashes and result paths, all with zero provider calls.

## Browser/proxy/process reproduction

Original wrapper:
`PYTHONPATH=backend/src; .venv/Scripts/python.exe -X utf8
evidence/tasks/feature-003-phase08-browser.py --result-prefix
feature-003-offline-review-20261116`.
First sandboxed run reached two direct/proxy API checks, then Chrome GPU access
errors/CDP Page.enable timeout. Result file and cleanup-port warning preserved.
Escalated attempt with prefix ...-escalated stopped at occupied port 5173 before
checks; its failure is retained too. No approval-review rejection occurred.

netstat and escalated read-only Win32 process inspection identified port 5173
as an existing Vite service (PID 21496, npm-style command). Ownership by this
test could not be established, so it was NOT killed. Instead generated an
ignored wrapper copy under .cache/offline-review-wrapper/run.py that substitutes
5174 for frontend port 5173 in generated verifier copies; backend 8000 and CDP
9228 are unchanged. Existing Vite config still proxies backend 8000. No source
verifier, application config, user's browser profile or stored results rewritten.

Executed the wrapper outside sandbox with prefix
`feature-003-offline-review-20261116-isolated`. The same assertions passed:

| Automated check | Result |
|---|---|
| Knowledge/source archive, actual API/proxy, no-match, fixture errors/restart | 10 PASS |
| Review/citation, two sessions, linked corrections, immutable audit, needs-information | 9 PASS |
| Recovery/config, historical data, missing key/model and foundation fallback isolation | 10 PASS |
| Actual killed-worker boundaries, late replies, two-connection behavior | 6 PASS |

The four component results and browser execution manifest are separate files
with the ...-isolated prefix. All use synthetic/test providers, isolated databases
and absent ENV_FILE. Returned creation/saved evidence/worker/review behavior is
actual local API/CLI/browser execution, not mocked UI-only assertions. These
automated checks do not supply real analyst identity/sign-off or LLM quality.

## Focused technical code/contracts/evidence review

Reviewed current context.py/tool definitions/projection, review.py/store CAS
boundary, error recovery paths, provider response bounding and tests, closed
public contracts and producer reconciliation. Observed:

- Three bounded tool names and closed arguments retain server-owned scope;
  case facts use explicit outbound projection. Inspection is not a general proof
  of prompt-injection immunity; negative tests/browser checks provide bounded evidence.
- Analyst disposition uses server-owned actor, report/revision binding, request
  replay and a single review/audit transaction. No provider/tool authority to
  close/escalate is added. UI and audit checks passed.
- Dataset-shaped outbound projection exists, but CaseContextReader.resolve still
  explicitly rejects actual dataset mode. It is not a connected producer adapter
  or substitute for T062/T064. Missing seven-day history remains a real dependency.
- HTTP response bytes and request/time limits are bounded; the provider was not
  used here. Offline mechanics cannot establish real provider/report quality.
- No new blocking runtime defect found in this focused review; the unit-test
  historical-file dependency was corrected above. This is not exhaustive security
  review, human acceptance or producer agreement.

## Evaluation clarification (T094 partial)

Reviewed authored development-v8 calibration packet B, frozen expectations,
committed summary and evidence; no held-out tuning or regrading. Actual ignored
v8 raw results are absent locally, so full raw-judge rationale/hash reproduction
is unavailable. Calibration file normalized SHA256:
843364017ee3ab8f4126c34a1192d34c52e98e9b58ee8f8eb68a155c4532f1d4.
Committed v8 summary normalized SHA256 before work:
4e9d0a27d995cbc92be53935cae61d74ed66fcea449e704c0d9e2c06f585b793.

CAL8-B invents funds origin and also discloses that origin is unknown. The
recorded judge detected unsupported critical invention; failed calibration is
the additional missingness interpretation disagreement. Wrote a separate
[clarification proposal](../../specs/003-ai-investigation/calibration-clarification-proposal.md)
with explicit completeness/no-invention/consistency fields and six proposed new
controls. No original expected label, rating, threshold, denominator or result
changed. Failed calibration and unavailable semantic-quality conclusion stand.
Actual independent human review/new protocol adoption is still pending; do not
rerun the model from this document. T094 is not checked complete.

## Current limits and remaining teammate work

This run advances the automated/technical portion of T066 and prepares a human
decision packet for T094. It does not constitute another teammate's execution or
their code/contract review. T066 stays unchecked and T061 full quality acceptance
remains unavailable. Human reviewer/runner table in reproduction.md stays honest.
No T062 approval/T064 adapter, new API budget or full Converge completion inferred.

Actual teammate can use the existing reproduction procedure, identify their
checkout/versions and perform the manual fixture review. Port 5173 may already
be serving their app; do not stop it without coordinating. Review the T094
proposal as a distinct decision before any new calibration protocol or live run.
