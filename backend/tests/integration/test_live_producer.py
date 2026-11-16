"""T005: deterministic synthetic producer and stable identity integration tests."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
from datetime import timezone
from decimal import Decimal

import psycopg
import pytest

from fraudlens.live_producer import produce_transactions, synthetic_timeline
from fraudlens.live_store import FactConflict, canonical_fact_digest, with_canonical_digest


def test_timeline_is_deterministic_and_covers_identity_currency_and_ties():
    first = synthetic_timeline()
    second = synthetic_timeline()
    assert first == second
    assert [event.transaction_id for event in first] == [
        "tx_synthetic_0001",
        "tx_synthetic_0002",
        "tx_synthetic_0003",
        "tx_synthetic_0004",
    ]
    banks = {event.sender_bank for event in first} | {event.receiver_bank for event in first}
    currencies = {event.paid_currency for event in first} | {event.received_currency for event in first}
    time_counts = Counter(event.event_time for event in first)
    assert banks == {"BANK-ALPHA", "BANK-BETA"}
    assert currencies == {"EUR", "USD"}
    assert any(count > 1 for count in time_counts.values())
    assert all(event.event_time.utcoffset().total_seconds() == 0 for event in first)
    assert all(event.event_fact_digest == canonical_fact_digest(event) for event in first)
    assert all(isinstance(event.paid_amount, Decimal) for event in first)


def test_producer_inserts_exact_facts_and_same_timeline_is_idempotent(isolated_live_postgres):
    timeline = synthetic_timeline()
    with psycopg.connect(**isolated_live_postgres.connect_kwargs()) as connection:
        assert produce_transactions(connection, timeline) == len(timeline)
        assert produce_transactions(connection, synthetic_timeline()) == 0
        rows = connection.execute(
            """
            SELECT transaction_id, sender_bank, sender_account, receiver_bank, receiver_account,
                   paid_amount, paid_currency, received_amount, received_currency, event_time
            FROM fraudlens.live_transactions
            ORDER BY event_time, transaction_id
            """
        ).fetchall()
        assert connection.execute("SELECT count(*) FROM fraudlens.live_transactions").fetchone()[0] == 4
        assert connection.execute("SELECT count(*) FROM fraudlens.ingestion_receipts").fetchone()[0] == 4
    assert [row[0] for row in rows] == [event.transaction_id for event in timeline]
    assert (rows[0][1], rows[0][2], rows[0][3], rows[0][4]) == (
        "BANK-ALPHA",
        "alpha-customer-01",
        "BANK-BETA",
        "beta-merchant-04",
    )
    assert format(rows[0][5], "f") == "125.400000"
    assert rows[0][6] == "EUR"
    assert format(rows[0][7], "f") == "136.120000"
    assert rows[0][8] == "USD"
    assert rows[0][9].astimezone(timezone.utc) == timeline[0].event_time


def test_same_source_identity_with_changed_fact_fails_closed(isolated_live_postgres):
    event = synthetic_timeline()[0]
    changed = with_canonical_digest(replace(event, paid_amount=Decimal("125.410000")))
    with psycopg.connect(**isolated_live_postgres.connect_kwargs()) as connection:
        assert produce_transactions(connection, [event]) == 1
        with pytest.raises(FactConflict, match="conflicts with existing facts"):
            with connection.transaction():
                produce_transactions(connection, [changed])
        stored = connection.execute(
            "SELECT paid_amount, event_fact_digest FROM fraudlens.live_transactions WHERE transaction_id = %s",
            (event.transaction_id,),
        ).fetchone()
    assert format(stored[0], "f") == "125.400000"
    assert stored[1].strip() == event.event_fact_digest