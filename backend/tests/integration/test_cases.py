"""US2 case delivery contracts; T012 intentionally precedes the case routes."""
import importlib
import json
import math
import re
from pathlib import Path
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator, FormatChecker

from fraudlens.contracts import RiskAssessment
from fraudlens.main import create_app
from fraudlens.settings import Settings

ROOT = Path(__file__).resolve().parents[3]
SCHEMA = json.loads(
    (ROOT / 'specs/001-project-foundation/contracts/schemas.json').read_text(encoding='utf-8'))
ENDPOINTS = ['/api/cases', '/api/cases/{case_id}']
PRIVATE_ERRORS = [
    r'PRIVATE_SCORER_FAILURE at C:\private\fraudlens\accounts.json',
    'PRIVATE_REPOSITORY_FAILURE at /private/fraudlens/accounts.json',
]


@pytest.fixture
def app():
    # Explicit configuration isolates this suite from the shell's APP_MODE.
    return create_app(settings=Settings())


@pytest.fixture
def client(app):
    # Exercise the public 500 response instead of re-raising server exceptions.
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


def assert_schema(payload, name):
    Draft202012Validator(
        {**SCHEMA, '$ref': f'#/$defs/{name}'},
        format_checker=FormatChecker(),
    ).validate(payload)


def success_payload(response, name):
    assert response.status_code == 200, 'Case delivery must exist before boundary checks'
    assert response.headers['content-type'].startswith('application/json')
    payload = response.json()
    assert_schema(payload, name)
    return payload


def existing_case_path(client, path):
    if '{case_id}' not in path:
        return path
    items = success_payload(client.get('/api/cases'), 'CaseList')['items']
    assert items, 'A detail boundary check needs an existing synthetic case'
    return path.format(case_id=items[0]['case_id'])


def assert_public_fixture_payload(payload):
    """Check labels recursively, including free-text evaluation claims."""
    forbidden = {
        'label', 'target', 'isfraud', 'fraudlabel', 'islaundering',
        'groundtruth', 'groundtruthlabel', 'referencedecision', 'referenceanswer',
        'accuracy', 'precision', 'recall', 'auc', 'f1', 'evaluation',
    }
    if isinstance(payload, dict):
        for key, value in payload.items():
            assert re.sub(r'[^a-z0-9]', '', key.lower()) not in forbidden
            assert_public_fixture_payload(value)
    elif isinstance(payload, list):
        for value in payload:
            assert_public_fixture_payload(value)
    elif isinstance(payload, str):
        assert not re.search(
            r'\b(?:accuracy|precision|recall|f1|roc.?auc|average precision)'
            r'\s*(?:of|is|=|:)?\s*\d', payload, re.IGNORECASE)


def assert_error(response, status, code):
    assert response.status_code == status
    assert response.headers['content-type'].startswith('application/json')
    payload = response.json()
    assert_schema(payload, 'Error')
    assert set(payload) == {'error'}
    assert set(payload['error']) == {'code', 'message'}
    assert payload['error']['code'] == code
    text = response.text
    for private in PRIVATE_ERRORS:
        assert private not in text
    assert not re.search(
        r'Traceback|RuntimeError|ValidationError|FileNotFoundError|'
        r'PRIVATE_\w+|[A-Za-z]:[\\/]|\\\\|(?:/[\w.-]+){2,}', text)
    return payload


def fixture_scorer_class(client):
    # Assert the missing behavior in the test body before attempting the future
    # scorer seam. Missing routes therefore produce assertion failures, not
    # import/fixture errors or a made-up substitute implementation.
    success_payload(client.get('/api/cases'), 'CaseList')
    module_spec = importlib.util.find_spec('fraudlens.scoring')
    assert module_spec is not None, 'Fixture scoring has not been implemented'
    module = importlib.import_module('fraudlens.scoring')
    scorer = getattr(module, 'FixtureScorer', None)
    assert scorer is not None, 'A patchable fixture scorer is required for boundary checks'
    return scorer


def test_list_has_exactly_three_synthetic_cases_in_stable_id_order(client):
    first = success_payload(client.get('/api/cases'), 'CaseList')
    second = success_payload(client.get('/api/cases'), 'CaseList')
    assert first == second
    items = first['items']
    assert len(items) == 3
    case_ids = [item['case_id'] for item in items]
    assert case_ids == sorted(case_ids)
    assert len(set(case_ids)) == 3
    assert len({item['transaction_id'] for item in items}) == 3
    for item in items:
        assert item['score_source'] == 'fixture'
        assert math.isfinite(item['score'])


def test_list_and_all_details_agree_on_identity_score_and_source(client):
    items = success_payload(client.get('/api/cases'), 'CaseList')['items']
    assert len(items) == 3  # Avoid vacuous agreement when delivery is empty.
    for item in items:
        path = f"/api/cases/{item['case_id']}"
        detail = success_payload(client.get(path), 'CaseDetail')
        assert detail == success_payload(client.get(path), 'CaseDetail')
        transaction = detail['transaction']
        risk = detail['risk_assessment']
        assert detail['case_id'] == item['case_id']
        assert transaction['transaction_id'] == risk['transaction_id'] == item['transaction_id']
        assert risk['score'] == item['score']
        assert risk['source'] == item['score_source'] == 'fixture'
        assert risk['scorer_version'] == 'fixture-v1'
        assert math.isfinite(risk['score'])
        assert 'illustrative' in risk['explanation'].lower()
        assert_public_fixture_payload(detail)


