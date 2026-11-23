"""Explicit recovery HTTP contracts with zero-spend reads."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from test_investigation_api import post
from test_investigation_api import runtime as api_runtime

runtime = api_runtime


def action(client, run, operation, body=None, key=None, revision=None):
    return client.post('/api/investigation/attempts/' + run['attempt_id'] + '/' + operation,
                       json=body if body is not None else {},
                       headers={'If-Match': str(run['revision'] if revision is None else revision),
                                'Idempotency-Key': key or str(uuid4())})


def test_cancel_retry_replay_cas_and_persisted_responses(runtime):
    client, service, body, _ = runtime
    run = post(client, body).json()
    cancel_key, retry_key = str(uuid4()), str(uuid4())
    cancelled = action(client, run, 'cancel', key=cancel_key)
    assert cancelled.status_code == 200
    ended = cancelled.json()
    assert ended['state'] == 'cancelled' and cancelled.headers['etag'] == str(ended['revision'])
    assert action(client, run, 'cancel', key=cancel_key).json() == ended
    stale = action(client, run, 'cancel')
    assert stale.status_code == 409 and stale.json()['error']['code'] == 'revision_conflict'
    retried = action(client, ended, 'retry', {'reuse_evidence': True}, retry_key)
    assert retried.status_code == 202
    child = retried.json()
    assert child['parent_attempt_id'] == run['attempt_id'] and child['run_id'] == run['run_id']
    assert child['budget']['provider_requests'] == 0
    listed = client.get('/api/investigation/runs?case_id=CASE-001').json()
    assert listed['total_count'] == 1 and listed['items'] == [child]
    done = asyncio.run(service.work_once())
    assert done['state'] == 'ready_for_review'
    assert action(client, ended, 'retry', {'reuse_evidence': True}, retry_key).json() == child
    changed = action(client, ended, 'retry', {'reuse_evidence': False}, retry_key)
    assert changed.status_code == 409 and changed.json()['error']['code'] == 'request_conflict'
    assert action(client, done, 'retry', {'reuse_evidence': False}).json()['error']['code'] == 'invalid_transition'
    assert action(client, done, 'cancel').json()['error']['code'] == 'invalid_transition'
    for _ in range(3):
        assert client.get('/api/investigation/attempts/' + done['attempt_id']).json()['budget']['provider_requests'] == 4


@pytest.mark.parametrize('operation,body', [('retry', {'reuse_evidence': True}), ('cancel', {})])
def test_closed_recovery_headers_guards_and_bodies(runtime, operation, body):
    client, _, request, _ = runtime
    run = post(client, request).json()
    path = '/api/investigation/attempts/' + run['attempt_id'] + '/' + operation
    headers = {'If-Match': '1', 'Idempotency-Key': str(uuid4())}
    for missing in ('If-Match', 'Idempotency-Key'):
        assert client.post(path, json=body, headers={k: v for k, v in headers.items() if k != missing}).status_code == 422
    for bad in ('0', '-1', '1.0', '"1"', ' 1', '1e2'):
        assert client.post(path, json=body, headers={**headers, 'If-Match': bad}).status_code == 422
    assert client.post(path, json={**body, 'actor': 'forged'}, headers=headers).status_code == 422
    assert client.post(path + '?extra=1', json=body, headers=headers).status_code == 422
    assert client.post(path, json=body, headers={**headers, 'Origin': 'https://external.invalid'}).status_code == 403
    assert client.post(path, content='{}', headers=headers).status_code == 422


def test_changed_source_rejects_retry_and_pinned_list_but_keeps_history(runtime, monkeypatch):
    client, service, request, _ = runtime
    run = post(client, request).json()
    done = asyncio.run(service.work_once())
    other = post(client, request).json()
    ended = action(client, other, 'cancel').json()
    original = service.context_reader.resolve
    def switched(case, mode, snapshot):
        if snapshot:
            raise ValueError('stale_snapshot')
        return {**original(case, mode, None), 'context_revision': 'e' * 64, 'snapshot_ref': 'fixture_' + 'e' * 64}
    monkeypatch.setattr(service.context_reader, 'resolve', switched)
    assert action(client, ended, 'retry', {'reuse_evidence': False}).json()['error']['code'] == 'stale_snapshot'
    pinned = client.get('/api/investigation/runs?case_id=CASE-001&context_revision=' + run['context_revision'])
    assert pinned.status_code == 409
    assert client.get('/api/investigation/attempts/' + done['attempt_id']).json() == done
    assert client.get('/api/investigation/runs?case_id=CASE-001').json()['items'] == []


def test_two_connections_same_key_one_child_different_keys_one_winner(runtime):
    client, service, request, store = runtime
    run = post(client, request).json()
    ended = action(client, run, 'cancel').json()
    key = str(uuid4())
    def retry(_):
        from fraudlens.investigation.store import InvestigationRepository
        from fraudlens.investigation.workflow import InvestigationService
        other = InvestigationService(InvestigationRepository(store.repository.path), store, service.settings)
        return other.retry(ended['attempt_id'], ended['revision'], False, service.settings.analyst, key)
    with ThreadPoolExecutor(2) as pool:
        a, b = pool.map(retry, range(2))
    assert a == b
    with store.repository.connection() as db:
        assert db.execute('SELECT count(*) FROM attempts').fetchone()[0] == 2
