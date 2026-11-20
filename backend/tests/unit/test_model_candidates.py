"""RED contracts for the frozen T224 model families on invented rows."""

import importlib
import json
from pathlib import Path

import pytest
from test_training_boundaries import row

CHOICES = json.loads(
    (Path(__file__).resolve().parents[3] / 'specs/002-data-and-risk-scoring/t221-model-choices.json')
    .read_text(encoding='utf-8'),
)


def prepared_views():
    prepare = importlib.import_module('fraudlens.training.boundaries').prepare_training_views
    rows = {
        'train': tuple(
            row(f'train-{index}', 'USD' if index % 2 else 'EUR',
                'Wire' if index % 2 else 'ACH', paid=str(index + 1))
            for index in range(40)
        ),
        'validation': tuple(row(f'valid-{index}', 'EUR', 'ACH', paid=str(index + 1))
                            for index in range(8)),
        'test': (row('test', 'GBP', 'Card'),),
        'showcase': (row('showcase', 'CAD', 'Cheque'),),
    }
    calls = []

    def labels(partition, ids):
        calls.append((partition, tuple(ids)))
        assert partition in {'train', 'validation'}
        return tuple(int(int(identity.rsplit('-', 1)[1]) % 4 == 0) for identity in ids)

    return prepare(rows, label_reader=labels), calls


def test_candidate_grids_match_frozen_choices_and_order():
    candidates = importlib.import_module('fraudlens.training.candidates')
    lightgbm = CHOICES['candidates']['lightgbm']
    expected_lightgbm = [
        (leaves, rate, minimum)
        for leaves in lightgbm['num_leaves']
        for rate in lightgbm['learning_rate']
        for minimum in lightgbm['min_child_samples']
    ]
    assert [(item.num_leaves, item.learning_rate, item.min_child_samples)
            for item in candidates.LIGHTGBM_GRID] == expected_lightgbm
    assert [
        (item.max_iter, item.learning_rate, item.max_leaf_nodes, item.l2_regularization)
        for item in candidates.HIST_GRADIENT_GRID
    ] == [
        (item['max_iter'], item['learning_rate'], item['max_leaf_nodes'],
         item['l2_regularization'])
        for item in CHOICES['candidates']['hist_gradient_boosting']['grid']
    ]


class FakeEstimator:
    """Capture fit calls without training any model."""

    def __init__(self, **settings):
        self.settings = settings
        self.fit_call = None

    def fit(self, *args, **kwargs):
        self.fit_call = (args, kwargs)
        return self


def test_lightgbm_fit_call_uses_train_and_validation_only(monkeypatch):
    candidates = importlib.import_module('fraudlens.training.candidates')
    views, calls = prepared_views()
    monkeypatch.setattr(candidates.lgb, 'LGBMClassifier', FakeEstimator)

    model = candidates.fit_lightgbm_candidate(views, candidates.LIGHTGBM_GRID[0], n_jobs=1)

    assert model.settings['n_estimators'] == 1000
    assert model.settings['scale_pos_weight'] == 3.0
    assert model.settings['n_jobs'] == 1
    assert model.settings['metric'] == 'binary_logloss'
    assert model.settings['deterministic'] is True
    args, kwargs = model.fit_call
    assert args[0].shape[0] == 40
    assert args[1].tolist() == list(views.train.labels)
    assert len(kwargs['eval_set']) == 1
    assert kwargs['eval_set'][0][0].shape[0] == 8
    assert kwargs['eval_set'][0][1].tolist() == list(views.validation.labels)
    assert kwargs['eval_names'] == ['validation']
    assert kwargs['eval_metric'] == 'binary_logloss'
    assert len(kwargs['callbacks']) == 1
    assert kwargs['callbacks'][0].stopping_rounds == 50
    assert kwargs['callbacks'][0].first_metric_only is True
    assert len(calls) == 2


def test_hist_gradient_fit_call_uses_train_only_weighting(monkeypatch):
    candidates = importlib.import_module('fraudlens.training.candidates')
    views, calls = prepared_views()
    monkeypatch.setattr(candidates, 'HistGradientBoostingClassifier', FakeEstimator)

    model = candidates.fit_hist_gradient_candidate(views, candidates.HIST_GRADIENT_GRID[0],
                                                   n_jobs=1)

    assert model.settings['early_stopping'] is False
    assert model.settings['min_samples_leaf'] == 500
    assert model.settings['max_iter'] == 200
    args, kwargs = model.fit_call
    assert args[0].shape[0] == 40
    assert args[1].tolist() == list(views.train.labels)
    assert kwargs['sample_weight'].tolist() == [3.0 if label else 1.0
                                                 for label in views.train.labels]
    assert len(calls) == 2


def test_grid_dispatches_all_thirteen_declared_candidates_without_training(monkeypatch):
    candidates = importlib.import_module('fraudlens.training.candidates')
    views, _ = prepared_views()
    monkeypatch.setattr(candidates.lgb, 'LGBMClassifier', FakeEstimator)
    monkeypatch.setattr(candidates, 'HistGradientBoostingClassifier', FakeEstimator)

    lightgbm = candidates.fit_lightgbm_grid(views, n_jobs=1)
    hist = candidates.fit_hist_gradient_grid(views, n_jobs=1)

    assert len(lightgbm) == 8
    assert len(hist) == 5
    assert [(model.settings['num_leaves'], model.settings['learning_rate'],
             model.settings['min_child_samples']) for model in lightgbm] == [
                 (item.num_leaves, item.learning_rate, item.min_child_samples)
                 for item in candidates.LIGHTGBM_GRID
             ]
    assert all(model.fit_call is not None for model in (*lightgbm, *hist))


@pytest.mark.parametrize('family', ['lightgbm', 'hist_gradient'])
def test_both_families_reject_single_class_training(family, monkeypatch):
    candidates = importlib.import_module('fraudlens.training.candidates')
    views, _ = prepared_views()
    monkeypatch.setattr(candidates.lgb, 'LGBMClassifier', FakeEstimator)
    monkeypatch.setattr(candidates, 'HistGradientBoostingClassifier', FakeEstimator)
    object.__setattr__(views.train, 'labels', (0,) * len(views.train.labels))
    with pytest.raises(ValueError, match='both classes'):
        if family == 'lightgbm':
            candidates.fit_lightgbm_candidate(views, candidates.LIGHTGBM_GRID[0], n_jobs=1)
        else:
            candidates.fit_hist_gradient_candidate(views, candidates.HIST_GRADIENT_GRID[0],
                                                   n_jobs=1)
