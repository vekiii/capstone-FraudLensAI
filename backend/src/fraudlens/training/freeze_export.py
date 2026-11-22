"""Freeze the reviewed native model and export sealed test scores without fitting."""

import argparse
import csv
import hashlib
import json
import math
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import lightgbm as lgb
import numpy as np

from fraudlens.data.features import FEATURE_ORDER, FEATURE_VERSION
from fraudlens.data.manifest import canonical_json_bytes, sha256_file
from fraudlens.scoring.artifacts import (
    ArtifactMetadata,
    TrustedArtifact,
    read_verified_artifact,
    write_artifact,
)
from fraudlens.training import comparison_run, local_run
from fraudlens.training.resource_guard import supervise_command

_COMPARISON = ('specs/002-data-and-risk-scoring/'
               't224-cross-family-comparison.ibm-day-60-20-20.candidate.json')
_COMPARISON_SHA = '7fd4e7349b2ef4921166d008f5c3b7e147c21a6554eae5160f33948d323bac32'
_DIAGNOSTIC = ('specs/002-data-and-risk-scoring/'
               't228-lightgbm-numeric-diagnostic.ibm-day-60-20-20.candidate.json')
_SOURCE_MODEL = ('data/eval/ibm-day-lightgbm-numeric-diagnostic-001/'
                 'arms/unweighted/model.txt')
_SOURCE_RESULT = ('data/eval/ibm-day-lightgbm-numeric-diagnostic-001/'
                  'arms/unweighted/result.json')
_SOURCE_SCORES = ('data/eval/ibm-day-lightgbm-numeric-diagnostic-001/'
                  'arms/unweighted/validation-probability.csv')
_PARENT_OUTPUT = 'data/eval/ibm-day-lightgbm-macos-preflight-schema-review-002'
_MODEL_SHA = '3b4e4019312d60610dd0094c6697897a061611a60e7777ed7be35e133af9451c'
_COMPARISON_REPORT_SHA = 'f72108083e2b789a106e13a772f8528256add0d5147ab69e6d2dab1e26a6ee62'
_COMPARISON_STATUS_SHA = 'a833e842ccd2d08fc60f06410601b27ce963e3da3d5f1dd647156f19d1c22036'
_THRESHOLD = 0.2489517623052024
_ARTIFACT_ID = 'selected-unweighted-lightgbm'


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError(f'{path} is not a JSON object')
    return value


def _write_json(path: Path, value: object) -> None:
    path.write_bytes(canonical_json_bytes(value) + b'\n')


def _id_digest(ids: list[str]) -> str:
    return hashlib.sha256(''.join(f'{identity}\n' for identity in ids).encode()).hexdigest()


def _check_identity_time(ids: list[str], times: list[datetime], count: int) -> None:
    if (len(ids) != count or len(times) != count or len(set(ids)) != count
            or any(not isinstance(identity, str) or not identity for identity in ids)
            or any(not isinstance(instant, datetime) or instant.tzinfo is None
                   or instant.utcoffset() is None for instant in times)
            or any(times[index] > times[index + 1] for index in range(count - 1))):
        raise ValueError('prediction IDs, count, order or timestamps are invalid')


def _checked_scores(booster: Any, matrix: np.ndarray, count: int) -> np.ndarray:
    scores = np.asarray(booster.predict(matrix, num_threads=4), dtype=np.float64)
    if (scores.shape != (count,) or not np.isfinite(scores).all()
            or np.any(scores < 0) or np.any(scores > 1)):
        raise ValueError('test scores must be finite probabilities in [0,1]')
    return scores


def verify_validation_reproduction(
    booster: Any, matrix: np.ndarray, ids: list[str], times: list[datetime],
    saved: Path,
) -> None:
    """Require exact native-score and row-identity reproduction before export."""
    _check_identity_time(ids, times, len(matrix))
    predicted = _checked_scores(booster, matrix, len(matrix))
    with saved.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ['transaction_id', 'occurred_at_utc', 'score']:
            raise ValueError('validation score schema mismatch')
        rows = list(reader)
    if (len(rows) != len(ids)
            or any(row['transaction_id'] != ids[index]
                   or row['occurred_at_utc'] != times[index].isoformat()
                   for index, row in enumerate(rows))):
        raise ValueError('validation prediction identity mismatch')
    recorded = np.asarray([float(row['score']) for row in rows], dtype=np.float64)
    if not np.array_equal(predicted, recorded):
        raise ValueError('validation prediction mismatch')


