# Feature 002 T002 — ignored artifact boundary

2026-11-13 Europe/Belgrade. Mechanical setup for FR-018; RED not applicable. [Session/revision/prompt/environment](feature-002-implementation.md). This file records only T002; later artifact/explanation tasks are not implemented.

Added `/data/artifacts/` to root `.gitignore` before creating `data/artifacts/` or writing the inspection result. Existing rules for raw, processed and large evaluation outputs retained.

```powershell
git check-ignore -v data/raw/HI-Small_Trans.csv data/processed/probe.sqlite data/artifacts/probe.json evals/results/probe.json
git ls-files -- data/raw data/processed data/artifacts evals/results
```

Both exit 0. Ignore output: `.gitignore:36:/data/raw/`, `:37:/data/processed/`, `:38:/data/artifacts/`, `:39:/evals/results/`. `ls-files` output empty: none tracked. Probe paths were not created. Actual report path `data/artifacts/feature-002-source-inspection.json` also checked with `git check-ignore -v` (exit 0, rule at line 38).

Shared `.agents/`, `.specify/`, lockfiles and original `data/fixtures/cases.json` preserved. No model binaries/explanations generated. Human review pending; no reviewer/approval invented.

---

# Feature 002 T037–T042 — local artifact, explanations and model scorer

2026-11-14, branch `model-implementations`. [Original prompt](../../prompts/development/002-phase-6-t037-t042-2026-11-14.md). The uncommitted T029–T036 work and notebook experiment were preserved. This phase used the existing fitted model and the unchanged [frozen protocol](../../evals/protocols/feature_002_v1.json); it did not fit a model, adjust the winner or threshold, query private labels, run T062, commit or push.

## Local trust anchor and compatibility

The ignored local directory is `artifacts/feature-002-history-v1-20261114/`. `create_manifest` checked the reviewed training metadata, protocol bytes and binary hash, then wrote an ignored `manifest.json`. The caller supplies the independently pinned manifest SHA-256 when loading. `load_trusted_artifact` resolves paths under the approved `artifacts/` root, rejects uploads, checks the manifest's exact schema, reviewed local origin, metadata hash, model hash, dataset/protocol/feature/scorer/transform/dependency versions, frozen feature order and threshold before calling `joblib.load`. The binary is loaded from the same bytes whose hash was checked, avoiding a path swap between hash and deserialization. The fitted preparation remains inside the existing pipeline; there is no refit.

| Frozen file | SHA-256 |
|---|---|
| `model.joblib` | `fd2332d543941886eb7d0092d7a606b683d1d7c198e3763865ebc7b6a2df0838` |
| `metadata.json` | `8b5a513f0346b31b4c7ff60143078567f63e041f9d86d59388b7057f00f398e2` |
| `manifest.json` | `2732691cb08daafba9d303ef6f3c8f616e03b3dc51505d3abb9772ceadd3919e` |
| `evals/protocols/feature_002_v1.json` | `01fff67d44895b5a1aa6de6dfbb6c6c107f01c041ba7c972bf42210e2b316068` |

The selected tree is candidate 5, depth 5 and minimum leaf 500. The symbolic validation threshold remains `no_alert`; calibration remains `none`. NumPy 2.5.4, scikit-learn 1.9.1 and joblib 1.6.0 match the metadata. The source SQLite and local generated artifact are Git ignored (`git check-ignore -v`, exit 0). The immutable dataset/build are complete; the frozen population remains 5,078,345 snapshots, with 2,774,357 train, 594,715 validation and 594,352 test after warm-up as documented in [T029 evidence](feature-002-protocol.md). This phase did not re-read test labels.

The trust boundary is local and procedural, not a publisher signature: an attacker able to rewrite the trusted root *and* replace the caller's pinned manifest digest can substitute executable pickle content. Only a reviewed local training artifact, pinned by digest, may enter this loader. Caller-controlled roots or digests must never be taken from HTTP uploads or request data. An invalid model raises an error; fixture and rules paths remain independent of the binary.

## RED → GREEN and commands

