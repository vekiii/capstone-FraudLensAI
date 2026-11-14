"""T030 RED: train-only preparation, bounded grid, selection and thresholds."""

import numpy as np
import pytest
from sklearn.pipeline import Pipeline

from fraudlens import evaluation


def test_fit_grid_uses_train_only_statistics_and_six_candidates():
    train = np.array([[0., 'Euro'], [1., 'Euro'], [2., 'US Dollar'],
                      [3., 'US Dollar'], [4., 'Euro'], [5., 'Euro']], dtype=object)
    validation = np.array([[1000., 'Unseen'], [2000., 'Unseen']], dtype=object)
    result = evaluation.fit_candidate_grid(
        train, np.array([0, 0, 0, 1, 1, 1]), validation,
        np.array([0, 1]), ('a', 'b'), numeric_columns=(0,),
        categorical_columns=(1,), candidates=(('logistic_l2', 0.1),
                                               ('decision_tree', 3, 1)))
    assert len(result) == 2
    for item in result:
        prep = item['pipeline'].named_steps['prepare']
        numeric = prep.named_transformers_['numeric']
        assert numeric.named_steps['imputer'].statistics_[0] == 2.5
        assert numeric.named_steps['scale'].mean_[0] == 2.5
        assert 'Unseen' not in prep.named_transformers_['category'].categories_[0]
        assert len(item['validation_scores']) == 2


def test_selection_ap_tie_uses_precision_then_grid_order():
    rows = [{'ap': 0.4, 'precision_at_k': 0.3},
            {'ap': 0.4 + 5e-7, 'precision_at_k': 0.5},
            {'ap': 0.4 + 5e-7, 'precision_at_k': 0.5}]
    assert evaluation.select_candidate(rows, ap_tolerance=1e-6) == 1


def test_inclusive_threshold_preserves_ties_and_can_choose_no_alert():
    choice = evaluation.select_threshold([0.9, 0.9, 0.4], [1, 0, 1], max_alerts=2)
    assert choice['threshold'] == 0.9
    assert choice['alerts'] == 2
    none = evaluation.select_threshold([0.2, 0.1], [0, 0], max_alerts=1)
    assert none['threshold'] == 'no_alert'
    assert none['alerts'] == 0


def test_candidate_limit_and_nonfinite_scores_fail_closed():
    with pytest.raises(ValueError):
        evaluation.select_candidate([{'ap': float('nan'), 'precision_at_k': 0.1}])
    with pytest.raises(ValueError):
        evaluation.select_threshold([float('nan')], [1])
    with pytest.raises(ValueError):
        evaluation.select_candidate([{'ap': 0.1, 'precision_at_k': 0.1}] * 7)
    with pytest.raises(ValueError):
        evaluation.select_threshold([0.5], [0.5])
    with pytest.raises(ValueError):
        evaluation.select_candidate([{'status': 'failed',
                                      'failure_type': 'RuntimeError'}])


def test_supervised_fit_receives_only_train_rows_and_failure_is_explicit(monkeypatch):
    train = np.array([[0., 'a'], [1., 'a'], [2., 'b'], [3., 'b']], dtype=object)
    validation = np.array([[100., 'new'], [101., 'new']], dtype=object)
    seen = []
    original_fit = Pipeline.fit

    def checked_fit(self, x, y, **kwargs):
        seen.append((len(x), tuple(y)))
        return original_fit(self, x, y, **kwargs)

    monkeypatch.setattr(Pipeline, 'fit', checked_fit)
    results = evaluation.fit_candidate_grid(
        train, [0, 0, 1, 1], validation, [0, 1], ('v1', 'v2'),
        numeric_columns=(0,), categorical_columns=(1,),
        candidates=(('decision_tree', 3, 1),))
    assert results[0]['status'] == 'complete'
    assert seen[0] == (4, (0, 0, 1, 1))
    assert all(count != 2 for count, _ in seen)

    def failing_fit(self, x, y, **kwargs):
        raise RuntimeError('controlled fit failure')

    monkeypatch.setattr(Pipeline, 'fit', failing_fit)
    failed = evaluation.fit_candidate_grid(
        train, [0, 0, 1, 1], validation, [0, 1], ('v1', 'v2'),
        numeric_columns=(0,), categorical_columns=(1,),
        candidates=(('decision_tree', 3, 1),))
    assert failed[0]['status'] == 'failed'
    assert failed[0]['failure_type'] == 'RuntimeError'
