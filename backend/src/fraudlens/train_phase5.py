"""Local T031/T032 history-v1 fitting; never reads test labels or notebook artifacts."""

import argparse
import hashlib
import json
import resource
import sqlite3
import time
from decimal import Decimal
from pathlib import Path

import joblib
import numpy as np
import sklearn

from fraudlens.evaluation import fit_candidate_grid, select_candidate, select_threshold

NUMERIC = (
    'sender_out_count_24h', 'sender_distinct_receivers_24h',
    'sender_paid_count_same_currency_24h', 'sender_paid_sum_same_currency_24h',
    'receiver_in_count_24h', 'receiver_distinct_senders_24h',
    'receiver_received_count_same_currency_24h',
    'receiver_received_sum_same_currency_24h', 'current_paid_amount',
)
CATEGORICAL = ('current_paid_currency', 'current_payment_format')
FEATURES = NUMERIC + CATEGORICAL


def _sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _rules(values):
    score = Decimal(0)
    if values['sender_out_count_24h'] >= 3:
        score += Decimal('0.35')
    if values['receiver_in_count_24h'] >= 3:
        score += Decimal('0.30')
    count = values['sender_paid_count_same_currency_24h']
    if (count >= 3 and Decimal(values['current_paid_amount']) * count
            >= 2 * Decimal(values['sender_paid_sum_same_currency_24h'])):
        score += Decimal('0.35')
    return float(score)


def _load_development(store, protocol):
    parts = protocol['split']['partitions']
    train_n = parts['train']['count']
    validation_n = parts['validation']['count']
    total = train_n + validation_n
    x = np.empty((total, len(FEATURES)), dtype=object)
    y = np.empty(total, dtype=np.int8)
    validation_ids = []
    rule_scores = np.empty(validation_n, dtype=np.float64)
    connection = sqlite3.connect(f'{store.resolve().as_uri()}?mode=ro', uri=True)
    connection.execute('PRAGMA query_only=ON')
    connection.execute('PRAGMA temp_store=FILE')
    try:
        cursor = connection.execute('''
            SELECT s.transaction_id,s.event_time,s.payload_json,l.status,l.value
            FROM feature_snapshots AS s
            JOIN private_evaluation_labels AS l
              ON l.version=s.version AND l.transaction_id=s.transaction_id
            WHERE s.version=? AND s.feature_version='history-v1'
              AND s.scoreable=1 AND s.event_time<=?
            ORDER BY s.event_time,s.transaction_id
        ''', (protocol['dataset_version'],
              protocol['split']['validation_end_inclusive']))
        positives = [0, 0]
        for i, (event_id, at, payload, status, label) in enumerate(cursor):
            if i >= total or status not in {'eligible_positive', 'eligible_negative'}:
                raise ValueError('development row/label population mismatch')
            role_index = int(at > protocol['split']['train_end_inclusive'])
            if role_index != int(i >= train_n) or label not in (0, 1):
                raise ValueError('chronological membership or label mismatch')
            values = json.loads(payload)
            for j, key in enumerate(NUMERIC):
                x[i, j] = float(values[key]) if values[key] is not None else np.nan
            for j, key in enumerate(CATEGORICAL, len(NUMERIC)):
                x[i, j] = values[key] if values[key] is not None else '__missing__'
            y[i] = label
            positives[role_index] += label
            if role_index:
                validation_ids.append(event_id)
                rule_scores[i - train_n] = _rules(values)
        if i + 1 != total or positives != [parts['train']['positives'],
                                           parts['validation']['positives']]:
            raise ValueError('development counts mismatch')
    finally:
        connection.close()
    reduction = protocol['fit_budget']['train_reduction']
    if reduction == 'sha256_id_mod_4_equals_0':
        # Re-read only train IDs; the selection is label-free and history stays full.
        selected = []
        connection = sqlite3.connect(f'{store.resolve().as_uri()}?mode=ro', uri=True)
        connection.execute('PRAGMA query_only=ON')
        try:
            cursor = connection.execute('''
                SELECT transaction_id FROM feature_snapshots
                WHERE version=? AND feature_version='history-v1' AND scoreable=1
                  AND event_time<=? ORDER BY event_time,transaction_id
            ''', (protocol['dataset_version'],
                  protocol['split']['train_end_inclusive']))
            for index, (event_id,) in enumerate(cursor):
                if int.from_bytes(hashlib.sha256(event_id.encode('ascii')).digest()[:8],
                                  'big') % 4 == 0:
                    selected.append(index)
        finally:
            connection.close()
        if not selected or len(set(y[selected])) < 2:
            raise ValueError('reduced training view ineligible')
        return x[selected], y[selected], x[train_n:], y[train_n:], \
            tuple(validation_ids), rule_scores
    if reduction != 'none_full_train':
        raise ValueError('unapproved training reduction')
    return x[:train_n], y[:train_n], x[train_n:], y[train_n:], \
        tuple(validation_ids), rule_scores


