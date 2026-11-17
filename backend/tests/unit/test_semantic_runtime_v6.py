"""Network-free durable semantic runtime integration controls."""
import asyncio
import json

import pytest

from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.settings import InvestigationSettings


@pytest.fixture
def runtime(tmp_path, knowledge_factory):
    from fraudlens.investigation.semantic_runtime import SemanticSearchService
    store = KnowledgeStore(tmp_path / 'runtime.sqlite')
    store.publish(knowledge_factory('money transfer evidence'))
    settings = InvestigationSettings(enabled=True, semantic_retrieval=True, provider='openai',
        model='synthetic-model', api_key='synthetic-key', store=store.repository.path)
    calls = []
    async def select(provider, query, passages):
        calls.append(query)
        return dict(verdict='insufficient', reason='No actual customer records.', selected=[]), dict(
            returned_model='synthetic-model', request_id='synthetic', usage={}, raw_response={})
    class Provider:
        model = 'synthetic-model'
        async def aclose(self):
            pass
    return SemanticSearchService(store, settings, provider_factory=Provider, selector=select), calls


def test_paid_search_is_idempotent_and_status_is_free(runtime):
    service, calls = runtime
    async def run():
        first = await service.search('Which customer sent this?', 'key-a')
        second = await service.search('Which customer sent this?', 'key-a')
        assert first == second and first['status'] == 'completed'
        assert first['result']['status'] == 'no_match'
        assert service.status('key-a')['provider_requests'] == 1
        assert len(calls) == 1
        with pytest.raises(ValueError, match='conflict'):
            await service.search('Different question', 'key-a')
    asyncio.run(run())


def test_cancel_during_call_cannot_publish(runtime):
    service, calls = runtime
    async def run():
        started, release = asyncio.Event(), asyncio.Event()
        async def waiting(*args):
            started.set()
            await release.wait()
            return dict(verdict='insufficient', reason='No records', selected=[]), {}
        service.selector = waiting
        task = asyncio.create_task(service.search('Which customer?', 'key-b'))
        await started.wait()
        assert service.cancel('key-b')['status'] == 'cancelled'
        release.set()
        result = await task
        assert result['status'] == 'cancelled' and result['result'] is None
        assert service.status('key-b')['provider_requests'] == 1
    asyncio.run(run())


def test_worker_semantic_dispatch_shares_attempt_budget(tmp_path, knowledge_factory):
    from uuid import uuid4

    from fraudlens.investigation.context import CaseContextReader
    from fraudlens.investigation.provider import ScriptedProvider
    from fraudlens.investigation.workflow import InvestigationService
    store = KnowledgeStore(tmp_path / 'worker.sqlite')
    store.publish(knowledge_factory('missing evidence money'))
    store.save_configuration(json.loads(open('data/knowledge/fraudlens-aml-knowledge-v1/retrieval.json').read()))
    settings = InvestigationSettings(semantic_retrieval=True, provider='openai', model='synthetic-model', api_key='synthetic')
    provider = ScriptedProvider()
    provider.model = 'synthetic-model'
    service = InvestigationService(store.repository, store, settings, provider_factory=lambda binding: provider)
    async def select(*args):
        return dict(verdict='insufficient', reason='No applicable guidance.', selected=[]), dict(
            returned_model='synthetic-model', request_id='synthetic', usage={})
    service.semantic_selector = select
    context = CaseContextReader().resolve('CASE-001', 'fixture', None)
    request = {k: context[k] for k in ('case_id', 'source_mode', 'snapshot_ref')}
    created = service.create(request, 'analyst', str(uuid4()))
    assert 'concise English' in service.binding(created['attempt_id'])['prompt']
    done = asyncio.run(service.work_once())
    assert done['state'] == 'ready_for_review'
    assert done['budget']['provider_requests'] == 5  # 4 ordinary+1 semantic
    assert done['budget']['tool_calls'] == 3


