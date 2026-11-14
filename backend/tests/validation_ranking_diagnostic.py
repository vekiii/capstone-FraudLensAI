"""Read-only frozen-validation ranking diagnostic; never queries test rows."""

import argparse
import hashlib
import json
import math
import sqlite3
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path

import numpy as np
from sklearn.metrics import average_precision_score

from fraudlens.evaluation import select_threshold
from fraudlens.model_scoring import load_trusted_artifact
from fraudlens.train_phase5 import CATEGORICAL, FEATURES, NUMERIC, _rules


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source(path: Path):
    connection = sqlite3.connect(f'{path.resolve().as_uri()}?mode=ro', uri=True)
    connection.execute('PRAGMA query_only=ON')
    return connection


def _ratio(values):
    """Exact current-to-prior mean ratio from strict-past same-currency facts."""
    count = values['sender_paid_count_same_currency_24h']
    paid = values['current_paid_amount']
    prior = values['sender_paid_sum_same_currency_24h']
    if count is None or count < 3 or paid is None or prior is None:
        return None
    try:
        current_amount = Decimal(str(paid))
        prior_sum = Decimal(str(prior))
    except InvalidOperation as exc:
        raise ValueError('invalid paid amount or prior sum') from exc
    if not current_amount.is_finite() or not prior_sum.is_finite():
        raise ValueError('nonfinite paid amount or prior sum')
    if prior_sum <= 0:
        return None
    if current_amount < 0:
        raise ValueError('negative paid amount')
    return Fraction(current_amount) * count / Fraction(prior_sum)


def _queue_order(ids, scores, ratios):
    if (len(ids) != len(scores) or len(ids) != len(ratios)
            or len(set(ids)) != len(ids)
            or any(not math.isfinite(float(score)) for score in scores)):
        raise ValueError('queue input mismatch')
    return sorted(range(len(ids)), key=lambda i: (
        -float(scores[i]), ratios[i] is None,
        -ratios[i] if ratios[i] is not None else Fraction(0), ids[i]))


def _measure(ids, scores, labels):
    ordered = sorted(range(len(ids)), key=lambda i: (-scores[i], ids[i]))
    highest = scores[ordered[0]]
    capacity = min(20, len(ordered))
    at_20 = scores[ordered[capacity - 1]]
    above = sum(score > at_20 for score in scores)
    group = [i for i, score in enumerate(scores) if score == at_20]
    selected = ordered[above:capacity]
    eligible = select_threshold(scores, labels, max_alerts=20)
    return {
        'ap': float(average_precision_score(labels, scores)),
        'positive_top_20': sum(labels[i] for i in ordered[:20]),
        'positive_top_50': sum(labels[i] for i in ordered[:50]),
        'positive_top_100': sum(labels[i] for i in ordered[:100]),
        'highest_score': highest,
        'highest_score_rows': sum(score == highest for score in scores),
        'rank_20_tie': {
            'score': at_20, 'rows_above': above, 'rows_in_group': len(group),
            'positives_in_group': sum(labels[i] for i in group),
            'group_rows_selected_top_20': len(selected),
            'group_positives_selected_top_20': sum(labels[i] for i in selected),
            'crosses_boundary': above + len(group) > capacity,
        },
        'top_inclusive_threshold_alerts': sum(score == highest for score in scores),
        'feasible_threshold_1_to_20': eligible['alerts'] > 0,
        'best_feasible_threshold': eligible if eligible['alerts'] > 0 else None,
        'selected_threshold': eligible,
    }


