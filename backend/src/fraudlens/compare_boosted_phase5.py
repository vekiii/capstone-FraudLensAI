"""Exploratory tree/rules/boosting comparison on frozen validation only.

This command never reads the frozen test partition or changes the published model.
"""

import argparse
import hashlib
import json
import math
import sqlite3
import time
from pathlib import Path

import joblib
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from threadpoolctl import threadpool_limits

from fraudlens.data_import import derive_dataset_version
from fraudlens.evaluation import fit_candidate_grid, select_threshold
from fraudlens.model_scoring import create_manifest, load_trusted_artifact
from fraudlens.process_metrics import peak_rss_bytes
from fraudlens.train_phase5 import FEATURES, NUMERIC, _load_development

FROZEN_MANIFEST_SHA = '2732691cb08daafba9d303ef6f3c8f616e03b3dc51505d3abb9772ceadd3919e'
BOOSTED_VERSION = 'model-history-v1-boosted-candidate'


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_source(store: Path, protocol: dict) -> dict:
    """Verify complete provenance and train/validation membership without labels."""
    connection = sqlite3.connect(f'{store.resolve().as_uri()}?mode=ro', uri=True)
    connection.execute('PRAGMA query_only=ON')
    connection.execute('PRAGMA temp_store=FILE')
    try:
        version = protocol['dataset_version']
        row = connection.execute('''
            SELECT status,source_records,rejected_records,source_sha256,
                   mapping_sha256,time_policy_sha256
            FROM dataset_versions WHERE id=?''', (version,)).fetchone()
        if (row is None or row[:3] != ('complete', 5078345, 0)
                or row[3:] != (protocol['source_sha256'], protocol['mapping_sha256'],
                               protocol['time_policy_sha256'])
                or derive_dataset_version(*(bytes.fromhex(value) for value in row[3:]))
                != version):
            raise ValueError('dataset provenance mismatch')
        build = connection.execute('''
            SELECT status,snapshot_count FROM feature_builds
            WHERE version=? AND feature_version='history-v1' ''', (version,)).fetchone()
        if build != ('complete', row[1]):
            raise ValueError('incomplete history-v1 build')
        hashes = [hashlib.sha256(), hashlib.sha256()]
        counts = [0, 0]
        cursor = connection.execute('''
            SELECT transaction_id,event_time FROM feature_snapshots
            WHERE version=? AND feature_version='history-v1' AND scoreable=1
              AND event_time<=? ORDER BY event_time,transaction_id''',
            (version, protocol['split']['validation_end_inclusive']))
        for event_id, at in cursor:
            role = int(at > protocol['split']['train_end_inclusive'])
            counts[role] += 1
            hashes[role].update(event_id.encode('ascii') + b'\n')
        parts = protocol['split']['partitions']
        for i, name in enumerate(('train', 'validation')):
            if (counts[i] != parts[name]['count']
                    or hashes[i].hexdigest() != parts[name]['ids_sha256']):
                raise ValueError(f'{name} membership mismatch')
        return {'dataset_version': version, 'complete_snapshots': build[1],
                'train_count': counts[0], 'validation_count': counts[1],
                'train_ids_sha256': hashes[0].hexdigest(),
                'validation_ids_sha256': hashes[1].hexdigest()}
    finally:
        connection.close()


def fit_boosted(train_x, train_y, validation_x, *, numeric_columns,
                categorical_columns):
    """Fit the frozen train-only preprocessing and one declared HGB candidate."""
    prepare = ColumnTransformer([
        ('numeric', Pipeline([('imputer', SimpleImputer(strategy='median')),
                              ('scale', StandardScaler())]), list(numeric_columns)),
        ('category', OneHotEncoder(handle_unknown='ignore'),
         list(categorical_columns)),
    ], sparse_threshold=0)
    model = HistGradientBoostingClassifier(
        max_iter=150, max_leaf_nodes=15, min_samples_leaf=100,
        learning_rate=0.1, class_weight='balanced', early_stopping=False,
        random_state=42)
    pipeline = Pipeline([('prepare', prepare), ('model', model)])
    with threadpool_limits(limits=2):
        pipeline.fit(train_x, train_y)
        scores = pipeline.predict_proba(validation_x)[:, 1]
    if not np.isfinite(scores).all() or np.any((scores < 0) | (scores > 1)):
        raise ValueError('invalid boosted validation scores')
    return pipeline, scores


