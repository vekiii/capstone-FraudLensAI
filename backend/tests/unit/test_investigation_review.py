"""Explicit analyst authority, immutable drafts and append-only corrections; no network."""
import asyncio
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

import pytest

from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import validate
from fraudlens.investigation.provider import ScriptedProvider
from fraudlens.investigation.settings import InvestigationSettings
from fraudlens.investigation.workflow import InvestigationService


@pytest.fixture
def runtime(tmp_path, knowledge_factory):
    store = KnowledgeStore(tmp_path / 'review.sqlite')
    store.publish(knowledge_factory('missing evidence money'))
    store.save_configuration(json.loads(Path('data/knowledge/fraudlens-aml-knowledge-v1/retrieval.json').read_text()))
    service = InvestigationService(store.repository, store, InvestigationSettings(analyst='server-analyst'))
    context = service.context_reader.resolve('CASE-001', 'fixture', None)
    body = {key: context[key] for key in ('case_id', 'source_mode', 'snapshot_ref')}
    return None, service, body, store


def request(run, disposition='close', **changes):
    return dict(report_id=run['report']['report_id'], disposition=disposition,
                rationale='  Synthetic test rationale  ', correction_note=None,
                supersedes_review_id=None, **changes)


def submit(service, run, body=None, key=None):
    from fraudlens.investigation.review import AnalystReviewService
    return AnalystReviewService(service).submit(run['attempt_id'], run['revision'],
                body or request(run), service.settings.analyst, key or str(uuid4()))


def ready(runtime):
    _, service, body, _ = runtime
    service.create(body, service.settings.analyst, str(uuid4()))
    return asyncio.run(service.work_once())


@pytest.mark.parametrize('disposition', ['escalate', 'close', 'request_more_information'])
def test_explicit_review_reopens_original_draft_and_evidence(runtime, disposition):
    run = ready(runtime)
    _, service, _, store = runtime
    evidence = service.evidence(run['attempt_id'])
    assert run['review'] is None  # Generated text/validation cannot approve.
    key = str(uuid4())
    reviewed = submit(service, run, request(run, disposition), key)
    assert reviewed['state'] == 'reviewed' and reviewed['revision'] == run['revision'] + 1
    assert reviewed['review']['actor'] == 'server-analyst'
    assert reviewed['review']['rationale'] == 'Synthetic test rationale'
    assert reviewed['review']['disposition'] == disposition
    assert reviewed['report'] == {**run['report'], 'semantic_review': 'reviewed_with_notes'}
    assert service.evidence(run['attempt_id']) == evidence
    assert service.read(run['attempt_id']) == reviewed
    assert submit(service, run, request(run, disposition), key) == reviewed
    with store.repository.connection() as db:
        original = json.loads(db.execute('SELECT content FROM reports WHERE report_id=?',
                                         (run['report']['report_id'],)).fetchone()[0])
        assert original['draft'] == run['report']['draft']


def test_linked_amendment_replay_and_stale_cas(runtime):
    run = ready(runtime)
    service = runtime[1]
    first = submit(service, run)
    body = request(run, 'escalate')
    body.update(supersedes_review_id=first['review']['review_id'], correction_note='<script>literal note</script>')
    key = str(uuid4())
    second = submit(service, first, body, key)
    assert second['review']['supersedes_review_id'] == first['review']['review_id']
    assert second['review']['review_id'] != first['review']['review_id']
    assert second['report'] == first['report']
    assert submit(service, first, body, key) == second
    with pytest.raises(ValueError, match='request_conflict'):
        submit(service, first, {**body, 'rationale': 'Changed'}, key)
    with pytest.raises(ValueError, match='revision_conflict'):
        submit(service, run)
    with pytest.raises(ValueError, match='revision_conflict'):
        submit(service, second, body)  # Superseded current-review ID, even at current revision.
    with service.repo.connection() as db:
        reviews = [json.loads(row[0]) for row in db.execute('SELECT content FROM reviews ORDER BY rowid')]
    assert reviews == [first['review'], second['review']]


@pytest.mark.parametrize('field,value', [('rationale', ''), ('rationale', '  '),
    ('rationale', 'x' * 2001), ('actor', ''), ('actor', ' '), ('actor', 'x' * 81),
    ('report_id', 'f' * 64), ('correction_note', ' '), ('disposition', 'approve')])
def test_invalid_text_report_and_generated_authority_never_write(runtime, field, value):
    run = ready(runtime)
    service = runtime[1]
    body, actor = request(run), service.settings.analyst
    if field == 'actor':
        actor = value
    else:
        body[field] = value
    from fraudlens.investigation.review import AnalystReviewService
    with pytest.raises(ValueError):
        AnalystReviewService(service).submit(run['attempt_id'], run['revision'], body, actor, str(uuid4()))
    assert service.read(run['attempt_id']) == run


