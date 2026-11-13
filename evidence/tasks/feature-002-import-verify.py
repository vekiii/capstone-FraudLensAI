"""Read-only aggregate verification of the local Feature 002 IBM import."""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--mapping', type=Path, required=True)
    parser.add_argument('--store', type=Path, required=True)
    args = parser.parse_args()
    uri = args.store.resolve().as_uri() + '?mode=ro'
    with sqlite3.connect(uri, uri=True) as connection:
        version = connection.execute(
            'SELECT version FROM active_dataset WHERE singleton=1').fetchone()[0]
        stage = connection.execute(
            'SELECT status,source_records,rejected_records,source_sha256,'
            'mapping_sha256,time_policy_sha256 FROM dataset_versions WHERE id=?',
            (version,)).fetchone()
        event_count, distinct_d, distinct_c = connection.execute(
            'SELECT COUNT(*),COUNT(DISTINCT transaction_id),COUNT(DISTINCT case_id) '
            'FROM operational_events WHERE version=?', (version,)).fetchone()
        label_count, eligible, positives, negatives = connection.execute(
            'SELECT COUNT(*),SUM(CASE WHEN status IN '
            "('eligible_positive','eligible_negative') THEN 1 ELSE 0 END),"
            "SUM(CASE WHEN status='eligible_positive' THEN 1 ELSE 0 END),"
            "SUM(CASE WHEN status='eligible_negative' THEN 1 ELSE 0 END) "
            'FROM private_evaluation_labels WHERE version=?', (version,)).fetchone()
        schema = connection.execute('PRAGMA user_version').fetchone()[0]
        integrity = connection.execute('PRAGMA quick_check').fetchone()[0]
    source_hash = sha256(args.source)
    mapping_hash = hashlib.sha256(
        args.mapping.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
    result = {
        'dataset_version': version, 'status': stage[0], 'source_records': stage[1],
        'event_valid': event_count, 'event_rejected': stage[2],
        'label_eligible': eligible, 'label_ineligible': event_count - eligible,
        'positives': positives, 'negatives': negatives,
        'private_label_records': label_count,
        'distinct_transaction_ids': distinct_d, 'distinct_case_ids': distinct_c,
        'source_sha256': source_hash, 'stored_source_sha256': stage[3],
        'mapping_sha256': mapping_hash, 'stored_mapping_sha256': stage[4],
        'time_policy_sha256': stage[5], 'sqlite_schema_version': schema,
        'sqlite_quick_check': integrity, 'database_bytes': args.store.stat().st_size,
    }
    result['reconciled'] = (
        stage[0] == 'complete' and stage[1] == event_count + stage[2]
        and event_count == eligible + result['label_ineligible']
        and eligible == positives + negatives
        and label_count == event_count and distinct_d == event_count
        and distinct_c == event_count and source_hash == stage[3]
        and mapping_hash == stage[4] and schema == 1 and integrity == 'ok')
    print(json.dumps(result, sort_keys=True))
    if not result['reconciled']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
