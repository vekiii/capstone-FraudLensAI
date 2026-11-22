"""No-fit contract tests for array-backed LightGBM setup."""

import numpy as np
import pytest

from fraudlens.training import candidates


def test_matrix_grid_weights_from_train_only_and_uses_all_frozen_candidates(monkeypatch):
    observed = []

    def fit(candidate, train, labels, validation, validation_labels, weight, n_jobs):
        observed.append((candidate, weight, n_jobs, labels.copy()))
        return candidate

    monkeypatch.setattr(candidates, '_fit_lightgbm', fit)
    models = candidates.fit_lightgbm_matrix_grid(
        np.zeros((4, 2)), np.array([1, 0, 0, 0]),
        np.zeros((3, 2)), np.array([1, 1, 0]), n_jobs=3,
    )

    assert models == candidates.LIGHTGBM_GRID
    assert len(observed) == 8
    assert {row[1] for row in observed} == {3.0}
    assert {row[2] for row in observed} == {3}


def test_matrix_grid_refuses_single_class_train_and_uninformative_validation():
    features = np.zeros((3, 1))
    with pytest.raises(ValueError, match='training labels'):
        candidates.fit_lightgbm_matrix_grid(
            features, np.array([0, 0, 0]), features, np.array([1, 0, 0]), n_jobs=1,
        )
    with pytest.raises(ValueError, match='no positive'):
        candidates.fit_lightgbm_matrix_grid(
            features, np.array([1, 0, 0]), features, np.array([0, 0, 0]), n_jobs=1,
        )
