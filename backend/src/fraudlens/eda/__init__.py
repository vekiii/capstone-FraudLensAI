"""Bounded, label-free, server-side synthetic dataset aggregates."""

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from math import ceil, isfinite
from typing import Any

from fraudlens.contracts import EdaSeries, EdaSummary
from fraudlens.data.features import normalize_timestamp_utc

_CATEGORIES = (
    ('sender_bank', 'Sender bank'),
    ('receiver_bank', 'Receiver bank'),
    ('payment_currency', 'Payment currency'),
    ('receiving_currency', 'Receiving currency'),
    ('payment_format', 'Payment format'),
)
_MAX_CATEGORIES = 20
_MAX_AMOUNT_CURRENCIES = 12
_MAX_POINTS = 366
_LABEL_KEYS = frozenset({'is_laundering', 'label', 'target', 'ground_truth'})
_FORBIDDEN_QUALITY_PARTS = ('label', 'launder', 'target', 'positive', 'negative', 'fraud')


def _utc(value: Any) -> str:
    return value.strftime('%Y-%m-%dT%H:%M:%SZ')


def _amount(value: object) -> Decimal:
    if not isinstance(value, str):
        raise ValueError('EDA amount must be decimal text')
    try:
        amount = Decimal(value)
    except InvalidOperation:
        raise ValueError('EDA amount must be decimal text') from None
    if not amount.is_finite() or amount < 0:
        raise ValueError('EDA amount must be finite and nonnegative')
    return amount


def _category_series(name: str, label: str, counts: Counter[str], total: int) -> EdaSeries:
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    shown = ordered[:_MAX_CATEGORIES - 1] if len(ordered) > _MAX_CATEGORIES else ordered
    hidden = total - sum(count for _, count in shown)
    if hidden:
        shown.append(('__OTHER__', hidden))
    return EdaSeries(
        series_id=f'{name}_count', label=label, unit='transactions',
        bucket_labels=[key for key, _ in shown], values=[float(count) for _, count in shown],
        denominator=total,
    )


def _time_bins(days: set[date]) -> tuple[date | None, int]:
    if not days:
        return None, 1
    first, last = min(days), max(days)
    width = max(1, ceil(((last - first).days + 1) / _MAX_POINTS))
    return first, width


