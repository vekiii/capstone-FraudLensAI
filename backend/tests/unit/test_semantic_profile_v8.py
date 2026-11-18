"""Future opt-in source-map/report-v5 integration; mocks, not live acceptance."""

import asyncio
import json
from types import SimpleNamespace
from uuid import uuid4

from fraudlens.investigation.models import ROOT
from fraudlens.investigation.retrieval_semantic_v6 import policy_identity, request_payload
from fraudlens.investigation.settings import InvestigationSettings


def source():
    return dict(
        passage_id="p1",
        text="Exact source.\nDo not alter whitespace. ",
        document=dict(title="Test", jurisdiction="SIMULATED", version="test", published_at=None),
    )


def test_v8_request_has_closed_source_keys_and_no_model_quote_field():
    payload = request_payload("What evidence?", [source()], "test", profile="v8")
    schema = payload["text"]["format"]["schema"]
    assert payload["text"]["format"]["name"] == "answerability_v8"
    assert set(schema["properties"]["source_ranks"]["properties"]) == {"p1"}
    assert "selected" not in schema["properties"]
    assert policy_identity("test", [source()], profile="v8") != policy_identity("test", [source()])


def test_v8_port_copies_authoritative_text_and_preserves_raw_rank_response():
    from fraudlens.investigation.semantic_response_audit import audited_selection

    sent, captured = [], []

    async def create(**kwargs):
        sent.append(kwargs)
        raw = dict(
            status="completed",
            model="test",
            output=[
                dict(
                    type="message",
                    content=[
                        dict(
                            type="output_text",
                            text=json.dumps(
                                dict(verdict="supported", reason="source", source_ranks={"p1": 1})
                            ),
                        )
                    ],
                )
            ],
        )
        return SimpleNamespace(model_dump=lambda **kwargs: raw)

    provider = SimpleNamespace(
        model="test", client=SimpleNamespace(responses=SimpleNamespace(create=create))
    )
    selection, _ = asyncio.run(
        audited_selection(provider, "What evidence?", [source()], captured.append, profile="v8")
    )
    assert selection["selected"] == [dict(passage_id="p1", quote=source()["text"])]
    assert len(sent) == len(captured) == 1
    assert "source_ranks" in captured[0]["output"][0]["content"][0]["text"]


def test_report_v5_and_v8_cap_are_explicit_defaults_remain_v4_v6_30():
    settings = InvestigationSettings(
        provider="openai",
        model="test",
        semantic_retrieval=True,
        semantic_profile="v8",
        report_prompt="v5",
        request_timeout_seconds=45,
    )
    assert settings.report_prompt == "v5" and settings.request_timeout_seconds == 45
    old = InvestigationSettings()
    assert (old.report_prompt, old.semantic_profile, old.request_timeout_seconds) == (
        "v4",
        "v6",
        30,
    )


def test_worker_binds_v5_and_v8_and_keeps_total_deadline(tmp_path, knowledge_factory, monkeypatch):
    from fraudlens.investigation.context import CaseContextReader
    from fraudlens.investigation.knowledge import KnowledgeStore
    from fraudlens.investigation.provider import ScriptedProvider
    from fraudlens.investigation.workflow import InvestigationService

    store = KnowledgeStore(tmp_path / "test.sqlite")
    store.publish(knowledge_factory("missing evidence"))
    store.save_configuration(
        json.loads((ROOT / "data/knowledge/fraudlens-aml-knowledge-v1/retrieval.json").read_text())
    )
    settings = InvestigationSettings(
        provider="openai",
        api_key="MOCK",
        model="test",
        semantic_retrieval=True,
        semantic_profile="v8",
        report_prompt="v5",
        request_timeout_seconds=45,
    )
    profiles = []

    async def select(provider, query, passages, capture, **kwargs):
        profiles.append(kwargs["profile"])
        return dict(verdict="insufficient", reason="No evidence", selected=[]), dict(
            returned_model="test"
        )

    monkeypatch.setattr("fraudlens.investigation.semantic_response_audit.audited_selection", select)
    provider = ScriptedProvider("needs_information")
    provider.model = "test"
    service = InvestigationService(
        store.repository, store, settings, provider_factory=lambda binding: provider
    )
    context = CaseContextReader().resolve("CASE-001", "fixture", None)
    view = service.create(
        {k: context[k] for k in ("case_id", "source_mode", "snapshot_ref")}, "analyst", str(uuid4())
    )
    binding = service.binding(view["attempt_id"])
    assert "Investigation application prompt v5" in binding["prompt"]
    assert binding["limits"]["request_timeout_seconds"] == 45
    assert binding["limits"]["total_timeout_seconds"] == 120
    result = asyncio.run(service.work_once())
    assert result["state"] == "needs_information" and profiles == ["v8"]
    service.settings = settings.model_copy(
        update=dict(semantic_profile="v6", report_prompt="v4", request_timeout_seconds=30)
    )
    child = service.retry(result["attempt_id"], result["revision"], False, "analyst", str(uuid4()))
    child_binding = service.binding(child["attempt_id"])
    assert child_binding["semantic_profile"] == "v8"
    assert child_binding["prompt"] == binding["prompt"]
    assert child_binding["limits"]["request_timeout_seconds"] == 45


def test_source_snapshot_explains_real_history_filter_policy():
    # Fixed public implementation policy, not a case-specific expected missing list.
    import importlib.util

    path = ROOT / "evidence/tasks/feature-003-materialize-quality-v2-20261118.py"
    spec = importlib.util.spec_from_file_location("materializer_future_source_policy", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert "focal minute" in module.HISTORY_POLICY and "inclusive" in module.HISTORY_POLICY
