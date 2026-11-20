"""Frozen T224 LightGBM and histogram-gradient candidate fits.

These finite-batch functions exercise synthetic contracts. Real-source fitting
requires the separate FR-021 protocol/provenance and resource preflight gate.
"""

from dataclasses import dataclass
from itertools import product

import lightgbm as lgb
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from threadpoolctl import threadpool_limits

from fraudlens.training.boundaries import TrainingViews


@dataclass(frozen=True)
class LightGBMCandidate:
    num_leaves: int
    learning_rate: float
    min_child_samples: int


@dataclass(frozen=True)
class HistGradientCandidate:
    max_iter: int
    learning_rate: float
    max_leaf_nodes: int
    l2_regularization: float


LIGHTGBM_GRID = tuple(
    LightGBMCandidate(leaves, rate, minimum)
    for leaves, rate, minimum in product((31, 63), (0.05, 0.1), (50, 200))
)
HIST_GRADIENT_GRID = (
    HistGradientCandidate(200, 0.05, 15, 0.0),
    HistGradientCandidate(200, 0.05, 31, 0.0),
    HistGradientCandidate(300, 0.05, 31, 1.0),
    HistGradientCandidate(200, 0.1, 15, 0.0),
    HistGradientCandidate(300, 0.1, 31, 1.0),
)


def _training_labels(views: TrainingViews) -> tuple[np.ndarray, float]:
    labels = np.asarray(views.train.labels, dtype=np.int8)
    positives = int(np.count_nonzero(labels))
    negatives = len(labels) - positives
    if positives == 0 or negatives == 0:
        raise ValueError('training labels must contain both classes')
    return labels, negatives / positives


def _fit_lightgbm(
    candidate: LightGBMCandidate,
    train: np.ndarray,
    labels: np.ndarray,
    validation: np.ndarray,
    validation_labels: np.ndarray,
    positive_weight: float,
    n_jobs: int,
) -> lgb.LGBMClassifier:
    model = lgb.LGBMClassifier(
        objective='binary',
        boosting_type='gbdt',
        metric='binary_logloss',
        n_estimators=1000,
        num_leaves=candidate.num_leaves,
        learning_rate=candidate.learning_rate,
        min_child_samples=candidate.min_child_samples,
        scale_pos_weight=positive_weight,
        random_state=42,
        n_jobs=n_jobs,
        device_type='cpu',
        deterministic=True,
        force_col_wise=True,
        verbosity=-1,
    )
    model.fit(
        train,
        labels,
        eval_set=[(validation, validation_labels)],
        eval_names=['validation'],
        eval_metric='binary_logloss',
        callbacks=[lgb.early_stopping(50, first_metric_only=True, verbose=False)],
    )
    return model


def fit_lightgbm_candidate(
    views: TrainingViews,
    candidate: LightGBMCandidate,
    *,
    n_jobs: int,
) -> lgb.LGBMClassifier:
    """Fit one declared configuration; validation is used for early stopping."""
    if candidate not in LIGHTGBM_GRID:
        raise ValueError('LightGBM candidate must belong to the frozen grid')
    if type(n_jobs) is not int or n_jobs < 1:
        raise ValueError('n_jobs must be a positive integer from the preflight policy')
    labels, positive_weight = _training_labels(views)
    train = views.preprocessor.matrix(views.train.features)
    validation = views.preprocessor.matrix(views.validation.features)
    validation_labels = np.asarray(views.validation.labels, dtype=np.int8)
    return _fit_lightgbm(
        candidate, train, labels, validation, validation_labels, positive_weight, n_jobs,
    )


def fit_lightgbm_grid(
    views: TrainingViews,
    *,
    n_jobs: int,
) -> tuple[lgb.LGBMClassifier, ...]:
    """Fit all eight declared LightGBM configurations in frozen grid order."""
    if type(n_jobs) is not int or n_jobs < 1:
        raise ValueError('n_jobs must be a positive integer from the preflight policy')
    labels, positive_weight = _training_labels(views)
    train = views.preprocessor.matrix(views.train.features)
    validation = views.preprocessor.matrix(views.validation.features)
    validation_labels = np.asarray(views.validation.labels, dtype=np.int8)
    return tuple(
        _fit_lightgbm(
            candidate, train, labels, validation, validation_labels, positive_weight, n_jobs,
        )
        for candidate in LIGHTGBM_GRID
    )


