"""Synthetic contracts for the IBM-style whole-day 60/20/20 split."""

from datetime import datetime, timedelta, timezone

import pytest

from fraudlens.data.research_split import plan_ibm_day_split


def rows(daily_counts):
    result = []
    ordinal = 0
    start = datetime(2022, 9, 2, tzinfo=timezone.utc)
    for day_offset, count in enumerate(daily_counts):
        for index in range(count):
            ordinal += 1
            result.append({
                'transaction_id': f'id-{ordinal}',
                'occurred_at_utc': start + timedelta(days=day_offset, minutes=index),
            })
    return result


def test_exact_60_20_20_counts_use_complete_chronological_dates():
    result = plan_ibm_day_split(rows([10] * 10))

    assert result.counts == {'train': 60, 'validation': 20, 'test': 20}
    assert result.train_end_utc.isoformat() == '2022-09-07'
    assert result.validation_end_utc.isoformat() == '2022-09-09'
    assert result.train_ids == tuple(f'id-{index}' for index in range(1, 61))
    assert result.validation_ids == tuple(f'id-{index}' for index in range(61, 81))
    assert result.test_ids == tuple(f'id-{index}' for index in range(81, 101))


def test_irregular_day_sizes_choose_global_minimum_relative_error():
    source = rows([4, 12, 7, 19, 5, 11, 8, 16, 6, 13])
    split = plan_ibm_day_split(source)
    repeated = plan_ibm_day_split(reversed(source))

    assert split == repeated
    assert set(split.train_ids).isdisjoint(split.validation_ids)
    assert set(split.train_ids).isdisjoint(split.test_ids)
    assert set(split.validation_ids).isdisjoint(split.test_ids)
    assert sum(split.counts.values()) == len(source)
    assert max(split.counts.values()) == split.counts['train']


def test_label_values_do_not_change_boundaries_or_membership():
    source = rows([10] * 10)
    plain = plan_ibm_day_split(source)
    labeled = plan_ibm_day_split([
        {**item, 'is_laundering': str(index % 2)}
        for index, item in enumerate(source)
    ])

    assert plain == labeled


def test_equal_timestamp_rows_stay_together_and_repeat_in_input_order():
    source = rows([2, 2, 2])
    source[1]['occurred_at_utc'] = source[0]['occurred_at_utc']
    source[3]['occurred_at_utc'] = source[2]['occurred_at_utc']
    result = plan_ibm_day_split(source)

    assert result == plan_ibm_day_split(source)
    assert result.train_ids[:2] == ('id-1', 'id-2')
    assert set(result.train_ids + result.validation_ids + result.test_ids) == {
        item['transaction_id'] for item in source
    }


@pytest.mark.parametrize('source', [[], rows([1, 1]), [
    {'transaction_id': 'same', 'timestamp': '2022/09/02 01:00'},
    {'transaction_id': 'same', 'timestamp': '2022/09/03 01:00'},
    {'transaction_id': 'other', 'timestamp': '2022/09/04 01:00'},
]])
def test_empty_or_duplicate_identity_input_fails_closed(source):
    with pytest.raises(ValueError):
        plan_ibm_day_split(source)
