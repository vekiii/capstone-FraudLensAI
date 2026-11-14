# T027-T030 offline provider and workflow

Baseline fece114 already contains the scripted provider, tools and bounded persisted
workflow. Its task markers/handoff lagged behind implementation. The existing
provider evidence records 15 intended RED -> GREEN cases. Workflow tests exercise
queued creation/GET without dispatch, all three actual permitted tools, durable
drafting, immutable configuration bindings, request/tool/deadline limits, one
transient retry, one repair, refusal, incomplete and invalid citation failures.

2026-11-14 continuation: existing provider + workflow tests, with the newly added
SDK/probe modules: **47 PASS**. Command: `.venv/Scripts/python.exe -m pytest
backend/tests/unit/test_investigation_openai.py
backend/tests/unit/test_investigation_probe.py
backend/tests/unit/test_investigation_provider.py
backend/tests/unit/test_investigation_workflow.py --basetemp <unique-cache>/tmp
-o cache_dir=<unique-cache>/cache -q --tb=short`. Ruff PASS.
First invocation had 33 PASS/14 setup errors because the parent temporary
directory did not exist. Creating that parent resolved setup; this was not RED.

Tests use an authored corpus and test provider, not live model or quality evidence.
Provider clients now close in workflow finally. Recovery enhancements remain Phase 5.

Saved original pytest caches recovered on disk: `.cache/003-workflow-red-
257df0730dca4a37b2e944c289878808/cache/v/cache/lastfailed` records 12 initial
workflow test failures (each current function except the later drafting test).
`.cache/003-drafting-red-00d174c1d96a414abc3ee0b28ba7846b/cache/v/cache/lastfailed`
records the additional durable-drafting failure. These corroborate previous RED
execution; the old console traceback is not reconstructed or invented. Current
13 workflow tests are GREEN in the final 629-test backend run. T029/T030 markers
now reflect saved code and this recovered evidence instead of stale next_work.
