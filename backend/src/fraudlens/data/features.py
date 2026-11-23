"""Label-free, strict-prior temporal features for ``hi-small-temporal-v1``.

``iter_temporal_features_ordered`` accepts an already chronological stream and
keeps only the preceding 24 hours plus one timestamp group in its rolling
state. ``build_temporal_features`` sorts a finite synthetic batch for tests;
it is not the external-sort / real-source publication pipeline.
"""

import math
import re
from collections import Counter, deque
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal, Inexact, Rounded, localcontext
from itertools import groupby
from typing import Any

FEATURE_VERSION = 'hi-small-temporal-v1'
HISTORY_FEATURE_ORDER = (
    'sender_out_count_24h',
    'sender_distinct_receivers_24h',
    'sender_paid_count_same_currency_24h',
    'sender_paid_sum_same_currency_24h',
    'receiver_in_count_24h',
    'receiver_distinct_senders_24h',
    'receiver_received_count_same_currency_24h',
    'receiver_received_sum_same_currency_24h',
)
CURRENT_FEATURE_ORDER = (
    'current_amount_paid_log1p',
    'current_payment_currency',
    'current_payment_format',
)
FEATURE_ORDER = HISTORY_FEATURE_ORDER + CURRENT_FEATURE_ORDER

_NAIVE_TIMESTAMP = re.compile(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}\Z')
_OFFSET_TIMESTAMP = re.compile(
    r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?'
    r'(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)\Z',
)
_AMOUNT = re.compile(r'[0-9]{1,13}(?:\.[0-9]{1,6})?\Z')
_WINDOW = timedelta(hours=24)
_ZERO = Decimal(0)
_RESERVED_CATEGORY = '__UNKNOWN__'
_REQUIRED_TEXT = (
    'transaction_id',
    'sender_bank',
    'sender_account',
    'receiver_bank',
    'receiver_account',
    'payment_currency',
    'receiving_currency',
    'payment_format',
)


def normalize_timestamp_utc(value: str) -> datetime:
    """Interpret source-naive minutes as UTC; normalize explicit ISO offsets."""
    if not isinstance(value, str):
        raise ValueError('timestamp must be valid text')
    try:
        if _NAIVE_TIMESTAMP.fullmatch(value):
            return datetime.strptime(value, '%Y/%m/%d %H:%M').replace(tzinfo=timezone.utc)
        if _OFFSET_TIMESTAMP.fullmatch(value):
            parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return parsed.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        pass
    raise ValueError('timestamp must be a valid source minute or explicit-offset instant')


def _amount(value: object, field_name: str) -> Decimal:
    if not isinstance(value, str) or _AMOUNT.fullmatch(value) is None:
        raise ValueError(f'{field_name} must be nonnegative decimal text at source precision')
    amount = Decimal(value)
    if not amount.is_finite() or amount < 0:
        raise ValueError(f'{field_name} must be finite and nonnegative')
    return amount


def _exact(operation: str, left: Decimal, right: Decimal) -> Decimal:
    with localcontext() as context:
        context.prec = 38
        context.traps[Inexact] = True
        context.traps[Rounded] = True
        try:
            return left + right if operation == 'add' else left - right
        except (Inexact, Rounded):
            raise ValueError('historical Decimal precision exceeded frozen policy') from None


@dataclass(frozen=True, slots=True)
class _Event:
    source_row_number: int
    transaction_id: str
    timestamp_text: str
    occurred_at_utc: datetime
    sender_key: tuple[str, str]
    receiver_key: tuple[str, str]
    amount_paid: Decimal
    payment_currency: str
    amount_received: Decimal
    receiving_currency: str
    payment_format: str


def _event(row: Mapping[str, object]) -> _Event:
    if not isinstance(row, Mapping):
        raise ValueError('feature input must be a mapping')
    number = row.get('source_row_number')
    if isinstance(number, bool) or not isinstance(number, int) or number < 1:
        raise ValueError('source_row_number must be a positive integer')
    for name in _REQUIRED_TEXT:
        value = row.get(name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'{name} must be nonempty text')
    for name in ('payment_currency', 'payment_format'):
        if row[name] == _RESERVED_CATEGORY:
            raise ValueError(f'{name} collides with the reserved unknown bucket')
    return _Event(
        source_row_number=number,
        transaction_id=row['transaction_id'],
        timestamp_text=row.get('timestamp'),
        occurred_at_utc=normalize_timestamp_utc(row.get('timestamp')),
        sender_key=(row['sender_bank'], row['sender_account']),
        receiver_key=(row['receiver_bank'], row['receiver_account']),
        amount_paid=_amount(row.get('amount_paid'), 'amount_paid'),
        payment_currency=row['payment_currency'],
        amount_received=_amount(row.get('amount_received'), 'amount_received'),
        receiving_currency=row['receiving_currency'],
        payment_format=row['payment_format'],
    )


