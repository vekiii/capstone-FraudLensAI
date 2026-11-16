# Feature 005 T003 â€” RED integration run

**Status:** RED as intended; schema and implementation were absent. No import, connection, or test-typo failure caused the result. The fixture connected to the real PostgreSQL 16.14 service and created/dropped a unique disposable database for each test. No test used `fraudlens_live`.

**Command:** `uv run --locked pytest backend/tests/integration/test_live_transactions.py -q`
**Exit:** 1 (expected failing RED run)

**Captured pytest output (secrets redacted):**

```text
FFFFFFF                                                                  [100%]
================================== FAILURES ===================================
________ test_source_identity_and_canonical_transaction_id_are_stable _________

isolated_live_postgres = LivePostgresSettings(host='127.0.0.1', port=5432, user='fraudlens_admin', dbname='fl_t003_cef3fd63ed9546769d222ef5bb77319a', connect_timeout=5, application_name='fraudlens_feature005_integration_test')

    def test_source_identity_and_canonical_transaction_id_are_stable(isolated_live_postgres):
        with psycopg.connect(**isolated_live_postgres.connect_kwargs()) as connection:
>           assert _require_live_schema_and_record(connection) is True
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

backend\tests\integration\test_live_transactions.py:69:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
backend\tests\integration\test_live_transactions.py:63: in _require_live_schema_and_record
    _require_live_schema(connection)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

connection = <psycopg.Connection [BAD] at 0x1d81096d810>

    def _require_live_schema(connection: psycopg.Connection[Any]) -> None:
        relation = connection.execute("SELECT to_regclass('fraudlens.live_transactions')").fetchone()[0]
>       assert relation is not None, (
            "T003 RED: required live_transactions schema is missing; T004 migration is not implemented"
        )
E       AssertionError: T003 RED: required live_transactions schema is missing; T004 migration is not implemented
E       assert None is not None

backend\tests\integration\test_live_transactions.py:41: AssertionError
_____________ test_exact_decimal_currency_and_utc_time_round_trip _____________

isolated_live_postgres = LivePostgresSettings(host='127.0.0.1', port=5432, user='fraudlens_admin', dbname='fl_t003_fc41336b054a40f1bd53c7da43c77613', connect_timeout=5, application_name='fraudlens_feature005_integration_test')

    def test_exact_decimal_currency_and_utc_time_round_trip(isolated_live_postgres):
        with psycopg.connect(**isolated_live_postgres.connect_kwargs()) as connection:
>           _require_live_schema_and_record(connection)

backend\tests\integration\test_live_transactions.py:81:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
backend\tests\integration\test_live_transactions.py:63: in _require_live_schema_and_record
    _require_live_schema(connection)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

connection = <psycopg.Connection [BAD] at 0x1d8109d8e90>

    def _require_live_schema(connection: psycopg.Connection[Any]) -> None:
        relation = connection.execute("SELECT to_regclass('fraudlens.live_transactions')").fetchone()[0]
>       assert relation is not None, (
            "T003 RED: required live_transactions schema is missing; T004 migration is not implemented"
        )
E       AssertionError: T003 RED: required live_transactions schema is missing; T004 migration is not implemented
E       assert None is not None

backend\tests\integration\test_live_transactions.py:41: AssertionError
________ test_sender_and_receiver_identities_include_bank_and_account _________

isolated_live_postgres = LivePostgresSettings(host='127.0.0.1', port=5432, user='fraudlens_admin', dbname='fl_t003_7f85bfd23d3548beb792787c28cb28f3', connect_timeout=5, application_name='fraudlens_feature005_integration_test')

    def test_sender_and_receiver_identities_include_bank_and_account(isolated_live_postgres):
        with psycopg.connect(**isolated_live_postgres.connect_kwargs()) as connection:
>           _require_live_schema_and_record(connection)

backend\tests\integration\test_live_transactions.py:93:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
backend\tests\integration\test_live_transactions.py:63: in _require_live_schema_and_record
    _require_live_schema(connection)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

connection = <psycopg.Connection [BAD] at 0x1d810976360>

    def _require_live_schema(connection: psycopg.Connection[Any]) -> None:
        relation = connection.execute("SELECT to_regclass('fraudlens.live_transactions')").fetchone()[0]
>       assert relation is not None, (
            "T003 RED: required live_transactions schema is missing; T004 migration is not implemented"
        )
E       AssertionError: T003 RED: required live_transactions schema is missing; T004 migration is not implemented
E       assert None is not None

backend\tests\integration\test_live_transactions.py:41: AssertionError
________________ test_same_source_id_and_same_facts_is_a_noop _________________

isolated_live_postgres = LivePostgresSettings(host='127.0.0.1', port=5432, user='fraudlens_admin', dbname='fl_t003_6388f846d1ca4e78888224570230b598', connect_timeout=5, application_name='fraudlens_feature005_integration_test')

    def test_same_source_id_and_same_facts_is_a_noop(isolated_live_postgres):
        with psycopg.connect(**isolated_live_postgres.connect_kwargs()) as connection:
>           assert _require_live_schema_and_record(connection) is True
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

backend\tests\integration\test_live_transactions.py:101:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
backend\tests\integration\test_live_transactions.py:63: in _require_live_schema_and_record
    _require_live_schema(connection)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

connection = <psycopg.Connection [BAD] at 0x1d81098f6b0>

    def _require_live_schema(connection: psycopg.Connection[Any]) -> None:
        relation = connection.execute("SELECT to_regclass('fraudlens.live_transactions')").fetchone()[0]
>       assert relation is not None, (
            "T003 RED: required live_transactions schema is missing; T004 migration is not implemented"
        )
E       AssertionError: T003 RED: required live_transactions schema is missing; T004 migration is not implemented
E       assert None is not None

backend\tests\integration\test_live_transactions.py:41: AssertionError
____________ test_same_source_id_with_changed_facts_is_a_conflict _____________

isolated_live_postgres = LivePostgresSettings(host='127.0.0.1', port=5432, user='fraudlens_admin', dbname='fl_t003_4548d2fdd8e74f398530d0f7419a98cc', connect_timeout=5, application_name='fraudlens_feature005_integration_test')

    def test_same_source_id_with_changed_facts_is_a_conflict(isolated_live_postgres):
        changed = {**FACT, "event_fact_digest": "b" * 64, "paid_amount": Decimal("99.000001")}
        with psycopg.connect(**isolated_live_postgres.connect_kwargs()) as connection:
>           _require_live_schema_and_record(connection)

backend\tests\integration\test_live_transactions.py:110:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
backend\tests\integration\test_live_transactions.py:63: in _require_live_schema_and_record
    _require_live_schema(connection)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

connection = <psycopg.Connection [BAD] at 0x1d810a34230>

    def _require_live_schema(connection: psycopg.Connection[Any]) -> None:
        relation = connection.execute("SELECT to_regclass('fraudlens.live_transactions')").fetchone()[0]
>       assert relation is not None, (
            "T003 RED: required live_transactions schema is missing; T004 migration is not implemented"
        )
E       AssertionError: T003 RED: required live_transactions schema is missing; T004 migration is not implemented
E       assert None is not None

backend\tests\integration\test_live_transactions.py:41: AssertionError
__________________ test_update_of_immutable_facts_is_denied ___________________

isolated_live_postgres = LivePostgresSettings(host='127.0.0.1', port=5432, user='fraudlens_admin', dbname='fl_t003_40cab543d61b4b0481b45b974613ffa3', connect_timeout=5, application_name='fraudlens_feature005_integration_test')

    def test_update_of_immutable_facts_is_denied(isolated_live_postgres):
        with psycopg.connect(**isolated_live_postgres.connect_kwargs(), autocommit=True) as connection:
>           _require_live_schema_and_record(connection)

backend\tests\integration\test_live_transactions.py:117:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
backend\tests\integration\test_live_transactions.py:63: in _require_live_schema_and_record
    _require_live_schema(connection)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

connection = <psycopg.Connection [BAD] at 0x1d81098f890>

    def _require_live_schema(connection: psycopg.Connection[Any]) -> None:
        relation = connection.execute("SELECT to_regclass('fraudlens.live_transactions')").fetchone()[0]
>       assert relation is not None, (
            "T003 RED: required live_transactions schema is missing; T004 migration is not implemented"
        )
E       AssertionError: T003 RED: required live_transactions schema is missing; T004 migration is not implemented
E       assert None is not None

backend\tests\integration\test_live_transactions.py:41: AssertionError
__________________ test_delete_of_immutable_facts_is_denied ___________________

isolated_live_postgres = LivePostgresSettings(host='127.0.0.1', port=5432, user='fraudlens_admin', dbname='fl_t003_3ea6f90efae249b0b694369d0cde7bd8', connect_timeout=5, application_name='fraudlens_feature005_integration_test')

    def test_delete_of_immutable_facts_is_denied(isolated_live_postgres):
        with psycopg.connect(**isolated_live_postgres.connect_kwargs(), autocommit=True) as connection:
>           _require_live_schema_and_record(connection)

backend\tests\integration\test_live_transactions.py:135:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
backend\tests\integration\test_live_transactions.py:63: in _require_live_schema_and_record
    _require_live_schema(connection)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

connection = <psycopg.Connection [BAD] at 0x1d81098fa70>

    def _require_live_schema(connection: psycopg.Connection[Any]) -> None:
        relation = connection.execute("SELECT to_regclass('fraudlens.live_transactions')").fetchone()[0]
>       assert relation is not None, (
            "T003 RED: required live_transactions schema is missing; T004 migration is not implemented"
        )
E       AssertionError: T003 RED: required live_transactions schema is missing; T004 migration is not implemented
E       assert None is not None

backend\tests\integration\test_live_transactions.py:41: AssertionError
=========================== short test summary info ===========================
FAILED backend/tests/integration/test_live_transactions.py::test_source_identity_and_canonical_transaction_id_are_stable
FAILED backend/tests/integration/test_live_transactions.py::test_exact_decimal_currency_and_utc_time_round_trip
FAILED backend/tests/integration/test_live_transactions.py::test_sender_and_receiver_identities_include_bank_and_account
FAILED backend/tests/integration/test_live_transactions.py::test_same_source_id_and_same_facts_is_a_noop
FAILED backend/tests/integration/test_live_transactions.py::test_same_source_id_with_changed_facts_is_a_conflict
FAILED backend/tests/integration/test_live_transactions.py::test_update_of_immutable_facts_is_denied
FAILED backend/tests/integration/test_live_transactions.py::test_delete_of_immutable_facts_is_denied
7 failed in 2.17s```
