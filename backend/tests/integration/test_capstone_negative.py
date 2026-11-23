"""EV-11–EV-16 at the existing HTTP, worker, provider and tool boundaries."""

import asyncio
import json

import httpx2
import pytest
from test_investigation_api import post
from test_investigation_api import runtime as api_runtime

from fraudlens.investigation.context import HistoryReader, outbound_context
from fraudlens.investigation.models import validate
from fraudlens.investigation.provider import OpenAIProvider, Turn

runtime = api_runtime


@pytest.fixture(autouse=True)
def forbid_provider_network(monkeypatch):
    async def unexpected_network(*args, **kwargs):
        pytest.fail('Capstone negative tests must use a local provider boundary')

    monkeypatch.setattr(httpx2.AsyncHTTPTransport, 'handle_async_request', unexpected_network)


def create_attempt(runtime):
    client, _, body, _ = runtime
    response = post(client, body)
    assert response.status_code == 202
    return validate('RunView', response.json())


def attempt_path(run):
    return f"/api/investigation/attempts/{run['attempt_id']}"


def work_and_read(runtime, created):
    client, service, _, _ = runtime
    done = asyncio.run(service.work_once())
    response = client.get(attempt_path(created))
    assert response.status_code == 200
    assert response.json() == done
    assert done['context_revision'] == created['context_revision']
    return done


def assert_failed_without_report(service, run, code):
    assert run['state'] == 'failed'
    assert run['failure']['code'] == code
    assert run['report'] is None
    with service.repo.connection() as db:
        assert db.execute('SELECT count(*) FROM reports').fetchone() == (0,)


def test_ev11_missing_binding_rejected_before_provider(runtime, monkeypatch):
    client, service, body, _ = runtime

    def unexpected_provider(binding):
        pytest.fail('Invalid create must not construct a provider')

    monkeypatch.setattr(service, 'provider_factory', unexpected_provider)
    missing = 'snapshot_ref'
    assert missing in body
    response = post(client, {key: value for key, value in body.items() if key != missing})
    assert response.status_code == 422
    assert validate('ErrorEnvelope', response.json())['error']['code'] == 'invalid_request'
    assert asyncio.run(service.work_once()) is None
    with service.repo.connection() as db:
        assert db.execute('SELECT count(*) FROM investigation_runs').fetchone() == (0,)
        assert db.execute('SELECT count(*) FROM provider_dispatches').fetchone() == (0,)


def test_ev12_invalid_drafts_rejected_after_one_repair(runtime, monkeypatch):
    _, service, _, _ = runtime
    drafts = iter([{'outcome': 'ready_for_review'}, {'outcome': 'needs_information'}])
    turns = []

    class InvalidDraftProvider:
        async def next_turn(self, conversation, tools, report_schema, limits):
            turns.append((conversation[-1]['type'], limits.get('tool_choice')))
            return Turn('draft', draft=next(drafts))

    monkeypatch.setattr(service, 'provider_factory', lambda binding: InvalidDraftProvider())
    done = work_and_read(runtime, create_attempt(runtime))
    assert_failed_without_report(service, done, 'output_invalid')
    assert turns == [('context', None), ('repair', 'none')]
    assert done['budget']['repairs'] == 1
    assert done['budget']['provider_requests'] == 2
    assert done['budget']['tool_calls'] == 0
    events = service.events(done['attempt_id'])
    assert sum(event['operation'] == 'repair' for event in events) == 1
    assert not any(event['operation'] == 'report' for event in events)


def test_ev13_missing_bound_citation_is_not_replaced(runtime, monkeypatch):
    client, service, _, _ = runtime
    done = work_and_read(runtime, create_attempt(runtime))
    assert done['state'] == 'ready_for_review'
    attempt = done['attempt_id']
    citations = done['report']['draft']['citations']
    evidence = service.evidence(attempt)
    missing = next(
        item for item in evidence
        if item['kind'] == 'procedure' and item['evidence_id'] in citations
    )
    other = next(
        item for item in evidence
        if item['evidence_id'] in citations and item['evidence_id'] != missing['evidence_id']
    )
    base = attempt_path(done) + '/evidence/'
    url = base + missing['evidence_id']
    before = client.get(url)
    assert before.status_code == 200
    assert before.json() == missing

    # Simulate loss at the archive read boundary in this disposable fixture only.
    read_evidence = service.evidence

    def missing_evidence(attempt_id):
        return [item for item in read_evidence(attempt_id) if item['evidence_id'] != missing['evidence_id']]

    monkeypatch.setattr(service, 'evidence', missing_evidence)
    events = service.events(attempt)
    response = client.get(url)
    assert response.status_code == 404
    assert validate('ErrorEnvelope', response.json())['error']['code'] == 'evidence_not_found'
    assert client.get(base + other['evidence_id']).json() == other
    assert client.get(attempt_path(done)).json() == done
    assert service.events(attempt) == events


