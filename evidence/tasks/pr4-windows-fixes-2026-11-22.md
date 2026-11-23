# PR #4 Windows fixes — 2026-11-22

The changes address the SQLite connection lifetime, direct publisher coverage
and shared manifest trust findings from the Windows review. The working branch
was `integration/model-rag-handoff` starting at PR #4 head `c0d59f2`.
The base was `integration/capstone-mvp` at `dd0bf612`. The verified code,
tests and quickstart are in commit `f68d2cd9cd0264770a94feda0f93634f621145a8`.
[User approval](../../prompts/development/2026-11-22-pr4-windows-fixes.md) · [Review evidence](pr4-windows-review-2026-11-22.md)

## Implementation

- Both offline publisher SQLite connections close after their transactions and
  before manifest sealing and the atomic stage rename. The reader test writers
  also close their connections before the missing-source assertion deletes a file.
- The model API and investigation adapter, including the worker, use
  `MODEL_CASE_BRIDGE_MANIFEST_SHA256`. The reader hashes the exact bytes it will
  parse and matches them and `COMPLETE` to the expected digest before parsing.
  Frozen lineage, database digest and semantic checks still run. Both routes
  return controlled 503 errors for an invalid or absent pin, and fixture case
  access remains available. The trusted digest comes from the handoff for the
  exact artifact. [Windows quickstart](../../specs/003-ai-investigation/quickstart.md)
- The new publisher tests call the production publisher on an authored
  one-row snapshot. The real snapshot completion and feature file verifiers
  run. The feature and prediction pins and frozen scorer are substituted for
  the synthetic input. Checks cover activation, absence of the private
  canary in the published data, the exact score, sealed database hashes,
  destination preservation and refusal of a changed feature partition.

## Windows execution

- RED on Python 3.14.10 ran `python -m pytest -q backend/tests/integration/test_model_case_bridge_reader.py backend/tests/integration/test_model_case_bridge_publisher.py --basetemp .cache/pr4-red-pytest`. Exit 1 with 7 failures and 11 passes. Both routes returned 200 in the five missing, invalid or resealed digest cases where 503 was expected. The publisher failed with WinError 5 at `os.replace` and the source-removal test failed with WinError 32.
- GREEN ran the same two modules plus `backend/tests/integration/test_model_case_bridge_api.py`, `backend/tests/contracts/test_model_case_bridge.py` and `backend/tests/integration/test_investigation_dataset_adapter.py`, with `--basetemp .cache/pr4-green-pytest`. All 65 passed. Ruff and `git diff --check` passed. Runtime dependencies used the locked Python 3.14.10 environment from the review.
- Isolated regression and browser work ran from the exact source archive of
  `c0d59f2` with the seven changed source and test files overlaid and byte
  checked. The transfer ZIP was rehashed and the 19 extracted entries matched
  their checksums. The transferred publication was reused, with expected
  manifest digest `16760ba36a2b36e6f144730c7afae7c855e34b2897166920bc6d185fcf9d2004`.
- Full backend `python -m pytest -q -rs backend/tests --basetemp backend-test-temp-final`
  used workspace-local `TEMP` and `TMP` and absolute `PYTHONPATH` pointing to
  the test checkout's `backend/src`. Exit 0 with **1,407 passed and 1 skipped**
  in 124.21 seconds. The skip was the Windows symlink-creation case and the
  six warnings were from LightGBM's synthetic diagnostic tests. The preceding
  run omitted `PYTHONPATH` and one existing Windows resource-supervisor child
  failed to import `fraudlens`. The child test passed in isolation with the
  corrected environment and in the complete rerun.
- `npm.cmd --prefix web ci --offline`, `npm.cmd --prefix web test -- --run`,
  and `npm.cmd --prefix web run build` exited 0 with **290 React passes**,
  typecheck and build. Vite reported its bundle-size warning.
- `python evidence/tasks/T233-parity.py` exited 0 with **8/8 exact frozen score matches and 1/1 exact ASGI HTTP match**. The unchanged score for the browser case was `0.9267620061893889`, matching the live risk and binding API results. The local model cases, fixture cases, results and EDA calls returned 200. The unpublished ID and stale snapshot returned 404 and 409.
- Chrome 158.0.8127.36 exercised the risk-to-investigation path with the
  independent digest set in the API and worker environment. A fresh local
  store used the approved corpus and test provider. The one-shot worker
  reached `ready_for_review` on attempt `att_cdce0e88a3d04e31ab9d61cd4d23ab56`.
  Both cited evidence endpoints returned 200 and each evidence pane rendered
  before the browser continued. The browser saved test review
  `rev_a28af537158846c2b017441b4016a202` and restored it after reload.

## Limits and continuation

This run exercised a synthetic publisher and consumed the existing, verified
full publication. It did not regenerate the full publication, retrain the
project model, repeat T230, access record-level labels, perform showcase replay
or call a real LLM provider. Git-tracked changes exclude the transfer artifacts,
local browser state, and test investigations. T252 remains open for actual
independent human review and reproduction. The PR #4 merge decision remains
separate from publication of these fixes. [T252 review packet](feature-002-review.md)
