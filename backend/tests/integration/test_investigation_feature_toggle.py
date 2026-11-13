"""Composition RED: future routes deliberately absent until T019/T035."""
import socket

import httpx
import pytest
from fastapi.testclient import TestClient

from fraudlens.cases import CaseService
from fraudlens.main import create_app
from fraudlens.scoring import FixtureScorer
from fraudlens.settings import Settings


@pytest.fixture(autouse=True)
def environment(monkeypatch):
    for key in ['OPENAI_API_KEY', 'OPENAI_MODEL', 'APP_MODE', 'INVESTIGATION_ENABLED']:
        monkeypatch.delenv(key, raising=False)


def test_disabled_foundation_is_unchanged():
    with TestClient(create_app()) as client:
        expected = CaseService(Settings().fixture_path, FixtureScorer()).get_case('CASE-001')
        assert client.get('/api/cases/CASE-001').json() == expected.model_dump(mode='json')
        assert client.get('/api/cases').status_code == 200
        assert client.get('/api/cases/CASE-999').json()['error']['code'] == 'case_not_found'


def test_startup_no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('Unexpected provider/network access')
    monkeypatch.setattr(socket, 'create_connection', forbidden)
    monkeypatch.setattr(httpx.HTTPTransport, 'handle_request', forbidden)
    monkeypatch.setattr(httpx.AsyncHTTPTransport, 'handle_async_request', forbidden)
    with TestClient(create_app()) as client:
        assert client.get('/api/health').status_code == 200


@pytest.mark.parametrize('path,code', [
    ('/api/knowledge/search?q=test', 'knowledge_unavailable'),
    ('/api/investigation/attempts/att_' + 'a' * 32, 'investigation_not_found'),
])
def test_new_errors_are_feature_specific(monkeypatch, path, code):
    monkeypatch.setenv('INVESTIGATION_ENABLED', 'true')
    with TestClient(create_app()) as client:
        response = client.get(path)
        assert response.json().get('contract_version') == 1
        assert response.json()['error']['code'] == code


def test_cross_origin_mutation_rejected(monkeypatch):
    monkeypatch.setenv('INVESTIGATION_ENABLED', 'true')
    with TestClient(create_app()) as client:
        response = client.post('/api/investigation/runs', json={},
                               headers={'origin': 'https://outside.invalid'})
        assert response.status_code == 403
        assert response.json()['error']['code'] == 'forbidden_scope'


def test_mutation_requires_json(monkeypatch):
    monkeypatch.setenv('INVESTIGATION_ENABLED', 'true')
    with TestClient(create_app()) as client:
        response = client.post('/api/investigation/runs', content='text',
                               headers={'content-type': 'text/plain', 'origin': 'http://testserver'})
        assert response.status_code == 422
        assert response.json()['error']['code'] == 'invalid_request'


def test_no_permissive_cors():
    with TestClient(create_app()) as client:
        response = client.options('/api/investigation/runs', headers={
            'origin': 'https://outside.invalid', 'access-control-request-method': 'POST'})
        assert response.headers.get('access-control-allow-origin') != '*'
