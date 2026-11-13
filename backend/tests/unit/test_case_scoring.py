"""T015 scorer rules and case delivery validation; no HTTP endpoints."""
import importlib
import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ConfigDict

from fraudlens.cases import FixtureCase, load_cases
from fraudlens.contracts import RiskAssessment, Transaction

SCHEMA = json.loads(
    (Path(__file__).resolve().parents[3] /
     'specs/001-project-foundation/contracts/schemas.json').read_text(encoding='utf-8'))


@pytest.fixture
def transaction():
    return Transaction(
        transaction_id='TX-001', occurred_at='2026-01-05T09:15:00Z',
        sender_account='DEMO-BANK-A:SYN-ACCOUNT-001', receiver_account='DEMO-BANK-B:SYN-ACCOUNT-002',
        amount='1250.00', currency='EUR',
    )


@pytest.fixture
def case(transaction):
    return FixtureCase(case_id='CASE-001', transaction=transaction)


def scoring_module():
    spec = importlib.util.find_spec('fraudlens.scoring')
    assert spec is not None, 'Missing fixture scorer/protocol (T015)'
    return importlib.import_module('fraudlens.scoring')


def case_delivery():
    module = importlib.import_module('fraudlens.cases')
    assert callable(getattr(module, 'score_case', None)), 'Missing validated case scoring (T015)'
    return module


def risk_fields(transaction):
    return dict(
        transaction_id=transaction.transaction_id, score=0.52, source='fixture',
        scorer_version='fixture-v1', scored_at=transaction.occurred_at,
        explanation='Illustrative synthetic score; no ML inference performed.',
    )


def assert_case_rejected(module, case, scorer):
    with pytest.raises(module.CaseScoringError) as caught:
        module.score_case(case, scorer)
    assert str(caught.value) == 'Unable to score case.'
    assert 'PRIVATE_' not in repr(caught.value)
    assert caught.value.__cause__ is None
    assert caught.value.__suppress_context__ is True


@pytest.mark.parametrize('tx_id,expected', [
    ('TX-000', 0.10), ('TX-001', 0.75), ('TX-002', 0.40),
    ('TX-003', 0.10), ('TX-004', 0.75), ('TX-999', 0.10),
])
def test_documented_id_rotation_uses_constants_for_any_valid_id(transaction, tx_id, expected):
    module = scoring_module()
    transaction.transaction_id = tx_id
    result = module.FixtureScorer().score(transaction)
    assert result.score == expected
    assert result.transaction_id == tx_id
    assert result.source == 'fixture'
    assert result.scorer_version == 'fixture-v1'


@pytest.mark.parametrize('occurred_at', ['2026-01-05T09:15:00Z', '2030-12-31T23:59:59Z'])
def test_scored_at_is_transaction_time_not_wall_clock(transaction, occurred_at):
    module = scoring_module()
    transaction.occurred_at = occurred_at
    result = module.FixtureScorer().score(transaction)
    assert result.scored_at == occurred_at
    assert 'illustrative' in result.explanation.lower()
    assert 'synthetic' in result.explanation.lower()
    assert 'no ml inference' in result.explanation.lower()


def test_complete_assessments_are_independent_of_call_order_and_instances():
    module = scoring_module()
    records = load_cases()
    scorer = module.FixtureScorer()
    first = {case.case_id: scorer.score(case.transaction) for case in records}
    reversed_results = {
        case.case_id: module.FixtureScorer().score(case.transaction) for case in reversed(records)
    }
    assert first == reversed_results


INVALID_TRANSACTIONS = [
    ('transaction_id', 'TX-1'), ('transaction_id', 'TX-001\n'),
    ('amount', -1), ('amount', '-1.00'), ('amount', '1.0'),
    ('sender_account', ''), ('receiver_account', 'a' * 121),
    ('currency', 'eur'), ('currency', 'EUR\n'),
    ('occurred_at', '2026-02-30T10:00:00Z'),
    ('occurred_at', '2026-01-05T09:15:00+00:00'),
]


@pytest.mark.parametrize('field,value', INVALID_TRANSACTIONS)
def test_fixture_scorer_revalidates_mutated_transactions(transaction, field, value):
    module = scoring_module()
    setattr(transaction, field, value)  # Existing models do not validate assignment.
    with pytest.raises(module.ScoringError, match='Unable to score synthetic transaction'):
        module.FixtureScorer().score(transaction)


@pytest.mark.parametrize('value', [None, {}, 'TX-001'])
def test_fixture_scorer_rejects_wrong_input_types(value):
    module = scoring_module()
    with pytest.raises(module.ScoringError):
        module.FixtureScorer().score(value)


def test_fixture_scorer_rejects_constructed_transaction_missing_required_field(transaction):
    module = scoring_module()
    fields = transaction.model_dump()
    del fields['amount']
    invalid = Transaction.model_construct(**fields)
    with pytest.raises(module.ScoringError):
        module.FixtureScorer().score(invalid)


def test_fixture_scorer_rejects_unvalidated_extra_label(transaction):
    module = scoring_module()
    invalid = transaction.model_copy(update={'is_fraud': True})
    with pytest.raises(module.ScoringError):
        module.FixtureScorer().score(invalid)


def test_score_case_returns_closed_canonical_detail_without_mutating_inputs(case):
    module = case_delivery()
    scorer = scoring_module().FixtureScorer()
    before = case.model_dump(mode='json')
    detail = module.score_case(case, scorer)
    Draft202012Validator(
        {**SCHEMA, '$ref': '#/$defs/CaseDetail'}, format_checker=FormatChecker(),
    ).validate(detail.model_dump(mode='json'))
    assert detail.case_id == case.case_id
    assert detail.transaction == case.transaction
    assert detail.risk_assessment.transaction_id == case.transaction.transaction_id
    assert case.model_dump(mode='json') == before


