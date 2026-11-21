"""T233 pre-parser integrity stop for the opt-in selected model."""
import lightgbm as lgb
import numpy as np
import pytest

from fraudlens.scoring.model_scorer import (
    THRESHOLD,
    FeatureTransaction,
    ModelScorer,
    ModelUnavailable,
)
from fraudlens.training.boundaries import TrainingPreprocessor

ID = 'ibm-hi-small:' + 'b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040' + ':row:1'
FEATURES = {
    'sender_out_count_24h': 2, 'sender_distinct_receivers_24h': 1,
    'sender_paid_count_same_currency_24h': 2,
    'sender_paid_sum_same_currency_24h': '12.50',
    'receiver_in_count_24h': 1, 'receiver_distinct_senders_24h': 1,
    'receiver_received_count_same_currency_24h': 1,
    'receiver_received_sum_same_currency_24h': '8.00',
    'current_amount_paid_log1p': 1.2,
    'current_payment_currency': 'New currency', 'current_payment_format': 'ACH',
}


class Booster:
    def __init__(self, score):
        self.value = score
        self.matrix = None

    def predict(self, matrix, **_kwargs):
        self.matrix = matrix
        return [self.value]


def synthetic_scorer(score):
    scorer = ModelScorer.__new__(ModelScorer)
    scorer.booster = Booster(score)
    scorer.preprocessor = TrainingPreprocessor(
        tuple(f'C{n:02}' for n in range(15)) + ('__UNKNOWN__',),
        ('ACH', 'Cash', 'Cheque', 'Credit Card', 'Wire', 'Other', '__UNKNOWN__'))
    return scorer


def test_incompatible_manifest_stops_before_native_parser(tmp_path, monkeypatch):
    artifact = tmp_path / 'selected-unweighted-lightgbm'
    artifact.mkdir()
    (artifact / 'manifest.json').write_bytes(b'{"tampered":true}')
    called = []
    monkeypatch.setattr(lgb, 'Booster', lambda **_kwargs: called.append(True))
    with pytest.raises(ModelUnavailable):
        ModelScorer(tmp_path)
    assert called == []


def test_frozen_threshold_and_unknown_bucket_without_vocab_learning():
    transaction = FeatureTransaction(ID, '2022-09-06T00:00:00+00:00', FEATURES)
    scorer = synthetic_scorer(THRESHOLD)
    result = scorer.score(transaction)
    assert result.risk_score == THRESHOLD
    assert result.review_status == 'review_recommended'
    assert scorer.score(FeatureTransaction(ID, transaction.occurred_at_utc, FEATURES)).source == 'model'
    assert scorer.preprocessor.currency_vocabulary[-1] == '__UNKNOWN__'
    assert scorer.booster.matrix.shape == (1, 32)
    assert np.count_nonzero(scorer.booster.matrix[0, 9:]) == 2
    assert scorer.booster.matrix[0, 24] == 1.0  # unknown currency bucket
    assert synthetic_scorer(THRESHOLD - 0.01).score(transaction).review_status == 'below_threshold'


def test_malformed_feature_or_score_cannot_become_zero_risk():
    transaction = FeatureTransaction(ID, '2022-09-06T00:00:00+00:00', FEATURES)
    for score in (float('nan'), -0.1, 1.1):
        with pytest.raises(ModelUnavailable):
            synthetic_scorer(score).score(transaction)
    with pytest.raises(ModelUnavailable):
        synthetic_scorer(0.1).score(FeatureTransaction(
            ID, transaction.occurred_at_utc, {**FEATURES, 'is_laundering': 1}))
