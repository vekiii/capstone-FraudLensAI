"""Bounded, read-only real-source chronology audit for the T029 protocol."""

import hashlib
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from fraudlens.data_import import derive_dataset_version


def nearest_boundary(groups, numerator, denominator, total, lower, upper):
    """Return a group-end index, preferring the earlier end on equal distance."""
    if lower >= upper:
        raise ValueError('insufficient timestamp groups')
    return min(range(lower, upper), key=lambda i: (
        abs(groups[i][1] * denominator - numerator * total), groups[i][1]))


def _groups(connection, version, *, scoreable):
    condition = 'AND scoreable=1' if scoreable else ''
    cursor = connection.execute(
        'SELECT event_time,COUNT(*) FROM feature_snapshots '
        f'WHERE version=? AND feature_version=? {condition} '
        'GROUP BY event_time ORDER BY event_time', (version, 'history-v1'))
    groups = []
    cumulative = 0
    for event_time, count in cursor:
        cumulative += count
        groups.append((event_time, cumulative))
    return groups


def _bounds(groups, train_numerator, train_denominator,
            validation_numerator, validation_denominator):
    total = groups[-1][1]
    first = nearest_boundary(groups, train_numerator, train_denominator, total, 0,
                             len(groups) - 2)
    second = nearest_boundary(groups, validation_numerator, validation_denominator, total,
                              first + 1, len(groups) - 1)
    return groups[first][0], groups[second][0], groups[first][1], groups[second][1]


def audit_sqlite_split(path: Path, expected_version: str) -> dict:
    """Scan time groups, freeze membership, then join labels in a later pass.

    Uses SQLite's read-only mode and an O(number of distinct timestamps) group
    table. No feature payloads, labels or event IDs are retained in Python.
    """
    uri = f'{Path(path).resolve().as_uri()}?mode=ro'
    connection = sqlite3.connect(uri, uri=True)
    connection.execute('PRAGMA query_only=ON')
    connection.execute('PRAGMA temp_store=FILE')
    try:
        row = connection.execute(
            'SELECT status,source_records,rejected_records,source_sha256,'
            'mapping_sha256,time_policy_sha256 FROM dataset_versions WHERE id=?',
            (expected_version,)).fetchone()
        if row is None or row[0] != 'complete' or row[2] != 0:
            raise ValueError('complete dataset version required')
        derived = derive_dataset_version(*(bytes.fromhex(item) for item in row[3:]))
        if derived != expected_version:
            raise ValueError('dataset provenance mismatch')
        build = connection.execute(
            'SELECT status,snapshot_count FROM feature_builds '
            'WHERE version=? AND feature_version=?',
            (expected_version, 'history-v1')).fetchone()
        if build != ('complete', row[1]):
            raise ValueError('complete history-v1 build required')
        scoreable = _groups(connection, expected_version, scoreable=True)
        if len(scoreable) < 3:
            raise ValueError('insufficient scoreable timestamp groups')
        start = connection.execute(
            'SELECT MIN(event_time) FROM feature_snapshots WHERE version=?',
            (expected_version,)).fetchone()[0]
        cutoff = (datetime.fromisoformat(start) + timedelta(hours=24)).isoformat()
        if scoreable[0][0] < cutoff:
            raise ValueError('warm-up boundary violated')
        train_time, validation_time, train_count, validation_total = _bounds(
            scoreable, 7, 10, 17, 20)
        boundaries = (train_time, validation_time)
        # The notebook used the full raw history, including warm-up, for 60/20/20.
        all_groups = _groups(connection, expected_version, scoreable=False)
        old_train, old_validation, _, _ = _bounds(all_groups, 6, 10, 8, 10)
        roles = {'train': {'count': 0, 'positive': 0, 'negative': 0, 'hash': hashlib.sha256()},
                 'validation': {'count': 0, 'positive': 0, 'negative': 0,
                                'hash': hashlib.sha256()},
                 'test': {'count': 0, 'positive': 0, 'negative': 0,
                          'hash': hashlib.sha256()}}
        first_last = {role: [None, None] for role in roles}
        overlap = {role: {'old_train': 0, 'old_validation': 0, 'old_test': 0}
                   for role in roles}
        warmup_count = 0
        covered_count = 0
        # Membership role is computed exclusively from frozen event time and
        # coverage. The private-label join is used only for post-freeze counts.
        cursor = connection.execute('''
            SELECT s.transaction_id,s.event_time,s.scoreable,s.coverage_state,
                   l.status,l.value
            FROM feature_snapshots AS s
            LEFT JOIN private_evaluation_labels AS l
              ON l.version=s.version AND l.transaction_id=s.transaction_id
            WHERE s.version=? AND s.feature_version=?
            ORDER BY s.event_time,s.transaction_id
        ''', (expected_version, 'history-v1'))
        seen = 0
        for event_id, at, score, coverage, status, value in cursor:
            seen += 1
            if at < cutoff:
                warmup_count += 1
                if score or coverage == 'full':
                    raise ValueError('warm-up coverage inconsistent')
                continue
            if not score or coverage != 'full':
                covered_count += 1
                continue
            role = 'train' if at <= boundaries[0] else (
                'validation' if at <= boundaries[1] else 'test')
            old_role = 'old_train' if at <= old_train else (
                'old_validation' if at <= old_validation else 'old_test')
            current = roles[role]
            current['count'] += 1
            current['hash'].update(event_id.encode('ascii') + b'\n')
            first_last[role][0] = first_last[role][0] or at
            first_last[role][1] = at
            overlap[role][old_role] += 1
            if status == 'eligible_positive' and value == 1:
                current['positive'] += 1
            elif status == 'eligible_negative' and value == 0:
                current['negative'] += 1
            else:
                raise ValueError('ineligible or missing scoreable label')
        if (seen != row[1] or train_count != roles['train']['count']
                or validation_total != roles['train']['count'] + roles['validation']['count']
                or seen != warmup_count + covered_count
                + sum(item['count'] for item in roles.values())):
            raise ValueError('split count reconciliation failed')
        output = {}
        reasons = []
        for role, current in roles.items():
            positives, negatives = current['positive'], current['negative']
            if not positives or not negatives:
                reasons.append(f'{role}_requires_both_classes')
            if role in {'validation', 'test'} and positives < 20:
                reasons.append(f'{role}_requires_20_positives')
            output[role] = {'count': current['count'], 'positives': positives,
                            'negatives': negatives,
                            'prevalence': positives / current['count'] if current['count'] else None,
                            'first': first_last[role][0], 'last': first_last[role][1],
                            'ids_sha256': current['hash'].hexdigest(),
                            'old_60_20_20_overlap': overlap[role]}
        return {'dataset_version': expected_version, 'source_sha256': row[3],
                'mapping_sha256': row[4], 'time_policy_sha256': row[5],
                'feature_version': 'history-v1', 'source_records': row[1],
                'snapshot_count': seen, 'timestamp_group_count': len(scoreable),
                'source_start': start, 'warmup_cutoff': cutoff,
                'warmup_count': warmup_count, 'coverage_excluded_count': covered_count,
                'scoreable_count': scoreable[-1][1],
                'train_end': train_time, 'validation_end': validation_time,
                'old_60_20_20_train_end': old_train,
                'old_60_20_20_validation_end': old_validation,
                'partitions': output, 'eligible': not reasons,
                'ineligibility_reasons': reasons}
    finally:
        connection.close()
