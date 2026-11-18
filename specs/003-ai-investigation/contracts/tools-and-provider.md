# Tool, provider and local command contracts (planned)

## Runtime boundaries

`CaseContextReader.resolve(case_id, source_mode, snapshot_ref)` returns a validated immutable context or controlled unavailable/stale result. `HistoryReader.read(context, account_side, limit)` returns authorized strictly pre-cutoff history; no tool accepts bank/account identity directly. Feature 002 owns eventual history production; feature 003 owns adapter validation. A fixture adapter may expose authored history, or explicit unavailable; it cannot claim observed dataset history.

`KnowledgeReader.search(query, corpus_version, retrieval_version)` returns <=5 passage references/text and adequacy status. `Provider.next_turn(conversation, tools, report_schema, remaining_limits)` returns tool requests, structured draft, refusal/incomplete or controlled failure with model/request IDs and nullable usage. `InvestigationRepository` owns context/evidence/run/review transactions and compare-and-swap; no external I/O in its transactions.

## Allowed tools

All argument objects are closed, strict and have every property required. Explicit nullable values represent optional choices. No model-provided run/case/corpus/model/actor/SQL/path/URL fields.

| Tool | Exact arguments | Result / authorization |
|---|---|---|
| get_case_facts | `{}` | Case evidence from server-bound context, available/unavailable fields, source/score/time/precision notices; no hidden labels |
| get_account_history | `{account_side: sender|receiver}` | Bank+account inferred locally from selected side, strict pre-cutoff, lookback=7 days, <=50 ordered events, coverage/truncation/availability and deterministic per-currency aggregates |
| search_procedures | `{query: string (1-500 trimmed characters)}` | Search pinned corpus/retrieval, <=5 exact passages with provenance and no-match state |

Tool outputs are <=16,000 UTF-8 bytes after safe projection; truncate complete result items deterministically and expose returned/eligible counts and truncated. Never cut raw JSON or silently clip an exact money field/passage. An individual oversized item produces controlled tool_result_too_large. Truncated history cannot be represented as full history; aggregates may be computed over the permitted lookback before display truncation only if labeled with scope/count and provenance. No aggregates across different currencies. Unavailable history returns no invented list/aggregates. Empty available history is a different state.

Each executed tool increments the 12-call limit before execution. Invalid arguments/scope are audited as rejected; they do not execute or expand the model's permissions. Provider requests consumed to make invalid tool calls still count. Deterministic tool failures can inform a limited draft; missing case identity or stale source fails the attempt. Search no-match is not a tool infrastructure error.

## Provider projection and strict output

Use OpenAI Responses custom function tools with strict argument schemas, `parallel_tool_calls=false`, and final `text.format` strict report schema. Refusal, incomplete response, unsupported schema/model and invalid tool responses remain explicit outcomes. Runtime SDK version resolved/locked at implementation, no guessed dependency version.

Outbound allowlist: instructions/prompt version; tool definitions; typed report schema; case/run-scoped opaque evidence/transaction identifiers; source mode and synthetic notices; event/raw time and time-basis; exact paid/received money/currency; score kind/source/version and actual available explanation values; server-aliased account sides; permitted history summaries/events; selected procedure text and provenance. Exclude credentials, source file paths/row ordinal, raw source rows, hidden targets, evaluation references, human-review notes and unrelated accounts. Context-revision IDs bind identity without revealing source-file path. Actual tool output is projected before provider delivery; privacy assertions test all turns and continuation items, not only the initial prompt.

Model output supplies report content only, not IDs/permissions/state/review. The application assigns attempt/report identity, immutable context references and final state after validation. Provider schema uses the ReportDraft definition and a strict supported subset (all keys required, additionalProperties=false, nullable optional values); provider capability probe verifies the compiled schema. Public/internal schemas need not be accepted by the provider without that compilation step. No schema weakening to make a failing call pass silently.

Preserve provider-required continuation items/call IDs privately, including opaque reasoning items if required by the API. Do not expose a reasoning transcript or present model reasoning as evidence. Store=false where supported; local state is authoritative. Required settings must be verified against the selected model; no assumption of temperature/seed support.

