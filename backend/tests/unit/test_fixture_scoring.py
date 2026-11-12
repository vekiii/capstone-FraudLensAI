"""T012 fixture-scorer behavior, with no production scorer implemented here."""
import importlib
import json
import math
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from fraudlens.contracts import RiskAssessment, Transaction

SCHEMA = json.loads(
    (Path(__file__).resolve().parents[3] /
     'specs/001-project-foundation/contracts/schemas.json').read_text(encoding='utf-8'))


@pytest.fixture(params=['TX-001', 'TX-002', 'TX-003'])
def transaction(request):
    # Test-only input, not the T014 production fixture collection.
    return Transaction(
        transaction_id=request.param, occurred_at='2026-01-01T10:00:00Z',
        sender_account='DEMO-BANK-A:001', receiver_account='DEMO-BANK-B:002',
        amount='1250.00', currency='EUR',
    )


def fixture_scorer():
    # Keep test collection valid before T015; report the absent scoring behavior
    # as a clear assertion failure rather than ModuleNotFoundError during setup.
    module_spec = importlib.util.find_spec('fraudlens.scoring')
    assert module_spec is not None, 'Missing fixture scoring behavior (T015 not implemented)'
    module = importlib.import_module('fraudlens.scoring')
    scorer = getattr(module, 'FixtureScorer', None)
    assert scorer is not None, 'Missing fixture scorer implementing score(Transaction)'
    return scorer()


def test_fixture_score_is_deterministic_across_calls_and_instances(transaction):
    scorer = fixture_scorer()
    before = transaction.model_dump(mode='json')
    first = scorer.score(transaction)
    second = scorer.score(transaction)
    other_instance = fixture_scorer().score(transaction.model_copy(deep=True))
    assert isinstance(first, RiskAssessment)
    assert isinstance(second, RiskAssessment)
    assert isinstance(other_instance, RiskAssessment)
    # Includes stable scored_at, source, version and explanation, not only score.
    assert first.model_dump(mode='json') == second.model_dump(mode='json')
    assert first.model_dump(mode='json') == other_instance.model_dump(mode='json')
    assert transaction.model_dump(mode='json') == before


def test_fixture_score_has_required_metadata_and_closed_public_shape(transaction):
    result = fixture_scorer().score(transaction)
    assert isinstance(result, RiskAssessment)
    payload = result.model_dump(mode='json')
    Draft202012Validator(
        {**SCHEMA, '$ref': '#/$defs/RiskAssessment'}, format_checker=FormatChecker(),
    ).validate(payload)
    assert set(payload) == {
        'transaction_id', 'score', 'source', 'scorer_version', 'scored_at', 'explanation',
    }
    assert payload['transaction_id'] == transaction.transaction_id
    assert type(payload['score']) in (float, int)  # bool must not count as a score.
    assert math.isfinite(payload['score'])
    assert 0 <= payload['score'] <= 1
    assert payload['source'] == 'fixture'
    assert payload['scorer_version'] == 'fixture-v1'
    assert 'illustrative' in payload['explanation'].lower()
