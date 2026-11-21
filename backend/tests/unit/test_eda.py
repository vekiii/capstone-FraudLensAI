"""T244 synthetic RED contract for bounded, label-free EDA aggregation."""

import importlib
from datetime import datetime, timedelta, timezone

import pytest


def eda_module():
    try:
        module = importlib.import_module('fraudlens.eda')
    except ModuleNotFoundError as error:
        if error.name != 'fraudlens.eda':
            raise
        pytest.fail('Missing Feature 002 EDA aggregate module (T245)', pytrace=False)
    assert callable(getattr(module, 'aggregate_eda', None))
    return module


def row(number, **changes):
    return {
        'source_row_number': number,
        'timestamp': '2022/09/01 00:00',
        'sender_bank': 'S1',
        'receiver_bank': 'R1',
        'amount_paid': '10.00',
        'payment_currency': 'USD',
        'amount_received': '9.00',
        'receiving_currency': 'EUR',
        'payment_format': 'Wire',
        **changes,
    }


def summary(rows, *, source_count=None, rejected_count=0, warmup_count=0):
    rows = list(rows)
    return eda_module().aggregate_eda(
        rows,
        dataset_version='synthetic-v1',
        source_sha256='a' * 64,
        source_count=len(rows) + rejected_count if source_count is None else source_count,
        rejected_count=rejected_count,
        warmup_count=warmup_count,
    ).model_dump(mode='json')


def series_by_id(payload):
    return {series['series_id']: series for series in payload['series']}


def test_counts_and_utc_coverage_reconcile_without_labels():
    payload = summary([
        row(1),
        row(2, timestamp='2022/09/02 00:00', payment_format='ACH'),
        row(3, timestamp='2022/09/02 00:01', sender_bank='S2'),
    ], rejected_count=1, warmup_count=1)
    assert payload['synthetic_data'] is True
    assert payload['source_count'] == 4
    assert payload['accepted_count'] == 3
    assert payload['rejected_count'] == 1
    assert payload['warmup_count'] == 1
    assert payload['scoreable_count'] == 2
    assert payload['coverage_start_utc'] == '2022-09-01T00:00:00Z'
    assert payload['coverage_end_utc'] == '2022-09-02T00:01:00Z'
    assert 'is_laundering' not in str(payload).lower()


def test_every_count_series_has_a_reconciling_denominator():
    payload = summary([
        row(1, payment_format='Wire'),
        row(2, payment_format='ACH', payment_currency='EUR'),
        row(3, payment_format='Wire', payment_currency='EUR'),
    ])
    for item in payload['series']:
        assert len(item['bucket_labels']) == len(item['values'])
        assert len(item['values']) <= 366
        if item['unit'] == 'transactions':
            assert item['denominator'] == payload['accepted_count']
            assert sum(item['values']) == item['denominator']
    formats = series_by_id(payload)['payment_format_count']
    assert dict(zip(formats['bucket_labels'], formats['values'], strict=True)) == {
        'ACH': 1, 'Wire': 2,
    }


def test_currency_amounts_are_separate_by_side_and_unit():
    payload = summary([
        row(1, amount_paid='10.00', payment_currency='USD',
            amount_received='9.00', receiving_currency='EUR'),
        row(2, amount_paid='5.00', payment_currency='USD',
            amount_received='4.00', receiving_currency='GBP'),
        row(3, amount_paid='7.00', payment_currency='EUR',
            amount_received='6.00', receiving_currency='EUR'),
    ])
    amounts = [item for item in payload['series'] if item['unit'] == 'amount']
    assert {(item['side'], item['currency']) for item in amounts} == {
        ('paid', 'USD'), ('paid', 'EUR'), ('received', 'EUR'), ('received', 'GBP'),
    }
    for item in amounts:
        assert item['currency'] in {'USD', 'EUR', 'GBP'}
        assert item['denominator'] in {1, 2}
        assert len(item['values']) == len(item['bucket_labels'])


def test_buckets_and_categories_remain_bounded_for_wide_input():
    base = datetime(2022, 1, 1, tzinfo=timezone.utc)
    rows = [
        row(index + 1, timestamp=(base + timedelta(days=index)).strftime('%Y/%m/%d %H:%M'),
            sender_bank=f'BANK-{index:04d}', payment_format=f'FORMAT-{index:04d}')
        for index in range(400)
    ]
    payload = summary(rows)
    assert len(payload['series']) <= 30
    assert all(len(item['bucket_labels']) <= 366 for item in payload['series'])
    assert len(series_by_id(payload)['payment_format_count']['bucket_labels']) <= 20
    assert all(len(item['bucket_labels']) == len(item['values']) for item in payload['series'])


def test_label_bearing_input_is_refused_before_aggregation():
    with pytest.raises(ValueError, match='label'):
        summary([row(1, is_laundering='1')])
