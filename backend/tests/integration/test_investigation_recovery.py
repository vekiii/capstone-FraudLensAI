"""Fault boundaries, durable child retries and rejected late worker writes."""
import asyncio
import json
import time
from uuid import uuid4

import pytest
from test_investigation_api import runtime as api_runtime

from fraudlens.investigation.provider import ProviderError, ScriptedProvider, Turn
from fraudlens.investigation.settings import InvestigationSettings
from fraudlens.investigation.workflow import InvestigationService

runtime = api_runtime


def create(runtime):
    _, service, body, _ = runtime
    return service.create(body, service.settings.analyst, str(uuid4()))


@pytest.mark.parametrize('boundary', ['claim', 'intent', 'result', 'drafting'])
def test_reopen_expired_work_never_replays_and_preserves_known_outcomes(runtime, boundary):
    _, service, _, store = runtime
    run = create(runtime)
    aid = run['attempt_id']
    service._claim(aid, 'fault-owner', 120)
    if boundary != 'claim':
        sequence = service.repo.reserve_dispatch(aid, 'fault-owner')
        if boundary in ('result', 'drafting'):
            service._dispatch_result(aid, sequence, 'completed', Turn('refusal'))
    if boundary == 'drafting':
        service.repo.transition(aid, service.repo.get(aid)['revision'], 'drafting')
    with store.repository.transaction() as db:
        db.execute('UPDATE worker_lease SET expires=?', (time.time() - 1,))
    def forbidden(binding):
        pytest.fail('No provider on reopen/recovery')
    reopened = InvestigationService(store.repository, store, service.settings, forbidden)
    result = reopened.read(aid)
    assert result['state'] == 'failed'
    assert result['failure']['code'] == 'interrupted'
    assert result['failure']['outcome_unknown'] is (boundary == 'intent')
    assert result['budget']['provider_requests'] == (0 if boundary == 'claim' else 1)
    assert reopened.read(aid) == result
    assert asyncio.run(reopened.work_once()) is None
    with store.repository.connection() as db:
        outcomes = db.execute('SELECT outcome FROM provider_dispatches').fetchall()
    assert outcomes == ([] if boundary == 'claim' else [('unknown' if boundary == 'intent' else 'completed',)])


def test_cancel_pending_reply_cannot_record_result_or_publish(runtime):
    _, service, _, store = runtime
    run = create(runtime)
    class Cancelling(ScriptedProvider):
        async def next_turn(self, *args):
            view = service.read(run['attempt_id'])
            service.cancel(view['attempt_id'], view['revision'], service.settings.analyst, str(uuid4()))
            return await super().next_turn(*args)
    service.provider_factory = lambda binding: Cancelling()
    result = asyncio.run(service.work_once())
    assert result['state'] == 'cancelled' and result['report'] is None
    assert result['failure']['outcome_unknown'] is True
    assert result['budget']['provider_requests'] == 1 and not result['trace']
    with store.repository.connection() as db:
        assert db.execute('SELECT outcome FROM provider_dispatches').fetchall() == [('unknown',)]
    assert not any(e['operation'] == 'dispatch_result' for e in service.events(run['attempt_id']))


def test_child_retry_rebinds_valid_evidence_and_preserves_parent(runtime):
    _, service, _, store = runtime
    parent = create(runtime)
    # Invalid citation ends after all three tools, with immutable valid evidence.
    service.provider_factory = lambda binding: ScriptedProvider('invalid_citation')
    parent = asyncio.run(service.work_once())
    old_evidence = service.evidence(parent['attempt_id'])
    key = str(uuid4())
    child = service.retry(parent['attempt_id'], parent['revision'], True, service.settings.analyst, key)
    assert child['run_id'] == parent['run_id']
    assert child['parent_attempt_id'] == parent['attempt_id']
    assert child['attempt_id'] != parent['attempt_id'] and child['state'] == 'created'
    assert child['budget'] == dict(provider_requests=0, tool_calls=0, repairs=0, transient_retries=0, deadline=None)
    copied = service.evidence(child['attempt_id'])
    assert len(copied) == len(old_evidence) > 0
    assert {e['evidence_id'] for e in copied}.isdisjoint(e['evidence_id'] for e in old_evidence)
    assert all(e['attempt_id'] == child['attempt_id'] for e in copied)
    assert [e['content_sha256'] for e in copied] == [e['content_sha256'] for e in old_evidence]
    assert service.read(parent['attempt_id']) == {**parent, 'revision': parent['revision'] + 1,
                                                'updated_at': service.read(parent['attempt_id'])['updated_at']}
    assert service.retry(parent['attempt_id'], parent['revision'], True, service.settings.analyst, key) == child
    with pytest.raises(ValueError, match='request_conflict'):
        service.retry(parent['attempt_id'], parent['revision'], False, service.settings.analyst, key)
    with pytest.raises(ValueError, match='revision_conflict'):
        service.retry(parent['attempt_id'], parent['revision'], True, service.settings.analyst, str(uuid4()))
    assert any(e['operation'] == 'retry' and e['prior_provider_requests'] == 5 for e in service.events(child['attempt_id']))
    # Changed active corpus must never silently reuse old passages.
    service.fail(child['attempt_id'], 'interrupted')
    changed = json.loads((store.repository.path.parent / 'authored-corpus/manifest.json').read_text())
    changed['corpus_id'] = 'replacement'
    path = store.repository.path.parent / 'authored-corpus/manifest.json'
    path.write_text(json.dumps(changed))
    store.publish(path)
    with pytest.raises(ValueError, match='stale_snapshot'):
        service.retry(child['attempt_id'], service.read(child['attempt_id'])['revision'], True, service.settings.analyst, str(uuid4()))
    fresh = service.retry(child['attempt_id'], service.read(child['attempt_id'])['revision'], False, service.settings.analyst, str(uuid4()))
    assert fresh['corpus_version'] != child['corpus_version'] and not service.evidence(fresh['attempt_id'])


