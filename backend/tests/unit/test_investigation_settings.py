"""Isolated environment configuration; no real keys or provider calls."""
import importlib
import logging
import socket
import sqlite3

import pytest
from fastapi.testclient import TestClient

from fraudlens.investigation.settings import load_settings

LIMITS = {
    'MAX_PROVIDER_REQUESTS': 8, 'MAX_TOOL_CALLS': 12, 'TOTAL_TIMEOUT_SECONDS': 120,
    'REQUEST_TIMEOUT_SECONDS': 30, 'MAX_INPUT_BYTES': 48000,
    'MAX_OUTPUT_TOKENS': 4096, 'MAX_RESPONSE_BYTES': 2097152,
}


@pytest.fixture(autouse=True)
def isolate(monkeypatch):
    # Never inspect or print actual environment secrets.
    for name in ['ENABLED', 'PROVIDER', 'SOURCE', 'STORE', 'ANALYST', *LIMITS]:
        monkeypatch.delenv('INVESTIGATION_' + name, raising=False)
    for name in ['OPENAI_API_KEY', 'OPENAI_MODEL', 'APP_MODE']:
        monkeypatch.delenv(name, raising=False)


def test_defaults(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    cfg = load_settings()
    assert cfg.enabled is False
    assert cfg.provider == 'test'
    assert cfg.source == 'fixture'
    assert cfg.store.is_absolute()
    assert cfg.store.name == 'investigations.sqlite'
    assert cfg.store.parent.name == 'processed'
    assert cfg.store != cfg.store.with_name('fraudlens.sqlite')
    for name, maximum in LIMITS.items():
        assert getattr(cfg, name.lower()) == maximum


@pytest.mark.parametrize('provider', ['test', 'openai'])
@pytest.mark.parametrize('source', ['fixture', 'dataset'])
def test_environment_choices(monkeypatch, provider, source):
    monkeypatch.setenv('INVESTIGATION_PROVIDER', provider)
    monkeypatch.setenv('INVESTIGATION_SOURCE', source)
    monkeypatch.setenv('OPENAI_MODEL', 'explicit-synthetic-model-id')
    cfg = load_settings()
    assert cfg.provider == provider
    assert cfg.source == source


@pytest.mark.parametrize('name,value', [
    ('PROVIDER', 'other'), ('PROVIDER', ''), ('SOURCE', 'model'), ('SOURCE', ''),
    ('ENABLED', 'sometimes'), ('ENABLED', ''), ('STORE', ''), ('ANALYST', ''),
])
def test_invalid_environment(monkeypatch, name, value):
    monkeypatch.setenv('INVESTIGATION_' + name, value)
    with pytest.raises(ValueError):
        load_settings()


@pytest.mark.parametrize('name,maximum', list(LIMITS.items()))
@pytest.mark.parametrize('kind', ['zero', 'negative', 'above', 'nan', 'infinity', 'text', 'fraction'])
def test_limits_reject_invalid(monkeypatch, name, maximum, kind):
    value = {'zero': '0', 'negative': '-1', 'above': str(maximum + 1),
             'nan': 'NaN', 'infinity': 'Infinity', 'text': 'abc', 'fraction': '1.5'}[kind]
    monkeypatch.setenv('INVESTIGATION_' + name, value)
    with pytest.raises(ValueError):
        load_settings()


@pytest.mark.parametrize('name,maximum', list(LIMITS.items()))
@pytest.mark.parametrize('boundary', ['lower', 'upper'])
def test_limits_allow_positive_bounds(monkeypatch, name, maximum, boundary):
    value = 1 if boundary == 'lower' else maximum
    monkeypatch.setenv('INVESTIGATION_' + name, str(value))
    assert getattr(load_settings(), name.lower()) == value


@pytest.mark.parametrize('model', [None, '', '   '])
def test_real_provider_requires_explicit_model(monkeypatch, model):
    monkeypatch.setenv('INVESTIGATION_PROVIDER', 'openai')
    if model is not None:
        monkeypatch.setenv('OPENAI_MODEL', model)
    with pytest.raises(ValueError):
        load_settings()


def test_environment_settings_and_redaction(monkeypatch, tmp_path, caplog):
    key, model = 'canary-secret-not-real-003', 'canary-model-not-real-003'
    monkeypatch.setenv('OPENAI_API_KEY', key)
    monkeypatch.setenv('OPENAI_MODEL', model)
    monkeypatch.setenv('INVESTIGATION_ENABLED', 'true')
    monkeypatch.setenv('INVESTIGATION_STORE', str(tmp_path / 'investigations.sqlite'))
    monkeypatch.setenv('INVESTIGATION_ANALYST', 'authored-test-analyst')
    with caplog.at_level(logging.DEBUG):
        cfg = load_settings()
        assert cfg.enabled is True
        assert cfg.analyst == 'authored-test-analyst'
        assert cfg.store == tmp_path / 'investigations.sqlite'
        assert key not in repr(cfg) + str(cfg) + caplog.text
        assert model not in repr(cfg) + str(cfg) + caplog.text
        assert key not in cfg.model_dump_json()
        assert model not in cfg.model_dump_json()
        monkeypatch.setenv('INVESTIGATION_PROVIDER', model)
        with pytest.raises(ValueError) as exc:
            load_settings()
        assert key not in str(exc.value) + repr(exc.value) + caplog.text
        assert model not in str(exc.value) + repr(exc.value) + caplog.text


def test_disabled_import_and_startup_have_no_external_effects(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('Unexpected network or database initialization')

    monkeypatch.setattr(socket, 'create_connection', forbidden)
    monkeypatch.setattr(sqlite3, 'connect', forbidden)
    module = importlib.import_module('fraudlens.investigation.settings')
    importlib.reload(module)
    assert module.load_settings().enabled is False
    from fraudlens.main import create_app
    with TestClient(create_app()) as client:
        assert client.get('/api/health').json() == {'status': 'ok', 'mode': 'fixture'}
