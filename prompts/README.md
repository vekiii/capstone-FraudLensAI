# Prompt records

`development/` preserves original implementation instructions, sanitized before
tracking. Link the record from task evidence. Save the received instruction before
implementation; preserve existing content and append clearly dated amendments
instead of reconstructing an “original” afterward. Record redactions without secrets.
The phase 1 record is [001-foundation-phase-01.md](development/001-foundation-phase-01.md);
it does not complete the later T023 record.

`app/` is reserved for versioned application prompts when a feature actually uses
them. Create it with its first meaningful file. Give each prompt a stable ID/version,
purpose, expected inputs/output contract and change rationale; link its version from
execution/evaluation evidence. The foundation has no LLM integration or runtime prompt.

Prompts describe instructions, not proof of execution. Actual commands, results,
limitations and review status belong in `evidence/`. Do not store credentials,
personal/financial data or hidden evaluation answers in prompt records.