| Actual command/check | Exit | Result |
|---|---:|---|
| `.venv/bin/python -m pytest backend/tests/unit/test_model_artifacts.py -q -p no:cacheprovider` before loader | 1 | 2 intended failures: missing `fraudlens.model_scoring`. |
| Same command after loader | 0 | 2 passed: path traversal, symlink escape, upload, hash, absence and version rejections; rejected inputs did not call deserialization. |
| `.venv/bin/python -m pytest backend/tests/unit/test_explanations.py -q -p no:cacheprovider` before explanation module | 1 | 6 intended missing-module failures. |
| Same command after implementation, before one test correction | 1 | 5 passed; one test had a wrong expected value equal to the reconstruction. Corrected the test expectation from 0.6 to 0.5. |
| Same command after correction | 0 | 6 passed; later expanded with a fixed linear coefficient example and digest/identity checks. |
| `.venv/bin/python -m pytest backend/tests/unit/test_model_scoring.py -q -p no:cacheprovider` before adapter | 1 | 4 intended failures: missing `ModelScorer`. |
| Same command after adapter | 0 | 4 passed: fitted prediction parity, order, unseen category/no refit, repeatability, source/kind, identity, label-free request and fail-closed invalid scores. |
| `PYTHONPATH=backend/src .venv/bin/python - <<'PY' ... create_manifest(...) ... PY` | 0 | Wrote ignored manifest; returned SHA-256 `2732691c…d3919e`. An initial invocation without `PYTHONPATH` exited 1 with `ModuleNotFoundError`; no artifact was written by that invocation. |
| `.venv/bin/python -m pytest backend/tests/integration/test_model_validation_snapshot.py -q -s -p no:cacheprovider` | 0 | 1 passed in 43.12 s; SQLite URI `mode=ro`, `PRAGMA query_only=ON`; query used `feature_snapshots`, `operational_events`, dataset/build status only. |
| `.venv/bin/python -m pytest backend/tests --ignore=backend/tests/unit/test_pretrained_loader.py --ignore=backend/tests/unit/test_pretrained_ibm_inference.py -q -p no:cacheprovider --basetemp .cache/pytest-phase6-regression --tb=short` | 0 | 640 passed, two pre-existing environment/deprecation warnings, 33.64 s. |
| `.venv/bin/python -m pytest backend/tests/unit/test_pretrained_loader.py backend/tests/unit/test_pretrained_ibm_inference.py -q -p no:cacheprovider --basetemp .cache/pytest-phase6-known-red --tb=no` | 1 | Separate known incompatible-pretrained RED: 66 failed, 4 passed; no new failure class. |
| Final `.venv/bin/python -m pytest backend/tests/unit/test_model_artifacts.py backend/tests/unit/test_explanations.py backend/tests/unit/test_model_scoring.py backend/tests/unit/test_rule_scoring.py -q -p no:cacheprovider --tb=short` | 0 | 27 passed after final focused additions. |
| `.venv/bin/ruff check backend` and `git diff --check` | 0, 0 | Clean. |
| `shasum -a 256` for four files above | 0 | Hashes match table. |

The complete backend run preceded the final additions to the focused artifact/linear tests; those additions passed the final focused run and Ruff. No production publication path exists yet; that is T043 onward.

The existing fixture suite still runs without a model file (included in the 640 backend passes). A separate rules-only semantic probe, `PYTHONPATH=backend/src:backend/tests/unit .venv/bin/python - <<'PY' ... score_v2(request(fact,snapshot),RuleScorer()) ... PY`, exited 0: snapshot digest `e358ad67506a8e069283fa1e9c0aaf0c5fc59cf594fce9504aaaf676fb813d11`, ordinal score `1.00`, method `rules`. The model fingerprint for the real probe is its model/manifest SHA-256 above plus the transaction/run/snapshot digest and exact score below; replaying the same request preserves those semantic fields while `scored_at` records a new actual wall-clock time.

## Actual validation snapshot and explanation

The first frozen validation row ordered by `(event_time, transaction_id)` was `D013cdf75db1ffe315190f188d4fcb9fa`; run ID `validation_probe_phase6`; feature digest `8a7e9b920cab4df414ab442b5d5e2b33bd07cfecb9eb8f7c6aba11ec144863cc`. The newly loaded artifact predicted **0.862565385475588**, exactly the first saved reload probe prediction **0.862565385475588** (absolute difference 0, frozen probability tolerance 1e-8). The scorer reported `score_source=model` and `score_kind=uncalibrated_probability_estimate`. No target label entered the request, query, prediction or explanation.

The actual fitted tree path explained `positive_class_estimate`: root base `0.5000000000038263`, shown local contributions `+0.3708658728201987` for `current_payment_format=ACH` (optional source category), `-0.0815839180715454` for `sender_paid_count_same_currency_24h=1` (events in current paid currency), and `+0.0591968216834225` for a later split on the same observed count. The remainder from omitted path nodes is `+0.0140866090399123`. Their sum equals the returned estimate within the frozen explanation tolerance 1e-8. Repeated features represent separate actual split edges, not independent causal effects. The explanation's snapshot digest matches the scored input; outer assessment binds the same transaction, run, dataset, scorer and event time. Linear tests reconstruct log odds before sigmoid; rule tests reconstruct the exact ordinal score from fired/nonfired conditions. Missing context uses explicit `unavailable` with a reason.

T037–T042 are implemented and locally verified. T062 real holdout metrics, T065 teammate explanation review, and T043 publication remain open. Earlier notebook test-period exposure still prevents an independent confirmatory same-source performance claim.
