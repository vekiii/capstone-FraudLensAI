# Feature 002 private team handoff — 2026-11-16

## Scope and identities

The main local scorer is `model-history-v1-boosted-candidate` at frozen threshold
`0.9936687168275105`, using trusted manifest SHA-256
`013c7ebe5ab5a5270a7b66af200060d3499c31eb2598c06a038ca887fd9320a6`.
The original immutable full run `run_boosted_full_20261114_v3` has 3,963,424
scored assessments, 1,114,921 warm-up exclusions and 166 threshold alerts.
The isolated derived policy is `boosted_utc_daily_top20_v1`; its run and exact
result are recorded in the [publication evidence](feature-002-daily-cap-publication-2026-11-16.md#completion-addendum-actual-derived-run-and-application):
`run_boosted_daily20_20261116_v1`, 3,963,424 retained assessments, 159
published alerts, seven excluded. Its activated isolated store is
`evals/results/boosted-daily20-20261116-v1.sqlite` with SHA-256
`5b7f834c877cc71aa3dbe90174b5bcd2bf7556dc4dc5a42bd48e7c9150973a70`.
Neither run changes the shared active scorer.

## Private package

Build on the contributor's machine:

```sh
PYTHONPATH=backend/src .venv/bin/python evidence/tasks/feature-002-build-private-handoff.py --output evals/results/team-handoff-20261116
```

The resulting ignored directory is
`evals/results/team-handoff-20261116/`. Its `MANIFEST.json` lists every
relative file and SHA-256. The build exited 0 and produced 15 payload files
(62 MiB); an independent rehash found zero mismatches. Recheck the manifest
after transfer because this handoff document may receive further additions.
The five operational/snapshot records hash to
`b6710f07f1d7c3336d00628270f1e3410e6771d7fee9498ad14227ddb16702be`,
and the five saved assessments to
`b127ded9795765e509ecd418734eb08f4cf18625ba53550d92500e7ac3ee664e`.
The package contains:

| Relative destination | Purpose |
|---|---|
| `boosted-artifact/` | Complete manifest, metadata, model and validation scores; copy to `artifacts/feature-002-boosted-validation-20261114/` on the peer machine. |
| `boosted-full-five-explanations.json` | Full-precision T065 sample; place under `evals/results/`. |
| `five-operational-snapshots.json` | Exactly five operational events and complete `history-v1` snapshots extracted from the read-only source database, without private labels. |
| `five-saved-assessments.json` | The five v3 saved assessments with score/explanation for exact comparison. |
| `boosted-validation.json` | Aggregate development validation report: 19 positives among 20 simulated alerts, AP `0.1721290264995173`. It is already inspected development evidence. |
| `benchmark/frozen-tree-artifact/` | Original selected tree manifest/metadata/model, separate from boosted. |
| `benchmark/test_predictions.json` | Original frozen test predictions by transaction; private transfer only. |
| `benchmark/test_report.json` | Original exploratory benchmark report. |
| `benchmark/holdout_ledger.json` | Original consumed-holdout ledger. |

The package intentionally omits the IBM CSV, complete SQLite work database,
full v3 run store and all private label files. The operational five-case JSON
is built solely from `operational_events` and `feature_snapshots`; it never
queries `private_evaluation_labels`. The package stays ignored and local for
the requester to transfer through the authorized private team channel. Verify
`MANIFEST.json` file hashes after transfer and verify the trusted model bytes
again before deserializing.

The complete source/history DB is available locally at
`data/processed/feature-002-ibm-v8-rules-work.sqlite` with full-file SHA-256
`5397b637814cbed9cf31389613207335321597c9682ec67d31abacf28ebda4d9`.
If transfer is impractical, restore it from the exact authorized IBM v8
`data/raw/HI-Small_Trans.csv` (SHA-256
`b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`):
run the [quickstart import and build-features commands](../../specs/002-data-and-risk-scoring/quickstart.md),
with the reviewed mapping, dataset version and `history-v1` feature catalog.
The expected result is 5,078,345 snapshots, 3,963,424 scoreable and
1,114,921 warm-up incomplete. The source CSV and database remain outside Git.

## Original T066 tree benchmark, checked separately

All original local inputs are present here. Tree manifest SHA-256
`2732691cb08daafba9d303ef6f3c8f616e03b3dc51505d3abb9772ceadd3919e`,
metadata `8b5a513f0346b31b4c7ff60143078567f63e041f9d86d59388b7057f00f398e2`,
model `fd2332d543941886eb7d0092d7a606b683d1d7c198e3763865ebc7b6a2df0838`.
Predictions SHA-256 `4897cb71ebeda7742cbeed27beda58db6c1d2ecfecf7825ad50801dd4d24cef4`,
report `a578d6df0b25014987e142959250a5965e8225b44fb6f6ea579d1fa1745cb7b6`,
ledger `4fd118ca62e08ca4e0d9661d0c4346171e2c6476db7bfbcf288a19b24c4a543d`.
The report's `predictions_sha256` and the ledger's `predictions_hash` both
match the saved prediction file; protocol digests match. The report marks
`prior_test_exposure=true`, so this is exploratory rather than independent.
The peer still needs these private files on her machine, the same-hash source
or independent rebuild, and her own `reproduce` command/result for T066.
Nothing is claimed missing on this contributor's machine; the teammate's
earlier Windows audit accurately records missing files *there*.

After copying `benchmark/frozen-tree-artifact/` to
`artifacts/feature-002-history-v1-20261114/` and the three benchmark JSONs
to `evals/results/phase8/`, run this separately from the boosted check:

```sh
PYTHONPATH=backend/src .venv/bin/python -m fraudlens.pipeline_cli reproduce --source-store data/processed/feature-002-ibm-v8-rules-work.sqlite --protocol evals/protocols/feature_002_v1.json --artifact-dir artifacts/feature-002-history-v1-20261114 --manifest-sha 2732691cb08daafba9d303ef6f3c8f616e03b3dc51505d3abb9772ceadd3919e --predictions evals/results/phase8/test_predictions.json --report evals/results/phase8/test_report.json --ledger evals/results/phase8/holdout_ledger.json --out-dir evals/results/phase8/reproduce-peer
```

Use a fresh output directory. The original exploratory benchmark reports
594,352 eligible test rows, 1,445 positives, model AP
`0.0307344403263558` and rules AP `0.0018670818306353214`; both have
zero hits at 20. The peer records actual numeric differences and the
`prior_test_exposure=true` limitation; these figures are not independent
acceptance evidence.

## Team verification steps

1. From a clean checkout, install locked dependencies, verify the package,
   source CSV/work DB, protocol and mapping hashes. Use the exact
   [quickstart](../../specs/002-data-and-risk-scoring/quickstart.md) commands.
2. For T065, compare all five IDs, operational facts, history windows/digests,
   full-precision saved scores and reconstructed explanations within `1e-8`.
   Record the actual reviewer and finding per case in
   [T065 evidence](feature-002-explanation-review.md).
3. For T066, run a new isolated boosted score run and daily-cap derivation with
   new IDs/stores, record manifest/source hashes, elapsed time, memory,
   score/count differences, API snapshot/list/detail results. Separately run
   the original tree `reproduce` path against the transferred benchmark bundle
   and record numeric differences and prior exposure in
   [T066 evidence](feature-002-peer-reproduction.md).
4. The team reviews the policy/contract/code and independent unseen-period
   result before any decision to change the shared active run. The acceptance
   floor remains at least five hits among at most 20 alerts in a previously
   unseen compatible 24-hour UTC interval, frozen before label access.
