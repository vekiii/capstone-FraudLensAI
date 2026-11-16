"""PostgreSQL storage for immutable Feature 005 live transaction facts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import psycopg


class FactConflict(ValueError):
    """A stable source or transaction identity was reused for different facts."""


@dataclass(frozen=True)
class LiveTransaction:
    transaction_id: str
    source_namespace: str
    source_event_id: str
    event_time: datetime
    sender_bank: str
    sender_account: str
    receiver_bank: str
    receiver_account: str
    paid_amount: Decimal
    paid_currency: str
    received_amount: Decimal
    received_currency: str
    payment_format: str | None = None
    event_fact_digest: str = ""

    def __post_init__(self) -> None:
        if self.event_time.tzinfo is None or self.event_time.utcoffset() is None:
            raise ValueError("event_time must be timezone-aware")
        if not isinstance(self.paid_amount, Decimal) or not isinstance(self.received_amount, Decimal):
            raise TypeError("amounts must be Decimal values; binary floats are not accepted")
        if self.paid_amount.is_nan() or self.paid_amount.is_infinite():
            raise ValueError("paid_amount must be finite")
        if self.received_amount.is_nan() or self.received_amount.is_infinite():
            raise ValueError("received_amount must be finite")


def canonical_fact_digest(transaction: LiveTransaction) -> str:
    """Hash stable UTF-8 JSON fields; keep decimal values as exact strings."""
    event_time_utc = transaction.event_time.astimezone(timezone.utc).isoformat(timespec="microseconds")
    fact = {
        "transaction_id": transaction.transaction_id,
        "source_namespace": transaction.source_namespace,
        "source_event_id": transaction.source_event_id,
        "event_time_utc": event_time_utc.replace("+00:00", "Z"),
        "sender_bank": transaction.sender_bank,
        "sender_account": transaction.sender_account,
        "receiver_bank": transaction.receiver_bank,
        "receiver_account": transaction.receiver_account,
        "paid_amount": format(transaction.paid_amount, "f"),
        "paid_currency": transaction.paid_currency,
        "received_amount": format(transaction.received_amount, "f"),
        "received_currency": transaction.received_currency,
        "payment_format": transaction.payment_format,
    }
    encoded = json.dumps(fact, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def with_canonical_digest(transaction: LiveTransaction) -> LiveTransaction:
    """Return the same event with its digest calculated from immutable fact fields."""
    from dataclasses import replace

    return replace(transaction, event_fact_digest=canonical_fact_digest(transaction))


def insert_live_transaction(
    connection: psycopg.Connection[Any], transaction: LiveTransaction
) -> bool:
    """Insert one immutable event; return False for an exact retry, raise on identity conflict."""
    expected_digest = canonical_fact_digest(transaction)
    if transaction.event_fact_digest != expected_digest:
        raise ValueError("event_fact_digest does not match canonical transaction facts")

    values = (
        transaction.transaction_id,
        transaction.source_namespace,
        transaction.source_event_id,
        transaction.event_fact_digest,
        transaction.event_time.astimezone(timezone.utc),
        transaction.sender_bank,
        transaction.sender_account,
        transaction.receiver_bank,
        transaction.receiver_account,
        transaction.paid_amount,
        transaction.paid_currency,
        transaction.received_amount,
        transaction.received_currency,
        transaction.payment_format,
    )
    try:
        return connection.execute(
            """
            SELECT fraudlens.record_live_transaction(
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """,
            values,
        ).fetchone()[0]
    except psycopg.errors.UniqueViolation as exc:
        raise FactConflict("source event or transaction ID conflicts with existing facts") from exc