def write_test_predictions(
    booster: Any, matrix: np.ndarray, ids: list[str], times: list[datetime],
    expected_id_sha256: str, output: Path,
) -> str:
    """Write and reread the frozen evaluator CSV; no label argument exists."""
    _check_identity_time(ids, times, len(matrix))
    if _id_digest(ids) != expected_id_sha256:
        raise ValueError('test partition ID/order SHA-256 mismatch')
    scores = _checked_scores(booster, matrix, len(ids))
    local_run._write_scores(output, ids, times, scores)
    with output.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ['transaction_id', 'occurred_at_utc', 'score']:
            raise ValueError('sealed test prediction schema mismatch')
        count = 0
        for index, row in enumerate(reader):
            if (index >= len(ids) or row['transaction_id'] != ids[index]
                    or row['occurred_at_utc'] != times[index].isoformat()
                    or not math.isfinite(float(row['score']))
                    or not 0 <= float(row['score']) <= 1
                    or float(row['score']) != scores[index]):
                raise ValueError('sealed test prediction row mismatch')
            count += 1
    if count != len(ids):
        raise ValueError('sealed test prediction count mismatch')
    return sha256_file(output)


def verify_origins(root: Path, features: Path, labels: Path) -> tuple[
    dict[str, Any], dict[str, Any], dict[str, tuple[str, ...]], bytes,
]:
    """Verify all identities before passing model bytes to LightGBM."""
    protocol = comparison_run.verify_protocol(root / _COMPARISON, _COMPARISON_SHA, root)
    if (features.resolve() != (root / 'data/processed/t219-ibm-day-60-20-20-v1').resolve()
            or labels.resolve() != (root / 'data/processed/t219-ibm-day-60-20-20-labels-v1').resolve()):
        raise ValueError('feature or label directory differs from frozen protocol')
    feature_manifest = local_run._manifest(
        features, 'hi-small-ibm-day-60-20-20-features-v1',
    )
    parent_path = root / comparison_run._PARENT
    parent_protocol = _read_json(parent_path)
    if sha256_file(parent_path) != protocol['parent_protocol_file_sha256']:
        raise ValueError('parent protocol file identity mismatch')
    if (sha256_file(features / 'manifest.json') != protocol['feature_manifest_sha256']
            or sha256_file(labels / 'manifest.json') != protocol['label_manifest_sha256']
            or feature_manifest['source_sha256'] != protocol['source_sha256']
            or feature_manifest['partition_scoreable_id_sha256']['test']
            != parent_protocol['research_partition_scoreable_id_sha256']['test']):
        raise ValueError('transferred feature/label identity mismatch')
    cross_output = root / 'data/eval/ibm-day-cross-family-comparison-001'
    if (sha256_file(cross_output / 'experiment.json') != _COMPARISON_REPORT_SHA
            or sha256_file(cross_output / 'status.json') != _COMPARISON_STATUS_SHA
            or _read_json(cross_output / 'status.json').get('state') != 'complete'
            or _read_json(cross_output / 'experiment.json').get('protocol_sha256')
            != _COMPARISON_SHA):
        raise ValueError('completed cross-family selection provenance mismatch')
    parent = root / _PARENT_OUTPUT
    old_report = _read_json(parent / 'experiment.json')
    if (sha256_file(parent / 'experiment.json')
            != protocol['existing_lightgbm']['weighted_current_phase']['result_sha256']
            or old_report['feature_manifest_sha256'] != protocol['feature_manifest_sha256']
            or old_report['features_file_hashes'] != feature_manifest['files']):
        raise ValueError('original train-only preprocessing lineage mismatch')
    _, original_manifest = read_verified_artifact(
        parent / 'artifacts', 'selected-lightgbm', TrustedArtifact(
            manifest_sha256=old_report['artifact_manifest_sha256'],
            source_sha256=protocol['source_sha256'],
            protocol_sha256=old_report['protocol_sha256'],
            feature_version=FEATURE_VERSION, feature_order=FEATURE_ORDER,
        ),
    )
    vocab = {
        'current_payment_currency': tuple(original_manifest['currency_vocabulary']),
        'current_payment_format': tuple(original_manifest['format_vocabulary']),
    }
    if (len(original_manifest['matrix_feature_order']) != 32
            or len(local_run._NUMERIC) + sum(map(len, vocab.values())) != 32
            or original_manifest['feature_version'] != protocol['feature_version']
            or original_manifest['feature_order'] != protocol['feature_order']):
        raise ValueError('original train-only matrix contract mismatch')
    selected = protocol['existing_lightgbm']['unweighted_diagnostic']
    result = _read_json(root / _SOURCE_RESULT)
    if (sha256_file(root / _SOURCE_RESULT) != selected['result_sha256']
            or result['model_sha256'] != _MODEL_SHA
            or result['probability_csv_sha256'] != sha256_file(root / _SOURCE_SCORES)
            or result['probability_metrics']['threshold'] != _THRESHOLD
            or result['probability_metrics']['f1'] != selected['validation_summary']['f1']
            or result['best_iteration'] != 140):
        raise ValueError('diagnostic validation result or threshold mismatch')
    if sha256_file(root / _SOURCE_MODEL) != _MODEL_SHA:
        raise ValueError('selected model SHA-256 mismatch before native load')
    model_bytes = (root / _SOURCE_MODEL).read_bytes()
    if hashlib.sha256(model_bytes).hexdigest() != _MODEL_SHA:
        raise ValueError('selected model bytes changed during read')
    return protocol, feature_manifest, vocab, model_bytes


