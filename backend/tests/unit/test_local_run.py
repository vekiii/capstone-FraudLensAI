"""Structural and train-vocabulary tests for the local reader; no estimator fit."""

import json

from fraudlens.data.features import FEATURE_ORDER
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
