"""Feature 002 edge cases using only authored rows and temporary stores."""

from datetime import timedelta
from decimal import Decimal

import pytest
from backend.tests.phase7_samples import VERSION, entry
from fastapi.testclient import TestClient
from test_data_import import BASE, parse_authored, source_bytes
from test_feature_history import START, T, event, replay
from test_model_artifacts import local_artifact as _artifact_fixture

from fraudlens.data_store import RunStore
from fraudlens.main import create_app
from fraudlens.settings import Settings


@pytest.fixture
def local_artifact(tmp_path):
    return _artifact_fixture.__wrapped__(tmp_path)


@pytest.mark.parametrize('amount,accepted', [
    ('0', True), ('9999999999999.999999', True),
    ('-0', False), ('NaN', False), ('Infinity', False),
    ('1e2', False), ('0.0000001', False),
])
def test_received_amount_policy_and_event_accounting(amount, accepted):
    row = BASE.copy()
    row[5] = amount
    result = parse_authored(source_bytes(row))
    assert result.report.event_valid == int(accepted)
    assert result.report.event_rejected == int(not accepted)
    assert len(result.events) == int(accepted)


@pytest.mark.parametrize('label,status', [
    ('', 'missing'), ('2', 'invalid'), ('unknown', 'invalid'),
])
def test_ineligible_label_preserves_future_history_without_predictor_leak(label, status):
    first = BASE.copy()
    first[0], first[-1] = '2026/01/01 00:00', '0'
    prior = BASE.copy()
    prior[0], prior[-1] = '2026/01/02 11:59', label
    target = BASE.copy()
    target[0], target[-1] = '2026/01/02 12:00', '1'
    parsed = parse_authored(source_bytes(first, prior, target))
    assert parsed.report.event_valid == 3
    assert parsed.private_labels[1].status == status
    assert parsed.private_labels[1].value is None
    snapshot = replay(parsed.events)[parsed.events[2].transaction_id]
    assert snapshot.feature_values['sender_out_count_24h'] == 1
    assert snapshot.feature_values['sender_paid_sum_same_currency_24h'] == Decimal('10.20')
    assert not {'label', 'label_status', 'eligibility'} & snapshot.feature_values.keys()


@pytest.mark.parametrize('offset,expected', [
    (timedelta(hours=24), 1),
    (timedelta(hours=24, minutes=1), 0),
    (timedelta(0), 0),
])
def test_replay_window_boundaries_remain_strictly_past(offset, expected):
    snapshots = replay([event('target', T), event('candidate', T - offset)])
    assert snapshots['target'].feature_values['sender_out_count_24h'] == expected


@pytest.mark.parametrize('order', [
    ('target', 'prior', 'peer'), ('peer', 'target', 'prior'),
])
def test_replay_permutation_and_equal_time_are_deterministic(order):
    facts = {'prior': event('prior', T - timedelta(minutes=1)),
             'target': event('target', T), 'peer': event('peer', T)}
    snapshots = replay([facts[name] for name in order])
    assert snapshots['target'].feature_values == snapshots['peer'].feature_values
    assert snapshots['target'].feature_values['sender_out_count_24h'] == 1
    assert snapshots['target'].feature_input_digest == replay(list(facts.values()))[
        'target'].feature_input_digest


@pytest.mark.parametrize('kwargs,state', [
    ({'missing_intervals': ((T - timedelta(hours=24), T - timedelta(hours=23)),)},
     'incomplete'),
    ({'missing_intervals': ((T - timedelta(hours=25), T - timedelta(hours=24)),)},
     'full'),
    ({'coverage_available': False}, 'unavailable'),
])
def test_missing_coverage_boundary_controls_scoreability(kwargs, state):
    snapshot = replay([event('start', START), event('target', T)], **kwargs)['target']
    assert snapshot.coverage_state == state
    assert snapshot.scoreable is (state == 'full')
    assert snapshot.feature_values['sender_out_count_24h'] == (0 if state == 'full' else None)


@pytest.mark.parametrize('received', ['-1', 'NaN', 'Infinity', 'bad'])
def test_replay_rejects_invalid_received_amount_before_history(received):
    facts = [event('bad', T - timedelta(minutes=1), received=received),
             event('target', T)]
    with pytest.raises(ValueError, match='invalid received amount'):
        replay(facts)


