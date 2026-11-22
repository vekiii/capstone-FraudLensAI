"""Feature 006 synthetic HTTP boundary probes; no real ML inputs are opened."""

from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from fraudlens.main import create_app
from fraudlens.scoring.model_scorer import FeatureTransaction
from fraudlens.settings import Settings

ID = 'ibm-hi-small:' + 'a' * 64 + ':row:1'


class Store:
    def __init__(self, record=None):
        self.record = record
        self.calls = 0

    def get(self, _identity):
        self.calls += 1
        return self.record


class Scorer:
    def __init__(self, output=None, error=None):
        self.output = output
        self.error = error
        self.calls = 0

    def score(self, _record):
        self.calls += 1
        if self.error:
            raise self.error
        return self.output


@pytest.mark.parametrize('path', [
    '/api/health', '/api/cases', f'/api/transactions/{ID}/risk',
    '/api/model/results', '/api/eda/summary',
])
def test_read_only_routes_reject_post_body_without_reflection(path):
    marker = 'SYNTHETIC_PRIVATE_TOKEN'
    with TestClient(create_app(settings=Settings()), raise_server_exceptions=False) as client:
        response = client.post(path, content='{"token":"' + marker + '"',
                               headers={'content-type': 'application/json'})
    assert response.status_code == 405
    assert response.json()['error']['code'] == 'invalid_request'
    assert marker not in response.text


@pytest.mark.parametrize('identifier', [
    'x' * 10_000, 'CASE-001', 'ibm-hi-small:' + 'a' * 64 + ':row:0',
    'ibm-hi-small:' + 'a' * 64 + ':row:01', '<img onerror=alert(1)>',
    'ibm-hi-small:' + 'a' * 64 + ':row:１２',
])
def test_bad_risk_ids_are_bounded_and_do_not_reach_store(identifier):
    store = Store()
    app = create_app(settings=Settings(mode='model'), feature_store=store,
                     model_scorer=Scorer())
    with TestClient(app) as client:
        response = client.get('/api/transactions/' + quote(identifier, safe='') + '/risk')
    assert response.status_code == 422
    assert response.json()['error']['code'] == 'invalid_request'
    assert identifier not in response.text
    assert len(response.content) < 256
    assert store.calls == 0


def test_risk_query_cannot_expand_or_change_assessment():
    store = Store(FeatureTransaction(ID, '2022-09-06T00:00:00Z', {}))
    scorer = Scorer()
    app = create_app(settings=Settings(mode='model'), feature_store=store,
                     model_scorer=scorer)
    with TestClient(app) as client:
        response = client.get(f'/api/transactions/{ID}/risk', params={
            'partition': 'showcase', 'include_labels': 'true', 'threshold': '0',
        })
    assert response.status_code == 422
    assert response.json()['error']['code'] == 'invalid_request'
    assert store.calls == scorer.calls == 0


@pytest.mark.parametrize('path', ['/api/model/results', '/api/eda/summary'])
def test_aggregate_queries_rejected_without_sensitive_echo(path):
    with TestClient(create_app(settings=Settings(mode='fixture'))) as client:
        response = client.get(path, params={'partition': 'showcase',
                                            'include_labels': 'true', 'secret': 'CANARY'})
    assert response.status_code == 422
    assert response.json()['error']['code'] == 'invalid_request'
    assert 'CANARY' not in response.text


def test_unexpected_scorer_exception_is_generic_and_never_zero_risk():
    app = create_app(settings=Settings(mode='model'),
                     feature_store=Store(FeatureTransaction(ID, '2022-09-06T00:00:00Z', {})),
                     model_scorer=Scorer(error=RuntimeError('SYNTHETIC_PRIVATE_PATH')))
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(f'/api/transactions/{ID}/risk')
    assert response.status_code == 500
    assert response.json()['error']['code'] == 'internal_error'
    assert 'SYNTHETIC_PRIVATE_PATH' not in response.text
    assert 'risk_score' not in response.text


def test_fixture_case_listing_is_local_single_user_behavior():
    with TestClient(create_app(settings=Settings())) as client:
        response = client.get('/api/cases')
    assert response.status_code == 200
    assert isinstance(response.json()['items'], list)
