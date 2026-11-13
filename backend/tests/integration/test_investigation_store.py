"""Durable invariants across independent SQLite connections, without network."""
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from fraudlens.investigation.context import CaseContextReader
from fraudlens.investigation.models import digest
from fraudlens.investigation.store import InvestigationRepository

ROOT = Path(__file__).resolve().parents[3]


def new(repo, key='11111111-1111-4111-8111-111111111111'):
    return repo.create(CaseContextReader().resolve('CASE-001', 'fixture', None),
                       'test-analyst', 'create', key, {'case_id': 'CASE-001'})


def test_schema_and_replay_conflict(tmp_path):
    repo = InvestigationRepository(tmp_path / 'investigations.sqlite')
    first = new(repo)
    assert new(repo) == first
    with pytest.raises(ValueError):
        repo.create(CaseContextReader().resolve('CASE-001', 'fixture', None),
                    'test-analyst', 'create', '11111111-1111-4111-8111-111111111111', {'case_id': 'CASE-002'})
    assert repo.get(first['attempt_id'])['revision'] == 1
    with repo.connection() as db:
        assert db.execute('PRAGMA foreign_keys').fetchone()[0] == 1
        assert db.execute('PRAGMA busy_timeout').fetchone()[0] <= 1000
        assert db.execute('SELECT version FROM schema_meta').fetchone()[0] == 1


def test_cas_and_transition(tmp_path):
    repo = InvestigationRepository(tmp_path / 'inv.sqlite')
    run = new(repo)
    result = repo.transition(run['attempt_id'], 1, 'gathering_evidence')
    assert result['revision'] == 2
    with pytest.raises(ValueError):
        repo.transition(run['attempt_id'], 1, 'failed')
    with pytest.raises(ValueError):
        repo.transition(run['attempt_id'], 2, 'reviewed')


def test_dispatch_is_durable_before_external_io(tmp_path):
    path = tmp_path / 'inv.sqlite'
    repo = InvestigationRepository(path)
    run = new(repo)
    repo.claim(run['attempt_id'], 'worker')
    for seq in range(1, 9):
        assert repo.reserve_dispatch(run['attempt_id'], 'worker') == seq
        assert InvestigationRepository(path).get(run['attempt_id'])['provider_requests'] == seq
    with pytest.raises(ValueError):
        repo.reserve_dispatch(run['attempt_id'], 'worker')
    with repo.connection() as db:
        assert db.execute('SELECT count(*) FROM provider_dispatches WHERE outcome=?', ('pending',)).fetchone()[0] == 8


def test_global_claim(tmp_path):
    path = tmp_path / 'inv.sqlite'
    repo = InvestigationRepository(path)
    one, two = new(repo), new(repo, '22222222-2222-4222-8222-222222222222')
    def claim(item):
        try:
            InvestigationRepository(path).claim(item['attempt_id'], item['attempt_id'])
            return True
        except ValueError:
            return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(claim, [one, two])) == [False, True]


def test_immutable_data_atomic_review_and_rollback(tmp_path):
    repo = InvestigationRepository(tmp_path / 'inv.sqlite')
    run = new(repo)
    attempt = run['attempt_id']
    evidence = json.loads((ROOT / 'specs/003-ai-investigation/contracts/examples/evidence-fixture.json').read_text())
    evidence.update(attempt_id=attempt, context_revision=run['context_revision'])
    repo.save_evidence(attempt, evidence)
    with pytest.raises(ValueError):
        repo.save_evidence(attempt, {**evidence, 'text': 'replacement'})
    repo.transition(attempt, 1, 'gathering_evidence')
    repo.transition(attempt, 2, 'drafting')
    draft = json.loads((ROOT / 'specs/003-ai-investigation/contracts/examples/needs-information-draft.json').read_text())
    report = repo.save_report(attempt, draft)
    assert report == digest({'attempt_id': attempt, 'context_revision': run['context_revision'], 'draft': draft})
    repo.transition(attempt, 3, 'needs_information')
    with pytest.raises(ValueError):
        repo.review(attempt, 4, 'analyst', 'close', 'cannot close missing data', report)
    assert repo.get(attempt)['revision'] == 4
    repo.review(attempt, 4, 'analyst', 'request_more_information', 'Missing facts', report)
    assert repo.get(attempt)['state'] == 'reviewed'
    with repo.connection() as db:
        assert db.execute('SELECT count(*) FROM reviews').fetchone()[0] == 1
        assert db.execute('SELECT count(*) FROM audit_events').fetchone()[0] == 1
        with pytest.raises(sqlite3.IntegrityError):
            db.execute('UPDATE contexts SET content=?', ('{}',))
        with pytest.raises(sqlite3.IntegrityError):
            db.execute('UPDATE reports SET content=?', ('{}',))
    with pytest.raises(RuntimeError):
        with repo.transaction() as db:
            db.execute('INSERT INTO audit_events(attempt_id,content) VALUES (?,?)', (attempt, '{}'))
            raise RuntimeError('simulated failure')
    with repo.connection() as db:
        assert db.execute('SELECT count(*) FROM audit_events').fetchone()[0] == 1
        with pytest.raises(sqlite3.IntegrityError):
            db.execute('INSERT INTO audit_events(attempt_id,content) VALUES (?,?)', ('unknown', '{}'))


def test_unknown_schema_refuses_migration(tmp_path):
    path = tmp_path / 'unknown.sqlite'
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE schema_meta(version INTEGER)')
        db.execute('INSERT INTO schema_meta VALUES (99)')
    before = path.read_bytes()
    with pytest.raises(ValueError):
        InvestigationRepository(path)
    assert path.read_bytes() == before

def test_replay_returns_original_response_after_state_change(tmp_path):
    repo = InvestigationRepository(tmp_path / 'replay.sqlite')
    original = new(repo)
    repo.transition(original['attempt_id'], 1, 'gathering_evidence')
    assert new(repo) == original

def test_tool_reservation_counts_executions_and_rejects_thirteenth(tmp_path):
    repo = InvestigationRepository(tmp_path / 'tools.sqlite')
    run = new(repo)
    repo.claim(run['attempt_id'], 'worker')
    for seq in range(1, 13):
        assert repo.reserve_tool(run['attempt_id'], 'worker', 'get_case_facts', {}) == seq
    with pytest.raises(ValueError):
        repo.reserve_tool(run['attempt_id'], 'worker', 'get_case_facts', {})
