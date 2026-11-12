"""Contract behavior checked against the independent foundation JSON Schema."""
import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ValidationError

from fraudlens import contracts

SCHEMA = json.loads(Path('specs/001-project-foundation/contracts/schemas.json').read_text())
TX = dict(transaction_id='TX-001', occurred_at='2026-01-01T10:00:00Z',
          sender_account='a', receiver_account='b', amount='1250.00', currency='EUR')
RISK = dict(transaction_id='TX-001', score=0.5, source='fixture',
            scorer_version='v1', scored_at='2026-01-01T10:00:00Z', explanation='Illustrative')
SUMMARY = dict(case_id='CASE-001', transaction_id='TX-001', score=0.5, score_source='fixture')
EXAMPLES = {
    'Transaction': TX, 'RiskAssessment': RISK, 'CaseSummary': SUMMARY,
    'CaseDetail': dict(case_id='CASE-001', transaction=TX, risk_assessment=RISK),
    'CaseList': dict(items=[SUMMARY]), 'Health': dict(status='ok', mode='fixture'),
    'Error': dict(error=dict(code='internal_error', message='Unavailable')),
}


def validator(name):
    return Draft202012Validator(
        {**SCHEMA, '$ref': f'#/$defs/{name}'}, format_checker=FormatChecker())


@pytest.mark.parametrize('name', EXAMPLES)
def test_roundtrip_and_required_closed_objects(name):
    payload = copy.deepcopy(EXAMPLES[name])
    model = getattr(contracts, name)
    validator(name).validate(payload)
    instance = model.model_validate(payload)
    validator(name).validate(instance.model_dump(mode='json'))
    assert model.model_validate_json(instance.model_dump_json()) == instance
    for field in payload:
        missing = {k: v for k, v in payload.items() if k != field}
        with pytest.raises(ValidationError):
            model.model_validate(missing)
    for extra in ['extra', 'isFraud', 'Is Laundering', 'reference_decision']:
        invalid = {**payload, extra: True}
        assert not validator(name).is_valid(invalid)
        with pytest.raises(ValidationError):
            model.model_validate(invalid)


INVALID = [
    ('Transaction', 'transaction_id', x) for x in ['TX-01', 'TX-0001', 'tx-001', 'TX-001\n', 1]
] + [
    ('CaseSummary', 'case_id', x) for x in ['CASE-1', 'case-001', 'CASE-001\n', 1]
] + [
    ('Transaction', field, x) for field in ['sender_account', 'receiver_account']
    for x in ['', 'a' * 121, 12, True]
] + [
    ('Transaction', 'amount', x) for x in [1.0, True, '-1.00', '01.00', '1.0', '1.000', '1e2', '1.00\n']
] + [
    ('Transaction', 'currency', x) for x in ['eur', 'EU', 'EURO', 'EUR\n', 1]
] + [
    (name, field, x) for name, field in [('Transaction', 'occurred_at'), ('RiskAssessment', 'scored_at')]
    for x in ['2026-02-30T10:00:00Z', '2026-01-01T10:00:00', '2026-01-01T10:00:00+00:00', 1]
] + [
    (name, 'score', x) for name in ['RiskAssessment', 'CaseSummary']
    for x in [-0.01, 1.01, '0.5', True, None]
] + [
    (name, field, x) for name, field in [('RiskAssessment', 'source'), ('CaseSummary', 'score_source')]
    for x in ['unknown', '', 1]
] + [
    ('RiskAssessment', field, x) for field, size in [('scorer_version', 80), ('explanation', 500)]
    for x in ['', 'a' * (size + 1), 1]
] + [('Health', 'status', 'bad'), ('Health', 'mode', 'model')]


@pytest.mark.parametrize('name,field,value', INVALID)
def test_invalid_fields(name, field, value):
    payload = {**EXAMPLES[name], field: value}
    assert not validator(name).is_valid(payload)
    with pytest.raises(ValidationError):
        getattr(contracts, name).model_validate(payload)


@pytest.mark.parametrize('name', ['RiskAssessment', 'CaseSummary'])
@pytest.mark.parametrize('score', [float('nan'), float('inf'), float('-inf')])
def test_nonfinite_scores(name, score):
    # Additional finite-number requirement: JSON Schema need not reject Python NaN.
    with pytest.raises(ValidationError):
        getattr(contracts, name).model_validate({**EXAMPLES[name], 'score': score})


@pytest.mark.parametrize('name,path', [
    ('CaseDetail', ['transaction']), ('CaseDetail', ['risk_assessment']),
    ('CaseList', ['items', 0]), ('Error', ['error']),
])
def test_nested_objects_are_closed(name, path):
    for label in ['isFraud', 'Is Laundering', 'reference_decision']:
        payload = copy.deepcopy(EXAMPLES[name])
        obj = payload
        for key in path:
            obj = obj[key]
        obj[label] = True
        assert not validator(name).is_valid(payload)
        with pytest.raises(ValidationError):
            getattr(contracts, name).model_validate(payload)


@pytest.mark.parametrize('score', [0, 1])
@pytest.mark.parametrize('source', ['fixture', 'rules', 'model'])
def test_score_boundaries_and_sources(score, source):
    payload = {**RISK, 'score': score, 'source': source, 'scorer_version': 'v' * 80,
               'explanation': 'e' * 500}
    validator('RiskAssessment').validate(contracts.RiskAssessment(**payload).model_dump(mode='json'))


@pytest.mark.parametrize('amount', ['0.00', '1.23', '12345678901234567890.99'])
def test_amount_and_account_boundaries(amount):
    payload = {**TX, 'amount': amount, 'sender_account': 'a' * 120, 'receiver_account': ' '}
    result = contracts.Transaction(**payload).model_dump(mode='json')
    assert result['amount'] == amount
    validator('Transaction').validate(result)


def test_empty_case_list():
    validator('CaseList').validate(contracts.CaseList(items=[]).model_dump(mode='json'))


def test_format_checker_rejects_invalid_calendar_date():
    payload = {**TX, 'occurred_at': '2026-02-30T10:00:00Z'}
    assert any(e.validator == 'format' for e in validator('Transaction').iter_errors(payload))


@pytest.mark.parametrize('code', ['invalid_request', 'case_not_found', 'internal_error'])
def test_error_codes_and_message_bounds(code):
    payload = {'error': {'code': code, 'message': 'm' * 200}}
    validator('Error').validate(contracts.Error(**payload).model_dump(mode='json'))
    for field, value in [('code', 'unknown'), ('message', ''), ('message', 'm' * 201)]:
        invalid = copy.deepcopy(payload)
        invalid['error'][field] = value
        assert not validator('Error').is_valid(invalid)
        with pytest.raises(ValidationError):
            contracts.Error(**invalid)
