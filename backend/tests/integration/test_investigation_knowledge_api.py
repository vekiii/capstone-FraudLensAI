import socket

import httpx
import pytest
from fastapi.testclient import TestClient

from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import validate
from fraudlens.main import create_app


@pytest.fixture
def knowledge_client(knowledge_factory, tmp_path, monkeypatch):
    monkeypatch.setenv('INVESTIGATION_ENABLED', 'true')
    store = KnowledgeStore(tmp_path / 'inv.sqlite')
    corpus = store.publish(knowledge_factory())
    config = dict(algorithm='bm25', k1=1.2, b=.75, maximum_results=5, adequacy_cutoff=0)
    retrieval = store.save_configuration(config)
    app = create_app()
    app.state.knowledge_store = store
    with TestClient(app) as client:
        yield client, corpus, retrieval


def test_knowledge_routes(knowledge_client):
    client, corpus, retrieval = knowledge_client
    response = client.get('/api/knowledge/documents', params={'corpus': corpus})
    assert response.status_code == 200
    validate('DocumentList', response.json())
    result = client.get('/api/knowledge/search', params={'q': 'money', 'corpus': corpus, 'retrieval': retrieval})
    assert result.status_code == 200
    validate('SearchResult', result.json())
    assert result.headers.get('x-results-truncated') == 'true'
    passage = result.json()['hits'][0]['passage']
    exact = client.get('/api/knowledge/passages/' + passage['passage_id'], params={'corpus': corpus})
    assert exact.status_code == 200
    assert exact.json() == passage


@pytest.mark.parametrize('url,status,code', [
    ('/api/knowledge/search?q=', 422, 'invalid_request'),
    ('/api/knowledge/search?q=test&limit=99', 422, 'invalid_request'),
    ('/api/knowledge/documents?corpus=../private', 422, 'invalid_request'),
    ('/api/knowledge/passages/' + 'f' * 64, 404, 'evidence_not_found'),
    ('/api/knowledge/documents?corpus=corpus_' + 'f' * 64, 503, 'knowledge_unavailable'),
])
def test_closed_errors(knowledge_client, url, status, code):
    client, _, _ = knowledge_client
    response = client.get(url)
    assert response.status_code == status
    validate('ErrorEnvelope', response.json())
    assert response.json()['error']['code'] == code
    assert 'Traceback' not in response.text


def test_disabled_or_missing_preserves_foundation(monkeypatch, tmp_path):
    monkeypatch.setenv('INVESTIGATION_ENABLED', 'false')
    monkeypatch.setenv('INVESTIGATION_STORE', str(tmp_path / 'missing.sqlite'))
    with TestClient(create_app()) as client:
        assert client.get('/api/knowledge/search?q=test').status_code == 503
        assert client.get('/api/cases').status_code == 200
    assert not (tmp_path / 'missing.sqlite').exists()


def test_requests_do_not_scrape_or_call_provider(knowledge_client, monkeypatch):
    client, corpus, retrieval = knowledge_client
    def forbidden(*args, **kwargs):
        pytest.fail('Unexpected external request')
    monkeypatch.setattr(socket, 'create_connection', forbidden)
    monkeypatch.setattr(httpx.HTTPTransport, 'handle_request', forbidden)
    monkeypatch.setattr(httpx.AsyncHTTPTransport, 'handle_async_request', forbidden)
    assert client.get('/api/knowledge/search', params={'q':'money','corpus':corpus,'retrieval':retrieval}).status_code == 200


def test_archive_corpus_pinning(knowledge_client, knowledge_factory):
    client, corpus, retrieval = knowledge_client
    first = client.get('/api/knowledge/search', params={'q':'money','corpus':corpus,'retrieval':retrieval}).json()
    store = client.app.state.knowledge_store
    second = store.publish(knowledge_factory('changed evidence'))
    assert second != corpus
    passage = first['hits'][0]['passage']
    assert client.get('/api/knowledge/passages/' + passage['passage_id'], params={'corpus':corpus}).json() == passage
