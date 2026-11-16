"""Authored development regressions only: no credentials, references or live API."""
import asyncio
import json
import time

import httpx2
import pytest
from test_investigation_openai import LIMITS, messages, response
from test_investigation_workflow import create
from test_investigation_workflow import runtime as workflow_runtime

from fraudlens.investigation.knowledge import KnowledgeStore, KnowledgeUnavailable
from fraudlens.investigation.models import ROOT
from fraudlens.investigation.provider import OpenAIProvider, ProviderError, ScriptedProvider, Turn
from fraudlens.investigation.retrieval import search
from fraudlens.investigation.settings import InvestigationSettings

runtime = workflow_runtime


@pytest.mark.parametrize('fault,reason', [
    ('citations', 'citation_set_mismatch'),
    ('assertion', 'exact_assertion_mismatch'),
    ('quote', 'exact_quote_mismatch'),
    ('kind', 'observation_required'),
])
def test_repair_explains_local_rejection_and_revalidates(runtime, fault, reason):
    class Repairable(ScriptedProvider):
        broken = False

        async def next_turn(self, conversation, *args):
            turn = await super().next_turn(conversation, *args)
            if turn.kind != 'draft':
                return turn
            if not self.broken:
                self.broken = True
                draft = turn.draft
                if fault == 'citations':
                    draft['citations'].append('ev_' + 'f' * 32)
                elif fault == 'assertion':
                    draft['observed_facts'][0]['exact_assertions'][0]['value'] = '999999.00'
                elif fault == 'quote':
                    draft['observed_facts'][0]['quotes'] = [dict(
                        evidence_ref=draft['citations'][0], text='AUTHORED ABSENT QUOTE')]
                else:
                    draft['observed_facts'][0]['kind'] = 'hypothesis'
                return Turn('draft', draft=draft)
            assert conversation[-1] == dict(type='repair', code='output_invalid', reason=reason)
            assert args[-1]['tool_choice'] == 'none'
            return turn

    _, request, make = runtime
    service = make(provider=Repairable())
    run = create(service, request)
    result = asyncio.run(service.work_once())
    assert result['state'] == 'ready_for_review'
    assert result['budget']['repairs'] == 1
    assert result['budget']['provider_requests'] == 5
    repairs = [e for e in service.events(run['attempt_id']) if e['operation'] == 'repair']
    assert len(repairs) == 1 and repairs[0]['reason'] == reason
    assert service.binding(run['attempt_id'])['prompt'].startswith('# Investigation application prompt v3')


def test_unknown_validator_exception_never_enters_feedback_or_audit(runtime, monkeypatch):
    secret = 'AUTHORED-CANARY-private-exception'

    def reject(*args, **kwargs):
        raise ValueError(secret)

    monkeypatch.setattr('fraudlens.investigation.workflow.validate_report', reject)

    class Inspected(ScriptedProvider):
        async def next_turn(self, conversation, *args):
            if conversation[-1]['type'] == 'repair':
                assert conversation[-1]['reason'] == 'schema_invalid'
                assert secret not in json.dumps(conversation)
            return await super().next_turn(conversation, *args)

    _, request, make = runtime
    service = make(provider=Inspected())
    run = create(service, request)
    result = asyncio.run(service.work_once())
    assert result['failure']['code'] == 'output_invalid'
    assert result['budget']['repairs'] == 1
    assert secret not in json.dumps(service.events(run['attempt_id']))


def test_sdk_serializes_only_fixed_repair_guidance():
    seen = []

    def handler(request):
        body = json.loads(request.content)
        seen.append(body)
        assert 'citations must equal' in body['input'][-1]['content']
        assert 'evidence_refs' in body['input'][-1]['content']
        assert body['store'] is False and body['parallel_tool_calls'] is False
        return httpx2.Response(200, json=response())

    async def exercise():
        provider = OpenAIProvider('AUTHORED-NOT-REAL', 'authored-model',
                                  transport=httpx2.MockTransport(handler))
        try:
            await provider.next_turn(messages() + [dict(type='repair', code='output_invalid',
                reason='citation_set_mismatch')], definitions(), {}, LIMITS)
        finally:
            await provider.aclose()

    from fraudlens.investigation.tools import definitions
    asyncio.run(exercise())
    assert len(seen) == 1


@pytest.mark.parametrize('reason', ['PRIVATE-CANARY', {'private': 'value'}, None, ['citation_set_mismatch']])
def test_untrusted_repair_reason_is_rejected_before_sdk_dispatch(reason):
    from fraudlens.investigation.provider import project_conversation
    with pytest.raises(ProviderError, match='provider_input_invalid'):
        project_conversation(messages() + [dict(type='repair', code='output_invalid', reason=reason)])


