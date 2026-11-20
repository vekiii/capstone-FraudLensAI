"""T225 RED contracts for validation-only scoring; no estimator is fitted."""

import importlib
import math
from datetime import datetime, timezone

import pytest


def evaluation():
    try:
        module = importlib.import_module('fraudlens.training.evaluation')
    except ModuleNotFoundError as error:
        if error.name != 'fraudlens.training.evaluation':
            raise
        pytest.fail('Missing T226 validation evaluation boundary', pytrace=False)
    return module


def instants(count, *, day=1):
    return tuple(datetime(2022, 9, day, tzinfo=timezone.utc) for _ in range(count))


def candidate(index, **changes):
    record = {
        'family': 'lightgbm',
        'candidate_index': index,
        'f1': 0.5,
        'average_precision': 0.6,
        'precision_at_20': 0.7,
        'num_leaves': 31,
        'min_child_samples': 200,
        'learning_rate': 0.05,
        'best_iteration': 100,
    }
    record.update(changes)
    return record


def test_threshold_maximizes_positive_class_f1_not_accuracy_or_default_half():
    selected = evaluation().choose_threshold((1, 0, 1, 0), (0.9, 0.8, 0.7, 0.1))

    assert selected.threshold == 0.7
    assert selected.f1 == pytest.approx(0.8)
    assert selected.precision == pytest.approx(2 / 3)
    assert selected.recall == 1.0


def test_equal_f1_thresholds_prefer_higher_precision():
    selected = evaluation().choose_threshold((1, 0, 0, 1), (0.9, 0.8, 0.7, 0.6))

    assert selected.threshold == 0.9
    assert selected.f1 == pytest.approx(2 / 3)
    assert selected.precision == 1.0


def test_validation_metrics_use_explicit_denominators_and_positive_class():
    result = evaluation().evaluate_validation(
        labels=(1, 0, 1, 0),
        scores=(0.9, 0.8, 0.7, 0.1),
        transaction_ids=('a', 'b', 'c', 'd'),
        occurred_at_utc=instants(4),
    )

    assert result.count == 4
    assert result.positive_count == 2
    assert result.prevalence == 0.5
    assert result.threshold == 0.7
    assert result.f1 == pytest.approx(0.8)
    assert result.average_precision == pytest.approx(5 / 6)
    assert result.roc_auc == pytest.approx(0.75)
    assert result.brier_score == pytest.approx(0.1875)
    assert result.confusion_matrix == {'tn': 1, 'fp': 1, 'fn': 0, 'tp': 2}
    assert result.precision_at[20] == pytest.approx(0.5)
    assert result.recall_at[20] == 1.0
    assert result.top_k_denominators[20] == 4
    assert result.top_k_denominators[50] == 4
    assert result.top_k_denominators[100] == 4
    assert result.pr_curve


def test_precision_at_20_breaks_score_ties_by_transaction_id():
    labels = (1,) * 19 + (0, 1)
    scores = (0.9,) * 19 + (0.5, 0.5)
    result = evaluation().evaluate_validation(
        labels=labels,
        scores=scores,
        transaction_ids=tuple(f'p{index:02d}' for index in range(19)) + ('A', 'Z'),
        occurred_at_utc=instants(21),
    )

    assert result.precision_at[20] == pytest.approx(19 / 20)
    assert result.recall_at[20] == pytest.approx(19 / 20)
    assert result.top_k_denominators[20] == 20


def test_daily_alert_counts_preserve_zero_and_more_than_twenty():
    result = evaluation().evaluate_validation(
        labels=(1,) * 22 + (0,),
        scores=(0.9,) * 22 + (0.1,),
        transaction_ids=tuple(f'id-{index}' for index in range(23)),
        occurred_at_utc=instants(22) + instants(1, day=2),
    )

    assert result.daily_alert_counts == {'2022-09-01': 22, '2022-09-02': 0}
    assert sum(result.daily_alert_counts.values()) == 22


@pytest.mark.parametrize('bad_score', [math.nan, math.inf, -math.inf, -0.01, 1.01, '0.5'])
def test_nonfinite_out_of_range_or_non_numeric_scores_are_rejected(bad_score):
    with pytest.raises(ValueError):
        evaluation().choose_threshold((1, 0), (bad_score, 0.2))


@pytest.mark.parametrize('labels,scores', [((1, 0), (0.5,)), ((1, 2), (0.5, 0.2)),
                                           ((1, 1), (0.5, 0.2)), ((), ())])
def test_invalid_or_single_class_validation_is_rejected(labels, scores):
    with pytest.raises(ValueError):
        evaluation().choose_threshold(labels, scores)


def test_evaluation_rejects_duplicate_ids_and_naive_times():
    module = evaluation()
    with pytest.raises(ValueError):
        module.evaluate_validation((1, 0), (0.9, 0.1), ('same', 'same'), instants(2))
    with pytest.raises(ValueError):
        module.evaluate_validation(
            (1, 0), (0.9, 0.1), ('a', 'b'),
            (datetime(2022, 9, 1), datetime(2022, 9, 2, tzinfo=timezone.utc)),
        )


@pytest.mark.parametrize(
    'first,second,winning_index',
    [
        (candidate(0, f1=0.8, average_precision=0.1),
         candidate(1, f1=0.7, average_precision=0.9), 0),
        (candidate(0, average_precision=0.8, precision_at_20=0.1),
         candidate(1, average_precision=0.7, precision_at_20=0.9), 0),
        (candidate(0, precision_at_20=0.8, num_leaves=63),
         candidate(1, precision_at_20=0.7, num_leaves=31), 0),
        (candidate(0, num_leaves=63), candidate(1, num_leaves=31), 1),
        (candidate(0, min_child_samples=50), candidate(1, min_child_samples=200), 1),
        (candidate(0, learning_rate=0.1), candidate(1, learning_rate=0.05), 1),
        (candidate(0, best_iteration=120), candidate(1, best_iteration=100), 1),
        (candidate(0), candidate(1), 0),
    ],
)
def test_lightgbm_ranking_obeys_metric_and_frozen_tie_order(first, second, winning_index):
    winner = evaluation().rank_lightgbm_candidates((first, second))

    assert winner['candidate_index'] == winning_index


def test_current_phase_ranking_refuses_other_families_and_bad_metrics():
    module = evaluation()
    with pytest.raises(ValueError):
        module.rank_lightgbm_candidates((candidate(0), candidate(1, family='decision_tree')))
    with pytest.raises(ValueError):
        module.rank_lightgbm_candidates((candidate(0, f1=math.nan),))