def test_two_connection_review_one_winner_and_same_key_replay(runtime):
    run = ready(runtime)
    service = runtime[1]
    def concurrent(key):
        try:
            return submit(service, run, key=key)
        except ValueError as exc:
            return str(exc)
    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(concurrent, [str(uuid4()), str(uuid4())]))
    assert sum(isinstance(result, dict) for result in results) == 1
    assert 'revision_conflict' in results
    other = service.create(runtime[2], service.settings.analyst, str(uuid4()))
    run = asyncio.run(service.work_once())
    assert run['attempt_id'] == other['attempt_id']
    key = str(uuid4())
    with ThreadPoolExecutor(2) as pool:
        a, b = pool.map(concurrent, [key, key])
    assert a == b and isinstance(a, dict)


def test_needs_information_restrictions_survive_review_and_no_draft_or_failed_cannot_review(runtime):
    service = runtime[1]
    # Authored provider limitations scenario, not a mutated ready report.
    service.provider_factory = lambda _: ScriptedProvider('needs_information')
    run = ready(runtime)
    assert run['state'] == 'needs_information'
    for action in ['close', 'escalate']:
        with pytest.raises(ValueError, match='invalid_transition'):
            submit(service, run, request(run, action))
    reviewed = submit(service, run, request(run, 'request_more_information'))
    body = request(run, 'close')
    body.update(supersedes_review_id=reviewed['review']['review_id'], correction_note='Cannot bypass limitations')
    with pytest.raises(ValueError, match='invalid_transition'):
        submit(service, reviewed, body)
    for state in ['created', 'failed', 'cancelled']:
        other = service.create(runtime[2], service.settings.analyst, str(uuid4()))
        if state != 'created':
            service.repo.transition(other['attempt_id'], other['revision'], state)
            other = service.read(other['attempt_id'])
        from fraudlens.investigation.review import AnalystReviewService
        with pytest.raises(ValueError, match='invalid_transition'):
            AnalystReviewService(service).submit(other['attempt_id'], other['revision'], request(run),
                                                  service.settings.analyst, str(uuid4()))


@pytest.mark.parametrize('length', [1, 2000])
def test_trimmed_boundary_rationale_and_actor(runtime, length):
    run = ready(runtime)
    from fraudlens.investigation.review import AnalystReviewService
    body = {**request(run), 'rationale': '  ' + 'x' * length + '  '}
    result = AnalystReviewService(runtime[1]).submit(run['attempt_id'], run['revision'], body, 'x' * 80, str(uuid4()))
    assert len(result['review']['rationale']) == length
    validate('RunView', result)


def test_request_response_failure_rolls_back_review_state_and_audit(runtime):
    run = ready(runtime)
    service = runtime[1]
    before = service.events(run['attempt_id'])
    with service.repo.connection() as db:
        db.execute("CREATE TRIGGER fault_review_key BEFORE INSERT ON request_keys WHEN NEW.operation='review' "
                   "BEGIN SELECT RAISE(ABORT, 'Authored atomicity fault'); END")
    with pytest.raises(sqlite3.IntegrityError, match='Authored atomicity fault'):
        submit(service, run)
    assert service.read(run['attempt_id']) == run
    assert service.events(run['attempt_id']) == before
    with service.repo.connection() as db:
        assert db.execute('SELECT count(*) FROM reviews').fetchone()[0] == 0


def test_amendment_requires_note_and_every_prior_event_is_immutable(runtime):
    run = ready(runtime)
    service = runtime[1]
    first = submit(service, run)
    body = {**request(run), 'supersedes_review_id': first['review']['review_id']}
    with pytest.raises(ValueError, match='invalid_transition'):
        submit(service, first, body)
    for table in ['reviews', 'reports', 'evidence_items', 'audit_events']:
        with service.repo.connection() as db:
            for operation in ['UPDATE', 'DELETE']:
                sql = f'{operation} {table}' + (" SET content='{}'" if operation == 'UPDATE' else '')
                with pytest.raises(sqlite3.IntegrityError, match='Immutable record'):
                    db.execute(sql if operation == 'UPDATE' else f'DELETE FROM {table}')


def test_missing_saved_limitations_draft_cannot_be_reviewed(runtime):
    service = runtime[1]
    run = service.create(runtime[2], service.settings.analyst, str(uuid4()))
    # Simulate inconsistent interrupted legacy state; the review boundary fails closed.
    with service.repo.transaction() as db:
        db.execute("UPDATE attempts SET state='needs_information' WHERE attempt_id=?", (run['attempt_id'],))
    from fraudlens.investigation.review import AnalystReviewService
    with pytest.raises(ValueError, match='invalid_transition'):
        AnalystReviewService(service).submit(run['attempt_id'], run['revision'], dict(report_id='f' * 64,
            disposition='request_more_information', rationale='Synthetic test', correction_note=None,
            supersedes_review_id=None), service.settings.analyst, str(uuid4()))
