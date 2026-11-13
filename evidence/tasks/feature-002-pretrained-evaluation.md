# IBM pretrained inference verification — gate audit

Date: 2026-11-13. Branch: `model-implementations`. Starting HEAD: `92bdd79dbbfd11a2d43567296d114a51a5725dd6`.

## Outcome

**No real IBM inference was performed.** Prompt 05's loader and Prompt 07's transaction adapter are absent, their suites remain RED, and the checked-in IBM source mapping disallows import. There is no approved pretrained artifact manifest or accepted primitive graph-state representation with verified bank/account collision and training-cutoff provenance. LightGBM is absent from the current environment. The user's reported team scope approval is recorded in the [IBM candidate decision](../../specs/002-data-and-risk-scoring/proposals/pretrained-ibm-model-decision.md), but it does not resolve these technical gates. Selecting a row or inventing a vector would misrepresent eligibility.

| Requested observation | Actual result |
| --- | --- |
| Source and model | Publisher: [FraudSentinel IBM AML LightGBM](https://huggingface.co/naazimsnh02/fraudsentinel-tier1-scorers/tree/4fc397afa0e22396d26153d69e46e46304411ca0), revision `4fc397afa0e22396d26153d69e46e46304411ca0`; target `Is Laundering`. Local source mapping names Kaggle IBM HI-Small v8, SHA-256 `b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040`. Publisher mirror row-byte identity is unverified. |
| Artifact integrity | Ignored local model 9,281,152 bytes, SHA-256 `5c20d22e5e395d3b7e1f2741583f350bdac10d43afcc697ccbcd5373efcfd798`; joblib 33,080,466 bytes, `189ab48262821327abfdd38c04923608954e7869ca59801ef3c1291698236a76`; metrics 1,917 bytes, `8c821488ac8a42c7461f958a3669d95e1ef5067e82831e15bd0ed79d8b27c974`. Repeat local hashes match prior acquisition evidence. No approved real manifest exists, so a manifest-to-file check cannot pass. Joblib was not deserialized. |
| Feature compatibility | Native model header has 22 features; its three categorical names use underscores. Source Python uses spaces. Training-period graph maps use unqualified account keys. No verified collision map or exact cutoff accompanies the safe local state; no eligible vector can be produced. |
| Smoke population | **0 selected, 0 scored, 0 record-level rejections measured.** The process stopped at the prerequisite gate before opening any IBM record. This is not a claim that all source records are ineligible. |
| Predictions and resource use | No prediction values, scoring time, peak inference memory or fitted-state comparison: inference did not run. Three ignored files occupy 42,363,535 bytes. The focused baseline regression run took 0.68 seconds as reported by pytest; peak memory was not measured. |
| Performance | PR-AUC, ROC-AUC, precision, recall and F1: **not computed**. No local independent labeled population or approved pretrained evaluation protocol is established. No holdout labels were read, reset or disclosed. |
| Safety | No training, fitting, tuning, parameter mutation, remote AI calls or real model inference was invoked in this audit. This is an observed absence of those operations, not a tested property of a future adapter. |

## Training exposure and threshold

The pinned publisher [`aml_lgbm.py`](https://huggingface.co/naazimsnh02/fraudsentinel-tier1-scorers/blob/4fc397afa0e22396d26153d69e46e46304411ca0/aml_lgbm.py) sorts its IBM mirror by parsed Timestamp, uses the first 80% (4,062,676 rows) for training and the remaining 20% (1,015,669) for its reported test. Its graph state is aggregated across the whole training portion; a tail slice of that portion supports early stopping. The local source audit records 5,078,345 records, matching the publisher's total, but source byte identity and row membership have not been proven. The local untracked `evals/protocols/feature_002_v1.json` describes a 24-hour warmup and 70/15/15 scoreable view: train 2,774,357 rows (through 2022-09-08 07:21 UTC), validation 594,715 (2022-09-08 07:22 through 2022-09-09 09:31), test 594,352 (from 2022-09-09 09:32). The local file is **not a committed, approved pretrained split manifest**; these are metadata observations, not a reuse or disclosure of its test labels. Different split rules and likely shared source rows mean local validation or test results cannot be called independent. Exact overlap cannot be quantified from the available publisher records.

The publisher selects its default 80%-recall routing threshold, `1.768963856800349e-116`, from precision-recall calculations on its **test labels**. It is a test-selected routing value, not an independently validated FraudLens threshold, and no threshold was applied here. Publisher metrics are historical source claims, not project measurements.

## Commands and observed results

| Command | Exit | Result |
| --- | ---: | --- |
| `git status --short --branch; git rev-parse HEAD` | 0 | Correct branch and HEAD; earlier unrelated worktree changes preserved. |
| `.venv/Scripts/python.exe -c <mapping/runtime/module-presence probe>` | 0 | Mapping `pending_team_review`, `executable_mapping=false`, `import_allowed=false`; LightGBM, loader, adapter and converted graph absent. |
| `Get-Item` and `Get-FileHash -Algorithm SHA256` for the three ignored files | 0 | Sizes/hashes as above; `git check-ignore -v` confirmed `/data/artifacts/`. |
| `.venv/Scripts/python.exe -m pytest backend/tests/unit/test_fixture_scoring.py backend/tests/unit/test_rule_scoring.py backend/tests/unit/test_scoring_boundary.py -q -p no:cacheprovider --basetemp data/artifacts/pytest-evaluation-baseline --tb=no` | 0 | 38 passed in 0.68 s; Foundation fixture and rules boundaries remain operational. |
| `.venv/Scripts/ruff.exe check backend/tests/unit/test_fixture_scoring.py backend/tests/unit/test_rule_scoring.py backend/tests/unit/test_scoring_boundary.py` | 0 | All checks passed. |
| `git diff --check` | 0 | No whitespace errors; Git emitted LF-to-CRLF notices only. |
| Read-only JSON probe of `evals/protocols/feature_002_v1.json` | 0 | Extracted status, dataset version and partition role times/counts only; no labels read. File is untracked. |

The Prompt 05/07 failures and their exact prior commands are in [pretrained-model evidence](feature-002-pretrained-model.md#prompt-07-transaction-inference-prerequisite-audit--2026-11-13). No smoke-test command, predictions, malformed-record rejection counts, performance metrics or inference memory measurements exist. Full backend regressions were not run; focused baseline checks above passed. IBM CSVs, completed databases, previous feature artifacts and sealed holdout state were not opened or changed.

**Next:** establish a verified, safe graph representation with bank/account and cutoff provenance, approve a real manifest and runtime, complete loader and adapter GREEN, then select a small label-free eligible smoke sample. Independent performance evaluation remains separate and requires exposure proof and an approved protocol.
