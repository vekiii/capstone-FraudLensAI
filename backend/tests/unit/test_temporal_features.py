"""Synthetic RED contracts for strict-prior temporal features (T211).

T213 supplies ``normalize_timestamp_utc(text)`` and
``build_temporal_features(rows)``. The latter returns rows ordered by UTC instant
then source row number, each with ``source_row_number``, ``occurred_at_utc``
(aware UTC datetime), ``is_scoreable`` and ``history`` (the eight FR-011 fields).
The input is fabricated, label-free canonical transaction data.
"""

import importlib
from datetime import datetime, timezone
from decimal import Decimal

import pytest

HISTORY_FIELDS = (
    'sender_out_count_24h',
    'sender_distinct_receivers_24h',
    'sender_paid_count_same_currency_24h',
    'sender_paid_sum_same_currency_24h',
    'receiver_in_count_24h',
    'receiver_distinct_senders_24h',
    'receiver_received_count_same_currency_24h',
    'receiver_received_sum_same_currency_24h',
)


def feature_module():
    """Collect all cases and fail at the intended missing T213 boundary."""
    try:
        module = importlib.import_module('fraudlens.data.features')
    except ModuleNotFoundError as error:
        if error.name != 'fraudlens.data.features':
            raise
        pytest.fail('Missing Feature 002 temporal feature builder (T213)', pytrace=False)
    assert callable(getattr(module, 'normalize_timestamp_utc', None))
    assert callable(getattr(module, 'build_temporal_features', None))
    return module


def row(number, timestamp, **changes):
    """A minimal accepted, label-free transaction with exact source text."""
    return {
        'source_row_number': number,
        'transaction_id': f'synthetic-{number}',
        'timestamp': timestamp,
        'sender_bank': 'S1',
        'sender_account': '001',
        'receiver_bank': 'R1',
        'receiver_account': '002',
        'amount_paid': '10.00',
        'payment_currency': 'USD',
        'amount_received': '9.00',
        'receiving_currency': 'EUR',
        'payment_format': 'Wire',
        **changes,
    }


def built(rows):
    result = list(feature_module().build_temporal_features(rows))
    assert len(result) == len(rows)
    assert result == sorted(
        result,
        key=lambda item: (item['occurred_at_utc'], item['source_row_number']),
    )
    assert all(item['occurred_at_utc'].tzinfo == timezone.utc for item in result)
    assert all(tuple(item['history']) == HISTORY_FIELDS for item in result)
    return {item['source_row_number']: item for item in result}


def history(result, number):
    return result[number]['history']


def test_naive_utc_and_explicit_offsets_normalize_to_same_aware_instant():
    normalize = feature_module().normalize_timestamp_utc
    expected = datetime(2022, 9, 1, 12, 0, tzinfo=timezone.utc)
    assert normalize('2022/09/01 12:00') == expected
    assert normalize('2022-09-01T14:00:00+02:00') == expected
    assert normalize('2022-09-01T07:00:00-05:00') == expected
    assert normalize('2022-09-01T12:00:00Z') == expected
    assert normalize('2022-09-01T12:00:01Z') < normalize('2022-09-01T12:00:02Z')


def test_timestamp_ties_are_indivisible_and_output_uses_stable_source_order():
    rows = [
        row(3, '2022/09/01 00:01'),
        row(2, '2022-09-01T02:00:00+02:00', amount_paid='20.00'),
        row(1, '2022/09/01 00:00'),
    ]
    output = list(feature_module().build_temporal_features(rows))
    assert [item['source_row_number'] for item in output] == [1, 2, 3]
    assert history({item['source_row_number']: item for item in output}, 1)['sender_out_count_24h'] == 0
    assert history({item['source_row_number']: item for item in output}, 2)['sender_out_count_24h'] == 0
    assert output[2]['history']['sender_out_count_24h'] == 2
    assert output[2]['history']['sender_paid_sum_same_currency_24h'] == Decimal('30.00')


