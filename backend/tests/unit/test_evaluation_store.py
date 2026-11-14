"""Controlled parity for bounded SQLite chronology against T027 in-memory split."""

import sqlite3

from test_evaluation_protocol import SOURCE_HASH, START, _population

from fraudlens.evaluation import build_split_manifest
from fraudlens.evaluation_store import audit_sqlite_split


def test_bounded_sqlite_split_matches_existing_membership_and_counts(tmp_path):
    dataset, snapshots, labels = _population()
    expected = build_split_manifest(dataset_version=dataset, snapshots=snapshots,
                                    labels=labels, source_start=START,
                                    expected_source_sha256=SOURCE_HASH)
    path = tmp_path / 'source.sqlite'
    connection = sqlite3.connect(path)
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
                       (dataset.dataset_version, 'complete', len(snapshots), 0,
                        dataset.source_sha256, dataset.mapping_sha256,
                        dataset.time_policy_sha256))
    connection.execute('INSERT INTO feature_builds VALUES (?,?,?,?)',
                       (dataset.dataset_version, 'history-v1', 'complete', len(snapshots)))
    connection.executemany('INSERT INTO feature_snapshots VALUES (?,?,?,?,?,?)',
                           ((dataset.dataset_version, 'history-v1', item.transaction_id,
                             item.event_time.isoformat(), int(item.scoreable),
                             item.coverage_state) for item in snapshots))
    connection.executemany('INSERT INTO private_evaluation_labels VALUES (?,?,?,?)',
                           ((dataset.dataset_version, item.transaction_id,
                             item.status, item.value) for item in labels))
    connection.commit()
    connection.close()
    actual = audit_sqlite_split(path, dataset.dataset_version)
    assert actual['eligible'] == expected.eligible, (actual['ineligibility_reasons'],
                                                   actual['partitions'])
    assert actual['warmup_count'] == len(expected.warmup_excluded_ids)
    assert actual['coverage_excluded_count'] == len(expected.coverage_excluded_ids)
    for role, part in expected.partitions.items():
        observed = actual['partitions'][role]
        assert observed['count'] == part.event_valid_count
        assert observed['positives'] == part.positives
        assert observed['negatives'] == part.negatives
        assert observed['first'] == (part.first_event_time.isoformat()
                                     if part.first_event_time else None)
        assert observed['last'] == (part.last_event_time.isoformat()
                                    if part.last_event_time else None)
        ids = connection_id_list(path, role, actual)
        assert ids == list(part.transaction_ids)


def connection_id_list(path, role, audit):
    bounds = audit['train_end'], audit['validation_end']
    where = {'train': 'event_time<=?',
             'validation': 'event_time>? AND event_time<=?',
             'test': 'event_time>?'}[role]
    args = {'train': (bounds[0],), 'validation': bounds, 'test': (bounds[1],)}[role]
    with sqlite3.connect(f'{path.as_uri()}?mode=ro', uri=True) as connection:
        return [row[0] for row in connection.execute(
            f'SELECT transaction_id FROM feature_snapshots WHERE scoreable=1 AND {where} '
            'ORDER BY event_time,transaction_id', args)]
