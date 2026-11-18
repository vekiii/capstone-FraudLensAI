"""Mock-only integration of the opt-in judge harness, never live calibration."""

import asyncio
import copy
import hashlib
import importlib.util
import json
from types import SimpleNamespace

import httpx2
import pytest
from pydantic import SecretStr

from fraudlens.investigation.acceptance_harness import DispatchLedger, metered_transport
from fraudlens.investigation.judging_v4 import project_packet
from fraudlens.investigation.models import ROOT


def fixture_run(tmp_path, monkeypatch, *, quota=False, invalid=False, strict_wire=False):
    path = ROOT / "evidence/tasks/feature-003-t101-judge-live-20261118.py"
    spec = importlib.util.spec_from_file_location("test_only_acceptance_judge_driver", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    control_root = ROOT / "evals/investigation/report-quality-v4"
    controls = json.loads((control_root / "inputs/controls.json").read_text())
    authored = json.loads((control_root / "reference/authored-ratings.json").read_text())
    packets = [project_packet(p) for p in controls]
    (tmp_path / "packets.json").write_text(json.dumps(packets))
    freeze = dict(
        batch_directory=str(tmp_path.resolve()),
        stage="calibration",
        maximum_requests=6,
        model="MOCK-only-model",
        packet_order=[p["packet_id"] for p in packets],
        files_sha256={},
    )
    frozen = tmp_path / "freeze.json"
    frozen.write_text(json.dumps(freeze))
    approval = tmp_path / "approval.json"
    approval.write_text(
        json.dumps(
            dict(
                approved=True,
                stage="calibration",
                maximum_requests=6,
                model="MOCK-only-model",
                freeze_sha256=hashlib.sha256(frozen.read_bytes()).hexdigest(),
                user_authorization="TEST FIXTURE ONLY; not actual user approval",
            )
        )
    )
    monkeypatch.setattr(
        module,
        "load_settings",
        lambda: SimpleNamespace(
            api_key=SecretStr("MOCK-KEY-NO-NETWORK"), model=SecretStr("MOCK-only-model")
        ),
    )
    sent = []

    def handler(request):
        body = json.loads(request.content)
        packet = json.loads(body["input"])
        sent.append(body)
        if strict_wire:

            def unsupported(node):
                if isinstance(node, dict):
                    return "uniqueItems" in node or any(unsupported(v) for v in node.values())
                if isinstance(node, list):
                    return any(unsupported(v) for v in node)
                return False

            if unsupported(body["text"]["format"]["schema"]):
                return httpx2.Response(
                    400,
                    json={
                        "error": {
                            "message": "uniqueItems is not permitted",
                            "type": "invalid_request_error",
                            "code": "invalid_json_schema",
                        }
                    },
                )
        if quota:
            return httpx2.Response(
                429,
                json={
                    "error": {
                        "message": "Mock quota",
                        "type": "insufficient_quota",
                        "code": "insufficient_quota",
                    }
                },
            )
        rating = copy.deepcopy(authored[len(sent) - 1])
        rating["packet_id"] = "0" * 64 if invalid else packet["packet_id"]
        return httpx2.Response(
            200,
            json=dict(
                id="resp_mock",
                object="response",
                status="completed",
                model="MOCK-only-model",
                output=[
                    dict(
                        id="msg_mock",
                        type="message",
                        role="assistant",
                        status="completed",
                        content=[dict(type="output_text", text=json.dumps(rating), annotations=[])],
                    )
                ],
                usage=dict(input_tokens=1, output_tokens=1, total_tokens=2),
            ),
        )

    monkeypatch.setattr(
        module,
        "metered_transport",
        lambda ledger: metered_transport(ledger, httpx2.MockTransport(handler)),
    )
    return module, SimpleNamespace(batch=tmp_path, approval=approval), sent


def test_six_isolated_packets_immutable_raws_no_private_expectations_in_driver(
    tmp_path, monkeypatch
):
    module, args, sent = fixture_run(tmp_path, monkeypatch)
    loaded = []
    original = module.load

    def record(path):
        loaded.append(str(path))
        return original(path)

    monkeypatch.setattr(module, "load", record)
    asyncio.run(module.run(args))
    assert len(sent) == 6
    assert all(len(json.loads(b["input"])["assessment_fields"]) == 11 for b in sent)
    assert all(b["max_output_tokens"] == 8192 and b["store"] is False for b in sent)
    assert not any("reference" in path or "expectations" in path for path in loaded)
    assert len(list(tmp_path.glob("*-raw.json"))) == 6
    assert len(json.loads((tmp_path / "ratings.json").read_text())) == 6
    assert all(
        json.loads(p.read_text())["validation_error"] is None
        for p in tmp_path.glob("*-result.json")
    )
    with pytest.raises(FileExistsError):
        asyncio.run(module.run(args))
    assert len(sent) == 6


def test_invalid_packet_binding_is_preserved_without_repair_or_retry(tmp_path, monkeypatch):
    module, args, sent = fixture_run(tmp_path, monkeypatch, invalid=True)
    asyncio.run(module.run(args))
    assert len(sent) == 6
    assert all(
        json.loads(p.read_text())["validation_error"] == "ValueError"
        for p in tmp_path.glob("*-result.json")
    )
    assert all(
        json.loads(p.read_text())["rating"]["packet_id"] == "0" * 64
        for p in tmp_path.glob("*-result.json")
    )


def test_quota_failure_stops_without_hidden_sdk_retries(tmp_path, monkeypatch):
    module, args, sent = fixture_run(tmp_path, monkeypatch, quota=True)
    asyncio.run(module.run(args))
    assert len(sent) == 1
    assert json.loads((tmp_path / "ratings.json").read_text()) == []
    ledger = DispatchLedger(tmp_path / "dispatch.sqlite", 6, "MOCK-only-model")
    with ledger.connection() as db:
        row = db.execute("SELECT result FROM dispatches").fetchone()
    assert json.loads(row[0])["stop_batch"]


def test_no_approval_blocks_before_any_mock_or_real_provider(tmp_path, monkeypatch):
    module, args, sent = fixture_run(tmp_path, monkeypatch)
    args.approval = None
    with pytest.raises(ValueError, match="approval"):
        asyncio.run(module.run(args))
    assert sent == []


def test_provider_subset_omits_unsupported_uniqueitems_without_changing_local_rubric(
    tmp_path, monkeypatch
):
    from fraudlens.investigation.judging_v4 import RATING_SCHEMA, validate_rating

    original = copy.deepcopy(RATING_SCHEMA)
    module, args, sent = fixture_run(tmp_path, monkeypatch, strict_wire=True)
    asyncio.run(module.run(args))
    assert len(sent) == 6
    assert len(json.loads((tmp_path / "ratings.json").read_text())) == 6
    assert RATING_SCHEMA == original
    packets = json.loads((tmp_path / "packets.json").read_text())
    value = json.loads((tmp_path / "ratings.json").read_text())[0]["rating"]
    value["checks"]["required_disclosures_complete"]["report_locations"] = [
        "/limitations",
        "/limitations",
    ]
    with pytest.raises(ValueError):
        validate_rating(packets[0], value)
