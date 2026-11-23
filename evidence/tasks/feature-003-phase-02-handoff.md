# Feature 003 phase 2 handoff
Date 2026-11-14 Europe/Belgrade (work began 2026-11-13). Branch feature03; baseline 6db94af3471a9007a8a0d88cba8c7ece32886483; initial tree clean.
Prompt: ../../prompts/development/003-investigation-phase-02.md. Human review pending.

T005/T006 contract boundary GREEN 57; T007/T008 fixture boundary GREEN 6. T009-T012 pending. Next: repository RED tests. No external blocker.

## Final state - phase 2 complete
T005-T012 completed by task type: T005/7/9 executed RED before T006/8/10 GREEN;
T011 artifacts saved/checked; T012 RED intentionally remains for T019/T035.
T013 onward untouched. Existing foundation and feature 002/ML files, schemas,
contracts, byte content of data/fixtures/cases.json and lockfiles unchanged.

Versions actually executed: Python 3.14.3, uv 0.10.9, Node 24.20.0, npm 11.19.0.
No dependency upgrades/installs required; existing project/lock configuration used.
Checklists 16/16; prerequisites selected feature 003 and exit 0; no hooks.

T011: initial application prompt investigation-v1 and untuned BM25 baseline config
version 1; k1=1.2,b=0.75, NFKC+casefold, Unicode alphanumeric tokens, deduplication,
passage-ID ascending ties, max 5 results. No glossary/improvement/retrieval executed.
Cutoff is explicitly null/unselected pending reviewed development data. This is
initial design, not proven quality or provider/human approval.
Prompt SHA256 (UTF-8 text, CRLF->LF only, no trimming/BOM): 21d7da36b4ff9bd5121f26c541d9ec5ba403e6bddbb683b7cc3abd5ec19d4a99
Config text SHA256 (same policy): 2a2dc7f8a9c55dd9f19f571c0bc58627be544ae17680eca6c40f6447f54a8750
Config canonical JSON SHA256 (UTF-8, sorted keys, compact separators, no NaN): 8985ddb2e1d5dbed481c1569464e2a5cd24f6c76b010c5f999d9550f7f1cb441

## Final actual commands and results

Command: `uv run --locked pytest backend/tests/unit/test_investigation_settings.py backend/tests/integration/test_startup.py --basetemp D:\AIBootcamp\capstone\.cache\003-p2-ef24d89e8ba04d9c93df02f34b1be26a -o cache_dir=D:\AIBootcamp\capstone\.cache\003-p2-cache-ef24d89e8ba04d9c93df02f34b1be26a --tb=short -q`

Exit 0.

```text
........................................................................ [ 80%]
.................                                                        [100%]
============================== warnings summary ===============================
.venv\Lib\site-packages\fastapi\testclient.py:1
  D:\AIBootcamp\capstone\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
89 passed, 1 warning in 0.66s
```

Command: `uv run --locked pytest backend/tests --basetemp D:\AIBootcamp\capstone\.cache\003-p2-fc382f4dbf4447b48159eb6ceb1dc600 -o cache_dir=D:\AIBootcamp\capstone\.cache\003-p2-cache-fc382f4dbf4447b48159eb6ceb1dc600 --tb=short -q`

Exit 1.

