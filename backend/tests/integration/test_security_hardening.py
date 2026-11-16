"""Security-header, request-boundary, and secret-history regressions."""

from __future__ import annotations

import subprocess
from pathlib import Path
from urllib.parse import quote

from fastapi.testclient import TestClient

from fraudlens.main import create_app
from fraudlens.settings import Settings

REPO_ROOT = Path(__file__).resolve().parents[3]
SECRET_PATTERN = (
    r"AKIA[0-9A-Z]{16}|"
    r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    r"sk-[A-Za-z0-9]{32,}|"
    r"gh[pousr]_[A-Za-z0-9]{30,}"
)
REQUIRED_HEADERS = {
    "content-security-policy": ("default-src 'none'", "frame-ancestors 'none'"),
    "x-content-type-options": ("nosniff",),
    "x-frame-options": ("DENY",),
    "referrer-policy": ("no-referrer",),
    "permissions-policy": ("camera=()", "microphone=()", "geolocation=()"),
    "cache-control": ("no-store",),
}


def _client() -> TestClient:
    return TestClient(create_app(settings=Settings()))


def test_success_and_error_responses_apply_security_headers() -> None:
    with _client() as client:
        responses = [client.get("/api/health"), client.get("/missing-security-probe")]

    assert [response.status_code for response in responses] == [200, 404]
    for response in responses:
        for header, required_parts in REQUIRED_HEADERS.items():
            value = response.headers[header]
            for required in required_parts:
                assert required in value
        assert "unsafe-inline" not in response.headers["content-security-policy"]
        assert "unsafe-eval" not in response.headers["content-security-policy"]


def test_read_only_api_never_issues_cookies() -> None:
    with _client() as client:
        responses = [client.get("/api/health"), client.get("/missing-cookie-probe")]

    assert all("set-cookie" not in response.headers for response in responses)


def test_oversized_request_body_is_rejected_before_route_dispatch() -> None:
    oversized = b"x" * (1_048_576 + 1)
    with _client() as client:
        response = client.post(
            "/api/cases",
            content=oversized,
            headers={"content-type": "application/json"},
        )

    assert response.status_code == 413
    assert response.json() == {
        "error": {"code": "invalid_request", "message": "Invalid request."}
    }
    assert len(response.content) < 256


def test_encoded_null_byte_is_rejected_without_reflection() -> None:
    malicious = "CASE-001\x00<script>alert('Ω')</script>"
    with _client() as client:
        response = client.get(f"/api/cases/{quote(malicious, safe='')}")

    assert response.status_code in {404, 422}
    assert response.headers["content-type"].startswith("application/json")
    assert "<script" not in response.text.lower()
    assert "CASE-001" not in response.text
    assert "Traceback" not in response.text


def test_tracked_contents_contain_no_high_confidence_secret_values() -> None:
    result = subprocess.run(
        ["git", "grep", "-I", "-l", "-E", SECRET_PATTERN, "--", "."],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode in {0, 1}
    assert not result.stdout.strip(), "high-confidence secret pattern found in tracked file"


def test_git_history_contains_no_high_confidence_secret_values() -> None:
    result = subprocess.run(
        ["git", "log", "--all", "--format=%H", f"-G{SECRET_PATTERN}", "--", "."],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert not result.stdout.strip(), "high-confidence secret pattern found in Git history"