@dataclass(slots=True)
class _AccountState:
    count: int = 0
    counterparties: Counter[tuple[str, str]] = field(default_factory=Counter)
    currency_counts: Counter[str] = field(default_factory=Counter)
    currency_sums: dict[str, Decimal] = field(default_factory=dict)

    def add(self, counterparty: tuple[str, str], currency: str, amount: Decimal) -> None:
        self.count += 1
        self.counterparties[counterparty] += 1
        self.currency_counts[currency] += 1
        self.currency_sums[currency] = _exact(
            'add', self.currency_sums.get(currency, _ZERO), amount,
        )

    def remove(self, counterparty: tuple[str, str], currency: str, amount: Decimal) -> None:
        self.count -= 1
        self.counterparties[counterparty] -= 1
        if self.counterparties[counterparty] == 0:
            del self.counterparties[counterparty]
        self.currency_counts[currency] -= 1
        remainder = _exact('subtract', self.currency_sums[currency], amount)
        if self.currency_counts[currency] == 0:
            del self.currency_counts[currency]
            del self.currency_sums[currency]
        else:
            self.currency_sums[currency] = remainder


def _history(
    event: _Event,
    sender: _AccountState | None,
    receiver: _AccountState | None,
) -> dict[str, int | Decimal]:
    return {
        'sender_out_count_24h': sender.count if sender else 0,
        'sender_distinct_receivers_24h': len(sender.counterparties) if sender else 0,
        'sender_paid_count_same_currency_24h': (
            sender.currency_counts[event.payment_currency] if sender else 0
        ),
        'sender_paid_sum_same_currency_24h': (
            sender.currency_sums.get(event.payment_currency, _ZERO) if sender else _ZERO
        ),
        'receiver_in_count_24h': receiver.count if receiver else 0,
        'receiver_distinct_senders_24h': len(receiver.counterparties) if receiver else 0,
        'receiver_received_count_same_currency_24h': (
            receiver.currency_counts[event.receiving_currency] if receiver else 0
        ),
        'receiver_received_sum_same_currency_24h': (
            receiver.currency_sums.get(event.receiving_currency, _ZERO) if receiver else _ZERO
        ),
    }


def _current(event: _Event) -> dict[str, float | str]:
    value = math.log1p(float(event.amount_paid))
    if not math.isfinite(value):
        raise ValueError('current_amount_paid_log1p is not finite')
    return {
        'current_amount_paid_log1p': value,
        'current_payment_currency': event.payment_currency,
        'current_payment_format': event.payment_format,
    }


def _features(events: Iterable[_Event]) -> Iterator[dict[str, Any]]:
    sender_state: dict[tuple[str, str], _AccountState] = {}
    receiver_state: dict[tuple[str, str], _AccountState] = {}
    active: deque[_Event] = deque()
    first_instant: datetime | None = None
    previous_key: tuple[datetime, int] | None = None

    for instant, grouped in groupby(events, key=lambda event: event.occurred_at_utc):
        group = list(grouped)
        for event in group:
            key = (event.occurred_at_utc, event.source_row_number)
            if previous_key is not None and key <= previous_key:
                raise ValueError('rows must have strictly increasing UTC/source-row order')
            previous_key = key
        if first_instant is None:
            first_instant = instant
        cutoff = instant - _WINDOW
        while active and active[0].occurred_at_utc < cutoff:
            old = active.popleft()
            sending = sender_state[old.sender_key]
            receiving = receiver_state[old.receiver_key]
            sending.remove(old.receiver_key, old.payment_currency, old.amount_paid)
            receiving.remove(old.sender_key, old.receiving_currency, old.amount_received)
            if sending.count == 0:
                del sender_state[old.sender_key]
            if receiving.count == 0:
                del receiver_state[old.receiver_key]

        # Phase one: freeze every same-instant output before adding its peers.
        outputs = []
        for event in group:
            history = _history(
                event,
                sender_state.get(event.sender_key),
                receiver_state.get(event.receiver_key),
            )
            current = _current(event)
            outputs.append({
                'source_row_number': event.source_row_number,
                'transaction_id': event.transaction_id,
                'timestamp': event.timestamp_text,
                'occurred_at_utc': instant,
                'is_scoreable': instant >= first_instant + _WINDOW,
                'feature_version': FEATURE_VERSION,
                'history': history,
                'current': current,
                'features': {**history, **current},
            })

        # Phase two: add the complete instant to the rolling 24-hour state.
        for event in group:
            sender_state.setdefault(event.sender_key, _AccountState()).add(
                event.receiver_key, event.payment_currency, event.amount_paid,
            )
            receiver_state.setdefault(event.receiver_key, _AccountState()).add(
                event.sender_key, event.receiving_currency, event.amount_received,
            )
            active.append(event)
        yield from outputs


def iter_temporal_features_ordered(
    rows: Iterable[Mapping[str, object]],
) -> Iterator[dict[str, Any]]:
    """Compute features from already sorted rows with a rolling 24-hour state.

    The caller owns external sorting/checkpointing for large datasets. This
    function rejects out-of-order input; it never reads labels from mappings.
    """
    return _features(_event(row) for row in rows)


def build_temporal_features(
    rows: Iterable[Mapping[str, object]],
) -> Iterator[dict[str, Any]]:
    """Sort one finite synthetic batch, then apply the same streaming kernel.

    This helper materializes and sorts input. Do not use it for the full source;
    the measured external chronological pass is a separate later gate.
    """
    prepared = [_event(row) for row in rows]
    prepared.sort(key=lambda event: (event.occurred_at_utc, event.source_row_number))
    numbers = [event.source_row_number for event in prepared]
    if len(set(numbers)) != len(numbers):
        raise ValueError('source_row_number must be unique')
    return _features(prepared)
