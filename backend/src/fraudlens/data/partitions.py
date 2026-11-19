"""Label-free chronological partition planning for finite synthetic batches.

This planner materializes IDs and sorts in memory. A measured external sort and
bounded publication pass are required before applying the policy to real data.
"""

from bisect import bisect_left
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from itertools import groupby

from fraudlens.data.features import normalize_timestamp_utc

DEVELOPMENT_TARGET = 3_000_000
_WARMUP = timedelta(hours=24)


@dataclass(frozen=True, slots=True)
class _Row:
    source_row_number: int
    transaction_id: str
    occurred_at_utc: datetime


@dataclass(frozen=True, slots=True)
class PartitionPlan:
    """Ordered identities and count-only boundaries; never contains labels."""

    warmup_ids: tuple[str, ...]
    scoreable_ids: tuple[str, ...]
    development_ids: tuple[str, ...]
    showcase_ids: tuple[str, ...]
    train_ids: tuple[str, ...]
    validation_ids: tuple[str, ...]
    test_ids: tuple[str, ...]
    t0_utc: datetime
    scoreable_start_utc: datetime
    development_end_utc: datetime
    train_end_utc: datetime
    validation_end_utc: datetime

    @property
    def warmup_count(self) -> int:
        return len(self.warmup_ids)

    @property
    def scoreable_count(self) -> int:
        return len(self.scoreable_ids)

    @property
    def development_count(self) -> int:
        return len(self.development_ids)

    @property
    def showcase_count(self) -> int:
        return len(self.showcase_ids)

    @property
    def train_count(self) -> int:
        return len(self.train_ids)

    @property
    def validation_count(self) -> int:
        return len(self.validation_ids)

    @property
    def test_count(self) -> int:
        return len(self.test_ids)


def _row(value: Mapping[str, object]) -> _Row:
    if not isinstance(value, Mapping):
        raise ValueError('partition input must be a mapping')
    number = value.get('source_row_number')
    identity = value.get('transaction_id')
    if isinstance(number, bool) or not isinstance(number, int) or number < 1:
        raise ValueError('source_row_number must be a positive integer')
    if not isinstance(identity, str) or not identity.strip():
        raise ValueError('transaction_id must be nonempty text')
    return _Row(number, identity, normalize_timestamp_utc(value.get('timestamp')))


def plan_partitions(
    rows: Iterable[Mapping[str, object]],
    *,
    development_target: int = DEVELOPMENT_TARGET,
) -> PartitionPlan:
    """Split by nearest cumulative whole-instant counts, with earlier ties.

    The default target is source rows, including warm-up. Train/validation/test
    targets are 70% and 85% of scoreable development rows. A required nonempty
    partition that cannot be represented by whole instants fails closed.
    """
    if isinstance(development_target, bool) or not isinstance(development_target, int):
        raise ValueError('development_target must be a positive integer')
    if development_target < 1:
        raise ValueError('development_target must be a positive integer')
    prepared = [_row(row) for row in rows]
    if not prepared:
        raise ValueError('cannot partition an empty source')
    prepared.sort(key=lambda row: (row.occurred_at_utc, row.source_row_number))
    if len({row.source_row_number for row in prepared}) != len(prepared):
        raise ValueError('source_row_number must be unique')
    if len({row.transaction_id for row in prepared}) != len(prepared):
        raise ValueError('transaction_id must be unique')

    groups = [tuple(group) for _, group in groupby(
        prepared, key=lambda row: row.occurred_at_utc,
    )]
    if len(groups) < 2:
        raise ValueError('development/showcase split needs separate timestamp groups')
    cumulative = []
    count = 0
    for group in groups:
        count += len(group)
        cumulative.append(count)
    # The showcase must contain at least one complete instant.
    development_count = min(
        cumulative[:-1], key=lambda boundary: (abs(boundary - development_target), boundary),
    )
    development = prepared[:development_count]
    showcase = prepared[development_count:]
    t0 = prepared[0].occurred_at_utc
    scoreable_start = t0 + _WARMUP
    warmup = [row for row in prepared if row.occurred_at_utc < scoreable_start]
    scoreable = [row for row in prepared if row.occurred_at_utc >= scoreable_start]
    if len(warmup) >= development_count:
        raise ValueError('nonempty scoreable development split requires warm-up to end first')
    scoreable_development = development[len(warmup):]
    scoreable_groups = [tuple(group) for _, group in groupby(
        scoreable_development, key=lambda row: row.occurred_at_utc,
    )]
    if len(scoreable_groups) < 3:
        raise ValueError('nonempty train/validation/test split needs three timestamp groups')
    boundaries = []
    count = 0
    for group in scoreable_groups[:-1]:
        count += len(group)
        boundaries.append(count)
    total = len(scoreable_development)
    # Integer distances preserve exact 70%/85% ties without binary floats.
    # For each possible train boundary, only the nearest eligible validation
    # boundaries can win. Avoid a quadratic scan over timestamp groups.
    pairs = []
    scaled_boundaries = [20 * boundary for boundary in boundaries]
    for index, train in enumerate(boundaries[:-1]):
        first_validation = index + 1
        insertion = bisect_left(scaled_boundaries, 17 * total, lo=first_validation)
        for candidate in (insertion - 1, insertion):
            if first_validation <= candidate < len(boundaries):
                pairs.append((train, boundaries[candidate]))
    train_count, validation_end = min(
        pairs,
        key=lambda pair: (
            abs(10 * pair[0] - 7 * total),
            abs(20 * pair[1] - 17 * total),
            pair[0], pair[1],
        ),
    )

    def ids(items: Iterable[_Row]) -> tuple[str, ...]:
        return tuple(row.transaction_id for row in items)

    return PartitionPlan(
        warmup_ids=ids(warmup),
        scoreable_ids=ids(scoreable),
        development_ids=ids(development),
        showcase_ids=ids(showcase),
        train_ids=ids(scoreable_development[:train_count]),
        validation_ids=ids(scoreable_development[train_count:validation_end]),
        test_ids=ids(scoreable_development[validation_end:]),
        t0_utc=t0,
        scoreable_start_utc=scoreable_start,
        development_end_utc=development[-1].occurred_at_utc,
        train_end_utc=scoreable_development[train_count - 1].occurred_at_utc,
        validation_end_utc=scoreable_development[validation_end - 1].occurred_at_utc,
    )
