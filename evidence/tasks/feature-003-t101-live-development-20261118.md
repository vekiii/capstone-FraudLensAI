# T101 actual authorized development — stopped on unknown outcome, 2026-11-18

## Authority and unchanged scope

User explicitly confirmed the reviewed packet, isolated same-model judging and
new maximum115 T101+40 T102=155 requests: "potvrdjujem, mozes da nastavis".
[Decision](../../specs/003-ai-investigation/acceptance-v1-approval-20261118.md).
No new tasks, training, commit/push/merge or old-budget reuse. T101/T102 remain
open. Applied speckit-implement with explicit feature003 selection, read current
AGENTS/next_work/protocols; checklist16/16, no extension hooks.

Actual branch `feature03`, HEAD5431299, prior preparation changes preserved.
The existing development-proposal freeze matched **all68 source pins** before
execution and again after the stopped batch. No prompt, code, model, threshold
or timeout changed during the run. Frozen raw SHA:
`0d72c9adfc27fe2f196fd496181a01663940c420163bd6069885bd52da9ac3c1`.
An actual hash-bound approval.json was exclusively created for that stage with
the user's authorization text; no fixture consent record was reused.

## Actual execution

Existing prepared live stage:
`evals/results/feature-003/acceptance-preparation-20261118/development-proposal/`.
One-shot overall scope record:
`evals/results/feature-003/acceptance-live-20261118/session-intent.json`.

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/003-ai-investigation'
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
.venv/Scripts/python.exe .cache/t101-live-supervisor.py --batch evals/results/feature-003/acceptance-preparation-20261118/development-proposal
```

Supervisor launched hidden separate local API/worker processes, confirmed
documents readiness, and launched the external observer on loopback8768. Fresh
empty investigation queue and exclusive batch/per-case UUID intents; no prior
attempt reused. Model `gpt-6-luna`, source authored fixture, semantic v6 enabled.

**DEVQ1-01 failed, first GET-observed terminal at45.65846850001253 seconds.**
No report was generated/validated. The ordinary source was not a controlled
fault. Four actual tools completed: get_case_facts, sender history, receiver
history and semantic-backed search_procedures. Five provider requests completed
HTTP200, all returned `gpt-6-luna`. Sixth request was for the report, then timed out
at the unchanged30-second request boundary. Its delivery/completion/token usage
remain unknown; there is no saved response or request ID for that dispatch.

The workflow recorded request_timeout at08:15:51.167589Z after the preceding
semantic result at08:15:21.106023Z. The ordinary application reserved a transient
retry, but the transport ledger rejected it locally because the preceding outcome
was unknown. Thus application budget shows7 reservations/1 retry while **actual
transport attempts are6**, with **five completed and one unknown**. The terminal
API failure code is `provider_incomplete`, `outcome_unknown=true`; this is not
evidence that a returned report contained bad prose or that model access failed.
No runtime defect or provider-side root cause is established by the timeout alone.

All actual request bodies were within48000 bytes (8888,14070,16826,19074,7262,24506).
Known completed usage totals **13912 tokens**; sixth usage is **unknown, not zero**.
The semantic request counts inside the same investigation budget. No further
provider requests were sent after the unknown dispatch. The batch retained:

| Development slot | Actual outcome |
| --- | --- |
| DEVQ1-01 | failed, no validated report, unknown sixth provider outcome |
| DEVQ1-02 | not_run |
| DEVQ1-03 | not_run |
| DEVQ1-04 | not_run |

Observer exited0 after recording the controlled failure; that exit does not mean
the investigation passed. Raw view/context/evidence/audit/HTTP observations,
request/response bodies and ledger remain archived. Supervisor cleaned up its API
and worker processes AFTER the batch stopped; cleanup is not a terminal timing
observation or proof of remote provider cancellation.

## Subsequent offline work and verification

No paid calibration, held-out quality generation/judging or timing batch started.
The previously authored TEST5 and local20-search diagnostic remain preparation
results, not new live performance/quality acceptance. Historical0/8, failed/
unavailable calibration-quality,2/5/outlier and completed T098 remain unchanged.

Prepared a separate future v4 judging driver:
`evidence/tasks/feature-003-t101-judge-live-20261118.py`. It was written outside
the generation freeze while development was running; generation source pins
remained unchanged. It projects only public packets, meters each dispatch, freezes
schema/prompt/code before judging, requires separate hash-bound stage approval,
retains original outputs/errors and joins expectations only in the offline assess
command. It has **not executed any judge request or actual calibration**. Its
missing-approval guard and static checks were exercised; no complete live driver
validation or quality result is claimed.

Existing31 helper/guard regression tests pass after this unit; runtime source
unchanged from the preparation's1112-test full pass. Ruff/format/diff checks pass.
No new frontend, full model quality evaluation or second-person reproduction.

## Concrete decision needed; same T101/T102, no new task

The approved protocol explicitly stops on an unknown provider outcome. Do not
restart this exhausted/unknown batch, edit its ledger, erase DEVQ1-01 or assume
the unreturned call cost nothing. Six reserved actual requests count against155.

Offline continuation proposal and the exact three undispatched public objects:
`evals/results/feature-003/acceptance-live-20261118/continuation-proposal.json` and
`continuation-inputs.json`. Proposed alternative: retain DEVQ1-01 as failed;
continue ONLY DEVQ1-02/03/04 in a newly frozen continuation with max24 requests,
no timeout/prompt/model change and explicit prior6 accounting. Combined development
maximum30, whole original scope maximum153<=155. No continuation approval record
or new dispatch exists. This is a proposed continuation, not a rerun/replacement.

Ask the user whether to take that continuation or investigate the timeout first.
Do not silently bypass the unknown-outcome stop or add a task. Feature003 cannot
close: no fresh calibrated report-quality or actual five-case timing acceptance.
[Machine-readable actual observations](feature-003-t101-live-development-20261118-results.json).
