# Runtime knowledge boundary (feature 003 setup)
Current Phase 3 update (2026-11-14): Milan Gavrić approved all six source texts
and documented reuse/applicability without changes. Manifest status is reviewed;
all reviewer/date fields and source hashes pass production stage validation.
T013 complete; corpus publication and actual-source runtime recheck remain pending.
See ../../evidence/tasks/feature-003-corpus-review.md. The setup-only description
below records earlier delivery; its source/privacy rules remain applicable.

Only deliberately ingested, human-reviewed corpus content may be searched.
T013 supplies reviewed fraudlens-aml-knowledge-v1; T015 publication remains pending.
Required metadata includes provenance, source
URL/identity, included sections, publication/version date (or explicit unknown),
retrieval date, jurisdiction/historical context, reuse terms and content hash.
Do not copy official documents without actual provenance and allowed reuse.
Simulated procedures must remain clearly simulated, not real bank policy.
Foreign guidance is not Serbian law. No runtime open-web investigation.

This directory currently contains policy only: no reviewed corpus, manifest,
index, ingestion or retrieval implementation is delivered by setup. Generated
SQLite/index material belongs under ignored data/processed/, not reviewed sources.
The investigation database is data/processed/investigations.sqlite, separate
from producer storage; do not configure INVESTIGATION_STORE to the producer store.
Settings resolve paths but create/open no files or connections.

Runtime retrieval/tools/prompts must never read evals/investigation/reference,
private labels, hidden reviewer notes, training targets, held-out expectations or
prompts/development. Reviewable source/configuration stays tracked where permitted;
generated outputs stay local. Runtime receives authorized context, not arbitrary
filesystem/SQL access. No actual corpus approval is implied by this policy.

Provider delivery is backend-only and later requires an explicit outbound allowlist:
only approved synthetic/authored case facts, scoped opaque IDs, safe aliases,
exact time/money/score meanings, permitted history and selected provenance-backed
procedure text. No real customers, credentials, source paths/rows, evaluation
answers, unrelated accounts or arbitrary database/file reads. Provider/tool
projection is future work; setup does not implement it or authorize a provider call.