def test_second_connection_cannot_claim_or_accept_late_dispatch(runtime):
    _, service, _, store = runtime
    run = create(runtime)
    other = InvestigationService(store.repository, store, service.settings)
    service._claim(run['attempt_id'], 'first', 120)
    with pytest.raises(ValueError, match='worker_claim_conflict'):
        other._claim(run['attempt_id'], 'second', 120)
    seq = service.repo.reserve_dispatch(run['attempt_id'], 'first')
    view = other.read(run['attempt_id'])
    other.cancel(view['attempt_id'], view['revision'], service.settings.analyst, str(uuid4()))
    with pytest.raises(ValueError, match='stale_worker'):
        service._dispatch_result(run['attempt_id'], seq, 'completed', Turn('refusal'))


def test_create_replay_returns_original_response_after_worker(runtime):
    _, service, body, _ = runtime
    key = str(uuid4())
    original = service.create(body, service.settings.analyst, key)
    asyncio.run(service.work_once())
    assert service.create(body, service.settings.analyst, key) == original


def test_retry_copied_evidence_is_used_in_new_tool_results(runtime):
    _, service, _, _ = runtime
    create(runtime)
    service.provider_factory = lambda binding: ScriptedProvider('invalid_citation')
    parent = asyncio.run(service.work_once())
    child = service.retry(parent['attempt_id'], parent['revision'], True, service.settings.analyst, str(uuid4()))
    copied = {e['evidence_id'] for e in service.evidence(child['attempt_id'])}
    service.provider_factory = lambda binding: ScriptedProvider()
    result = asyncio.run(service.work_once())
    assert result['state'] == 'ready_for_review'
    assert set(result['report']['draft']['citations']).issubset(copied)
    assert result['budget']['provider_requests'] == 4 and result['budget']['repairs'] == 0
    assert result['budget']['deadline'] > parent['budget']['deadline']


def test_create_replay_survives_changed_source_without_resolving_it(runtime, monkeypatch):
    _, service, body, _ = runtime
    key = str(uuid4())
    original = service.create(body, service.settings.analyst, key)
    def switched(*args):
        raise ValueError('stale_snapshot')
    monkeypatch.setattr(service.context_reader, 'resolve', switched)
    assert service.create(body, service.settings.analyst, key) == original


def test_retry_rejects_changed_history_even_with_same_context_digest(runtime, monkeypatch):
    from fraudlens.investigation.context import HistoryReader
    _, service, _, _ = runtime
    create(runtime)
    service.provider_factory = lambda binding: ScriptedProvider('invalid_citation')
    parent = asyncio.run(service.work_once())
    original = HistoryReader.read
    def changed(self, *args):
        result = original(self, *args)
        result['totals'] = {'USD': '999'}
        return result
    monkeypatch.setattr(HistoryReader, 'read', changed)
    with pytest.raises(ValueError, match='stale_snapshot'):
        service.retry(parent['attempt_id'], parent['revision'], True, service.settings.analyst, str(uuid4()))


def test_backoff_cannot_escape_the_single_attempt_deadline(runtime):
    _, service, body, store = runtime
    class Transient:
        calls = 0
        async def next_turn(self, *args):
            self.calls += 1
            raise ProviderError('provider_failure', retryable=True, retry_after=2)
    provider = Transient()
    service = InvestigationService(store.repository, store,
        InvestigationSettings(total_timeout_seconds=1), lambda binding: provider)
    service.create(body, 'analyst', str(uuid4()))
    started = time.monotonic()
    result = asyncio.run(service.work_once())
    assert time.monotonic() - started < 3
    assert result['state'] == 'failed' and result['failure']['code'] == 'budget_exhausted'
    assert result['failure']['outcome_unknown'] is False
    assert result['budget']['provider_requests'] == provider.calls == 1
    assert result['budget']['transient_retries'] == 1
