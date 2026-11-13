"""Startup and health work without provider access or application data."""
import json
import socket
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ValidationError


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    for name in ['APP_MODE', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'MODEL_PATH', 'CORPUS_PATH']:
        monkeypatch.delenv(name, raising=False)


def test_default_settings_resolve_repository_fixture_path(monkeypatch, tmp_path):
    from fraudlens.settings import load_settings

    monkeypatch.chdir(tmp_path)
    settings = load_settings()
    assert settings.mode == 'fixture'
    expected = Path(__file__).resolve().parents[3] / 'data/fixtures/cases.json'
    assert settings.fixture_path == expected


@pytest.mark.parametrize('mode', ['fixture', None])
def test_lifecycle_health_without_keys_data_or_network(monkeypatch, tmp_path, mode):
    def forbidden(*args, **kwargs):
        pytest.fail('Unexpected outbound network call during startup/health')

    original_connect = socket.socket.connect

    def guarded_connect(sock, address):
        # Windows asyncio uses a loopback socketpair internally for TestClient.
        if isinstance(address, tuple) and address[0] in ('127.0.0.1', '::1'):
            return original_connect(sock, address)
        return forbidden()

    monkeypatch.setattr(socket.socket, 'connect', guarded_connect)
    monkeypatch.setattr(socket, 'create_connection', forbidden)
    monkeypatch.setattr(httpx.HTTPTransport, 'handle_request', forbidden)
    monkeypatch.setattr(httpx.AsyncHTTPTransport, 'handle_async_request', forbidden)
    monkeypatch.chdir(tmp_path)
    if mode is not None:
        monkeypatch.setenv('APP_MODE', mode)
    from fraudlens.main import create_app
    from fraudlens.settings import Settings

    # Deliberately absent fixture file; settings injection must be usable.
    settings = Settings(fixture_path=tmp_path / 'missing/cases.json')
    app = create_app(settings=settings)
    assert app.state.settings is settings
    with TestClient(app) as client:
        response = client.get('/api/health')
        assert response.status_code == 200
        assert response.headers['content-type'].startswith('application/json')
        assert response.json() == {'status': 'ok', 'mode': 'fixture'}
        root = Path(__file__).resolve().parents[3]
        schema = json.loads((root / 'specs/001-project-foundation/contracts/schemas.json').read_text())
        Draft202012Validator({**schema, '$ref': '#/$defs/Health'},
                             format_checker=FormatChecker()).validate(response.json())


def test_factory_reads_environment_and_default_health():
    from fraudlens.main import create_app

    with TestClient(create_app()) as client:
        assert client.get('/api/health').json() == {'status': 'ok', 'mode': 'fixture'}


@pytest.mark.parametrize('mode', ['model', 'rules', '', 'FIXTURE'])
def test_factory_rejects_unsupported_environment_mode(monkeypatch, mode):
    from fraudlens.main import create_app

    monkeypatch.setenv('APP_MODE', mode)
    with pytest.raises(ValidationError):
        create_app()
