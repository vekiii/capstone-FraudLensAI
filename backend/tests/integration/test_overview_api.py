"""Read-only overview aggregates expose predictions without ground-truth labels."""

import sqlite3
from datetime import UTC, datetime

import pytest
from backend.tests.phase7_samples import VERSION, entry
from fastapi.testclient import TestClient

from fraudlens.data_store import RunStore, _overview_aggregation
from fraudlens.main import create_app
from fraudlens.settings import Settings


def _client(path):
    return TestClient(create_app(Settings(mode='dataset', scorer='rules',
                                          run_store_path=path)))


def _make_run(path, events, *, threshold='0.5', run='run_overview', unknown=False):
    store = RunStore(path)
    store.begin_run(run, VERSION, 'rules', 'rules-v1', None, threshold, len(events))
    for index, (at, score) in enumerate(events, start=1):
        store.append(run, *entry(index, run=run, at=at, score=score))
    if unknown and events:
        store.connection.execute(
            "UPDATE scored_assessments SET event_time='unknown-time' WHERE run_id=?",
            (run,))
    store.complete(run)
    store.activate(run, 'rules')
    store.close()


def test_overview_aggregates_time_and_prediction_counts_without_labels(tmp_path):
    path = tmp_path / 'runs.sqlite'
    _make_run(path, [
        (datetime(2022, 9, 10, 23, 59, 59, tzinfo=UTC), 0.8),
        (datetime(2022, 9, 11, 0, 0, 0, tzinfo=UTC), 0.2),
        (datetime(2022, 9, 11, 12, 0, 0, tzinfo=UTC), 0.7),
    ])

    with _client(path) as api:
        response = api.get('/api/overview')

    assert response.status_code == 200
    body = response.json()
    assert body['dataset']['scored_transactions'] == 3
    assert body['dataset']['confirmed_fraud'] is None
    assert body['dataset']['legitimate'] is None
    assert body['dataset']['fraud_rate'] is None
    assert body['predictions']['flagged'] == 2
    assert body['predictions']['not_flagged'] == 1
    assert body['predictions']['flag_rate'] == 2 / 3
    assert body['series'] == [
        {'period': '2022-09-10', 'transactions': 1, 'flagged': 1, 'not_flagged': 0},
        {'period': '2022-09-11', 'transactions': 2, 'flagged': 1, 'not_flagged': 1},
    ]
    assert body['model']['threshold'] == '0.5'
    assert body['model']['precision'] is None
    assert body['model']['recall'] is None
    assert body['model']['f1'] is None
    assert 'no ground-truth labels' in body['model']['metric_source']
    assert 'private_evaluation_labels' not in str(body)


def test_overview_handles_empty_run_and_missing_timestamps(tmp_path):
    path = tmp_path / 'runs.sqlite'
    _make_run(path, [(datetime(2022, 9, 10, tzinfo=UTC), 0.2)], unknown=True)

    with _client(path) as api:
        body = api.get('/api/overview').json()

    assert body['dataset']['scored_transactions'] == 1
    assert body['dataset']['unknown_timestamp_transactions'] == 1
    assert body['series'] == []
    assert body['predictions']['flagged'] == 0
    assert body['predictions']['not_flagged'] == 1


@pytest.mark.parametrize('invalid_timestamp', [
    '2022-09-10Tnot-a-timeZ',
    '2022-02-30T12:00:00Z',
    '2022-09-10T12:00:00+03:00',
    '2022-09-10',
])
def test_overview_excludes_invalid_or_non_utc_timestamps(tmp_path, invalid_timestamp):
    path = tmp_path / 'runs.sqlite'
    _make_run(path, [(datetime(2022, 9, 10, tzinfo=UTC), 0.8)])
    store = RunStore(path)
    store.connection.execute('DROP TRIGGER immutable_scored_update')
    store.connection.execute(
        'UPDATE scored_assessments SET event_time=?', (invalid_timestamp,))
    store.close()

    with _client(path) as api:
        body = api.get('/api/overview').json()

    assert body['dataset']['scored_transactions'] == 1
    assert body['dataset']['unknown_timestamp_transactions'] == 1
    assert body['series'] == []
    assert body['predictions']['flagged'] == 1


