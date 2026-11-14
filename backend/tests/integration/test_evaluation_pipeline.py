"""T035 RED: controlled CLI freeze and holdout disclosure behavior."""

import hashlib
import json
import sqlite3

from fraudlens.data_import import derive_dataset_version
from fraudlens.evaluation_store import audit_sqlite_split
from fraudlens.pipeline_cli import main


def _controlled_source(tmp_path, *, test_positives=25):
    source = tmp_path / 'source.sqlite'
    hashes = ('a' * 64, 'b' * 64, 'c' * 64)
    version = derive_dataset_version(*(bytes.fromhex(item) for item in hashes))
    connection = sqlite3.connect(source)
    connection.executescript('''
        CREATE TABLE dataset_versions(id TEXT,status TEXT,source_records INTEGER,
            rejected_records INTEGER,source_sha256 TEXT,mapping_sha256 TEXT,
            time_policy_sha256 TEXT);
        CREATE TABLE feature_builds(version TEXT,feature_version TEXT,status TEXT,
            snapshot_count INTEGER);
        CREATE TABLE feature_snapshots(version TEXT,feature_version TEXT,
            transaction_id TEXT,event_time TEXT,scoreable INTEGER,coverage_state TEXT);
        CREATE TABLE private_evaluation_labels(version TEXT,transaction_id TEXT,
            status TEXT,value INTEGER);
    ''')
    connection.execute('INSERT INTO dataset_versions VALUES (?,?,?,?,?,?,?)',
                       (version, 'complete', 151, 0, *hashes))
    connection.execute('INSERT INTO feature_builds VALUES (?,?,?,?)',
                       (version, 'history-v1', 'complete', 151))
    times = ['2026-01-02T00:00:00+00:00', '2026-01-03T00:00:00+00:00',
             '2026-01-04T00:00:00+00:00']
    connection.execute('INSERT INTO feature_snapshots VALUES (?,?,?,?,?,?)',
                       (version, 'history-v1', 'warm',
                        '2026-01-01T00:00:00+00:00', 0, 'incomplete'))
    connection.execute('INSERT INTO private_evaluation_labels VALUES (?,?,?,?)',
                       (version, 'warm', 'eligible_negative', 0))
    for group, at in enumerate(times):
        for row in range(50):
            event_id = f'event-{group}-{row:02}'
            positive = row < (test_positives if group == 2 else 25)
            connection.execute('INSERT INTO feature_snapshots VALUES (?,?,?,?,?,?)',
                               (version, 'history-v1', event_id, at, 1, 'full'))
            connection.execute('INSERT INTO private_evaluation_labels VALUES (?,?,?,?)',
                               (version, event_id,
                                'eligible_positive' if positive else 'eligible_negative',
                                int(positive)))
    connection.commit()
    connection.close()
    audit = audit_sqlite_split(source, version)
    config = tmp_path / 'protocol.json'
    config.write_text(json.dumps({'dataset_version': version,
                                  'source_sha256': hashes[0],
                                  'split': {'train_end_inclusive': audit['train_end'],
                                            'validation_end_inclusive': audit['validation_end'],
                                            'partitions': audit['partitions']},
                                  'eligibility': {'eligible': audit['eligible']}}))
    return source, version, config


def test_freeze_rejects_missing_source_without_changing_config(tmp_path, capsys):
    config = tmp_path / 'protocol.json'
    config.write_text('{"version":"controlled-test-v1"}')
    before = config.read_bytes()
    code = main(['freeze-protocol', '--store', str(tmp_path / 'missing.sqlite'),
                 '--dataset-version', 'dv_' + 'a' * 64, '--config', str(config)])
    assert code == 2
    assert config.read_bytes() == before
    assert json.loads(capsys.readouterr().out)['error_codes'] == ['source_missing']


def test_freeze_accepts_exact_controlled_source_and_rejects_tampered_config(tmp_path, capsys):
    source, version, config = _controlled_source(tmp_path)
    args = ['freeze-protocol', '--store', str(source), '--dataset-version', version,
            '--config', str(config)]
    assert main(args) == 0
    assert json.loads(capsys.readouterr().out)['status'] == 'frozen'
    changed = json.loads(config.read_text())
    changed['split']['partitions']['test']['count'] += 1
    config.write_text(json.dumps(changed))
    before = config.read_bytes()
    assert main(args) == 2
    assert config.read_bytes() == before
    assert json.loads(capsys.readouterr().out)['error_codes'] == ['protocol_source_mismatch']