def test_explicit_semantic_api_closed_request_and_replay(runtime, monkeypatch):
    from uuid import uuid4

    from fastapi.testclient import TestClient

    from fraudlens.main import create_app
    service, calls = runtime
    monkeypatch.setenv('INVESTIGATION_ENABLED', 'true')
    monkeypatch.setenv('INVESTIGATION_SEMANTIC_RETRIEVAL', 'true')
    monkeypatch.setenv('INVESTIGATION_PROVIDER', 'openai')
    monkeypatch.setenv('OPENAI_MODEL', 'synthetic-model')
    monkeypatch.setenv('OPENAI_API_KEY', 'synthetic-key')
    app = create_app()
    app.state.semantic_search_service = service
    headers = {'Idempotency-Key': str(uuid4())}
    with TestClient(app) as client:
        first = client.post('/api/knowledge/semantic-search', json=dict(query='Which customer?'), headers=headers)
        assert first.status_code == 200
        assert first.json()['status'] == 'completed' and first.json()['result']['status'] == 'no_match'
        assert 'raw_response' not in first.json().get('audit', {})
        assert client.post('/api/knowledge/semantic-search', json=dict(query='Which customer?'), headers=headers).json() == first.json()
        assert client.get('/api/knowledge/semantic-search/status', headers=headers).json() == first.json()
        assert len(calls) == 1
        bad = client.post('/api/knowledge/semantic-search', json=dict(query='Which customer?', model='forged'), headers=headers)
        assert bad.status_code == 422 and len(calls) == 1
        external = client.post('/api/knowledge/semantic-search', json=dict(query='Which customer?'), headers={**headers, 'Origin': 'https://evil.invalid'})
        assert external.status_code == 403


def test_api_store_budget_is_not_reset_by_reopen(runtime):
    from fraudlens.investigation.semantic_runtime import SemanticSearchService
    service, calls = runtime
    service.settings = service.settings.model_copy(update=dict(max_semantic_requests=1))
    asyncio.run(service.search('Which customer?', 'one'))
    reopened = SemanticSearchService(service.knowledge, service.settings,
        provider_factory=service.provider_factory, selector=service.selector)
    assert reopened.status('one')['status'] == 'completed'
    with pytest.raises(ValueError, match='budget'):
        asyncio.run(reopened.search('Which other customer?', 'two'))
    assert len(calls) == 1


def test_api_timeout_is_failure_not_correct_no_match(runtime):
    service, _ = runtime
    service.settings = service.settings.model_copy(update=dict(request_timeout_seconds=1))
    async def slow(*args):
        await asyncio.sleep(2)
    service.selector = slow
    result = asyncio.run(service.search('Which customer?', 'timeout'))
    assert result['status'] == 'failed' and result['result'] is None
    assert result['provider_requests'] == 1 and result['outcome_unknown']


def worker_service(tmp_path, knowledge_factory, **overrides):
    from fraudlens.investigation.context import CaseContextReader
    from fraudlens.investigation.provider import ScriptedProvider
    from fraudlens.investigation.workflow import InvestigationService
    store = KnowledgeStore(tmp_path / 'bounded-worker.sqlite')
    store.publish(knowledge_factory('missing evidence money'))
    store.save_configuration(json.loads(open('data/knowledge/fraudlens-aml-knowledge-v1/retrieval.json').read()))
    settings = InvestigationSettings(semantic_retrieval=True, provider='openai',
        model='synthetic-model', api_key='synthetic', **overrides)
    provider = ScriptedProvider()
    provider.model = 'synthetic-model'
    service = InvestigationService(store.repository, store, settings, provider_factory=lambda binding: provider)
    context = CaseContextReader().resolve('CASE-001', 'fixture', None)
    return service, {k: context[k] for k in ('case_id', 'source_mode', 'snapshot_ref')}


def test_worker_cancel_during_semantic_wait_cannot_publish(tmp_path, knowledge_factory):
    from uuid import uuid4
    service, request = worker_service(tmp_path, knowledge_factory)
    async def run():
        started, release = asyncio.Event(), asyncio.Event()
        async def waiting(*args):
            started.set()
            await release.wait()
            return dict(verdict='insufficient', reason='No guidance', selected=[]), {}
        service.semantic_selector = waiting
        run = service.create(request, 'analyst', str(uuid4()))
        task = asyncio.create_task(service.work_once())
        await started.wait()
        view = service.read(run['attempt_id'])
        service.cancel(run['attempt_id'], view['revision'], 'analyst', str(uuid4()))
        release.set()
        done = await task
        assert done['state'] == 'cancelled' and done['report'] is None
        assert done['budget']['provider_requests'] == 4
        assert not any(e['kind'] == 'procedure' for e in service.evidence(run['attempt_id']))
    asyncio.run(run())


