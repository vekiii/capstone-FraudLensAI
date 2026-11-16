"""T003: live fact contract against a real, disposable PostgreSQL database."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import psycopg
import pytest
from psycopg import errors

FACT = {
    "transaction_id": "tx_feature005_exact_001",
    "source_namespace": "synthetic-bank-feed-v1",
    "source_event_id": "feed-event-0001",
    "event_fact_digest": "a" * 64,
    "event_time": datetime(2026, 11, 16, 9, 30, 0, 123456, tzinfo=timezone.utc),
    "sender_bank": "BANK-A",
    "sender_account": "acct-0091",
    "receiver_bank": "BANK-B",
    "receiver_account": "acct-0091",
    "paid_amount": Decimal("1234567890123.123456"),
    "paid_currency": "EUR",
    "received_amount": Decimal("456.780000"),
    "received_currency": "USD",
    "payment_format": "SEPA-CREDIT",
}

COLUMNS = (
    "transaction_id, source_namespace, source_event_id, event_fact_digest, event_time, "
    "sender_bank, sender_account, receiver_bank, receiver_account, paid_amount, paid_currency, "
    "received_amount, received_currency, payment_format"
)
ARGUMENTS = ", ".join(["%s"] * 14)


def _require_live_schema(connection: psycopg.Connection[Any]) -> None:
    relation = connection.execute("SELECT to_regclass('fraudlens.live_transactions')").fetchone()[0]
    assert relation is not None, (
        "T003 RED: required live_transactions schema is missing; T004 migration is not implemented"
    )


def _record(connection: psycopg.Connection[Any], fact: dict[str, object]) -> bool:
    values = tuple(fact[key] for key in FACT)
    return connection.execute(
        f"SELECT fraudlens.record_live_transaction({ARGUMENTS})", values
    ).fetchone()[0]


def _row(connection: psycopg.Connection[Any], transaction_id: str = FACT["transaction_id"]):
    return connection.execute(
        f"SELECT {COLUMNS} FROM fraudlens.live_transactions WHERE transaction_id = %s",
        (transaction_id,),
    ).fetchone()


def _require_live_schema_and_record(
    connection: psycopg.Connection[Any], fact: dict[str, object] = FACT
) -> bool:
    _require_live_schema(connection)
    return _record(connection, fact)


def test_source_identity_and_canonical_transaction_id_are_stable(isolated_live_postgres):
    with psycopg.connect(**isolated_live_postgres.connect_kwargs()) as connection:
        assert _require_live_schema_and_record(connection) is True
        row = _row(connection)
    assert row[0:4] == (
        FACT["transaction_id"],
        FACT["source_namespace"],
        FACT["source_event_id"],
        FACT["event_fact_digest"],
    )


def test_exact_decimal_currency_and_utc_time_round_trip(isolated_live_postgres):
    with psycopg.connect(**isolated_live_postgres.connect_kwargs()) as connection:
        _require_live_schema_and_record(connection)
        row = _row(connection)
    assert format(row[9], "f") == "1234567890123.123456"
    assert format(row[11], "f") == "456.780000"
    assert row[10] == "EUR"
    assert row[12] == "USD"
    assert row[4] == FACT["event_time"]
    assert row[4].utcoffset().total_seconds() == 0


def test_sender_and_receiver_identities_include_bank_and_account(isolated_live_postgres):
    with psycopg.connect(**isolated_live_postgres.connect_kwargs()) as connection:
        _require_live_schema_and_record(connection)
        row = _row(connection)
    assert (row[5], row[6]) == ("BANK-A", "acct-0091")
    assert (row[7], row[8]) == ("BANK-B", "acct-0091")


def test_same_source_id_and_same_facts_is_a_noop(isolated_live_postgres):
    with psycopg.connect(**isolated_live_postgres.connect_kwargs()) as connection:
        assert _require_live_schema_and_record(connection) is True
        assert _record(connection, FACT) is False
        assert connection.execute("SELECT count(*) FROM fraudlens.live_transactions").fetchone()[0] == 1
        assert connection.execute("SELECT count(*) FROM fraudlens.ingestion_receipts").fetchone()[0] == 1


def test_same_source_id_with_changed_facts_is_a_conflict(isolated_live_postgres):
    changed = {**FACT, "event_fact_digest": "b" * 64, "paid_amount": Decimal("99.000001")}
    with psycopg.connect(**isolated_live_postgres.connect_kwargs()) as connection:
        _require_live_schema_and_record(connection)
        with pytest.raises(errors.UniqueViolation, match="source event reused with different facts"):
            _record(connection, changed)


def test_update_of_immutable_facts_is_denied(isolated_live_postgres):
    with psycopg.connect(**isolated_live_postgres.connect_kwargs(), autocommit=True) as connection:
        _require_live_schema_and_record(connection)
        connection.execute("SET ROLE live_producer")
        with pytest.raises(errors.InsufficientPrivilege):
            connection.execute(
                "UPDATE fraudlens.live_transactions SET paid_amount = 1 WHERE transaction_id = %s",
                (FACT["transaction_id"],),
            )
        connection.execute("RESET ROLE")
        connection.execute("SET ROLE migration_owner")
        with pytest.raises(errors.ObjectNotInPrerequisiteState, match="immutable"):
            connection.execute(
                "UPDATE fraudlens.live_transactions SET paid_amount = 1 WHERE transaction_id = %s",
                (FACT["transaction_id"],),
            )


def test_delete_of_immutable_facts_is_denied(isolated_live_postgres):
    with psycopg.connect(**isolated_live_postgres.connect_kwargs(), autocommit=True) as connection:
        _require_live_schema_and_record(connection)
        connection.execute("SET ROLE live_producer")
        with pytest.raises(errors.InsufficientPrivilege):
            connection.execute(
                "DELETE FROM fraudlens.live_transactions WHERE transaction_id = %s",
                (FACT["transaction_id"],),
            )
        connection.execute("RESET ROLE")
        connection.execute("SET ROLE migration_owner")
        with pytest.raises(errors.ObjectNotInPrerequisiteState, match="immutable"):
            connection.execute(
                "DELETE FROM fraudlens.live_transactions WHERE transaction_id = %s",
                (FACT["transaction_id"],),
            )
@pytest.mark.parametrize("amount", [Decimal("10000000000000"), Decimal("1.0000001")])
def test_numeric_bounds_match_event_contract(isolated_live_postgres, amount):
    invalid = {**FACT, "paid_amount": amount}
    with psycopg.connect(**isolated_live_postgres.connect_kwargs()) as connection:
        _require_live_schema(connection)
        with pytest.raises(errors.CheckViolation):
            _record(connection, invalid)


def test_catalog_enforces_keys_immutability_no_labels_and_role_boundaries(
    isolated_live_postgres,
):
    with psycopg.connect(**isolated_live_postgres.connect_kwargs()) as connection:
        columns = {
            row[0]
            for row in connection.execute(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'fraudlens' AND table_name = 'live_transactions'
                """
            )
        }
        constraints = {
            row[0]: row[1]
            for row in connection.execute(
                """
                SELECT c.conname, pg_get_constraintdef(c.oid)
                FROM pg_constraint AS c
                JOIN pg_class AS t ON t.oid = c.conrelid
                JOIN pg_namespace AS n ON n.oid = t.relnamespace
                WHERE n.nspname = 'fraudlens' AND t.relname IN ('live_transactions', 'ingestion_receipts')
                ORDER BY t.relname, c.conname
                """
            )
        }
        triggers = connection.execute(
            """
            SELECT tgname, tgenabled
            FROM pg_trigger AS t
            JOIN pg_class AS c ON c.oid = t.tgrelid
            JOIN pg_namespace AS n ON n.oid = c.relnamespace
            WHERE n.nspname = 'fraudlens' AND c.relname = 'live_transactions' AND NOT t.tgisinternal
            """
        ).fetchall()
        privileges = {
            "producer_execute": connection.execute(
                """
                SELECT has_function_privilege('live_producer', p.oid, 'EXECUTE')
                FROM pg_proc AS p JOIN pg_namespace AS n ON n.oid = p.pronamespace
                WHERE n.nspname = 'fraudlens' AND p.proname = 'record_live_transaction'
                """
            ).fetchone()[0],
            "producer_update": connection.execute(
                "SELECT has_table_privilege('live_producer', 'fraudlens.live_transactions', 'UPDATE')"
            ).fetchone()[0],
            "producer_delete": connection.execute(
                "SELECT has_table_privilege('live_producer', 'fraudlens.live_transactions', 'DELETE')"
            ).fetchone()[0],
            "cdc_select": connection.execute(
                "SELECT has_table_privilege('cdc_connector', 'fraudlens.live_transactions', 'SELECT')"
            ).fetchone()[0],
            "worker_select": connection.execute(
                "SELECT has_table_privilege('live_worker', 'fraudlens.live_transactions', 'SELECT')"
            ).fetchone()[0],
            "labels_select": connection.execute(
                "SELECT has_table_privilege('label_curator', 'fraudlens.live_transactions', 'SELECT')"
            ).fetchone()[0],
            "registry_select": connection.execute(
                "SELECT has_table_privilege('registry_operator', 'fraudlens.live_transactions', 'SELECT')"
            ).fetchone()[0],
            "api_select": connection.execute(
                "SELECT has_table_privilege('live_api_reader', 'fraudlens.live_transactions', 'SELECT')"
            ).fetchone()[0],
        }
    assert "label" not in columns
    assert "target" not in columns
    assert any("PRIMARY KEY (transaction_id)" in definition for definition in constraints.values())
    assert any(
        "UNIQUE (source_namespace, source_event_id)" in definition
        for definition in constraints.values()
    )
    assert any("PRIMARY KEY (source_namespace, source_event_id)" in definition for definition in constraints.values())
    assert any(name == "live_transactions_immutable" and enabled == "O" for name, enabled in triggers)
    assert privileges == {
        "producer_execute": True,
        "producer_update": False,
        "producer_delete": False,
        "cdc_select": True,
        "worker_select": True,
        "labels_select": False,
        "registry_select": False,
        "api_select": False,
    }
    print(f"CATALOG columns={sorted(columns)}")
    print(f"CATALOG constraints={constraints}")
    print(f"CATALOG triggers={triggers}")
    print(f"CATALOG role_privileges={privileges}")