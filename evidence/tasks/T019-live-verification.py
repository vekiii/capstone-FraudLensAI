"""T019 real HTTP/proxy checks; requires quickstart servers on 8000 and 5173.

Run from repository root: uv run --locked python evidence/tasks/T019-live-verification.py
PYTHONPATH must include backend/src. No debug routes, fixture mutations or browser claims.
"""
import json
import re
import socket
import tempfile
import threading
import time
from contextlib import contextmanager
from pathlib import Path

import httpx
import uvicorn
from jsonschema import Draft202012Validator, FormatChecker

from fraudlens.main import create_app
from fraudlens.scoring import FixtureScorer
from fraudlens.settings import Settings

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / 'specs/001-project-foundation/contracts/schemas.json').read_text())
REPORT = {'live': {}, 'injected': {}}
FORBIDDEN = {'isfraud', 'fraudlabel', 'confirmedfraud', 'islaundering', 'groundtruth',
             'referencedecision', 'referenceanswer', 'accuracy', 'precision', 'recall', 'auc', 'f1'}


def public(payload):
    if isinstance(payload, dict):
        for key, value in payload.items():
            assert re.sub('[^a-z0-9]', '', key.lower()) not in FORBIDDEN
            public(value)
    elif isinstance(payload, list):
        for value in payload:
            public(value)
    elif isinstance(payload, str):
        assert not re.search(r'\b(?:accuracy|precision|recall|auc|f1)\s*(?:is|=|:)?\s*\d',
                             payload, re.I)


def read(client, path, status, schema, code=None):
    response = client.get(path)
    assert response.status_code == status, (path, response.status_code)
    assert response.headers['content-type'].startswith('application/json')
    body = response.json()
    Draft202012Validator({**SCHEMA, '$ref': f'#/$defs/{schema}'},
                        format_checker=FormatChecker()).validate(body)
    public(body)
    if code:
        assert body['error']['code'] == code
        assert not re.search(r'Traceback|PRIVATE_|RuntimeError|[A-Za-z]:[\\/]|/private/', response.text)
    return body


@contextmanager
def serve(app):
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        listener.listen(128)
        server = uvicorn.Server(uvicorn.Config(app, log_level='error', access_log=False))
        thread = threading.Thread(target=server.run, kwargs={'sockets': [listener]}, daemon=True)
        thread.start()
        deadline = time.monotonic() + 5
        while not server.started and thread.is_alive() and time.monotonic() < deadline:
            time.sleep(0.01)
        try:
            assert server.started, 'Injected live server did not start'
            yield f'http://127.0.0.1:{listener.getsockname()[1]}'
        finally:
            server.should_exit = True
            thread.join(timeout=5)
            assert not thread.is_alive(), 'Injected server did not stop'


class InvalidScorer(FixtureScorer):
    def score(self, transaction):
        return super().score(transaction).model_copy(update={'score': 2.0})


class MismatchedScorer(FixtureScorer):
    def score(self, transaction):
        return super().score(transaction).model_copy(update={'transaction_id': 'TX-999'})


class FailingScorer(FixtureScorer):
    def score(self, transaction):
        raise RuntimeError('PRIVATE_SCORER at C:/private/accounts.json')


for base in ['http://127.0.0.1:8000', 'http://127.0.0.1:5173']:
    with httpx.Client(base_url=base, timeout=5, trust_env=False) as client:
        results = {}
        results['health'] = read(client, '/api/health', 200, 'Health')
        listing = read(client, '/api/cases', 200, 'CaseList')
        assert listing == read(client, '/api/cases', 200, 'CaseList')
        assert [item['case_id'] for item in listing['items']] == ['CASE-001', 'CASE-002', 'CASE-003']
        assert len({item['transaction_id'] for item in listing['items']}) == 3
        results['list'] = listing
        for item in listing['items']:
            path = f"/api/cases/{item['case_id']}"
            detail = read(client, path, 200, 'CaseDetail')
            assert detail == read(client, path, 200, 'CaseDetail')
            assessment = detail['risk_assessment']
            assert item['case_id'] == detail['case_id']
            assert item['transaction_id'] == detail['transaction']['transaction_id'] == assessment['transaction_id']
            assert item['score'] == assessment['score']
            assert item['score_source'] == assessment['source'] == 'fixture'
            assert assessment['scorer_version'] == 'fixture-v1'
            assert 'illustrative' in assessment['explanation'].lower()
            results[item['case_id']] = detail
        results['404'] = read(client, '/api/cases/CASE-999', 404, 'Error', 'case_not_found')
        for identifier in ['CASE-1', 'CASE-0001', 'case-001', 'CASE-ABC', 'CASE-001%0A']:
            results[f'422:{identifier}'] = read(client, f'/api/cases/{identifier}',
                                                422, 'Error', 'invalid_request')
        if base.endswith(':5173'):
            html = client.get('/')
            assert html.status_code == 200 and '/src/main.ts' in html.text
            for asset in ['/src/main.ts', '/src/views.ts', '/src/styles.css']:
                assert client.get(asset).status_code == 200
        REPORT['live'][base] = results

assert REPORT['live']['http://127.0.0.1:8000'] == REPORT['live']['http://127.0.0.1:5173']

with tempfile.TemporaryDirectory(prefix='fraudlens-t019-') as directory:
    empty = Path(directory) / 'empty.json'
    empty.write_text('[]', encoding='utf-8')
    with serve(create_app(settings=Settings(fixture_path=empty))) as base:
        with httpx.Client(base_url=base, timeout=5, trust_env=False) as client:
            REPORT['injected']['empty'] = read(client, '/api/cases', 200, 'CaseList')
            assert REPORT['injected']['empty'] == {'items': []}

for name, scorer in [('invalid_score', InvalidScorer()), ('wrong_transaction', MismatchedScorer()),
                     ('private_exception', FailingScorer())]:
    with serve(create_app(settings=Settings(), scorer=scorer)) as base:
        with httpx.Client(base_url=base, timeout=5, trust_env=False) as client:
            REPORT['injected'][name] = {
                path: read(client, path, 500, 'Error', 'internal_error')
                for path in ['/api/cases', '/api/cases/CASE-001']
            }

(ROOT / 'evidence/tasks/T019-responses.json').write_text(
    json.dumps(REPORT, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
print('PASS: real backend/proxy schemas, determinism, identity, 404/422, assets and 7 injected HTTP responses.')
print('Browser UI/console checks are not performed by this script.')
