# Live full-report / controlled repair v6 — 2026-11-16

User authorized continuation on feature03-reliability-v2 after published4262193.
Design: [live-repair-v6.md](../../specs/003-ai-investigation/live-repair-v6.md).
Original request: [development prompt](../../prompts/development/003-live-repair-v6-2026-11-16.md).
No production runtime, application/judge prompt, dependency or .env changes.

## Frozen method

Three fresh authored template instances; two ordinary quality cases (incomplete
mixed-currency history with guidance, unavailable history/controlled no-match)
and one application-candidate fault diagnostic with unavailable history/guidance.
The controlled provider wrapper preserves the actual model draft/private items
and full SDK history. It delivers an intentionally invalid authored candidate to
local validation once, using actual case evidence but a wrong typed assertion.
The normal strict validator and bounded repair then handle the real next response.
This measures controlled application-candidate recovery, not a natural model error.

Primary quality denominator is exactly2 ordinary cases including failures.
Diagnostic final report rated separately. Three opaque calibration packets
accompany available reports in one same-model judge call; expected labels stay
local. Failed/unavailable calibration blocks quality claims; thresholds/support,
coverage, mandatory disclosures and zero critical errors remain unchanged.
Authored development templates and same-model calibration are not an independent
holdout or human review. All old outcomes/failed release targets remain intact.

Pack: evals/investigation/development-v6/. Raw sealed outputs/private continuations,
fault candidate, freeze and durable ledger: ignored evals/results/feature-003/development-v6/.
Maximum25 actual transports,8 per generation case and1 judge, no hidden retries
or ambiguous replay. Existing8requests/12tools/1repair/1retry/30s/120s/48k limits
unchanged. Stop after quota/credit/rate/access failure; no tuning between cases.
Judge60s/8192 output tokens/200k input. Record input bytes and repair transport
identities. Completed batches and leftover allowances must not be replayed.

## Executed preparation and verification

Existing Python3.14.7/OpenAI SDK3.51.0/httpx2 environment; no installs.
Explicit feature003 prerequisite/checklist gate16/16 PASS, no extension hooks.
RED6 intended failures before harness guards; GREEN11 new checks and42 related
checks PASS. Full backend **893 passed in61.61s**. Ruff/diff PASS before dispatch.
All32 previous artifact hashes verified; new source/input/reference/protocol
frozen before the first actual request. No prior holdout/reference reuse for tuning.

```powershell
.venv/Scripts/python.exe -m pytest backend/tests/unit/test_investigation_live_repair_v6.py -q --tb=short
.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short
.venv/Scripts/ruff.exe check backend evidence/tasks/feature-003-live-repair-v6.py evidence/tasks/feature-003-live-repair-v6-inputs.py
$env:PYTHONPATH = 'backend/src'
.venv/Scripts/python.exe evidence/tasks/feature-003-live-repair-v6-inputs.py
.venv/Scripts/python.exe evidence/tasks/feature-003-live-repair-v6.py
.venv/Scripts/python.exe evidence/tasks/feature-003-live-repair-v6.py --execute
```

Builder/execute commands above record the one authorized execution; do not replay.
At execution no commit/push was requested. Subsequent user instruction explicitly
authorized publishing this completed unit on feature03-reliability-v2 before T088.

## Actual outcomes

**17/25 actual transports:16 generation +1 judge, all HTTP200**, returned model
`gpt-6-luna` throughout. No timeout, transient retry, quota/access error or unknown
usage. Reported73,054 input +13,630 output = **86,684 tokens**; spend unknown.
All three attempts ended as validated `needs_information`, each within90/120s.
This is a draft sufficiency state; no human disposition was made.

| Case / role | Seconds | Requests / tools / repairs | Machine quality |
|---|---:|---|---|
| DEV6-761 ordinary | 27.194 | 5 / 4 / 0 | PASS |
| DEV6-762 ordinary | 26.171 | 5 / 4 / 0 | FAIL: missing human-authority disclosure |
| DEV6-763 controlled candidate fault | 43.954 | 6 / 4 / 1 | Separate final-report PASS |

Ordinary quality **1/2**, with both cases retained in the denominator. On these
two reports, factual support6/6 and essential coverage19/19; procedures1/1 on761
and0/N/A on762. No critical or additional machine flags. The failed762 report
does not state that a human analyst retains final authority: the judge marked
`missingness_correct=false`. Its summary/observations/limitations/missing fields
were inspected offline; they cover fixture/score/history/time/no-guidance gaps
but omit that authority statement. This supports retaining the failure without
regrading or weakening the requirement. No automatic intervention actually ran.

All **three calibration packets matched**. The single same-model judge call took
36.438s. This narrow calibration supports these machine ratings conditionally;
it does not establish independent evaluator reliability or human validation.
No causal before/after improvement claim or original release-gate pass.

The controlled diagnostic injected exactly once, local validation recorded
`exact_assertion_mismatch`, and one actual repair request was dispatched with
`tool_choice=none`. Request size **37,169<48,000 bytes** (also the largest generation
request), leaving10,831 bytes. The next actual model draft passed unchanged local
schema/fact/citation validation. Its separate machine rating had factual4/4,
essential7/7, procedure1/1, correct missingness and no critical/additional flags.
It is **excluded from the2 primary reports**. A natural model failure was not
claimed; raw model output and continuation differ intentionally from the labeled
injected application candidate, whose only purpose is exercising strict recovery.

## Final audit and handoff

```powershell
$env:PYTHONPATH = 'backend/src'
.venv/Scripts/python.exe evidence/tasks/feature-003-live-repair-v6.py --audit
git diff --check
```

[Safe audited results](feature-003-live-repair-v6-results.json): **PASS**.
Frozen inputs, runtime, runner, prompts/configs and all32 pre-existing artifact
hashes match. Ten new raw/metadata JSON hashes exported;13 cited evidence IDs
resolve through actual revalidated reports. The injected candidate remains
strictly invalid; original private items match their recorded hashes. All
generation request sizes, same-schema continuation, repair tool_choice and
8/12/1/1 ceilings were checked. No old results/scores overwritten or rerun.
Secret exclusion, local links and193-line ignored guide checked. No post hooks.

No production code change or new API batch after these outcomes. Unused8 requests
are not a reusable allowance. New evaluation artifacts/tests/docs were initially
local on feature03-reliability-v2, HEAD4262193; user subsequently authorized their
commit/push. Pending human/producer/reproduction/full
Converge and original failed quality/retrieval/latency gates remain open.

Next concrete step: authored RED regression for the missing explicit human final
authority in no-guidance drafts, then a separately designed/versioned correction.
Preserve immutable reports/raw responses and unchanged semantic thresholds; do not
fix the score by dropping that disclosure. Task T088 records this unstarted work.
