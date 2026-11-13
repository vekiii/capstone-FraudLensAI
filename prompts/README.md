# Prompt records

`development/` preserves original implementation instructions, sanitized before
tracking. Link the record from task evidence. Save the received instruction before
implementation; preserve existing content and append clearly dated amendments
instead of reconstructing an “original” afterward. Record redactions without secrets.
The phase 1 original is [001-foundation-phase-01.md](development/001-foundation-phase-01.md).
The [foundation instruction index](development/001-foundation.md), added for T023,
links preserved phase/task originals, continuations and their execution evidence.

`app/` is reserved for versioned application prompts when a feature actually uses
them. Create it with its first meaningful file. Give each prompt a stable ID/version,
purpose, expected inputs/output contract and change rationale; link its version from
execution/evaluation evidence. The foundation has no LLM integration or runtime prompt.

Prompts describe instructions, not proof of execution. Actual commands, results,
limitations and review status belong in `evidence/`. Do not store credentials,
personal/financial data or hidden evaluation answers in prompt records.
