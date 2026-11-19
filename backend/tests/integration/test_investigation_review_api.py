"""Closed review route, server actor, safe conflicts and durable request identities."""
import asyncio
from uuid import uuid4

import pytest
from test_investigation_api import post
from test_investigation_api import runtime as api_runtime
from test_investigation_recovery_api import action

runtime = api_runtime


def body(run, **changes):
    return dict(report_id=run['report']['report_id'], disposition='close', rationale='Test review',
                correction_note=None, supersedes_review_id=None) | changes


def ready(runtime):
    post(runtime[0], runtime[2])
    return asyncio.run(runtime[1].work_once())


def test_review_amendment_etag_replay_and_immutable_draft(runtime):
    client, service, _, _ = runtime
    run = ready(runtime)
    key = str(uuid4())
    response = action(client, run, 'reviews', body(run), key)
    assert response.status_code == 201
    first = response.json()
    assert first['review']['actor'] == 'server-analyst'
    assert response.headers['etag'] == str(first['revision'])
    assert action(client, run, 'reviews', body(run), key).json() == first
    amendment = body(run, disposition='escalate', correction_note='New interpretation',
                     supersedes_review_id=first['review']['review_id'])
    second = action(client, first, 'reviews', amendment)
    assert second.status_code == 201
    assert second.json()['review']['supersedes_review_id'] == first['review']['review_id']
    assert second.json()['report']['draft'] == run['report']['draft']
    assert service.read(run['attempt_id']) == second.json()
    assert action(client, run, 'reviews', body(run), key).json() == first  # Original response after amendment.
    assert action(client, first, 'reviews', body(run)).json()['error']['code'] == 'revision_conflict'
    latest = second.json()
    assert action(client, latest, 'reviews', amendment).json()['error']['code'] == 'revision_conflict'
    assert action(client, run, 'reviews', body(run, rationale='changed'), key).json()['error']['code'] == 'request_conflict'
    assert latest['budget'] == run['budget']


@pytest.mark.parametrize('changes', [{'rationale': ''}, {'rationale': '  '}, {'rationale': 'x' * 2001},
    {'actor': 'forged'}, {'correction_note': ' '}, {'report_id': 'bad'}, {'disposition': 'approve'}])
def test_closed_input_and_safe_errors(runtime, changes):
    client = runtime[0]
    run = ready(runtime)
    response = action(client, run, 'reviews', body(run, **changes))
    assert response.status_code == 422 and response.json()['error']['code'] == 'invalid_request'
    assert 'forged' not in response.text
    assert runtime[1].read(run['attempt_id']) == run


def test_headers_origin_report_and_amendment_checks(runtime):
    client = runtime[0]
    run = ready(runtime)
    path = '/api/investigation/attempts/' + run['attempt_id'] + '/reviews'
    headers = {'If-Match': str(run['revision']), 'Idempotency-Key': str(uuid4())}
    for missing in headers:
        assert client.post(path, json=body(run), headers={k: v for k, v in headers.items() if k != missing}).status_code == 422
    for bad in ['0', '-1', '1.5', '"4"', ' 4']:
        assert client.post(path, json=body(run), headers=headers | {'If-Match': bad}).status_code == 422
    assert client.post(path, json=body(run), headers=headers | {'Origin': 'https://external.invalid'}).status_code == 403
    assert client.post(path, content='{}', headers=headers).status_code == 422
    assert client.post(path + '?actor=forged', json=body(run), headers=headers).status_code == 422
    assert action(client, run, 'reviews', body(run, report_id='f' * 64)).json()['error']['code'] == 'revision_conflict'
    assert action(client, run, 'reviews', body(run, supersedes_review_id='rev_' + 'f' * 32)).status_code == 409
    assert action(client, run, 'reviews', body(run, correction_note='Initial note')).status_code == 201


def test_maximum_unicode_review_survives_escaped_json_transport(runtime):
    import json
    client = runtime[0]
    run = ready(runtime)
    payload = body(run, rationale='\U0001f600' * 2000, correction_note='\U0001f601' * 2000)
    response = client.post('/api/investigation/attempts/' + run['attempt_id'] + '/reviews',
        content=json.dumps(payload, ensure_ascii=True), headers={'Content-Type': 'application/json',
            'If-Match': str(run['revision']), 'Idempotency-Key': str(uuid4())})
    assert response.status_code == 201
    assert response.json()['review']['rationale'] == payload['rationale']
