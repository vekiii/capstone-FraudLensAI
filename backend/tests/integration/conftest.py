"""Fixtures for disposable PostgreSQL databases; never target SQLite or mocks."""

from __future__ import annotations

import ipaddress
import os
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

import psycopg
import pytest
from psycopg import sql

REPO_ROOT = Path(__file__).resolve().parents[3]
_TEST_DATABASE_PREFIX = "fraudlens_test_"
_TEST_ADVISORY_LOCK = 0x46524155444C454E


@dataclass(frozen=True)
class LivePostgresSettings:
    host: str
    port: int
    user: str
    dbname: str
    password: str = field(repr=False)
    connect_timeout: int = 5
    application_name: str = "fraudlens_feature005_integration_test"

    def _connect_kwargs(self) -> dict[str, object]:
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "dbname": self.dbname,
            "password": self.password,
            "connect_timeout": self.connect_timeout,
            "application_name": self.application_name,
        }

    def connect(self, *, autocommit: bool = False) -> psycopg.Connection:
        """Connect without allowing a failed call to print credential kwargs."""
        try:
            return psycopg.connect(**self._connect_kwargs(), autocommit=autocommit)
        except psycopg.Error as exc:
            raise RuntimeError(
                f"PostgreSQL connection failed for {self.host}:{self.port}/{self.dbname} "
                f"({type(exc).__name__})"
            ) from None


def _local_postgres_settings(dbname: str = "postgres") -> LivePostgresSettings:
    secret_path = REPO_ROOT / "infra" / "compose" / ".env.local"
    if not secret_path.is_file():
        raise RuntimeError("Ignored local PostgreSQL credentials file is missing")
    values: dict[str, str] = {}
    for line in secret_path.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    password = values.get("POSTGRES_PASSWORD")
    if not password:
        raise RuntimeError("POSTGRES_PASSWORD is absent from the ignored local credentials file")
    return LivePostgresSettings(
        host=os.environ.get("FRAUDLENS_TEST_PGHOST", "127.0.0.1"),
        port=int(os.environ.get("FRAUDLENS_TEST_PGPORT", "5432")),
        user=os.environ.get("FRAUDLENS_TEST_PGUSER", "fraudlens_admin"),
        dbname=dbname,
        password=password,
    )


def _is_loopback_host(host: str) -> bool:
    if host.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _test_database_name() -> str:
    return f"{_TEST_DATABASE_PREFIX}{uuid.uuid4().hex}"


def _safe_database_cleanup(
    database_name: str,
    expected_name: str,
    owner_name: str | None,
    expected_owner: str,
) -> bool:
    """Allow cleanup only for this fixture's generated DB and its recorded owner."""
    return (
        database_name == expected_name
        and re.fullmatch(r"fraudlens_test_[0-9a-f]{32}", database_name) is not None
        and owner_name == expected_owner
    )


@pytest.fixture
def isolated_live_postgres() -> Iterator[LivePostgresSettings]:
    """Use one opt-in, loopback PostgreSQL cluster and a uniquely owned test DB.

    Database cleanup is limited to the exact database this fixture created and
    verifies its owner first. Roles are cluster-global, so this fixture never
    drops roles, including roles it caused the migration to create.
    """
    if os.environ.get("FRAUDLENS_TEST_PG_DISPOSABLE") != "1":
        pytest.skip("set FRAUDLENS_TEST_PG_DISPOSABLE=1 for an approved local test cluster")

    admin_settings = _local_postgres_settings()
    if not _is_loopback_host(admin_settings.host):
        raise RuntimeError("PostgreSQL integration tests require a loopback host")

    database_name = _test_database_name()
    if re.fullmatch(r"fraudlens_test_[0-9a-f]{32}", database_name) is None:
        raise RuntimeError("generated PostgreSQL test database name is invalid")

    migration_path = REPO_ROOT / "backend" / "migrations" / "001_live_facts.sql"
    admin = admin_settings.connect(autocommit=True)
    lock_acquired = False
    database_created = False
    try:
        admin.execute("SELECT pg_advisory_lock(%s)", (_TEST_ADVISORY_LOCK,))
        lock_acquired = True
        server_version = admin.execute("SELECT current_setting('server_version')").fetchone()[0]
        if not server_version.startswith("16.14"):
            raise RuntimeError("Feature 005 tests require pinned PostgreSQL 16.14")

        collision = admin.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (database_name,)
        ).fetchone()
        if collision is not None:
            raise RuntimeError("refusing to use a pre-existing PostgreSQL test database")

        admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
        database_created = True
        test_settings = _local_postgres_settings(database_name)
        if not migration_path.is_file():
            raise RuntimeError("Feature 005 PostgreSQL migration file is missing")
        with test_settings.connect() as test_db:
            test_db.execute(migration_path.read_text(encoding="utf-8"))
        yield test_settings
    finally:
        try:
            if database_created:
                owner_row = admin.execute(
                    "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = %s",
                    (database_name,),
                ).fetchone()
                if owner_row is not None:
                    owner_name = owner_row[0]
                    if not _safe_database_cleanup(
                        database_name, database_name, owner_name, admin_settings.user
                    ):
                        raise RuntimeError(
                            "refusing PostgreSQL test cleanup: generated database owner/name changed"
                        )
                    admin.execute(
                        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                        "WHERE datname = %s AND pid <> pg_backend_pid()",
                        (database_name,),
                    )
                    admin.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(database_name)))
        finally:
            try:
                if lock_acquired:
                    admin.execute("SELECT pg_advisory_unlock(%s)", (_TEST_ADVISORY_LOCK,))
            finally:
                admin.close()
