"""Offline HTTP creation, bounded reads and an explicit separate worker."""
import asyncio
import json
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from fraudlens.investigation.cli import main
from fraudlens.investigation.context import CaseContextReader
from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import validate
from fraudlens.investigation.settings import InvestigationSettings
from fraudlens.investigation.workflow import InvestigationService
from fraudlens.main import create_app


@pytest.fixture
def runtime(tmp_path, knowledge_factory, monkeypatch):
    store = KnowledgeStore(tmp_path / 'runs.sqlite')
    store.publish(knowledge_factory('missing evidence money'))
    store.save_configuration(json.loads(Path('data/knowledge/fraudlens-aml-knowledge-v1/retrieval.json').read_text()))
    monkeypatch.setenv('INVESTIGATION_ENABLED', 'true')
    monkeypatch.setenv('INVESTIGATION_PROVIDER', 'test')
    monkeypatch.setenv('INVESTIGATION_STORE', str(store.repository.path))
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    monkeypatch.delenv('OPENAI_MODEL', raising=False)
    settings = InvestigationSettings(enabled=True, store=store.repository.path, analyst='server-analyst')
    service = InvestigationService(store.repository, store, settings)
    app = create_app()
    app.state.investigation_service = service
    context = CaseContextReader().resolve('CASE-001', 'fixture', None)
    body = {k: context[k] for k in ('case_id', 'source_mode', 'snapshot_ref')}
    with TestClient(app) as client:
        yield client, service, body, store


def post(client, body, key=None, **kwargs):
    return client.post('/api/investigation/runs', json=body,
                       headers={'Idempotency-Key': key or str(uuid4()), **kwargs})


def test_create_replay_worker_read_and_owned_evidence(runtime):
    client, service, body, store = runtime
    key = str(uuid4())
    response = post(client, body, key)
    assert response.status_code == 202
    run = validate('RunView', response.json())
    assert run['state'] == 'created' and run['budget']['provider_requests'] == 0
    assert response.headers['etag'] == '1'
    assert post(client, body, key).json() == run
    changed = {**body, 'case_id': 'CASE-002'}
    assert post(client, changed, key).status_code == 409
    with store.repository.connection() as db:
        assert db.execute('SELECT actor FROM request_keys').fetchall() == [('server-analyst',)]
    done = asyncio.run(service.work_once())
    assert done['state'] == 'ready_for_review'
    path = '/api/investigation/attempts/' + run['attempt_id']
    for _ in range(2):
        assert client.get(path).json() == done
    item = service.evidence(run['attempt_id'])[0]
    assert client.get(path + '/evidence/' + item['evidence_id']).json() == item
    other = post(client, body).json()
    wrong = '/api/investigation/attempts/' + other['attempt_id'] + '/evidence/' + item['evidence_id']
    assert client.get(wrong).status_code == 404
    assert client.get(path).json()['budget']['provider_requests'] == 4


def test_list_resolves_server_snapshot_and_bounds_saved_runs(runtime):
    client, service, body, _ = runtime
    for _ in range(22):
        service.create(body, 'server-analyst', str(uuid4()))
    response = client.get('/api/investigation/runs?case_id=CASE-001')
    assert response.status_code == 200
    result = validate('RunList', response.json())
    assert result['total_count'] == 22 and result['truncated'] and len(result['items']) == 20
    assert response.headers['x-investigation-snapshot'] == body['snapshot_ref']
    revision = response.headers['x-investigation-context']
    assert all(item['context_revision'] == revision for item in result['items'])
    assert result['items'] == sorted(result['items'], key=lambda item: (-float(__import__('datetime').datetime.fromisoformat(item['created_at']).timestamp()), item['run_id']))
    assert client.get('/api/investigation/runs?case_id=CASE-001&context_revision=' + 'a' * 64).status_code == 409


@pytest.mark.parametrize('change,status,code', [
    ({'actor': 'forged'}, 422, 'invalid_request'),
    ({'snapshot_ref': 'old'}, 409, 'stale_snapshot'),
    ({'source_mode': 'dataset'}, 503, 'context_unavailable'),
    ({'case_id': 'CASE-999'}, 404, 'case_not_found'),
])
def test_safe_create_errors(runtime, change, status, code):
    client, _, body, _ = runtime
    response = post(client, {**body, **change})
    assert response.status_code == status
    assert validate('ErrorEnvelope', response.json())['error']['code'] == code


def test_mutation_guards_before_configuration_and_closed_queries(runtime):
    client, _, body, _ = runtime
    assert post(client, body, Origin='https://external.invalid').status_code == 403
    assert post(client, body, Host='external.invalid').status_code == 403
    assert client.post('/api/investigation/runs', json=body).status_code == 422
    assert client.get('/api/investigation/runs?case_id=CASE-001&limit=100').status_code == 422
    assert client.get('/api/investigation/runs?case_id=CASE-001&case_id=CASE-002').status_code == 422
    missing = client.get('/api/investigation/attempts/att_' + 'a' * 32)
    assert missing.status_code == 404 and missing.json()['error']['code'] == 'investigation_not_found'


def test_worker_cli_once_is_explicit_and_does_not_enqueue(runtime, capsys):
    client, _, body, store = runtime
    run = post(client, body).json()
    assert run['state'] == 'created'
    assert main(['worker', '--store', str(store.repository.path), '--once']) == 0
    assert json.loads(capsys.readouterr().out)['state'] == 'ready_for_review'
    assert main(['worker', '--store', str(store.repository.path), '--once']) == 0
    assert json.loads(capsys.readouterr().out)['state'] == 'idle'


def test_unexpected_new_route_error_uses_safe_feature_envelope(runtime, monkeypatch):
    client, service, _, _ = runtime
    def broken(attempt):
        raise RuntimeError('PRIVATE-ERROR-DETAIL')
    monkeypatch.setattr(service, 'read', broken)
    with TestClient(client.app, raise_server_exceptions=False) as production:
        response = production.get('/api/investigation/attempts/att_' + 'a' * 32)
    assert response.status_code == 500
    assert response.json().get('contract_version') == 1
    assert validate('ErrorEnvelope', response.json())['error']['code'] == 'internal_error'
    assert 'PRIVATE' not in response.text
