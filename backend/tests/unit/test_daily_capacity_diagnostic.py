"""Pure daily-cap selection boundaries independent of run publication."""

from datetime import UTC, datetime

import pytest

from fraudlens.daily_capacity_diagnostic import select_daily_threshold_alerts


def alert(number, at, score='0.9'):
    return {'transaction_id': f'D{number:032x}', 'event_time': at, 'score': score}


def test_utc_day_edges_are_separate():
    first = alert(1, '2022-09-02T23:59:00Z')
    second = alert(2, '2022-09-03T00:00:00Z')
    kept, dropped = select_daily_threshold_alerts([second, first], '0.8', limit=1)
    assert [row['transaction_id'] for row in kept] == [first['transaction_id'],
                                                        second['transaction_id']]
    assert dropped == []


def test_equal_scores_use_ascending_stable_id_and_overflow_is_dropped():
    rows = [alert(i, '2022-09-02T12:00:00Z') for i in range(25, 0, -1)]
    kept, dropped = select_daily_threshold_alerts(rows, '0.8')
    assert [row['transaction_id'] for row in kept] == [alert(i, '', '')['transaction_id']
                                                        for i in range(1, 21)]
    assert [row['transaction_id'] for row in dropped] == [alert(i, '', '')['transaction_id']
                                                           for i in range(21, 26)]


def test_higher_score_wins_and_threshold_is_inclusive():
    rows = [alert(1, '2022-09-02T12:00:00Z', '0.8'),
            alert(2, '2022-09-02T12:01:00Z', '0.9'),
            alert(3, '2022-09-02T12:02:00Z', '0.7')]
    kept, dropped = select_daily_threshold_alerts(rows, '0.8', limit=1)
    assert [row['transaction_id'] for row in kept] == [rows[1]['transaction_id']]
    assert dropped == [rows[0]]


@pytest.mark.parametrize('bad_time', [
    '2022-09-02T12:00:00', '2022-09-02T13:00:00+01:00', 'not-a-time',
])
def test_ambiguous_or_non_utc_time_rejected(bad_time):
    with pytest.raises(ValueError, match='UTC'):
        select_daily_threshold_alerts([alert(1, bad_time)], '0.8')


def test_duplicate_id_and_nonfinite_score_rejected():
    row = alert(1, datetime(2022, 9, 2, tzinfo=UTC).isoformat())
    with pytest.raises(ValueError, match='duplicate'):
        select_daily_threshold_alerts([row, row], '0.8')
    with pytest.raises(ValueError, match='score'):
        select_daily_threshold_alerts([alert(1, '2022-09-02T00:00:00Z', 'NaN')],
                                      '0.8')