def run_export(args: argparse.Namespace) -> dict[str, Any]:
    started = time.monotonic()
    protocol, feature_manifest, vocab, model_bytes = verify_origins(
        args.root, args.features, args.labels,
    )
    booster = lgb.Booster(model_str=model_bytes.decode('utf-8'))
    if booster.num_feature() != 32 or booster.num_trees() != 140:
        raise ValueError('selected model has wrong feature width or tree count')
    validation, validation_ids, validation_times = local_run._read_feature_file(
        args.features / 'validation.jsonl', vocab, feature_manifest['counts']['validation'],
    )
    verify_validation_reproduction(
        booster, validation, validation_ids, validation_times, args.root / _SOURCE_SCORES,
    )
    test, test_ids, test_times = local_run._read_feature_file(
        args.features / 'test.jsonl', vocab, feature_manifest['counts']['test'],
    )
    if len(test_ids) != 233_070:
        raise ValueError('test partition count differs from frozen experiment')
    args.output.mkdir(parents=True, exist_ok=True)
    artifact_root = args.output / 'artifacts'
    artifact_root.mkdir()
    result = _read_json(args.root / _SOURCE_RESULT)
    revision = subprocess.run(
        ['git', 'rev-parse', 'HEAD'], cwd=args.root, check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    artifact_sha = write_artifact(
        artifact_root, _ARTIFACT_ID, model_bytes, ArtifactMetadata(
            feature_version=FEATURE_VERSION, feature_order=FEATURE_ORDER,
            currency_vocabulary=vocab['current_payment_currency'],
            format_vocabulary=vocab['current_payment_format'],
            source_sha256=protocol['source_sha256'], protocol_sha256=_COMPARISON_SHA,
            code_revision=revision, seed=42, threshold=_THRESHOLD,
            threshold_method='validation-positive-f1-v1',
            validation_metrics={
                'f1': result['probability_metrics']['f1'],
                'average_precision': result['probability_metrics']['average_precision'],
            },
        ),
    )
    trusted_model, new_manifest = read_verified_artifact(
        artifact_root, _ARTIFACT_ID, TrustedArtifact(
            manifest_sha256=artifact_sha, source_sha256=protocol['source_sha256'],
            protocol_sha256=_COMPARISON_SHA, feature_version=FEATURE_VERSION,
            feature_order=FEATURE_ORDER,
        ),
    )
    if trusted_model != model_bytes or new_manifest['threshold'] != _THRESHOLD:
        raise ValueError('new trusted artifact does not match selected bytes/threshold')
    prediction_sha = write_test_predictions(
        booster, test, test_ids, test_times,
        feature_manifest['partition_scoreable_id_sha256']['test'],
        args.output / 'test-predictions-sealed.csv',
    )
    code_paths = (
        'backend/src/fraudlens/training/freeze_export.py',
        'backend/src/fraudlens/training/local_run.py',
        'backend/src/fraudlens/training/comparison_run.py',
        'backend/src/fraudlens/training/resource_guard.py',
        'backend/src/fraudlens/scoring/artifacts.py',
        'backend/src/fraudlens/data/features.py',
        'backend/src/fraudlens/data/manifest.py',
    )
    lineage = {
        'format': 'fraudlens-fr023-selected-model-freeze-v1',
        'source_model_sha256': _MODEL_SHA,
        'frozen_model_sha256': sha256_file(artifact_root / _ARTIFACT_ID / 'model.txt'),
        'trusted_artifact_manifest_sha256': artifact_sha,
        'original_train_only_manifest_sha256': _read_json(
            args.root / _PARENT_OUTPUT / 'experiment.json',
        )['artifact_manifest_sha256'],
        'feature_version': FEATURE_VERSION, 'feature_order': list(FEATURE_ORDER),
        'matrix_feature_order': new_manifest['matrix_feature_order'],
        'matrix_columns': 32,
        'currency_vocabulary': list(vocab['current_payment_currency']),
        'format_vocabulary': list(vocab['current_payment_format']),
        'source_sha256': protocol['source_sha256'],
        'feature_manifest_sha256': protocol['feature_manifest_sha256'],
        'test_feature_file_sha256': feature_manifest['files']['test'],
        'test_partition_id_sha256': feature_manifest['partition_scoreable_id_sha256']['test'],
        'validation_score_sha256': sha256_file(args.root / _SOURCE_SCORES),
        'validation_result_sha256': sha256_file(args.root / _SOURCE_RESULT),
        'validation_metrics': {
            key: result['probability_metrics'][key]
            for key in ('f1', 'average_precision', 'precision', 'recall', 'threshold')
        },
        'threshold': _THRESHOLD,
        'diagnostic_protocol_canonical_sha256': protocol['diagnostic_protocol_canonical_sha256'],
        'diagnostic_protocol_file_sha256': sha256_file(args.root / _DIAGNOSTIC),
        'cross_family_protocol_canonical_sha256': _COMPARISON_SHA,
        'cross_family_protocol_file_sha256': sha256_file(args.root / _COMPARISON),
        'cross_family_experiment_sha256': sha256_file(
            args.root / 'data/eval/ibm-day-cross-family-comparison-001/experiment.json',
        ),
        'uv_lock_sha256': sha256_file(args.root / 'uv.lock'),
        'runtime': protocol['runtime'], 'git_head': revision,
        'export_code_sha256': {name: sha256_file(args.root / name) for name in code_paths},
        'test_prediction_sha256': prediction_sha,
        'test_prediction_count': len(test_ids),
        'test_labels_read': False, 'fit_called': False,
    }
    _write_json(args.output / 'freeze-lineage.json', lineage)
    report = {
        'kind': 'fraudlens-fr023-selected-model-freeze-v1',
        'protocol_sha256': _COMPARISON_SHA,
        'source_sha256': protocol['source_sha256'],
        'feature_manifest_sha256': protocol['feature_manifest_sha256'],
        'artifact_manifest_sha256': artifact_sha,
        'selected_model_sha256': _MODEL_SHA,
        'validation_metrics': lineage['validation_metrics'],
        'prediction_sha256': {'test': prediction_sha},
        'test_prediction_count': len(test_ids),
        'test_partition_id_sha256': lineage['test_partition_id_sha256'],
        'freeze_lineage_sha256': sha256_file(args.output / 'freeze-lineage.json'),
        'test_labels_read': False, 'showcase_labels_read': False,
        'fit_called': False, 'elapsed_seconds': time.monotonic() - started,
    }
    _write_json(args.output / 'experiment.json', report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('features', 'labels', 'output', 'root'):
        parser.add_argument(f'--{name}', required=True, type=Path)
    parser.add_argument('--n-jobs', type=int, required=True)
    parser.add_argument('--_worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.n_jobs != 4 or not args.root.is_dir():
        parser.error('frozen export requires exactly four threads and an existing root')
    if args._worker:
        print(json.dumps(run_export(args), sort_keys=True))
        return
    protocol, _, _, _ = verify_origins(args.root, args.features, args.labels)
    command = [sys.executable, '-m', 'fraudlens.training.freeze_export',
               '--features', str(args.features), '--labels', str(args.labels),
               '--output', '{output}', '--root', str(args.root),
               '--n-jobs', '4', '--_worker']
    print(json.dumps(supervise_command(
        command, args.output, protocol['resource_ceilings'], report_name='experiment.json',
    ), sort_keys=True))


if __name__ == '__main__':
    main()
