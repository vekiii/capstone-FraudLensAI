"""Focused security regressions for the local read-only HTTP boundary.

All payloads are synthetic. These checks do not contact a network service or
exercise the destructive PostgreSQL fixture.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from urllib.parse import quote

from fastapi.testclient import TestClient

from fraudlens.main import create_app
from fraudlens.settings import Settings

REPO_ROOT = Path(__file__).resolve().parents[3]


def _client(settings: Settings | None = None) -> TestClient:
    return TestClient(create_app(settings=settings or Settings()))


def _assert_generic_error(response, expected_status: int) -> None:
    assert response.status_code == expected_status
    assert response.headers["content-type"].startswith("application/json")
    payload = response.json()
    assert set(payload) == {"error"}
    assert set(payload["error"]) == {"code", "message"}
    assert "Traceback" not in response.text
    assert "fraudlens" not in response.text.lower()
    assert "sqlite" not in response.text.lower()


def test_case_listing_requires_an_authenticated_principal() -> None:
    """RED until the API has the analyst access boundary planned by T028."""
    with _client() as client:
        response = client.get("/api/cases")

    assert response.status_code in {401, 403}
    assert "items" not in response.text


def test_hostile_origin_preflight_receives_no_cross_origin_permission() -> None:
    with _client() as client:
        response = client.options(
            "/api/cases",
            headers={
                "Origin": "https://attacker.invalid",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization",
            },
        )

    assert response.status_code == 405
    assert "access-control-allow-origin" not in response.headers
    assert "access-control-allow-credentials" not in response.headers
    _assert_generic_error(response, 405)


def test_dataset_sql_injection_payload_is_rejected_before_store_access(tmp_path: Path) -> None:
    case_id = "C" + ("a" * 32) + "' OR '1'='1"
    settings = Settings(
        mode="dataset",
        scorer="rules",
        run_store_path=tmp_path / "must-not-be-opened.sqlite",
    )
    with _client(settings) as client:
        response = client.get(
            f"/api/cases/{quote(case_id, safe='')}",
            params={"snapshot": "run_security"},
        )

    _assert_generic_error(response, 422)
    assert "OR" not in response.text
    assert "syntax" not in response.text.lower()


def test_xss_payload_is_not_reflected_by_case_validation() -> None:
    payload = "<img src=x onerror=alert(1)>"
    with _client() as client:
        response = client.get(f"/api/cases/{quote(payload, safe='')}")

    _assert_generic_error(response, 422)
    assert payload not in response.text
    assert "<img" not in response.text.lower()


def test_oversized_case_identifier_has_a_bounded_generic_response() -> None:
    oversized = "CASE-" + ("9" * 10_000)
    with _client() as client:
        response = client.get(f"/api/cases/{oversized}")

    _assert_generic_error(response, 422)
    assert len(response.content) < 512
    assert oversized not in response.text


def test_unicode_confusable_case_identifier_is_rejected_without_echo() -> None:
    confusable = "CASE-１２３"
    with _client() as client:
        response = client.get(f"/api/cases/{quote(confusable, safe='')}")

    _assert_generic_error(response, 422)
    assert confusable not in response.text


def test_encoded_path_traversal_does_not_expose_files_or_paths() -> None:
    traversal = "..%2F..%2Finfra%2Fcompose%2F.env.local"
    with _client() as client:
        response = client.get(f"/api/cases/{traversal}")

    assert response.status_code in {404, 422}
    assert response.headers["content-type"].startswith("application/json")
    assert ".env.local" not in response.text
    assert "POSTGRES_PASSWORD" not in response.text
    assert str(REPO_ROOT) not in response.text


def test_unexpected_query_parameters_cannot_change_case_listing() -> None:
    with _client() as client:
        baseline = client.get("/api/cases")
        injected = client.get(
            "/api/cases",
            params={"admin": "true", "role": "superuser", "limit": "999999999"},
        )

    assert baseline.status_code == injected.status_code == 200
    assert injected.json() == baseline.json()
    assert "superuser" not in injected.text


def test_malformed_json_on_read_only_resource_is_not_parsed_or_reflected() -> None:
    marker = "PRIVATE_SYNTHETIC_SECRET"
    with _client() as client:
        response = client.post(
            "/api/cases",
            content=f'{{"token":"{marker}"',
            headers={"content-type": "application/json"},
        )

    _assert_generic_error(response, 405)
    assert marker not in response.text


def test_tracked_files_exclude_private_env_and_key_material() -> None:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    tracked = {
        Path(name).as_posix()
        for name in result.stdout.decode("utf-8").split("\0")
        if name
    }

    forbidden_env = {
        path for path in tracked
        if Path(path).name.startswith(".env") and Path(path).name != ".env.example"
    }
    forbidden_keys = {
        path for path in tracked
        if Path(path).suffix.lower() in {".key", ".pem", ".p12", ".pfx"}
    }
    assert "infra/compose/.env.local" not in tracked
    assert not forbidden_env
    assert not forbidden_keys
