"""Frozen train-only prevalence, decision-tree and L2 logistic baselines."""

from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from fraudlens.training.boundaries import TrainingViews


@dataclass(frozen=True)
class PrevalenceConstant:
    positive_probability: float

    def predict_proba(self, matrix: np.ndarray) -> np.ndarray:
        score = self.positive_probability
        return np.tile(np.array([1.0 - score, score]), (len(matrix), 1))


@dataclass(frozen=True)
class ScaledLogistic:
    """Retain the train-fitted numeric scaler for subsequent predictions."""

    estimator: LogisticRegression
    scaler: StandardScaler
    numeric_width: int

    def predict_proba(self, matrix: np.ndarray) -> np.ndarray:
        prepared = matrix.copy()
        prepared[:, :self.numeric_width] = self.scaler.transform(
            prepared[:, :self.numeric_width],
        )
        return self.estimator.predict_proba(prepared)


def fit_baselines(
    views: TrainingViews,
) -> dict[str, PrevalenceConstant | DecisionTreeClassifier | ScaledLogistic]:
    """Fit the three declared candidates using training features and labels only.

    Validation, test and showcase are never passed to estimator or scaler fit.
    This entry point is for synthetic checks until the FR-021 fit gate opens.
    """
    labels = np.asarray(views.train.labels, dtype=np.int8)
    positives = int(np.count_nonzero(labels))
    negatives = len(labels) - positives
    if positives == 0 or negatives == 0:
        raise ValueError('training labels must contain both classes')
    weights = {0: 1.0, 1: negatives / positives}
    train = views.preprocessor.matrix(views.train.features)

    tree = DecisionTreeClassifier(
        max_depth=5,
        min_samples_leaf=500,
        class_weight=weights,
        random_state=42,
    )
    tree.fit(train, labels)

    scaler = StandardScaler()
    logistic_train = train.copy()
    numeric_width = views.preprocessor.numeric_width
    logistic_train[:, :numeric_width] = scaler.fit_transform(
        logistic_train[:, :numeric_width],
    )
    logistic = LogisticRegression(
        l1_ratio=0.0,
        C=1.0,
        solver='lbfgs',
        max_iter=1000,
        class_weight=weights,
        random_state=42,
    )
    logistic.fit(logistic_train, labels)

    return {
        'prevalence_constant': PrevalenceConstant(positives / len(labels)),
        'decision_tree': tree,
        'logistic_regression': ScaledLogistic(logistic, scaler, numeric_width),
    }
