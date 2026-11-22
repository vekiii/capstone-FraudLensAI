# T228 colleague guide: running the local AML models

**Status checked: 2026-11-20.** This guide is for a colleague with a Mac running macOS and an account able to access the repository and approved data transfer. macOS is not iOS. An iPhone or iPad does not provide the supported repository environment for this Python/LightGBM workflow; run it on a Mac, or on a team-provided Windows/Linux computer. Do not copy sensitive project data to an unapproved cloud service.

## Before starting: what is and is not ready

- The training code and locked Python environment are in the repository.
- The prepared features and train/validation labels are in ignored `data/processed/` folders on the original workstation. They are not in Git, so cloning the repository alone is not enough.
- The exact local CSV was approved for fitting, but the complete FR-021 training protocol is still a **candidate**. Its canonical SHA-256 is `f34c51bcaeec63072a29eceae987b85ff3e8d88ac106fe51e9fc16355d5b3f5f`; it has not been explicitly approved/frozen. The user previously asked for a protocol review and said to wait for explicit approval. **Do not start fitting until the team records approval of this exact protocol hash or a newly reviewed hash.**
- No model has been trained, so there are no measured fit times or performance results yet.

Ask the project owner to provide, through the team's approved transfer method:

1. The repository branch/commit that contains the runner and this guide.
2. `data/processed/t219-ibm-day-60-20-20-v1/` (label-free chronological features and manifest).
3. `data/processed/t219-ibm-day-60-20-20-labels-v1/` (training and validation labels only and manifest).
4. The reviewed protocol JSON and its approved canonical SHA-256, after the approval is recorded. The current candidate file is `specs/002-data-and-risk-scoring/t219-training-protocol.ibm-60-20-20.candidate.json`.

Do not substitute the raw CSV, the historical T210 files, test labels, or showcase data. If the project owner cannot provide these exact inputs and their manifests, stop and ask them to finish/repeat the approved preparation on the source workstation. Do not create partitions yourself.

## 1. Prepare the Mac

Open Terminal and install Git and `uv` using the team's approved package installation method. `uv` is the project's Python environment and lockfile manager. Install Apple's command line developer tools if Git or native build support asks for them:

```sh
xcode-select --install
```

If macOS says they are already installed, continue. Confirm the tools:

```sh
git --version
uv --version
```

Clone the approved repository URL and enter the project directory (replace the URL and branch with the values the project owner supplies):

```sh
git clone <approved-repository-url> FraudLensAI
cd FraudLensAI
git switch <approved-branch>
git status --short --branch
```

Check that this checkout contains the runner:

```sh
test -f backend/src/fraudlens/training/local_run.py && echo "training runner found"
```

## 2. Place and check the prepared inputs

If you received `T228-colleague-transfer-2026-11-20.zip`, verify its SHA-256 against `T228-colleague-transfer-2026-11-20.zip.sha256` and extract it in a separate local directory. Run the commands from the Git clone created in step 1: the runner requires a Git revision, and the ZIP snapshot has no `.git` directory. Copy the two prepared directories from the extracted bundle into that clone, preserving their filenames and contents:

```sh
shasum -a 256 /path/to/T228-colleague-transfer-2026-11-20.zip
unzip -q /path/to/T228-colleague-transfer-2026-11-20.zip -d /path/to/extracted-bundle
mkdir -p data/processed
cp -R /path/to/extracted-bundle/FraudLensAI/data/processed/t219-ibm-day-60-20-20-v1 data/processed/
cp -R /path/to/extracted-bundle/FraudLensAI/data/processed/t219-ibm-day-60-20-20-labels-v1 data/processed/
```

Compare the printed ZIP SHA-256 with the separately supplied `.sha256` file. If the repository branch has not yet been pushed, ask the owner for the updated branch before continuing. The protocol JSON is in the clone; use the reviewed path and approved hash supplied by the owner. Do not put raw or record-level labels in tracked files.

Check that all three locations exist:

```sh
test -f data/processed/t219-ibm-day-60-20-20-v1/manifest.json
test -f data/processed/t219-ibm-day-60-20-20-labels-v1/manifest.json
test -f specs/002-data-and-risk-scoring/t219-training-protocol.ibm-60-20-20.candidate.json
```

Have the project owner confirm the transferred manifest digests against [T219 evidence](T219.md) before proceeding. Those expected manifest digests are:

- Feature manifest: `63873b79a1ff875c5702a62c40c7a9cb3faef6bb7e0bb658739abac35274c05f`
- Train/validation label manifest: `5aee2e1d5f4f2ca7329fcc7b5b1ca0c808c4e8e39e84559e76a0d3e1a6add12c`
- Current candidate canonical JSON digest (hash the canonical JSON, not the file bytes): `f34c51bcaeec63072a29eceae987b85ff3e8d88ac106fe51e9fc16355d5b3f5f`

The application candidate verifier rechecks source and manifest bindings at run time. If any check fails, stop; do not edit manifests or change the expected hashes to make the run pass.

