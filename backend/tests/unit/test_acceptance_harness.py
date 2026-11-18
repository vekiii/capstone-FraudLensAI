import asyncio
import json

import pytest

from fraudlens.investigation.acceptance_harness import (
    DispatchLedger,
    MaterializedReader,
    build_service,
    metered_transport,
    require_authorization,
)
from fraudlens.investigation.models import ROOT


def inputs():
    return json.loads(
        (ROOT / "evals/investigation/acceptance-v1-20261118/inputs/timing.json").read_text(
            encoding="utf-8"
        )
    )


def test_reader_binds_exact_new_context_and_rejects_switches():
    rows = inputs()
    reader = MaterializedReader(rows)
    context = rows[0]["context"]
    assert reader.resolve(context["case_id"], "fixture", context["snapshot_ref"]) == context
    for case, mode, snapshot in [
        ("CASE-001", "fixture", None),
        (context["case_id"], "dataset", None),
        (context["case_id"], "fixture", "fixture_" + "f" * 64),
    ]:
        with pytest.raises(ValueError):
            reader.resolve(case, mode, snapshot)


def test_reader_rejects_private_fields_before_any_runtime_use():
    rows = inputs()
    rows[1]["essential_facts"] = ["PRIVATE"]
    with pytest.raises(ValueError, match="Input-only"):
        MaterializedReader(rows)


def test_histories_route_per_case_and_preserve_unavailable():
    rows = inputs()
    reader = MaterializedReader(rows)
    assert reader.read(rows[0]["context"], "sender")["eligible_count"] == 2
    assert reader.read(rows[0]["context"], "receiver")["eligible_count"] == 1
    assert reader.read(rows[1]["context"], "sender")["availability"] == "unavailable"
    assert reader.read(rows[2]["context"], "sender")["totals"] == {"GBP": "83.47", "USD": "29.61"}


def test_persistent_transport_budget_is_not_reset_by_new_instance(tmp_path):
    path = tmp_path / "dispatch.sqlite"
    ledger = DispatchLedger(path, 2, "reviewed-model")
    assert ledger.reserve(b'{"model":"reviewed-model"}') == 1
    ledger.complete(1, dict(status=200))
    assert DispatchLedger(path, 2, "reviewed-model").reserve(b'{"model":"reviewed-model"}') == 2
    ledger.complete(2, dict(status=200))
    with pytest.raises(ValueError, match="exhausted"):
        DispatchLedger(path, 2, "reviewed-model").reserve(b'{"model":"reviewed-model"}')


def test_frozen_model_and_cap_cannot_be_reset(tmp_path):
    path = tmp_path / "dispatch.sqlite"
    DispatchLedger(path, 2, "reviewed-model")
    for cap, model in [(3, "reviewed-model"), (2, "replacement")]:
        with pytest.raises(ValueError, match="changed"):
            DispatchLedger(path, cap, model)


def test_foreign_model_and_private_gold_blocked_before_transport(tmp_path):
    ledger = DispatchLedger(tmp_path / "dispatch.sqlite", 2, "reviewed-model")
    for body in [b'{"model":"other"}', b'{"model":"reviewed-model","essential_facts":["PRIVATE"]}']:
        with pytest.raises(ValueError):
            ledger.reserve(body)
    assert ledger.reserve(b'{"model":"reviewed-model"}') == 1


def test_unknown_dispatch_preserved_and_blocks_later_dispatches(tmp_path):
    ledger = DispatchLedger(tmp_path / "dispatch.sqlite", 2, "reviewed-model")
    ledger.reserve(b'{"model":"reviewed-model"}')
    with pytest.raises(ValueError, match="unknown"):
        ledger.reserve(b'{"model":"reviewed-model"}')


def test_completed_dispatch_allows_next_but_access_failure_stops(tmp_path):
    ledger = DispatchLedger(tmp_path / "dispatch.sqlite", 3, "reviewed-model")
    seq = ledger.reserve(b'{"model":"reviewed-model"}')
    ledger.complete(seq, dict(status=200, usage={"total_tokens": 7}))
    seq = ledger.reserve(b'{"model":"reviewed-model"}')
    ledger.complete(seq, dict(status=403))
    with pytest.raises(ValueError, match="stopped"):
        ledger.reserve(b'{"model":"reviewed-model"}')


def test_meter_archives_real_transport_bytes_usage_but_never_headers(tmp_path):
    import httpx2

    ledger = DispatchLedger(tmp_path / "dispatch.sqlite", 2, "reviewed-model")
    calls = []

    def handler(request):
        calls.append(request)
        return httpx2.Response(
            200,
            json=dict(output=[], usage={"total_tokens": 9}),
            headers={"x-request-id": "public-request-id"},
        )

    async def exercise():
        async with httpx2.AsyncClient(
            transport=metered_transport(ledger, httpx2.MockTransport(handler))
        ) as client:
            response = await client.post(
                "https://provider.invalid/v1/responses",
                headers={"Authorization": "Bearer SECRET"},
                json={"model": "reviewed-model"},
            )
            assert response.json()["usage"]["total_tokens"] == 9

    asyncio.run(exercise())
    with ledger.connection() as db:
        rows = db.execute("SELECT request,result FROM dispatches").fetchall()
    assert len(calls) == len(rows) == 1
    assert "SECRET" not in str(rows)
    assert json.loads(rows[0][1])["usage"]["total_tokens"] == 9


