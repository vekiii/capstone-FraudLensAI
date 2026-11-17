# Explicit semantic-search HTTP contract v1

Existing GET search/documents/passages stay deterministic and free. With enabled
investigation+semantic retrieval and explicit OpenAI configuration:

POST /api/knowledge/semantic-search, Idempotency-Key UUID, JSON body
{"query":"English procedure question","corpus":"optional corpus digest"}.
Closed body, max4096 bytes; model/provider/actor/path cannot be client supplied.
Only loopback/same-origin requests. No automatic retry. One reserved provider call
per key; default lifetime store cap10, configurable1..30. Replay same key/body/
source/runtime returns saved job (pending202,completed200,failed503), no spend;
different body/source/model/runtime conflicts409. Provider failure is not no-match.

GET /api/knowledge/semantic-search/status with same Idempotency-Key returns saved
job; POST /api/knowledge/semantic-search/cancel, same key, JSON{} cancels own pending
job without another provider call. A separate window can cancel while original
POST awaits. Expired/interrupted calls remain counted; reads never redispatch.
Saved job fields: contract_version1,job_id,status,provider_requests1,corpus_version,
retrieval_version,runtime_revision,result(nullable SearchResult),error(nullable),
outcome_unknown,optional audit. Terminal states never accept late publication.

IDs are actor/key-scoped on server, not authentication. This remains local demo;
production auth/shared exposure is outside this task. Audit stores model/raw output
locally; do not send private customer questions as part of diagnostic evaluation.

For worker activation set INVESTIGATION_SEMANTIC_RETRIEVAL=true in API and worker
terminals; new binding pins model/policy/runtime. Existing attempt/retry keeps its
original mode; explicit non-reuse retry may bind a new runtime, and reuse rejects
changed policy. Semantic stages consume existing max8 provider requests/max12 tools/
max120seconds, including timeout/cancel/unknown outcomes. No separate hidden spend.
