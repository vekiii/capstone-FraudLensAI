"""T033 RED: frozen prediction metrics and holdout disclosure lifecycle."""

import json

import pytest

from fraudlens import evaluation


def test_hand_metrics_top_k_tie_and_threshold_counts():
    ids = ['b', 'a', 'c', 'd']
    scores = [0.9, 0.9, 0.5, 0.1]
    labels = [0, 1, 1, 0]
    report = evaluation.calculate_metrics(ids, scores, labels, threshold=0.9,
                                          k=1, probability=True)
    assert report['average_precision'] == pytest.approx((0.5 + 2 / 3) / 2)
    assert report['precision_at_k'] == 1
    assert report['recall_at_k'] == 0.5
    assert report['k_crosses_score_tie'] is True
    assert report['confusion'] == {'tp': 1, 'fp': 1, 'tn': 1, 'fn': 1}
    assert report['prevalence'] == 0.5
    assert report['alert_rate'] == 0.5
    assert report['brier'] == pytest.approx((0.9**2 + 0.1**2 + 0.5**2 + 0.1**2) / 4)


def test_zero_alert_and_ordinal_rules_brier_absent():
    report = evaluation.calculate_metrics(['a', 'b'], [0.0, 0.65], [0, 1],
                                          threshold='no_alert', probability=False)
    assert report['confusion'] == {'tp': 0, 'fp': 0, 'tn': 1, 'fn': 1}
    assert report['threshold_precision'] is None
    assert report['brier'] is None
    assert report['uncertainty_status'] == 'not_quantified'


def test_reject_ineligible_population_and_mismatched_scorer_ids():
    with pytest.raises(ValueError):
        evaluation.calculate_metrics(['a', 'b'], [0.2, 0.3], [1, 1],
                                     threshold=0.5, probability=True)
    with pytest.raises(ValueError):
        evaluation.evaluate_frozen({'model': [('a', 0.3)],
                                    'rules': [('b', 0.6)]}, {'a': 1, 'b': 0},
                                   {'model': 0.5, 'rules': 0.5})
    with pytest.raises(ValueError):
        evaluation.calculate_metrics(['a', 'b'], [0.2, 0.3], [0.5, 1],
                                     threshold=0.5, probability=True)


def test_seen_unseen_coverage_and_capacity_minimum():
    predictions = {'model': [('a', 0.7), ('b', 0.3)],
                   'rules': [('a', 0.65), ('b', 0.0)]}
    output = evaluation.evaluate_frozen(predictions, {'a': 1, 'b': 0},
                                        {'model': 0.5, 'rules': 0.65},
                                        account_seen={'a': True, 'b': False})
    assert output['model']['k'] == 2
    assert output['model']['account_coverage'] == {
        'status': 'measured', 'seen': 1, 'unseen': 1, 'seen_rate': 0.5}
    assert output['rules']['brier'] is None
    with pytest.raises(ValueError):
        evaluation.evaluate_frozen(predictions, {'a': 1, 'b': 0},
                                   {'model': 0.5, 'rules': 0.65},
                                   account_seen={'a': True})


def test_atomic_holdout_first_disclosure_then_exploratory_reuse(tmp_path):
    ledger = tmp_path / 'holdout.json'
    first = evaluation.consume_holdout(ledger, 'protocol-hash', 'predictions-hash')
    assert first == 'first_disclosure'
    assert json.loads(ledger.read_text())['predictions_hash'] == 'predictions-hash'
    assert evaluation.consume_holdout(ledger, 'protocol-hash', 'predictions-hash') \
        == 'exploratory_reuse'
    with pytest.raises(ValueError):
        evaluation.consume_holdout(ledger, 'protocol-hash', 'changed-predictions')
