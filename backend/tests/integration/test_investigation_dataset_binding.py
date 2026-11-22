"""Published v2 Cases and investigation must bind to the same public context."""

import asyncio
import json
import sqlite3
from pathlib import Path
from uuid import uuid4

import httpx2
import pytest
from backend.tests.phase7_samples import VERSION, entry
from fastapi.testclient import TestClient

from fraudlens.data_store import RunStore
from fraudlens.investigation import history_index
from fraudlens.investigation.context import outbound_context
from fraudlens.investigation.dataset import DatasetReader
from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import SCHEMA, canonical
from fraudlens.investigation.provider import OpenAIProvider
from fraudlens.investigation.settings import load_settings
from fraudlens.investigation.tools import definitions, facts
from fraudlens.investigation.workflow import InvestigationService
from fraudlens.main import create_app
from fraudlens.settings import Settings

RUN = 'run_test_1'
ROUTE = '/api/investigation/runs'


@pytest.fixture
def dataset_runtime(tmp_path, knowledge_factory, monkeypatch):
    path = tmp_path / 'scored.sqlite'
    case_id, tx, risk = entry()
    store = RunStore(path)
    store.begin_run(RUN, VERSION, 'rules', 'rules-v1', None, '0.5', 1)
    store.append(RUN, case_id, tx, risk)
    store.complete(RUN)
    store.activate(RUN, 'rules')
    store.close()

    knowledge = KnowledgeStore(tmp_path / 'investigation.sqlite')
    knowledge.publish(knowledge_factory('missing evidence money'))
    knowledge.save_configuration(json.loads(
        Path('data/knowledge/fraudlens-aml-knowledge-v1/retrieval.json').read_text()))
    for key, value in {
        'ENABLED': 'true', 'PROVIDER': 'test', 'TEST_SCENARIO': 'grounded',
        'SEMANTIC_RETRIEVAL': 'false', 'SOURCE': 'dataset',
        'STORE': knowledge.repository.path, 'DATASET_RUN_STORE': path,
        'DATASET_SCORE_SOURCE': 'rules', 'DATASET_STORE': tmp_path / 'missing-source.sqlite',
    }.items():
        monkeypatch.setenv(f'INVESTIGATION_{key}', str(value))
    monkeypatch.delenv('INVESTIGATION_DATASET_HISTORY_INDEX', raising=False)
    monkeypatch.delenv('INVESTIGATION_DATASET_HISTORY_INDEX_SHA256', raising=False)
    service = InvestigationService(knowledge.repository, knowledge, load_settings())
    app = create_app(Settings(mode='dataset', scorer='rules', run_store_path=path))
    app.state.investigation_service = service
    with TestClient(app) as client:
        yield client, service, path, dict(case_id=case_id, source_mode='dataset', snapshot_ref=RUN)


def create(client, request):
    return client.post(ROUTE, json=request, headers={'Idempotency-Key': str(uuid4())})


