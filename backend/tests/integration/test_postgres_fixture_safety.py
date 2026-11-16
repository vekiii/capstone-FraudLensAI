"""Pure checks for the destructive-operation guards in the PG test fixture."""

import conftest
import pytest


@pytest.mark.parametrize("host", ["localhost", "127.0.0.1", "::1"])
def test_postgres_test_host_accepts_loopback(host):
    assert conftest._is_loopback_host(host)


@pytest.mark.parametrize("host", ["0.0.0.0", "192.0.2.15", "postgres.example.test"])
def test_postgres_test_host_rejects_non_loopback(host):
    assert not conftest._is_loopback_host(host)


def test_generated_database_name_has_isolated_namespace():
    database_name = conftest._test_database_name()
    assert conftest._safe_database_cleanup(
        database_name, database_name, "fraudlens_admin", "fraudlens_admin"
    )


@pytest.mark.parametrize(
    ("database_name", "expected_name", "owner_name", "expected_owner"),
    [
        ("postgres", "postgres", "fraudlens_admin", "fraudlens_admin"),
        ("fraudlens_live", "fraudlens_live", "fraudlens_admin", "fraudlens_admin"),
        ("fraudlens_test_" + "a" * 32, "fraudlens_test_" + "b" * 32,
         "fraudlens_admin", "fraudlens_admin"),
        ("fraudlens_test_" + "a" * 32, "fraudlens_test_" + "a" * 32,
         "other_owner", "fraudlens_admin"),
        ("fraudlens_test_not-a-uuid", "fraudlens_test_not-a-uuid",
         "fraudlens_admin", "fraudlens_admin"),
    ],
)
def test_postgres_cleanup_guard_rejects_existing_or_unowned_database(
    database_name, expected_name, owner_name, expected_owner
):
    assert not conftest._safe_database_cleanup(database_name, expected_name, owner_name, expected_owner)


def test_postgres_cleanup_guard_allows_only_generated_owned_database():
    database_name = "fraudlens_test_" + "a" * 32
    assert conftest._safe_database_cleanup(
        database_name, database_name, "fraudlens_admin", "fraudlens_admin"
    )
