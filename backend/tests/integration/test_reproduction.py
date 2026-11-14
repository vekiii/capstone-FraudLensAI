"""T063 RED: frozen repeat must reject changed inputs and numeric divergence."""

import hashlib
import json

import pytest

from fraudlens.pipeline_cli import main


def fixtures():
    protocol = {'reproduction_tolerances': {'probability_absolute': 1e-8,
                                            'metric_absolute': 1e-8},
                'holdout': {'old_tree_60_20_20_test_exposure': True}}
    bundle = {'protocol_sha256': 'p' * 64, 'manifest_sha256': 'm' * 64,
              'source_sha256': 's' * 64, 'dataset_version': 'dv_' + 'd' * 64,
              'feature_version': 'history-v1', 'ordered_features': ['x'],
              'thresholds': {'model': 'no_alert', 'rules': 'no_alert'},
              'test_ids_sha256': 'i' * 64,
              'predictions': {'model': [['D1', 0.1], ['D2', 0.9]],
                              'rules': [['D1', 0.0], ['D2', 1.0]]},
              'run_id': 'run_original', 'scored_at': 'earlier'}
    report = {'disclosure': 'first_disclosure', 'prior_test_exposure': True,
              'metrics': {'model': {'average_precision': 0.5, 'row_count': 2,
                                    'threshold': 'no_alert'},
                          'rules': {'average_precision': 0.4, 'row_count': 2,
                                    'threshold': 'no_alert'}}}
    return protocol, bundle, report


def test_reproduce_cli_rejects_missing_inputs(tmp_path):
    assert main(['reproduce', '--source-store', str(tmp_path / 'absent.sqlite'),
                 '--protocol', str(tmp_path / 'absent.json'),
                 '--artifact-dir', str(tmp_path / 'artifact'),
                 '--manifest-sha', 'a' * 64,
                 '--predictions', str(tmp_path / 'predictions.json'),
                 '--report', str(tmp_path / 'report.json'),
                 '--ledger', str(tmp_path / 'ledger.json'),
                 '--out-dir', str(tmp_path / 'repeat')]) != 0
    assert not (tmp_path / 'repeat').exists()


def test_semantic_repeat_ignores_run_time_and_accepts_declared_tolerance():
    from fraudlens.pipeline_cli import compare_reproduction

    protocol, original, report = fixtures()
    repeated = json.loads(json.dumps(original))
    repeated['run_id'] = 'run_repeat'
    repeated['scored_at'] = 'later'
    repeated['predictions']['model'][0][1] += 5e-9
    metrics = json.loads(json.dumps(report['metrics']))
    metrics['model']['average_precision'] += 5e-9
    result = compare_reproduction(protocol, original, repeated, report, metrics)
    assert result['status'] == 'exploratory_reuse'
    assert result['max_prediction_abs_diff'] <= 1e-8
    assert result['max_metric_abs_diff'] <= 1e-8


@pytest.mark.parametrize('change', ['source_sha256', 'manifest_sha256',
                                    'dataset_version', 'test_ids_sha256',
                                    'feature_version', 'thresholds'])
def test_changed_frozen_identity_fails(change):
    from fraudlens.pipeline_cli import compare_reproduction

    protocol, original, report = fixtures()
    repeated = json.loads(json.dumps(original))
    repeated[change] = 'changed'
    with pytest.raises(ValueError):
        compare_reproduction(protocol, original, repeated, report, report['metrics'])


def test_prediction_and_metric_tolerance_violations_fail():
    from fraudlens.pipeline_cli import compare_reproduction

    protocol, original, report = fixtures()
    repeated = json.loads(json.dumps(original))
    repeated['predictions']['model'][0][1] += 2e-8
    with pytest.raises(ValueError):
        compare_reproduction(protocol, original, repeated, report, report['metrics'])
    repeated = json.loads(json.dumps(original))
    metrics = json.loads(json.dumps(report['metrics']))
    metrics['model']['average_precision'] += 2e-8
    with pytest.raises(ValueError):
        compare_reproduction(protocol, original, repeated, report, metrics)


def test_prediction_file_hash_and_exposure_are_bound():
    from fraudlens.pipeline_cli import validate_reproduction_files

    protocol, bundle, report = fixtures()
    raw = json.dumps(bundle).encode()
    report['predictions_sha256'] = hashlib.sha256(raw).hexdigest()
    assert validate_reproduction_files(protocol, raw, report)['prior_test_exposure']
    with pytest.raises(ValueError):
        validate_reproduction_files(protocol, raw + b' ', report)
    with pytest.raises(ValueError):
        validate_reproduction_files(protocol | {'holdout': {}}, raw, report)
