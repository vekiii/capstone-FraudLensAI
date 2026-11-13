# Main merge review - 2026-11-13

## Decision and exact revisions

User requested review of collaborators' branches and merging verified work into main.
After fetching origin, the clean starting checkout was local `initialization` at
`55306089b506458fcaec9b621f49c00dd971d46e`, also the remote
`002-data-and-risk-scoring` tip. Its name therefore does not identify the stable
foundation snapshot. No branch was reset and no collaborator commits were rewritten.

Merge candidate: **origin/initialization**, commit
`f37e67a554395b564feadbd8d39a2ea151993a94`.
Main before merge: `b03e8e3b9b5a4234beb2fcc15fecf3b1507df737`.
Candidate includes accepted feature 001 and feature 002 specification/planning
documents, not the feature 002 importer implementation. Foundation runtime,
fixtures, dependency files and feature 001 artifacts are unchanged from accepted
`33bcf62`. All T001-T028 are checked; existing human/peer evidence records team
acceptance without claiming independent machine installations.

Feature 002 implementation at `5530608` is **excluded** pending the Windows
regression below and completion of its remaining tasks. Its historical successful
macOS tests and IBM import are preserved on that branch, not independently
reproduced here. Planning documents on main must not be mistaken for working ML.

## Actual verification

Windows; Python 3.14.3; Node 24.20.0; npm 11.19.0.
A detached worktree `.cache/merge-review-foundation` pinned to f37e67a isolated
the candidate from the newer feature branch. Its tracked worktree stayed clean.

- `uv sync --locked --group dev --offline --python <existing Python interpreter>`:
  exit 0, isolated environment created with locked dependencies.
- `npm.cmd --prefix frontend ci --offline --no-audit --no-fund`: exit 0.
- `npm.cmd --prefix frontend run test -- --run`: **151 passed**, exit 0.
- `npm.cmd --prefix frontend run typecheck`: exit 0.
- `npm.cmd --prefix frontend run build`: exit 0.
- `uv run --locked pytest backend/tests -q --basetemp <unique absolute workspace
  cache path> -o cache_dir=<unique absolute workspace cache path>`:
  **310 passed**, exit 0; existing Starlette/httpx deprecation warning.
- `uv run --locked ruff check backend`: exit 0.
- After switching main and preparing the merge, `.venv/Scripts/python.exe -m
  pytest backend/tests -q` with fresh absolute workspace temp/cache overrides:
  **310 passed**, exit 0, same warning. Ruff again exit 0.
- `git diff --quiet f37e67a -- backend frontend pyproject.toml uv.lock
  data/fixtures`: exit 0 on prepared main; reviewed runtime is identical.

Initial isolated pytest attempt used a nonexistent relative `.cache` parent:
235 passed / 75 setup errors (WinError 3). Corrected absolute paths produced the
310-pass result above; no test or application behavior was weakened. A plain
Python diagnostic initially lacked the application's import path; explicitly
setting PYTHONPATH confirmed imports came from the isolated worktree.
No fresh browser verification or model evaluation is claimed. Existing browser
evidence is historical feature 001 T019 evidence.

## Why feature 002 waits

On starting revision 5530608, executing the complete backend suite on this Windows
checkout produced **459 passed, 6 failed**, exit 1. All failures are in
`backend/tests/integration/test_data_store.py`: the helper at line 40 compares
the reviewed LF-normalized mapping digest to SHA-256 of raw checkout bytes.
With `core.autocrlf=true`, the mapping has CRLF bytes. The production authorization
loader intentionally normalizes CRLF to LF, consistent with the approved policy.

Reviewed normalized digest:
`a816260aecc12f056dedc53397ff9c5f19b0e9b5bd669db1e1d1b2a849093e57`.
Raw Windows checkout digest:
`9a87e1ddaad2c6825d76111eae4fdcf54e2bec5ed0c7c25685b1ea8a0dd42ae1`.

Affected cases: import/replay/private output; wrong source/mapping hash;
interrupted-stage retry; changed-source protection in_place/replace/size_change.
They fail at the helper assertion before testing those behaviors. This is not
evidence of a defective actual import, but prevents declaring the branch green
on the team's Windows setup. Do not change approved mapping semantics or remove
provenance assertions to hide the failure.

Next: on the feature branch, align the test helper with the reviewed normalized
digest policy, add explicit LF/CRLF regression coverage, run the full suite and
relevant checks, then review the branch for merge again. A repository EOL policy
may be considered separately; no mapping bytes or feature 002 code were changed
in this merge review. T017 and later implementation still remain separate work.

## Publication and limits

The candidate's 151 tracked files had no file larger than 1 MB and no tracked
raw/processed datasets, environments, node_modules, build output or local secrets
files. A bounded scan for common private-key/token signatures found no matches;
this is not an exhaustive security audit.

Historical `git diff --check main..origin/initialization` has two cosmetic
extra-blank-line-at-EOF warnings in
`prompts/development/001-foundation-phase-02.md:155` and
`specs/002-data-and-risk-scoring/spec.md:755`. They do not affect runtime; original
prompt content was preserved. This review does not claim a warning-free historical
diff. The local merge preserves both parents; no push is performed.

Original request: [merge review prompt](../../prompts/development/main-merge-review-2026-11-13.md).
