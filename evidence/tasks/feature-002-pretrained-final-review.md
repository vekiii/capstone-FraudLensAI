# Feature 002 IBM pretrained model: final Phase 5 review

Review date: 2026-11-13. Branch: `model-implementations`. Starting HEAD `429d6ec8c9b15a4a2e5cc223aa0005ab42a97c2d`; verified regression-fix commit `07cce92cc5924cb6c3bd66888c14b165f618e3af`. This is a repository and local-artifact review, **not** acceptance of a working pretrained scorer or independent performance benchmark. Phase 6 and Phase 7 were not started.

## History, authority and task state

`git log --all --graph --decorate --oneline` was inspected. The branch descends from Feature 002 `27ac7d49e3d638717c752dce225216d291bf9e87`, not from the separate `main` tip. At the fix commit, its local history has 46 commits, including 13 since that baseline: `fe310c1` protocol RED, `a2857cd` protocol GREEN, `d606fb7` resource pilot, `b8643a4` branch preparation, `87b6980` artifact review, `13472f9` gated architecture, `c872375` IBM candidate review, `81b3b9a` inference RED, `79987df` loader RED, `f426cec` extended inference RED, `92bdd79` inference gate, `429d6ec` evaluation gate, and `07cce92` mapping checkout fix. No commit implements a pretrained loader, inference adapter or production model scorer. Pre-existing uncommitted evidence/handoff edits, an untracked `evals/` protocol and two protocol helper scripts remain untouched.

The user conveyed collective team approval of the **pretrained direction**; [the decision record](../../specs/002-data-and-risk-scoring/proposals/pretrained-ibm-model-decision.md) records it without invented reviewer names. The IBM source mapping file still reports `pending_team_review`, `executable_mapping=false` and `import_allowed=false`. There is no recorded human sign-off on exact bank/account semantics, graph cutoff, safe primitive conversion, runtime, real manifest or independent evaluation design. The original [Feature 002 tasks](../../specs/002-data-and-risk-scoring/tasks.md) remain authoritative: T026–T028 are checked; T029–T036 are open. The separate [pretrained checklist](../../specs/002-data-and-risk-scoring/checklists/pretrained-ibm-loader.md) has native-byte verification checked but graph-state, loader, adapter and real inference items open. No original training task was marked complete on the strength of pretrained tests.

## Source, bytes and data preservation

