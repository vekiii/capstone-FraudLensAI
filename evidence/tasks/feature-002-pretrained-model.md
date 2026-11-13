# Feature 002 pretrained artifact investigation

## IBM AML LightGBM candidate correction — 2026-11-13

**Status:** Primary candidate for review, not an approved production model. This corrects the earlier ApexFi IEEE-only direction while retaining IBM HI-Small as the project dataset. See the [pending source decision](../../specs/002-data-and-risk-scoring/proposals/pretrained-ibm-model-decision.md). The historical ApexFi investigation below remains accurate for that earlier candidate.

### Local state and Prompt 04

Branch `model-implementations`, starting HEAD `13472f9058079687cf4ae4ce159db9286fdcb039`. Recent commits: `13472f9` architecture proposal, `87b6980` ApexFi review, `b8643a4` pretrained branch proposal, `d606fb7` resource pilot, `a2857cd` temporal protocol, `fe310c1` protocol RED tests. Starting worktree had uncommitted `next_work.md`, this evidence, and `project-evidence-plan-2026-11-12.md`, plus untracked `evals/` and two protocol scripts. Those were not discarded. `backend/tests/unit/test_pretrained_loader.py` is absent; no Prompt 04 loader RED implementation/tests or RED execution exists despite the prompt's characterization. The generic desired assertions remain valuable but are not yet test code. No training-task checkbox was changed.

### Pinned upstream files and provenance