@pytest.mark.parametrize('parallel', [True, False])
def test_dataset_history_at_provider_boundary_retains_events_and_exact_facts(dataset_runtime, parallel):
    client, service, _, request = dataset_runtime
    attempt = create(client, request).json()
    context = service.context(attempt['attempt_id'])
    messages = [dict(type='context', data=outbound_context(context, attempt['run_id']))]
    history = []
    for side in ('sender', 'receiver'):
        body = dict(account_side=side, availability='available', eligible_count=40, returned_count=17,
                    truncated=True, totals={'US Dollar': '500.00'}, events=[
                        dict(transaction_id=f'D{number:032x}', account_alias='account_' + 'c' * 24,
                             occurred_at='2022-08-31T23:00:00Z', event_time_raw='2022/08/31 23:00',
                             amount='100.00', currency='US Dollar', direction='outgoing',
                             time_basis='assumed_utc_for_synthetic_benchmark')
                        for number in range(17)
                    ])
        evidence = dict(evidence_id='ev_' + uuid4().hex, kind='history', text=canonical(body).decode(),
                        facts=facts(body), returned_count=17, eligible_count=40, truncated=True)
        history.append(evidence)
        messages.append(dict(type='tool_result', call_id=side, result=dict(
            status='completed', evidence=[evidence], returned_count=17, eligible_count=40, truncated=True)))
    sent = []

    def respond(request):
        sent.append((len(request.content), json.loads(request.content)))
        return httpx2.Response(200, json=dict(status='completed', model='unit-test', output=[]))

    async def turn():
        adapter = OpenAIProvider('local-test-key', 'unit-test', transport=httpx2.MockTransport(respond),
                                 parallel_tools=parallel)
        try:
            return await adapter.next_turn(messages, definitions(), SCHEMA['$defs']['ReportDraft'],
                dict(max_input_bytes=36000 if parallel else 48000, max_output_tokens=4096,
                     max_response_bytes=2097152, request_timeout=10))
        finally:
            await adapter.aclose()

    before = canonical(messages)
    assert asyncio.run(turn()).kind == 'draft'
    assert canonical(messages) == before
    (size, payload), = sent
    assert size <= (36000 if parallel else 48000)
    for item, source in zip(payload['input'][1:], history, strict=True):
        returned, = json.loads(item['output'])['evidence']
        assert returned['text'] == source['text']
        assert returned['eligible_count'] == 40
        assert returned['returned_count'] == 17 and returned['truncated'] is True
        assert returned['facts'] == [fact for fact in source['facts']
                                     if not parallel or not fact['path'].startswith('events.')]


@pytest.mark.parametrize('history_available', [True, False])
def test_published_case_completes_with_grounded_facts_and_history_status(
        dataset_runtime, history_available):
    client, service, _, request = dataset_runtime
    if history_available:
        with sqlite3.connect(service.settings.dataset_store) as db:
            db.executescript("""
                CREATE TABLE active_dataset (singleton, version);
                CREATE TABLE dataset_versions (id, rejected_records, status);
                CREATE TABLE operational_events (version, transaction_id, payload_json);
            """)
            db.execute('INSERT INTO active_dataset VALUES (1, ?)', (VERSION,))
            db.execute("INSERT INTO dataset_versions VALUES (?, 0, 'complete')", (VERSION,))
            db.execute('INSERT INTO operational_events VALUES (?, ?, ?)', (
                VERSION, 'D' + '2' * 32, json.dumps({'event_time_utc': '2022-09-01T00:00:00Z'}),
            ))
    case_id = request['case_id']
    detail = client.get(f'/api/cases/{case_id}', params={'snapshot': RUN})
    listing = client.get(ROUTE, params={'case_id': case_id})
    response = create(client, request)
    assert (detail.status_code, listing.status_code, response.status_code) == (200, 200, 202)
    run = response.json()
    context = service.context(run['attempt_id'])
    assert context['source_payload'] == detail.json()
    assert context['source_mode'] == run['source_mode'] == 'dataset'
    assert context['snapshot_ref'] == listing.headers['x-investigation-snapshot'] == RUN
    assert context['context_revision'] == listing.headers['x-investigation-context'] == run['context_revision']
    availability = 'available' if history_available else 'unavailable'
    assert context['history']['availability'] == availability
    history = service.history_reader.read(context, 'sender')
    assert history['availability'] == availability
    assert history['eligible_count'] == (0 if history_available else None)
    done = asyncio.run(service.work_once())
    evidence = service.evidence(run['attempt_id'])
    item = next(item for item in evidence if item['kind'] == 'history')
    assert item['history']['availability'] == availability
    assert item['eligible_count'] == (0 if history_available else None)
    assert done['state'] == ('ready_for_review' if history_available else 'needs_information')
    draft = done['report']['draft']
    assert draft['observed_facts'][0]['exact_assertions'][0]['path'] == 'transaction.paid.amount'
    if not history_available:
        assert any('Istorija nije dostupna' in text for text in draft['limitations'])