def test_transport_timeout_preserves_unknown_and_prevents_retry(tmp_path):
    import httpx2

    ledger = DispatchLedger(tmp_path / "dispatch.sqlite", 2, "reviewed-model")
    calls = []

    def handler(request):
        calls.append(request)
        raise httpx2.ReadTimeout("private transport error")

    async def exercise():
        async with httpx2.AsyncClient(
            transport=metered_transport(ledger, httpx2.MockTransport(handler))
        ) as client:
            with pytest.raises(httpx2.ReadTimeout):
                await client.post("https://provider.invalid", json={"model": "reviewed-model"})
            with pytest.raises(ValueError, match="unknown"):
                await client.post("https://provider.invalid", json={"model": "reviewed-model"})

    asyncio.run(exercise())
    assert len(calls) == 1


def test_quota_failure_is_preserved_and_blocks_remaining_budget(tmp_path):
    ledger = DispatchLedger(tmp_path / "dispatch.sqlite", 2, "reviewed-model")
    seq = ledger.reserve(b'{"model":"reviewed-model"}')
    ledger.complete(seq, dict(status=429, response_json={"error": {"code": "insufficient_quota"}}))
    with pytest.raises(ValueError, match="stopped"):
        ledger.reserve(b'{"model":"reviewed-model"}')


def test_completed_result_cannot_be_replaced(tmp_path):
    ledger = DispatchLedger(tmp_path / "dispatch.sqlite", 2, "reviewed-model")
    seq = ledger.reserve(b'{"model":"reviewed-model"}')
    ledger.complete(seq, dict(status=403))
    with pytest.raises(ValueError, match="already completed"):
        ledger.complete(seq, dict(status=200))


@pytest.mark.parametrize("mutation", ["missing", "false", "wrong_hash", "wrong_cap", "bool_cap"])
def test_authorization_fail_closed_before_any_provider_initialization(tmp_path, mutation):
    import hashlib

    freeze_path = tmp_path / "freeze.json"
    freeze_path.write_text(
        json.dumps(
            dict(
                batch_directory=str(tmp_path.resolve()),
                stage="development",
                maximum_requests=32,
                model="reviewed-model",
                files_sha256={},
            )
        )
    )
    approval = dict(
        approved=True,
        freeze_sha256=hashlib.sha256(freeze_path.read_bytes()).hexdigest(),
        stage="development",
        maximum_requests=32,
        model="reviewed-model",
        user_authorization="TEST FIXTURE ONLY, not real user approval",
    )
    path = tmp_path / "approval.json"
    if mutation == "missing":
        with pytest.raises(FileNotFoundError):
            require_authorization(path, freeze_path)
        return
    if mutation == "false":
        approval["approved"] = False
    elif mutation == "wrong_hash":
        approval["freeze_sha256"] = "0" * 64
    elif mutation == "wrong_cap":
        approval["maximum_requests"] = 155
    else:
        approval["maximum_requests"] = True
    path.write_text(json.dumps(approval))
    with pytest.raises(ValueError, match="approval"):
        require_authorization(path, freeze_path)


def test_build_service_blocks_unmetered_openai_and_never_uses_default_fixture_rows(tmp_path):
    from fraudlens.investigation.knowledge import KnowledgeStore
    from fraudlens.investigation.settings import InvestigationSettings

    knowledge = KnowledgeStore(tmp_path / "runs.sqlite")
    settings = InvestigationSettings(enabled=True, provider="openai", model="reviewed-model")
    with pytest.raises(ValueError, match="metered"):
        build_service(knowledge, inputs(), settings)
    test_settings = InvestigationSettings(
        enabled=True, provider="test", store=tmp_path / "runs.sqlite"
    )
    service = build_service(knowledge, inputs(), test_settings)
    assert service.context_reader.resolve("CASE-931", "fixture", None) == inputs()[0]["context"]
    with pytest.raises(ValueError):
        service.context_reader.resolve("CASE-001", "fixture", None)


def test_hash_bound_approval_accepts_exact_source_then_blocks_change_and_clone(tmp_path):
    import hashlib

    source = tmp_path / "source.txt"
    source.write_text("frozen")
    freeze_path = tmp_path / "freeze.json"
    freeze_path.write_text(
        json.dumps(
            dict(
                batch_directory=str(tmp_path.resolve()),
                stage="development",
                maximum_requests=32,
                model="reviewed-model",
                files_sha256={str(source): hashlib.sha256(source.read_bytes()).hexdigest()},
            )
        )
    )
    approval_path = tmp_path / "approval.json"
    approval_path.write_text(
        json.dumps(
            dict(
                approved=True,
                freeze_sha256=hashlib.sha256(freeze_path.read_bytes()).hexdigest(),
                stage="development",
                maximum_requests=32,
                model="reviewed-model",
                user_authorization="TEST FIXTURE ONLY, not real user consent",
            )
        )
    )
    assert require_authorization(approval_path, freeze_path)["maximum_requests"] == 32
    copied = tmp_path / "cloned"
    copied.mkdir()
    (copied / "freeze.json").write_bytes(freeze_path.read_bytes())
    with pytest.raises(ValueError, match="approval"):
        require_authorization(approval_path, copied / "freeze.json")
    source.write_text("changed")
    with pytest.raises(ValueError, match="source changed"):
        require_authorization(approval_path, freeze_path)
