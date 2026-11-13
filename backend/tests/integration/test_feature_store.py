"""T020: authored-only CLI and SQLite feature-build publication checks."""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from fraudlens.data_import import derive_dataset_version, parse_canonical_source
from fraudlens.data_store import DatasetStore
from fraudlens.pipeline_cli import main

ROOT = Path(__file__).resolve().parents[3]
HEADER = ('Timestamp,From Bank,Account,To Bank,Account,Amount Received,'
          'Receiving Currency,Amount Paid,Payment Currency,Payment Format,'
          'Is Laundering\n')
ROWS = ('2026/01/01 00:00,A,1,R,1,7,US Dollar,10,Euro,Wire,0\n'
        '2026/01/02 00:00,A,1,R,1,9,US Dollar,20,Euro,Wire,\n'
        '2026/01/02 00:01,A,1,R,1,11,US Dollar,30,Euro,Wire,invalid\n')


def seed(store, *, source_marker=b'source-v1', with_provenance=True):
    raw = (HEADER + ROWS).encode()
    parsed = parse_canonical_source(raw, namespace='synthetic:t020', member='authored.csv')
    source = hashlib.sha256(source_marker).digest()
    mapping = hashlib.sha256(b'approved-synthetic-mapping').digest()
    policy = hashlib.sha256(b'assumed-utc').digest()
    version = derive_dataset_version(source, mapping, policy)
    provenance = dict(source_sha256=source.hex(), mapping_sha256=mapping.hex(),
                      time_policy_sha256=policy.hex()) if with_provenance else {}
    store.stage(version, source_records=3, **provenance)
    for event, label in zip(parsed.events, parsed.private_labels, strict=True):
        store.add_event(version, event)
        store.add_private_label(version, event.transaction_id, value=label.value,
                                status=label.status)
    store.complete(version)
    return version


def cli_args(path, version):
    return ['build-features', '--store', str(path), '--dataset-version', version]


def test_cli_build_features_complete_and_idempotent(tmp_path, capsys):
    path = tmp_path / 'authored.sqlite'
    store = DatasetStore(path)
    version = seed(store)
    store.activate(version)
    store.close()
    assert main(cli_args(path, version)) == 0
    first = json.loads(capsys.readouterr().out)
    assert first == {'status': 'complete', 'dataset_version': version,
                     'feature_version': 'history-v1', 'snapshot_count': 3,
                     'repeated': False}
    replay = subprocess.run(
        [sys.executable, '-m', 'fraudlens.pipeline_cli', *cli_args(path, version)],
        cwd=ROOT, env={**os.environ, 'PYTHONPATH': str(ROOT / 'backend/src')},
        capture_output=True, text=True, check=False)
    assert replay.returncode == 0
    assert json.loads(replay.stdout) == {**first, 'repeated': True}
    reopened = DatasetStore(path)
    assert reopened.feature_snapshot_count(version) == 3
    assert reopened.active_version() == version
    rows = reopened.connection.execute('''
        SELECT payload_json,coverage_state FROM feature_snapshots
        WHERE version=? ORDER BY as_of''', (version,)).fetchall()
    assert [state for _, state in rows] == ['incomplete', 'full', 'full']
    assert json.loads(rows[1][0])['sender_out_count_24h'] == 1
    assert all('label' not in payload and 'transaction_id' not in payload
               for payload, _ in rows)
    snapshots = list(reopened.iter_feature_snapshots(version))
    assert len(snapshots) == 3
    assert snapshots[1].feature_values['sender_paid_sum_same_currency_24h'] == 10
    reopened.close()


def test_cli_rejects_staged_and_incompatible_versions(tmp_path, capsys):
    path = tmp_path / 'authored.sqlite'
    store = DatasetStore(path)
    staged = 'dv_' + 'a' * 64
    store.stage(staged, source_records=0)
    incompatible = seed(store, source_marker=b'without-provenance',
                        with_provenance=False)
    store.close()
    assert main(cli_args(path, staged)) == 2
    assert json.loads(capsys.readouterr().out)['error_codes'] == ['dataset_incomplete']
    assert main(cli_args(path, incompatible)) == 2
    assert json.loads(capsys.readouterr().out)['error_codes'] == ['dataset_incompatible']
    assert main(cli_args(path, incompatible) + ['--feature-version', 'history-v2']) == 2
    assert json.loads(capsys.readouterr().out)['error_codes'] == ['dataset_incompatible']
    reopened = DatasetStore(path)
    assert reopened.feature_snapshot_count(staged) is None
    assert reopened.feature_snapshot_count(incompatible) is None
    reopened.close()