@pytest.mark.parametrize(('change', 'status', 'code'), [
    ({'case_id': 'C' + 'f' * 32}, 404, 'case_not_found'),
    ({'case_id': 'CASE-001'}, 404, 'case_not_found'),
    ({'case_id': 'CASE-001', 'source_mode': 'fixture'}, 503, 'context_unavailable'),
    ({'snapshot_ref': 'run_other'}, 409, 'stale_snapshot'),
])
def test_rejects_unbound_create_without_storing_a_run(dataset_runtime, change, status, code):
    client, service, _, request = dataset_runtime
    response = create(client, {**request, **change})
    assert response.status_code == status
    assert response.json()['error']['code'] == code
    with service.repo.connection() as db:
        assert db.execute('SELECT count(*) FROM investigation_runs').fetchone()[0] == 0


@pytest.mark.parametrize('field,value', [
    ('score', 0.99), ('published_score', 0.99), ('scorer_version', 'rules-other'),
    ('transaction_id', 'D' + 'f' * 32), ('run_id', 'run_other'),
])
def test_rejects_mismatched_published_assessment(dataset_runtime, field, value):
    client, service, path, request = dataset_runtime
    with sqlite3.connect(path) as db:
        # Deliberately corrupt only the temporary database to exercise the consumer's guard.
        db.execute('DROP TRIGGER immutable_scored_update')
        if field == 'published_score':
            db.execute('UPDATE scored_assessments SET score=?', (value,))
        else:
            risk_json = db.execute('SELECT assessment_json FROM scored_assessments').fetchone()[0]
            risk = {**json.loads(risk_json), field: value}
            db.execute('UPDATE scored_assessments SET assessment_json=?', (json.dumps(risk),))
    response = create(client, request)
    assert response.status_code == 503
    assert response.json()['error']['code'] == 'context_unavailable'
    with service.repo.connection() as db:
        assert db.execute('SELECT count(*) FROM investigation_runs').fetchone()[0] == 0


def test_dataset_list_never_reads_fixture_and_checks_revision(dataset_runtime):
    client, _, _, request = dataset_runtime
    response = client.get(ROUTE, params={'case_id': 'CASE-001'})
    assert response.status_code == 404
    assert response.json()['error']['code'] == 'case_not_found'
    response = client.get(ROUTE, params={
        'case_id': request['case_id'], 'context_revision': 'e' * 64,
    })
    assert response.status_code == 409
    assert response.json()['error']['code'] == 'stale_snapshot'


def test_history_index_reuses_validation_across_readers_and_checks_replacement(
        dataset_runtime, tmp_path, monkeypatch):
    _, service, scored, request = dataset_runtime
    source = service.settings.dataset_store
    with sqlite3.connect(source) as db:
        db.executescript("""
            CREATE TABLE active_dataset (singleton, version);
            CREATE TABLE dataset_versions (id, rejected_records, status);
            CREATE TABLE operational_events (version, transaction_id, payload_json);
        """)
        db.execute('INSERT INTO active_dataset VALUES (1, ?)', (VERSION,))
        db.execute("INSERT INTO dataset_versions VALUES (?, 0, 'complete')", (VERSION,))
    index = tmp_path / 'history.sqlite'
    digest = history_index.prepare_history_index(source, index)['index_sha256']
    hashed = []
    file_digest = history_index.file_digest

    def record(path):
        hashed.append(path)
        return file_digest(path)

    monkeypatch.setattr(history_index, 'file_digest', record)
    for _ in range(2):
        reader = DatasetReader(scored, source, 'rules', history_index=index,
                               history_index_sha256=digest)
        assert reader.resolve(request['case_id'], RUN)['history']['availability'] == 'unavailable'
    assert hashed == [index, source]
    with index.open('ab') as stream:
        stream.write(b'changed')
    with pytest.raises(ValueError, match='stale_snapshot'):
        reader.resolve(request['case_id'], RUN)
