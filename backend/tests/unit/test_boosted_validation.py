"""Controlled checks for the separate validation-only boosted experiment."""

import numpy as np
import pytest

from fraudlens.compare_boosted_phase5 import fit_boosted, summarize


def test_summary_uses_stable_id_ties_and_whole_score_threshold():
    ids = ('D3', 'D1', 'D2', 'D4')
    scores = np.array([0.9, 0.9, 0.9, 0.1])
    labels = np.array([1, 0, 1, 0])
    result = summarize(ids, scores, labels, k=2)
    assert result['positive_top_20'] == 1
    assert result['highest_score_rows'] == 3
    assert result['rank_20_tie']['crosses_boundary'] is True
    assert result['threshold']['threshold'] == 'no_alert'
    assert result['alerts'] == 0


def test_boosted_fit_is_train_only_and_unknown_categories_score():
    train = np.array([
        [0.0, 'EUR'], [1.0, 'EUR'], [2.0, 'USD'], [3.0, 'USD'],
        [4.0, 'EUR'], [5.0, 'USD'], [6.0, 'EUR'], [7.0, 'USD'],
    ], dtype=object)
    labels = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    validation = np.array([[8.0, 'NEW'], [9.0, 'EUR']], dtype=object)
    pipeline, scores = fit_boosted(train, labels, validation,
                                   numeric_columns=(0,), categorical_columns=(1,))
    assert len(scores) == 2
    assert np.isfinite(scores).all()
    assert 'NEW' not in pipeline.named_steps['prepare'].named_transformers_[
        'category'].categories_[0]
    numeric = pipeline.named_steps['prepare'].named_transformers_['numeric']
    assert numeric.named_steps['imputer'].statistics_[0] == 3.5
    assert numeric.named_steps['scale'].mean_[0] == 3.5


def test_summary_rejects_invalid_scores():
    with pytest.raises(ValueError):
        summarize(('D1', 'D2'), [float('nan'), 0.5], [0, 1])
