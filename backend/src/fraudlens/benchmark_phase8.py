"""Bounded, label-free frozen test prediction and later private-label extraction."""

import argparse
import hashlib
import json
import resource
import sqlite3
import time
from pathlib import Path

import numpy as np

from fraudlens.model_scoring import load_trusted_artifact
from fraudlens.train_phase5 import CATEGORICAL, FEATURES, NUMERIC, _rules


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _source(path: Path):
    connection = sqlite3.connect(f'{path.resolve().as_uri()}?mode=ro', uri=True)
    connection.execute('PRAGMA query_only=ON')
    connection.execute('PRAGMA temp_store=FILE')
    return connection


def _identity_check(connection, protocol):
    version = protocol['dataset_version']
    if connection.execute('''SELECT status,source_sha256,mapping_sha256,
        time_policy_sha256 FROM dataset_versions WHERE id=?''',
                          (version,)).fetchone() != (
                              'complete', protocol['source_sha256'],
                              protocol['mapping_sha256'], protocol['time_policy_sha256']):
        raise ValueError('dataset version incomplete')
    if connection.execute('''SELECT status FROM feature_builds
        WHERE version=? AND feature_version='history-v1' ''',
                          (version,)).fetchone() != ('complete',):
        raise ValueError('feature build incomplete')
    for role, condition in (
        ('train', 'event_time<=?'),
        ('validation', 'event_time>? AND event_time<=?'),
        ('test', 'event_time>?')):
        split = protocol['split']
        params = ((split['train_end_inclusive'],) if role == 'train' else
                  (split['train_end_inclusive'], split['validation_end_inclusive'])
                  if role == 'validation' else (split['validation_end_inclusive'],))
        count = connection.execute(f'''SELECT COUNT(*) FROM feature_snapshots
            WHERE version=? AND feature_version='history-v1' AND scoreable=1
              AND {condition}''', (version, *params)).fetchone()[0]
        if count != split['partitions'][role]['count']:
            raise ValueError(f'{role} count mismatch')


def _batch_scores(rows, pipeline):
    matrix = np.empty((len(rows), len(FEATURES)), dtype=object)
    rules = []
    for index, (_, payload) in enumerate(rows):
        values = json.loads(payload)
        for column, key in enumerate(NUMERIC):
            matrix[index, column] = (float(values[key]) if values[key] is not None
                                     else np.nan)
        for column, key in enumerate(CATEGORICAL, len(NUMERIC)):
            matrix[index, column] = (values[key] if values[key] is not None
                                     else '__missing__')
        rules.append(_rules(values))
    model = pipeline.predict_proba(matrix)[:, 1]
    return [float(score) for score in model], rules