def test_interruption_hides_partial_build_and_preserves_previous_complete(
        tmp_path, monkeypatch):
    path = tmp_path / 'authored.sqlite'
    store = DatasetStore(path)
    old = seed(store)
    new = seed(store, source_marker=b'source-v2')
    store.build_features(old)
    store.close()
    original = DatasetStore._write_feature_batch

    def interrupted(self, batch):
        original(self, batch)
        raise RuntimeError('injected interruption after committed batch')

    monkeypatch.setattr(DatasetStore, '_write_feature_batch', interrupted)
    reopened = DatasetStore(path)
    with pytest.raises(RuntimeError, match='injected interruption'):
        reopened.build_features(new)
    assert reopened.feature_snapshot_count(new) is None
    assert reopened.feature_snapshot_count(old) == 3
    assert reopened.connection.execute(
        'SELECT COUNT(*) FROM feature_snapshots WHERE version=?', (new,)).fetchone()[0] == 0
    reopened.close()
    monkeypatch.setattr(DatasetStore, '_write_feature_batch', original)
    restarted = DatasetStore(path)
    assert restarted.build_features(new) == {'snapshot_count': 3, 'repeated': False}
    assert restarted.feature_snapshot_count(new) == 3
    assert restarted.feature_snapshot_count(old) == 3
    restarted.close()


def test_abandoned_staged_build_is_invisible_and_retryable(tmp_path):
    path = tmp_path / 'authored.sqlite'
    store = DatasetStore(path)
    version = seed(store)
    store._ensure_feature_tables()
    with store.connection:
        store.connection.execute('''
            INSERT INTO feature_builds(version,feature_version,status,snapshot_count)
            VALUES (?,'history-v1','staged',1)''', (version,))
        store.connection.execute('''
            INSERT INTO feature_snapshots VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
            (version, 'history-v1', 'partial', '2026-01-01T00:00:00+00:00',
             '2026-01-01T00:00:00+00:00', '2026-01-01T00:00:00+00:00',
             'incomplete', 0, 'x', '2026-01-01T00:00:00+00:00', '{}'))
    store.close()
    reopened = DatasetStore(path)
    assert reopened.feature_snapshot_count(version) is None
    with pytest.raises(ValueError, match='feature_build_incomplete'):
        list(reopened.iter_feature_snapshots(version))
    assert reopened.build_features(version)['snapshot_count'] == 3
    assert reopened.feature_snapshot_count(version) == 3
    assert reopened.connection.execute(
        "SELECT COUNT(*) FROM feature_snapshots WHERE transaction_id='partial'").fetchone()[0] == 0
    reopened.close()


def test_feature_writes_use_bounded_batches(tmp_path, monkeypatch):
    path = tmp_path / 'authored.sqlite'
    store = DatasetStore(path)
    rows = ''.join(
        f'2026/01/01 {index // 60:02d}:{index % 60:02d},A,1,R,1,'
        '7,US Dollar,10,Euro,Wire,\n'
        for index in range(513))
    parsed = parse_canonical_source((HEADER + rows).encode(),
                                    namespace='synthetic:t020-batches',
                                    member='authored.csv')
    assert parsed.report.event_valid == 513
    source = hashlib.sha256(b'batch-source').digest()
    mapping = hashlib.sha256(b'batch-mapping').digest()
    policy = hashlib.sha256(b'batch-time-policy').digest()
    version = derive_dataset_version(source, mapping, policy)
    store.stage(version, source_records=513, source_sha256=source.hex(),
                mapping_sha256=mapping.hex(), time_policy_sha256=policy.hex())
    for event, label in zip(parsed.events, parsed.private_labels, strict=True):
        store.add_event(version, event)
        store.add_private_label(version, event.transaction_id, value=label.value,
                                status=label.status)
    store.complete(version)
    lengths = []
    original = store._write_feature_batch

    def measured(batch):
        lengths.append(len(batch))
        original(batch)

    monkeypatch.setattr(store, '_write_feature_batch', measured)
    assert store.build_features(version) == {'snapshot_count': 513, 'repeated': False}
    assert lengths == [512, 1]
    store.close()