## 3. Create the locked Python environment

From the repository root, run:

```sh
uv sync --locked --group dev --group ml
uv run --locked --group ml python --version
uv run --locked --group ml python -c 'import lightgbm, sklearn; print("LightGBM", lightgbm.__version__, "scikit-learn", sklearn.__version__)'
```

Expected locked versions are Python 3.14.10, LightGBM 4.7.0 and scikit-learn 1.9.1. macOS was not the platform used for the recorded compatibility run. If `uv sync` cannot resolve/install the lock on her Mac (including Apple Silicon), save the full error and stop; do not loosen or regenerate the lock. Send the Mac model/chip, macOS version, `uv --version`, and error to the project owner.

## 4. Run no-fit checks first

These commands check the candidate, CLI and relevant synthetic tests; they do not train a model:

```sh
uv run --locked --group ml python evidence/tasks/T219-ibm-candidate.py
uv run --locked --group ml python -m fraudlens.training.local_run --help
uv run --locked --group dev --group ml pytest backend/tests/unit/test_research_split.py backend/tests/unit/test_research_labels.py backend/tests/unit/test_research_protocol.py backend/tests/unit/test_local_run.py backend/tests/unit/test_lightgbm_matrices.py backend/tests/unit/test_evaluation.py -q --basetemp .cache/pytest-ibm-training
```

If a command fails, keep its complete output and stop before fitting. These tests do not establish model performance or Mac fit compatibility.

## 5. Confirm the approval gate, then run the experiment

Before fitting, the project owner must give you the approved protocol JSON path and its canonical hash, and point you to the written human decision. Confirm it is the hash in that decision. The hash below is the current **unapproved candidate** and is shown only to make the present stop condition concrete:

```text
f34c51bcaeec63072a29eceae987b85ff3e8d88ac106fe51e9fc16355d5b3f5f
```

Once approval is recorded, substitute the approved path, exact approved hash, and a new output directory in this command. Start with four worker threads, as in the project runbook:

```sh
uv run --locked --group ml python -m fraudlens.training.local_run \
  --features data/processed/t219-ibm-day-60-20-20-v1 \
  --labels data/processed/t219-ibm-day-60-20-20-labels-v1 \
  --protocol <approved-protocol.json> \
  --protocol-sha256 <approved-canonical-sha256> \
  --output data/eval/ibm-day-lightgbm-mac-001 \
  --n-jobs 4
```

The output path must not already exist. This fits the eight frozen LightGBM candidates; it does not fit the HistGradientBoosting comparisons or the baselines. The runner uses training data to fit preprocessing and class weights, validation data for early stopping and selection, and does not read test labels. Do not increase threads or run concurrent copies on the same Mac during the first run.

## 6. Collect and deliver the result

The run creates files under the ignored path `data/eval/ibm-day-lightgbm-mac-001/`. The main review files are:

- `experiment.json`: run identity, input/protocol/lock hashes, runtime versions, candidate settings, training counts and selected candidate/threshold.
- `validation-scores.csv`: validation predictions and row identifiers for each candidate. Treat as project data; transfer/store only through the approved method.
- `artifacts/selected-lightgbm/model.txt` and its manifest: selected native LightGBM text model and integrity metadata.
- `test-predictions-sealed.csv`: predictions for the frozen test rows without labels. Keep sealed; do not inspect against labels or alter the validation-selected threshold.

At the end, record the terminal output, run folder, Mac model/chip, macOS version, wall-clock duration and whether the command completed. Send the project owner the `experiment.json`, aggregate console summary, and model artifact through the approved transfer method. Do not commit `data/processed/` or `data/eval/` to Git. The project owner should review the manifest and validation results. Test evaluation is a separate, explicitly authorized step; do not run it as part of this guide. Showcase labels remain excluded.

## Candidate models and decisions after this run

The active candidate family is LightGBM only. The eight settings cross `num_leaves` 31/63, `learning_rate` 0.05/0.1, and `min_child_samples` 50/200; each uses up to 1,000 boosting rounds, validation early stopping after 50 rounds without improvement, seed 42, CPU execution, and train-only positive-class weighting. The positive-class weight is calculated from training labels, not validation/test labels. Threshold and candidate ranking use validation metrics under the candidate protocol.

This run answers which one of those eight candidates ranks best on this validation partition under the frozen rule. It does **not** establish test performance, showcase performance, generalization to another dataset, or production readiness. The separate HistGradientBoosting family has five implemented configurations; prevalence, depth-5/minimum-leaf-500 tree and L2 logistic baselines are also implemented. They are not part of this LightGBM-only run and should only be compared later after the team reviews and activates the previously frozen cross-family comparison rule. Do not change the ranking objective or add candidates after seeing results without recording a new human decision and protocol version first.

## If she literally has an iPhone/iPad

She cannot follow the local Mac terminal steps on iOS. Use a Mac or a team-provided remote Windows/Linux computer, and follow that machine's access and data-handling rules. Do not upload the dataset to a personal notebook/cloud runtime as a workaround.
