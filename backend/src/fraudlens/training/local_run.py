"""Explicit local LightGBM training command for prepared research artifacts."""

import argparse
import csv
import ctypes
import hashlib
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import sklearn

from fraudlens.data.features import FEATURE_ORDER, FEATURE_VERSION
from fraudlens.data.manifest import canonical_json_bytes, sha256_file
from fraudlens.scoring.artifacts import ArtifactMetadata, write_artifact
from fraudlens.training.candidates import LIGHTGBM_GRID, fit_lightgbm_matrix_grid
from fraudlens.training.evaluation import evaluate_validation, rank_lightgbm_candidates
from fraudlens.training.protocol import verify_research_protocol

_CATEGORICAL = ('current_payment_currency', 'current_payment_format')
_NUMERIC = tuple(name for name in FEATURE_ORDER if name not in _CATEGORICAL)
_SOURCE_SHA = 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040'


class _MemoryCounters(ctypes.Structure):
    _fields_ = [
        ('cb', ctypes.c_ulong), ('PageFaultCount', ctypes.c_ulong),
        ('PeakWorkingSetSize', ctypes.c_size_t), ('WorkingSetSize', ctypes.c_size_t),
        ('QuotaPeakPagedPoolUsage', ctypes.c_size_t), ('QuotaPagedPoolUsage', ctypes.c_size_t),
        ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t), ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
        ('PagefileUsage', ctypes.c_size_t), ('PeakPagefileUsage', ctypes.c_size_t),
        ('PrivateUsage', ctypes.c_size_t),
    ]


def _peak_working_set() -> int | None:
    if sys.platform != 'win32':
        return None
    counters = _MemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    handle = ctypes.windll.kernel32.GetCurrentProcess
    handle.restype = ctypes.c_void_p
    get_info = ctypes.windll.psapi.GetProcessMemoryInfo
    get_info.argtypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong)
    if not get_info(handle(), ctypes.byref(counters), counters.cb):
        return None
    return counters.PeakWorkingSetSize


def _load_protocol(path: Path, expected_digest: str) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    protocol = json.loads(raw)
    canonical = canonical_json_bytes(protocol)
    digest = hashlib.sha256(canonical).hexdigest()
    if digest != expected_digest:
        raise ValueError('protocol canonical SHA-256 does not match the supplied digest')
    if protocol.get('format') != 'fraudlens-fr021-training-protocol-v2':
        raise ValueError('protocol is not the reviewed v2 candidate format')
    if protocol.get('dataset_sha256') != _SOURCE_SHA:
        raise ValueError('protocol source identity mismatch')
    return protocol, digest


def _manifest(root: Path, format_name: str) -> dict[str, Any]:
    manifest = json.loads((root / 'manifest.json').read_bytes())
    if manifest.get('format') != format_name:
        raise ValueError(f'unexpected manifest format in {root}')
    for name, digest in manifest.get('files', {}).items():
        if sha256_file(root / f'{name}.jsonl') != digest:
            raise ValueError(f'{name} file checksum mismatch in {root}')
    return manifest


def _read_labels(root: Path, part: str, expected_ids: list[str]) -> np.ndarray:
    result = np.empty(len(expected_ids), dtype=np.int8)
    count = 0
    with (root / f'{part}.jsonl').open(encoding='utf-8') as stream:
        for index, line in enumerate(stream):
            row = json.loads(line)
            if (index >= len(expected_ids) or row.get('transaction_id') != expected_ids[index]
                    or type(row.get('label')) is not int or row['label'] not in (0, 1)):
                raise ValueError(f'{part} labels are not aligned binary identity records')
            result[index] = row['label']
            count += 1
    if count != len(expected_ids):
        raise ValueError(f'{part} label count mismatch')
    return result


def _discover_vocab(path: Path) -> dict[str, tuple[str, ...]]:
    categories = {name: set() for name in _CATEGORICAL}
    count = 0
    with path.open(encoding='utf-8') as stream:
        for line in stream:
            item = json.loads(line)
            if set(item) != {'transaction_id', 'occurred_at_utc', 'features'}:
                raise ValueError('feature row schema mismatch')
            row = item['features']
            if set(row) != set(FEATURE_ORDER):
                raise ValueError('feature field contract mismatch')
            for name in _CATEGORICAL:
                value = row[name]
                if not isinstance(value, str) or not value or value == '__UNKNOWN__':
                    raise ValueError(f'invalid training category for {name}')
                categories[name].add(value)
            count += 1
    if not count:
        raise ValueError('training partition cannot be empty')
    return {name: tuple(sorted(categories[name])) + ('__UNKNOWN__',)
            for name in _CATEGORICAL}


