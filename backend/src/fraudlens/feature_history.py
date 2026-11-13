"""Pure, label-free point-in-time feature replay for history-v1."""

import hashlib
import json
import re
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, fields
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from itertools import groupby
from typing import Iterable

from fraudlens.data_contracts import CanonicalTransaction

FEATURE_VERSION = 'history-v1'
WINDOW = timedelta(hours=24)
_VERSION_ID = re.compile(r'dv_[0-9a-f]{64}\Z')
_EVENT_FIELDS = frozenset(field.name for field in fields(CanonicalTransaction))
_HISTORY_KEYS = (
    'sender_out_count_24h', 'sender_distinct_receivers_24h',
    'sender_paid_count_same_currency_24h', 'sender_paid_sum_same_currency_24h',
    'receiver_in_count_24h', 'receiver_distinct_senders_24h',
    'receiver_received_count_same_currency_24h',
    'receiver_received_sum_same_currency_24h',
)


@dataclass(frozen=True)
class FeatureDefinition:
    source_fields: tuple[str, ...]
    direction: str
    unit: str
    consumers: tuple[str, ...]
    availability: str = 'before_scoring_at_event_time'
    lookback: str = '[t-24h,t)'
    unknown_policy: str = 'not_applicable'
    missing_policy: str = 'null_when_coverage_deficient'
    unsupported_source_policy: str = 'reject_invalid_event'


_CATALOG = {
    'sender_out_count_24h': FeatureDefinition(
        ('sender_bank', 'sender_account', 'event_time_utc'),
        'outgoing', 'events', ('rules', 'model', 'explanation')),
    'sender_distinct_receivers_24h': FeatureDefinition(
        ('sender_bank', 'sender_account', 'receiver_bank', 'receiver_account',
         'event_time_utc'), 'outgoing', 'bank_qualified_counterparties',
        ('model', 'explanation')),
    'sender_paid_count_same_currency_24h': FeatureDefinition(
        ('sender_bank', 'sender_account', 'paid_currency', 'event_time_utc'),
        'outgoing_paid', 'events_in_current_paid_currency',
        ('rules', 'model', 'explanation')),
    'sender_paid_sum_same_currency_24h': FeatureDefinition(
        ('sender_bank', 'sender_account', 'paid_amount', 'paid_currency',
         'event_time_utc'), 'outgoing_paid', 'decimal_in_current_paid_currency',
        ('rules', 'model', 'explanation')),
    'receiver_in_count_24h': FeatureDefinition(
        ('receiver_bank', 'receiver_account', 'event_time_utc'),
        'incoming', 'events', ('rules', 'model', 'explanation')),
    'receiver_distinct_senders_24h': FeatureDefinition(
        ('receiver_bank', 'receiver_account', 'sender_bank', 'sender_account',
         'event_time_utc'), 'incoming', 'bank_qualified_counterparties',
        ('model', 'explanation')),
    'receiver_received_count_same_currency_24h': FeatureDefinition(
        ('receiver_bank', 'receiver_account', 'received_currency', 'event_time_utc'),
        'incoming_received', 'events_in_current_received_currency',
        ('model', 'explanation')),
    'receiver_received_sum_same_currency_24h': FeatureDefinition(
        ('receiver_bank', 'receiver_account', 'received_amount', 'received_currency',
         'event_time_utc'), 'incoming_received', 'decimal_in_current_received_currency',
        ('model', 'explanation')),
    'current_paid_amount': FeatureDefinition(
        ('paid_amount',), 'current_paid', 'decimal_in_current_paid_currency',
        ('rules', 'model', 'explanation'), availability='at_event_observation',
        lookback='current', missing_policy='reject_invalid_event'),
    'current_paid_currency': FeatureDefinition(
        ('paid_currency',), 'current_paid', 'source_currency_name',
        ('rules', 'model', 'explanation'), availability='at_event_observation',
        lookback='current', unknown_policy='frozen_unknown_encoding',
        missing_policy='reject_invalid_event'),
    'current_payment_format': FeatureDefinition(
        ('payment_format',), 'current', 'optional_source_category',
        ('model', 'explanation'), availability='at_event_observation',
        lookback='current', unknown_policy='frozen_unknown_encoding',
        missing_policy='explicit_null',
        unsupported_source_policy='reject_pending_mapping_revision'),
}


