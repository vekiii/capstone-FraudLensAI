"""Bounded persisted orchestration, actual tool dispatch, controlled failures."""
import asyncio
import json
import time
from pathlib import Path
from uuid import uuid4

import pytest

from fraudlens.investigation.context import CaseContextReader
from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import validate
from fraudlens.investigation.provider import ProviderError, ScriptedProvider, Turn
from fraudlens.investigation.settings import InvestigationSettings
from fraudlens.investigation.workflow import InvestigationService


@pytest.fixture
def runtime(tmp_path, knowledge_factory):
    knowledge = KnowledgeStore(tmp_path / 'runtime.sqlite')
    knowledge.publish(knowledge_factory('missing evidence money'))
    config = json.loads(Path('data/knowledge/fraudlens-aml-knowledge-v1/retrieval.json').read_text())
    knowledge.save_configuration(config)
    context = CaseContextReader().resolve('CASE-001', 'fixture', None)
    request = dict(case_id=context['case_id'], source_mode='fixture', snapshot_ref=context['snapshot_ref'])
    def make(scenario='grounded', provider=None, settings=None):
        return InvestigationService(knowledge.repository, knowledge, settings or InvestigationSettings(),
            provider_factory=(lambda binding: provider or ScriptedProvider(scenario)))
    return knowledge, request, make


def create(service, request):
    return service.create(request, 'local-analyst', str(uuid4()))


def test_creation_and_get_never_dispatch_provider(runtime):
    _, request, make = runtime
    class Forbidden:
        async def next_turn(self, *args):
            pytest.fail('Creation/GET must not invoke provider')
    service = make(provider=Forbidden())
    run = create(service, request)
    validate('RunView', run)
    assert run['state'] == 'created' and run['budget']['provider_requests'] == 0
    assert service.read(run['attempt_id']) == run


def test_full_grounded_flow_persists_actual_three_tools_and_report(runtime):
    knowledge, request, make = runtime
    service = make()
    run = create(service, request)
    result = asyncio.run(service.work_once())
    validate('RunView', result)
    assert result['attempt_id'] == run['attempt_id'] and result['state'] == 'ready_for_review'
    assert result['budget']['provider_requests'] == 4 and result['budget']['tool_calls'] == 3
    assert [step['name'] for step in result['trace']] == [
        'get_case_facts', 'get_account_history', 'search_procedures']
    assert all(step['status'] == 'completed' for step in result['trace'])
    assert result['report']['semantic_review'] == 'not_reviewed' and result['review'] is None
    assert 'TEST provider' in result['report']['draft']['limitations'][0]
    assert service.read(run['attempt_id']) == result
    assert asyncio.run(service.work_once()) is None
    with knowledge.repository.connection() as db:
        assert db.execute('SELECT count(*) FROM provider_dispatches WHERE outcome=?', ('completed',)).fetchone()[0] == 4
        assert db.execute('SELECT count(*) FROM evidence_items').fetchone()[0] >= 3


@pytest.mark.parametrize('scenario,state,code', [('needs_information', 'needs_information', None),
    ('invalid_citation', 'failed', 'output_invalid'), ('refusal', 'failed', 'provider_refusal'),
    ('incomplete', 'failed', 'provider_incomplete')])
def test_explicit_outcomes_and_single_repair(runtime, scenario, state, code):
    _, request, make = runtime
    service = make(scenario)
    run = create(service, request)
    result = asyncio.run(service.work_once())
    assert result['state'] == state
    assert (result['failure']['code'] if result['failure'] else None) == code
    assert result['budget']['repairs'] == (1 if scenario == 'invalid_citation' else 0)
    if state == 'failed':
        assert result['report'] is None
    else:
        assert result['report']['draft']['limitations']
    assert result['attempt_id'] == run['attempt_id']


def test_reserve_before_dispatch_and_do_not_hold_sqlite_lock_during_provider_io(runtime):
    knowledge, request, make = runtime
    class Inspected(ScriptedProvider):
        async def next_turn(self, *args):
            with knowledge.repository.transaction() as db:
                requests = db.execute('SELECT count(*) FROM provider_dispatches WHERE outcome=?', ('pending',)).fetchone()[0]
                assert requests == 1
            return Turn('refusal')
    service = make(provider=Inspected())
    create(service, request)
    assert asyncio.run(service.work_once())['failure']['code'] == 'provider_refusal'