The selected source is [FraudSentinel Tier-1 Scorers at immutable revision `4fc397afa0e22396d26153d69e46e46304411ca0`](https://huggingface.co/naazimsnh02/fraudsentinel-tier1-scorers/tree/4fc397afa0e22396d26153d69e46e46304411ca0). Its [pinned model card](https://huggingface.co/naazimsnh02/fraudsentinel-tier1-scorers/blob/4fc397afa0e22396d26153d69e46e46304411ca0/README.md) and [`aml_lgbm.py`](https://huggingface.co/naazimsnh02/fraudsentinel-tier1-scorers/blob/4fc397afa0e22396d26153d69e46e46304411ca0/aml_lgbm.py) identify the AML LightGBM target as IBM `Is Laundering`, separate from its Sparkov card-fraud model and IEEE-CIS `isFraud`. The card declares `apache-2.0` / Apache-2.0 and says source datasets retain separate licenses. No standalone LICENSE file was established in the earlier repository-tree review; the applicable data-derived-state terms still need review before redistribution.

| Ignored local file | Bytes | Locally rechecked SHA-256 |
| --- | ---: | --- |
| `data/artifacts/aml_lgbm_model.txt` | 9,281,152 | `5c20d22e5e395d3b7e1f2741583f350bdac10d43afcc697ccbcd5373efcfd798` |
| `data/artifacts/aml_lgbm_preproc.joblib` | 33,080,466 | `189ab48262821327abfdd38c04923608954e7869ca59801ef3c1291698236a76` |
| `data/artifacts/aml_lgbm_metrics.json` | 1,917 | `8c821488ac8a42c7461f958a3669d95e1ef5067e82831e15bd0ed79d8b27c974` |

The joblib digest agrees with the publisher's listed value; the model and metrics digests above are independent local measurements, not verified publisher SHA-256 attestations. All three match the prior local acquisition evidence, supporting unchanged **local bytes** since that measurement. No training, fitting, reserialization or parameter mutation was performed in this review. A real approved model manifest does not exist, so manifest-to-file verification cannot pass.

`data/raw/HI-Small_Trans.csv` remains 475,664,283 bytes with SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`, matching the recorded source value. The mapping's canonical Git blob SHA-256 is `a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57`. A Windows CRLF checkout initially produced `9a87e1ddaad2c6825d76111eae4fdcf54e2bec5ed0c7c25685b1ea8a0dd42ae1`, causing six integration failures. Its normalized content equaled the Git blob. Separate fix `07cce92` adds only `.gitattributes` to force LF for that file and restores the worktree to the **existing recorded Git bytes**, without changing its Git content, mapping rules or import status. All 600 non-pretrained-RED backend tests then passed.

## Feature, preprocessing and serving boundary

The native LightGBM text header declares `version=v4`, `max_feature_idx=21` and `objective=binary sigmoid:1`. Exact native order:

`hour, dow, log_paid, log_recv, amt_diff, ccy_mismatch, self_loop, is_round, same_bank, snd_out_deg, snd_in_deg, snd_out_cnt, snd_in_cnt, snd_out_amt_mean, rcv_out_deg, rcv_in_deg, rcv_in_cnt, gather_scatter, amt_to_snd_mean, Receiving_Currency, Payment_Currency, Payment_Format`.

The pinned source Python calls the last three `Receiving Currency`, `Payment Currency`, `Payment Format`; the native header replaces their spaces with underscores. The native `pandas_categorical` footer records ordered vocabularies of 15 receiving currencies, 15 payment currencies and 7 payment formats. The RED inference fixture captures this distinction, but no production transformation has been verified. The IBM raw mapping identifies the two `Account` occurrences by position, keeps paid/received money and currencies separate, and reserves `Is Laundering` for private evaluation. Its import gate remains closed, so a real score request cannot be built through an approved mapping.

The publisher's [source](https://huggingface.co/naazimsnh02/fraudsentinel-tier1-scorers/blob/4fc397afa0e22396d26153d69e46e46304411ca0/aml_lgbm.py) builds graph counts/degrees/means over its whole initial 80% training period with **unqualified** account strings. FraudLens uses bank-qualified identity and strict point-in-time `history-v1` snapshots. The joblib saves `graph`, `features` and `cat_cols`, but no verified bank/account collision index or exact training cutoff. Thus source-compatible graph state and no-future-information eligibility have **not** been proven. Re-keying the graph or replacing missing values with arbitrary zeroes would change model semantics. An earlier read-only `pickletools.genops` scan, repeated here, found 6,560,865 primitive/container/memo opcodes and zero executable reconstruction opcodes. This does not prove pickle deserialization safe; neither `joblib.load` nor `pickle.load` was invoked, and no sanitized primitive graph artifact exists.

There is no `fraudlens.pretrained` loader, `fraudlens.pretrained_inference` adapter, approved real manifest or installed LightGBM runtime. The RED suites specify controlled unavailable/incompatible, identity, label-exclusion, no-training, finite-score and uncalibrated-score behavior, but those assertions have **not run through production code**. Consequently safe stale/missing-artifact errors, exact vector identity, bank-qualified lookups, label isolation and prediction provenance remain unverified for real inference. No output is currently represented by the application as a calibrated laundering probability; there is no model output at all.

## Evaluation and human review limits

The publisher reports 4,062,676 training and 1,015,669 test rows from an IBM HI-Small mirror, totaling 5,078,345, the same count as the local audited source. Its training graph may expose later facts to earlier training rows. Its 80%-recall routing threshold `1.768963856800349e-116` was selected using **publisher test labels**; neither that operating point nor the card's ROC-AUC/PR-AUC is an independent FraudLens result. The untracked local protocol describes a different 70/15/15 `history-v1` population after warmup. Publisher mirror byte/row identity and exact training exposure are unknown, so local validation/test independence cannot be asserted. No local holdout labels were read or reset; no local PR-AUC, ROC-AUC, precision, recall or F1 was computed.

Real inference smoke status: **zero IBM records selected, zero scored, zero record-level rejections measured; no prediction values**. No independent performance evaluation exists. Reported team approval of direction is recorded; named technical or human acceptance of the actual artifact/input/evaluation boundary is not. No Phase 6 artifact publication, Phase 7 API migration, frontend change, push or merge was done.

## Checks and Git hygiene

| Command/check | Exit | Observed |
| --- | ---: | --- |
| `git log --all --graph --decorate --oneline`, `git merge-base`, `git rev-list --count` | 0 | Full local graph inspected; Feature 002 base `27ac7d4`, 46 branch commits at `07cce92`, 13 branch-only commits. |
| `Get-FileHash -Algorithm SHA256` on raw CSV, three model files and mapping bytes | 0 | Hashes and sizes above; original CSV and canonical mapping content match their recorded values. |
| `git diff --exit-code -- data/mappings/ibm_hi_small_v1.json`; `git ls-files --eol` | 0 | No mapping content diff; index/worktree both LF after fix. |
| Static `pickletools.genops` scan of joblib | 0 | 6,560,865 opcodes; zero executable reconstruction opcodes; no deserialization. |
| `.venv/Scripts/python.exe -m pytest backend/tests --ignore=backend/tests/unit/test_pretrained_loader.py --ignore=backend/tests/unit/test_pretrained_ibm_inference.py -q -p no:cacheprovider --basetemp data/artifacts/pytest-final-review-regressions --tb=no` | 1 | Before LF fix: 594 passed, 6 data-store integration failures due mapping worktree digest mismatch. |
| Same command with `--basetemp data/artifacts/pytest-final-review-after-lf` | 0 | **600 passed**, 1 warning, 13.82 s after fix. |
| Prompt 05 loader suite, `-q -p no:cacheprovider --basetemp data/artifacts/pytest-final-review-loader --tb=no` | 1 | 30 intentional missing-loader failures, 3 passes. |
| Prompt 06 inference suite, `-q -p no:cacheprovider --basetemp data/artifacts/pytest-final-review-inference --tb=no` | 1 | 32 intentional missing-adapter failures, 1 pass. |
| `.venv/Scripts/ruff.exe check backend/src backend/tests`; `git diff --check` | 0 each | Ruff passed; no whitespace errors (Git line-ending notices only). |
| `git ls-files` path/type scan and tracked-content secret-marker scan | 0 | 241 tracked paths after fix; no tracked raw/artifact/processed dataset, model binary, database or candidate secret path; no private-key block or simple long literal credential assignment found. This limited scan is not a comprehensive secret audit. |
| `git check-ignore -v` | 0 | Raw CSV and model/joblib are excluded by `/data/raw/` and `/data/artifacts/`. |

**Disposition:** Phase 5 pretrained implementation is incomplete. Keep original T029–T036 open and no real model score or independent metric claim. One concrete next action: establish a faithful safe primitive graph representation with verified bank/account and training-cutoff provenance, a reviewed source mapping and real artifact manifest/runtime, then make Prompt 05 loader tests GREEN before implementing Prompt 07 inference.