def feature_catalog() -> dict[str, FeatureDefinition]:
    """Return a copy of the frozen allowlist and canonical source lineage."""
    return dict(_CATALOG)


def validate_feature_projection(request: dict) -> dict:
    """Fail closed on unapproved predictors, lineage or nested extras."""
    if not isinstance(request, dict) or request.get('feature_version') != FEATURE_VERSION:
        raise ValueError('feature version mismatch')
    if set(request) - {'feature_version', 'predictors', 'join_keys', 'lineage'}:
        raise ValueError('forbidden extra feature request field')
    predictors = request.get('predictors')
    if not isinstance(predictors, dict) or not set(predictors) <= set(_CATALOG):
        raise ValueError('feature allowlist violation')
    if any(isinstance(value, (dict, list, tuple, set)) for value in predictors.values()):
        raise ValueError('nested predictor forbidden')
    joins = request.get('join_keys', {})
    if not isinstance(joins, dict) or set(joins) - {
            'sender_bank', 'sender_account', 'receiver_bank', 'receiver_account'}:
        raise ValueError('forbidden join metadata')
    if any(not isinstance(value, str) or not value for value in joins.values()):
        raise ValueError('forbidden nested join metadata')
    lineage = request.get('lineage', {})
    if not isinstance(lineage, dict) or set(lineage) - set(predictors):
        raise ValueError('forbidden lineage')
    for key, declaration in lineage.items():
        if (not isinstance(declaration, dict)
                or set(declaration) != {'source_fields', 'as_of'}
                or declaration['as_of'] != 't'
                or tuple(declaration['source_fields']) != _CATALOG[key].source_fields):
            raise ValueError('forbidden lineage')
    return dict(predictors)


@dataclass(frozen=True)
class HistoricalFeatureSnapshot:
    transaction_id: str
    dataset_version: str
    feature_version: str
    event_time: datetime
    as_of: datetime
    coverage_start: datetime
    coverage_state: str
    scoreable: bool
    feature_values: dict
    feature_input_digest: str
    created_at: datetime


def _event_fact(event: CanonicalTransaction) -> None:
    if not isinstance(event, CanonicalTransaction) or set(vars(event)) != _EVENT_FIELDS:
        raise ValueError('forbidden operational event fields or private label')
    if event.event_time_utc.tzinfo is None:
        raise ValueError('event timestamp must be timezone-aware')
    if not all(isinstance(getattr(event, name), str) and getattr(event, name)
               for name in ('sender_bank', 'sender_account', 'receiver_bank',
                            'receiver_account', 'paid_currency', 'received_currency')):
        raise ValueError('incomplete canonical event')
    amount = Decimal(event.paid_amount)
    if not amount.is_finite() or amount < 0:
        raise ValueError('invalid current paid amount')


def _digest(version: str, event: CanonicalTransaction, values: dict,
            coverage_start: datetime, coverage_state: str) -> str:
    payload = {'dataset_version': version, 'feature_version': FEATURE_VERSION,
               'event_fact_digest': event.event_fact_digest.hex(),
               'as_of': event.event_time_utc.isoformat(),
               'coverage_start': coverage_start.isoformat(),
               'coverage_state': coverage_state,
               'values': {key: str(value) if isinstance(value, Decimal) else value
                          for key, value in values.items()}}
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=True,
                     separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def _coverage(at, start, missing_intervals, available):
    if not available:
        return 'unavailable'
    if at < start + WINDOW:
        return 'incomplete'
    lower = at - WINDOW
    if any(begin < at and end > lower for begin, end in missing_intervals):
        return 'incomplete'
    return 'full'