```text
........................................................................ [ 14%]
........................................................................ [ 29%]
........................................................................ [ 44%]
FFFF.................................................................... [ 59%]
........................................................................ [ 74%]
........................................................................ [ 89%]
....................................................                     [100%]
================================== FAILURES ===================================
_ test_new_errors_are_feature_specific[/api/knowledge/search?q=test-knowledge_unavailable] _
backend\tests\integration\test_investigation_feature_toggle.py:46: in test_new_errors_are_feature_specific
    assert response.json().get('contract_version') == 1
E   AssertionError: assert None == 1
E    +  where None = <built-in method get of dict object at 0x000001CF50696900>('contract_version')
E    +    where <built-in method get of dict object at 0x000001CF50696900> = {'error': {'code': 'case_not_found', 'message': 'Case not found.'}}.get
E    +      where {'error': {'code': 'case_not_found', 'message': 'Case not found.'}} = json()
E    +        where json = <Response [404 Not Found]>.json
_ test_new_errors_are_feature_specific[/api/investigation/attempts/att_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-investigation_not_found] _
backend\tests\integration\test_investigation_feature_toggle.py:46: in test_new_errors_are_feature_specific
    assert response.json().get('contract_version') == 1
E   AssertionError: assert None == 1
E    +  where None = <built-in method get of dict object at 0x000001CF50677640>('contract_version')
E    +    where <built-in method get of dict object at 0x000001CF50677640> = {'error': {'code': 'case_not_found', 'message': 'Case not found.'}}.get
E    +      where {'error': {'code': 'case_not_found', 'message': 'Case not found.'}} = json()
E    +        where json = <Response [404 Not Found]>.json
_____________________ test_cross_origin_mutation_rejected _____________________
backend\tests\integration\test_investigation_feature_toggle.py:55: in test_cross_origin_mutation_rejected
    assert response.status_code == 403
E   assert 404 == 403
E    +  where 404 = <Response [404 Not Found]>.status_code
_________________________ test_mutation_requires_json _________________________
backend\tests\integration\test_investigation_feature_toggle.py:64: in test_mutation_requires_json
    assert response.status_code == 422
E   assert 404 == 422
E    +  where 404 = <Response [404 Not Found]>.status_code
============================== warnings summary ===============================
.venv\Lib\site-packages\fastapi\testclient.py:1
  D:\AIBootcamp\capstone\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED backend/tests/integration/test_investigation_feature_toggle.py::test_new_errors_are_feature_specific[/api/knowledge/search?q=test-knowledge_unavailable]
FAILED backend/tests/integration/test_investigation_feature_toggle.py::test_new_errors_are_feature_specific[/api/investigation/attempts/att_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-investigation_not_found]
FAILED backend/tests/integration/test_investigation_feature_toggle.py::test_cross_origin_mutation_rejected
FAILED backend/tests/integration/test_investigation_feature_toggle.py::test_mutation_requires_json
4 failed, 480 passed, 1 warning in 4.20s
```

Command: `uv run --locked pytest backend/tests --ignore=backend/tests/integration/test_investigation_feature_toggle.py --basetemp D:\AIBootcamp\capstone\.cache\003-p2-a082b3b8210c4e71b3cc7982060887af -o cache_dir=D:\AIBootcamp\capstone\.cache\003-p2-cache-a082b3b8210c4e71b3cc7982060887af --tb=short -q`

Exit 0.

```text
........................................................................ [ 15%]
........................................................................ [ 30%]
........................................................................ [ 45%]
........................................................................ [ 60%]
........................................................................ [ 75%]
........................................................................ [ 90%]
.............................................                            [100%]
============================== warnings summary ===============================
.venv\Lib\site-packages\fastapi\testclient.py:1
  D:\AIBootcamp\capstone\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
477 passed, 1 warning in 3.57s
```

Command: `uv run --locked ruff check backend`

Exit 0.

```text
All checks passed!
```

Command: `uv run --locked python --version`

Exit 0.

```text
Python 3.14.3
```

Command: `uv --version`

Exit 0.

```text
uv 0.10.9 (f675560f3 2026-03-06)
```

Command: `node --version`

Exit 0.

```text
v24.20.0
```

Command: `cmd /c npm.cmd --version`

Exit 0.

```text
11.19.0
```

Only deliberate T012 module is excluded from the separately labeled 477-test
regression; full suite was actually executed and has 480 passed / 4 failed.
Known Starlette/httpx warning retained. No environment failures in final runs.

## Scope/limits and next step
No SDK/provider calls, secret access, real producer/model integration, ingestion,
retrieval execution, worker/recovery, review workflow/UI or browser/evaluation run.
These are not prerequisites for fixture/storage primitives. Human review, real
producer review and model capability remain pending. No frontend modifications.
No technical blocker. Next: separately request phase 3 starting T013 source review;
T012 failures resolve only when later T019/T035 are authorized/implemented.
No commit/push/merge/deploy. No new task or future behavior implemented silently.

