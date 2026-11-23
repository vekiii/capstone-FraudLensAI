import math
from dataclasses import replace
from pathlib import Path

import pytest

from fraudlens.scoring.local_contributions import compute_local_contributions, stable_binary_score
from fraudlens.scoring.model_scorer import FeatureStore, ModelScorer, ModelUnavailable

ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / 'data/eval/ibm-day-lightgbm-unweighted-freeze-001/artifacts'
FEATURES = ROOT / 'data/processed/t219-ibm-day-60-20-20-v1'
CASE = ('ibm-hi-small:b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040:'
        'row:1500153')


@pytest.fixture(scope='module')
def frozen():
    if not ARTIFACTS.exists() or not FEATURES.exists():
        pytest.skip('ignored frozen inputs absent')
    return ModelScorer(ARTIFACTS), FeatureStore(FEATURES).get(CASE)


def test_reconstruction_and_unchanged_score(frozen):
    scorer, transaction = frozen
    before = scorer.score(transaction)
    result = compute_local_contributions(scorer, transaction)
    after = scorer.score(transaction)
    assert result['transaction_id'] == transaction.transaction_id
    assert result['score'] == before.risk_score == after.risk_score
    assert before.review_status == after.review_status
    assert len(result['matrix_contributions']) == 32
    assert len(result['groups']) == 11
    assert all(math.isfinite(x) for x in result['matrix_contributions'])
    assert math.isclose(result['base_value'] + math.fsum(result['matrix_contributions']),
                        result['raw_score'], rel_tol=0, abs_tol=1e-8)
    assert math.isclose(result['base_value'] + math.fsum(result['groups'].values()),
                        result['raw_score'], rel_tol=0, abs_tol=1e-8)
    assert math.isclose(stable_binary_score(result['raw_score'], 1.0), result['score'],
                        rel_tol=0, abs_tol=1e-12)
    assert result['base_value'] + sum(x['contribution'] for x in result['top3']) + result['remainder'] == pytest.approx(result['raw_score'], abs=1e-8)


def test_stable_sigmoid_edges():
    assert stable_binary_score(1000, 1) == 1
    assert stable_binary_score(-1000, 1) == 0
    with pytest.raises(ValueError):
        stable_binary_score(float('nan'), 1)


def test_unknown_category_uses_frozen_bucket(frozen):
    scorer, transaction = frozen
    altered = replace(transaction, features={**transaction.features,
                  'current_payment_currency': 'Novel currency'})
    result = compute_local_contributions(scorer, altered)
    assert len(result['matrix_contributions']) == 32
    assert math.isclose(result['base_value'] + math.fsum(result['groups'].values()),
                        result['raw_score'], abs_tol=1e-8)


def test_wrong_manifest_order_fails_closed(frozen):
    scorer, transaction = frozen
    original = scorer.manifest
    scorer.manifest = {**original, 'matrix_feature_order': list(reversed(original['matrix_feature_order']))}
    try:
        with pytest.raises(ModelUnavailable, match='order mismatch'):
            compute_local_contributions(scorer, transaction)
    finally:
        scorer.manifest = original


@pytest.mark.parametrize('corruption', [float('nan'), float('inf'), 1.0])
def test_corrupt_native_contribution_fails_closed(frozen, corruption):
    scorer, transaction = frozen
    native = scorer.booster

    class CorruptBooster:
        def __getattr__(self, name):
            return getattr(native, name)

        def predict(self, matrix, **kwargs):
            result = native.predict(matrix, **kwargs)
            if kwargs.get('pred_contrib'):
                result[0, 0] = corruption if not math.isfinite(corruption) else result[0, 0] + corruption
            return result

    scorer.booster = CorruptBooster()
    try:
        with pytest.raises(ModelUnavailable, match='shape or value|reconstruction'):
            compute_local_contributions(scorer, transaction)
    finally:
        scorer.booster = native
