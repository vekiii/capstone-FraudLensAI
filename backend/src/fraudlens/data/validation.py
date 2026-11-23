"""Deterministic row validation for the restricted local canonical dataset.

The caller supplies a finite, bounded batch (normally one pipeline chunk). This
module keeps source text intact, validates numeric text with Decimal, and emits
only fixed reason codes in the rejection ledger.
"""

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

_REQUIRED_FIELDS = (
    'source_sha256',
    'source_row_number',
    'transaction_id',
    'timestamp',
    'sender_bank',
    'sender_account',
    'receiver_bank',
    'receiver_account',
    'amount_received',
    'receiving_currency',
    'amount_paid',
    'payment_currency',
    'payment_format',
    'is_laundering',
)
_IDENTITY_FIELDS = (
    ('sender_bank', 'MISSING_SENDER_BANK'),
    ('sender_account', 'MISSING_SENDER_ACCOUNT'),
    ('receiver_bank', 'MISSING_RECEIVER_BANK'),
    ('receiver_account', 'MISSING_RECEIVER_ACCOUNT'),
)
_AMOUNT_FIELDS = (
    ('amount_received', 'INVALID_AMOUNT_RECEIVED'),
    ('amount_paid', 'INVALID_AMOUNT_PAID'),
)
_CURRENCY_FIELDS = (
    ('receiving_currency', 'MISSING_RECEIVING_CURRENCY'),
    ('payment_currency', 'MISSING_PAYMENT_CURRENCY'),
    ('payment_format', 'MISSING_PAYMENT_FORMAT'),
)
_TIMESTAMP_PATTERN = re.compile(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}\Z')
_AMOUNT_PATTERN = re.compile(r'[0-9]+(?:\.[0-9]+)?\Z')


@dataclass(frozen=True, slots=True)
class Rejection:
    """Privacy-bounded reason ledger entry; deliberately contains no raw values."""

    source_row_number: int
    reason_code: str


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """Counts and row outcomes for one bounded input batch."""

    source_count: int
    accepted_count: int
    rejected_count: int
    accepted_rows: tuple['CanonicalRow', ...]
    rejections: tuple[Rejection, ...]


class CanonicalRow(dict[str, Any]):
    """Dictionary-compatible canonical row with provenance attribute access."""

    @property
    def source_row_number(self) -> int:
        return self['source_row_number']


def _nonempty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_timestamp(value: object) -> bool:
    if not isinstance(value, str) or _TIMESTAMP_PATTERN.fullmatch(value) is None:
        return False
    try:
        datetime.strptime(value, '%Y/%m/%d %H:%M')
    except ValueError:
        return False
    return True


def _valid_amount(value: object) -> bool:
    if not isinstance(value, str) or _AMOUNT_PATTERN.fullmatch(value) is None:
        return False
    try:
        amount = Decimal(value)
    except InvalidOperation:
        return False
    return amount.is_finite() and amount >= 0


def _reason_for(row: Mapping[str, object]) -> str | None:
    if any(field not in row for field in _REQUIRED_FIELDS):
        return 'MISSING_REQUIRED_FIELD'
    if not _valid_timestamp(row['timestamp']):
        return 'INVALID_TIMESTAMP'
    for field, reason in _IDENTITY_FIELDS:
        if not _nonempty_text(row[field]):
            return reason
    for field, reason in _AMOUNT_FIELDS:
        if not _valid_amount(row[field]):
            return reason
    for field, reason in _CURRENCY_FIELDS:
        if not _nonempty_text(row[field]):
            return reason
    if row['is_laundering'] not in ('0', '1'):
        return 'INVALID_LABEL'
    return None


def validate_rows(rows: Iterable[Mapping[str, object]]) -> ValidationReport:
    """Validate a finite chunk, returning exact-text canonical rows and ledger.

    The first failure in the fixed validation order determines the single
    bounded reason code for each rejected source row. Timestamp text is kept as
    supplied: timezone policy has not been established by source evidence.
    Amounts are checked with Decimal but are neither converted to float nor
    quantized, because source precision policy is not yet frozen.
    """
    accepted: list[CanonicalRow] = []
    rejected: list[Rejection] = []
    source_count = 0
    for ordinal, source_row in enumerate(rows, start=1):
        source_count += 1
        if not isinstance(source_row, Mapping):
            # A non-mapping row has no trustworthy source row reference. Use its
            # batch ordinal to retain source/accepted/rejected reconciliation.
            rejected.append(Rejection(ordinal, 'MISSING_REQUIRED_FIELD'))
            continue
        source_row_number = source_row.get('source_row_number', ordinal)
        if (
            isinstance(source_row_number, bool)
            or not isinstance(source_row_number, int)
            or source_row_number < 1
        ):
            source_row_number = ordinal
        reason = _reason_for(source_row)
        if reason is not None:
            rejected.append(Rejection(source_row_number, reason))
            continue
        canonical = CanonicalRow(source_row)
        canonical['sender_key'] = (source_row['sender_bank'], source_row['sender_account'])
        canonical['receiver_key'] = (source_row['receiver_bank'], source_row['receiver_account'])
        accepted.append(canonical)

    return ValidationReport(
        source_count=source_count,
        accepted_count=len(accepted),
        rejected_count=len(rejected),
        accepted_rows=tuple(accepted),
        rejections=tuple(rejected),
    )
