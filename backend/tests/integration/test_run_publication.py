"""T043/T047: complete-only, immutable, restartable scored-run publication."""

import pytest
from backend.tests.phase7_samples import VERSION, entry


def begin(store, run='run_test_1', *, source='rules', expected=1,
          threshold='0.5', artifact=None):
    store.begin_run(run, VERSION, source,
                    'rules-v1' if source == 'rules' else 'model-history-v1',
                    artifact, threshold, expected)


def test_partial_failure_and_restart_preserve_previous_active(tmp_path):
    from fraudlens.data_store import RunStore

    path = tmp_path / 'runs.sqlite'
    store = RunStore(path)
    begin(store)
    store.append('run_test_1', *entry())
    store.complete('run_test_1')
    store.activate('run_test_1', 'rules')
    assert store.list_active('rules')['total_alerts'] == 1
    begin(store, 'run_test_2', expected=2)
    store.append('run_test_2', *entry(2, run='run_test_2'))
    with pytest.raises(ValueError):
        store.complete('run_test_2')
    store.close()
    reopened = RunStore(path)
    assert reopened.list_active('rules')['snapshot_ref'] == 'run_test_1'
    with pytest.raises(ValueError):
        reopened.activate('run_test_2', 'rules')
    assert reopened.list_active('rules')['snapshot_ref'] == 'run_test_1'
    reopened.close()


def test_switch_is_atomic_and_stale_detail_rejected(tmp_path):
    from fraudlens.data_store import RunStore, StaleSnapshot

    path = tmp_path / 'runs.sqlite'
    first = RunStore(path)
    second = RunStore(path)
    for run, index in [('run_test_1', 1), ('run_test_2', 2)]:
        begin(first, run)
        first.append(run, *entry(index, run=run))
        first.complete(run)
    first.activate('run_test_1', 'rules')
    old = first.list_active('rules')
    second.activate('run_test_2', 'rules')
    with pytest.raises(StaleSnapshot):
        first.detail_active('rules', old['snapshot_ref'], old['items'][0]['case_id'])
    assert first.list_active('rules')['snapshot_ref'] == 'run_test_2'
    first.activate('run_test_2', 'rules')
    assert second.list_active('rules')['snapshot_ref'] == 'run_test_2'
    first.close()
    second.close()


def test_completed_rows_immutable_and_wrong_scorer_artifact_fail(tmp_path):
    from fraudlens.data_store import RunStore

    store = RunStore(tmp_path / 'runs.sqlite')
    begin(store)
    store.append('run_test_1', *entry())
    store.complete('run_test_1')
    with pytest.raises(ValueError):
        store.append('run_test_1', *entry(2))
    with pytest.raises(ValueError):
        store.activate('run_test_1', 'model')
    with pytest.raises(ValueError):
        begin(store, 'run_model_bad', source='model', artifact=None)
    store.activate('run_test_1', 'rules')
    assert store.list_active('rules')['total_alerts'] == 1
    store.close()


def test_model_activation_requires_exact_artifact_digest(tmp_path):
    from fraudlens.data_store import RunStore

    store = RunStore(tmp_path / 'runs.sqlite')
    digest = 'a' * 64
    begin(store, 'run_model_1', source='model', expected=0,
          threshold='no_alert', artifact=digest)
    store.complete('run_model_1')
    with pytest.raises(ValueError):
        store.activate('run_model_1', 'model')
    with pytest.raises(ValueError):
        store.activate('run_model_1', 'model', 'b' * 64)
    store.activate('run_model_1', 'model', digest)
    assert store.list_active('model')['snapshot_ref'] == 'run_model_1'
    store.close()


