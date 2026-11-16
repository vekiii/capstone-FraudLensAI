"""Pure UTC daily selection shared by diagnostic and isolated publication."""

from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation


def select_daily_threshold_alerts(rows, threshold, *, limit=20):
    """Select score-desc/ID-asc top rows per UTC date from threshold alerts."""
    if type(limit) is not int or limit < 1:
        raise ValueError('daily limit invalid')
    try:
        boundary = Decimal(str(threshold))
    except InvalidOperation as exc:
        raise ValueError('threshold invalid') from exc
    if not boundary.is_finite() or not 0 <= boundary <= 1:
        raise ValueError('threshold invalid')

    groups = defaultdict(list)
    seen = set()
    for row in rows:
        transaction_id = row['transaction_id']
        if transaction_id in seen:
            raise ValueError('duplicate transaction identity')
        seen.add(transaction_id)
        try:
            at = datetime.fromisoformat(row['event_time'])
        except (TypeError, ValueError) as exc:
            raise ValueError('UTC event time invalid') from exc
        if at.utcoffset() != timedelta(0):
            raise ValueError('UTC event time required')
        try:
            score = Decimal(str(row['score']))
        except InvalidOperation as exc:
            raise ValueError('score invalid') from exc
        if not score.is_finite() or not 0 <= score <= 1:
            raise ValueError('score invalid')
        if score >= boundary:
            groups[at.date()].append((score, transaction_id, row))

    kept, dropped = [], []
    for day in sorted(groups):
        ranked = sorted(groups[day], key=lambda item: (-item[0], item[1]))
        kept.extend(item[2] for item in ranked[:limit])
        dropped.extend(item[2] for item in ranked[limit:])
    return kept, dropped
