"""IBM-style chronological day split for the scoreable HI-Small rows.

This versioned experiment split keeps complete UTC dates together and chooses
two boundaries by the maximum relative error from the declared 60/20/20 row
targets, following IBM Multi-GNN's AML day-split approach. It never reads labels.
"""

from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime, timezone

from fraudlens.data.features import normalize_timestamp_utc

_TARGETS = (0.60, 0.20, 0.20)


@dataclass(frozen=True, slots=True)
class ResearchSplit:
    train_ids: tuple[str, ...]
    validation_ids: tuple[str, ...]
    test_ids: tuple[str, ...]
    train_end_utc: date
    validation_end_utc: date
    daily_counts: tuple[tuple[date, int], ...]

    @property
    def counts(self) -> dict[str, int]:
        return {
            'train': len(self.train_ids),
            'validation': len(self.validation_ids),
            'test': len(self.test_ids),
        }


def _row_time(row: Mapping[str, object]) -> datetime:
    if not isinstance(row, Mapping):
        raise ValueError('research split rows must be mappings')
    value = row.get('occurred_at_utc', row.get('timestamp'))
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError('research split datetime must be timezone-aware')
        return value.astimezone(timezone.utc)
    return normalize_timestamp_utc(value)


def plan_ibm_day_split(rows: Iterable[Mapping[str, object]]) -> ResearchSplit:
    """Return deterministic, nonempty, whole-UTC-day 60/20/20 partitions.

    For every pair of day boundaries, minimize the largest relative deviation
    from the target shares. Exact ties use the earlier train then validation
    boundary, matching the source implementation's stable enumeration order.
    """
    grouped: dict[date, list[tuple[datetime, int, str]]] = defaultdict(list)
    seen: set[str] = set()
    for ordinal, row in enumerate(rows):
        instant = _row_time(row)
        identity = row.get('transaction_id')
        if not isinstance(identity, str) or not identity.strip() or identity in seen:
            raise ValueError('research split identities must be unique nonempty text')
        seen.add(identity)
        grouped[instant.date()].append((instant, ordinal, identity))
    days = sorted(grouped)
    if len(days) < 3:
        raise ValueError('60/20/20 split requires at least three UTC dates')
    daily_counts = [len(grouped[day]) for day in days]
    total = sum(daily_counts)
    prefix = [0]
    for count in daily_counts:
        prefix.append(prefix[-1] + count)
    best_key = None
    best_pair = None
    for train_end in range(1, len(days) - 1):
        train_count = prefix[train_end]
        for validation_end in range(train_end + 1, len(days)):
            validation_count = prefix[validation_end] - train_count
            test_count = total - prefix[validation_end]
            proportions = (train_count / total, validation_count / total, test_count / total)
            errors = tuple(abs(actual - target) / target
                           for actual, target in zip(proportions, _TARGETS, strict=True))
            key = (max(errors), train_end, validation_end)
            if best_key is None or key < best_key:
                best_key, best_pair = key, (train_end, validation_end)
    assert best_pair is not None
    train_end, validation_end = best_pair

    def ordered_ids(selected_days: list[date]) -> tuple[str, ...]:
        return tuple(
            identity
            for day in selected_days
            for _, _, identity in sorted(grouped[day], key=lambda item: (item[0], item[1]))
        )

    return ResearchSplit(
        train_ids=ordered_ids(days[:train_end]),
        validation_ids=ordered_ids(days[train_end:validation_end]),
        test_ids=ordered_ids(days[validation_end:]),
        train_end_utc=days[train_end - 1],
        validation_end_utc=days[validation_end - 1],
        daily_counts=tuple(zip(days, daily_counts, strict=True)),
    )
