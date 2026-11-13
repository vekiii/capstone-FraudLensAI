"""T020: replace scoring through case delivery, without changing shipped fixtures."""
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from fraudlens.cases import CaseScoringError, CaseService
from fraudlens.contracts import RiskAssessment, Transaction
from fraudlens.scoring import FixtureScorer
from fraudlens.settings import Settings

SCHEMA = json.loads(
    (Path(__file__).resolve().parents[3] /
     'specs/001-project-foundation/contracts/schemas.json').read_text(encoding='utf-8'))


class RulesScorer:
    """Test-only structural adapter; its constant is not an AML rule or probability."""

    def __init__(self, value: float = 0.23):
        self.value = value
        self.seen_ids: list[str] = []

    def score(self, transaction: Transaction) -> RiskAssessment:
        self.seen_ids.append(transaction.transaction_id)
        return RiskAssessment(
            transaction_id=transaction.transaction_id, score=self.value, source='rules',
            scorer_version='test-rules-v1', scored_at=transaction.occurred_at,
            explanation='Test-only illustrative rules result; no AML or ML evaluation.',
        )


class InvalidRulesScorer(RulesScorer):
    """Bypass model construction checks to exercise delivery's own validation."""

    def __init__(self, updates: dict[str, object]):
        super().__init__()
        self.updates = updates

    def score(self, transaction: Transaction) -> RiskAssessment:
        result = super().score(transaction)
        # A list must fail as a whole even after the first assessment was valid.
        if transaction.transaction_id == 'TX-002':
            return result.model_copy(update=self.updates)
        return result


class FailingRulesScorer(RulesScorer):
    def score(self, transaction: Transaction) -> RiskAssessment:
        result = super().score(transaction)
        if transaction.transaction_id == 'TX-002':
            raise RuntimeError('PRIVATE_TEST_SCORER_FAILURE')
        return result


@pytest.fixture
def fixture_path():
    path = Settings().fixture_path
    before = path.read_bytes()
    yield path
    assert path.read_bytes() == before, 'Scorer substitution must not rewrite shipped fixtures'


def assert_schema(payload, name):
    Draft202012Validator(
        {**SCHEMA, '$ref': f'#/$defs/{name}'}, format_checker=FormatChecker(),
    ).validate(payload)


def deliver(service, operation):
    if operation == 'list':
        return service.list_cases()
    return service.get_case('CASE-002')


def assert_rejected(service, scorer, operation):
    with pytest.raises(CaseScoringError) as caught:
        deliver(service, operation)
    assert str(caught.value) == 'Unable to score case.'
    assert caught.value.__cause__ is None
    assert caught.value.__suppress_context__ is True
    expected = ['TX-001', 'TX-002'] if operation == 'list' else ['TX-002']
    assert scorer.seen_ids == expected


def test_rules_scorer_replaces_fixture_for_every_case_without_delivery_changes(fixture_path):
    fixture_service = CaseService(fixture_path, FixtureScorer())
    baseline = fixture_service.list_cases()
    scorer = RulesScorer()
    service = CaseService(fixture_path, scorer)

    summaries = service.list_cases()
    assert_schema(summaries.model_dump(mode='json'), 'CaseList')
    assert len(summaries.items) == 3
    assert [(item.case_id, item.transaction_id) for item in summaries.items] == [
        (item.case_id, item.transaction_id) for item in baseline.items
    ]
    for summary, original in zip(summaries.items, baseline.items, strict=True):
        detail = service.get_case(summary.case_id)
        assert_schema(detail.model_dump(mode='json'), 'CaseDetail')
        assert detail.case_id == summary.case_id
        assert detail.transaction == fixture_service.get_case(summary.case_id).transaction
        assert detail.transaction.transaction_id == summary.transaction_id
        assert detail.risk_assessment.transaction_id == summary.transaction_id
        assert detail.risk_assessment.score == summary.score == 0.23
        assert detail.risk_assessment.score != original.score
        assert detail.risk_assessment.source == summary.score_source == 'rules'
        assert detail.risk_assessment.scorer_version == 'test-rules-v1'
        assert detail.risk_assessment.scored_at == detail.transaction.occurred_at
        assert detail.risk_assessment.explanation.startswith('Test-only illustrative rules')

    assert scorer.seen_ids == ['TX-001', 'TX-002', 'TX-003', 'TX-001', 'TX-002', 'TX-003']
    # An injected adapter is local to its service, not a new production default.
    assert CaseService(fixture_path, FixtureScorer()).list_cases() == baseline


@pytest.mark.parametrize('operation', ['list', 'detail'])
@pytest.mark.parametrize('value', [0.0, 1.0])
def test_rules_score_bounds_are_delivered_without_clamping(fixture_path, operation, value):
    service = CaseService(fixture_path, RulesScorer(value))
    result = deliver(service, operation)
    if operation == 'list':
        assert_schema(result.model_dump(mode='json'), 'CaseList')
        assert len(result.items) == 3
        assert all(item.score == value and item.score_source == 'rules' for item in result.items)
    else:
        assert_schema(result.model_dump(mode='json'), 'CaseDetail')
        assert result.risk_assessment.score == value
        assert result.risk_assessment.source == 'rules'


@pytest.mark.parametrize('operation', ['list', 'detail'])
@pytest.mark.parametrize('value', [-0.01, 1.01, float('nan'), float('inf'), float('-inf')],
                         ids=['negative', 'above-one', 'nan', 'positive-inf', 'negative-inf'])
def test_invalid_rules_scores_reject_delivery(fixture_path, operation, value):
    scorer = InvalidRulesScorer({'score': value})
    assert_rejected(CaseService(fixture_path, scorer), scorer, operation)


@pytest.mark.parametrize('operation', ['list', 'detail'])
def test_rules_assessment_for_another_transaction_rejects_delivery(fixture_path, operation):
    scorer = InvalidRulesScorer({'transaction_id': 'TX-999'})
    assert_rejected(CaseService(fixture_path, scorer), scorer, operation)


@pytest.mark.parametrize('operation', ['list', 'detail'])
def test_rules_failure_rejects_delivery_without_fixture_fallback(fixture_path, operation):
    scorer = FailingRulesScorer()
    assert_rejected(CaseService(fixture_path, scorer), scorer, operation)