def test_ev14_unknown_tool_rejected_before_reservation(runtime, monkeypatch):
    _, service, _, _ = runtime
    call = dict(call_id='capstone-ev14', name='capstone_unknown_tool', arguments={})
    turns = []

    class UnknownToolProvider:
        async def next_turn(self, *args):
            turns.append(call)
            return Turn('tools', calls=(call,))

    monkeypatch.setattr(service, 'provider_factory', lambda binding: UnknownToolProvider())
    done = work_and_read(runtime, create_attempt(runtime))
    assert_failed_without_report(service, done, 'context_unavailable')
    events = service.events(done['attempt_id'])
    assert [event for event in events if event['operation'] == 'tool'] == [
        dict(operation='tool', name='unknown', status='rejected', code='invalid_arguments_or_scope')
    ]
    assert turns == [call] and done['budget']['provider_requests'] == 1
    assert done['trace'] == [] and done['budget']['tool_calls'] == 0
    assert service.evidence(done['attempt_id']) == []
    with service.repo.connection() as db:
        assert db.execute('SELECT count(*) FROM tool_steps').fetchone() == (0,)


def test_ev15_transport_timeout_counts_one_retry_and_unknown_usage(runtime, monkeypatch):
    _, service, _, _ = runtime
    sends = []

    def timeout(request):
        sends.append(request.url.path)
        raise httpx2.ReadTimeout('Synthetic read timeout', request=request)

    def provider(binding):
        return OpenAIProvider(
            'dummy-capstone-test-key', 'capstone-mock-model',
            prompt=binding['prompt'], transport=httpx2.MockTransport(timeout),
        )

    monkeypatch.setattr(service, 'provider_factory', provider)
    done = work_and_read(runtime, create_attempt(runtime))
    assert_failed_without_report(service, done, 'provider_failure')
    assert done['failure']['outcome_unknown'] is True
    assert sends == ['/v1/responses', '/v1/responses']
    assert done['budget']['provider_requests'] == 2
    assert done['budget']['transient_retries'] == 1
    assert done['budget']['tool_calls'] == 0
    events = service.events(done['attempt_id'])
    assert sum(event['operation'] == 'transient_retry' for event in events) == 1
    dispatches = [event for event in events if event['operation'] == 'dispatch_result']
    assert [(event['sequence'], event['outcome'], event['usage']) for event in dispatches] == [
        (1, 'unknown', None), (2, 'unknown', None),
    ]
    assert all(event['diagnostic']['reason'] == 'request_timeout' for event in dispatches)


def test_ev16_history_read_fault_retains_bound_facts(runtime, monkeypatch):
    _, service, _, _ = runtime
    created = create_attempt(runtime)
    attempt = created['attempt_id']
    before = service.context(attempt)
    reads = []

    def history_fault(self, context, side, limit):
        reads.append((context['context_revision'], side, limit))
        raise OSError('Synthetic history read failure')

    monkeypatch.setattr(HistoryReader, 'read', history_fault)
    done = work_and_read(runtime, created)
    assert_failed_without_report(service, done, 'context_unavailable')
    assert reads == [(created['context_revision'], 'sender', 50)]
    assert [(step['name'], step['status']) for step in done['trace']] == [
        ('get_case_facts', 'completed'), ('get_account_history', 'failed'),
    ]
    assert done['trace'][1]['evidence_refs'] == []
    assert done['budget']['provider_requests'] == 2
    assert service.context(attempt) == before
    evidence, = service.evidence(attempt)
    assert evidence['kind'] == 'case_fact'
    assert evidence['context_revision'] == created['context_revision']
    expected = outbound_context(before, created['run_id'])
    actual = json.loads(evidence['text'])
    assert actual['transaction'] == expected['transaction']
    assert actual['assessment'] == expected['assessment']


def test_oversized_provider_input_is_terminal_without_transport(runtime, monkeypatch):
    _, service, _, _ = runtime
    test_key = 'synthetic-budget-test-key'
    # The context fits on its own, but the serialized request also carries the
    # report schema, tool definitions and instructions.
    synthetic_context = 'synthetic ' * 4500

    def unexpected_send(_request):
        pytest.fail('An oversized provider request must never reach transport')

    def provider(binding):
        return OpenAIProvider(test_key, 'capstone-mock-model', prompt=binding['prompt'],
                              transport=httpx2.MockTransport(unexpected_send))

    monkeypatch.setattr(service, 'provider_factory', provider)
    def oversized_context(context, run_id):
        return {**outbound_context(context, run_id), 'notice': synthetic_context}

    monkeypatch.setattr('fraudlens.investigation.workflow.outbound_context', oversized_context)
    done = work_and_read(runtime, create_attempt(runtime))
    assert_failed_without_report(service, done, 'budget_exhausted')
    assert done['failure']['outcome_unknown'] is False
    assert done['budget']['provider_requests'] == 1  # Local reservation, no send.
    assert done['budget']['transient_retries'] == 0
    assert asyncio.run(service.work_once()) is None
    serialized = json.dumps(done)
    assert test_key not in serialized
    assert synthetic_context not in serialized
