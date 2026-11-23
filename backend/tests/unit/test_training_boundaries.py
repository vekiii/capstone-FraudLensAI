"""Synthetic RED contracts for training preparation (T220).

T223 supplies ``fraudlens.training.boundaries.prepare_training_views``. It
accepts feature-only rows grouped as train/validation/test/showcase and a
``label_reader(partition, transaction_ids)`` callback. The result exposes a
fitted ``preprocessor`` with ``currency_vocabulary`` and
``format_vocabulary`` tuples, plus ``train``, ``validation``, ``test`` and
``showcase`` views. Each view exposes ``features``; only train/validation
views expose ``labels``. No estimator fit or real data is involved here.
"""

import importlib

import pytest

from fraudlens.data.features import FEATURE_ORDER


def training_boundary():
    try:
        module = importlib.import_module('fraudlens.training.boundaries')
    except ModuleNotFoundError as error:
        if error.name != 'fraudlens.training.boundaries':
            raise
        pytest.fail('Missing Feature 002 training preparation boundary (T223)', pytrace=False)
    assert callable(getattr(module, 'prepare_training_views', None)), (
        'Missing prepare_training_views boundary'
    )
    return module.prepare_training_views


def row(identity, currency, payment_format, *, paid='1.25', received='2.50'):
    return {
        'transaction_id': identity,
        'sender_out_count_24h': 1,
        'sender_distinct_receivers_24h': 1,
        'sender_paid_count_same_currency_24h': 1,
        'sender_paid_sum_same_currency_24h': paid,
        'receiver_in_count_24h': 2,
        'receiver_distinct_senders_24h': 1,
        'receiver_received_count_same_currency_24h': 2,
        'receiver_received_sum_same_currency_24h': received,
        'current_amount_paid_log1p': 0.81,
        'current_payment_currency': currency,
        'current_payment_format': payment_format,
    }


def partitions():
    return {
        'train': (row('train-z', 'USD', 'Wire'), row('train-a', 'EUR', 'ACH')),
        'validation': (row('valid', 'GBP', 'Cash'),),
        'test': (row('test', 'JPY', 'Card'),),
        'showcase': (row('showcase', 'CAD', 'Cheque'),),
    }


class GuardedLabels:
    """Record each request and fail immediately if sealed labels are touched."""

    def __init__(self):
        self.calls = []

    def __call__(self, partition, transaction_ids):
        ids = tuple(transaction_ids)
        self.calls.append((partition, ids))
        if partition not in {'train', 'validation'}:
            raise AssertionError(f'{partition} record labels must remain unread')
        return tuple(int(identity == 'train-z' or identity == 'valid') for identity in ids)


def prepared(rows=None, labels=None):
    labels = labels or GuardedLabels()
    result = training_boundary()(rows or partitions(), label_reader=labels)
    return result, labels


def test_only_train_and_validation_labels_are_requested():
    result, labels = prepared()

    assert labels.calls == [
        ('train', ('train-z', 'train-a')),
        ('validation', ('valid',)),
    ]
    assert result.train.labels == (1, 0)
    assert result.validation.labels == (1,)
    assert not hasattr(result.test, 'labels')
    assert not hasattr(result.showcase, 'labels')


def test_vocabularies_fit_only_scoreable_training_rows():
    result, _ = prepared()

    assert result.preprocessor.currency_vocabulary == ('EUR', 'USD', '__UNKNOWN__')
    assert result.preprocessor.format_vocabulary == ('ACH', 'Wire', '__UNKNOWN__')
    assert 'GBP' not in result.preprocessor.currency_vocabulary
    assert 'JPY' not in result.preprocessor.currency_vocabulary
    assert 'CAD' not in result.preprocessor.currency_vocabulary
    assert 'Cash' not in result.preprocessor.format_vocabulary
    assert 'Card' not in result.preprocessor.format_vocabulary
    assert 'Cheque' not in result.preprocessor.format_vocabulary


def test_sealed_partition_category_changes_do_not_refit_preprocessor():
    original, _ = prepared()
    changed = partitions()
    changed['test'] = (row('test', 'ZZZ', 'Other'),)
    changed['showcase'] = (row('showcase', 'AAA', 'New'),)
    revised, _ = prepared(changed)

    assert revised.preprocessor.currency_vocabulary == original.preprocessor.currency_vocabulary
    assert revised.preprocessor.format_vocabulary == original.preprocessor.format_vocabulary
    assert revised.train.features == original.train.features
    assert revised.validation.features == original.validation.features


def test_unseen_validation_test_and_showcase_categories_use_unknown_bucket():
    result, _ = prepared()
    for field in ('current_payment_currency', 'current_payment_format'):
        unknown_values = [
            view.features[0][field]
            for view in (result.validation, result.test, result.showcase)
        ]
        assert unknown_values[0] == unknown_values[1] == unknown_values[2]
        assert all(
            encoded[field] != unknown_values[0]
            for encoded in result.train.features
        )


def test_feature_order_excludes_identity_and_label():
    result, _ = prepared()
    for view in (result.train, result.validation, result.test, result.showcase):
        assert tuple(view.features[0]) == FEATURE_ORDER
        assert 'transaction_id' not in view.features[0]
        assert 'is_laundering' not in view.features[0]


@pytest.mark.parametrize('field', ['current_payment_currency', 'current_payment_format'])
@pytest.mark.parametrize('value', ['', '__UNKNOWN__'])
def test_invalid_or_reserved_training_categories_are_rejected(field, value):
    rows = partitions()
    bad_train = dict(rows['train'][0], **{field: value})
    rows['train'] = (bad_train, rows['train'][1])

    with pytest.raises(ValueError):
        prepared(rows)


def test_label_in_feature_input_is_rejected_before_any_label_read():
    rows = partitions()
    rows['test'] = (dict(rows['test'][0], is_laundering=1),)
    labels = GuardedLabels()

    with pytest.raises(ValueError):
        prepared(rows, labels)
    assert labels.calls == []
