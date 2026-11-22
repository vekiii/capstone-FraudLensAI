# V6 runtime integration and automated-judge evaluation, 2026-11-17

User explicitly authorizes API/worker integration and separate LLM-as-judge
evaluation. Use speckit-implement for T095 only, preserve all earlier evidence.
Maximum44 new public-data calls, no retries:20 candidate/20 blind judge/4 judge
calibrations. Earlier30-call allowance is exhausted and separate. No merge/push.

Opt-in semantic_retrieval setting defaults false. New investigation binding pins
semantic policy/model/corpus; old/retried attempts preserve original binding.
All semantic worker calls use existing8-dispatch/12-tool/120s attempt limits,
reserve intent before network, no hidden retries, respect source/cancel/deadline
before evidence commit. Invalid tool inputs must spend zero semantic calls.

Existing GET knowledge search remains deterministic/free. Explicit local-only
POST /api/knowledge/semantic-search is paid, idempotent, one request per job and
bounded lifetime store budget. Status/cancel with same key never redispatch;
cancelled/expired/stale jobs cannot publish late results. Provider failures remain
503 errors, never successful no-match. Closed request shape, server model/path,
strict source policy and ephemeral client transport with bounded cleanup.

Evaluation: use20 previously proposed/unexecuted English held-out inputs, pin
code/prompt/corpus before execution. Candidate receives only question/public
passages. Separate judge receives no candidate selection/reference labels; derive
complete relevant source sets/answerability with cited quotes in separate context.
Four synthetic known-label calibration questions must all pass; otherwise mark
judge quality invalid and do not accept favorable aggregate metrics. Freeze all
outputs before offline comparison. Record expected-source disagreement with AI
author references and do not silently discard/relabel failures. Same model is
correlated automated review, not independent human approval. User approves this
automated evaluation method for T095 only; no changes to T094/report criteria.
SC-002 thresholds remain .80/.70/all4 no-answer on16+4, all failures counted.
