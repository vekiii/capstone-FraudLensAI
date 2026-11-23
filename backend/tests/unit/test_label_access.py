"""Synthetic RED contracts for the restricted label-audit boundary (T216).

T217 supplies ``LabelAuditService(records, partition_by_id, audit_log_path)``
and ``query(*, shape, purpose, partition=None, start_utc=None,
end_utc=None, transaction_id=None)``. Every request, including refusals, must
append a purpose/query/time/result record to the local audit log. These tests
use invented labels only; they never open the real source or snapshot.
"""

import importlib
import json
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from fraudlens.main import create_app
from fraudlens.settings import Settings


def access_module():
    try:
        module = importlib.import_module('fraudlens.training.label_access')
    except ModuleNotFoundError as error:
        if error.name not in ('fraudlens.training', 'fraudlens.training.label_access'):
            raise
        pytest.fail('Missing Feature 002 restricted label access (T217)', pytrace=False)
    assert callable(getattr(module, 'LabelAuditService', None))
    return module


def records():
    """Invented rows; one warm-up and one scoreable showcase row."""
    return [
        {'transaction_id': 'warm', 'occurred_at_utc': datetime(2022, 9, 1, tzinfo=timezone.utc),
         'is_scoreable': False, 'is_laundering': 1},
        {'transaction_id': 'train-a', 'occurred_at_utc': datetime(2022, 9, 2, tzinfo=timezone.utc),
         'is_scoreable': True, 'is_laundering': 1},
        {'transaction_id': 'train-b', 'occurred_at_utc': datetime(2022, 9, 2, tzinfo=timezone.utc),
         'is_scoreable': True, 'is_laundering': 0},
        {'transaction_id': 'validation',
         'occurred_at_utc': datetime(2022, 9, 3, tzinfo=timezone.utc),
         'is_scoreable': True, 'is_laundering': 1},
        {'transaction_id': 'test', 'occurred_at_utc': datetime(2022, 9, 4, tzinfo=timezone.utc),
         'is_scoreable': True, 'is_laundering': 0},
        {'transaction_id': 'showcase',
         'occurred_at_utc': datetime(2022, 9, 5, tzinfo=timezone.utc),
         'is_scoreable': True, 'is_laundering': 1},
    ]


def service(tmp_path):
    mapping = {
        'warm': 'development_warmup', 'train-a': 'train', 'train-b': 'train',
        'validation': 'validation', 'test': 'test', 'showcase': 'showcase',
    }
    path = tmp_path / 'label-audit.jsonl'
    instance = access_module().LabelAuditService(
        records(), partition_by_id=mapping, audit_log_path=path,
    )
    return instance, path


def log_entries(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]


def test_development_daily_aggregates_are_utc_count_only(tmp_path):
    access, path = service(tmp_path)
    result = access.query(shape='development_daily', purpose='pretraining_class_audit')

    assert result == (
        {'utc_day': '2022-09-02', 'source_count': 2, 'scoreable_count': 2,
         'positive_count': 1},
        {'utc_day': '2022-09-03', 'source_count': 1, 'scoreable_count': 1,
         'positive_count': 1},
        {'utc_day': '2022-09-04', 'source_count': 1, 'scoreable_count': 1,
         'positive_count': 0},
    )
    assert len(log_entries(path)) == 1
    assert log_entries(path)[0]['result'] == 'allowed'


def test_partition_totals_are_aggregate_and_exclude_warmup(tmp_path):
    access, _ = service(tmp_path)
    result = access.query(shape='partition_totals', purpose='pretraining_class_audit')

    assert result == (
        {'partition': 'train', 'scoreable_count': 2, 'positive_count': 1},
        {'partition': 'validation', 'scoreable_count': 1, 'positive_count': 1},
        {'partition': 'test', 'scoreable_count': 1, 'positive_count': 0},
    )


def test_one_showcase_wide_total_is_allowed_and_repeat_is_logged_denied(tmp_path):
    access, path = service(tmp_path)
    assert access.query(shape='showcase_total', purpose='pretraining_class_audit') == {
        'source_count': 1, 'scoreable_count': 1, 'positive_count': 1,
    }
    with pytest.raises(PermissionError):
        access.query(shape='showcase_total', purpose='pretraining_class_audit')
    assert [entry['result'] for entry in log_entries(path)] == ['allowed', 'denied']


@pytest.mark.parametrize('partition', ['train', 'validation', 'test', 'showcase'])
def test_record_level_audit_labels_are_refused_for_every_partition(tmp_path, partition):
    access, path = service(tmp_path)
    with pytest.raises(PermissionError):
        access.query(
            shape='record_labels', partition=partition, purpose='pretraining_class_audit',
            transaction_id='train-a',
        )
    entry = log_entries(path)[0]
    assert entry['result'] == 'denied'
    assert entry['purpose'] == 'pretraining_class_audit'
    assert entry['query']['shape'] == 'record_labels'
    assert 'time' in entry
    assert 'is_laundering' not in json.dumps(entry)


@pytest.mark.parametrize('shape', ['showcase_daily', 'showcase_subrange'])
def test_showcase_day_and_subrange_queries_are_refused(tmp_path, shape):
    access, path = service(tmp_path)
    with pytest.raises(PermissionError):
        access.query(
            shape=shape, purpose='pretraining_class_audit', partition='showcase',
            start_utc=datetime(2022, 9, 5, tzinfo=timezone.utc),
            end_utc=datetime(2022, 9, 6, tzinfo=timezone.utc),
        )
    assert log_entries(path)[0]['result'] == 'denied'