def _bucket(day: date, first: date, width: int) -> date:
    return first + timedelta(days=((day - first).days // width) * width)


def _day_label(day: date, width: int) -> str:
    if width == 1:
        return day.isoformat()
    return f'{day.isoformat()}..{(day + timedelta(days=width - 1)).isoformat()}'


def aggregate_eda(
    rows: Iterable[Mapping[str, object]], *, dataset_version: str,
    source_sha256: str, source_count: int, rejected_count: int,
    warmup_count: int, quality_counts: Mapping[str, int] | None = None,
) -> EdaSummary:
    """Consume already verified label-free canonical facts without retaining rows.

    The caller must verify the source/snapshot before iterating. A label-bearing
    row is rejected even though no label value is ever used by this function.
    """
    if any(isinstance(value, bool) or not isinstance(value, int) or value < 0
           for value in (source_count, rejected_count, warmup_count)):
        raise ValueError('EDA source and quality counts must be nonnegative integers')
    if quality_counts is None:
        quality_counts = {}
    if len(quality_counts) > 20 or any(
        not isinstance(key, str) or not key or len(key) > 80
        or any(part in key.lower() for part in _FORBIDDEN_QUALITY_PARTS)
        or isinstance(value, bool) or not isinstance(value, int) or value < 0
        for key, value in quality_counts.items()
    ):
        raise ValueError('EDA quality counts are invalid or label-bearing')
    category_counts: dict[str, Counter[str]] = {name: Counter() for name, _ in _CATEGORIES}
    day_counts: Counter[date] = Counter()
    amount_sums: dict[tuple[str, str], dict[date, Decimal]] = defaultdict(dict)
    amount_counts: Counter[tuple[str, str]] = Counter()
    first_instant = None
    last_instant = None
    accepted = 0
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError('EDA row must be a mapping')
        if any(str(key).lower() in _LABEL_KEYS for key in row):
            raise ValueError('label-bearing EDA row is forbidden')
        instant = normalize_timestamp_utc(row.get('timestamp'))
        first_instant = instant if first_instant is None else min(first_instant, instant)
        last_instant = instant if last_instant is None else max(last_instant, instant)
        day = instant.date()
        day_counts[day] += 1
        for name, _ in _CATEGORIES:
            value = row.get(name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError('EDA category must be nonempty text')
            category_counts[name][value] += 1
        for side, currency_name, amount_name in (
            ('paid', 'payment_currency', 'amount_paid'),
            ('received', 'receiving_currency', 'amount_received'),
        ):
            key = (side, row[currency_name])
            value = _amount(row.get(amount_name))
            amount_sums[key][day] = amount_sums[key].get(day, Decimal(0)) + value
            amount_counts[key] += 1
        accepted += 1
    if accepted + rejected_count != source_count or warmup_count > accepted:
        raise ValueError('EDA source and quality counts do not reconcile')

    series: list[EdaSeries] = [
        _category_series(name, label, category_counts[name], accepted)
        for name, label in _CATEGORIES
    ]
    first_day, width = _time_bins(set(day_counts))
    if first_day is not None:
        bucket_counts: Counter[date] = Counter()
        for day, count in day_counts.items():
            bucket_counts[_bucket(day, first_day, width)] += count
        ordered_days = sorted(bucket_counts)
        series.append(EdaSeries(
            series_id='utc_transaction_count', label='Transactions by UTC day',
            unit='transactions', timezone='UTC',
            bucket_labels=[_day_label(day, width) for day in ordered_days],
            values=[float(bucket_counts[day]) for day in ordered_days],
            denominator=accepted,
        ))
    else:
        series.append(EdaSeries(
            series_id='utc_transaction_count', label='Transactions by UTC day',
            unit='transactions', timezone='UTC', bucket_labels=[], values=[],
            denominator=0,
        ))
    selected = sorted(amount_counts, key=lambda key: (-amount_counts[key], key))
    selected = [key for key in selected if key[0] == 'paid'][:_MAX_AMOUNT_CURRENCIES] + [
        key for key in selected if key[0] == 'received'
    ][:_MAX_AMOUNT_CURRENCIES]
    omitted = {
        side: max(0, sum(key[0] == side for key in amount_counts)
                  - _MAX_AMOUNT_CURRENCIES)
        for side in ('paid', 'received')
    }
    for side, currency in selected:
        daily = amount_sums[(side, currency)]
        assert first_day is not None
        bins: dict[date, Decimal] = defaultdict(Decimal)
        for day, value in daily.items():
            bins[_bucket(day, first_day, width)] += value
        ordered_days = sorted(bins)
        values = [float(bins[day]) for day in ordered_days]
        if not all(isfinite(value) for value in values):
            raise ValueError('EDA amount total is nonfinite')
        series.append(EdaSeries(
            series_id=f'{side}_amount_{currency}', label=f'{side.title()} amount: {currency}',
            unit='amount', side=side, currency=currency, timezone='UTC',
            bucket_labels=[_day_label(day, width) for day in ordered_days],
            values=values, denominator=amount_counts[(side, currency)],
        ))
    return EdaSummary(
        dataset_version=dataset_version, source_sha256=source_sha256,
        synthetic_data=True,
        coverage_start_utc=_utc(first_instant) if first_instant else None,
        coverage_end_utc=_utc(last_instant) if last_instant else None,
        source_count=source_count, accepted_count=accepted,
        rejected_count=rejected_count, warmup_count=warmup_count,
        scoreable_count=accepted - warmup_count,
        quality_counts=dict(quality_counts), omitted_amount_currencies=omitted,
        series=series,
    )