def train(store: Path, protocol_path: Path, output: Path):
    protocol_bytes = protocol_path.read_bytes()
    protocol = json.loads(protocol_bytes)
    if (not protocol['eligibility']['eligible']
            or protocol['fit_budget']['train_reduction'] not in
            {'none_full_train', 'sha256_id_mod_4_equals_0'}
            or protocol['holdout']['first_scientific_disclosure']
            != 'T062_after_artifact_and_explanation_checks'):
        raise ValueError('unsupported or ineligible frozen protocol')
    start = time.monotonic()
    train_x, train_y, validation_x, validation_y, validation_ids, rule_scores = \
        _load_development(store, protocol)
    print(json.dumps({'stage': 'development_loaded', 'train': len(train_y),
                      'validation': len(validation_y),
                      'peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}),
          flush=True)
    candidates = []
    outcomes = []
    for index, candidate in enumerate(protocol['candidates']):
        spec = ((('logistic_l2', candidate['C']) if candidate['kind'] == 'logistic_l2'
                 else ('decision_tree', candidate['max_depth'],
                       candidate['min_samples_leaf'])),)
        fit_start = time.monotonic()
        result = fit_candidate_grid(
            train_x, train_y, validation_x, validation_y, validation_ids,
            numeric_columns=tuple(range(len(NUMERIC))),
            categorical_columns=tuple(range(len(NUMERIC), len(FEATURES))),
            candidates=spec)[0]
        elapsed = time.monotonic() - fit_start
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        print(json.dumps({'stage': 'fit_resource_measurement', 'index': index,
                          'elapsed_seconds': round(elapsed, 3),
                          'peak_rss_bytes': rss}), flush=True)
        if (elapsed > protocol['fit_budget']['max_fit_seconds_each']
                or time.monotonic() - start > protocol['fit_budget']['max_total_fit_seconds']
                or rss > protocol['fit_budget']['max_process_peak_bytes']):
            raise RuntimeError('frozen fit resource ceiling exceeded')
        candidates.append(result)
        if result['status'] == 'failed':
            outcomes.append({'index': index, 'candidate': candidate,
                             'status': 'failed', 'failure_type': result['failure_type'],
                             'fit_and_validation_seconds': round(elapsed, 3),
                             'peak_rss_bytes': rss})
            print(json.dumps({'stage': 'fit_failed', **outcomes[-1]}), flush=True)
            continue
        outcomes.append({'index': index, 'candidate': candidate,
                         'status': 'complete',
                         'validation_ap': result['ap'],
                         'validation_precision_at_20': result['precision_at_k'],
                         'fit_and_validation_seconds': round(elapsed, 3),
                         'peak_rss_bytes': rss})
        print(json.dumps({'stage': 'fit_complete', **outcomes[-1]}), flush=True)
    winner = select_candidate(candidates, ap_tolerance=protocol['ap_tie_tolerance'])
    model_threshold = select_threshold(candidates[winner]['validation_scores'],
                                       validation_y, max_alerts=20)
    rule_threshold = select_threshold(rule_scores, validation_y, max_alerts=20)
    output.mkdir(parents=True, exist_ok=False)
    model_path = output / 'model.joblib'
    joblib.dump(candidates[winner]['pipeline'], model_path)
    reloaded = joblib.load(model_path)  # Local, just-created file; T038 adds trusted loading.
    probe_count = min(5, len(validation_y))
    original = candidates[winner]['validation_scores'][:probe_count]
    repeated = reloaded.predict_proba(validation_x[:probe_count])[:, 1]
    if not np.allclose(original, repeated, atol=1e-12, rtol=0):
        raise RuntimeError('reloaded prediction mismatch')
    report = {
        'status': 'frozen_development_only', 'protocol_sha256': hashlib.sha256(
            protocol_bytes).hexdigest(), 'dataset_version': protocol['dataset_version'],
        'feature_version': protocol['feature_version'], 'ordered_features': FEATURES,
        'numeric_features': NUMERIC, 'categorical_features': CATEGORICAL,
        'dependencies': {'numpy': np.__version__, 'scikit_learn': sklearn.__version__,
                         'joblib': joblib.__version__},
        'candidate_outcomes': outcomes, 'winner_index': winner,
        'model_validation_threshold': model_threshold,
        'rules_validation_threshold': rule_threshold,
        'calibration': 'none', 'test_predictions': 'not_generated',
        'test_labels': 'not_read', 'model_file': 'model.joblib',
        'model_sha256': _sha(model_path), 'reload_probe_count': probe_count,
        'reload_probe_predictions': repeated.tolist(),
        'peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'total_seconds': round(time.monotonic() - start, 3),
    }
    (output / 'metadata.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--store', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(train(args.store, args.protocol, args.out)), flush=True)


if __name__ == '__main__':
    main()
