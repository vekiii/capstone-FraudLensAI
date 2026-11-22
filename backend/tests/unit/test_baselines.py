"""Synthetic RED contracts for the frozen T223 comparison baselines."""

import importlib

import numpy as np
import pytest
from test_training_boundaries import GuardedLabels, partitions, row


def test_baselines_use_train_prevalence_and_frozen_estimator_settings():
    prepare = importlib.import_module('fraudlens.training.boundaries').prepare_training_views
    fit_baselines = importlib.import_module('fraudlens.training.baselines').fit_baselines
    labels = GuardedLabels()
    views = prepare(partitions(), label_reader=labels)

    fitted = fit_baselines(views)

    assert set(fitted) == {'prevalence_constant', 'decision_tree', 'logistic_regression'}
    assert fitted['prevalence_constant'].positive_probability == 0.5
    tree = fitted['decision_tree']
    assert tree.max_depth == 5
    assert tree.min_samples_leaf == 500
    assert tree.class_weight == {0: 1.0, 1: 1.0}
    logistic = fitted['logistic_regression'].estimator
    assert logistic.l1_ratio == 0.0  # L2 in the locked scikit-learn API.
    assert logistic.C == 1.0
    assert logistic.class_weight == {0: 1.0, 1: 1.0}
    assert labels.calls == [('train', ('train-z', 'train-a')), ('validation', ('valid',))]
    for model in fitted.values():
        scores = model.predict_proba(views.preprocessor.matrix(views.validation.features))
        assert scores.shape == (1, 2)
        assert np.all(np.isfinite(scores))
        assert np.all((0 <= scores) & (scores <= 1))


def test_single_class_training_is_rejected_before_any_fit():
    prepare = importlib.import_module('fraudlens.training.boundaries').prepare_training_views
    fit_baselines = importlib.import_module('fraudlens.training.baselines').fit_baselines
    views = prepare(partitions(), label_reader=lambda _partition, ids: (0,) * len(ids))

    with pytest.raises(ValueError, match='both classes'):
        fit_baselines(views)


def test_imbalance_and_numeric_scaling_use_training_rows_only():
    prepare = importlib.import_module('fraudlens.training.boundaries').prepare_training_views
    fit_baselines = importlib.import_module('fraudlens.training.baselines').fit_baselines
    rows = partitions()
    rows['train'] = tuple(
        row(f'train-{index}', 'USD', 'Wire', paid=str(index + 1))
        for index in range(6)
    )
    rows['validation'] = (row('valid', 'USD', 'Wire', paid='1000000'),)
    views = prepare(
        rows,
        label_reader=lambda partition, ids: (
            (1, 1, 0, 0, 0, 0) if partition == 'train' else (0,)
        ),
    )

    fitted = fit_baselines(views)

    assert fitted['prevalence_constant'].positive_probability == 2 / 6
    assert fitted['decision_tree'].class_weight == {0: 1.0, 1: 2.0}
    assert fitted['logistic_regression'].estimator.class_weight == {0: 1.0, 1: 2.0}
    assert fitted['logistic_regression'].scaler.mean_[3] == 3.5