def predict(source: Path, protocol_path: Path, artifact_dir: Path,
            manifest_sha: str, output: Path) -> dict:
    if output.exists():
        raise ValueError('predictions already exist')
    started = time.monotonic()
    protocol_raw = protocol_path.read_bytes()
    protocol_sha = hashlib.sha256(protocol_raw).hexdigest()
    protocol = json.loads(protocol_raw)
    if not protocol['eligibility']['eligible']:
        raise ValueError('ineligible protocol')
    artifact = load_trusted_artifact(
        artifact_dir, expected_manifest_sha256=manifest_sha,
        expected_dataset_version=protocol['dataset_version'],
        expected_protocol_sha256=protocol_sha)
    if (artifact.manifest['ordered_features'] != list(FEATURES)
            or artifact.manifest['validation_threshold']['threshold'] != 'no_alert'):
        raise ValueError('frozen model or threshold mismatch')
    metadata = json.loads((artifact_dir / 'metadata.json').read_text())
    thresholds = {'model': metadata['model_validation_threshold']['threshold'],
                  'rules': metadata['rules_validation_threshold']['threshold']}
    connection = _source(source)
    try:
        _identity_check(connection, protocol)
        cursor = connection.execute('''
            SELECT transaction_id,payload_json FROM feature_snapshots
            WHERE version=? AND feature_version='history-v1' AND scoreable=1
              AND event_time>? ORDER BY event_time,transaction_id''',
            (protocol['dataset_version'], protocol['split']['validation_end_inclusive']))
        model_rows = []
        rules_rows = []
        digest = hashlib.sha256()
        while True:
            rows = cursor.fetchmany(10000)
            if not rows:
                break
            model_scores, rule_scores = _batch_scores(rows, artifact.pipeline)
            for (event_id, _), model_score, rule_score in zip(
                    rows, model_scores, rule_scores, strict=True):
                digest.update((event_id + '\n').encode('ascii'))
                model_rows.append([event_id, model_score])
                rules_rows.append([event_id, rule_score])
        count = len(model_rows)
        expected = protocol['split']['partitions']['test']
        if count != expected['count'] or digest.hexdigest() != expected['ids_sha256']:
            raise ValueError('frozen test membership mismatch')
    finally:
        connection.close()
    bundle = {
        'frozen': True, 'candidate_status': 'selected',
        'protocol_sha256': protocol_sha, 'manifest_sha256': manifest_sha,
        'source_sha256': protocol['source_sha256'],
        'dataset_version': protocol['dataset_version'],
        'feature_version': 'history-v1', 'ordered_features': list(FEATURES),
        'thresholds': thresholds,
        'predictions': {'model': model_rows, 'rules': rules_rows},
        'test_ids_sha256': digest.hexdigest(),
        'resource': {'elapsed_seconds': time.monotonic() - started,
                     'peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},
    }
    with output.open('x') as target:
        json.dump(bundle, target, separators=(',', ':'))
        target.write('\n')
    return {'status': 'frozen_predictions_saved', 'rows': count,
            'predictions_sha256': sha256(output), 'test_ids_sha256': digest.hexdigest(),
            'resource': bundle['resource']}


def labels(source: Path, protocol_path: Path, predictions: Path, output: Path) -> dict:
    """Open test labels only after the prediction file exists and passes ID checks."""
    if output.exists():
        raise ValueError('labels output already exists')
    protocol = json.loads(protocol_path.read_text())
    bundle = json.loads(predictions.read_text())
    if (bundle.get('protocol_sha256') != sha256(protocol_path)
            or bundle.get('test_ids_sha256')
            != protocol['split']['partitions']['test']['ids_sha256']):
        raise ValueError('predictions not frozen for protocol')
    ids = [row[0] for row in bundle['predictions']['model']]
    if (ids != [row[0] for row in bundle['predictions']['rules']]
            or len(ids) != protocol['split']['partitions']['test']['count']
            or hashlib.sha256(''.join(i + '\n' for i in ids).encode('ascii')).hexdigest()
            != bundle['test_ids_sha256']):
        raise ValueError('prediction identities mismatch')
    connection = _source(source)
    try:
        cursor = connection.execute('''
            SELECT s.transaction_id,l.value,l.status FROM feature_snapshots AS s
            JOIN private_evaluation_labels AS l
              ON l.version=s.version AND l.transaction_id=s.transaction_id
            WHERE s.version=? AND s.feature_version='history-v1' AND s.scoreable=1
              AND s.event_time>? ORDER BY s.event_time,s.transaction_id''',
            (protocol['dataset_version'], protocol['split']['validation_end_inclusive']))
        truth = {}
        positives = 0
        for index, (event_id, value, status) in enumerate(cursor):
            if (index >= len(ids) or event_id != ids[index]
                    or status not in {'eligible_positive', 'eligible_negative'}
                    or value not in (0, 1)):
                raise ValueError('private label population mismatch')
            truth[event_id] = value
            positives += value
        if (len(truth) != len(ids)
                or positives != protocol['split']['partitions']['test']['positives']):
            raise ValueError('private label counts mismatch')
    finally:
        connection.close()
    with output.open('x') as target:
        json.dump(truth, target, separators=(',', ':'))
        target.write('\n')
    return {'status': 'private_labels_saved', 'rows': len(truth),
            'positives': positives, 'labels_sha256': sha256(output)}


def coverage(source: Path, protocol_path: Path) -> dict:
    """Count bank-qualified sender overlap with earlier train rows, without labels."""
    protocol = json.loads(protocol_path.read_text())
    split = protocol['split']
    seen_train = set()
    counts = {role: {'seen': 0, 'unseen': 0} for role in
              ('train', 'validation', 'test')}
    connection = _source(source)
    try:
        _identity_check(connection, protocol)
        cursor = connection.execute('''
            SELECT s.event_time,json_extract(e.payload_json,'$.sender_join_key')
            FROM feature_snapshots AS s JOIN operational_events AS e
              ON e.version=s.version AND e.transaction_id=s.transaction_id
            WHERE s.version=? AND s.feature_version='history-v1' AND s.scoreable=1
            ORDER BY s.event_time,s.transaction_id''', (protocol['dataset_version'],))
        for at, key in cursor:
            role = ('train' if at <= split['train_end_inclusive'] else
                    'validation' if at <= split['validation_end_inclusive'] else 'test')
            if not isinstance(key, str) or not key:
                raise ValueError('bank-qualified sender key missing')
            counts[role]['seen' if key in seen_train else 'unseen'] += 1
            if role == 'train':
                seen_train.add(key)
        for role, values in counts.items():
            if sum(values.values()) != split['partitions'][role]['count']:
                raise ValueError('account coverage membership mismatch')
            values['seen_rate'] = values['seen'] / sum(values.values())
        return {'status': 'measured_label_free', 'basis':
                'sender bank-qualified join key previously observed in train',
                'partitions': counts, 'unique_train_sender_keys': len(seen_train)}
    finally:
        connection.close()


def main(argv=None):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('predict', 'labels', 'coverage'):
        command = sub.add_parser(name)
        command.add_argument('--source', type=Path, required=True)
        command.add_argument('--protocol', type=Path, required=True)
        if name != 'coverage':
            command.add_argument('--output', type=Path, required=True)
        if name == 'predict':
            command.add_argument('--artifact-dir', type=Path, required=True)
            command.add_argument('--manifest-sha', required=True)
        elif name == 'labels':
            command.add_argument('--predictions', type=Path, required=True)
    args = parser.parse_args(argv)
    result = (predict(args.source, args.protocol, args.artifact_dir,
                      args.manifest_sha, args.output) if args.command == 'predict'
              else labels(args.source, args.protocol, args.predictions, args.output)
              if args.command == 'labels' else coverage(args.source, args.protocol))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