def test_case_boundary_uses_injected_scorer_once_without_replacing_its_score(case):
    module = case_delivery()
    scorer = Mock()
    scorer.score.return_value = RiskAssessment(**risk_fields(case.transaction))
    detail = module.score_case(case, scorer)
    scorer.score.assert_called_once()
    assert scorer.score.call_args.args[0] == case.transaction
    assert detail.risk_assessment.score == 0.52


INVALID_RISK_FIELDS = [
    ('score', -0.01), ('score', 1.01), ('score', float('nan')),
    ('score', float('inf')), ('score', float('-inf')), ('score', '0.5'),
    ('score', True), ('score', None), ('source', 'unknown'),
    ('transaction_id', 'TX-01'), ('transaction_id', 'TX-001\n'),
    ('scorer_version', ''), ('scorer_version', 'v' * 81),
    ('explanation', ''), ('explanation', 'e' * 501),
    ('scored_at', '2026-02-30T10:00:00Z'), ('scored_at', '2026-01-01T10:00:00+00:00'),
]


@pytest.mark.parametrize('field,value', INVALID_RISK_FIELDS)
def test_case_boundary_revalidates_invalid_risk_instances(case, field, value):
    module = case_delivery()
    fields = risk_fields(case.transaction)
    fields[field] = value
    scorer = Mock()
    scorer.score.return_value = RiskAssessment.model_construct(**fields)
    assert_case_rejected(module, case, scorer)
    scorer.score.assert_called_once()


@pytest.mark.parametrize('field', [
    'transaction_id', 'score', 'source', 'scorer_version', 'scored_at', 'explanation',
])
def test_case_boundary_rejects_missing_assessment_fields(case, field):
    module = case_delivery()
    fields = risk_fields(case.transaction)
    del fields[field]
    scorer = Mock()
    scorer.score.return_value = RiskAssessment.model_construct(**fields)
    assert_case_rejected(module, case, scorer)


@pytest.mark.parametrize('value', [None, {}, 'PRIVATE_INVALID_ASSESSMENT'])
def test_case_boundary_rejects_non_assessment_results(case, value):
    module = case_delivery()
    scorer = Mock()
    scorer.score.return_value = value
    assert_case_rejected(module, case, scorer)


@pytest.mark.parametrize('field', ['unexpected', 'confirmed_fraud', 'model_accuracy'])
def test_case_boundary_rejects_unvalidated_extra_assessment_fields(case, field):
    module = case_delivery()
    valid = RiskAssessment(**risk_fields(case.transaction))
    scorer = Mock()
    scorer.score.return_value = valid.model_copy(update={field: True})
    assert_case_rejected(module, case, scorer)


def test_case_boundary_rejects_extras_from_a_permissive_model_subclass(case):
    module = case_delivery()

    class PermissiveAssessment(RiskAssessment):
        model_config = ConfigDict(extra='allow')

    scorer = Mock()
    scorer.score.return_value = PermissiveAssessment(**risk_fields(case.transaction), private=True)
    assert_case_rejected(module, case, scorer)


def test_case_boundary_rejects_a_valid_assessment_for_the_wrong_transaction(case):
    module = case_delivery()
    scorer = Mock()
    scorer.score.return_value = RiskAssessment(**{
        **risk_fields(case.transaction), 'transaction_id': 'TX-002',
    })
    assert_case_rejected(module, case, scorer)


@pytest.mark.parametrize('field,value', [('transaction_id', 'TX-002'), ('amount', '0.00')])
def test_scorer_cannot_mutate_the_transaction_it_is_scoring(case, field, value):
    module = case_delivery()
    before = case.model_dump(mode='json')

    def mutate(transaction):
        setattr(transaction, field, value)
        return RiskAssessment(**risk_fields(transaction))

    scorer = Mock()
    scorer.score.side_effect = mutate
    assert_case_rejected(module, case, scorer)
    assert case.model_dump(mode='json') == before


@pytest.mark.parametrize('kind', ['case_id', 'transaction', 'extra'])
def test_case_boundary_revalidates_case_inputs_before_calling_scorer(case, kind):
    module = case_delivery()
    if kind == 'case_id':
        case.case_id = 'CASE-1'
    elif kind == 'transaction':
        case.transaction.amount = '-1.00'
    else:
        case = case.model_copy(update={'fraud_label': True})
    scorer = Mock()
    assert_case_rejected(module, case, scorer)
    scorer.score.assert_not_called()


def test_case_boundary_raises_generic_error_instead_of_falling_back_on_scorer_failure(case):
    module = case_delivery()
    scorer = Mock()
    scorer.score.side_effect = RuntimeError('PRIVATE_FAILURE C:\\private\\model.json')
    assert_case_rejected(module, case, scorer)
    scorer.score.assert_called_once()


def test_validated_detail_does_not_share_mutable_input_or_upstream_result(case):
    module = case_delivery()
    scorer = Mock()
    upstream = RiskAssessment(**risk_fields(case.transaction))
    scorer.score.return_value = upstream
    detail = module.score_case(case, scorer)
    case.transaction.amount = '0.00'
    upstream.score = 0.99
    assert detail.transaction.amount == '1250.00'
    assert detail.risk_assessment.score == 0.52