## Earlier RED paths
- phase2-red: not available
- context-red: not available
- store-red: D:\AIBootcamp\capstone\.cache\store-red-85452e719c7e4bd18eed48a0dd149fc2
- history-red: not available
- replay-red: D:\AIBootcamp\capstone\.cache\replay-red-157ed6f64f9b47e3ad870654d04f33d2
- privacy-red: not available
- tool-red: D:\AIBootcamp\capstone\.cache\tool-red-2c6e4e1c6a93450688abc27a54136517
All were uv run --locked pytest <target module> with --basetemp above and a paired unique absolute .cache test-cache/phase2-cache directory; --tb=short/no -q. Outcomes documented in the task evidence, no import/collection failures.

## Final review
Reviewed tracked diff and all new authored files, not only git diff --stat (which
shows two tracked files). New files: models/context/store modules; contract/context/
store/toggle tests; contexts/history authored fixtures; application prompt and retrieval
config; original phase-02 instruction; four task evidence records and this handoff.
No other preexisting local work at baseline. Saved prompt exact-text comparison True.
Git diff --exit-code HEAD confirms original cases, both lockfiles and both schemas
unchanged. Current original cases raw SHA256:
267eba2a2142f5a144268cd4df4fd902c71f92080dcfeeb002f21a50deddbdbf.
Pinned producer LF hash unchanged:
bf487d84ccac1e315d0e20fece0d2a7f45990bce954ba40bf97cd54e43929f88.
Source schemas are runtime validation assets for the new models; their local registry
resolves only the pinned resources, never downloads remote references.
Authored files normalized for encoding/line endings; re-ran three boundary modules:
uv run --locked pytest backend/tests/contracts/test_investigation_contracts.py
backend/tests/unit/test_investigation_context.py backend/tests/integration/test_investigation_store.py
--basetemp D:/AIBootcamp/capstone/.cache/final-5b08de5ede124dcc9d17f0cf099ec14a
-o cache_dir=D:/AIBootcamp/capstone/.cache/test-cache-5b08de5ede124dcc9d17f0cf099ec14a -q
Exit 0, 86 passed. Ruff exit 0. Final git diff --check and per-new-file
--no-index --check NUL passed. No after-implement hook configuration exists.
No live quality or human acceptance inferred from these results.


## Repeated-request verification - 2026-11-14
User resent the same phase-02 instruction; byte SHA256 of new attachment and saved
original both a5f94471e51b0668f8fedefcc80c06f8f7ec44dab30cd3839452ea5d04fb5b13.
No new scope or changed instruction. Branch feature03, current baseline
83b587bcc17f8ad703ea67ca593b3785d7fc4391, initially clean working tree.
Read AGENTS/next_work, compared existing implementation/task/evidence state.
Local speckit-implement applied only to re-verification of T005-T012; prerequisite
script exit 0, checklist 16/16, no hook config. No artificial RED or duplicate code.
Actual command:
uv run --locked pytest backend/tests --basetemp
D:/AIBootcamp/capstone/.cache/phase2-recheck-d369df8b58474c5087579a68c9d0edbe
-o cache_dir=D:/AIBootcamp/capstone/.cache/phase2-recheck-cache-d369df8b58474c5087579a68c9d0edbe
--tb=short -q
Result: pytest exit 1, 480 passed / 4 expected T012 failures, 1 known Starlette/httpx
warning. Same exact four node IDs/reasons as feature-003-api.md: two missing feature
envelopes, missing cross-origin 403 and JSON 422 guards, old routes give 404.
uv run --locked ruff check backend: exit 0. git diff --check: exit 0.
No source/test/fixture/config/schema/lockfile edits, no new provider/browser/evaluation
execution or human approval. Existing targeted counts remain historical; full suite
was freshly rerun. T005-T012 remain complete by task type; T012 intentionally RED.
Only this handoff and next_work updated. Next: separately authorize phase 3 T013;
no T013 or later work, commit/push/merge/deploy performed.
