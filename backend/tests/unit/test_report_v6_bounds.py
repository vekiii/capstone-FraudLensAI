import asyncio
import json

import httpx2
import pytest
from test_investigation_openai import LIMITS, messages, response
from test_investigation_workflow import create, runtime  # noqa: F401

from fraudlens.investigation import provider as provider_module
from fraudlens.investigation.models import SCHEMA
from fraudlens.investigation.provider import OpenAIProvider, ProviderError, ScriptedProvider
from fraudlens.investigation.settings import InvestigationSettings
from fraudlens.investigation.tools import definitions


def settings(**kwargs):
    return InvestigationSettings(
        provider="openai",
        model="mock",
        api_key="MOCK",
        semantic_retrieval=True,
        semantic_profile="v8",
        report_prompt="v6",
        **kwargs,
    )


def test_explicit_8192_profile_and_old_defaults():
    assert settings(max_output_tokens=8192).max_output_tokens == 8192
    assert InvestigationSettings().max_output_tokens == 4096
    for prompt in ("v4", "v5"):
        with pytest.raises(ValueError):
            InvestigationSettings(
                provider="openai",
                model="mock",
                semantic_retrieval=True,
                semantic_profile="v8",
                report_prompt=prompt,
                max_output_tokens=8192,
            )
    with pytest.raises(ValueError):
        settings(max_output_tokens=8193)


def test_factories_use_saved_output_cap(runtime, monkeypatch):  # noqa: F811
    from fraudlens.investigation.acceptance_harness import DispatchLedger, build_service
    from fraudlens.investigation.context import CaseContextReader

    knowledge, request, make = runtime
    chosen = settings(max_output_tokens=8192, request_timeout_seconds=45)
    service = make(settings=chosen)
    view = create(service, request)
    binding = service.binding(view["attempt_id"])
    assert binding["limits"]["max_output_tokens"] == 8192
    assert binding["history_bounds_version"] == 1
    captured = []

    def fake(*args, **kwargs):
        captured.append(kwargs)
        return object()

    monkeypatch.setattr("fraudlens.investigation.provider.OpenAIProvider", fake)
    service.settings = InvestigationSettings()
    service._provider(binding)
    assert captured[-1]["output_token_cap"] == 8192
    assert captured[-1]["request_timeout_cap"] == 45
    context = CaseContextReader().resolve("CASE-001", "fixture", None)
    item = dict(
        id="test",
        language="sr-Latn",
        instruction="Review evidence",
        context=context,
        history_fixture=dict(events=[], accounts={}),
        procedure_queries=["Missing facts"],
    )
    ledger = DispatchLedger(knowledge.repository.path.parent / "ledger.sqlite", 8, "mock")
    other = build_service(knowledge, [item], chosen, ledger=ledger)
    other.provider_factory(binding)
    assert captured[-1]["output_token_cap"] == 8192


def test_latency_profile_requires_explicit_v6_and_wires_low_reasoning():
    chosen = settings(request_timeout_seconds=60, report_reasoning_effort="low")
    assert chosen.request_timeout_seconds == 60
    with pytest.raises(ValueError):
        InvestigationSettings(report_reasoning_effort="low")
    requests = []

    def handler(request):
        requests.append(json.loads(request.content))
        return httpx2.Response(
            200,
            json=response(
                output=[
                    dict(
                        type="function_call", call_id="call1", name="get_case_facts", arguments="{}"
                    )
                ]
            ),
        )

    async def exercise():
        provider = OpenAIProvider(
            "MOCK",
            "mock",
            transport=httpx2.MockTransport(handler),
            request_timeout_cap=60,
            reasoning_effort="low",
        )
        try:
            await provider.next_turn(
                messages(), definitions(), SCHEMA["$defs"]["ReportDraft"], LIMITS
            )
        finally:
            await provider.aclose()

    asyncio.run(exercise())
    assert requests[0]["reasoning"] == {"effort": "low"}


def test_compiled_report_requires_claims_when_case_evidence_is_available():
    legacy = provider_module.compile_report_schema()["properties"]
    detailed = provider_module.compile_report_schema(require_case_sections=True)["properties"]
    for section in ("summary", "observed_facts", "citations"):
        assert "minItems" not in legacy[section]
        assert detailed[section]["minItems"] == 1