def test_worker_semantic_and_draft_share_lowered_cap(tmp_path, knowledge_factory):
    from uuid import uuid4
    service, request = worker_service(tmp_path, knowledge_factory, max_provider_requests=4)
    async def insufficient(*args):
        return dict(verdict='insufficient', reason='No guidance', selected=[]), {}
    service.semantic_selector = insufficient
    service.create(request, 'analyst', str(uuid4()))
    done = asyncio.run(service.work_once())
    assert done['state'] == 'failed' and done['failure']['code'] == 'budget_exhausted'
    assert done['budget']['provider_requests'] == 4 and done['report'] is None


def test_worker_source_change_during_semantic_call_rejects_result(tmp_path, knowledge_factory):
    from uuid import uuid4
    service, request = worker_service(tmp_path, knowledge_factory)
    async def changed(*args):
        previous = service.context_reader.resolve
        def different(*args):
            return {**previous(*args), 'context_revision': 'b' * 64}
        service.context_reader.resolve = different
        return dict(verdict='insufficient', reason='No guidance', selected=[]), {}
    service.semantic_selector = changed
    run = service.create(request, 'analyst', str(uuid4()))
    done = asyncio.run(service.work_once())
    assert done['state'] == 'failed' and done['report'] is None
    assert not any(e['kind'] == 'procedure' for e in service.evidence(run['attempt_id']))


def test_worker_semantic_positive_preserves_citation_and_report_path(tmp_path, knowledge_factory):
    from uuid import uuid4
    service, request = worker_service(tmp_path, knowledge_factory)
    async def relevant(provider, query, passages):
        passage = next(p for p in passages if 'missing evidence money' in p['text'])
        return dict(verdict='supported', reason='Relevant synthetic test guidance', selected=[
            dict(passage_id=passage['passage_id'], quote='missing evidence money')]), dict(
                returned_model='synthetic-model', request_id='synthetic-positive', usage={})
    service.semantic_selector = relevant
    run = service.create(request, 'analyst', str(uuid4()))
    done = asyncio.run(service.work_once())
    assert done['state'] == 'ready_for_review' and done['budget']['provider_requests'] == 5
    procedures = [e for e in service.evidence(run['attempt_id']) if e['kind'] == 'procedure']
    assert len(procedures) == 1 and procedures[0]['evidence_id'] in done['report']['draft']['citations']


def test_invalid_worker_semantic_query_spends_no_extra_call(tmp_path, knowledge_factory):
    from uuid import uuid4

    from fraudlens.investigation.provider import Turn
    service, request = worker_service(tmp_path, knowledge_factory)
    class InvalidProvider:
        async def next_turn(self, *args):
            return Turn('tools', calls=(dict(call_id='bad', name='search_procedures',
                        arguments=dict(query='SELECT password FROM accounts')),))
    service.provider_factory = lambda binding: InvalidProvider()
    async def forbidden(*args):
        pytest.fail('Invalid tool must not dispatch semantic provider')
    service.semantic_selector = forbidden
    service.create(request, 'analyst', str(uuid4()))
    done = asyncio.run(service.work_once())
    assert done['state'] == 'failed' and done['budget']['provider_requests'] == 1


def test_rejected_sdk_quote_keeps_server_audit_and_never_redispatches(runtime):
    from types import SimpleNamespace
    service, _ = runtime
    passage = service.knowledge.passages(service.knowledge.latest('corpus'))[0]
    raw = dict(status='completed', output=[dict(type='message', content=[dict(type='output_text',
        text=json.dumps(dict(verdict='supported', reason='Incorrect quote', selected=[
            dict(passage_id=passage['passage_id'], quote='Invented unsupported quotation')])) )])])
    calls = []
    class Response:
        def model_dump(self, **kwargs):
            return raw
    async def create(**kwargs):
        calls.append(1)
        return Response()
    class Provider:
        model = 'synthetic-model'
        client = SimpleNamespace(responses=SimpleNamespace(create=create))
        async def aclose(self):
            pass
    service.selector = None
    service.provider_factory = Provider
    result = asyncio.run(service.search('What procedure applies?', 'bad-quote'))
    assert result['status'] == 'failed' and result['result'] is None
    with service.repo.connection() as db:
        saved = db.execute('SELECT response_json FROM semantic_search_dispatch_audit').fetchall()
    assert len(saved) == 1 and json.loads(saved[0][0]) == raw
    assert asyncio.run(service.search('What procedure applies?', 'bad-quote')) == result
    assert len(calls) == 1
