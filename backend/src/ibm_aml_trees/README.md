# IBM AML tree notebook reproduction

This is an **offline exploratory experiment**, separate from the FraudLens
`history-v1` application scorer and from the untracked Feature 002 protocol.
The input is the local IBM HI-Small CSV. The reference notebook is in
`reference/ibm-aml-with-trees.ipynb`.

Run from the repository root in PowerShell with the locked project environment:

```powershell
$env:PYTHONPATH = 'backend/src'
.\.venv\Scripts\python.exe -m ibm_aml_trees.train --data data/raw/HI-Small_Trans.csv --out artifacts --retro
.\.venv\Scripts\python.exe -m ibm_aml_trees.evaluate --run artifacts/<run_id>
```

Optional flags: `--train-frac F` samples only the training partition after
full-history feature construction; `--split stratified` is a **development-only**
grouped split that leaks time and is not comparable to the temporal result.
`--retro` adds **delayed alerts, not real-time**. The default is a temporal
60/20/20 split, three seeds (0, 1, 2), and 1,000 bootstrap resamples per
variant and seed. The CLI prints elapsed seconds for loading, feature creation,
and each variant's fit/evaluation stage.

The source CSV, generated models, and manifests stay in ignored local paths.
Each completed run contains `manifest.json`, `model.joblib` (history model,
seed 0), other seed/ablation model files, and `scoring.py`. Import the latter
from a **trusted local run** to call `score(df_history, df_new)`; both inputs
can be pandas DataFrames or lists of dictionaries with `ts`, `from_bank`,
`from_acct`, `to_bank`, `to_acct`, `amt_paid`, `cur_recv`, `cur_paid`, and `fmt`.
It returns model probabilities in the original order of `df_new`. A label
column, if present, is ignored. Joblib files are executable serialization:
do not load files from external or untrusted origins.

The reader uses Python CSV and NumPy arrays because pandas and PyArrow are
not installed in the locked project environment. It retains bank/account
strings until integer coding, stable-sorts timestamps, and saves each original
row index. The 29 feature names and formulas follow the notebook. The
notebook's account-history keys are account strings **without bank
qualification**; they therefore do not satisfy FraudLens's application
identity contract. Rows earlier in stable order within the same minute count
as history, also unlike FraudLens `history-v1` which excludes all same-time
peers. These results must not be presented as an application model score.

Other deliberate differences from the notebook: split boundaries move to
whole timestamp groups so train/validation/test have no time overlap;
sampling happens only after full feature construction; validation-only
threshold selection, 95% bootstrap intervals, versioned manifests and
model reload checks are added. Only HI-Small training/evaluation and optional
retroactive flagging are implemented. The notebook's LI-Small, HI-Medium,
plots and patterns-file analyses are outside this isolated task.

The manifest records pandas as `null` because it is not installed. PR-AUC is
scikit-learn average precision. Bootstrap intervals resample test rows with
the model and validation threshold held fixed; they do not measure variation
from model retraining or dataset generation. Re-reading a completed manifest
with `evaluate` displays its recorded metrics without reusing test labels.
