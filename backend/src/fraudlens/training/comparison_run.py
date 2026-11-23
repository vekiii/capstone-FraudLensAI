"""Pending-review FR-023 comparison: seven fits and one constant, no holdout use."""

import argparse
import hashlib
import json
import pickle
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

import lightgbm
import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from threadpoolctl import threadpool_limits

from fraudlens.data.manifest import canonical_json_bytes, sha256_file
from fraudlens.training import candidates, diagnostic_run, local_run
from fraudlens.training.evaluation import evaluate_validation
from fraudlens.training.resource_guard import supervise_command

_FORMAT = 'fraudlens-fr023-cross-family-comparison-v1'
_DIAGNOSTIC_SHA = '22a4e6c8efe744de7d4d9b5304a8252f144ffa532037d7f0d8a5a83c66951b5b'
_MODEL_SHA = '3b4e4019312d60610dd0094c6697897a061611a60e7777ed7be35e133af9451c'
_RULE = 'specs/002-data-and-risk-scoring/t224-cross-family-selection.json'
_CHOICES = 'specs/002-data-and-risk-scoring/t221-model-choices.json'
_DIAGNOSTIC = ('specs/002-data-and-risk-scoring/'
               't228-lightgbm-numeric-diagnostic.ibm-day-60-20-20.candidate.json')
_PARENT = ('specs/002-data-and-risk-scoring/'
           't219-training-protocol.ibm-day-60-20-20.macos-preflight-schema-review.candidate.json')


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError(f'{path} must be a JSON object')
    return value