def test_overview_accepts_canonical_zero_offset_timestamp(tmp_path):
    path = tmp_path / 'runs.sqlite'
    _make_run(path, [(datetime(2022, 9, 10, tzinfo=UTC), 0.2)])
    store = RunStore(path)
    store.connection.execute(
        'DROP TRIGGER immutable_scored_update')
    store.connection.execute(
        "UPDATE scored_assessments SET event_time='2022-09-10T00:00:00+00:00'")
    store.close()

    with _client(path) as api:
        body = api.get('/api/overview').json()

    assert body['dataset']['unknown_timestamp_transactions'] == 0
    assert body['series'] == [
        {'period': '2022-09-10', 'transactions': 1, 'flagged': 0, 'not_flagged': 1},
    ]


def test_overview_does_not_publish_an_incomplete_run_from_corrupt_active_pointer(tmp_path):
    path = tmp_path / 'runs.sqlite'
    store = RunStore(path)
    store.begin_run('run_unapproved', VERSION, 'rules', 'rules-v1', None, '0.5', 1)
    store.connection.execute(
        'INSERT INTO active_run(singleton,run_id) VALUES(1,?)', ('run_unapproved',))
    store.close()

    with _client(path) as api:
        response = api.get('/api/overview')

    assert response.status_code == 503
    assert response.json()['error']['code'] == 'run_unavailable'


@pytest.mark.parametrize(('field', 'value'), [
    ('scored_count', 2),
    ('total_alerts', 1),
])
def test_overview_fails_closed_when_completed_run_totals_are_inconsistent(
        tmp_path, field, value):
    path = tmp_path / 'runs.sqlite'
    _make_run(path, [(datetime(2022, 9, 10, tzinfo=UTC), 0.2)])
    store = RunStore(path)
    store.connection.execute('DROP TRIGGER immutable_run_update')
    store.connection.execute(f'UPDATE scored_runs SET {field}=?', (value,))
    store.close()

    with _client(path) as api:
        response = api.get('/api/overview')

    assert response.status_code == 500
    assert response.json() == {'error': {
        'code': 'internal_error', 'message': 'Internal server error.'}}


def test_overview_empty_and_unavailable_active_run(tmp_path):
    path = tmp_path / 'runs.sqlite'
    _make_run(path, [])
    with _client(path) as api:
        empty = api.get('/api/overview')
        assert empty.status_code == 200
        assert empty.json()['dataset']['scored_transactions'] == 0
        assert empty.json()['predictions']['flag_rate'] is None
        assert empty.json()['series'] == []

    with _client(tmp_path / 'missing.sqlite') as api:
        unavailable = api.get('/api/overview')
    assert unavailable.status_code == 503
    assert unavailable.json()['error']['code'] == 'run_unavailable'


def test_overview_aggregation_switches_to_week_for_large_run():
    assert _overview_aggregation(10_000) == 'day'
    assert _overview_aggregation(10_001) == 'week'


def test_overview_returns_closed_error_for_unreadable_store(tmp_path):
    path = tmp_path / 'not-a-run-store.sqlite'
    path.write_text('not sqlite', encoding='utf-8')
    with _client(path) as api:
        response = api.get('/api/overview')
    assert response.status_code == 500
    assert response.json() == {'error': {
        'code': 'internal_error', 'message': 'Internal server error.'}}


def test_overview_sanitizes_database_connection_failure(tmp_path, monkeypatch):
    def fail_to_open(_settings):
        raise sqlite3.OperationalError('disk I/O error')

    monkeypatch.setattr('fraudlens.main._dataset_store', fail_to_open)
    with _client(tmp_path / 'runs.sqlite') as api:
        response = api.get('/api/overview')

    assert response.status_code == 500
    assert response.json() == {'error': {
        'code': 'internal_error', 'message': 'Internal server error.'}}