def test_eight_request_budget_and_twelve_tool_budget(runtime):
    _, request, make = runtime
    class Loop:
        def __init__(self, count):
            self.n, self.count = 0, count
        async def next_turn(self, *args):
            calls = tuple(dict(call_id=f'call_{self.n + i}', name='get_case_facts', arguments={})
                          for i in range(self.count))
            self.n += self.count
            return Turn('tools', calls=calls)
    service = make(provider=Loop(1))
    create(service, request)
    result = asyncio.run(service.work_once())
    assert result['budget']['provider_requests'] == 8
    assert result['failure']['code'] == 'budget_exhausted'
    service = make(provider=Loop(12))
    create(service, request)
    result = asyncio.run(service.work_once())
    assert result['budget']['tool_calls'] == 12
    assert result['failure']['code'] == 'budget_exhausted'


def test_one_transient_retry_and_no_access_retry(runtime):
    _, request, make = runtime
    class Broken:
        def __init__(self, access=False):
            self.calls, self.access = 0, access
        async def next_turn(self, *args):
            self.calls += 1
            raise ProviderError('provider_access' if self.access else 'provider_failure',
                                retryable=not self.access)
    for access, expected in [(False, 2), (True, 1)]:
        provider = Broken(access)
        service = make(provider=provider)
        create(service, request)
        result = asyncio.run(service.work_once())
        assert provider.calls == expected
        assert result['budget']['transient_retries'] == (0 if access else 1)
        assert result['budget']['provider_requests'] == expected


def test_deadline_is_hard_and_counts_wait_time(runtime):
    _, request, make = runtime
    class Slow:
        async def next_turn(self, *args):
            await asyncio.sleep(30)
            pytest.fail('A timed-out request must be cancelled')
    service = make(provider=Slow(), settings=InvestigationSettings(total_timeout_seconds=1))
    create(service, request)
    start = time.monotonic()
    result = asyncio.run(service.work_once())
    assert time.monotonic() - start < 3
    assert result['state'] == 'failed' and result['failure']['code'] == 'budget_exhausted'
    assert result['failure']['outcome_unknown'] is True


def test_generated_unknown_tool_has_no_authority(runtime):
    knowledge, request, make = runtime
    class BadTool:
        async def next_turn(self, *args):
            return Turn('tools', calls=({'call_id': 'bad', 'name': 'execute_sql',
                                        'arguments': {'sql': 'SELECT * FROM labels'}},))
    service = make(provider=BadTool())
    create(service, request)
    result = asyncio.run(service.work_once())
    assert result['state'] == 'failed' and result['budget']['tool_calls'] == 0
    with knowledge.repository.connection() as db:
        assert db.execute('SELECT count(*) FROM evidence_items').fetchone()[0] == 0


def test_context_and_corpus_versions_are_pinned_at_creation(runtime):
    knowledge, request, make = runtime
    service = make()
    original = create(service, request)
    # The worker must keep the created binding even after active config changes.
    config = knowledge.configuration(original['retrieval_version'])
    config['adequacy_cutoff'] = 999
    new = knowledge.save_configuration(config)
    assert new != original['retrieval_version']
    result = asyncio.run(service.work_once())
    assert result['retrieval_version'] == original['retrieval_version']
    assert result['corpus_version'] == original['corpus_version']


def test_drafting_state_is_durable_before_report_validation(runtime, monkeypatch):
    import fraudlens.investigation.workflow as module
    _, request, make = runtime
    service = make()
    run = create(service, request)
    original = module.validate_report
    def inspected(*args, **kwargs):
        assert service.repo.get(run['attempt_id'])['state'] == 'drafting'
        return original(*args, **kwargs)
    monkeypatch.setattr(module, 'validate_report', inspected)
    assert asyncio.run(service.work_once())['state'] == 'ready_for_review'