def test_activation_sql_failure_rolls_back_pointer(tmp_path):
    import sqlite3

    from fraudlens.data_store import RunStore

    store = RunStore(tmp_path / 'runs.sqlite')
    for run in ('run_test_1', 'run_test_2'):
        begin(store, run, expected=0, threshold='no_alert')
        store.complete(run)
    store.activate('run_test_1', 'rules')
    store.connection.execute('''
        CREATE TRIGGER reject_switch BEFORE UPDATE ON active_run
        BEGIN SELECT RAISE(ABORT, 'injected activation failure'); END''')
    with pytest.raises(sqlite3.IntegrityError, match='injected activation failure'):
        store.activate('run_test_2', 'rules')
    assert store.list_active('rules')['snapshot_ref'] == 'run_test_1'
    store.close()
    reopened = RunStore(tmp_path / 'runs.sqlite')
    assert reopened.list_active('rules')['snapshot_ref'] == 'run_test_1'
    reopened.close()


def test_label_like_extra_or_wrong_identity_never_stage(tmp_path):
    from fraudlens.data_store import RunStore

    store = RunStore(tmp_path / 'runs.sqlite')
    begin(store)
    case, transaction, assessment = entry()
    with pytest.raises(ValueError):
        store.append('run_test_1', case, transaction | {'label': 1}, assessment)
    with pytest.raises(ValueError):
        store.append('run_test_1', case, transaction,
                     assessment | {'run_id': 'run_other'})
    with pytest.raises(ValueError):
        store.complete('run_test_1')
    store.close()


def test_cli_rules_zero_run_and_model_failure_do_not_substitute(
        tmp_path, capsys, monkeypatch):
    import json
    import sqlite3

    from fraudlens.pipeline_cli import main

    source = tmp_path / 'source.sqlite'
    connection = sqlite3.connect(source)
    connection.executescript('''
        CREATE TABLE dataset_versions(id TEXT PRIMARY KEY,status TEXT);
        CREATE TABLE feature_builds(version TEXT,feature_version TEXT,status TEXT);
        CREATE TABLE feature_snapshots(version TEXT,feature_version TEXT,
            transaction_id TEXT,event_time TEXT,scoreable INTEGER,payload_json TEXT,
            as_of TEXT,coverage_start TEXT,coverage_state TEXT,
            feature_input_digest TEXT,created_at TEXT);
        CREATE TABLE operational_events(version TEXT,transaction_id TEXT,
            case_id TEXT,payload_json TEXT);
    ''')
    connection.execute("INSERT INTO dataset_versions VALUES(?,'complete')", (VERSION,))
    connection.execute("INSERT INTO feature_builds VALUES(?,'history-v1','complete')",
                       (VERSION,))
    connection.commit()
    connection.close()
    protocol = tmp_path / 'protocol.json'
    protocol.write_text(json.dumps({
        'dataset_version': VERSION, 'feature_version': 'history-v1',
        'rules_validation_threshold': {'threshold': 'no_alert'},
        'model_validation_threshold': {'threshold': 'no_alert'},
        'protocol_sha256': 'f' * 64,
    }))
    output = tmp_path / 'runs.sqlite'
    base = ['--source-store', str(source), '--run-store', str(output),
            '--dataset-version', VERSION, '--protocol', str(protocol)]
    assert main(['score-run', *base, '--run-id', 'run_empty', '--scorer', 'rules',
                 '--threshold', 'no_alert']) == 0
    assert 'completed' in capsys.readouterr().out
    assert main(['activate-run', '--run-store', str(output), '--run-id', 'run_empty',
                 '--scorer', 'rules']) == 0
    assert main(['score-run', *base, '--run-id', 'run_model', '--scorer', 'model',
                 '--threshold', 'no_alert']) != 0
    import fraudlens.pipeline_cli as cli

    def verified_loader(*_args, **kwargs):
        assert kwargs['expected_protocol_sha256'] == 'f' * 64
        return type('Artifact', (), {'manifest_sha256': 'a' * 64})()

    monkeypatch.setattr(cli, 'load_trusted_artifact', verified_loader)
    monkeypatch.setattr(cli, 'ModelScorer', lambda _artifact: object())
    assert main(['score-run', *base, '--run-id', 'run_model', '--scorer', 'model',
                 '--threshold', 'no_alert', '--artifact-dir', str(tmp_path),
                 '--manifest-sha', 'a' * 64]) == 0
    from fraudlens.data_store import RunStore

    store = RunStore(output)
    assert store.list_active('rules')['snapshot_ref'] == 'run_empty'
    store.close()
