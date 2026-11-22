"""T246 synthetic EDA API contract: precomputed, bounded, label-free only."""

import json
from hashlib import sha256
from pathlib import Path

from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

from fraudlens.eda import aggregate_eda
from fraudlens.main import create_app


class StubEda:
    def __init__(self, payload):
        self.payload = payload
        self.calls = 0

    def load(self):
        self.calls += 1
        return self.payload


def _summary():
    return aggregate_eda(
        [{
            'source_row_number': 1, 'timestamp': '2022/09/01 00:00',
            'sender_bank': 'S1', 'receiver_bank': 'R1',
            'amount_paid': '10.00', 'payment_currency': 'USD',
            'amount_received': '9.00', 'receiving_currency': 'EUR',
            'payment_format': 'Wire',
        }],
        dataset_version='synthetic-v1', source_sha256='a' * 64,
        source_count=1, rejected_count=0, warmup_count=1,
    )


def test_summary_route_returns_only_precomputed_closed_aggregate():
    stub = StubEda(_summary())
    with TestClient(create_app(eda_service=stub)) as client:
        response = client.get('/api/eda/summary')
    assert response.status_code == 200
    assert response.json() == stub.payload.model_dump(mode='json')
    assert stub.calls == 1
    assert 'is_laundering' not in response.text
    assert 'transaction_id' not in response.text
    schema_path = (Path(__file__).resolve().parents[3]
                   / 'specs/002-data-and-risk-scoring/contracts/schemas.json')
    schema = json.loads(schema_path.read_text())
    Draft202012Validator(schema).validate(response.json())
    Draft202012Validator({**schema, '$ref': '#/$defs/EdaSummary'}).validate(response.json())


def test_valid_hash_pinned_precomputed_summary_loads_without_source_rows(tmp_path):
    from fraudlens.eda.service import EdaService

    body = _summary().model_dump_json().encode()
    path = tmp_path / 'eda-summary.json'
    path.write_bytes(body)
    service = EdaService(path, sha256(body).hexdigest(), expected_source_sha256='a' * 64)
    with TestClient(create_app(eda_service=service)) as client:
        response = client.get('/api/eda/summary')
    assert response.status_code == 200
    assert response.json() == _summary().model_dump(mode='json')


def test_default_fixture_startup_has_controlled_unavailable_eda():
    with TestClient(create_app()) as client:
        assert client.get('/api/cases').status_code == 200
        response = client.get('/api/eda/summary')
    assert response.status_code == 404
    assert response.json()['error']['code'] == 'dataset_unavailable'


def test_summary_refuses_arbitrary_query_before_loading():
    stub = StubEda(_summary())
    with TestClient(create_app(eda_service=stub)) as client:
        response = client.get('/api/eda/summary?partition=showcase')
    assert response.status_code == 422
    assert response.json()['error']['code'] == 'invalid_request'
    assert stub.calls == 0


def test_missing_and_tampered_summary_are_controlled(tmp_path):
    from fraudlens.eda.service import EdaService

    missing = tmp_path / 'missing.json'
    altered = tmp_path / 'altered.json'
    body = _summary().model_dump_json().encode()
    altered.write_bytes(body + b'\n')
    for path, expected in ((missing, sha256(body).hexdigest()),
                           (altered, sha256(body).hexdigest())):
        with TestClient(create_app(eda_service=EdaService(path, expected,
                                                          expected_source_sha256='a' * 64))) as client:
            response = client.get('/api/eda/summary')
        assert response.status_code == 404
        assert response.json()['error']['code'] == 'dataset_unavailable'
        assert str(path) not in response.text


def test_valid_hash_but_malformed_or_label_bearing_payload_is_refused(tmp_path):
    from fraudlens.eda.service import EdaService

    path = tmp_path / 'summary.json'
    label_quality = _summary().model_dump(mode='json')
    label_quality['quality_counts']['positive_count'] = 1
    for body in (b'{}', _summary().model_dump_json().encode()[:-1] +
                 b',"is_laundering":1}', json.dumps(label_quality).encode()):
        path.write_bytes(body)
        service = EdaService(path, sha256(body).hexdigest(),
                             expected_source_sha256='a' * 64)
        with TestClient(create_app(eda_service=service)) as client:
            response = client.get('/api/eda/summary')
        assert response.status_code == 404
        assert response.json()['error']['code'] == 'dataset_unavailable'