def _read_feature_file(path: Path, vocab: dict[str, tuple[str, ...]], expected_count: int):
    ids: list[str] = []
    timestamps: list[datetime] = []
    width = len(_NUMERIC) + sum(len(vocab[name]) for name in _CATEGORICAL)
    matrix = np.zeros((expected_count, width), dtype=np.float64)
    category_offsets = {}
    lookups = {}
    offset = len(_NUMERIC)
    for name in _CATEGORICAL:
        category_offsets[name] = offset
        lookups[name] = {value: index for index, value in enumerate(vocab[name])}
        offset += len(vocab[name])
    with path.open(encoding='utf-8') as stream:
        for row_number, line in enumerate(stream):
            if row_number >= expected_count:
                raise ValueError(f'{path.name} contains more rows than its frozen count')
            item = json.loads(line)
            if set(item) != {'transaction_id', 'occurred_at_utc', 'features'}:
                raise ValueError('feature row schema mismatch')
            row = item['features']
            if set(row) != set(FEATURE_ORDER):
                raise ValueError('feature field contract mismatch')
            ids.append(item['transaction_id'])
            timestamps.append(datetime.fromisoformat(item['occurred_at_utc']))
            for column, name in enumerate(_NUMERIC):
                value = float(row[name])
                if not np.isfinite(value):
                    raise ValueError(f'{name} is non-finite')
                matrix[row_number, column] = value
            for name in _CATEGORICAL:
                index = lookups[name].get(row[name], lookups[name]['__UNKNOWN__'])
                matrix[row_number, category_offsets[name] + index] = 1.0
    if len(ids) != expected_count:
        raise ValueError(f'{path.name} row count differs from its frozen count')
    return matrix, ids, timestamps


def _git_revision(root: Path) -> tuple[str, bool]:
    revision = subprocess.run(
        ['git', 'rev-parse', 'HEAD'], cwd=root, check=True, capture_output=True,
        text=True,
    ).stdout.strip()
    dirty = bool(subprocess.run(
        ['git', 'status', '--porcelain'], cwd=root, check=True, capture_output=True,
        text=True,
    ).stdout.strip())
    return revision, dirty


def _write_scores(path: Path, ids: list[str], timestamps: list[datetime], scores):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream, lineterminator='\n')
        writer.writerow(('transaction_id', 'occurred_at_utc', 'score'))
        writer.writerows((identity, instant.isoformat(), format(float(score), '.17g'))
                         for identity, instant, score in zip(ids, timestamps, scores, strict=True))


