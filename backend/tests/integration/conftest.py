"""Fixtures for real PostgreSQL integration tests; never use SQLite or mocks here."""

from __future__ import annotations

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
ROLE_NAMES = (
    "migration_owner",
    "live_producer",
    "cdc_connector",
    "live_worker",
    "label_curator",
    "registry_operator",
    "live_api_reader",
)


@dataclass(frozen=True)
class LivePostgresSettings:
    host: str
    port: int
    user: str
    dbname: str
    password: str = field(repr=False)
    connect_timeout: int = 5
    application_name: str = "fraudlens_feature005_integration_test"

    def connect_kwargs(self) -> dict[str, object]:
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "dbname": self.dbname,
            "password": self.password,
            "connect_timeout": self.connect_timeout,
            "application_name": self.application_name,
        }


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


@pytest.fixture
def isolated_live_postgres() -> Iterator[LivePostgresSettings]:
    """Create one disposable database and remove it and test-created roles after each test."""
    admin_settings = _local_postgres_settings()
    database_name = f"fl_t003_{uuid.uuid4().hex}"
    assert re.fullmatch(r"fl_t003_[0-9a-f]{32}", database_name)
    created_roles: set[str] = set()
    migration_path = REPO_ROOT / "backend" / "migrations" / "001_live_facts.sql"

    with psycopg.connect(**admin_settings.connect_kwargs(), autocommit=True) as admin:
        server_version = admin.execute("SELECT current_setting('server_version')").fetchone()[0]
        assert server_version.startswith("16.14"), "Feature 005 tests require pinned PostgreSQL 16.14"
        existing = {
            row[0]
            for row in admin.execute(
                "SELECT rolname FROM pg_roles WHERE rolname = ANY(%s)",
                (list(ROLE_NAMES),),
            )
        }
        created_roles = set(ROLE_NAMES) - existing
        admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))

    test_settings = _local_postgres_settings(database_name)
    try:
        if migration_path.is_file():
            with psycopg.connect(**test_settings.connect_kwargs()) as test_db:
                test_db.execute(migration_path.read_text(encoding="utf-8"))
        yield test_settings
    finally:
        with psycopg.connect(**admin_settings.connect_kwargs(), autocommit=True) as admin:
            admin.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s AND pid <> pg_backend_pid()",
                (database_name,),
            )
            admin.execute(
                sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(database_name))
            )
            for role_name in sorted(created_roles, reverse=True):
                admin.execute(sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(role_name)))