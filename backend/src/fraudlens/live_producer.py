"""Deterministic synthetic live transactions for Feature 005 integration work."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Iterable

import psycopg

from fraudlens.live_store import LiveTransaction, insert_live_transaction, with_canonical_digest

NAMESPACE = "fraudlens-synthetic-v1"
BANK_ALPHA = "BANK-ALPHA"
BANK_BETA = "BANK-BETA"


def synthetic_timeline() -> tuple[LiveTransaction, ...]:
    """Return stable sample IDs, two banks/currencies, and a same-time tie pair."""
    events = (
        LiveTransaction(
            transaction_id="tx_synthetic_0001",
            source_namespace=NAMESPACE,
            source_event_id="synthetic-event-0001",
            event_time=datetime(2026, 11, 16, 9, 30, 0, tzinfo=timezone.utc),
            sender_bank=BANK_ALPHA,
            sender_account="alpha-customer-01",
            receiver_bank=BANK_BETA,
            receiver_account="beta-merchant-04",
            paid_amount=Decimal("125.400000"),
            paid_currency="EUR",
            received_amount=Decimal("136.120000"),
            received_currency="USD",
            payment_format="SYNTHETIC-CROSS-BORDER",
        ),
        LiveTransaction(
            transaction_id="tx_synthetic_0002",
            source_namespace=NAMESPACE,
            source_event_id="synthetic-event-0002",
            event_time=datetime(2026, 11, 16, 9, 31, 0, tzinfo=timezone.utc),
            sender_bank=BANK_BETA,
            sender_account="beta-customer-07",
            receiver_bank=BANK_ALPHA,
            receiver_account="alpha-merchant-02",
            paid_amount=Decimal("76.250000"),
            paid_currency="USD",
            received_amount=Decimal("76.250000"),
            received_currency="USD",
            payment_format="SYNTHETIC-DOMESTIC",
        ),
        LiveTransaction(
            transaction_id="tx_synthetic_0003",
            source_namespace=NAMESPACE,
            source_event_id="synthetic-event-0003",
            event_time=datetime(2026, 11, 16, 9, 31, 0, tzinfo=timezone.utc),
            sender_bank=BANK_ALPHA,
            sender_account="alpha-customer-03",
            receiver_bank=BANK_BETA,
            receiver_account="beta-merchant-05",
            paid_amount=Decimal("44.100000"),
            paid_currency="EUR",
            received_amount=Decimal("48.220000"),
            received_currency="USD",
            payment_format="SYNTHETIC-CROSS-BORDER",
        ),
        LiveTransaction(
            transaction_id="tx_synthetic_0004",
            source_namespace=NAMESPACE,
            source_event_id="synthetic-event-0004",
            event_time=datetime(2026, 11, 16, 9, 32, 0, tzinfo=timezone.utc),
            sender_bank=BANK_BETA,
            sender_account="beta-customer-09",
            receiver_bank=BANK_ALPHA,
            receiver_account="alpha-merchant-08",
            paid_amount=Decimal("0.010000"),
            paid_currency="USD",
            received_amount=Decimal("0.010000"),
            received_currency="USD",
            payment_format="SYNTHETIC-DOMESTIC",
        ),
    )
    return tuple(with_canonical_digest(event) for event in events)


def produce_transactions(
    connection: psycopg.Connection, events: Iterable[LiveTransaction]
) -> int:
    """Insert a timeline idempotently and return the number of new facts."""
    return sum(insert_live_transaction(connection, event) for event in events)