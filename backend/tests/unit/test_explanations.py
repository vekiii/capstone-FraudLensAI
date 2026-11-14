"""T039: fixed arithmetic and real fitted path explanation contracts."""

import importlib
from dataclasses import replace
from decimal import Decimal

import numpy as np
import pytest
from test_rule_scoring import history, request


def api():
    module = importlib.import_module('fraudlens.explanations')
    assert callable(getattr(module, 'additive_explanation', None))
    return module


def test_known_top_three_tie_remainder_and_reconstruction():
    module = api()
    fact, snapshot = history()
    req = request(fact, snapshot)
    contributions = [
        ('sender_out_count_24h', Decimal('0.2')),
        ('receiver_in_count_24h', Decimal('-0.3')),
        ('current_paid_amount', Decimal('0.3')),
        ('current_paid_currency', Decimal('0.1')),
    ]
    explanation = module.additive_explanation(
        req, contributions, base=Decimal('0.4'),
        scale='positive_class_estimate', method='tree_path',
        expected=Decimal('0.7'), tolerance=Decimal('1e-8'))
    assert explanation['feature_snapshot_digest'] == snapshot.feature_input_digest
    assert [item['feature_key'] for item in explanation['items']] == [
        'receiver_in_count_24h', 'current_paid_amount', 'sender_out_count_24h']
    assert explanation['items'][0]['observed_value'] == str(
        snapshot.feature_values['receiver_in_count_24h'])
    assert explanation['items'][1]['unit'] == 'Euro'
    assert explanation['items'][0]['direction'] == 'decreases'
    assert explanation['partial'] is True
    assert explanation['base_value'] + explanation['remainder'] + sum(
        (item['contribution'] for item in explanation['items']), Decimal(0)) == Decimal('0.7')


@pytest.mark.parametrize('change', [
    {'scale': 'log_odds'}, {'method': 'global_importance'},
    {'expected': Decimal('0.5')},
    {'contributions': [('current_paid_amount', Decimal('NaN'))]},
])
def test_wrong_scale_method_score_or_nonfinite_rejected(change):
    module = api()
    fact, snapshot = history()
    args = dict(request=request(fact, snapshot),
                contributions=[('current_paid_amount', Decimal('0.2'))],
                base=Decimal('0.4'), scale='positive_class_estimate',
                method='tree_path', expected=Decimal('0.6'),
                tolerance=Decimal('1e-8'))
    with pytest.raises(ValueError):
        module.additive_explanation(**(args | change))


def test_unavailable_is_explicit_and_rule_conditions_are_actual():
    module = api()
    fact, snapshot = history()
    req = request(fact, snapshot)
    unavailable = module.unavailable_explanation(req, 'missing_context')
    assert unavailable == {'status': 'unavailable', 'reason_code': 'missing_context',
                           'feature_snapshot_digest': snapshot.feature_input_digest}
    from fraudlens.rule_scoring import evaluate_rules

    rule = module.rule_explanation(req, evaluate_rules(req))
    assert rule['method'] == 'rules'
    assert rule['explained_scale'] == 'risk_score'
    assert rule['items'][0]['rule_condition'].startswith('fired:')
    assert rule['base_value'] + rule['remainder'] + sum(
        (item['contribution'] for item in rule['items']), Decimal(0)) == Decimal('1.00')


def test_fixed_linear_log_odds_and_wrong_snapshot_identity_rejected():
    module = api()
    fact, snapshot = history()
    req = request(fact, snapshot)
    explanation = module.additive_explanation(
        req, [('sender_out_count_24h', Decimal('1')),
              ('receiver_in_count_24h', Decimal('-1'))],
        base=Decimal(0), scale='log_odds', method='linear_log_odds',
        expected=Decimal('0.5'), tolerance=Decimal('1e-8'))
    assert explanation['partial'] is False
    assert explanation['base_value'] + explanation['remainder'] + sum(
        (item['contribution'] for item in explanation['items']), Decimal(0)) == 0
    with pytest.raises(ValueError, match='identity'):
        module.additive_explanation(
            replace(req, canonical_transaction=replace(fact, transaction_id='wrong')),
            [], base=Decimal(0), scale='log_odds', method='linear_log_odds',
            expected=Decimal('0.5'), tolerance=Decimal('1e-8'))
    with pytest.raises(ValueError, match='digest'):
        module.additive_explanation(
            replace(req, feature_snapshot=replace(snapshot,
                                                   feature_input_digest='0' * 64)),
            [], base=Decimal(0), scale='log_odds', method='linear_log_odds',
            expected=Decimal('0.5'), tolerance=Decimal('1e-8'))


def test_linear_fitted_coefficients_follow_actual_transformed_values():
    module = api()
    fact, snapshot = history()
    req = replace(request(fact, snapshot), scorer_version='model-history-v1')

    class Prepare:
        n_features_in_ = 2
        transformers_ = [('numeric', object(), [0, 1])]

        def get_feature_names_out(self):
            return ['numeric__sender_out_count_24h', 'numeric__receiver_in_count_24h']

        def transform(self, row):
            return row

    class Linear:
        classes_ = np.array([0, 1])
        coef_ = np.array([[1.0, -1.0]])
        intercept_ = np.array([0.0])

    class Pipeline:
        named_steps = {'prepare': Prepare(), 'model': Linear()}

    explanation = module.model_explanation(
        req, Pipeline(), np.array([[3.0, 3.0]]), Decimal('0.5'),
        ['sender_out_count_24h', 'receiver_in_count_24h'])
    assert explanation['method'] == 'linear_log_odds'
    assert explanation['explained_scale'] == 'log_odds'
    assert [item['contribution'] for item in explanation['items']] == [
        Decimal('3.0'), Decimal('-3.0')]
