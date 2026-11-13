# T012 intentional composition RED
Date 2026-11-14 Europe/Belgrade; started 2026-11-13. Branch feature03; baseline 6db94af3471a9007a8a0d88cba8c7ece32886483; initial tree clean.
Prompt: ../../prompts/development/003-investigation-phase-02.md. Human review pending.

T012 is completed as an executed RED task. No investigation routes, placeholder
production endpoints, xfail or skip added. Three existing foundation/no-network/CORS
checks pass. Four intended assertion failures:
- test_new_errors_are_feature_specific[/api/knowledge/search?q=test-knowledge_unavailable]
- test_new_errors_are_feature_specific[/api/investigation/attempts/att_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-investigation_not_found]
  Both get old unversioned foundation case_not_found envelope (404), not versioned
  feature errors. Knowledge composition resolves in T019; run route in T035.
- test_cross_origin_mutation_rejected: old 404 instead of forbidden_scope HTTP 403.
- test_mutation_requires_json: old 404 instead of invalid_request HTTP 422.
  Mutation routes/guards are future T035; no implementation in this phase.

Command: `uv run --locked pytest backend/tests/integration/test_investigation_feature_toggle.py --basetemp D:\AIBootcamp\capstone\.cache\003-p2-06ec776227804c2798e784f9125d66bc -o cache_dir=D:\AIBootcamp\capstone\.cache\003-p2-cache-06ec776227804c2798e784f9125d66bc --tb=short -q`

Exit 1.

```text
..FFFF.                                                                  [100%]
================================== FAILURES ===================================
_ test_new_errors_are_feature_specific[/api/knowledge/search?q=test-knowledge_unavailable] _
backend\tests\integration\test_investigation_feature_toggle.py:46: in test_new_errors_are_feature_specific
    assert response.json().get('contract_version') == 1
E   AssertionError: assert None == 1
E    +  where None = <built-in method get of dict object at 0x000002845B4C0200>('contract_version')
E    +    where <built-in method get of dict object at 0x000002845B4C0200> = {'error': {'code': 'case_not_found', 'message': 'Case not found.'}}.get
E    +      where {'error': {'code': 'case_not_found', 'message': 'Case not found.'}} = json()
E    +        where json = <Response [404 Not Found]>.json
_ test_new_errors_are_feature_specific[/api/investigation/attempts/att_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-investigation_not_found] _
backend\tests\integration\test_investigation_feature_toggle.py:46: in test_new_errors_are_feature_specific
    assert response.json().get('contract_version') == 1
E   AssertionError: assert None == 1
E    +  where None = <built-in method get of dict object at 0x000002845B507C40>('contract_version')
E    +    where <built-in method get of dict object at 0x000002845B507C40> = {'error': {'code': 'case_not_found', 'message': 'Case not found.'}}.get
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
4 failed, 3 passed, 1 warning in 0.67s
```

Full-suite expected RED is recorded in phase-02 handoff. It is not GREEN.
