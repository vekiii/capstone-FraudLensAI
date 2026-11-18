# Execution evidence

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

For Feature 002, retain the original specification-generation prompt in
`prompts/development/002-dataset-ml-eda.md`. Record source verification, restricted
label-audit access, actual preparation/training commands, outputs, limitations and
human review as separate task evidence. Do not place raw/processed rows, model
artifacts, record-level labels, or holdout answers in this directory. Evidence for
documentation or ignore-policy setup must state that no data/model checks were run.