def run(store: Path, protocol_path: Path, artifact_dir: Path, manifest_sha: str,
        selection_output: Path | None = None):
    protocol_bytes = protocol_path.read_bytes()
    protocol_sha = hashlib.sha256(protocol_bytes).hexdigest()
    protocol = json.loads(protocol_bytes)
    metadata_path = artifact_dir / 'metadata.json'
    metadata = json.loads(metadata_path.read_text())
    artifact = load_trusted_artifact(
        artifact_dir, expected_manifest_sha256=manifest_sha,
        expected_dataset_version=protocol['dataset_version'],
        expected_protocol_sha256=protocol_sha)
    if (protocol['feature_inputs'] != list(FEATURES)
            or artifact.manifest['ordered_features'] != list(FEATURES)
            or artifact.manifest['winner_index'] != 5
            or metadata['model_validation_threshold']['threshold'] != 'no_alert'
            or metadata['rules_validation_threshold']['threshold'] != 'no_alert'):
        raise ValueError('frozen candidate, feature or threshold mismatch')
    split = protocol['split']
    expected = split['partitions']['validation']
    ids = []
    model_scores = []
    rule_scores = []
    ratios = []
    digest = hashlib.sha256()
    connection = _source(store)
    try:
        version = protocol['dataset_version']
        identity = connection.execute('''
            SELECT status,source_sha256,mapping_sha256,time_policy_sha256
            FROM dataset_versions WHERE id=?''', (version,)).fetchone()
        if identity != ('complete', protocol['source_sha256'],
                        protocol['mapping_sha256'], protocol['time_policy_sha256']):
            raise ValueError('source identity mismatch')
        if connection.execute('''SELECT status FROM feature_builds WHERE version=?
            AND feature_version='history-v1' ''', (version,)).fetchone() != ('complete',):
            raise ValueError('feature build incomplete')
        cursor = connection.execute('''
            SELECT transaction_id,payload_json FROM feature_snapshots
            WHERE version=? AND feature_version='history-v1' AND scoreable=1
              AND event_time>? AND event_time<=?
            ORDER BY event_time,transaction_id''',
            (version, split['train_end_inclusive'],
             split['validation_end_inclusive']))
        while rows := cursor.fetchmany(10000):
            matrix = np.empty((len(rows), len(FEATURES)), dtype=object)
            for row_index, (event_id, payload) in enumerate(rows):
                values = json.loads(payload)
                ids.append(event_id)
                digest.update((event_id + '\n').encode('ascii'))
                if selection_output is not None:
                    ratios.append(_ratio(values))
                for column, key in enumerate(NUMERIC):
                    matrix[row_index, column] = (float(values[key])
                                                 if values[key] is not None else np.nan)
                for column, key in enumerate(CATEGORICAL, len(NUMERIC)):
                    matrix[row_index, column] = (values[key] if values[key] is not None
                                                 else '__missing__')
                rule_scores.append(_rules(values))
            model_scores.extend(float(value) for value in
                                artifact.pipeline.predict_proba(matrix)[:, 1])
        if len(ids) != expected['count'] or digest.hexdigest() != expected['ids_sha256']:
            raise ValueError('validation membership mismatch')
        selections = None
        if selection_output is not None:
            if selection_output.exists():
                raise ValueError('selection output already exists')
            selections = {}
            for name, scores in (('tree', model_scores), ('rules', rule_scores)):
                old = sorted(range(len(ids)), key=lambda i: (-scores[i], ids[i]))[:20]
                new = _queue_order(ids, scores, ratios)[:20]
                for order_name, indices in (('old_id', old), ('new_ratio', new)):
                    selections[f'{name}_{order_name}'] = {
                        'selected_ids': [ids[i] for i in indices],
                        'ratio_available_selected': sum(ratios[i] is not None
                                                        for i in indices),
                    }
            selection_output.parent.mkdir(parents=True, exist_ok=True)
            with selection_output.open('x') as stream:
                json.dump({'scope': 'validation_only_before_label_join',
                           'protocol_sha256': protocol_sha,
                           'validation_ids_sha256': digest.hexdigest(),
                           'rule': 'score_desc_then_available_exact_ratio_desc_then_id_asc',
                           'selections': selections}, stream, indent=2)
                stream.write('\n')
        # Labels enter only after all model and rule scores and membership are fixed.
        label_cursor = connection.execute('''
            SELECT s.transaction_id,l.status,l.value FROM feature_snapshots AS s
            JOIN private_evaluation_labels AS l
              ON l.version=s.version AND l.transaction_id=s.transaction_id
            WHERE s.version=? AND s.feature_version='history-v1' AND s.scoreable=1
              AND s.event_time>? AND s.event_time<=?
            ORDER BY s.event_time,s.transaction_id''',
            (version, split['train_end_inclusive'],
             split['validation_end_inclusive']))
        labels = []
        for index, (event_id, status, value) in enumerate(label_cursor):
            if (index >= len(ids) or event_id != ids[index]
                    or status not in {'eligible_positive', 'eligible_negative'}
                    or value not in (0, 1)):
                raise ValueError('validation label identity mismatch')
            labels.append(value)
        if len(labels) != len(ids) or sum(labels) != expected['positives']:
            raise ValueError('validation label count mismatch')
    finally:
        connection.close()
    measured = {'tree_depth_5_leaf_500': _measure(ids, model_scores, labels),
                'rules_R1_R3': _measure(ids, rule_scores, labels)}
    if abs(measured['tree_depth_5_leaf_500']['ap'] -
           metadata['candidate_outcomes'][5]['validation_ap']) > 1e-8:
        raise ValueError('selected model AP does not reproduce saved validation')
    if (measured['tree_depth_5_leaf_500']['selected_threshold'] !=
            metadata['model_validation_threshold']
            or measured['rules_R1_R3']['selected_threshold'] !=
            metadata['rules_validation_threshold']):
        raise ValueError('frozen threshold does not reproduce')
    queue_metrics = None
    if selections is not None:
        by_id = dict(zip(ids, labels, strict=True))
        queue_metrics = {}
        for name, selection in selections.items():
            chosen = selection['selected_ids']
            positives = sum(by_id[event_id] for event_id in chosen)
            queue_metrics[name] = {
                'selected': len(chosen), 'positives': positives,
                'precision_at_20': positives / len(chosen),
                'recall_at_20': positives / sum(labels),
                'ratio_available_selected': selection['ratio_available_selected'],
                'selected_ids': chosen,
            }
        if (queue_metrics['tree_old_id']['positives'] != 0
                or queue_metrics['rules_old_id']['positives'] != 0):
            raise ValueError('old ID order does not reproduce frozen diagnostic')
    unavailable = [{
        'index': index, 'candidate': protocol['candidates'][index],
        'saved_validation_ap': metadata['candidate_outcomes'][index]['validation_ap'],
        'status': 'unavailable_no_predictions_or_artifact',
    } for index in range(len(protocol['candidates'])) if index != 5]
    return {
        'scope': 'frozen_validation_only', 'source_mode': 'sqlite_read_only',
        'protocol_sha256': protocol_sha, 'manifest_sha256': manifest_sha,
        'metadata_sha256': _sha(metadata_path),
        'model_sha256': artifact.manifest['model_sha256'],
        'validation_ids_sha256': digest.hexdigest(), 'rows': len(ids),
        'positives': sum(labels), 'prevalence': sum(labels) / len(labels),
        'tie_order': 'descending_score_then_ascending_transaction_id',
        'scorers': measured, 'unavailable_candidates': unavailable,
        'review_queue': queue_metrics,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--store', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--artifact-dir', type=Path, required=True)
    parser.add_argument('--manifest-sha', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--selection-output', type=Path)
    args = parser.parse_args()
    if args.selection_output == args.output or args.output.exists():
        raise ValueError('diagnostic output path already exists or overlaps selection')
    result = run(args.store, args.protocol, args.artifact_dir, args.manifest_sha,
                 args.selection_output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'output': str(args.output), 'rows': result['rows'],
                      'positives': result['positives'],
                      'scorers': result['scorers'],
                      'review_queue': result['review_queue']}, separators=(',', ':')))


if __name__ == '__main__':
    main()