def test_well_formed_unknown_case_returns_generic_404(client):
    assert_error(client.get('/api/cases/CASE-999'), 404, 'case_not_found')


@pytest.mark.parametrize('case_id', [
    'CASE-1', 'CASE-0001', 'case-001', 'TX-001', 'CASE-ABC',
    'CASE-001%0A', 'CASE-%EF%BC%90%EF%BC%90%EF%BC%91',
])
def test_malformed_case_id_returns_normalized_422(client, case_id):
    assert_error(client.get(f'/api/cases/{case_id}'), 422, 'invalid_request')


def test_empty_collection_returns_exact_contract_response(tmp_path):
    fixture_path = tmp_path / 'empty-cases.json'
    fixture_path.write_text('[]', encoding='utf-8')
    app = create_app(settings=Settings(fixture_path=fixture_path))
    with TestClient(app, raise_server_exceptions=False) as client:
        payload = success_payload(client.get('/api/cases'), 'CaseList')
    assert payload == {'items': []}


@pytest.mark.parametrize('path,name', [
    ('/api/cases', 'CaseList'), ('/api/cases/{case_id}', 'CaseDetail'),
])
def test_success_payloads_are_closed_and_have_no_labels_or_evaluation_claims(client, path, name):
    # The independent schema closes every object, including nested transactions,
    # assessments and list items. This checks actual HTTP output, not model types.
    payload = success_payload(client.get(existing_case_path(client, path)), name)
    assert_public_fixture_payload(payload)


INVALID_RISK_FIELDS = [
    ('score', -0.01), ('score', 1.01), ('score', float('nan')),
    ('score', float('inf')), ('score', float('-inf')), ('score', '0.5'),
    ('score', True), ('score', None), ('source', 'unknown'),
    ('scorer_version', ''), ('explanation', ''),
    ('scored_at', '2026-02-30T10:00:00Z'),
]


@pytest.mark.parametrize('path', ENDPOINTS)
@pytest.mark.parametrize('field,value', INVALID_RISK_FIELDS)
def test_invalid_scorer_output_returns_generic_500(client, monkeypatch, path, field, value):
    scorer = fixture_scorer_class(client)
    path = existing_case_path(client, path)

    def invalid_score(transaction):
        # Deliberately bypass construction validation: case delivery must protect
        # HTTP clients from an invalid upstream result, not trust its Python type.
        fields = dict(
            transaction_id=transaction.transaction_id, score=0.5, source='fixture',
            scorer_version='fixture-v1', scored_at='2026-01-01T10:00:00Z',
            explanation='Illustrative synthetic score; no ML inference performed.',
        )
        fields[field] = value
        return RiskAssessment.model_construct(**fields)

    score = Mock(side_effect=invalid_score)
    monkeypatch.setattr(scorer, 'score', score)
    assert_error(client.get(path), 500, 'internal_error')
    assert score.called, 'The request must exercise the injected invalid scorer'


@pytest.mark.parametrize('path', ENDPOINTS)
def test_wrong_transaction_scorer_result_is_rejected(client, monkeypatch, path):
    scorer = fixture_scorer_class(client)
    path = existing_case_path(client, path)

    def mismatched_score(transaction):
        return RiskAssessment(
            transaction_id='TX-998' if transaction.transaction_id != 'TX-998' else 'TX-997',
            score=0.5, source='fixture', scorer_version='fixture-v1',
            scored_at='2026-01-01T10:00:00Z', explanation='Illustrative synthetic score.',
        )

    score = Mock(side_effect=mismatched_score)
    monkeypatch.setattr(scorer, 'score', score)
    assert_error(client.get(path), 500, 'internal_error')
    assert score.called


@pytest.mark.parametrize('path', ENDPOINTS)
def test_scorer_exceptions_are_generic_and_never_disclose_internal_details(client, monkeypatch, path):
    scorer = fixture_scorer_class(client)
    path = existing_case_path(client, path)
    errors = []
    for private in PRIVATE_ERRORS:
        score = Mock(side_effect=RuntimeError(private))
        monkeypatch.setattr(scorer, 'score', score)
        errors.append(assert_error(client.get(path), 500, 'internal_error'))
        assert score.called
    # No dependence on private exception text; the contract does not mandate a
    # particular English message for internal_error.
    assert errors[0] == errors[1]


@pytest.mark.parametrize('path', ['/api/cases', '/api/cases/CASE-001'])
def test_missing_repository_returns_generic_500_without_file_path(tmp_path, path):
    fixture_path = tmp_path / 'PRIVATE_REPOSITORY_FAILURE' / 'missing.json'
    app = create_app(settings=Settings(fixture_path=fixture_path))
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(path)
    assert_error(response, 500, 'internal_error')
    assert str(fixture_path) not in response.text
