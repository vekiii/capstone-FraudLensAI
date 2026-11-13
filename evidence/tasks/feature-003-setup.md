# Feature 003 setup evidence
Date 2026-11-13 Europe/Belgrade. Branch feature03; baseline fd6d724b83a3a35cee9bf821651e56ffc269b2f9.
Initial untracked specs/003-ai-investigation/feature3_tasks_prompt.md preserved.
Scope T001-T004, FR-003/004-006/017-018/024-025/028.
Original prompt: ../../prompts/development/003-investigation-phase-01.md.
Spec-kit prerequisites exit 0, correct absolute feature directory. Checklist 16/16.
No extension hooks configured. Read constitution/design/evaluation/tools boundaries,
previous planning evidence and foundation setup. Toolchain uv 0.10.9, Python 3.14.3,
Node 24.20.0, npm 11.19.0. uv sync --locked --group dev exit 0, 40 audited.
T001 complete: meaningful package/fixture boundaries; unit tests and policy READMEs
follow in sequence. No dummy future modules, fake data, .gitkeep or empty dir claims.
Lockfiles inspected, no modifications. Human review pending. No provider/model/key
access, producer approval or independent reproduction claimed.

T002 actual RED: uv run --locked pytest backend/tests/unit/test_investigation_settings.py
--basetemp D:/AIBootcamp/capstone/.cache/003-red-f285a213aeb745389b8a83673d999d65
-o cache_dir=D:/AIBootcamp/capstone/.cache/003-cache-f285a213aeb745389b8a83673d999d65 --tb=short
Exit 1: 81 collected and 81 failed, NotImplementedError at importable load_settings
boundary. No import/collection/temp errors; missing configuration implementation
was the expected reason. Minimal scaffold contained no preimplemented validators.
One upstream Starlette/httpx warning. T003 next; GREEN pending.

T003 GREEN command: same targeted pytest with
--basetemp D:/AIBootcamp/capstone/.cache/003-green-ec408d34f64a4edf9389f2c09e36a359
-o cache_dir=D:/AIBootcamp/capstone/.cache/003-cache-ec408d34f64a4edf9389f2c09e36a359
--tb=short. Exit 0: 81 passed, one known Starlette/httpx warning. Ruff exit 0.
Separate InvestigationSettings/load_settings, explicit environment only; no .env
loader, foundation settings change, provider SDK or factory composition. SecretStr
key/model fields repr=False/exclude=True; safe generic validation errors.
Default store dedicated investigations.sqlite under data/processed; overrides are
trusted operator paths and must not target producer storage (no producer DB opened).
Limits documented in .env.example; smaller positive integer overrides allowed,
counts/seconds/UTF-8 input bytes/output tokens/response bytes explicit. No access
verification inferred from explicit model presence. Empty .env values are examples.
T003 complete; T004 policy READMEs now delivered, no runtime/evaluation content.


## Final verification / T004 completion
From repo root, UV_CACHE_DIR=D:/AIBootcamp/capstone/.cache/uv.
- uv run --locked pytest backend/tests/integration/test_startup.py --basetemp
  D:/AIBootcamp/capstone/.cache/003-startup-5877e3dbb3d4468fb249754cc4ca2ff6
  -o cache_dir=D:/AIBootcamp/capstone/.cache/003-cache-5877e3dbb3d4468fb249754cc4ca2ff6
  --tb=short: exit 0, 8 passed.
- uv run --locked pytest backend/tests --basetemp
  D:/AIBootcamp/capstone/.cache/003-regression-8fa846ed0b8347a28e795e2fd35a9d4e
  -o cache_dir=D:/AIBootcamp/capstone/.cache/003-cache-8fa846ed0b8347a28e795e2fd35a9d4e
  --tb=short: exit 0, 391 passed (310 existing + 81 configuration tests).
- uv run --locked ruff check backend: exit 0.
Known upstream Starlette/httpx deprecation warning, no runtime/test failure.
No feature 002 failures observed on this branch; no feature 002 code touched.
T004 knowledge/evaluation READMEs distinguish runtime sources, private reference,
frozen inputs/splits/rubric and ignored generated results. No evaluation data authored.
Generated SQLite/index data is local under data/processed; evaluation outputs local
under evals/results/feature-003; neither created by settings or this setup phase.

Actual git check-ignore -v each exited 0 for .cache/003-probe/tmp,
data/processed/investigations.sqlite and -wal, data/processed/investigation-index.bin,
evals/results/feature-003/results.json, .env and .env.local.
Per-path git check-ignore -q each exited 1 (shareable) for .env.example,
data/knowledge/README.md, planned corpus manifest path, evals/investigation/README.md,
data/fixtures/investigation/README.md, lockfiles and shared skill/constitution.
Existing ignore policy sufficient, no ignore edits. Synthetic fixture boundary README
is intentional scaffolding, not fake contexts/history/provider data.

Limits/future work: no actual provider/model access verified, no SDK added, no
corpus ingestion/retrieval, outbound mapper, store implementation, CLI, workflow,
reports/UI or held-out evaluation. Foundation APP_MODE unchanged. Human review,
producer approval and independent reproduction pending. No commit/push/merge/deploy.
T001-T004 complete; T005 and later not started.

Final authored files normalized to UTF-8/LF; rechecked targeted pytest with
--basetemp D:/AIBootcamp/capstone/.cache/003-final-b6e022b8b4964b58a3d50830a3e4536f
-o cache_dir=D:/AIBootcamp/capstone/.cache/003-cache-b6e022b8b4964b58a3d50830a3e4536f
-q: exit 0, 81 passed; Ruff exit 0. Resolved versions: Pydantic 2.14.3,
FastAPI 0.162.4, pytest 9.2.0, httpx 0.28.1, Ruff 0.17.4.
Original saved prompt exact-text comparison True. Final hook check absent.
Reviewed all changed/new authored files and task diff: only T001-T004 checked.
Final git diff --check and per-new-file --no-index --check NUL passed.
Preexisting untracked task prompt left untouched, not treated as authored setup.