def test_parallel_history_profile_keeps_existing_tool_arguments():
    assert settings(report_parallel_tools=True).report_parallel_tools is True
    with pytest.raises(ValueError):
        InvestigationSettings(report_parallel_tools=True)
    seen = []

    def handler(request):
        seen.append(json.loads(request.content))
        return httpx2.Response(
            200,
            json=response(
                output=[
                    dict(
                        type="function_call",
                        call_id=f"call_{side}",
                        name="get_account_history",
                        arguments=json.dumps(dict(account_side=side)),
                    )
                    for side in ("sender", "receiver")
                ]
            ),
        )

    async def exercise():
        provider = OpenAIProvider(
            "MOCK", "mock", transport=httpx2.MockTransport(handler), parallel_tools=True
        )
        try:
            return await provider.next_turn(
                messages(), definitions(), SCHEMA["$defs"]["ReportDraft"], LIMITS
            )
        finally:
            await provider.aclose()

    assert [c["arguments"]["account_side"] for c in asyncio.run(exercise()).calls] == [
        "sender",
        "receiver",
    ]
    assert seen[0]["parallel_tool_calls"] is True
    assert seen[0]["tools"] == definitions()


@pytest.mark.parametrize("cap,allowed", [(8192, True), (4096, False)])
def test_sdk_cap_is_explicit_and_transmitted(cap, allowed):
    sent = []

    def handler(request):
        sent.append(json.loads(request.content))
        return httpx2.Response(
            200,
            json=response(
                output=[
                    dict(
                        type="function_call", call_id="call1", name="get_case_facts", arguments="{}"
                    )
                ]
            ),
        )

    async def exercise():
        provider = OpenAIProvider(
            "MOCK", "mock", transport=httpx2.MockTransport(handler), output_token_cap=cap
        )
        try:
            return await provider.next_turn(
                messages(),
                definitions(),
                SCHEMA["$defs"]["ReportDraft"],
                {**LIMITS, "max_output_tokens": 8192},
            )
        finally:
            await provider.aclose()

    if allowed:
        assert asyncio.run(exercise()).kind == "tools"
        assert sent[0]["max_output_tokens"] == 8192
    else:
        with pytest.raises(ProviderError):
            asyncio.run(exercise())
        assert not sent


def test_legacy_history_projection_is_unchanged(runtime):  # noqa: F811
    _, request, make = runtime
    service = make()
    view = create(service, request)
    assert "history_bounds_version" not in service.binding(view["attempt_id"])
    asyncio.run(service.work_once())
    for item in service.evidence(view["attempt_id"]):
        if item["kind"] == "history":
            assert "window_end_exclusive" not in json.loads(item["text"])


@pytest.mark.parametrize("scenario,available", [("grounded", True), ("needs_information", False)])
def test_worker_delivers_computed_bounds_and_retry_pins(runtime, scenario, available):  # noqa: F811
    _, request, make = runtime
    provider = ScriptedProvider("needs_information")
    service = make(provider=provider, settings=InvestigationSettings(report_prompt="v6"))
    if available:
        # Use actual default fixture history reader when available; select an explicit reader
        # whose cutoff has seconds, so the bound cannot merely echo cutoff.
        class Reader:
            def read(self, context, side, limit):
                return dict(
                    availability="available",
                    coverage="incomplete",
                    cutoff="2026-01-05T09:18:43Z",
                    start="2025-12-29T09:18:43Z",
                    lookback_days=7,
                    events=[],
                    totals={},
                    returned_count=0,
                    eligible_count=0,
                    truncated=False,
                )

        service.history_reader = Reader()
    view = create(service, request)
    binding = service.binding(view["attempt_id"])
    assert binding["history_bounds_version"] == 1
    result = asyncio.run(service.work_once())
    history = [e for e in service.evidence(view["attempt_id"]) if e["kind"] == "history"]
    assert history
    for e in history:
        body = json.loads(e["text"])
        assert body["window_end_exclusive"] == ("2026-01-05T09:18:00Z" if available else None)
        assert body["window_start_inclusive"] == ("2025-12-29T09:18:43Z" if available else None)
        fact = {f["path"]: f["value"] for f in e["facts"]}
        if available:
            assert fact["window_end_exclusive"] == "2026-01-05T09:18:00Z"
    assert result["state"] in ("ready_for_review", "needs_information")
    service.settings = InvestigationSettings()
    child = service.retry(
        result["attempt_id"],
        result["revision"],
        True,
        "analyst",
        __import__("uuid").uuid4().__str__(),
    )
    assert service.binding(child["attempt_id"])["history_bounds_version"] == 1
    assert service.binding(child["attempt_id"])["prompt"] == binding["prompt"]