def run_training(args: argparse.Namespace) -> dict[str, Any]:
    started = time.monotonic()
    if args.output.exists():
        raise ValueError('experiment output already exists; refusing overwrite')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    protocol, protocol_sha = _load_protocol(args.protocol, args.protocol_sha256)
    feature_manifest = _manifest(args.features, 'hi-small-ibm-day-60-20-20-features-v1')
    label_manifest = _manifest(args.labels, 'hi-small-ibm-day-60-20-20-training-labels-v1')
    feature_sha = sha256_file(args.features / 'manifest.json')
    verify_research_protocol(
        protocol, protocol_sha, feature_manifest, label_manifest, feature_sha,
        sha256_file(args.labels / 'manifest.json'),
    )
    if (label_manifest.get('feature_manifest_sha256') != feature_sha
            or label_manifest.get('source_sha256') != _SOURCE_SHA
            or feature_manifest.get('source_sha256') != _SOURCE_SHA
            or feature_manifest.get('feature_version') != FEATURE_VERSION
            or feature_manifest.get('feature_order') != list(FEATURE_ORDER)):
        raise ValueError('source, feature or label manifest identities differ')
    if (protocol.get('research_feature_manifest_sha256') != feature_sha
            or protocol.get('research_label_manifest_sha256') != sha256_file(
                args.labels / 'manifest.json')):
        raise ValueError('protocol does not bind the prepared input manifests')

    vocab = _discover_vocab(args.features / 'train.jsonl')
    expected_counts = feature_manifest['counts']
    train, train_ids, _ = _read_feature_file(
        args.features / 'train.jsonl', vocab, expected_counts['train'],
    )
    validation, validation_ids, validation_times = _read_feature_file(
        args.features / 'validation.jsonl', vocab, expected_counts['validation'])
    train_labels = _read_labels(args.labels, 'train', train_ids)
    validation_labels = _read_labels(args.labels, 'validation', validation_ids)
    if np.count_nonzero(train_labels) == 0 or np.count_nonzero(train_labels) == len(train_labels):
        raise ValueError('training data has only one class; fitting refused')
    if np.count_nonzero(validation_labels) == 0:
        raise ValueError('validation has no positives; selection is uninformative')
    train_positive = int(np.count_nonzero(train_labels))
    train_negative = len(train_labels) - train_positive
    train_positive_weight = train_negative / train_positive

    fit_started = time.monotonic()
    models = fit_lightgbm_matrix_grid(
        train, train_labels, validation, validation_labels, n_jobs=args.n_jobs,
    )
    fit_seconds = round(time.monotonic() - fit_started, 3)
    results = []
    for index, (candidate, model) in enumerate(zip(LIGHTGBM_GRID, models, strict=True)):
        scores = model.predict_proba(validation, num_iteration=model.best_iteration_)[:, 1]
        evaluation = evaluate_validation(
            validation_labels, scores, validation_ids, validation_times,
        )
        results.append({
            'family': 'lightgbm', 'candidate_index': index,
            'num_leaves': candidate.num_leaves,
            'learning_rate': candidate.learning_rate,
            'min_child_samples': candidate.min_child_samples,
            'best_iteration': int(model.best_iteration_),
            'f1': evaluation.f1,
            'average_precision': evaluation.average_precision,
            'precision_at_20': evaluation.precision_at[20],
        })
    selected = rank_lightgbm_candidates(results)
    index = selected['candidate_index']
    model = models[index]
    validation_scores = model.predict_proba(validation, num_iteration=model.best_iteration_)[:, 1]
    chosen_evaluation = evaluate_validation(
        validation_labels, validation_scores, validation_ids, validation_times,
    )
    evaluation = asdict(chosen_evaluation)
    args.output.mkdir(exist_ok=False)
    revision, dirty = _git_revision(args.root)
    model_bytes = model.booster_.model_to_string(num_iteration=model.best_iteration_).encode()
    artifact_root = args.output / 'artifacts'
    artifact_root.mkdir()
    artifact_sha = write_artifact(
        artifact_root, 'selected-lightgbm', model_bytes,
        ArtifactMetadata(
            feature_version=FEATURE_VERSION,
            feature_order=FEATURE_ORDER,
            currency_vocabulary=vocab[_CATEGORICAL[0]],
            format_vocabulary=vocab[_CATEGORICAL[1]],
            source_sha256=_SOURCE_SHA,
            protocol_sha256=protocol_sha,
            code_revision=revision,
            seed=42,
            threshold=float(evaluation['threshold']),
            threshold_method='validation-positive-f1-v1',
            validation_metrics={
                'f1': float(evaluation['f1']),
                'average_precision': float(evaluation['average_precision']),
            },
        ),
    )
    _write_scores(args.output / 'validation-scores.csv', validation_ids, validation_times,
                  validation_scores)
    manifest = json.loads((args.features / 'manifest.json').read_bytes())
    test_matrix, test_ids, test_times = _read_feature_file(
        args.features / 'test.jsonl', vocab, expected_counts['test'],
    )
    test_scores = model.predict_proba(test_matrix, num_iteration=model.best_iteration_)[:, 1]
    _write_scores(args.output / 'test-predictions-sealed.csv', test_ids, test_times, test_scores)
    report = {
        'protocol_sha256': protocol_sha,
        'source_sha256': _SOURCE_SHA,
        'feature_manifest_sha256': feature_sha,
        'label_manifest_sha256': sha256_file(args.labels / 'manifest.json'),
        'code_revision': revision,
        'working_tree_dirty': dirty,
        'python_version': sys.version.split()[0],
        'lightgbm_version': __import__('lightgbm').__version__,
        'scikit_learn_version': sklearn.__version__,
        'numpy_version': np.__version__,
        'uv_lock_sha256': sha256_file(args.root / 'uv.lock'),
        'n_jobs': args.n_jobs,
        'device_type': 'cpu',
        'deterministic': True,
        'force_col_wise': True,
        'early_stopping_rounds': 50,
        'logical_cpu_count_observed': os.cpu_count(),
        'peak_working_set_bytes': _peak_working_set(),
        'fit_seconds_all_candidates': fit_seconds,
        'seed': 42,
        'train_count': len(train_ids),
        'train_positive_count': train_positive,
        'train_negative_count': train_negative,
        'scale_pos_weight': train_positive_weight,
        'validation_count': len(validation_ids),
        'test_prediction_count': len(test_ids),
        'test_labels_read': False,
        'selected_candidate': selected,
        'validation_metrics': evaluation,
        'candidate_results': results,
        'artifact_manifest_sha256': artifact_sha,
        'prediction_sha256': {
            'validation': sha256_file(args.output / 'validation-scores.csv'),
            'test': sha256_file(args.output / 'test-predictions-sealed.csv'),
        },
        'elapsed_seconds': round(time.monotonic() - started, 3),
        'features_file_hashes': manifest['files'],
    }
    (args.output / 'experiment.json').write_bytes(canonical_json_bytes(report) + b'\n')
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--features', type=Path, required=True)
    parser.add_argument('--labels', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--protocol-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--n-jobs', type=int, default=4)
    args = parser.parse_args()
    if args.n_jobs < 1 or not args.root.is_dir():
        parser.error('--n-jobs must be positive and --root must be a directory')
    print(json.dumps(run_training(args), sort_keys=True))


if __name__ == '__main__':
    main()