def _digest(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.write_bytes(canonical_json_bytes(value) + b'\n')


def declared_plan() -> dict[str, Any]:
    return {
        'baselines': ['prevalence_constant', 'decision_tree', 'logistic_regression'],
        'hist_gradient_boosting': [asdict(item) for item in candidates.HIST_GRADIENT_GRID],
    }


def validate_plan(plan: object) -> None:
    if plan != declared_plan():
        raise ValueError('comparison plan differs from frozen FR-023 choices')


def verify_protocol(path: Path, digest: str, root: Path) -> dict[str, Any]:
    protocol = _read_json(path)
    if (_digest(protocol) != digest or protocol.get('format') != _FORMAT
            or protocol.get('status') != 'pending_human_review'):
        raise ValueError('comparison protocol digest, format or status mismatch')
    validate_plan(protocol.get('fit_plan'))
    choices = _read_json(root / _CHOICES)
    rule = _read_json(root / _RULE)
    if (protocol.get('model_choices_canonical_sha256') != _digest(choices)
            or protocol.get('cross_family_rule_canonical_sha256') != _digest(rule)
            or protocol.get('cross_family_rule') != rule
            or rule.get('activation') != 'separate_reviewed_decision_after_current_lightgbm_phase'):
        raise ValueError('frozen model choices or cross-family rule mismatch')
    if (protocol.get('diagnostic_protocol_canonical_sha256') != _DIAGNOSTIC_SHA
            or protocol.get('diagnostic_protocol_file_sha256') != sha256_file(root / _DIAGNOSTIC)
            or protocol.get('parent_protocol_canonical_sha256')
            != diagnostic_run._PARENT_SHA
            or protocol.get('parent_protocol_file_sha256') != sha256_file(root / _PARENT)):
        raise ValueError('comparison lineage mismatch')
    if (protocol.get('uv_lock_sha256') != sha256_file(root / 'uv.lock')
            or protocol.get('runtime') != {
                'python': sys.version.split()[0], 'lightgbm': lightgbm.__version__,
                'numpy': np.__version__, 'scikit_learn': sklearn.__version__,
            } or protocol.get('n_jobs') != 4):
        raise ValueError('comparison locked runtime mismatch')
    code = protocol.get('implementation_file_sha256')
    required_code = {
        'backend/src/fraudlens/training/comparison_run.py',
        'backend/src/fraudlens/training/diagnostic_run.py',
        'backend/src/fraudlens/training/local_run.py',
        'backend/src/fraudlens/training/resource_guard.py',
        'backend/src/fraudlens/training/candidates.py',
        'backend/src/fraudlens/training/baselines.py',
        'backend/src/fraudlens/training/evaluation.py',
        'backend/src/fraudlens/training/protocol.py',
        'backend/src/fraudlens/data/features.py',
        'backend/src/fraudlens/data/manifest.py',
    }
    if (not isinstance(code, dict) or set(code) != required_code
            or any(sha256_file(root / name) != value for name, value in code.items())):
        raise ValueError('comparison executable code hash mismatch')
    diagnostic, parent = diagnostic_run.verify_diagnostic_protocol(
        root / _DIAGNOSTIC, _DIAGNOSTIC_SHA, root / _PARENT, root,
    )
    if (protocol.get('resource_ceilings') != diagnostic['resource_ceilings']
            or protocol.get('feature_manifest_sha256') != diagnostic['feature_manifest_sha256']
            or protocol.get('label_manifest_sha256') != diagnostic['label_manifest_sha256']
            or protocol.get('input_file_sha256') != diagnostic['input_file_sha256']
            or protocol.get('partition_id_sha256') != diagnostic['partition_id_sha256']
            or protocol.get('source_sha256') != parent['dataset_sha256']):
        raise ValueError('comparison input or resource identity mismatch')
    old = protocol.get('existing_lightgbm')
    weighted = root / 'data/eval/ibm-day-lightgbm-macos-preflight-schema-review-002'
    unweighted = root / 'data/eval/ibm-day-lightgbm-numeric-diagnostic-001/arms/unweighted'
    for entry, model in ((old.get('weighted_current_phase') if isinstance(old, dict) else None,
                          weighted / 'artifacts/selected-lightgbm/model.txt'),
                         (old.get('unweighted_diagnostic') if isinstance(old, dict) else None,
                          unweighted / 'model.txt')):
        if not isinstance(entry, dict) or entry.get('model_sha256') != sha256_file(model):
            raise ValueError('existing LightGBM artifact identity mismatch')
    if old['unweighted_diagnostic']['model_sha256'] != _MODEL_SHA:
        raise ValueError('unweighted LightGBM model identity mismatch')
    if (old['weighted_current_phase'].get('result_sha256')
            != sha256_file(weighted / 'experiment.json')
            or old['unweighted_diagnostic'].get('result_sha256')
            != sha256_file(unweighted / 'result.json')):
        raise ValueError('existing LightGBM result identity mismatch')
    return protocol


def _score_model(name: str, model: Any, validation: np.ndarray) -> np.ndarray:
    scores = np.asarray(model.predict_proba(validation)[:, 1], dtype=np.float64)
    if (scores.shape != (len(validation),) or not np.isfinite(scores).all()
            or np.any(scores < 0) or np.any(scores > 1)):
        raise ValueError(f'{name}: invalid probabilities; comparison remains incomplete')
    return scores


def compare_matrices(
    train: np.ndarray, train_labels: np.ndarray, validation: np.ndarray,
    validation_labels: np.ndarray, ids: list[str], times: list[datetime],
    output: Path, *, n_jobs: int, synthetic: bool = False,
) -> list[dict[str, Any]]:
    """Fit exactly the declared candidates from aligned train/validation arrays."""
    if (train.ndim != 2 or validation.ndim != 2 or train.shape[1] != validation.shape[1]
            or len(train) != len(train_labels) or len(validation) != len(validation_labels)
            or len(ids) != len(validation) or len(times) != len(validation)
            or not np.isfinite(train).all() or not np.isfinite(validation).all()
            or not np.isin(train_labels, (0, 1)).all()
            or not np.isin(validation_labels, (0, 1)).all()
            or len(set(ids)) != len(ids) or n_jobs < 1):
        raise ValueError('comparison matrices, labels or identities are invalid')
    positives = int(np.count_nonzero(train_labels))
    negatives = len(train_labels) - positives
    if not positives or not negatives or not np.count_nonzero(validation_labels):
        raise ValueError('comparison requires train and validation positives')
    ratio = negatives / positives
    weights = {0: 1.0, 1: ratio}
    numeric_width = train.shape[1] if synthetic else len(local_run._NUMERIC)
    if numeric_width > train.shape[1]:
        raise ValueError('numeric feature width exceeds matrix width')
    (output / 'candidates').mkdir(parents=True)
    results: list[dict[str, Any]] = []
    names = declared_plan()['baselines'] + [
        f'hist_gradient_boosting_{index}' for index in range(1, 6)
    ]
    for index, name in enumerate(names):
        target = output / 'candidates' / name
        target.mkdir()
        fit_start = time.monotonic()
        params: dict[str, Any]
        marker = output / 'fit-progress.json'
        if name != 'prevalence_constant':
            _write_json(marker, {'candidate_index': index, 'arm': name,
                                 'started_monotonic': time.monotonic()})
        try:
            if name == 'prevalence_constant':
                model = None
                params = {'positive_probability': positives / len(train_labels)}
                scores = np.full(len(validation), params['positive_probability'])
                artifact = {'format': 'prevalence-constant-v1', **params}
                artifact_bytes = canonical_json_bytes(artifact) + b'\n'
                artifact_name = 'model.json'
            elif name == 'decision_tree':
                model = DecisionTreeClassifier(max_depth=5, min_samples_leaf=500,
                                               class_weight=weights, random_state=42)
                params = model.get_params()
                model.fit(train, train_labels)
                scores = _score_model(name, model, validation)
                artifact_bytes = pickle.dumps(model, protocol=pickle.HIGHEST_PROTOCOL)
                artifact_name = 'model.pkl'
            elif name == 'logistic_regression':
                scaler = StandardScaler()
                scaled_train = train.copy()
                scaled_train[:, :numeric_width] = scaler.fit_transform(
                    scaled_train[:, :numeric_width],
                )
                scaled_validation = validation.copy()
                scaled_validation[:, :numeric_width] = scaler.transform(
                    scaled_validation[:, :numeric_width],
                )
                model = LogisticRegression(l1_ratio=0.0, C=1.0, solver='lbfgs',
                                           max_iter=1000, class_weight=weights,
                                           random_state=42)
                params = {'estimator': model.get_params(),
                          'numeric_width': numeric_width,
                          'scaler_mean': scaler.mean_.tolist(),
                          'scaler_scale': scaler.scale_.tolist()}
                with threadpool_limits(limits=n_jobs):
                    model.fit(scaled_train, train_labels)
                scores = _score_model(name, model, scaled_validation)
                artifact_bytes = pickle.dumps((scaler, model, numeric_width),
                                              protocol=pickle.HIGHEST_PROTOCOL)
                artifact_name = 'model.pkl'
            else:
                candidate = candidates.HIST_GRADIENT_GRID[index - 3]
                sample_weights = np.where(train_labels == 1, ratio, 1.0)
                model = candidates._fit_hist_gradient(candidate, train, train_labels,
                                                      sample_weights, n_jobs)
                params = model.get_params()
                scores = _score_model(name, model, validation)
                artifact_bytes = pickle.dumps(model, protocol=pickle.HIGHEST_PROTOCOL)
                artifact_name = 'model.pkl'
        finally:
            marker.unlink(missing_ok=True)
        elapsed = time.monotonic() - fit_start
        if not np.isfinite(scores).all() or np.any(scores < 0) or np.any(scores > 1):
            raise ValueError(f'{name}: invalid probabilities; comparison remains incomplete')
        (target / artifact_name).write_bytes(artifact_bytes)
        local_run._write_scores(target / 'validation-scores.csv', ids, times, scores)
        metrics = asdict(evaluate_validation(validation_labels, scores, ids, times))
        values, counts = np.unique(scores, return_counts=True)
        result = {
            'name': name, 'index': index, 'family': 'hist_gradient_boosting'
            if name.startswith('hist_gradient') else name,
            'parameters': params,
            'training_weight': None if name == 'prevalence_constant' else weights,
            'metrics': metrics,
            'alert_count': sum(metrics['daily_alert_counts'].values()),
            'fit_elapsed_seconds': elapsed,
            'iterations_executed': int(model.n_iter_) if name.startswith('hist_gradient')
            else int(model.n_iter_[0]) if name == 'logistic_regression' else None,
            'worker_peak_bytes_cumulative_at_end': diagnostic_run._peak_bytes(),
            'runtime': {
                'python': sys.version.split()[0], 'scikit_learn': sklearn.__version__,
                'numpy': np.__version__, 'n_jobs': n_jobs,
            },
            'score_diagnostics': {
                'exact_zero': int(np.count_nonzero(scores == 0)),
                'exact_one': int(np.count_nonzero(scores == 1)),
                'distinct': len(values), 'top_tie': int(counts[-1]),
                'min': float(values[0]), 'max': float(values[-1]),
            },
            'model_artifact': artifact_name,
            'model_sha256': hashlib.sha256(artifact_bytes).hexdigest(),
            'validation_scores_sha256': sha256_file(target / 'validation-scores.csv'),
            'serialization': 'JSON constant' if model is None
            else 'trusted-local pickle; never load untrusted bytes or use in app',
        }
        _write_json(target / 'result.json', result)
        results.append(result)
    return results


def run_comparison(args: argparse.Namespace) -> dict[str, Any]:
    started = time.monotonic()
    protocol = verify_protocol(args.protocol, args.protocol_sha256, args.root)
    prep = argparse.Namespace(
        features=args.features, labels=args.labels, root=args.root,
        protocol=args.root / _DIAGNOSTIC, protocol_sha256=_DIAGNOSTIC_SHA,
        parent_protocol=args.root / _PARENT,
    )
    (_, train, train_labels, validation, validation_labels,
     ids, times, vocab) = diagnostic_run._prepare_inputs(prep)
    results = compare_matrices(train, train_labels, validation, validation_labels,
                               ids, times, args.output, n_jobs=args.n_jobs)
    report = {
        'kind': _FORMAT, 'protocol_sha256': args.protocol_sha256,
        'status': 'comparison_complete_review_pending',
        'candidate_results': [
            {'name': item['name'], 'result_sha256': sha256_file(
                args.output / 'candidates' / item['name'] / 'result.json',
            ), 'model_sha256': item['model_sha256']}
            for item in results
        ],
        'existing_lightgbm': protocol['existing_lightgbm'],
        'train_count': len(train), 'validation_count': len(validation),
        'vocabulary_sizes': {key: len(value) for key, value in vocab.items()},
        'validation_already_used_for_development': True,
        'test_features_read': False, 'test_labels_read': False,
        'test_predictions_written': False,
        'elapsed_seconds': time.monotonic() - started,
        'worker_peak_bytes_cumulative': diagnostic_run._peak_bytes(),
        'git_head': subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=args.root,
                                   capture_output=True, text=True, check=True).stdout.strip(),
    }
    _write_json(args.output / 'experiment.json', report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('features', 'labels', 'protocol', 'output', 'root'):
        parser.add_argument(f'--{name}', type=Path, required=True)
    parser.add_argument('--protocol-sha256', required=True)
    parser.add_argument('--n-jobs', type=int, required=True)
    parser.add_argument('--_worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.n_jobs != 4 or not args.root.is_dir():
        parser.error('comparison requires four threads and an existing root')
    if args._worker:
        print(json.dumps(run_comparison(args), sort_keys=True))
        return
    protocol = verify_protocol(args.protocol, args.protocol_sha256, args.root)
    command = [sys.executable, '-m', 'fraudlens.training.comparison_run',
               '--features', str(args.features), '--labels', str(args.labels),
               '--protocol', str(args.protocol), '--protocol-sha256', args.protocol_sha256,
               '--output', '{output}', '--root', str(args.root), '--n-jobs', '4', '--_worker']
    print(json.dumps(supervise_command(
        command, args.output, protocol['resource_ceilings'], report_name='experiment.json',
    ), sort_keys=True))


if __name__ == '__main__':
    main()