def test_extra_filter_on_allowed_shape_fails_closed_and_is_logged(tmp_path):
    access, path = service(tmp_path)
    with pytest.raises(PermissionError):
        access.query(
            shape='partition_totals', purpose='pretraining_class_audit',
            transaction_id='test',
        )
    assert log_entries(path)[0]['result'] == 'denied'


def test_unapproved_purpose_cannot_read_aggregate_labels(tmp_path):
    access, path = service(tmp_path)
    with pytest.raises(PermissionError):
        access.query(shape='development_daily', purpose='debugging')
    assert log_entries(path)[0]['result'] == 'denied'


def test_showcase_total_stays_single_use_across_service_instances(tmp_path):
    access, path = service(tmp_path)
    access.query(shape='showcase_total', purpose='pretraining_class_audit')
    another, _ = service(tmp_path)

    with pytest.raises(PermissionError):
        another.query(shape='showcase_total', purpose='pretraining_class_audit')
    assert [entry['result'] for entry in log_entries(path)] == ['allowed', 'denied']


def test_denied_query_does_not_read_any_label(tmp_path):
    class GuardedRecord(dict):
        def get(self, key, default=None):
            if key == 'is_laundering':
                raise AssertionError('denied query read a label')
            return super().get(key, default)

    access = access_module().LabelAuditService(
        [GuardedRecord(entry) for entry in records()],
        partition_by_id={
            'warm': 'development_warmup', 'train-a': 'train', 'train-b': 'train',
            'validation': 'validation', 'test': 'test', 'showcase': 'showcase',
        },
        audit_log_path=tmp_path / 'guarded.jsonl',
    )
    with pytest.raises(PermissionError):
        access.query(shape='record_labels', purpose='pretraining_class_audit')


def test_invalid_label_encoding_fails_without_releasing_aggregate(tmp_path):
    altered = records()
    altered[1]['is_laundering'] = 1.0
    path = tmp_path / 'invalid-label.jsonl'
    access = access_module().LabelAuditService(
        altered,
        partition_by_id={
            'warm': 'development_warmup', 'train-a': 'train', 'train-b': 'train',
            'validation': 'validation', 'test': 'test', 'showcase': 'showcase',
        },
        audit_log_path=path,
    )
    with pytest.raises(ValueError, match='label'):
        access.query(shape='partition_totals', purpose='pretraining_class_audit')
    assert log_entries(path)[0]['result'] == 'error'


def test_exact_canonical_text_labels_are_accepted(tmp_path):
    canonical = records()
    for entry in canonical:
        entry['is_laundering'] = str(entry['is_laundering'])
    access = access_module().LabelAuditService(
        canonical,
        partition_by_id={
            'warm': 'development_warmup', 'train-a': 'train', 'train-b': 'train',
            'validation': 'validation', 'test': 'test', 'showcase': 'showcase',
        },
        audit_log_path=tmp_path / 'canonical-labels.jsonl',
    )
    assert access.query(shape='showcase_total', purpose='pretraining_class_audit') == {
        'source_count': 1, 'scoreable_count': 1, 'positive_count': 1,
    }


def test_malformed_query_shape_is_denied_and_logged(tmp_path):
    access, path = service(tmp_path)
    with pytest.raises(PermissionError):
        access.query(shape=['record_labels'], purpose='pretraining_class_audit')
    assert log_entries(path)[0]['result'] == 'denied'


@pytest.mark.parametrize('query', [
    'transaction_id=ibm-hi-small%3Aexample%3Arow%3A1',
    'partition=test&utc_day=2022-09-06',
    'partition=showcase&start_utc=2022-09-06T00%3A00%3A00Z',
    'partition=test&end_utc=2022-09-07T00%3A00%3A00Z',
    'shape=record_labels',
])
def test_results_route_refuses_record_daily_and_subrange_queries_before_labels(query):
    with TestClient(create_app(settings=Settings())) as client:
        response = client.get(f'/api/model/results?{query}')
    assert response.status_code == 422
    assert response.json()['error']['code'] == 'invalid_request'
    assert 'is_laundering' not in response.text


def test_results_route_without_model_opt_in_does_not_disclose_test_metrics():
    with TestClient(create_app(settings=Settings())) as client:
        response = client.get('/api/model/results')
    assert response.status_code == 409
    assert response.json()['error']['code'] == 'evaluation_not_authorized'


@pytest.mark.parametrize('shape', ['test_daily', 'test_subrange', 'showcase_daily',
                                   'showcase_subrange', 'record_labels'])
def test_results_purpose_cannot_query_restricted_label_shapes(tmp_path, shape):
    access, path = service(tmp_path)
    with pytest.raises(PermissionError):
        access.query(shape=shape, purpose='results_api', partition='test',
                     start_utc=datetime(2022, 9, 4, tzinfo=timezone.utc),
                     end_utc=datetime(2022, 9, 5, tzinfo=timezone.utc),
                     transaction_id='test' if shape == 'record_labels' else None)
    assert log_entries(path)[0]['result'] == 'denied'