`git ls-remote https://huggingface.co/naazimsnh02/fraudsentinel-tier1-scorers HEAD` exited 0 and returned immutable revision `4fc397afa0e22396d26153d69e46e46304411ca0`. The upstream [file tree](https://huggingface.co/naazimsnh02/fraudsentinel-tier1-scorers/tree/main) at that observed revision lists all **five** requested files (the request calls them four):

| File | Observed availability and role |
| --- | --- |
| [`aml_lgbm_model.txt`](https://huggingface.co/naazimsnh02/fraudsentinel-tier1-scorers/blob/main/aml_lgbm_model.txt) | Listed as a downloadable 9.28 MB native LightGBM text model. Actual model bytes, SHA-256, native header/version and exact encoded feature order were **not** independently verified in this documentation review. |
| [`aml_lgbm_preproc.joblib`](https://huggingface.co/naazimsnh02/fraudsentinel-tier1-scorers/blob/main/aml_lgbm_preproc.joblib) | Listed as a downloadable 33.1 MB Xet object. Publisher page gives Xet hash `2aa91910bec32027f1b10c4de091df544e13b28295d5869c12182ca657d191e0` and SHA-256 `189ab48262821327abfdd38c04923608954e7869ca59801ef3c1291698236a76`; neither was independently recalculated. Upstream code writes `graph`, `features` and `cat_cols` into it. Never deserialize merely to inspect. |
| [`aml_lgbm_metrics.json`](https://huggingface.co/naazimsnh02/fraudsentinel-tier1-scorers/blob/main/aml_lgbm_metrics.json) | Readable 1.92 kB metadata: `domain=aml`, `n_features=22`, 4,062,676 train / 1,015,669 test rows, best iteration 671, PR-AUC 0.02295 and ROC-AUC 0.82191 as **author reports**, not FraudLens results. |
| [`aml_lgbm.py`](https://huggingface.co/naazimsnh02/fraudsentinel-tier1-scorers/blob/main/aml_lgbm.py) | Readable 7.32 kB training and feature-construction reference, statically inspected and never executed. |
| [`infer.py`](https://huggingface.co/naazimsnh02/fraudsentinel-tier1-scorers/blob/main/infer.py) | Readable 5.31 kB reference. Its AMLScorer calls `joblib.load` and reproduces feature construction with account-key lookups and zero defaults; it was not executed or adopted. |

The [model card](https://huggingface.co/naazimsnh02/fraudsentinel-tier1-scorers) declares Apache-2.0 and associates the AML LightGBM with IBM HI-Small, not IEEE-CIS. The source `load_dataset("eexzzm/IBM-Transactions-for-Anti-Money-Laundering-HI-Small-Trans")` trains with `Is Laundering` labels. The tree displayed no standalone LICENSE file; actual reuse/attribution and the source dataset's separate terms need review. FraudLens's local Kaggle IBM release is documented as CDLA-Sharing-1.0, but the author's Hugging Face mirror is not byte-verified against it. Local `pyproject.toml` requires Python `>=3.14,<3.15` and does not declare LightGBM or pandas; no compatible locked runtime was verified or installed. The historical model-card metrics and threshold are not independent FraudLens validation.

### Exact source feature recipe and mismatch

Upstream `FEATURES` has **22 ordered slots**: `hour`, `dow`, `log_paid`, `log_recv`, `amt_diff`, `ccy_mismatch`, `self_loop`, `is_round`, `same_bank`, `snd_out_deg`, `snd_in_deg`, `snd_out_cnt`, `snd_in_cnt`, `snd_out_amt_mean`, `rcv_out_deg`, `rcv_in_deg`, `rcv_in_cnt`, `gather_scatter`, `amt_to_snd_mean`, `Receiving Currency`, `Payment Currency`, `Payment Format`. The final three are pandas categorical columns. The source-level order is verified from `aml_lgbm.py`; saved native booster header and category-code agreement with the joblib remain unverified.

| Input group | IBM source / FraudLens comparison |
| --- | --- |
| Time and amounts | IBM `Timestamp`, `Amount Paid`, `Amount Received`, currencies and payment format supply the raw facts for hour/day, log amounts, absolute difference, currency mismatch and round amount. FraudLens retains exact Decimal and an explicit time-basis policy; upstream converts to floats, parses naive timestamp text, and silently substitutes hour/day 0 for malformed time. Those conversions/defaults need review, not automatic reuse. |
| Bank and self-transfer | `same_bank` compares `From Bank`/`To Bank`; `self_loop` compares unqualified `Account` and `Account.1`. FraudLens identifies an account by bank **and** account string. Equal raw account strings at different banks would be a false self-loop under upstream semantics. |
| Graph state | `build_graph_feats(tr)` groups unqualified sender/receiver account strings over the **entire first 80%** chronological train partition to compute distinct counterparties, in/out counts, paid mean and sum. It saves tables in joblib; the sum table is saved but not one of the 22 features. `featurize` obtains sender/receiver degrees/counts/mean, `gather_scatter`, and amount-to-sender-mean. Unknown keys become zero. FraudLens `history-v1` instead uses bank-qualified identities, strict earlier events, a 24-hour window, explicit warmup/coverage and different units. It cannot be substituted for these learned inputs. |

The upstream graph dictionary is built on the full train partition **before** its last 10% is used as early-stopping validation. Thus its per-row aggregates can include future transactions even within training and validation. Its test features use training-period tables, not evolving point-in-time history. This is not the approved `history-v1` policy even though the author calls the graph step train-only. The source comment mentions suspicious-history priors, but the returned graph dictionary contains no label-derived prior; do not infer extra features from that comment. A faithful adapter would require preserved training-period graph state and categorical mappings; recomputing it from the current IBM dataset could change the learned feature semantics or expose held-out rows. Neither joblib loading nor a safe primitive-state extraction has been approved.

### Evaluation and security limits

Upstream uses an 80/20 chronological row split and a tail slice of the 80% for early stopping. It computes `precision_recall_curve(yte, p)` and chooses routing thresholds for target recall **from test labels**, then reports test precision/recall and makes 80%-recall the default. The `1.768963856800349e-116` published threshold is therefore selected on test outcomes, cannot be called independently validated, and must not be carried into FraudLens's frozen validation-only threshold policy. The extreme value also does not establish empirical calibration.

Our audited IBM file has **5,078,345** records, exactly the author's 4,062,676 + 1,015,669 total, and the author references an IBM HI-Small mirror. This strongly suggests shared source rows; exact file bytes, row identity and training exposure have **not** been proven. A FraudLens test on the same dataset cannot be advertised as independent unseen-model evaluation without an exposure audit. Do not inspect local holdout labels or reuse the author's test threshold to select a scorer.

`joblib.load` may execute arbitrary Python object reconstruction. The publisher SHA-256 only establishes file identity if checked; it does not make execution safe. No joblib, model parser, third-party script, training, inference, dataset download or full IBM scan was run here. Kluey's [IBM XGBoost repository](https://github.com/Kluey/AML-Transaction-Detection) remains a separate alternative; its README describes rolling history and a validation-selected threshold, but its actual bundle bytes, schema and preprocessing compatibility have not been audited for FraudLens, so no second switch is authorized.

**Approval state:** the user's candidate-switch instruction authorizes this review, not a scope exception. Original T026–T028 remain complete, T029–T036 open. The [decision proposal](../../specs/002-data-and-risk-scoring/proposals/pretrained-ibm-model-decision.md) requires the team's actual decision on feature/identity/history semantics, safe preprocessing, license, evaluation claims and replacement tasks before production implementation.

**Next action — Prompt 04C:** finish artifact/state/provenance and row-exposure review, record the team decision, approve an IBM-specific manifest and inference-only checklist, then revise/preserve generic loader RED tests. The earlier Prompt 04 test module is absent, so there is nothing to run GREEN yet.

Documentation and Git hygiene: `git diff --check` exited 0 (only a local LF/CRLF warning); a relative Markdown-link check exited 0 with 138 links checked; `git status --short --branch` exited 0. The read-only `git ls-remote` above exited 0. An attempted filtered, no-checkout metadata clone did not finish within about a minute, was interrupted (exit 1), and its incomplete ignored review directory was removed after verifying its absolute path remained inside the workspace. A Hugging Face API request failed to connect, so no API-derived file metadata is claimed. No application tests or Ruff were run for this documentation-only review. Prior uncommitted acquisition/RED/GREEN gate notes in this evidence and `next_work.md` were reviewed and preserved; the unrelated project-evidence edit and T029 draft files are excluded from this commit.

## Pretrained loader GREEN request gate check — 2026-11-13

At HEAD `13472f9058079687cf4ae4ce159db9286fdcb039` on
`model-implementations`, Prompt 04 has no RED test module or recorded intended
failures, and the inference architecture is still a proposal with no approved
artifact manifest or inference-only checklist. `backend/tests/unit/test_pretrained_loader.py`,
`backend/src/fraudlens/pretrained.py`, and `data/artifacts/` were absent at this
check. The existing untracked `evals/protocols/feature_002_v1.json` is a draft
of the original IBM training benchmark, not a pretrained artifact manifest.
The requested GREEN implementation therefore did not start. No model was
downloaded, loaded, trained, or run.

Read-only commands: `git status --short --branch`, `git rev-parse HEAD`,
`Test-Path` for the three paths above, `rg --files` for relevant manifests/tests,
and reads of `AGENTS.md`, `next_work.md`, the scope and architecture proposals,
and this evidence all exited 0. Loader tests, backend regressions and Ruff were
**not run** because no approved loader contract or RED suite exists. No GREEN
result, integrity smoke check or implementation commit is claimed.

Next: resolve PML-001, freeze an approved manifest and task checklist, then
write and execute loader RED tests before attempting GREEN implementation.

## Pretrained loader RED request gate check — 2026-11-13

At HEAD `13472f9058079687cf4ae4ce159db9286fdcb039` on
`model-implementations`, the requested RED loader tests were not written or run.
The [inference architecture](../../specs/002-data-and-risk-scoring/proposals/pretrained-inference-architecture.md)
is still explicitly a proposal; no approved artifact manifest instance or
authorized inference-only task checklist exists in this branch. The existing
[scope proposal](../../specs/002-data-and-risk-scoring/proposals/pretrained-model-integration.md)
records the team decision as pending. The original T037 tests a different,
locally trained artifact path and still depends on open T036. An API, accepted
format/runtime matrix, and feature-schema identity for a pretrained loader
would therefore be invented if tests were added now.

Read-only commands: `git status --short --branch`, `git rev-parse HEAD`,
`rg --files -g '*pretrained*' -g '*manifest*' -g '*model*' specs/002-data-and-risk-scoring
evidence/tasks backend/tests backend/src evals`, and reads of `AGENTS.md`,
`next_work.md`, the two proposals and current T029–T037 task entries all exited
0. The relevant backend test directory was listed successfully. Collection,
RED execution, dependency-version capture, and loader integrity tests were
**not run**; there are no intended test failures to report. No loader code,
model bytes, or original training-task checkbox was changed. The previously
documented acquisition block remains in force.

Next: record the actual scope decision; approve a concrete, versioned manifest
and inference-only checklist; then write and run synthetic RED tests against
that frozen contract.

## Acquisition request gate check — 2026-11-13

At HEAD `13472f9058079687cf4ae4ce159db9286fdcb039` on
`model-implementations`, the requested local acquisition workflow stopped before
download or code changes. The [scope decision](../../specs/002-data-and-risk-scoring/proposals/pretrained-model-integration.md)
still says "team decision pending," and the [inference architecture](../../specs/002-data-and-risk-scoring/proposals/pretrained-inference-architecture.md)
is explicitly a proposal. The ApexFi LightGBM text is a conditional IEEE-only
candidate, not an approved IBM model. Model/data reuse rights, safe equivalence
for mandatory fitted preprocessing, authentic complete IEEE input coverage, and
revised source-specific contracts/tasks are unresolved. The project's Python
requirement is `>=3.14,<3.15`; `pyproject.toml` does not declare LightGBM, so a
locked runtime compatibility check cannot yet pass without an approved dependency
decision. No package was installed or upgraded.

Read-only checks: `git status --short --branch`, `git rev-parse HEAD`, reads of
`AGENTS.md`, `next_work.md`, the two proposals, this evidence, constitution,
`.gitignore`, and `pyproject.toml` all exited 0. `git check-ignore -v
data/artifacts/lightgbm_model.txt data/raw/ieee/train_transaction.csv
evals/results/model-output.json` exited 0 and confirmed all three ignore rules.
No network download, artifact copy, deserialization, native parse, fit, inference,
evaluation, or integrity rerun occurred in this request; the earlier verified
source bytes and hashes below are historical evidence, not a newly acquired
local artifact. No downloader/configuration was implemented and no verification
success or commit is claimed. Existing working-tree changes were preserved.

**Next gate:** Record the actual team scope/rights decision and resolve safe
preprocessing parity, authentic IEEE examples, and the approved Python 3.14
LightGBM runtime/contract before acquisition.

**Observed 2026-11-13 on `model-implementations`, starting at
`b8643a42b7a1bed8f5b9199ddb31826c34d3591e`.** Read-only source and byte
inspection only. No model was deserialized, trained, fitted, tuned, invoked for
inference, or evaluated; no IBM source rows or holdout labels were read. The
[scope-change proposal](../../specs/002-data-and-risk-scoring/proposals/pretrained-model-integration.md)
still awaits the team's actual decision.

## Outcome

**No investigated pretrained model is compatible with direct IBM HI-Small
`history-v1` scoring.** The best artifact for a separate, clearly labeled
IEEE-CIS demonstration is ApexFi's **native LightGBM booster** because its
actual text-format bytes are obtainable without loading a Python pickle. It
is **not selected as the FraudLens IBM model**. Its original trained target is
IEEE-CIS `isFraud`, while FraudLens evaluates IBM `Is Laundering`; their labels,
populations and feature meanings differ. No score or claimed performance can
be transferred. IBM integration stops at this incompatibility gate pending a
new team decision and approved specification/tasks.

## Source and artifact comparison

| Source | Pinned source and actual files | License/provenance | Result |
| --- | --- | --- | --- |
| [shejz primary reference](https://github.com/shejz/IEEE-CIS-Fraud-Detection/tree/492cd00e40518c5f636686a3b079bb70a47bb6f5) | Git HEAD `492cd00e40518c5f636686a3b079bb70a47bb6f5`; tracked files are `README.md`, `Model.ipynb`, `EDA/EDA_I.ipynb`, `EDA/EDA_II.ipynb`. GitHub [releases API](https://api.github.com/repos/shejz/IEEE-CIS-Fraud-Detection/releases?per_page=100) returned `[]`; shallow clone had no tags. No weights/model binary in this revision. | GitHub repository metadata has no detected license; no license file is tracked. README/notebook are methodology, not permission or a pretrained model. | **No downloadable pretrained artifact found.** |
| [ApexFi IEEE-CIS model](https://huggingface.co/karthifde/apexfi-fraud-detection/tree/ffd8f87966cc911f11a7b9faf7096daee6101e1d/ieee_cis) | Hugging Face revision `ffd8f87966cc911f11a7b9faf7096daee6101e1d`. `ieee_cis/lightgbm_model.txt`: **15,503,690 bytes**, SHA-256 `e2ff1f42d0d73e910edd93d825bc6d62bd192677d100095171e045c8bf290574`, downloaded via Git LFS and independently hashed. `preprocessing_artifacts.pkl`: **3,633,997 bytes**, SHA-256 `65576e88c4668561367dcd53117edf9953cb479cde6f2b81b7938ef59b31785a`, also downloaded and hashed but never loaded. Other published LFS pointers: `gnn_model.pt` 232,745 bytes, SHA-256 `685463c24766074d32d3e565787fb089f6e8309c031c6fdf11b235ad433027ce`; `stacking_meta.pkl` 682 bytes, SHA-256 `3ad204eaace04f4602bd5ec4afc6db5d4e6ab738b1d40ccba853c59cdb132346`. These last two bytes were **not** fetched. | [Model card](https://huggingface.co/karthifde/apexfi-fraud-detection) declares MIT and research/educational use; underlying IEEE-CIS dataset conditions must be assessed separately. No independent proof of the claimed training run or model metrics was established. | **Actual native booster verified**, but only for IEEE-CIS semantics. Preprocessing pickle is required to recover the full input mapping. |
| [manasscodes alternative](https://github.com/manasscodes/IEEE-CIS-Fraud-Detection/tree/094b263cb77847035aa3db505df951a36eeea35b/models) | Git HEAD `094b263cb77847035aa3db505df951a36eeea35b`; actual committed bytes fetched and hashed: `models/lightgbm_tuned.pkl` **2,531,828 bytes**, SHA-256 `9d249e76ac85672aca997b4fcdd2722ce0c3c07531ff5e4baa575a3beed4377d`; `models/preprocessor.pkl` **65,057 bytes**, SHA-256 `d07e2b99aa0048029fc807cc5e2119b93aac31a4b17d088ab0253f238207d4ce`; `models/lightgbm_model.pkl` **408,116 bytes**, SHA-256 `d0f47ead8336924996b95f938d2b6250abe15dd3dfc864a5c43dd5e2cdde9f0b`. | [README](https://github.com/manasscodes/IEEE-CIS-Fraud-Detection/blob/094b263cb77847035aa3db505df951a36eeea35b/README.md) claims MIT, but there is no tracked LICENSE file and GitHub license metadata is empty. Exact reuse terms require clarification. | **Actual fitted files verified**, but pickle/joblib loading is unsafe for untrusted bytes; IEEE schema and Python requirement also block direct use. |

The [ApexFi native download](https://huggingface.co/karthifde/apexfi-fraud-detection/resolve/ffd8f87966cc911f11a7b9faf7096daee6101e1d/ieee_cis/lightgbm_model.txt)
is pinned to the revision above. Git LFS returned the complete text booster,
not its 133-byte pointer; the calculated digest equals the pointer OID. The
[ApexFi preprocessing download](https://huggingface.co/karthifde/apexfi-fraud-detection/resolve/ffd8f87966cc911f11a7b9faf7096daee6101e1d/ieee_cis/preprocessing_artifacts.pkl)
also returned full bytes with a matching digest. The alternative artifacts
were complete Git blobs in a temporary clone, not README-only references.
Nothing was copied into the FraudLens tracked tree.

## Exact input requirements and preprocessing

**ApexFi:** Static inspection of the native booster finds LightGBM `version=v4`,
binary sigmoid objective and `max_feature_idx=445`: exactly **446 ordered
numeric slots** named `Column_0` through `Column_445`. Those names carry no
business meaning by themselves. The verified preprocessing pickle was read
only with Python standard-library `pickletools.genops`, which parses opcodes
without executing them. Its ordered input is **435 raw columns + 9 frequency
columns + 2 graph-degree columns**; SHA-256 of compact JSON serialization of
that 446-name order is
`55c0a49ba855ab1e91857eb1ecb14da5295ed7b3831172a6468804ef1560977b`.
The first 13 raw names in order are `transactionamt`, `productcd`, `card2`,
`card3`, `card4`, `card5`, `card6`, `addr1`, `addr2`, `dist1`, `dist2`,
`p_emaildomain`, `r_emaildomain`, followed by **`v1`–`v339`**, `c1`–`c14`,
`d1`–`d15`, `m1`–`m9`, `id_01`–`id_38`, `devicetype`, `day_of_week`,
`hour_of_day`, `is_weekend`, `bank_rate`, `sbi_lending_rate`,
`call_money_rate` (with the exact intermediate order preserved in the pickle).
The nine appended names, in order, are `card1_freq`, `card2_freq`,
`card3_freq`, `card5_freq`, `addr1_freq`, `addr2_freq`, `deviceinfo_freq`,
`p_emaildomain_freq`, `r_emaildomain_freq`; the last two are
`device_shared_degree`, `card_shared_degree`.

The pinned [ApexFi preprocessing builder](https://github.com/KarthickRamAlagar/apexfi-fraud-graph/blob/29890b788cf3147b916ad8ab32010d672a547ca9/ml/build_preprocessing_artifacts.py)
records its categorical label encodings, train-derived frequency tables,
defaults, and order. The pinned [new-transaction feature builder](https://github.com/KarthickRamAlagar/apexfi-fraud-graph/blob/29890b788cf3147b916ad8ab32010d672a547ca9/ml/new_transaction_features.py)
constructs a `float32` 1-by-446 vector. Its 21 declared categorical fields
(`productcd`, `card4`, `card6`, `p_emaildomain`, `r_emaildomain`,
`devicetype`, `id_12`, `id_15`, `id_16`, `id_23`, `id_27`, `id_28`,
`id_29`, `id_30`, `id_31`, `id_33`, `id_34`, `id_35`, `id_36`,
`id_37`, `id_38`) use saved integer label maps; `m1`–`m9` use 1/0/−1; other
missing numeric fields default to 0; the nine frequency values use
`log1p` of saved counts; graph degrees require the source's card/device
neighbor lookup. The categorical mappings were fitted on the **full IEEE
dataset**, according to the builder, while frequency tables use training
rows. That full-dataset encoding procedure does not satisfy FraudLens's
train-only learned-transform rule. The card itself warns that Vesta `V`
features cannot be supplied for genuinely new transactions. The [inference
example](https://huggingface.co/karthifde/apexfi-fraud-detection/blob/ffd8f87966cc911f11a7b9faf7096daee6101e1d/predict_example.py)
loads the native booster plus PyTorch GraphSAGE and a pickle stacker; it
requires `lightgbm`, `torch`, `torch_geometric` via `model.py`, `numpy`, and
`scikit-learn` for the stacker. Its `torch.load(..., weights_only=False)` and
`pickle.load` are unsafe on untrusted files. LightGBM-only use would omit the
stacker's claimed hybrid result and still require exact preprocessing.

**manasscodes:** Non-executing static inspection of `preprocessor.pkl` finds
a fitted scikit-learn `ColumnTransformer` with **401 numeric** and **31
categorical** source fields, ordered as two groups (compact JSON group-order
SHA-256 `7f15f0ff37c0caabd18351ff46f89c934fa3522f3dbd998b10a6caea2e892960`).
Numeric order begins `TransactionDT`, `TransactionAmt`, `card1`, `card2`,
`card3`, `card5`, `addr1`, `addr2`, `dist1`, `dist2`, then `C1`–`C14`,
`D1`–`D15`, `V1`–`V339`, then `id_01`–`id_11`, `id_13`, `id_14`,
`id_17`–`id_22`, `id_24`–`id_26`, `id_32` (the absent members of those
ranges do not appear in the numeric group). The exact categorical order is
`ProductCD`, `card4`, `card6`, `P_emaildomain`, `R_emaildomain`,
`M1`–`M9`, `id_12`, `id_15`, `id_16`, `id_23`, `id_27`–`id_31`,
`id_33`–`id_38`, `DeviceType`, `DeviceInfo`. The [preprocessing
notebook](https://github.com/manasscodes/IEEE-CIS-Fraud-Detection/blob/094b263cb77847035aa3db505df951a36eeea35b/notebooks/02_data_preprocessing.ipynb)
selects `int64`/`float64` source dtypes for the numeric group and `object`
for the categorical group. It uses median imputation for numeric fields, most-frequent imputation and
`OneHotEncoder(handle_unknown="ignore")` for categoricals. Static strings
identify scikit-learn **1.9.0** in the fitted pickle; the tuned LightGBM
pickle embeds a binary booster with **2,703** anonymized `Column_*` outputs.
The repository pins LightGBM 4.6.0, NumPy 2.4.6, SciPy 1.18.0,
scikit-learn 1.9.0, pandas 3.0.3 and joblib 1.5.3, and its
`pyproject.toml` requires Python `>=3.12,<3.14`; FraudLens T028 uses
Python 3.14.10 with a different locked stack. None of these pickles was
deserialized.

## IBM and FraudLens compatibility matrix

Source mapping: [IBM HI-Small ordered fields](../../data/mappings/ibm_hi_small_v1.json),
[approved `history-v1` catalog](../../backend/src/fraudlens/feature_history.py),
and [v2 data/scoring contract](../../specs/002-data-and-risk-scoring/contracts/data-and-scoring.md).
“Derivable” means a deterministic IBM-side value can be computed, **not** that
it has the IEEE training meaning. No model-input row below is an exact
semantic match across datasets.

| IBM source field or FraudLens value | Closest IEEE input | Status and reason |
| --- | --- | --- |
| `Timestamp` / `event_time_utc` | `TransactionDT`; ApexFi `day_of_week`, `hour_of_day`, `is_weekend` | Calendar components are derivable under the documented synthetic clock convention, but IEEE `TransactionDT` is an offset from an unknown origin and its learned time distribution differs. No exact match. |
| `From Bank` / `sender_bank` | IEEE card issuer/bank hints, `card*` | No match. An IBM bank ID is not a payment-card property. |
| first `Account` / `sender_account` | `card1`, card frequencies, graph degree | No match. Bank-qualified sender account is not a card/device identity and cannot be used to query IEEE neighbor tables. |
| `To Bank` / `receiver_bank` | `addr*`, card/network hints | No match. Receiver bank is not billing region/address. |
| second `Account` / `receiver_account` | `card*`, `DeviceInfo` | No match. Distinct receiver account semantics. |
| `Amount Received` / `received_amount` | `TransactionAmt` | No match. IEEE has one USD payment amount; IBM preserves two sides and may have distinct currencies. |
| `Receiving Currency` / `received_currency` | None | Unavailable to IEEE model; no FX conversion is approved. |
| `Amount Paid` / `paid_amount` / `current_paid_amount` | `TransactionAmt` | Numeric decimal-to-float conversion is deterministic only after validating units, but IBM paid currency is not always IEEE USD and the target population differs. Conditional numeric resemblance is not a valid schema match. |
| `Payment Currency` / `paid_currency` / `current_paid_currency` | None | No equivalent IEEE feature; arbitrary USD assumption or FX conversion is forbidden. |
| `Payment Format` / `payment_format` / `current_payment_format` | `ProductCD`, `card6` | No match. Payment method/format is neither product code nor card type. |
| `Is Laundering` / private label | `isFraud` | Different target, never a predictor. IBM label remains private and cannot be mapped into IEEE feature input. |
| `sender_out_count_24h` | `C1`–`C14`, card frequency | No match: different entity, window and counting definition. |
| `sender_distinct_receivers_24h` | `C*`, graph degree | No match: directed bank-qualified counterparties versus IEEE card/device relations. |
| `sender_paid_count_same_currency_24h` | `C*`, card frequency | No match: current-currency, past-24h count is unavailable in IEEE encoding. |
| `sender_paid_sum_same_currency_24h` | `D*`, `C*` | No match: exact currency-specific Decimal sum versus unrelated IEEE features. |
| `receiver_in_count_24h` | `C*`, graph degree | No match: receiver-directed bank account history differs. |
| `receiver_distinct_senders_24h` | `C*`, graph degree | No match: directed counterparties differ. |
| `receiver_received_count_same_currency_24h` | `C*` | No match: receiver/current-currency definition differs. |
| `receiver_received_sum_same_currency_24h` | `D*` | No match: exact currency sum differs. |
| IBM event facts and full `history-v1` snapshot | `V1`–`V339`, `id_*`, `M*`, `dist*`, email/device/card/address, external rates | Unavailable. IBM does not provide Vesta anonymized fields, card/device/address/email/identity data, or the named market rates. Filling hundreds of mandatory slots with zero/null/defaults would lose model semantics. |
| v2 `ScoreRequestV2` identity, version, coverage and explanation | Source-specific IEEE inference payload | No compatible adapter exists. v2 demands the matching dataset/feature/artifact identity, label-free score request, finite [0,1] score and verifiable local explanation. A foreign IEEE probability cannot be relabeled as an IBM laundering risk assessment. |

## Security, legal and implementation decision

`pickle.load`, `joblib.load` and PyTorch loading with `weights_only=False`
can execute code during deserialization. No such loader was called. The
standard-library `pickletools` walk was static inspection only; it does not
establish that the pickles are safe to load. Prefer ApexFi's native LightGBM
text for any separately approved IEEE demonstration, after hash, path,
schema and runtime validation. A text parser still needs normal dependency
and file-integrity review. The Manass alternative has no native standalone
booster in this revision, so its Python object and fitted preprocessor
would require an unapproved trust decision. Its README's MIT sentence is
weaker than a tracked license grant; clarify with the owner before reuse.
The ApexFi MIT declaration does not resolve IEEE-CIS dataset terms, the
provenance of the trained weights, or permission for repackaging.

The [Feature 002 specification](../../specs/002-data-and-risk-scoring/spec.md)
requires `history-v1`-compatible inputs, source-bound artifacts and honest IBM
benchmark evaluation. The [constitution](../../.specify/memory/constitution.md)
requires explicit team approval for this scope change. **Team decision
pending:** choose either an isolated IEEE-CIS demonstration with its own data,
label, contracts and license review, or retain/revise the IBM model plan using
an IBM-compatible artifact if one can actually be found. Do not silently
route IBM cases through either investigated IEEE model, substitute missing
features, publish IEEE metrics as FraudLens results, change Phase 5 checkboxes,
or access the sealed holdout. No IBM integration is authorized by this record.

## Reproducibility and limits

Checks performed: `git ls-remote ... HEAD` for all three sources; temporary
`git clone --depth 1` outside the tracked tree; `git ls-files` and `git
rev-parse HEAD` with per-command `safe.directory`; GitHub public releases and
repository metadata API reads; `git lfs pull -I` for exactly the two ApexFi
files above; `Get-FileHash -Algorithm SHA256` and length checks; native text
header inspection; Python standard-library `pickletools.genops` and JSON
notebook source reading. All final byte/hash inspections succeeded. Initial
sandboxed network clones were blocked; approved elevated read-only fetches
succeeded. No executable import of third-party code or model objects occurred.
The static pickle scan does not prove every runtime preprocessing detail or
the accuracy of author-reported metrics. No dataset, inference, metric,
calibration or holdout check was run.

Documentation review before commit: `git diff --cached --name-status` exited
0 and listed only this evidence, `next_work.md` and the prompt record;
`git diff --cached --check` exited 0; a read-only Python relative-link check
exited 0 with 96 local links checked and none missing. No application tests
were run for this documentation-only investigation.
