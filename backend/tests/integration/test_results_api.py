"""Synthetic results API gates; no project labels or prediction rows are read."""

from dataclasses import replace

from fastapi.testclient import TestClient

from fraudlens.main import create_app
from fraudlens.settings import Settings
from fraudlens.training.results import ResultsPaths, ResultsService


class StubResults:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = 0

    def load(self):
        self.calls += 1
        if self.error:
            raise self.error
        return self.result


def test_authorized_results_are_aggregate_only():
    payload = {
        'model_version': 'lightgbm-3b4e4019312d',
        'feature_version': 'hi-small-temporal-v1',
        'dataset_version': 'ibm-hi-small-b19d39f5',
        'threshold': 0.2489517623052024, 'calibration_status': 'not_assessed',
        'partitions': [], 'limitations': ['Synthetic local capstone.'],
    }
    service = StubResults(payload)
    with TestClient(create_app(settings=Settings(mode='model'), results_service=service)) as client:
        response = client.get('/api/model/results')
    assert response.status_code == 200
    assert response.json() == payload
    assert service.calls == 1
    assert 'is_laundering' not in response.text


def test_results_query_is_refused_without_calling_report_loader():
    service = StubResults({})
    with TestClient(create_app(settings=Settings(mode='model'), results_service=service)) as client:
        response = client.get('/api/model/results?transaction_id=example')
    assert response.status_code == 422
    assert service.calls == 0


def test_verified_existing_reports_return_only_bounded_aggregates():
    with TestClient(create_app(settings=Settings(mode='model'))) as client:
        response = client.get('/api/model/results')
    assert response.status_code == 200
    body = response.json()
    assert body['threshold'] == 0.2489517623052024
    assert body['model_version'] == 'lightgbm-3b4e4019312d'
    assert [(part['partition'], part['row_count'], part['positive_count'], part['negative_count'])
            for part in body['partitions']] == [
                ('validation', 482650, 471, 482179), ('test', 233070, 218, 232852)]
    assert all(part['state'] == 'available' for part in body['partitions'])
    assert all('Whole-partition P@20' in [metric['name'] for metric in part['metrics']]
               for part in body['partitions'])
    assert 'is_laundering' not in response.text
    assert 'transaction_id' not in response.text


def test_missing_approval_and_report_are_controlled(tmp_path):
    paths = ResultsPaths()
    missing = tmp_path / 'missing'
    scenarios = [
        (replace(paths, authorization=missing), 409, 'evaluation_not_authorized'),
        (replace(paths, completion=missing), 409, 'evaluation_not_authorized'),
        (replace(paths, report=missing), 404, 'results_unavailable'),
    ]
    for source, status, code in scenarios:
        with TestClient(create_app(settings=Settings(mode='model'),
                                   results_service=ResultsService(source))) as client:
            response = client.get('/api/model/results')
        assert response.status_code == status
        assert response.json()['error']['code'] == code
        assert str(missing) not in response.text


def test_report_byte_change_is_rejected_before_parsing(tmp_path):
    paths = ResultsPaths()
    altered = tmp_path / 'altered.json'
    altered.write_bytes(paths.report.read_bytes() + b'\n')
    with TestClient(create_app(settings=Settings(mode='model'),
                               results_service=ResultsService(replace(paths, report=altered)))) as client:
        response = client.get('/api/model/results')
    assert response.status_code == 404
    assert response.json()['error']['code'] == 'results_unavailable'