def summarize(ids, scores, labels, *, k=20) -> dict:
    """Measure rank and inclusive alert policy with stable ID ties."""
    scores = np.asarray(scores, dtype=np.float64)
    labels = np.asarray(labels)
    if (not ids or len(ids) != len(scores) or len(ids) != len(labels)
            or len(set(ids)) != len(ids) or k < 1
            or not np.isfinite(scores).all() or np.any((scores < 0) | (scores > 1))
            or not set(labels.tolist()) <= {0, 1} or len(set(labels.tolist())) < 2):
        raise ValueError('invalid validation result')
    order = sorted(range(len(ids)), key=lambda i: (-float(scores[i]), ids[i]))
    top = order[:min(k, len(order))]
    hits = int(sum(labels[i] for i in top))
    positives = int(labels.sum())
    highest = float(scores[order[0]])
    boundary = float(scores[top[-1]])
    above = int(np.count_nonzero(scores > boundary))
    equal = scores == boundary
    threshold = select_threshold(scores, labels, max_alerts=k)
    alerted = scores >= threshold['threshold'] if threshold['threshold'] != 'no_alert' \
        else np.zeros(len(scores), dtype=bool)
    return {'ap': float(average_precision_score(labels, scores)),
            'positive_top_20': hits, 'precision_at_20': hits / len(top),
            'recall_at_20': hits / positives,
            'highest_score': highest,
            'highest_score_rows': int(np.count_nonzero(scores == highest)),
            'rank_20_tie': {'score': boundary, 'rows_above': above,
                            'rows_in_group': int(np.count_nonzero(equal)),
                            'positives_in_group': int(labels[equal].sum()),
                            'crosses_boundary': above + int(np.count_nonzero(equal))
                            > len(top)},
            'threshold': threshold, 'alerts': int(np.count_nonzero(alerted)),
            'positive_alerts': int(labels[alerted].sum())}


