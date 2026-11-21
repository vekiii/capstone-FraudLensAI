"""Structural and train-vocabulary tests for the local reader; no estimator fit."""

import argparse
import json

import numpy as np
import pytest

from fraudlens.data.features import FEATURE_ORDER, FEATURE_VERSION
from fraudlens.training import local_run
from fraudlens.training.local_run import _NUMERIC, _discover_vocab, _read_feature_file


def _record(identity, currency, payment_format):
    features = {name: 0 for name in FEATURE_ORDER}
    features['sender_paid_sum_same_currency_24h'] = '0.00'
    features['receiver_received_sum_same_currency_24h'] = '0.00'
    features['current_payment_currency'] = currency
    features['current_payment_format'] = payment_format
    return {
        'transaction_id': identity,
        'occurred_at_utc': '2022-09-02T01:00:00+00:00',
        'features': features,
    }


def test_matrix_vocab_is_discovered_from_train_and_unseen_values_use_unknown(tmp_path):
    train_path = tmp_path / 'train.jsonl'
    train_path.write_text(json.dumps(_record('train', 'USD', 'ACH')) + '\n')
    validation_path = tmp_path / 'validation.jsonl'
    validation_path.write_text(json.dumps(_record('valid', 'EUR', 'WIRE')) + '\n')

    vocabulary = _discover_vocab(train_path)
    matrix, ids, _ = _read_feature_file(validation_path, vocabulary, 1)

    assert vocabulary['current_payment_currency'] == ('USD', '__UNKNOWN__')
    assert vocabulary['current_payment_format'] == ('ACH', '__UNKNOWN__')
    assert ids == ['valid']
    assert matrix.shape == (1, len(FEATURE_ORDER) + 2)
    assert matrix[0, len(_NUMERIC)] == 0
    assert matrix[0, len(_NUMERIC) + 1] == 1
    assert matrix[0, len(_NUMERIC) + 2] == 0
    assert matrix[0, len(_NUMERIC) + 3] == 1


def _publisher_manifest_fixture(monkeypatch, tmp_path, *, feature_order=None,
                                feature_version=FEATURE_VERSION):
    """Mirror the IBM-day publisher's top-level schema, without data rows."""
    features = {
        'format': 'hi-small-ibm-day-60-20-20-features-v1',
        'source_sha256': local_run._SOURCE_SHA,
        'parent_feature_manifest_sha256': 'parent',
        'method': 'whole_utc_day_boundaries_minimize_max_relative_target_share_error',
        'target_shares': {'train': 0.6, 'validation': 0.2, 'test': 0.2},
        'warmup_rows_excluded_from_partitions': 1,
        'showcase_rows_excluded_from_experiment': 1,
        'chronological': True,
        'cutoffs_inclusive_utc_day': {},
        'counts': {'train': 1, 'validation': 1, 'test': 1},
        'daily_counts': [],
        'partition_scoreable_id_sha256': {},
        'label_values_read': False,
        'files': {'train': 'a', 'validation': 'b', 'test': 'c'},
        'resource_ceilings': {},
    }
    labels = {
        'format': 'hi-small-ibm-day-60-20-20-training-labels-v1',
        'source_sha256': local_run._SOURCE_SHA,
        'feature_manifest_sha256': 'feature-sha',
        'scope': 'train_and_validation_only',
        'label_values_read': {'train': True, 'validation': True,
                              'test': False, 'showcase': False, 'warmup': False},
        'counts': {}, 'partition_scoreable_id_sha256': {},
        'files': {'train': 'd', 'validation': 'e'},
    }
    protocol = {
        'dataset_sha256': local_run._SOURCE_SHA,
        'feature_version': feature_version,
        'feature_order': list(FEATURE_ORDER) if feature_order is None else feature_order,
        'feature_manifest_sha256': 'parent',
        'research_feature_manifest_sha256': 'feature-sha',
        'research_label_manifest_sha256': 'label-sha',
    }
    monkeypatch.setattr(local_run, '_load_protocol', lambda *_: (protocol, 'protocol-sha'))
    monkeypatch.setattr(local_run, '_manifest', lambda path, _format: (
        features if path.name == 'features' else labels
    ))
    monkeypatch.setattr(local_run, 'verify_research_protocol', lambda *_: None)
    monkeypatch.setattr(local_run, 'sha256_file', lambda path: (
        'feature-sha' if path.parent.name == 'features' else 'label-sha'
    ))
    args = argparse.Namespace(
        output=tmp_path / 'out', features=tmp_path / 'features',
        labels=tmp_path / 'labels', protocol=tmp_path / 'protocol.json',
        protocol_sha256='protocol-sha', root=tmp_path, n_jobs=4,
        _worker=False,
    )
    return args


