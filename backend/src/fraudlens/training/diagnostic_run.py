"""Separate, exact-hash five-arm FR-021 numerical diagnostic; train/validation only."""

import argparse
import hashlib
import json
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

import lightgbm as lgb
import numpy as np
import sklearn
from sklearn.metrics import average_precision_score, roc_auc_score

from fraudlens.data.features import FEATURE_ORDER, FEATURE_VERSION
from fraudlens.data.manifest import canonical_json_bytes, sha256_file
from fraudlens.training import local_run
from fraudlens.training.evaluation import evaluate_validation
from fraudlens.training.protocol import verify_research_protocol
from fraudlens.training.resource_guard import supervise_command

_FORMAT = 'fraudlens-fr021-numeric-diagnostic-v1'
_PARENT_FORMAT = 'fraudlens-fr021-training-protocol-v2'
_SOURCE_SHA = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'
_FEATURES = 'data/processed/t219-ibm-day-60-20-20-v1'
_LABELS = 'data/processed/t219-ibm-day-60-20-20-labels-v1'
_PRIOR_OUTPUT = 'data/eval/ibm-day-lightgbm-macos-preflight-schema-review-002'
_PARENT_SHA = '1ebac4f24aa198cfd1de70b96204676cb3fbd0cc07786296944c6ade0214f6be'
_ARM_PLAN = (
    ('control', {}),
    ('unweighted', {'scale_pos_weight': 1.0}),
    ('no_average', {'boost_from_average': False}),
    ('l2_one', {'reg_lambda': 1.0}),
    ('delta_one', {'max_delta_step': 1.0}),
)


def arm_plan() -> list[dict[str, Any]]:
    """Exact order and sole change in each diagnostic arm."""
    return [{'name': name, 'overrides': dict(changes)} for name, changes in _ARM_PLAN]


def verify_arm_plan(value: object) -> None:
    if value != arm_plan():
        raise ValueError('five-arm plan differs from the reviewed diagnostic design')


def arm_parameters(train_negative: int, train_positive: int) -> tuple[tuple[str, dict[str, Any]], ...]:
    if train_negative < 1 or train_positive < 1:
        raise ValueError('train must contain both classes')
    base = {
        'objective': 'binary', 'boosting_type': 'gbdt',
        'metric': 'binary_logloss', 'n_estimators': 1000,
        'num_leaves': 31, 'learning_rate': 0.05, 'min_child_samples': 200,
        'scale_pos_weight': train_negative / train_positive,
        'boost_from_average': True, 'reg_lambda': 0.0, 'max_delta_step': 0.0,
        'random_state': 42, 'n_jobs': 4, 'device_type': 'cpu',
        'deterministic': True, 'force_col_wise': True, 'verbosity': -1,
    }
    return tuple((name, {**base, **changes}) for name, changes in _ARM_PLAN)