def test_slow_cleanup_is_cancelled_within_remaining_attempt_time(runtime):
    class SlowClose(ScriptedProvider):
        cancelled = False

        async def aclose(self):
            try:
                await asyncio.sleep(10)
            finally:
                self.cancelled = True

    _, request, make = runtime
    provider = SlowClose()
    service = make(provider=provider, settings=InvestigationSettings(total_timeout_seconds=1))
    run = create(service, request)

    async def exercise():
        return await asyncio.wait_for(service.work_once(), timeout=2)

    started = time.monotonic()
    result = asyncio.run(exercise())
    assert time.monotonic() - started < 2
    assert result['state'] == 'ready_for_review' and provider.cancelled
    assert result['budget']['provider_requests'] == 4
    assert service.read(run['attempt_id'])['state'] == 'ready_for_review'
    assert any(e['operation'] == 'provider_cleanup' and e['status'] == 'timeout'
               for e in service.events(run['attempt_id']))


def test_cleanup_error_preserves_terminal_report_and_does_not_leak(runtime):
    class BrokenClose(ScriptedProvider):
        async def aclose(self):
            raise OSError('AUTHORED-CANARY-close-error')

    _, request, make = runtime
    service = make(provider=BrokenClose())
    run = create(service, request)
    result = asyncio.run(service.work_once())
    assert result['state'] == 'ready_for_review'
    events = service.events(run['attempt_id'])
    assert events[-1]['operation'] == 'provider_cleanup' and events[-1]['status'] == 'failed'
    assert 'AUTHORED-CANARY-close-error' not in json.dumps(events)


def test_last_provider_request_is_reserved_for_a_draft(runtime):
    from fraudlens.investigation.provider import scripted_draft

    class FinalDraft:
        calls = 0

        async def next_turn(self, conversation, tools, schema, limits):
            self.calls += 1
            if self.calls < 3:
                return Turn('tools', calls=(dict(call_id=f'call_{self.calls}',
                            name='get_case_facts', arguments={}),))
            assert limits['tool_choice'] == 'none'
            return Turn('draft', draft=scripted_draft(conversation, 'grounded'))

    _, request, make = runtime
    service = make(provider=FinalDraft(), settings=InvestigationSettings(max_provider_requests=3))
    create(service, request)
    result = asyncio.run(service.work_once())
    assert result['state'] == 'ready_for_review'
    assert result['budget']['provider_requests'] == 3
    assert result['budget']['tool_calls'] == 2


def test_external_cancellation_during_cleanup_is_not_swallowed(runtime):
    class Closing(ScriptedProvider):
        async def aclose(self):
            entered.set()
            await asyncio.Event().wait()

    _, request, make = runtime
    service = make(provider=Closing())
    run = create(service, request)

    async def exercise():
        nonlocal entered
        entered = asyncio.Event()
        task = asyncio.create_task(service.work_once())
        await entered.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    entered = None
    asyncio.run(exercise())
    assert service.read(run['attempt_id'])['state'] == 'ready_for_review'
    assert not any(e['operation'] == 'provider_cleanup' for e in service.events(run['attempt_id']))


@pytest.fixture
def bilingual_search(tmp_path, knowledge_factory):
    store = KnowledgeStore(tmp_path / 'bilingual.sqlite')
    corpus = store.publish(knowledge_factory('missing evidence facts review synthetic'))
    glossary = json.loads((ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/glossary.json').read_text(encoding='utf-8'))
    config = dict(configuration_version=4, algorithm='bm25', k1=1.2, b=.75,
                  adequacy_cutoff=0.0, maximum_results=5, variant='title_glossary',
                  query_normalization='sr_cyrillic_to_latin_v1', glossary=glossary)
    return store, corpus, config


@pytest.mark.parametrize('latin,cyrillic', [
    ('nedostaje dokaz', 'недостаје доказ'),
    ('NEDOSTAJUĆE ČINJENICE', 'НЕДОСТАЈУЋЕ ЧИЊЕНИЦЕ'),
    ('pregled dokazi', 'преглед докази'),
    ('sintetički', 'синтетички'),
])
def test_script_equivalence_with_reviewed_glossary(bilingual_search, latin, cyrillic):
    store, corpus, config = bilingual_search
    version = store.save_configuration(config)
    latin_result = search(store, latin, corpus, version)
    cyrl_result = search(store, cyrillic, corpus, version)
    assert latin_result['status'] == cyrl_result['status'] == 'matched'
    assert latin_result['hits'] == cyrl_result['hits']
    assert cyrl_result['query'] == cyrillic


def test_legacy_retrieval_remains_unchanged_and_unknown_words_stay_no_match(bilingual_search):
    store, corpus, config = bilingual_search
    candidate = store.save_configuration(config)
    legacy = store.save_configuration({k: v for k, v in config.items() if k != 'query_normalization'})
    assert search(store, 'доказ', corpus, legacy)['status'] == 'no_match'
    assert search(store, 'доказ', corpus, candidate)['status'] == 'matched'
    assert search(store, 'непостојећаречxyz', corpus, candidate)['status'] == 'no_match'
    assert search(store, 'evidence', corpus, candidate)['hits'] == search(store, 'evidence', corpus, legacy)['hits']


@pytest.mark.parametrize('policy', ['guessed_policy', None, 1, {}])
def test_unknown_query_normalization_fails_closed(bilingual_search, policy):
    store, corpus, config = bilingual_search
    version = store.save_configuration({**config, 'query_normalization': policy})
    with pytest.raises(KnowledgeUnavailable):
        search(store, 'evidence', corpus, version)