def test_ibm_day_publisher_schema_reaches_preprocessing_without_fit(monkeypatch, tmp_path):
    class ReachedPreprocessing(Exception):
        pass

    args = _publisher_manifest_fixture(monkeypatch, tmp_path)
    monkeypatch.setattr(local_run, '_discover_vocab', lambda *_: (
        (_ for _ in ()).throw(ReachedPreprocessing())
    ))
    monkeypatch.setattr(local_run, 'fit_lightgbm_matrix_grid', lambda *_a, **_k: (
        pytest.fail('fit must not start during this contract test')
    ))

    with pytest.raises(ReachedPreprocessing):
        local_run.run_training(args)


def test_ibm_day_publisher_schema_rejects_feature_order_mismatch(monkeypatch, tmp_path):
    args = _publisher_manifest_fixture(
        monkeypatch, tmp_path, feature_order=list(reversed(FEATURE_ORDER)),
    )
    monkeypatch.setattr(local_run, '_discover_vocab', lambda *_: (
        pytest.fail('preprocessing must not start with mismatched feature order')
    ))

    with pytest.raises(ValueError, match='feature.*order|feature.*identity'):
        local_run.run_training(args)


def test_ibm_day_publisher_schema_rejects_feature_version_mismatch(monkeypatch, tmp_path):
    args = _publisher_manifest_fixture(monkeypatch, tmp_path, feature_version='unknown-v2')
    monkeypatch.setattr(local_run, '_discover_vocab', lambda *_: (
        pytest.fail('preprocessing must not start with mismatched feature version')
    ))

    with pytest.raises(ValueError, match='feature version/order'):
        local_run.run_training(args)


def test_unknown_feature_manifest_schema_is_rejected(tmp_path):
    root = tmp_path / 'features'
    root.mkdir()
    (root / 'manifest.json').write_text(json.dumps({
        'format': 'hi-small-ibm-day-60-20-20-features-v1',
        'files': {'train': 'a', 'validation': 'b', 'test': 'c'},
        'unexpected_schema': True,
    }))
    with pytest.raises(ValueError, match='unexpected manifest format'):
        local_run._manifest(root, 'hi-small-ibm-day-60-20-20-features-v1')


def test_preflight_only_writes_input_report_without_calling_fit(monkeypatch, tmp_path):
    args = argparse.Namespace(output=tmp_path / 'preflight', _worker=True)
    prepared = local_run._PreparedInputs(
        'protocol', 'feature', 'label', {},
        {'current_payment_currency': ('USD', '__UNKNOWN__'),
         'current_payment_format': ('ACH', '__UNKNOWN__')},
        np.zeros((2, 4)), ['a', 'b'], np.array([0, 1]),
        np.zeros((1, 4)), ['v'], [], np.array([1]), 1, 1, 1.0,
    )
    monkeypatch.setattr(local_run, '_prepare_training_inputs', lambda *_: prepared)
    monkeypatch.setattr(local_run, 'fit_lightgbm_matrix_grid', lambda *_a, **_k: (
        pytest.fail('preflight invoked estimator fit')
    ))

    report = local_run.run_preflight(args)

    assert report['estimator_fit_called'] is False
    assert report['test_labels_read'] is False
    assert report['test_feature_file_hashed'] is True
    assert report['test_feature_rows_parsed'] is False
    assert report['train_matrix_shape'] == [2, 4]
    assert (args.output / 'preflight.json').is_file()
    assert not (args.output / 'experiment.json').exists()


def test_preflight_cli_routes_to_guard_without_fit(monkeypatch, tmp_path, capsys):
    output = tmp_path / 'preflight'
    monkeypatch.setattr(local_run, '_load_protocol', lambda *_: ({
        'resource_ceilings': {'fit': {'initial_free_disk_bytes_min': 1}},
    }, 'protocol'))
    monkeypatch.setattr(local_run, 'fit_lightgbm_matrix_grid', lambda *_a, **_k: (
        pytest.fail('CLI preflight invoked estimator fit')
    ))
    called = {}

    def fake_supervise(command, target, limits, **kwargs):
        called.update(command=command, target=target, limits=limits, kwargs=kwargs)
        return {'state': 'complete'}

    monkeypatch.setattr(local_run, 'supervise_command', fake_supervise)
    monkeypatch.setattr(local_run.sys, 'argv', [
        'local_run', '--features', str(tmp_path / 'features'),
        '--labels', str(tmp_path / 'labels'), '--protocol', str(tmp_path / 'protocol'),
        '--protocol-sha256', 'protocol', '--output', str(output),
        '--root', str(tmp_path), '--preflight-only',
    ])

    local_run.main()

    assert '--preflight-only' in called['command']
    assert called['kwargs']['report_name'] == 'preflight.json'
    assert called['target'] == output
    assert capsys.readouterr().out.strip() == '{"state": "complete"}'
