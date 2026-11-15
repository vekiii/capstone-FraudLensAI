# T066 independent reproduction handoff — pending_independent_reproduction

The author completed a numerical repeat, but no second teammate has reproduced it. Use the [quickstart](../../specs/002-data-and-risk-scoring/quickstart.md) in a separate checkout with the authorized same-hash IBM v8 CSV. Install with `UV_CACHE_DIR="$PWD/.cache/uv" uv sync --locked --group dev` and `npm ci` in `frontend/`. Verify source, mapping, protocol, manifest, metadata and model hashes listed in the [benchmark](feature-002-benchmark.md). Confirm the source `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`, DatasetVersion `dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802`, complete 5,078,345-row feature build and frozen scoreable split 2,774,357 / 594,715 / 594,352. The ignored artifact and original prediction/report/ledger files are not in checkout. Obtain the exact frozen files via an approved private team-local transfer and verify their hashes for a bit-identical `reproduce` run. Alternatively, use the quickstart's fresh train/validation fit and manifest commands for a separately identified artifact and first benchmark, then repeat that report; do not call its output the frozen author's artifact without matching verification.

Follow the quickstart's `inspect`, `import`, `build-features`, `freeze-protocol`, `score-run`, `activate-run` and `reproduce` examples. Use a fresh local output/store path; never edit the author's archived IBM database or frozen artifact. Expected selected scorer is model-history-v1, the train-fitted depth-5 tree at manifest SHA `2732691cb08daafba9d303ef6f3c8f616e03b3dc51505d3abb9772ceadd3919e`, with symbolic `no_alert` and zero published alerts. The author's frozen test comparison has 594,352 eligible rows, 1,445 positives, model AP 0.0307344403263558 and rules AP 0.0018670818306353214; both P@20 and R@20 are zero. The repeat should compare scores and metrics within 1e-8, report actual maxima, and retain the `exploratory_reuse` / prior-exposure caveat. Private labels must enter only after predictions are saved.

The teammate should record their name/date, machine and versions, lock and input hashes, exact commands/exits, elapsed time/peak memory, numeric differences and any unavailable source or incompatibility here. An absent authorized CSV means `pending_source_unavailable`; no teammate run means the current `pending_independent_reproduction`. The author's command/results are in [T062–T064 benchmark evidence](feature-002-benchmark.md) and do not close SC-009.

## Boosted full-run reproduction — pending teammate run