def run(store: Path, protocol_path: Path, artifact_dir: Path | None = None) -> dict:
    start = time.monotonic()
    protocol_raw = protocol_path.read_bytes()
    protocol = json.loads(protocol_raw)
    if (protocol['feature_inputs'] != list(FEATURES)
            or protocol['fit_budget']['train_reduction'] != 'sha256_id_mod_4_equals_0'
            or not protocol['eligibility']['eligible']):
        raise ValueError('unsupported frozen protocol')
    source = verify_source(store, protocol)
    train_x, train_y, validation_x, validation_y, ids, rules = _load_development(
        store, protocol)
    if (len(train_y) != 693230 or int(train_y.sum()) != 719
            or len(validation_y) != 594715 or int(validation_y.sum()) != 588
            or len(ids) != 594715):
        raise ValueError('frozen development class counts mismatch')
    tree_result = fit_candidate_grid(
        train_x, train_y, validation_x, validation_y, ids,
        numeric_columns=tuple(range(len(NUMERIC))),
        categorical_columns=tuple(range(len(NUMERIC), len(FEATURES))),
        candidates=(('decision_tree', 5, 500),))[0]
    if tree_result['status'] != 'complete':
        raise ValueError(f"tree refit failed: {tree_result['failure_type']}")
    tree = summarize(ids, tree_result['validation_scores'], validation_y)
    rule = summarize(ids, rules, validation_y)
    if (tree['positive_top_20'] != 0 or rule['positive_top_20'] != 0
            or abs(tree['ap'] - 0.0143070042) > 1e-8
            or abs(rule['ap'] - 0.0007610525) > 1e-8):
        raise ValueError('reference validation mismatch; investigate before boosting')
    frozen = load_trusted_artifact(
        Path('artifacts/feature-002-history-v1-20261114'),
        expected_manifest_sha256=FROZEN_MANIFEST_SHA,
        expected_dataset_version=protocol['dataset_version'],
        expected_protocol_sha256=hashlib.sha256(protocol_raw).hexdigest())
    frozen_scores = frozen.pipeline.predict_proba(validation_x)[:, 1]
    tree_max_abs_diff = float(np.max(np.abs(
        frozen_scores - tree_result['validation_scores'])))
    if not math.isfinite(tree_max_abs_diff) or tree_max_abs_diff > 1e-8:
        raise ValueError('tree refit differs from frozen model')
    boost_start = time.monotonic()
    boosted_pipeline, boosted_scores = fit_boosted(
        train_x, train_y, validation_x,
        numeric_columns=tuple(range(len(NUMERIC))),
        categorical_columns=tuple(range(len(NUMERIC), len(FEATURES))))
    boosted = summarize(ids, boosted_scores, validation_y)
    artifact = None
    if artifact_dir is not None:
        artifact_dir = artifact_dir.resolve()
        artifact_dir.mkdir(parents=True, exist_ok=False)
        model_path = artifact_dir / 'model.joblib'
        scores_path = artifact_dir / 'validation_scores.npy'
        joblib.dump(boosted_pipeline, model_path)
        np.save(scores_path, boosted_scores, allow_pickle=False)
        metadata = {
            'status': 'frozen_development_only', 'scorer_version': BOOSTED_VERSION,
            'model_kind': 'hist_gradient_boosting_research_candidate',
            'model_file': 'model.joblib', 'model_sha256': _sha(model_path),
            'validation_scores_sha256': _sha(scores_path),
            'protocol_sha256': hashlib.sha256(protocol_raw).hexdigest(),
            'dataset_version': protocol['dataset_version'],
            'feature_version': 'history-v1', 'ordered_features': list(FEATURES),
            'numeric_features': list(NUMERIC),
            'categorical_features': list(FEATURES[len(NUMERIC):]),
            'dependencies': {'numpy': np.__version__,
                             'scikit_learn': __import__('sklearn').__version__,
                             'joblib': joblib.__version__},
            'winner_index': 'exploratory_boosted_only',
            'model_validation_threshold': boosted['threshold'],
            'rules_validation_threshold': rule['threshold'],
            'calibration': 'none', 'test_predictions': 'not_generated',
            'test_labels': 'not_read', 'validation_ids_sha256':
            source['validation_ids_sha256'], 'validation_rows': len(ids),
            'validation_positive_top_20': boosted['positive_top_20'],
            'validation_positive_alerts': boosted['positive_alerts'],
            'validation_ap': boosted['ap'],
        }
        (artifact_dir / 'metadata.json').write_text(
            json.dumps(metadata, sort_keys=True, indent=2) + '\n')
        manifest_sha = create_manifest(artifact_dir, protocol_path)
        artifact = {'directory': str(artifact_dir), 'manifest_sha256': manifest_sha,
                    'model_sha256': metadata['model_sha256'],
                    'metadata_sha256': _sha(artifact_dir / 'metadata.json'),
                    'validation_scores_sha256': metadata['validation_scores_sha256']}
    return {'status': 'exploratory_validation_only',
            'protocol_sha256': hashlib.sha256(protocol_raw).hexdigest(),
            'source': source, 'train_rows': len(train_y),
            'train_positives': int(train_y.sum()),
            'validation_rows': len(validation_y),
            'validation_positives': int(validation_y.sum()),
            'validation_prevalence': float(validation_y.mean()),
            'ordered_features': FEATURES,
            'boosted_parameters': {'max_iter': 150, 'max_leaf_nodes': 15,
                                   'min_samples_leaf': 100, 'learning_rate': 0.1,
                                   'class_weight': 'balanced',
                                   'early_stopping': False, 'seed': 42,
                                   'max_threads': 2},
            'tree_refit_max_abs_diff_from_frozen': tree_max_abs_diff,
            'scorers': {'rules': rule, 'tree_refit': tree, 'boosted': boosted},
            'artifact': artifact,
            'boost_fit_and_validation_seconds': time.monotonic() - boost_start,
            'elapsed_seconds': time.monotonic() - start,
            'peak_rss_bytes': peak_rss_bytes()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--artifact-dir', type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(run(args.store, args.protocol, args.artifact_dir), sort_keys=True))


if __name__ == '__main__':
    main()