def test_freeze_ineligible_source_reports_status_without_fit(tmp_path, capsys):
    source, version, config = _controlled_source(tmp_path, test_positives=0)
    assert main(['freeze-protocol', '--store', str(source),
                 '--dataset-version', version, '--config', str(config)]) == 2
    assert json.loads(capsys.readouterr().out)['error_codes'] == ['source_ineligible']


def test_evaluate_first_disclosure_then_exploratory_reuse(tmp_path, capsys):
    protocol = tmp_path / 'protocol.json'
    protocol.write_text(json.dumps({'version': 'controlled-test-v1',
                                    'holdout': {'old_tree_60_20_20_test_exposure': True}}))
    digest = hashlib.sha256(protocol.read_bytes()).hexdigest()
    predictions = tmp_path / 'predictions.json'
    predictions.write_text(json.dumps({
        'frozen': True, 'candidate_status': 'selected', 'protocol_sha256': digest,
        'thresholds': {'model': 0.5, 'rules': 'no_alert'},
        'predictions': {'model': [['a', 0.9], ['b', 0.1]],
                        'rules': [['a', 0.65], ['b', 0.0]]}}))
    labels = tmp_path / 'labels.json'
    labels.write_text(json.dumps({'a': 1, 'b': 0}))
    ledger = tmp_path / 'ledger.json'
    report = tmp_path / 'report.json'
    args = ['evaluate', '--protocol', str(protocol), '--predictions', str(predictions),
            '--labels', str(labels), '--ledger', str(ledger), '--report', str(report)]
    assert main(args) == 0
    first = json.loads(report.read_text())
    assert first['disclosure'] == 'first_disclosure'
    assert first['independent_confirmatory_claim'] is False
    assert first['metrics']['model']['confusion']['tp'] == 1
    first_output = json.loads(capsys.readouterr().out)
    assert first_output['report_sha256'] == hashlib.sha256(report.read_bytes()).hexdigest()
    report.unlink()
    assert main(args) == 0
    second = json.loads(report.read_text())
    assert second['disclosure'] == 'exploratory_reuse'
    capsys.readouterr()


def test_evaluate_rejects_failed_candidate_and_mismatched_ids(tmp_path, capsys):
    protocol = tmp_path / 'protocol.json'
    protocol.write_text('{"version":"controlled-test-v1"}')
    digest = hashlib.sha256(protocol.read_bytes()).hexdigest()
    predictions = tmp_path / 'predictions.json'
    payload = {'frozen': True, 'candidate_status': 'failed',
               'protocol_sha256': digest,
               'thresholds': {'model': 0.5, 'rules': 0.5},
               'predictions': {'model': [['a', 0.8], ['b', 0.1]],
                               'rules': [['a', 0.65], ['b', 0.0]]}}
    predictions.write_text(json.dumps(payload))
    labels = tmp_path / 'labels.json'
    labels.write_text('{"a":1,"b":0}')
    args = ['evaluate', '--protocol', str(protocol), '--predictions', str(predictions),
            '--labels', str(labels), '--ledger', str(tmp_path / 'ledger.json'),
            '--report', str(tmp_path / 'report.json')]
    assert main(args) == 2
    assert json.loads(capsys.readouterr().out)['error_codes'] == ['frozen_predictions_required']
    assert not (tmp_path / 'ledger.json').exists()
    payload['candidate_status'] = 'selected'
    payload['predictions']['rules'][1][0] = 'other'
    predictions.write_text(json.dumps(payload))
    assert main(args) == 2
    assert json.loads(capsys.readouterr().out)['error_codes'] == ['prediction_identities_mismatch']
    assert not (tmp_path / 'ledger.json').exists()


def test_evaluate_refuses_unfrozen_predictions_before_labels(tmp_path, capsys):
    protocol = tmp_path / 'protocol.json'
    protocol.write_text('{"version":"controlled-test-v1"}')
    predictions = tmp_path / 'predictions.json'
    predictions.write_text('{"frozen":false}')
    ledger = tmp_path / 'ledger.json'
    code = main(['evaluate', '--protocol', str(protocol),
                 '--predictions', str(predictions), '--labels', str(tmp_path / 'missing'),
                 '--ledger', str(ledger), '--report', str(tmp_path / 'report')])
    assert code == 2
    assert not ledger.exists()
    assert json.loads(capsys.readouterr().out)['error_codes'] == ['frozen_predictions_required']
