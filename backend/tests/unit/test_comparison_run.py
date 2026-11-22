"""Synthetic cross-family comparison contracts; no project-data fits."""

from datetime import datetime, timezone

import numpy as np
import pytest

from fraudlens.training.comparison_run import _score_model, compare_matrices, validate_plan


def test_plan_rejects_changed_grid():
    with pytest.raises(ValueError, match='plan'):
        validate_plan({'baselines': [], 'hist_gradient_boosting': []})


def test_synthetic_outputs_and_train_only_scaling(tmp_path):
    rng = np.random.default_rng(42)
    train = rng.normal(size=(1100, 4))
    labels = np.array([0] * 900 + [1] * 200, dtype=np.int8)
    validation = rng.normal(size=(120, 4))
    validation_labels = np.array([0] * 100 + [1] * 20, dtype=np.int8)
    ids = [f'tx-{index:03d}' for index in range(120)]
    instants = [datetime(2022, 9, 5, tzinfo=timezone.utc)] * 120
    results = compare_matrices(train, labels, validation, validation_labels,
                               ids, instants, tmp_path, n_jobs=2, synthetic=True)
    assert [result['name'] for result in results] == [
        'prevalence_constant', 'decision_tree', 'logistic_regression',
        *(f'hist_gradient_boosting_{index}' for index in range(1, 6)),
    ]
    assert all((tmp_path / 'candidates' / result['name'] / 'result.json').is_file()
               for result in results)
    assert all(result['metrics']['threshold'] is not None for result in results)
    logistic = next(item for item in results if item['name'] == 'logistic_regression')
    assert logistic['parameters']['scaler_mean'] == pytest.approx(train.mean(axis=0))
    assert logistic['parameters']['numeric_width'] == 4
    assert [item['family'] for item in results[3:]] == ['hist_gradient_boosting'] * 5
    assert all(item['model_sha256'] and item['validation_scores_sha256'] for item in results)


def test_nonfinite_candidate_score_is_rejected():
    class Broken:
        def predict_proba(self, matrix):
            return np.column_stack((np.zeros(len(matrix)), np.full(len(matrix), np.nan)))

    with pytest.raises(ValueError, match='invalid probabilities'):
        _score_model('broken', Broken(), np.zeros((2, 1)))
