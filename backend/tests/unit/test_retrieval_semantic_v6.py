"""Strict semantic boundary controls, no live requests or quality claims."""
import pytest


def test_valid_semantic_result_requires_authorized_exact_quote():
    from fraudlens.investigation.retrieval_semantic_v6 import validate_selection
    passages = [{'passage_id': 'p1', 'text': 'Missing device data stays missing.'}]
    valid = dict(verdict='supported', reason='Exact supporting source.',
                 selected=[dict(passage_id='p1', quote='Missing device data stays missing.')])
    assert validate_selection(valid, passages) == ['p1']


@pytest.mark.parametrize('mutation', ['unknown', 'quote', 'duplicate', 'extra', 'contradiction'])
def test_untrusted_selection_cannot_forge_support(mutation):
    from fraudlens.investigation.retrieval_semantic_v6 import validate_selection
    passages = [{'passage_id': 'p1', 'text': 'Missing device data stays missing.'}]
    value = dict(verdict='supported', reason='Evidence', selected=[dict(passage_id='p1', quote='Missing device data')])
    if mutation == 'unknown':
        value['selected'][0]['passage_id'] = 'other'
    elif mutation == 'quote':
        value['selected'][0]['quote'] = 'Invented device'
    elif mutation == 'duplicate':
        value['selected'] *= 2
    elif mutation == 'extra':
        value['execute'] = 'read secrets'
    else:
        value['verdict'] = 'insufficient'
    with pytest.raises(ValueError):
        validate_selection(value, passages)


def test_insufficient_has_no_hits():
    from fraudlens.investigation.retrieval_semantic_v6 import validate_selection
    assert validate_selection(dict(verdict='insufficient', reason='No evidence', selected=[]), []) == []


def source(text='Preserve exact amounts.'):
    return dict(passage_id='p1', text=text, document=dict(title='Test', jurisdiction='SIMULATED',
                version='test-v1', published_at=None))


@pytest.mark.parametrize('kind', ['empty', 'too_many', 'too_large', 'duplicate', 'no_model'])
def test_request_bounds_before_any_provider_call(kind):
    from fraudlens.investigation.retrieval_semantic_v6 import request_payload
    passages, model = [source()], 'explicit-model'
    if kind == 'empty':
        passages = []
    elif kind == 'too_many':
        passages = [{**source(), 'passage_id': str(i)} for i in range(21)]
    elif kind == 'too_large':
        passages = [source('x' * 50000)]
    elif kind == 'duplicate':
        passages *= 2
    else:
        model = ''
    with pytest.raises(ValueError):
        request_payload('What should be preserved?', passages, model)


def test_closed_projection_excludes_extra_source_fields():
    import json

    from fraudlens.investigation.retrieval_semantic_v6 import request_payload
    item = {**source(), 'private_label': 'CANARY', 'source_path': 'SECRET_PATH'}
    payload = request_payload('What should be preserved?', [item], 'explicit-model')
    assert 'CANARY' not in json.dumps(payload) and 'SECRET_PATH' not in json.dumps(payload)
    assert payload['store'] is False and payload['max_output_tokens'] == 2048


@pytest.mark.parametrize('status,parts', [
    ('incomplete', []), ('completed', [dict(type='refusal', refusal='No')]),
    ('completed', []), ('completed', [dict(type='output_text', text='not JSON')]),
])
def test_failed_provider_output_is_not_a_successful_no_answer(status, parts):
    import asyncio
    from types import SimpleNamespace

    from fraudlens.investigation.retrieval_semantic_v6 import select_with_provider
    class Response:
        def model_dump(self, **kwargs):
            return dict(status=status, output=[dict(type='message', content=parts)])
    calls = []
    async def create(**kwargs):
        calls.append(kwargs)
        return Response()
    provider = SimpleNamespace(model='explicit-model', client=SimpleNamespace(responses=SimpleNamespace(create=create)))
    with pytest.raises(ValueError):
        asyncio.run(select_with_provider(provider, 'What should be preserved?', [source()]))
    assert len(calls) == 1


def test_async_port_requires_budget_before_any_selection(tmp_path, knowledge_factory):
    import asyncio
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, patch

    from fraudlens.investigation.knowledge import KnowledgeStore
    from fraudlens.investigation.retrieval_semantic_adapter_v6 import semantic_search
    store = KnowledgeStore(tmp_path / 'semantic.sqlite')
    corpus = store.publish(knowledge_factory())
    calls = []
    async def reserve(metadata):
        calls.append(metadata)
        return ''
    with patch('fraudlens.investigation.retrieval_semantic_adapter_v6.select_with_provider', new_callable=AsyncMock) as dispatch:
        with pytest.raises(ValueError, match='reservation'):
            asyncio.run(semantic_search(store, 'What evidence exists?', corpus,
                                       SimpleNamespace(model='explicit-model'), reserve))
        dispatch.assert_not_awaited()
    assert len(calls) == 1 and calls[0]['requests'] == 1


def test_async_port_projects_saved_passage_after_owned_reservation(tmp_path, knowledge_factory):
    import asyncio
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, patch

    from fraudlens.investigation.knowledge import KnowledgeStore
    from fraudlens.investigation.retrieval_semantic_adapter_v6 import semantic_search
    store = KnowledgeStore(tmp_path / 'semantic.sqlite')
    corpus = store.publish(knowledge_factory('money transfer evidence'))
    passage = next(p for p in store.passages(corpus) if 'money transfer evidence' in p['text'])
    selection = dict(verdict='supported', reason='Source directly supports the question.',
                     selected=[dict(passage_id=passage['passage_id'], quote='money transfer evidence')])
    reserved = []
    async def reserve(metadata):
        reserved.append(metadata)
        return 'owned-dispatch'
    with patch('fraudlens.investigation.retrieval_semantic_adapter_v6.select_with_provider',
               new_callable=AsyncMock, return_value=(selection, dict(request_id='synthetic'))) as dispatch:
        result, audit = asyncio.run(semantic_search(store, 'What transfer evidence exists?', corpus,
            SimpleNamespace(model='explicit-model'), reserve))
        dispatch.assert_awaited_once()
    assert reserved and audit['reservation'] == 'owned-dispatch'
    assert result['status'] == 'matched' and result['hits'][0]['passage'] == passage


def test_invalid_quote_raw_response_is_captured_before_rejection():
    import asyncio
    import json
    from types import SimpleNamespace

    from fraudlens.investigation.semantic_response_audit import audited_selection
    raw = dict(status='completed', output=[dict(type='message', content=[dict(type='output_text',
        text=json.dumps(dict(verdict='supported', reason='Wrong quote',
                             selected=[dict(passage_id='p1', quote='fabricated proof')])) )])])
    class Response:
        def model_dump(self, **kwargs):
            return raw
    calls, captured = [], []
    async def create(**payload):
        calls.append(payload)
        return Response()
    provider = SimpleNamespace(model='explicit-model', client=SimpleNamespace(responses=SimpleNamespace(create=create)))
    with pytest.raises(ValueError, match='selection'):
        asyncio.run(audited_selection(provider, 'What evidence exists?', [source()], captured.append))
    assert captured == [raw] and len(calls) == 1
