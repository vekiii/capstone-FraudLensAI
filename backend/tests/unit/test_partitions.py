"""Synthetic RED contracts for warm-up and whole-instant partitions (T214).

T215 supplies ``plan_partitions(rows, *, development_target)``. Inputs contain
stable source-row identity and timestamp text only; labels, if present, must
have no influence. The result exposes ordered ``warmup_ids``, ``scoreable_ids``,
``development_ids``, ``showcase_ids``, ``train_ids``, ``validation_ids`` and
``test_ids`` plus the corresponding count fields. IDs are synthetic strings.
"""

import importlib
from datetime import datetime, timedelta, timezone

import pytest


def partition_module():
    """Collect all cases and fail at the missing T215 module boundary."""
    try:
        module = importlib.import_module('fraudlens.data.partitions')
    except ModuleNotFoundError as error:
        if error.name != 'fraudlens.data.partitions':
            raise
        pytest.fail('Missing Feature 002 partition planner (T215)', pytrace=False)
    assert callable(getattr(module, 'plan_partitions', None)), 'Missing plan_partitions boundary'
    return module


def row(number, minute, *, count=1, spellings=None):
    """Create one or more rows at a UTC minute, with distinct stable IDs."""
    instant = datetime(2022, 9, 1, tzinfo=timezone.utc) + timedelta(minutes=minute)
    return [
        {
            'source_row_number': number + index,
            'transaction_id': f'synthetic-{number + index}',
            'timestamp': (
                spellings[index] if spellings else instant.strftime('%Y/%m/%d %H:%M')
            ),
        }
        for index in range(count)
    ]


def ids(*numbers):
    return tuple(f'synthetic-{number}' for number in numbers)


def planned(rows, *, target):
    plan = partition_module().plan_partitions(rows, development_target=target)
    assert plan.warmup_count == len(plan.warmup_ids)
    assert plan.scoreable_count == len(plan.scoreable_ids)
    assert plan.development_count == len(plan.development_ids)
    assert plan.showcase_count == len(plan.showcase_ids)
    assert plan.train_count == len(plan.train_ids)
    assert plan.validation_count == len(plan.validation_ids)
    assert plan.test_count == len(plan.test_ids)
    assert plan.development_count + plan.showcase_count == len(rows)
    assert plan.warmup_count + plan.scoreable_count == len(rows)
    assert plan.train_count + plan.validation_count + plan.test_count == (
        plan.development_count - plan.warmup_count
    )
    assert set(plan.development_ids).isdisjoint(plan.showcase_ids)
    assert set(plan.train_ids).isdisjoint(plan.validation_ids)
    assert set(plan.train_ids).isdisjoint(plan.test_ids)
    assert set(plan.validation_ids).isdisjoint(plan.test_ids)
    return plan


def test_warmup_is_half_open_and_exact_boundary_group_is_scoreable():
    rows = [
        *row(1, 0),
        *row(2, 1439),
        *row(3, 1440, count=2, spellings=(
            '2022/09/02 00:00', '2022-09-02T02:00:00+02:00',
        )),
        *row(5, 1441),
        *row(6, 1442),
        *row(7, 1443),
        *row(8, 1444),
    ]
    plan = planned(list(reversed(rows)), target=7)

    assert plan.warmup_ids == ids(1, 2)
    assert plan.scoreable_ids == ids(3, 4, 5, 6, 7, 8)
    assert plan.development_ids == ids(1, 2, 3, 4, 5, 6, 7)
    assert plan.showcase_ids == ids(8)
    assert any(
        set(ids(3, 4)) <= set(group)
        for group in (plan.train_ids, plan.validation_ids, plan.test_ids)
    )


def test_development_boundary_uses_source_count_including_warmup_and_earlier_tie():
    rows = [*row(1, 0)]
    rows += [entry for minute in range(1440, 1460) for entry in row(minute - 1438, minute)]
    rows += row(22, 1460, count=2)
    rows += row(24, 1461)
    # The candidate boundaries around target 22 are 21 and 23 source rows.
    plan = planned(rows, target=22)

    assert plan.warmup_ids == ids(1)
    assert plan.development_count == 21
    assert plan.showcase_ids == ids(22, 23, 24)
    assert plan.development_count != 22
    assert all(number not in plan.development_ids for number in ids(22, 23))


def test_development_boundary_chooses_closer_later_whole_group():
    rows = [*row(1, 0)]
    rows += [entry for minute in range(1440, 1460) for entry in row(minute - 1438, minute)]
    rows += row(22, 1460, count=3)
    rows += row(25, 1461)
    # Boundaries 21 and 24 surround target 23; 24 is closer.
    plan = planned(rows, target=23)

    assert plan.development_count == 24
    assert set(ids(22, 23, 24)) <= set(plan.development_ids)
    assert plan.showcase_ids == ids(25)


def test_train_and_validation_boundaries_choose_earlier_equal_distance_group():
    rows = [*row(1, 0)]
    rows += [entry for offset in range(13) for entry in row(offset + 2, 1440 + offset)]
    rows += row(15, 1453, count=2)
    rows += row(17, 1454)
    rows += row(18, 1455, count=2)
    rows += row(20, 1456)
    rows += row(21, 1457)
    rows += row(22, 1458)  # showcase
    # 20 scoreable development rows: 70% target 14 has 13/15 tie;
    # 85% target 17 has 16/18 tie. Both choose the earlier boundary.
    plan = planned(rows, target=21)

    assert plan.train_ids == ids(*range(2, 15))
    assert plan.validation_ids == ids(15, 16, 17)
    assert plan.test_ids == ids(18, 19, 20, 21)
    assert plan.showcase_ids == ids(22)


def test_labels_do_not_change_time_boundaries_or_enter_partition_results():
    rows = [*row(1, 0)]
    rows += [entry for offset in range(8) for entry in row(offset + 2, 1440 + offset)]
    rows += row(10, 1448)
    without_labels = planned(rows, target=9)
    with_labels = planned([
        {**entry, 'is_laundering': str(index % 2)}
        for index, entry in enumerate(reversed(rows))
    ], target=9)

    for field in ('warmup_ids', 'development_ids', 'showcase_ids',
                  'train_ids', 'validation_ids', 'test_ids'):
        assert getattr(with_labels, field) == getattr(without_labels, field)
    assert 'is_laundering' not in repr(with_labels)


def test_impossible_nonempty_train_validation_test_split_fails_closed():
    rows = [
        *row(1, 0),
        *row(2, 1440, count=3),
        *row(5, 1441),
    ]
    with pytest.raises(ValueError, match='nonempty|timestamp|split'):
        partition_module().plan_partitions(rows, development_target=4)
