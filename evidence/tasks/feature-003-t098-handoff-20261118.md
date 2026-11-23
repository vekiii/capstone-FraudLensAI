# T098 private ZIP inspection — 2026-11-18

**Package integrity PASS; required published producer stores still missing.
T098 remains OPEN. Stop for the user's choice before local producer generation.**

Branch feature03-retrieval-v4, HEAD038f728; all previous uncommitted availability
work preserved. [Original request](../../prompts/development/003-t098-handoff-zip-20261118.md).
Read current AGENTS.md/next_work.md before inspection, reused the previously read
feature003 context and speckit-implement scope, rechecked T098/accepted boundary.
Explicit selection `SPECIFY_FEATURE_DIRECTORY=specs/003-ai-investigation` and
child PowerShell check-prerequisites `-Json -RequireTasks -IncludeTasks` exit0.
Requirements checklist remains16/16 checked; extensions.yml absent, no hooks.
This is prerequisite inspection/extraction, not business implementation.

## Actual package verification and extraction

Input `team-handoff-20261116.zip`,28916871 bytes, SHA-256
`84594f4ad98794f15326d1a8f093250b2dac2cfe6dae301d62c67252194e7696`.
Archive MANIFEST.json SHA-256
`21ec67d094488c691715c9764dd3be554b43eddbd679e5fe37031c24a0fdf65d`
matches the separately published handoff identity at producer commit
`93d387e573d5c288f41ab6c38d30aa837b69987c`.
All15 declared payload SHA-256 checks PASS; member set equals manifest file set.
ZIP payload streams were fully read, including CRC verification. No duplicate
case-insensitive names, absolute/traversing/drive/backslash paths or symlinks.
MacOS metadata entries were ignored. Results:
[machine observations](feature-003-t098-handoff-20261118-results.json).

Used stdlib pathlib/hashlib/zipfile/json/shutil in the existing Python environment.
The executed verification loop was equivalent to:

```python
with zipfile.ZipFile(archive) as z:
    manifest_raw = z.read('team-handoff-20261116/MANIFEST.json')
    assert hashlib.sha256(manifest_raw).hexdigest() == published_manifest_sha256
    manifest = json.loads(manifest_raw)
    for name, expected in manifest['files_sha256'].items():
        with z.open('team-handoff-20261116/' + name) as stream:
            assert hashlib.file_digest(stream, 'sha256').hexdigest() == expected
```

Selected8 files extracted to NEW ignored `.cache/t098-zip-84594f4ad987/`:
MANIFEST.json; boosted-artifact manifest/metadata/model.joblib; the five-case
explanations, operational snapshots and saved assessments JSONs; and copied
handoff instructions. Resolved destinations were contained within the extraction
root, exclusive file creation prevented overwrite, and extracted hashes were
checked again. `git check-ignore` confirms the model path is ignored.
No model/joblib deserialization or executable code loading occurred.

Benchmark payloads and validation_scores.npy were hash-verified as byte streams
only, not extracted, semantically read, executed or supplied to any runtime
prediction/retrieval/tool input. Attached handoff instructions were copied as
data, not executed as commands. No new model metric or second-person
reproduction is claimed from hash verification.

## What is now available and what still blocks T098

Now available: the actual transferred boosted model files and five saved
producer examples. The verified archive binds dataset
`dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802`.
Existing local IBM CSV was independently hashed during the preceding GitHub
inspection and matches `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`.
No CSV records/labels were parsed. The package's five source events and scoring
feature snapshots do not provide the full seven-day investigation history or
an actual completed/active producer RunStore.

**There are zero SQLite members in the ZIP.** Still missing:

- `data/processed/feature-002-ibm-v8-rules-work.sqlite`, canonical source/history
  store documented with SHA-256
  `5397b637814cbed9cf31389613207335321597c9682ec67d31abacf28ebda4d9`.
- A published model run store, preferably the isolated activated
  `evals/results/boosted-daily20-20261116-v1.sqlite`, documented run
  `run_boosted_daily20_20261116_v1`/159 alerts and SHA-256
  `5b7f834c877cc71aa3dbe90174b5bcd2bf7556dc4dc5a42bd48e7c9150973a70`.
  The full166-candidate archive is also absent; its hash in this manifest is a
  reference, not included source bytes.
- An actual completed/active rules RunStore and its run/path/version/hash
  identities. A source database filename containing "rules-work" does not
  establish a published rules scored run.

These expected store identities come from the separately inspected producer
documentation/manifest, not freshly verified database bytes. No five-example
JSONs were converted into substitute producer stores or full-history evidence.

## Choice requested; no dependent work performed

Preferred shortest T098 path: obtain consistent ready-made dataset + model
publication + rules publication snapshots privately from the producer, then
check hashes/provenance/schema compatibility and use existing read-only adapter,
investigation API and matching worker with explicit test provider.

Alternative: use the verified CSV and transferred artifact to generate NEW
isolated producer dataset/history and rules/model publications via the documented
import/build-features/score-run/daily-cap pipeline, without training. This is
additional local preparation/inference, needs source-revision/dependency/space
planning, and produces its own run IDs/checksums. It cannot be called the
contributor's byte-identical archive. Do not run refitting/benchmark/private-label
commands from the attached instructions. Await the user's choice before this
path; the request explicitly says to stop and ask when inputs are incomplete.

No new pytest/backend/frontend/browser tests run (no application behavior changed).
Prior44PASS is historical regression, not this archive's integration acceptance.
No producer import/feature build, training, inference, activation, API/worker
execution, fixture substitution, live provider/paid evaluation, label/reference
semantic reads, credential/dependency edit, commit/push/merge or historical result
change. T094/T095/T096/T097/T099/T100 status unchanged. SC-003 report quality and
SC-006 fresh live performance remain separate unmet acceptance criteria.

Next concrete step: user chooses ready-made database transfer or new isolated
local producer preparation; T098 remains unchecked until actual execution.
