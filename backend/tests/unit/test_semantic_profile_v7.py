"""Opt-in formatting profile; strict source semantics and old identities preserved."""

import asyncio
import json
from types import SimpleNamespace
from uuid import uuid4

import pytest

from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import ROOT
from fraudlens.investigation.retrieval_semantic_v6 import policy_identity, request_payload
from fraudlens.investigation.settings import InvestigationSettings


def source():
    return dict(
        passage_id="p1",
        text="Preserve exact evidence.\nUnknown facts stay unknown.",
        document=dict(title="Test", jurisdiction="SIMULATED", version="test", published_at=None),
    )


def test_frozen_v6_policy_identity_and_payload_remain_unchanged(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.sqlite")
    corpus = store.publish(ROOT / "data/knowledge/fraudlens-aml-knowledge-v1/manifest.json")
    expected = json.loads(
        (ROOT / "evals/investigation/acceptance-v1-20261118/protocol.json").read_text()
    )
    assert policy_identity("gpt-6-luna", store.passages(corpus)) == expected["semantic_policy"]
    assert request_payload("What evidence?", [source()], "test")["instructions"] == (
        ROOT / "prompts/application/retrieval-answerability-v6.md"
    ).read_text(encoding="utf-8")


def test_v7_profile_is_explicit_bound_and_does_not_change_schema_or_limits():
    old = request_payload("What evidence?", [source()], "test")
    new = request_payload("What evidence?", [source()], "test", profile="v7")
    assert old["text"] == new["text"] and old["input"] == new["input"]
    assert new["max_output_tokens"] == 2048 and new["store"] is False
    assert "Select each passage_id at most once" in new["instructions"]
    assert policy_identity("test", [source()], profile="v7") != policy_identity("test", [source()])


@pytest.mark.parametrize("profile", ["auto", "latest", False])
def test_unknown_profile_rejected_before_provider(profile):
    with pytest.raises(ValueError):
        request_payload("What evidence?", [source()], "test", profile=profile)


def test_setting_reads_explicit_environment_profile_without_changing_default(monkeypatch):
    from fraudlens.investigation.settings import load_settings

    assert InvestigationSettings().semantic_profile == "v6"
    monkeypatch.setenv("INVESTIGATION_SEMANTIC_PROFILE", "v7")
    monkeypatch.setenv("INVESTIGATION_PROVIDER", "openai")
    monkeypatch.setenv("INVESTIGATION_SEMANTIC_RETRIEVAL", "true")
    monkeypatch.setenv("OPENAI_MODEL", "synthetic-model")
    assert load_settings().semantic_profile == "v7"


def test_audited_v7_payload_is_used_and_bad_quotes_still_fail_without_retry():
    from fraudlens.investigation.semantic_response_audit import audited_selection

    calls, saved = [], []

    async def create(**payload):
        calls.append(payload)
        value = dict(
            status="completed",
            output=[
                dict(
                    type="message",
                    content=[
                        dict(
                            type="output_text",
                            text=json.dumps(
                                dict(
                                    verdict="supported",
                                    reason="test",
                                    selected=[dict(passage_id="p1", quote="Invented quote")],
                                )
                            ),
                        )
                    ],
                )
            ],
        )
        return SimpleNamespace(model_dump=lambda **kwargs: value)

    provider = SimpleNamespace(
        model="test", client=SimpleNamespace(responses=SimpleNamespace(create=create))
    )
    with pytest.raises(ValueError, match="selection"):
        asyncio.run(
            audited_selection(provider, "What evidence?", [source()], saved.append, profile="v7")
        )
    assert len(calls) == len(saved) == 1
    assert "Select each passage_id at most once" in calls[0]["instructions"]


def test_worker_pins_profile_and_retry_inherits_it(tmp_path, knowledge_factory, monkeypatch):
    from fraudlens.investigation.context import CaseContextReader
    from fraudlens.investigation.provider import ScriptedProvider
    from fraudlens.investigation.workflow import InvestigationService

    store = KnowledgeStore(tmp_path / "worker.sqlite")
    store.publish(knowledge_factory("missing evidence money"))
    store.save_configuration(
        json.loads((ROOT / "data/knowledge/fraudlens-aml-knowledge-v1/retrieval.json").read_text())
    )
    settings = InvestigationSettings(
        semantic_retrieval=True,
        semantic_profile="v7",
        provider="openai",
        model="test-model",
        api_key="TEST-ONLY",
    )
    profiles = []

    async def select(provider, query, passages, capture, **kwargs):
        profiles.append(kwargs.get("profile", "v6"))
        return dict(verdict="insufficient", reason="No guidance", selected=[]), dict(
            returned_model="test-model"
        )

    monkeypatch.setattr("fraudlens.investigation.semantic_response_audit.audited_selection", select)
    provider = ScriptedProvider("needs_information")
    provider.model = "test-model"
    service = InvestigationService(
        store.repository, store, settings, provider_factory=lambda binding: provider
    )
    context = CaseContextReader().resolve("CASE-001", "fixture", None)
    request = {k: context[k] for k in ("case_id", "source_mode", "snapshot_ref")}
    created = service.create(request, "analyst", str(uuid4()))
    assert service.binding(created["attempt_id"])["semantic_profile"] == "v7"
    result = asyncio.run(service.work_once())
    assert result["state"] in ("ready_for_review", "needs_information") and profiles == ["v7"]
    service.settings = settings.model_copy(update=dict(semantic_profile="v6"))
    child = service.retry(result["attempt_id"], result["revision"], False, "analyst", str(uuid4()))
    assert service.binding(child["attempt_id"])["semantic_profile"] == "v7"


def test_standalone_search_uses_v7_policy_but_status_never_redispatches(
    tmp_path, knowledge_factory, monkeypatch
):
    from fraudlens.investigation.semantic_runtime import SemanticSearchService

    store = KnowledgeStore(tmp_path / "standalone.sqlite")
    corpus = store.publish(knowledge_factory("missing evidence"))
    settings = InvestigationSettings(
        enabled=True,
        semantic_retrieval=True,
        semantic_profile="v7",
        provider="openai",
        model="test-model",
        api_key="TEST-ONLY",
    )
    profiles = []

    async def select(provider, query, passages, capture, **kwargs):
        profiles.append(kwargs.get("profile", "v6"))
        return dict(verdict="insufficient", reason="No guidance", selected=[]), dict(
            returned_model="test-model"
        )

    monkeypatch.setattr("fraudlens.investigation.semantic_response_audit.audited_selection", select)
    service = SemanticSearchService(
        store, settings, provider_factory=lambda: SimpleNamespace(model="test-model")
    )
    first = asyncio.run(service.search("What evidence?", "request-1"))
    assert first["status"] == "completed" and profiles == ["v7"]
    assert first["retrieval_version"] == policy_identity(
        "test-model", store.passages(corpus), profile="v7"
    )
    assert service.status("request-1") == first and profiles == ["v7"]
