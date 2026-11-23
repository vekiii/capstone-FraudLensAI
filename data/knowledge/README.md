# Runtime knowledge boundary (feature 003)
Current update (2026-11-15): Milan Gavrić approved all six source texts
and documented reuse/applicability without changes. Manifest status is reviewed;
all reviewer/date fields and source hashes pass production stage validation.
T013-T022 complete: reviewed corpus published to the separate local store;
actual-source API/proxy/automated browser recheck passed. See
../../evidence/tasks/feature-003-phase-03-completion.md and the approval record
../../evidence/tasks/feature-003-corpus-review.md. The setup-only description
below records earlier delivery; its source/privacy rules remain applicable.

Only deliberately ingested, human-reviewed corpus content may be searched.
T013 supplies reviewed fraudlens-aml-knowledge-v1; T015 publishes its exact archive.
Required metadata includes provenance, source
URL/identity, included sections, publication/version date (or explicit unknown),
retrieval date, jurisdiction/historical context, reuse terms and content hash.
Do not copy official documents without actual provenance and allowed reuse.
Simulated procedures must remain clearly simulated, not real bank policy.
Foreign guidance is not Serbian law. No runtime open-web investigation.

This directory contains the reviewed manifest, source texts and retrieval config.
Loader/search/API/UI, provider projection, test-provider reports and review are
implemented. Generated
SQLite/index material belongs under ignored data/processed/, not reviewed sources.
The investigation database is data/processed/investigations.sqlite, separate
from producer storage; do not configure INVESTIGATION_STORE to the producer store.
Settings resolve paths but create/open no files or connections.

Runtime retrieval/tools/prompts must never read evals/investigation/reference,
private labels, hidden reviewer notes, training targets, held-out expectations or
prompts/development. Reviewable source/configuration stays tracked where permitted;
generated outputs stay local. Runtime receives authorized context, not arbitrary
filesystem/SQL access. No actual corpus approval is implied by this policy.

Provider delivery is backend-only and uses an explicit outbound allowlist:
only approved synthetic/authored case facts, scoped opaque IDs, safe aliases,
exact time/money/score meanings, permitted history and selected provenance-backed
procedure text. No real customers, credentials, source paths/rows, evaluation
answers, unrelated accounts or arbitrary database/file reads. Provider/tool
projection is implemented and tested; corpus preparation alone authorizes no
provider call. Original setup policy is not a live execution budget.

## Prepare a separate local archive

From repository root, with existing locked dependencies:

```powershell
$env:PYTHONPATH = Join-Path $PWD 'backend/src'
$env:INVESTIGATION_ENABLED = 'true'
$env:INVESTIGATION_PROVIDER = 'test'
$env:OPENAI_API_KEY = ''
$env:OPENAI_MODEL = ''
.venv/Scripts/python.exe -m fraudlens.investigation.cli prepare-knowledge --manifest data/knowledge/fraudlens-aml-knowledge-v1/manifest.json --store data/processed/investigations.sqlite
```

The command validates review metadata, source hashes and document-root boundaries
and archives exact normalized text; it never downloads source text. Use
--stage-only for validation without publication. Runtime source replacement
preserves old passage text/provenance under archived version identities. This
store belongs only to investigation; never point it at producer storage.

Default retrieval.json still uses the original 0.5 demo heuristic. T054 reviewed
glossary.json and implemented the separate title/glossary variant; T055 froze
development-selected baseline/improved cutoffs in
../../evals/investigation/freezes/retrieval-v1.json. Those evaluated configurations
are distinct from ordinary demo preparation. T056 measured both at Recall/MRR
0.50, below target. Do not adjust corpus/glossary/cutoff using exposed held-out
answers or overwrite frozen outputs. No accuracy claim follows from fixture
search success. The separate producer/history agreement and read-only adapter
were completed in T062–T064 on 2026-11-16; full IBM/model integration remains
unverified. These compatibility checks do not establish retrieval/report quality.
See [quickstart](../../specs/003-ai-investigation/quickstart.md),
[regression](../../evidence/tasks/feature-003-regression.md) and
[reproduction protocol](../../evidence/tasks/feature-003-reproduction.md).
