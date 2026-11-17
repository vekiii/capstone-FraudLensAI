# Semantic v6 actual implementation and bounded OpenAI diagnostics

User explicitly requests robust RAG after v5 failed. User approved up to30 calls
on public/educational passages/test questions, no retries. Branch remains
feature03-retrieval-v4; prior work/evidence preserved; no merge/commit/push.
Scoped speckit-implement, current handoff/constitution/feature read, selected
SPECIFY_FEATURE_DIRECTORY=specs/003-ai-investigation prerequisites PASS.
Design before implementation: retrieval-development-v6.md. No new dependency.

V6 replaces lexical adequacy heuristics with explicit semantic source sufficiency:
all current small-corpus passages (limit20/48k) passed as untrusted data. Explicit
OpenAI model selects <=5 authorized sources and exact supporting quotes or returns
insufficient. General policy must not answer specific customer facts/current legal
quantities. No query IDs, denylist, examples or labels in prompt/runtime. Exact
quotes and IDs validated deterministically; semantic fidelity is still a model
judgment, not guaranteed by valid quotes. Output rank weights are not probabilities.
Core and prompt were fixed before execution; exact bytes match archived freeze.

Explicit async port retrieval_semantic_adapter_v6.semantic_search requires caller's
durable dispatch reservation before a paid call. Legacy synchronous search remains
unchanged. NO hidden model invocation inside worker tools/API or unaccounted nested
spend. Application activation in existing routes still requires budget-aware
async wiring and failure/cancellation tests; this unit delivers the opt-in port,
not silent deployment into the analyst UI. Full app RAG/report quality not claimed.

TDD:7 initial tests RED (missing module), then GREEN7; expanded malformed/refusal/
size/private-field/quote/unknown-ID checks17 PASS. Full backend992 PASS83.49s,
exit0 before final budget-adapter tests. Final focused adapter/core tests recorded
at handoff. Ruff/diff PASS. Frontend unchanged/no rerun in this unit. No old source
facts, configs, labels, results or acceptance criteria modified.

Live script backend/tests/support/retrieval_semantic_v6_live.py --prepare froze
inputs, public passages, model, source/prompt hashes BEFORE requests. --run executed
exactly30 dispatches, intent persisted/fsynced BEFORE each, SDK max_retries0,
30second timeout,2048 output tokens,48k request/2MiB response transport cap,
store=false. Exclusive run marker prevents replay; first failure would stop batch.
All30 completed, returned model gpt-6-luna. Usage43259 input+3817 output=47076
tokens. Monetary cost not calculated. No further API calls authorized by this
exhausted batch. Credential read by existing private settings only; no key logged.
No ML/private customer data, training labels or reference answers sent to provider.

24 earlier exposed challenge queries plus6 additional author-controlled probes
(3answerable/3unanswerable) were fixed before execution. Only questions and public
source allowlist sent; references loaded AFTER immutable per-response outputs.
All15 answerable relevant documents ranked first; all15 no-answer correctly
insufficient; no missing/failed cases. Author-proposed references NOT independently
human reviewed. Source excerpts limited to existing educational corpus.

Post-hoc same30 comparison (local v5 only; no model calls/retuning):

| Variant | Recall@5 | MRR@5 | No-answer correct |
|---|---:|---:|---:|
| V5 |.5333|.50|5/15|
| V6 |1.00|1.00|15/15|

The v6 result covers prior difficult paraphrases and exact-customer/legal-fact
negative cases. This is stronger diagnostic generalization evidence, NOT proof
of zero overfitting, independent held-out acceptance or universal safety. Six
sources/agent-authored labels and model non-determinism limit inference. Repeated
performance, adversarial injection quality and larger-corpus scaling not assessed.
No adjustments made to semantic prompt/core after viewing results. Added adapter
was split into a separate module so actual live core hash remains exact.

Final focused core/adapter suite:19 PASS0.42s, exit0, after the992 full collection.
Ruff and final diff check PASS. Exact live core+prompt hashes reverified; split
adapter addition never altered the executed semantic policy. Same30-row local
v5 comparison was post-hoc reporting only, no model calls or candidate retuning.

Raw model outputs, request IDs, usage and freeze in retrieval-v6-live JSON;
local comparison in retrieval-v6-comparison JSON. Public input/reference/passage/
ledger/freeze bundle: evals/investigation/retrieval-semantic-v6-diagnostic/.
These are diagnostic artifacts, never future untouched acceptance data.

T095/SC-002 remain open: independent reviewed English acceptance and budget-aware
application integration are still needed. All30 allowed calls consumed. No automatic
rerun, silent model fallback, merge, task closure or report-quality acceptance.