def fit_lightgbm_matrix_grid(
    train: np.ndarray,
    labels: np.ndarray,
    validation: np.ndarray,
    validation_labels: np.ndarray,
    *,
    n_jobs: int,
) -> tuple[lgb.LGBMClassifier, ...]:
    """Fit the frozen LightGBM grid from preprocessed arrays."""
    if type(n_jobs) is not int or n_jobs < 1:
        raise ValueError('n_jobs must be a positive integer')
    y_train = np.asarray(labels, dtype=np.int8)
    y_validation = np.asarray(validation_labels, dtype=np.int8)
    if (train.ndim != 2 or validation.ndim != 2 or train.shape[1] != validation.shape[1]
            or train.shape[0] != len(y_train) or validation.shape[0] != len(y_validation)
            or not np.isin(y_train, (0, 1)).all()
            or not np.isin(y_validation, (0, 1)).all()):
        raise ValueError('training and validation arrays must be aligned binary matrices')
    positives = int(np.count_nonzero(y_train))
    negatives = len(y_train) - positives
    if positives == 0 or negatives == 0:
        raise ValueError('training labels must contain both classes')
    if int(np.count_nonzero(y_validation)) == 0:
        raise ValueError('validation has no positive examples; model selection is uninformative')
    weight = negatives / positives
    return tuple(
        _fit_lightgbm(candidate, train, y_train, validation, y_validation, weight, n_jobs)
        for candidate in LIGHTGBM_GRID
    )


def _fit_hist_gradient(
    candidate: HistGradientCandidate,
    train: np.ndarray,
    labels: np.ndarray,
    sample_weights: np.ndarray,
    n_jobs: int,
) -> HistGradientBoostingClassifier:
    model = HistGradientBoostingClassifier(
        loss='log_loss',
        early_stopping=False,
        min_samples_leaf=500,
        random_state=42,
        max_iter=candidate.max_iter,
        learning_rate=candidate.learning_rate,
        max_leaf_nodes=candidate.max_leaf_nodes,
        l2_regularization=candidate.l2_regularization,
    )
    with threadpool_limits(limits=n_jobs):
        model.fit(train, labels, sample_weight=sample_weights)
    return model


def fit_hist_gradient_candidate(
    views: TrainingViews,
    candidate: HistGradientCandidate,
    *,
    n_jobs: int,
) -> HistGradientBoostingClassifier:
    """Fit one declared HGB comparison using train rows only."""
    if candidate not in HIST_GRADIENT_GRID:
        raise ValueError('histogram-gradient candidate must belong to the frozen grid')
    if type(n_jobs) is not int or n_jobs < 1:
        raise ValueError('n_jobs must be a positive integer from the preflight policy')
    labels, positive_weight = _training_labels(views)
    train = views.preprocessor.matrix(views.train.features)
    weights = np.where(labels == 1, positive_weight, 1.0)
    return _fit_hist_gradient(candidate, train, labels, weights, n_jobs)


def fit_hist_gradient_grid(
    views: TrainingViews,
    *,
    n_jobs: int,
) -> tuple[HistGradientBoostingClassifier, ...]:
    """Fit all five declared HGB comparisons in frozen grid order."""
    if type(n_jobs) is not int or n_jobs < 1:
        raise ValueError('n_jobs must be a positive integer from the preflight policy')
    labels, positive_weight = _training_labels(views)
    train = views.preprocessor.matrix(views.train.features)
    weights = np.where(labels == 1, positive_weight, 1.0)
    return tuple(
        _fit_hist_gradient(candidate, train, labels, weights, n_jobs)
        for candidate in HIST_GRADIENT_GRID
    )
