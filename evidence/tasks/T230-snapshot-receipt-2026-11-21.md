# T230 supplied snapshot receipt — blocked before label access (2026-11-21)

The [one-time authorization](T230-authorization-2026-11-21.md) was recorded **before** any test-label access. The user's requested evaluation was **not run**. No test/showcase label value was parsed, no aggregate test metric or report was produced, and T230 remains open. The two supplied files were treated as data, not as instructions.

## Archive and isolated byte verification

Supplied local paths were `/Users/ladylazarus/Downloads/T230-test-evaluation-snapshot.zip` and the matching `.zip.sha256` file. `shasum -a 256` measured ZIP SHA-256 `c76ab04410a24a150a9e525b23a4f14e980f73394afcc7c2e54ef471705b3ee3`, matching both the user value and sidecar. The sidecar uses CRLF: direct `shasum -a 256 -c` on macOS attempted a filename ending in `\r` and failed open; `tr -d '\r' < ...zip.sha256 | (cd /Users/ladylazarus/Downloads && shasum -a 256 -c)` returned `T230-test-evaluation-snapshot.zip: OK`. The sidecar itself was not changed.

`zipfile` inspection found exactly two regular files under one safe top-level folder, no absolute path, traversal, link, duplicate, extra entry or bad CRC:

| ZIP member | Uncompressed bytes | Independently measured SHA-256 after extraction into a separate temporary directory |
|---|---:|---|
| `t210-hi-small-b19d39f5/accepted.jsonl` | 3,015,200,326 | `8a8315288f24a387d1bd0ec3765ac9e64a6b5ce131a634952aee1b302bd9f9ba` |
| `t210-hi-small-b19d39f5/manifest.json` | 34,819 | `38e1cdee0e96f73abfc398ff2207c8b8fc1ed0c526a6872e56a1462e55edbb88` |

The isolated verification streamed decompressed bytes into a new `/private/tmp/t230-snapshot-verify-*` directory, checked both sizes and hashes, parsed **only the manifest**, then removed the temporary extraction. No transaction row or label was printed or interpreted. The manifest says `complete=true`, 5,078,345 source/accepted rows and zero rejected rows. Its `processed_files` list **requires** `rejections.jsonl`, size 0, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

## Blocking contract mismatch

The archive does **not** contain `COMPLETE` or `rejections.jsonl`. The current `verify_completed_snapshot()` in `backend/src/fraudlens/data/manifest.py` requires a `COMPLETE` marker equal to the hash of the exact manifest bytes and verifies the existence, size and hash of **every** listed processed file. `evidence/tasks/T230-evaluate.py` calls it before opening the accepted row stream. Thus the archive's two verified bytes alone cannot pass the evaluator's existing snapshot gate. The user explicitly directed us not to invent missing content, alter the manifest or bypass integrity checks. No `COMPLETE` marker or empty file was reconstructed; the existing evaluator was not changed.

The desired final `data/processed/t210-hi-small-b19d39f5/` path was absent and remains absent. An incomplete snapshot was **not** published there. `.gitignore:38` excludes `/data/processed/`, and `git ls-files --stage`/`git status --short` showed no staged snapshot files. The original ZIP remains in Downloads, outside the Git checkout; the transient extraction was removed.

## Independent frozen-input checks, still without labels

Current bytes matched every expected identity: diagnostic canonical protocol `22a4e6c8efe744de7d4d9b5304a8252f144ffa532037d7f0d8a5a83c66951b5b`, cross-family canonical protocol `7fd4e7349b2ef4921166d008f5c3b7e147c21a6554eae5160f33948d323bac32`, model `3b4e4019312d60610dd0094c6697897a061611a60e7777ed7be35e133af9451c`, trusted manifest `c766e90159a70eff2d1f29d5ff425029af20ff123f1fad08e45f9fc416076d45`, lineage `9f1679c767aeab290467bddac764a8658664864751ae3f7e5aaa9a46eea14b25`, prediction CSV `99727d426f78698ee9a0f37ec50c1c900dc848f13bed6ef0756544f76c3f04f7`, experiment `a943836322fb2815d5cad85b291719333e21d22c1dcdb5fcbdbb18fbda1316ac`, feature manifest `63873b79a1ff875c5702a62c40c7a9cb3faef6bb7e0bb658739abac35274c05f`, test feature file `693320617cd8ff05c3ba177fcf9e3447bd2f7b92c5b29736fce304d60023c9e0`, `uv.lock` `b9b1c52056c3706fd21fc1fefa9934fc1c1c8c09dd2b0f465d8d49ad25cc1ffe`, and unchanged evaluator `bd008c6f28b9c2fbd02b4cbcf5f1b04bceb65be45b5e45afafc030ee0472aeff`. The experiment and manifest links matched; fixed threshold remained `0.2489517623052024`; freeze status was `complete`.

The current runtime was Python 3.14.10, LightGBM 4.7.0, NumPy 2.5.5 and scikit-learn 1.9.1. A fresh label-free CSV/test-feature scan found 233,070 unique IDs in exact feature-file order, UTC timestamps from `2022-09-06T00:00:00+00:00` to `2022-09-06T11:12:00+00:00`, finite scores from `9.305900253928908e-13` to `0.9999974605522108`, and frozen ID digest `b9d9231b67969c96585dcb9ea8ce46ee9079501c02b1f18fd473c2e61a4d487f`. These are prediction/input integrity findings, **not test performance**.

No T230 output file existed or was created. No new fit, prediction regeneration, evaluator execution, test/showcase label access, model activation, commit or push occurred. The existing weighted freeze and all prior outputs were left untouched.

**Next step:** obtain a byte-preserving archive from the original verified T210 snapshot that additionally contains its original `COMPLETE` marker and zero-byte `rejections.jsonl`. Verify every member and the complete snapshot before publishing it to the ignored target path; only then recheck the frozen inputs immediately before the separately authorized one-time T230 evaluation. This receipt does not claim that evaluation has happened.