def _digest(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError(f'{path} must be a JSON object')
    return value


def verify_diagnostic_protocol(
    path: Path, digest: str, parent_path: Path, root: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Fail closed on plan, lineage, runtime, code, input, or ceiling drift."""
    protocol = _read_json(path)
    if (_digest(protocol) != digest or protocol.get('format') != _FORMAT
            or protocol.get('status') != 'pending_human_review'):
        raise ValueError('diagnostic protocol format or canonical digest mismatch')
    verify_arm_plan(protocol.get('arms'))
    if (protocol.get('comparison_rules') != {
        'control_reproduction': True,
        'compare_extreme_raw_margins_and_saturation': True,
        'compare_validation_metrics_and_alert_counts': True,
        'automatic_application_winner': False,
    } or protocol.get('n_jobs') != 4
            or protocol.get('data_scope') != 'train_validation_only'
            or protocol.get('validation_already_used_for_selection_and_diagnosis') is not True):
        raise ValueError('diagnostic analysis or thread contract mismatch')
    parent = _read_json(parent_path)
    if (_digest(parent) != _PARENT_SHA or parent.get('format') != _PARENT_FORMAT
            or protocol.get('parent_protocol_canonical_sha256') != _PARENT_SHA
            or protocol.get('parent_protocol_file_sha256') != sha256_file(parent_path)
            or protocol.get('resource_ceilings') != parent.get('resource_ceilings', {}).get('fit')
            or protocol.get('source_sha256') != _SOURCE_SHA
            or parent.get('dataset_sha256') != _SOURCE_SHA):
        raise ValueError('diagnostic parent, source or resource ceiling mismatch')
    if (protocol.get('feature_manifest_sha256') != parent.get('research_feature_manifest_sha256')
            or protocol.get('label_manifest_sha256') != parent.get('research_label_manifest_sha256')
            or parent.get('feature_version') != FEATURE_VERSION
            or parent.get('feature_order') != list(FEATURE_ORDER)):
        raise ValueError('diagnostic feature or label identity mismatch')
    train_counts = parent.get('class_distribution', {}).get('train', {})
    negative, positive = train_counts.get('negative'), train_counts.get('positive')
    if (type(negative) is not int or type(positive) is not int
            or negative < 1 or positive < 1
            or protocol.get('train_class_counts') != {
                'negative': negative, 'positive': positive,
            }
            or protocol.get('control_scale_pos_weight') != negative / positive
            or protocol.get('control_parameters') != arm_parameters(negative, positive)[0][1]):
        raise ValueError('diagnostic control parameter contract mismatch')
    if (protocol.get('uv_lock_sha256') != sha256_file(root / 'uv.lock')
            or protocol.get('runtime') != {
                'python': sys.version.split()[0], 'lightgbm': lgb.__version__,
                'numpy': np.__version__, 'scikit_learn': sklearn.__version__,
            }):
        raise ValueError('diagnostic locked runtime mismatch')
    expected_code = protocol.get('implementation_file_sha256')
    required_code = {
        'backend/src/fraudlens/training/diagnostic_run.py',
        'backend/src/fraudlens/training/resource_guard.py',
        'backend/src/fraudlens/training/local_run.py',
        'backend/src/fraudlens/training/evaluation.py',
        'backend/src/fraudlens/training/protocol.py',
        'backend/src/fraudlens/training/candidates.py',
        'backend/src/fraudlens/training/boundaries.py',
        'backend/src/fraudlens/data/features.py',
        'backend/src/fraudlens/data/manifest.py',
        'backend/src/fraudlens/scoring/artifacts.py',
    }
    if (not isinstance(expected_code, dict) or set(expected_code) != required_code
            or any(sha256_file(root / name) != expected_code[name] for name in required_code)):
        raise ValueError('diagnostic executable code hash mismatch')
    prior = protocol.get('prior_experiment')
    if (not isinstance(prior, dict) or prior.get('path') != _PRIOR_OUTPUT
            or prior.get('experiment_sha256') != sha256_file(root / _PRIOR_OUTPUT / 'experiment.json')
            or prior.get('selected_model_sha256') != sha256_file(
                root / _PRIOR_OUTPUT / 'artifacts/selected-lightgbm/model.txt'
            )):
        raise ValueError('diagnostic prior experiment identity mismatch')
    previous = _read_json(root / _PRIOR_OUTPUT / 'experiment.json')
    if (previous.get('protocol_sha256') != _PARENT_SHA
            or previous.get('selected_candidate', {}).get('candidate_index') != 1
            or previous['selected_candidate'].get('num_leaves') != 31
            or previous['selected_candidate'].get('learning_rate') != 0.05
            or previous['selected_candidate'].get('min_child_samples') != 200
            or prior.get('selected_manifest_sha256') != previous.get('artifact_manifest_sha256')
            or prior.get('sealed_test_prediction_sha256')
            != previous.get('prediction_sha256', {}).get('test')):
        raise ValueError('diagnostic selected baseline mismatch')
    return protocol, parent


def _manifest(root: Path, expected_format: str, parts: set[str]) -> dict[str, Any]:
    manifest = _read_json(root / 'manifest.json')
    expected_keys = (local_run._FEATURE_MANIFEST_KEYS if 'features-v1' in expected_format
                     else local_run._LABEL_MANIFEST_KEYS)
    if (manifest.get('format') != expected_format or set(manifest) != expected_keys
            or not isinstance(manifest.get('files'), dict)
            or set(manifest['files']) != parts):
        raise ValueError('transferred manifest schema mismatch')
    for part in ('train', 'validation'):
        if sha256_file(root / f'{part}.jsonl') != manifest['files'][part]:
            raise ValueError(f'{part} transferred file checksum mismatch')
    return manifest


def _prepare_inputs(args: argparse.Namespace):
    protocol, parent = verify_diagnostic_protocol(
        args.protocol, args.protocol_sha256, args.parent_protocol, args.root,
    )
    feature_root, label_root = args.features, args.labels
    if (feature_root.resolve() != (args.root / _FEATURES).resolve()
            or label_root.resolve() != (args.root / _LABELS).resolve()):
        raise ValueError('diagnostic input paths differ from frozen protocol')
    features = _manifest(feature_root, 'hi-small-ibm-day-60-20-20-features-v1',
                         {'train', 'validation', 'test'})
    labels = _manifest(label_root, 'hi-small-ibm-day-60-20-20-training-labels-v1',
                       {'train', 'validation'})
    feature_sha = sha256_file(feature_root / 'manifest.json')
    label_sha = sha256_file(label_root / 'manifest.json')
    if (feature_sha != protocol['feature_manifest_sha256']
            or label_sha != protocol['label_manifest_sha256']
            or protocol.get('partition_id_sha256') != {
                'train': features['partition_scoreable_id_sha256']['train'],
                'validation': features['partition_scoreable_id_sha256']['validation'],
            }
            or protocol.get('input_file_sha256') != {
                'feature_train': features['files']['train'],
                'feature_validation': features['files']['validation'],
                'label_train': labels['files']['train'],
                'label_validation': labels['files']['validation'],
            }):
        raise ValueError('diagnostic train/validation file hash mismatch')
    verify_research_protocol(parent, _PARENT_SHA, features, labels, feature_sha, label_sha)
    if (features.get('source_sha256') != _SOURCE_SHA
            or labels.get('source_sha256') != _SOURCE_SHA
            or labels.get('feature_manifest_sha256') != feature_sha):
        raise ValueError('diagnostic source or label linkage mismatch')
    vocab = local_run._discover_vocab(feature_root / 'train.jsonl')
    train, train_ids, _ = local_run._read_feature_file(
        feature_root / 'train.jsonl', vocab, features['counts']['train'],
    )
    validation, validation_ids, validation_times = local_run._read_feature_file(
        feature_root / 'validation.jsonl', vocab, features['counts']['validation'],
    )
    train_labels = local_run._read_labels(label_root, 'train', train_ids)
    validation_labels = local_run._read_labels(label_root, 'validation', validation_ids)
    positives = int(np.count_nonzero(train_labels))
    if not positives or positives == len(train_labels):
        raise ValueError('diagnostic train must contain both classes')
    if (protocol.get('train_class_counts') != {
        'positive': positives, 'negative': len(train_labels) - positives,
    } or protocol.get('control_scale_pos_weight')
            != (len(train_labels) - positives) / positives):
        raise ValueError('diagnostic control class-weight contract mismatch')
    if (not positives or positives == len(train_labels)
            or not np.count_nonzero(validation_labels)
            or positives != labels['counts']['train']['positive']
            or int(np.count_nonzero(validation_labels))
            != labels['counts']['validation']['positive']):
        raise ValueError('diagnostic class-count contract mismatch')
    return (protocol, train, train_labels, validation, validation_labels,
            validation_ids, validation_times, vocab)


def _peak_bytes() -> int:
    return int(local_run._peak_working_set() or 0)


def _tie_diagnostics(scores: np.ndarray, ids: list[str]) -> dict[str, Any]:
    values, counts = np.unique(scores, return_counts=True)
    ranked = sorted(range(len(scores)), key=lambda index: (-scores[index], ids[index]))
    boundaries = {}
    for k in (20, 50, 100):
        cutoff = float(scores[ranked[min(k, len(scores)) - 1]])
        boundaries[str(k)] = {
            'score': cutoff, 'group_size': int(np.count_nonzero(scores == cutoff)),
            'strictly_above': int(np.count_nonzero(scores > cutoff)),
        }
    return {
        'distinct_scores': len(values),
        'largest_tie': int(counts.max()),
        'top_score': float(values[-1]),
        'top_score_tie': int(counts[-1]),
        'top_k_boundaries': boundaries,
    }


def _leaf_diagnostics(model: lgb.LGBMClassifier) -> list[dict[str, Any]]:
    result = []
    for index, tree in enumerate(model.booster_.dump_model()['tree_info']):
        leaves = []

        def visit(node: dict[str, Any]) -> None:
            if 'leaf_value' in node:
                leaves.append(node)
            else:
                visit(node['left_child'])
                visit(node['right_child'])

        visit(tree['tree_structure'])
        minimum = min(leaves, key=lambda node: node['leaf_value'])
        maximum = max(leaves, key=lambda node: node['leaf_value'])
        result.append({
            'tree_index': index, 'leaf_count': len(leaves),
            'minimum': {key: minimum[key] for key in ('leaf_value', 'leaf_count', 'leaf_weight')},
            'maximum': {key: maximum[key] for key in ('leaf_value', 'leaf_count', 'leaf_weight')},
        })
    return result


def _write_json(path: Path, value: object) -> None:
    path.write_bytes(canonical_json_bytes(value) + b'\n')


def run_matrix_diagnostics(
    train: np.ndarray, train_labels: np.ndarray,
    validation: np.ndarray, validation_labels: np.ndarray,
    validation_ids: list[str], validation_times: list[datetime], output: Path,
) -> list[dict[str, Any]]:
    """Fit exactly five planned arms; caller supplies aligned train/validation arrays."""
    if (train.ndim != 2 or validation.ndim != 2 or train.shape[1] != validation.shape[1]
            or len(train) != len(train_labels) or len(validation) != len(validation_labels)
            or len(validation) != len(validation_ids) or len(validation) != len(validation_times)
            or not np.isfinite(train).all() or not np.isfinite(validation).all()
            or not np.isin(train_labels, (0, 1)).all()
            or not np.isin(validation_labels, (0, 1)).all()):
        raise ValueError('diagnostic matrices must be finite aligned binary train/validation')
    if (len(set(validation_ids)) != len(validation_ids)
            or any(not isinstance(identity, str) or not identity for identity in validation_ids)
            or any(not isinstance(instant, datetime) or instant.tzinfo is None
                   or instant.utcoffset() is None for instant in validation_times)):
        raise ValueError('diagnostic validation IDs or timestamps are invalid')
    positives = int(np.count_nonzero(train_labels))
    negatives = len(train_labels) - positives
    if not positives or not negatives or not np.count_nonzero(validation_labels):
        raise ValueError('diagnostic train and validation must contain positives')
    output.mkdir(parents=True, exist_ok=True)
    arm_root = output / 'arms'
    arm_root.mkdir()
    results = []
    for index, (name, params) in enumerate(arm_parameters(negatives, positives)):
        arm_dir = arm_root / name
        arm_dir.mkdir()
        marker = output / 'fit-progress.json'
        temporary = output / 'fit-progress.json.tmp'
        temporary.write_text(json.dumps({
            'candidate_index': index, 'arm': name, 'started_monotonic': time.monotonic(),
        }), encoding='utf-8')
        temporary.replace(marker)
        fit_started = time.monotonic()
        model = lgb.LGBMClassifier(**params)
        model.fit(
            train, train_labels, eval_set=[(validation, validation_labels)],
            eval_names=['validation'], eval_metric='binary_logloss',
            callbacks=[lgb.early_stopping(50, first_metric_only=True, verbose=False)],
        )
        fit_elapsed = time.monotonic() - fit_started
        marker.unlink()
        best = int(model.best_iteration_)
        history = model.evals_result_
        total = len(history.get('validation', {}).get('binary_logloss', []))
        if (best < 1 or total < best
                or not total):
            raise ValueError('diagnostic early-stopping history is incomplete')
        probability = model.predict_proba(validation, num_iteration=best)[:, 1]
        raw = model.booster_.predict(validation, raw_score=True, num_iteration=best,
                                     num_threads=4)
        if not np.isfinite(raw).all():
            raise ValueError('nonfinite diagnostic raw margin')
        metrics = asdict(evaluate_validation(
            validation_labels, probability, validation_ids, validation_times,
        ))
        raw_order = sorted(range(len(raw)), key=lambda row: (-raw[row], validation_ids[row]))
        raw_metrics = {
            'average_precision': float(average_precision_score(validation_labels, raw)),
            'roc_auc': float(roc_auc_score(validation_labels, raw))
            if len(np.unique(validation_labels)) == 2 else None,
            'precision_at': {str(k): sum(int(validation_labels[row]) for row in
                                        raw_order[:min(k, len(raw))]) / min(k, len(raw))
                             for k in (20, 50, 100)},
            'tie_diagnostics': _tie_diagnostics(raw, validation_ids),
        }
        model_bytes = model.booster_.model_to_string(num_iteration=-1).encode()
        (arm_dir / 'model.txt').write_bytes(model_bytes)
        local_run._write_scores(arm_dir / 'validation-probability.csv',
                                validation_ids, validation_times, probability)
        local_run._write_scores(arm_dir / 'validation-raw.csv',
                                validation_ids, validation_times, raw)
        result = {
            'arm': name, 'index': index, 'declared_parameters': params,
            'effective_sklearn_parameters': model.get_params(),
            'effective_native_parameters': model.booster_.params,
            'fit_options': {'sample_weight': None, 'class_weight': None,
                            'init_score': None, 'eval_sample_weight': None,
                            'eval_class_weight': None, 'metric': 'binary_logloss',
                            'early_stopping_rounds': 50, 'first_metric_only': True},
            'best_iteration': best, 'total_rounds': total,
            'exported_trees': int(model.booster_.num_trees()), 'history': history,
            'probability_metrics': metrics,
            'alert_count': sum(metrics['daily_alert_counts'].values()),
            'raw_diagnostics': raw_metrics,
            'saturation': {
                'raw_min': float(np.min(raw)), 'raw_max': float(np.max(raw)),
                'raw_quantiles': [float(value) for value in np.quantile(
                    raw, (0, 0.01, 0.5, 0.99, 1),
                )],
                'probability_exact_zero': int(np.count_nonzero(probability == 0)),
                'probability_exact_one': int(np.count_nonzero(probability == 1)),
                'probability_quantiles': [float(value) for value in np.quantile(
                    probability, (0, 0.01, 0.5, 0.99, 1),
                )],
                'probability_ties': _tie_diagnostics(probability, validation_ids),
                'raw_distinct_within_probability_one': int(len(np.unique(
                    raw[probability == 1],
                ))),
                'leaf_diagnostics': _leaf_diagnostics(model),
            },
            'fit_elapsed_seconds': round(fit_elapsed, 6),
            'worker_peak_bytes_cumulative_at_end': _peak_bytes(),
            'model_sha256': hashlib.sha256(model_bytes).hexdigest(),
            'probability_csv_sha256': sha256_file(arm_dir / 'validation-probability.csv'),
            'raw_csv_sha256': sha256_file(arm_dir / 'validation-raw.csv'),
            'score_semantics': 'uncalibrated_weighted_training_probabilities',
        }
        _write_json(arm_dir / 'result.json', result)
        results.append(result)
    return results


def run_diagnostic(args: argparse.Namespace) -> dict[str, Any]:
    started = time.monotonic()
    (protocol, train, train_labels, validation, validation_labels,
     ids, times, vocab) = _prepare_inputs(args)
    results = run_matrix_diagnostics(train, train_labels, validation, validation_labels,
                                     ids, times, args.output)
    report = {
        'kind': _FORMAT, 'protocol_sha256': args.protocol_sha256,
        'parent_protocol_sha256': _PARENT_SHA,
        'source_sha256': _SOURCE_SHA,
        'feature_manifest_sha256': protocol['feature_manifest_sha256'],
        'label_manifest_sha256': protocol['label_manifest_sha256'],
        'train_count': len(train), 'validation_count': len(validation),
        'train_positive_count': int(np.count_nonzero(train_labels)),
        'validation_positive_count': int(np.count_nonzero(validation_labels)),
        'vocabulary_sizes': {key: len(value) for key, value in vocab.items()},
        'arms': [{'name': result['arm'],
                  'result_sha256': sha256_file(args.output / 'arms' / result['arm'] / 'result.json'),
                  'model_sha256': result['model_sha256'],
                  'best_iteration': result['best_iteration'],
                  'total_rounds': result['total_rounds'],
                  'fit_elapsed_seconds': result['fit_elapsed_seconds']}
                 for result in results],
        'comparison_rules': protocol['comparison_rules'],
        'test_features_parsed': False, 'test_labels_read': False,
        'test_predictions_written': False,
        'validation_is_not_independent_generalization_evidence': True,
        'elapsed_seconds': round(time.monotonic() - started, 3),
        'worker_peak_bytes_cumulative': _peak_bytes(),
        'git_head': subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=args.root,
                                   check=True, capture_output=True, text=True).stdout.strip(),
    }
    previous = _read_json(args.root / _PRIOR_OUTPUT / 'experiment.json')
    control = results[0]
    old_metrics = previous['validation_metrics']
    new_metrics = control['probability_metrics']
    report['control_reproduction'] = {
        'prior_best_iteration': previous['selected_candidate']['best_iteration'],
        'diagnostic_best_iteration': control['best_iteration'],
        'prior_threshold': old_metrics['threshold'],
        'diagnostic_threshold': new_metrics['threshold'],
        'metric_differences': {name: new_metrics[name] - old_metrics[name]
                               for name in ('precision', 'recall', 'f1',
                                            'average_precision', 'roc_auc')},
        'prior_alert_count': sum(old_metrics['daily_alert_counts'].values()),
        'diagnostic_alert_count': control['alert_count'],
        'investigate_if_different': True,
    }
    report['comparisons_to_control'] = [{
        'arm': result['arm'],
        'raw_min_delta': result['saturation']['raw_min'] - control['saturation']['raw_min'],
        'raw_max_delta': result['saturation']['raw_max'] - control['saturation']['raw_max'],
        'probability_zero_count_delta': result['saturation']['probability_exact_zero']
        - control['saturation']['probability_exact_zero'],
        'probability_one_count_delta': result['saturation']['probability_exact_one']
        - control['saturation']['probability_exact_one'],
        'alert_count_delta': result['alert_count'] - control['alert_count'],
        'metric_differences': {name: result['probability_metrics'][name]
                               - control['probability_metrics'][name]
                               for name in ('precision', 'recall', 'f1',
                                            'average_precision', 'roc_auc')},
    } for result in results]
    _write_json(args.output / 'diagnostic.json', report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--features', type=Path, required=True)
    parser.add_argument('--labels', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--protocol-sha256', required=True)
    parser.add_argument('--parent-protocol', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--n-jobs', type=int, default=4)
    parser.add_argument('--_worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.n_jobs != 4 or not args.root.is_dir():
        parser.error('diagnostic requires exactly four threads and an existing root')
    if args._worker:
        print(json.dumps(run_diagnostic(args), sort_keys=True))
        return
    protocol, _ = verify_diagnostic_protocol(
        args.protocol, args.protocol_sha256, args.parent_protocol, args.root,
    )
    command = [sys.executable, '-m', 'fraudlens.training.diagnostic_run',
               '--features', str(args.features), '--labels', str(args.labels),
               '--protocol', str(args.protocol), '--protocol-sha256', args.protocol_sha256,
               '--parent-protocol', str(args.parent_protocol), '--output', '{output}',
               '--root', str(args.root), '--n-jobs', '4', '--_worker']
    print(json.dumps(supervise_command(
        command, args.output, protocol['resource_ceilings'], report_name='diagnostic.json',
    ), sort_keys=True))


if __name__ == '__main__':
    main()