def iter_feature_snapshots(events: Iterable[CanonicalTransaction], *,
                           dataset_version: str, coverage_start: datetime,
                           purpose: str = 'scoring', missing_intervals=(),
                           coverage_available: bool = True):
    """Replay event-time-sorted facts with only the sliding 24-hour history in memory."""
    if (purpose not in {'scoring', 'training'}
            or not isinstance(dataset_version, str)
            or not _VERSION_ID.fullmatch(dataset_version)):
        raise ValueError('invalid replay purpose or dataset version')
    if coverage_start.tzinfo is None:
        raise ValueError('coverage start must be timezone-aware')
    intervals = tuple(missing_intervals)
    if any(begin.tzinfo is None or end.tzinfo is None or begin >= end
           for begin, end in intervals):
        raise ValueError('invalid coverage interval')

    window = deque()
    sender_count = defaultdict(int)
    receiver_count = defaultdict(int)
    sender_receivers = defaultdict(Counter)
    receiver_senders = defaultdict(Counter)
    sender_paid = defaultdict(lambda: [0, Decimal(0)])
    receiver_received = defaultdict(lambda: [0, Decimal(0)])

    def update(event, sign):
        sender = (event.sender_bank, event.sender_account)
        receiver = (event.receiver_bank, event.receiver_account)
        sender_count[sender] += sign
        receiver_count[receiver] += sign
        if sender_count[sender] == 0:
            del sender_count[sender]
        if receiver_count[receiver] == 0:
            del receiver_count[receiver]
        sender_receivers[sender][receiver] += sign
        receiver_senders[receiver][sender] += sign
        if sender_receivers[sender][receiver] == 0:
            del sender_receivers[sender][receiver]
        if receiver_senders[receiver][sender] == 0:
            del receiver_senders[receiver][sender]
        if not sender_receivers[sender]:
            del sender_receivers[sender]
        if not receiver_senders[receiver]:
            del receiver_senders[receiver]
        paid = sender_paid[(sender, event.paid_currency)]
        paid[0] += sign
        paid[1] += sign * Decimal(event.paid_amount)
        if paid[0] == 0:
            del sender_paid[(sender, event.paid_currency)]
        received = receiver_received[(receiver, event.received_currency)]
        received[0] += sign
        received[1] += sign * Decimal(event.received_amount)
        if received[0] == 0:
            del receiver_received[(receiver, event.received_currency)]

    last_time = None
    for at, group in groupby(events, key=lambda event: event.event_time_utc):
        peers = list(group)
        if last_time is not None and at < last_time:
            raise ValueError('replay input must be sorted by event time')
        last_time = at
        for event in peers:
            _event_fact(event)
        lower = at - WINDOW
        while window and window[0].event_time_utc < lower:
            update(window.popleft(), -1)
        state = _coverage(at, coverage_start, intervals, coverage_available)
        for event in peers:
            sender = (event.sender_bank, event.sender_account)
            receiver = (event.receiver_bank, event.receiver_account)
            if state == 'full':
                paid_count, paid_sum = sender_paid[(sender, event.paid_currency)]
                received_count, received_sum = receiver_received[
                    (receiver, event.received_currency)]
                history = dict(zip(_HISTORY_KEYS, (
                    sender_count[sender], len(sender_receivers[sender]),
                    paid_count, paid_sum, receiver_count[receiver],
                    len(receiver_senders[receiver]), received_count, received_sum),
                    strict=True))
            else:
                history = dict.fromkeys(_HISTORY_KEYS)
            values = {**history, 'current_paid_amount': Decimal(event.paid_amount),
                      'current_paid_currency': event.paid_currency,
                      'current_payment_format': event.payment_format}
            yield HistoricalFeatureSnapshot(
                transaction_id=event.transaction_id, dataset_version=dataset_version,
                feature_version=FEATURE_VERSION, event_time=at, as_of=at,
                coverage_start=coverage_start, coverage_state=state,
                scoreable=state == 'full', feature_values=values,
                feature_input_digest=_digest(dataset_version, event, values,
                                             coverage_start, state),
                created_at=datetime.now(UTC))
        for event in peers:
            update(event, +1)
            window.append(event)


def build_feature_snapshots(events: Iterable[CanonicalTransaction], *,
                            dataset_version: str, coverage_start: datetime,
                            purpose: str = 'scoring', missing_intervals=(),
                            coverage_available: bool = True) -> dict:
    """Convenient pure replay for bounded authored fixtures; CLI uses the iterator."""
    ordered = sorted(events, key=lambda event: (event.event_time_utc, event.transaction_id))
    result = {}
    for snapshot in iter_feature_snapshots(
            ordered, dataset_version=dataset_version, coverage_start=coverage_start,
            purpose=purpose, missing_intervals=missing_intervals,
            coverage_available=coverage_available):
        if snapshot.transaction_id in result:
            raise ValueError('duplicate transaction identity')
        result[snapshot.transaction_id] = snapshot
    return result