def test_current_event_and_same_instant_events_never_enter_history():
    result = built([
        row(1, '2022/09/01 00:00'),
        row(2, '2022/09/01 00:01', amount_paid='2.00'),
        row(3, '2022/09/01 00:01', amount_paid='3.00'),
    ])
    assert history(result, 1)['sender_out_count_24h'] == 0
    for number in (2, 3):
        assert history(result, number)['sender_out_count_24h'] == 1
        assert history(result, number)['sender_paid_sum_same_currency_24h'] == Decimal('10.00')


def test_exact_24_hour_lower_edge_excluded_and_newer_event_included():
    result = built([
        row(1, '2022/09/01 00:00', amount_paid='100.00'),
        row(2, '2022/09/01 00:01', amount_paid='7.00'),
        row(3, '2022/09/02 00:00'),
    ])
    assert history(result, 3)['sender_out_count_24h'] == 1
    assert history(result, 3)['sender_paid_sum_same_currency_24h'] == Decimal('7.00')
    assert history(result, 3)['receiver_received_sum_same_currency_24h'] == Decimal('9.00')


def test_paid_and_received_aggregates_use_their_own_currency_columns():
    result = built([
        row(1, '2022/09/01 00:00', amount_paid='1.01', amount_received='2.02'),
        row(2, '2022/09/01 00:01', payment_currency='EUR', receiving_currency='USD',
            amount_paid='100.00', amount_received='200.00'),
        row(3, '2022/09/01 00:02', amount_paid='3.03', amount_received='4.04'),
    ])
    current = history(result, 3)
    assert current['sender_out_count_24h'] == 2
    assert current['sender_paid_count_same_currency_24h'] == 1
    assert current['sender_paid_sum_same_currency_24h'] == Decimal('1.01')
    assert current['receiver_in_count_24h'] == 2
    assert current['receiver_received_count_same_currency_24h'] == 1
    assert current['receiver_received_sum_same_currency_24h'] == Decimal('2.02')


def test_account_identity_and_distinct_counterparties_are_bank_qualified():
    result = built([
        row(1, '2022/09/01 00:00', receiver_bank='R1', receiver_account='007'),
        row(2, '2022/09/01 00:01', receiver_bank='R2', receiver_account='007'),
        row(3, '2022/09/01 00:02', sender_bank='S2', receiver_bank='R1',
            receiver_account='007'),
        row(4, '2022/09/01 00:03', receiver_bank='R1', receiver_account='007'),
    ])
    current = history(result, 4)
    assert current['sender_out_count_24h'] == 2
    assert current['sender_distinct_receivers_24h'] == 2
    assert current['receiver_in_count_24h'] == 2
    assert current['receiver_distinct_senders_24h'] == 2


def test_warmup_is_half_open_and_rows_at_exact_24_hours_are_scoreable():
    result = built([
        row(1, '2022/09/01 00:00'),
        row(2, '2022/09/01 23:59'),
        row(3, '2022/09/02 00:00'),
    ])
    assert [result[number]['is_scoreable'] for number in (1, 2, 3)] == [False, False, True]
    assert history(result, 3)['sender_out_count_24h'] == 1


def test_empty_history_is_zero_and_decimal_sums_are_exact():
    result = built([
        row(1, '2022/09/01 00:00', amount_paid='0.1', amount_received='0.1'),
        row(2, '2022/09/01 00:01', amount_paid='0.2', amount_received='0.2'),
        row(3, '2022/09/01 00:02'),
    ])
    first = history(result, 1)
    assert all(first[field] == 0 for field in HISTORY_FIELDS)
    assert isinstance(first['sender_paid_sum_same_currency_24h'], Decimal)
    assert history(result, 3)['sender_paid_sum_same_currency_24h'] == Decimal('0.3')
    assert history(result, 3)['receiver_received_sum_same_currency_24h'] == Decimal('0.3')


@pytest.mark.parametrize('field', ['timestamp', 'sender_bank', 'payment_currency', 'amount_paid'])
def test_missing_required_feature_input_fails_explicitly(field):
    incomplete = row(1, '2022/09/01 00:00')
    del incomplete[field]
    with pytest.raises(ValueError, match=field):
        list(feature_module().build_temporal_features([incomplete]))