@pytest.mark.parametrize('score,threshold,expected', [
    (0, '0', 1), (1, '1', 1), (0.5, '0.5', 1),
    (0.5, '0.5000001', 0), (1, 'no_alert', 0),
])
def test_run_store_score_bounds_threshold_equality_and_no_alert(
        tmp_path, score, threshold, expected):
    store = RunStore(tmp_path / 'runs.sqlite')
    store.begin_run('run_edge', VERSION, 'rules', 'rules-v1', None, threshold, 1)
    store.append('run_edge', *entry(score=score, run='run_edge'))
    store.complete('run_edge')
    store.activate('run_edge', 'rules')
    listing = store.list_active('rules')
    assert listing['total_alerts'] == expected
    assert listing['displayed_count'] == expected
    store.close()


@pytest.mark.parametrize('score', [-0.01, 1.01, float('nan'), float('inf')])
def test_run_store_rejects_bad_scores_before_completion(tmp_path, score):
    store = RunStore(tmp_path / 'runs.sqlite')
    store.begin_run('run_bad', VERSION, 'rules', 'rules-v1', None, '0.5', 1)
    with pytest.raises(ValueError):
        store.append('run_bad', *entry(score=score, run='run_bad'))
    with pytest.raises(ValueError, match='incomplete'):
        store.complete('run_bad')
    with pytest.raises(ValueError, match='unavailable'):
        store.activate('run_bad', 'rules')
    store.close()


@pytest.mark.parametrize('bad_key', [
    'expected_manifest_sha256', 'expected_dataset_version',
    'expected_protocol_sha256', 'expected_feature_version',
])
def test_artifact_mismatch_blocks_deserialization(local_artifact, monkeypatch, bad_key):
    from fraudlens import model_scoring

    root, artifact, protocol, metadata = local_artifact
    manifest = model_scoring.create_manifest(artifact, protocol, trusted_root=root)
    calls = []
    monkeypatch.setattr(model_scoring.joblib, 'load', lambda path: calls.append(path))
    expected = {'trusted_root': root, 'expected_manifest_sha256': manifest,
                'expected_dataset_version': metadata['dataset_version'],
                'expected_protocol_sha256': metadata['protocol_sha256']}
    expected[bad_key] = 'wrong'
    with pytest.raises(ValueError):
        model_scoring.load_trusted_artifact(artifact, **expected)
    assert calls == []


@pytest.mark.parametrize('case_id,snapshot,status', [
    ('bad', 'run_one', 422),
    ('C' + 'f' * 32, None, 422),
    ('C' + 'f' * 32, 'run_old', 409),
    ('C' + 'f' * 32, 'run_one', 404),
])
def test_dataset_detail_error_boundaries(tmp_path, case_id, snapshot, status):
    path = tmp_path / 'runs.sqlite'
    store = RunStore(path)
    store.begin_run('run_one', VERSION, 'rules', 'rules-v1', None, 'no_alert', 0)
    store.complete('run_one')
    store.activate('run_one', 'rules')
    store.close()
    app = create_app(Settings(mode='dataset', scorer='rules', run_store_path=path))
    with TestClient(app) as client:
        params = {} if snapshot is None else {'snapshot': snapshot}
        response = client.get(f'/api/cases/{case_id}', params=params)
    assert response.status_code == status


@pytest.mark.parametrize('expected_count', [0, 1])
def test_staging_run_cannot_become_active(tmp_path, expected_count):
    path = tmp_path / 'runs.sqlite'
    store = RunStore(path)
    store.begin_run('run_staging', VERSION, 'rules', 'rules-v1', None,
                    'no_alert', expected_count)
    with pytest.raises(ValueError, match='unavailable'):
        store.activate('run_staging', 'rules')
    store.close()
    with TestClient(create_app(Settings(mode='dataset', scorer='rules',
                                        run_store_path=path))) as client:
        response = client.get('/api/cases')
    assert response.status_code == 503
    assert response.json()['error']['code'] == 'run_unavailable'


@pytest.mark.parametrize('mode,expected_status', [
    ('fixture', 200), ('dataset', 503),
])
def test_fixture_and_dataset_mode_do_not_fallback(tmp_path, mode, expected_status):
    path = tmp_path / 'missing.sqlite'
    settings = (Settings(mode='fixture') if mode == 'fixture' else
                Settings(mode='dataset', scorer='rules', run_store_path=path))
    with TestClient(create_app(settings)) as client:
        response = client.get('/api/cases')
    assert response.status_code == expected_status
    if mode == 'fixture':
        assert 'contract_version' not in response.json()
        assert len(response.json()['items']) == 3
    else:
        assert response.json()['error']['code'] == 'run_unavailable'
