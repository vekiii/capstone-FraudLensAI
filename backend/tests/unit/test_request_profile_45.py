"""Explicit45s drafting opt-in; legacy30 and total120 remain bounded."""

import asyncio

import httpx2
import pytest

from fraudlens.investigation.context import CaseContextReader, outbound_context
from fraudlens.investigation.models import SCHEMA
from fraudlens.investigation.provider import OpenAIProvider
from fraudlens.investigation.settings import InvestigationSettings
from fraudlens.investigation.tools import definitions


def test_request45_only_allowed_in_explicit_semantic_v7_profile():
    settings = InvestigationSettings(
        provider="openai",
        model="TEST",
        semantic_retrieval=True,
        semantic_profile="v7",
        request_timeout_seconds=45,
    )
    assert settings.request_timeout_seconds == 45
    assert settings.total_timeout_seconds == 120
    assert InvestigationSettings().request_timeout_seconds == 30
    with pytest.raises(ValueError):
        InvestigationSettings(request_timeout_seconds=31)
    with pytest.raises(ValueError):
        InvestigationSettings(
            provider="openai",
            model="TEST",
            semantic_retrieval=True,
            semantic_profile="v7",
            request_timeout_seconds=46,
        )


@pytest.mark.parametrize("explicit,expected", [(False, 30), (True, 45)])
def test_provider_cap_is_explicit_and_sdk_default_cannot_expand_it(explicit, expected):
    observed = []

    def handler(request):
        observed.append(request.extensions["timeout"])
        return httpx2.Response(
            200,
            json=dict(
                status="completed",
                model="TEST",
                output=[
                    dict(
                        type="function_call",
                        name="get_case_facts",
                        call_id="mock-call",
                        arguments="{}",
                    )
                ],
            ),
        )

    async def exercise():
        options = dict(request_timeout_cap=45) if explicit else {}
        provider = OpenAIProvider(
            "MOCK-ONLY", "TEST", transport=httpx2.MockTransport(handler), **options
        )
        context = CaseContextReader().resolve("CASE-001", "fixture", None)
        conversation = [dict(type="context", data=outbound_context(context, "inv_" + "a" * 32))]
        try:
            result = await provider.next_turn(
                conversation,
                definitions(),
                SCHEMA["$defs"]["ReportDraft"],
                dict(
                    request_timeout=100,
                    max_input_bytes=48000,
                    max_output_tokens=4096,
                    max_response_bytes=2097152,
                ),
            )
            assert result.kind == "tools"
        finally:
            await provider.aclose()

    asyncio.run(exercise())
    assert len(observed) == 1 and observed[0]["read"] == expected


def test_worker_factory_uses_frozen_profile_cap_even_when_current_settings_differ(
    tmp_path, monkeypatch
):
    from fraudlens.investigation.knowledge import KnowledgeStore
    from fraudlens.investigation.workflow import InvestigationService

    knowledge = KnowledgeStore(tmp_path / "test.sqlite")
    service = InvestigationService(knowledge.repository, knowledge)
    monkeypatch.setattr(
        "fraudlens.investigation.provider.OpenAIProvider", lambda *args, **kwargs: kwargs
    )
    binding = dict(
        provider_mode="openai",
        requested_model="TEST",
        prompt="",
        semantic_profile="v7",
        limits=dict(request_timeout_seconds=45),
    )
    assert service._provider(binding)["request_timeout_cap"] == 45
    binding.pop("semantic_profile")
    assert service._provider(binding).get("request_timeout_cap", 30) == 30