For the separate boosted candidate, use the [complete isolated command and activation procedure](../../specs/002-data-and-risk-scoring/quickstart.md#separate-boosted-research-candidate-local-pending-independent-acceptance) with a **new** peer run ID/store. Required local inputs are an authorized IBM v8 CSV or its independently imported complete `history-v1` work store, frozen protocol, and the ignored boosted artifact transferred through the approved private team channel. Nothing under `data/raw/`, `data/processed/`, `artifacts/` or `evals/results/` is assumed to exist in a clean checkout. Verify SHA-256 before scoring: CSV `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`; mapping `a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57`; time policy `67a408fc52e57035115186c3c9863dfeac5a72d709292e0f7baeef560086d781`; `uv.lock` `19c29c5c6d8cd4b09666b2d5cc3a9d5ff52c3b95e8ec5875e6517d19329744cc`; protocol `01fff67d44895b5a1aa6de6dfbb6c6c107f01c041ba7c972bf42210e2b316068`; boosted manifest `013c7ebe5ab5a5270a7b66af200060d3499c31eb2598c06a038ca887fd9320a6`; metadata `c59376e06350bb403bd58898ef63f1588bc866b46dbead7fee09f3787b542044`; model `fce2a4057e46e02f0974bfcfdcae983e0952d6a3b98efea714e44746f08866c8`.

Run `UV_CACHE_DIR="$PWD/.cache/uv" uv sync --locked --group dev`, verify the files with `shasum -a 256`, and confirm source dataset version `dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802`, 5,078,345 snapshots, 3,963,424 full and 1,114,921 warm-up incomplete. The exact `score-run` command, `sqlite3 -readonly` status query and isolated `activate-run` command are in quickstart; use threshold `0.9936687168275105`, one worker, and keep labels closed. Expected score-run exit 0 and SQLite row `completed|3963424|3963424|166`. The author observed approximately 47 minutes; record the peer's actual elapsed time and peak memory. Expect 166 total alerts, 100 shown by the bounded API list, and full days September 2/9 over capacity at 24/23 alerts. Compare at least the five T065 examples against the peer's output at full precision and record max score/explanation differences within the declared 1e-8 tolerance. Record API list/detail snapshot IDs and HTTP results if checking the app.

After the technical reproduction, the teammate must separately reproduce the frozen selected tree/report path described above for T066's original acceptance scope, or record exactly which authorized input is unavailable. A fresh boosted refit may have different artifact bytes and must receive its own manifest/run identity. Record reviewer name, machine/OS, Python/Node/package versions, hashes, command lines and exits, elapsed/RSS, counts/differences and any deviation here. No second teammate result or signoff has been recorded; T066 and SC-009 remain open.

## Peer reproduction attempt — BLOCKED by unavailable pinned inputs — 2026-11-15

Reviewer: Isidora Popovic, assisted by Codex. This was a resource and workflow audit only; no model was fitted, no prediction was generated, no labels were opened, and no substitute result was produced.

### Branch and worktree handling

The current branch is `model-implementations`, HEAD `8bd9ce52d6eb98abe772a5a4fbc06416cf108917` (`docs(t065): review five model explanations`). The pre-existing uncommitted changes in `next_work.md` and `evidence/tasks/project-evidence-plan-2026-11-12.md`, plus four untracked local drafts, were preserved. Fetch succeeded. `FETCH_HEAD` and `origin/model-implementations` both resolve to `2099c7e50beb28e69c2e815154ab4233cd975487`; therefore the local branch is one T065 commit ahead and no newer remote commits need integration. No merge, reset, checkout or rebase was performed.

Commands executed for branch inspection/fetch:

```text
git status --short --branch
git branch --show-current
git remote -v
git log -3 --oneline --decorate
git fetch origin model-implementations
git rev-parse HEAD FETCH_HEAD origin/model-implementations
git log --oneline --decorate HEAD..FETCH_HEAD
git diff --stat HEAD..FETCH_HEAD
```

The ordinary fetch first failed because `.git/FETCH_HEAD` was not writable in the sandbox; the requested fetch then succeeded with sandbox approval. It reported no new commit beyond the existing remote tip.

### Environment and input verification

Environment observed on this Windows machine: venv Python **3.14.10**, scikit-learn **1.9.1**, NumPy **2.5.4**, joblib **1.6.0**, FastAPI **0.162.4**, Pydantic **2.14.3**, pytest **9.2.0**, uv **0.13.8**, Node **v24.21.0**, npm **11.19.0**. System `python --version` reports Python 3.13.3; the project venv is separate. pandas and pyarrow are not installed in the venv. `sqlite3` CLI was not found. Invoking `npm --version` through the PowerShell shim was blocked by execution policy; `npm.cmd --version` succeeded. The expected author environment is Python 3.14.7, scikit-learn 1.9.1 and NumPy 2.5.4, so Python patch-version parity is absent.

Commands executed for environment checks:

```text
uv --version
python --version
node --version
npm --version
npm.cmd --version
.venv/Scripts/python.exe --version
.venv/Scripts/python.exe -c "import sys,sklearn; print('exe',sys.executable); print('sklearn',sklearn.__version__)"
.venv/Scripts/python.exe -c "import importlib.metadata as m; names=['scikit-learn','numpy','joblib','pandas','fastapi','pydantic','pyarrow','pytest']; [print(n, (m.version(n) if any(d.metadata['Name'].lower()==n.lower() for d in m.distributions()) else 'NOT INSTALLED')) for n in names]"
```

The first combined package import including pandas exited with `ModuleNotFoundError: No module named 'pandas'`. No package installation or environment synchronization was attempted because the pinned database/model inputs are missing and installation would not unblock an exact reproduction.

| Required input | Expected identity from handoff | Local observation |
|---|---|---|
| IBM v8 CSV | SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040` | Present at `data/raw/HI-Small_Trans.csv`; SHA-256 matches. |
| IBM mapping | SHA-256 `a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57` | Present at `data/mappings/ibm_hi_small_v1.json`; SHA-256 matches. |
| Dependency lock | SHA-256 `19c29c5c6d8cd4b09666b2d5cc3a9d5ff52c3b95e8ec5875e6517d19329744cc` | Present; SHA-256 matches. |
| Frozen protocol | SHA-256 `01fff67d44895b5a1aa6de6dfbb6c6c107f01c041ba7c972bf42210e2b316068` | `evals/protocols/feature_002_v1.json` is present but hashes to `e8073b9c664f241418566eb87b4a3797e9798aeb2d306d035bbd2c8676e38074`; pinned protocol identity does not match. No local protocol was substituted. |
| Time policy | SHA-256 `67a408fc52e57035115186c3c9863dfeac5a72d709292e0f7baeef560086d781` | The handoff documents this hash, but no corresponding local input file was found. |
| Imported history-v1 source database | DatasetVersion `dv_8ef39d505d3515131a969fade4b14ef0b11fc3318f9995c27d966e7a91e32802`; 5,078,345 snapshots | Required `data/processed/feature-002-ibm-v8-rules-work.sqlite` is absent. The alternate history-work SQLite is also absent. |
| Boosted candidate | Manifest SHA `013c7ebe5ab5a5270a7b66af200060d3499c31eb2598c06a038ca887fd9320a6`; metadata SHA `c59376e06350bb403bd58898ef63f1588bc866b46dbead7fee09f3787b542044`; model SHA `fce2a4057e46e02f0974bfcfdcae983e0952d6a3b98efea714e44746f08866c8` | `artifacts/feature-002-boosted-validation-20261114/` and its manifest, metadata and model are absent. |
| Original full-run explanation sample | SHA `7d50bec8aba0b4e36c58a1a696de27ae4869fe650ba653618f04f35a9227a54f` | `evals/results/boosted-full-five-explanations.json` is absent. |
| Original prediction/report outputs | Referenced by the benchmark and quickstart | `evals/results/boosted-validation.json`, `evals/results/phase8/test_predictions.json` and associated ignored report/ledger outputs are absent. |

Input commands executed:

```text
Get-FileHash -Algorithm SHA256 -LiteralPath uv.lock,data/mappings/ibm_hi_small_v1.json,evals/protocols/feature_002_v1.json
Get-FileHash -Algorithm SHA256 -LiteralPath data/raw/HI-Small_Trans.csv,data/mappings/ibm_hi_small_v1.json,evals/protocols/feature_002_v1.json
Test-Path -LiteralPath <each required database, artifact, prediction, and sample path listed above>
rg --files data evals artifacts
git ls-files '*time*policy*' '*protocol*'
```

### Procedure outcome and comparison

No reproduction command was run. In particular, the documented `score-run`, read-only SQLite status query, isolated `activate-run`, frozen tree `reproduce` and any label/report comparison were **not** attempted: the source SQLite and pinned boosted model are absent, and the protocol on disk does not match the handoff hash. The exact commands to run once the approved resources are supplied remain those in the [quickstart boosted full-run procedure](../../specs/002-data-and-risk-scoring/quickstart.md#separate-boosted-research-candidate-local-pending-independent-acceptance). Expected boosted result remains `completed|3963424|3963424|166`, 166 total alerts, with 100 displayed by the bounded list API; the contributor recorded 24 and 23 alerts on two complete UTC days. Original frozen-tree comparison expectation remains 594,352 eligible rows, 1,445 positives, AP 0.0307344403263558 for the model and 0.0018670818306353214 for rules, with P@20 and R@20 both zero. Actual reproduced metrics, elapsed time, peak memory, score/explanation deltas and acceptability comparison are **not available**. There is no basis to call reproduction successful or to assess metric differences.

**T066 status: BLOCKED.** The CSV, mapping and lockfile hashes match, but missing source DB/artifacts and the protocol hash mismatch prevent exact execution; missing pandas and SQLite CLI are additional environment gaps. No output or metric was fabricated.

### Request to Elena

> Hi Elena, I’m ready to continue T066 on `model-implementations`. The pinned CSV and mapping are present and match their hashes, but I’m missing `data/processed/feature-002-ibm-v8-rules-work.sqlite`, the exact boosted artifact directory (manifest `013c7ebe…`, metadata `c59376e…`, model `fce2a4…`), the full-run five-explanation JSON, and the frozen prediction/report files. My checked-in `feature_002_v1.json` hashes to `e8073b9c…`, while T066 requires `01fff67d…`. Could you provide access to the approved same-hash database, artifact, protocol and required ignored outputs through the team-local transfer, or point me to their authorized location? Please also confirm the exact time-policy file and whether the original frozen tree artifact/report bundle is available for the original T066 reproduction scope. I have not regenerated or substituted any of these inputs.

Once the exact inputs are available, verify all hashes and versions first, use a new peer run ID/store, keep labels closed during scoring, run the documented reproduction and record exact outputs here. Do not mark T066 complete based on the resource audit above.

The requester subsequently reported mutual agreement with Elena to provide access for T065/T066 and related Feature 002 verification. See the [access approval record](feature-002-access-approval.md). This is user-reported agreement; no separate direct confirmation from Elena is recorded in the repository, and the database/artifacts/protocol inputs remain missing or mismatched. **T066 remains BLOCKED** until the authorized resources are received, their pinned identities are verified, and the reproduction is completed. This approval concerns evidence access only; it does not authorize merge, deployment, or release.
