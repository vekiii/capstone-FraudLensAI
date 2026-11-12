"""T016 framework error normalization and privacy-preserving application logs."""
import json
import logging
from pathlib import Path
from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator, FormatChecker

from fraudlens.contracts import CaseList
from fraudlens.main import create_app
from fraudlens.scoring import FixtureScorer
from fraudlens.settings import Settings

SCHEMA = json.loads(
    (Path(__file__).resolve().parents[3] /
     'specs/001-project-foundation/contracts/schemas.json').read_text(encoding='utf-8'))
PRIVATE = r'PRIVATE_EXCEPTION credential=PRIVATE_KEY C:\private\accounts.json'


def assert_error(response, status, code):
    assert response.status_code == status
    assert response.headers['content-type'].startswith('application/json')
    payload = response.json()
    Draft202012Validator(
        {**SCHEMA, '$ref': '#/$defs/Error'}, format_checker=FormatChecker(),
    ).validate(payload)
    assert payload['error']['code'] == code
    assert 'PRIVATE_' not in response.text
    assert 'Traceback' not in response.text
    assert 'C:\\' not in response.text


def assert_redacted_error_log(caplog):
    records = [record for record in caplog.records if record.name == 'fraudlens.main']
    assert records, 'Internal failures must produce a server-side error event'
    for record in records:
        assert record.levelno >= logging.ERROR
        assert 'PRIVATE_' not in record.getMessage()
        assert 'C:\\' not in record.getMessage()
        assert record.exc_info is None


def test_framework_not_found_uses_public_envelope():
    with TestClient(create_app(settings=Settings())) as client:
        response = client.get('/PRIVATE_UNREGISTERED_ROUTE')
    assert_error(response, 404, 'case_not_found')


def test_framework_method_not_allowed_preserves_status_and_allow_header():
    with TestClient(create_app(settings=Settings())) as client:
        response = client.post('/api/health')
    assert_error(response, 405, 'invalid_request')
    assert 'GET' in response.headers['allow']


def test_framework_request_validation_discards_rejected_input():
    app = create_app(settings=Settings())

    @app.get('/__test/request-validation')
    def probe(count: int):
        return {'count': count}

    with TestClient(app) as client:
        response = client.get('/__test/request-validation', params={'count': PRIVATE})
    assert_error(response, 422, 'invalid_request')


def test_framework_response_validation_is_generic_and_logged(caplog):
    caplog.set_level(logging.ERROR, logger='fraudlens.main')
    app = create_app(settings=Settings())

    @app.get('/__test/response-validation', response_model=CaseList)
    def probe():
        return {'items': PRIVATE}

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get('/__test/response-validation')
    assert_error(response, 500, 'internal_error')
    assert_redacted_error_log(caplog)


def test_http_exception_internal_detail_is_not_public_or_logged(caplog):
    caplog.set_level(logging.ERROR, logger='fraudlens.main')
    app = create_app(settings=Settings())

    @app.get('/__test/http-error')
    def probe():
        raise HTTPException(status_code=500, detail=PRIVATE)

    with TestClient(app) as client:
        response = client.get('/__test/http-error')
    assert_error(response, 500, 'internal_error')
    assert_redacted_error_log(caplog)


def test_unhandled_programming_error_returns_safe_500_without_swallowing_exception(caplog):
    caplog.set_level(logging.ERROR, logger='fraudlens.main')
    app = create_app(settings=Settings())

    @app.get('/__test/programming-error')
    def probe():
        raise RuntimeError(PRIVATE)

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get('/__test/programming-error')
    assert_error(response, 500, 'internal_error')
    with TestClient(app, raise_server_exceptions=True) as client:
        with pytest.raises(RuntimeError, match='PRIVATE_EXCEPTION'):
            client.get('/__test/programming-error')
    assert_redacted_error_log(caplog)


@pytest.mark.parametrize('failure', ['fixture', 'scorer'])
def test_known_service_failures_are_logged_without_sensitive_details(tmp_path, monkeypatch, caplog, failure):
    caplog.set_level(logging.ERROR, logger='fraudlens.main')
    settings = Settings()
    if failure == 'fixture':
        settings = Settings(fixture_path=tmp_path / 'PRIVATE_MISSING_FIXTURE.json')
    else:
        monkeypatch.setattr(FixtureScorer, 'score', Mock(side_effect=RuntimeError(PRIVATE)))
    with TestClient(create_app(settings=settings), raise_server_exceptions=False) as client:
        response = client.get('/api/cases')
    assert_error(response, 500, 'internal_error')
    assert_redacted_error_log(caplog)
