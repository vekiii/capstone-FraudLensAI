# Investigation evaluation boundary
Setup creates policy only. No held-out answers, evaluation packs, rubric/split
files, corpus documents or generated results exist here as part of this phase.

Planned roles (created only by their actual tasks):
- inputs/: reviewed synthetic/authored evaluation questions and cases; runtime
  generation can receive only explicitly selected authorized input projections.
- reference/: independently authored/reviewed expected facts, relevance judgments,
  private answers and reviewer notes, never retrieval/provider/tool/prompt inputs.
- splits.json / protocol.json: frozen development vs held-out identities, rubric,
  denominators, hashes, reviewed configuration and second-review assignments.
- ../results/feature-003/: ignored local generated predictions, metrics, reports,
  failures and review outputs; concise sanitized evidence summaries go in evidence/.

Freeze corpus, inputs, independent references, splits and rubric before tuning.
Use development data for selection; do not tune against held-out answers.
Join reference answers only offline after outputs are frozen, never in generation.
Runtime must not load private labels, hidden reviewer notes, training artifacts,
reference answers or development prompts. No unrestricted file/database access.
Only approved synthetic/authored case information may later leave the backend
through an explicit allowlist; never actual customer data or credentials.

Fixture/test-provider checks prove workflow/contract behavior, not live AI or ML
quality. Actual model access, reviewed corpus and human report evaluation remain
separate future gates. No source permission, producer review, reference review,
model capability or acceptance is inferred from this README.
