# Execution evidence

The [project evidence and contribution plan as of 12 November 2026](tasks/project-evidence-plan-2026-11-12.md)
consolidates the historical work, named contributors, validation and provisional
time calculation. Its estimates are separate from measured working hours; source
task records remain authoritative for the original execution details.

Use [templates/task.md](templates/task.md) for task records in `evidence/tasks/`.
Link task/requirement IDs, original development prompts, code revision or working
diff, runtime/dependency/data versions, exact commands, exit codes and observed
results. Update the handoff after each task or coherent unit so another contributor
can continue from a checkout without conversation history.

Record RED → GREEN and regression for business behavior. RED must demonstrate the
intended missing behavior. For mechanical setup write “not applicable”; do not
invent failures. Distinguish passed, failed, not run, blocked and no tests collected.
Never treat absent tests as a passing suite. Planned commands are not execution.

Fixture checks verify synthetic contracts/behavior; they are not ML evaluation.
Model evaluation records additionally identify data/split/model versions and leakage
controls. Keep reference labels outside application inputs. Record manual checks
only when performed. Human review is `not_requested`, `pending` or `reviewed`;
name an actual reviewer and date only after review. Peer reproduction stays pending
until another teammate actually runs it (SC-001).

Development instructions belong in `prompts/development/`; versioned runtime
prompts belong in `prompts/app/`. Link them rather than conflating prompts with
execution evidence. Sanitize secrets and sensitive data before recording anything;
document redactions without preserving secret originals in Git. Keep logs small
and reviewed; generated local evaluation artifacts follow data/README.md.