Maintenance v7: new attempts privately pin `report_policy=human_authority_notice_v1`
with application prompt v4. Require the exact separate limitations item
`Konačnu odluku donosi ljudski analitičar; AI nacrt ne izvršava radnje.` in either
outcome. Omission uses fixed `human_authority_notice_required` repair guidance,
within the existing single-repair budget, then fails if still absent. This is a
literal protocol check, not semantic safety approval. Raw drafts are not edited;
the public ReportDraft schema and semantic_review status remain unchanged. Old
bindings lacking this policy retain old validation; retry inherits its parent's
policy/prompt. Unknown policy is rejected before dispatch. Full design:
[human-authority-v7.md](../human-authority-v7.md).

## Accounting and recovery

8 dispatched provider requests, 12 executed tools, 120 s elapsed per attempt. Request <=30 s and <=remaining deadline; input <=48,000 UTF-8 bytes; max_output_tokens=4096; full received response <=2 MiB using bounded transport reading (Content-Length alone is insufficient). SDK hidden retries disabled. At most one transient retry with <=2 s backoff and one schema/reference repair; both count against all budgets. Oversize/incomplete/refusal does not trigger endless repair. No retry for access, unsupported model/schema or rejected credentials. Persist actual/unknown usage, never inferred spend.

Reserve budget and dispatch intent before sending, then release DB lock. Unknown result after crash is not proof that no request executed. On restart mark interrupted/failed and require a new explicit child attempt. Cancel/deadline and late responses use state/revision CAS; a late response cannot publish. Retrying can spend additional tokens; no exactly-once billing guarantee. Child attempt may copy revalidated evidence only when context/corpus/config still compatible. It does not automatically replay ambiguous requests or reset counters in the old attempt.

## Planned CLI

`uv run --locked python -m fraudlens.investigation.cli <command>` from root.

| Command | Main inputs / effects |
|---|---|
| prepare-knowledge | --manifest, --store; local validated complete corpus, no network download |
| probe-provider | --synthetic-only; explicitly requested availability + minimal tool/report capability check, safe request IDs/model/usage; no case data |
| worker | --store, --once or --poll; explicit one-worker claim, persist outcomes, no automatic retry after restart |
| evaluate-retrieval | --protocol, --configuration baseline|improved; deterministic ranks/metrics to ignored output |
| evaluate-reports | --protocol, --provider test|openai; inputs only to provider, held-out reference join occurs offline after reports frozen |
| summarize-reviews | --protocol, --reviews; validate reviewer completeness and compute rubric counts/disagreements |

All command paths are trusted local operator inputs, never model/browser arguments. Print safe IDs/counts/reasons only. Exit 0 completed, 2 missing/ineligible prerequisites, 1 execution/validation failure. A completed metric computation below target records failed quality acceptance even when command execution succeeds. No provider initialization at module import or ordinary GET/startup.

## Explicit report-v6 addendum, 2026-11-18

Authorized opt-in generator profile: report_prompt=v6 with OpenAI semanticv8 may
set max_output_tokens8192. Default remains4096 and old prompt bytes unchanged.
Both application and metered harness factories pass explicit output_token_cap8192
from persisted attempt binding; default provider cap remains4096. Rejected caps
fail before HTTP; SDK retries0, output response2MiB and request/input limits retain
prior ceilings. Semantic selector output budget remains its own unchanged budget.
Request45/selector30/total120 and8requests/12tools are not increased.

New v6 attempts pin history_bounds_version1. History evidence text and exact-fact
projection add window_start_inclusive and window_end_exclusive. The former copies
actual history start; latter is UTC cutoff floored to minute, exclusive. Unavailable
history has null values; no cutoff or totals inferred. The typed history envelope,
raw cutoff and filtering rules are unchanged; no old evidence or bindings altered.
Legacy attempts omit fields. Retries preserve version/prompt/output caps and
revalidate evidence using the same source reader before reuse. These additive
public facts are not private expected answers. Code computes, new prompt copies.

Future opt-in settings (not activated by this document):
INVESTIGATION_PROVIDER=openai, INVESTIGATION_SEMANTIC_RETRIEVAL=true,
INVESTIGATION_SEMANTIC_PROFILE=v8, INVESTIGATION_REPORT_PROMPT=v6,
INVESTIGATION_MAX_OUTPUT_TOKENS=8192. Request45 remains separately explicit.
Evaluation freezes must include max_output_tokens8192 and report_promptv6; shared
runner defaults omitted fields to old4096. New input/source/code freezes are
required; no old acceptance/profile/prompt hash inheritance or live-spend approval.
