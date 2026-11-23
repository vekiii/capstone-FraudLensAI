"""Isolated calculation prototype; no API, bridge, or investigation integration."""

import math

import numpy as np

from fraudlens.data.features import FEATURE_ORDER
from fraudlens.scoring.model_scorer import FeatureTransaction, ModelScorer, ModelUnavailable
from fraudlens.training.boundaries import _validate_row


def stable_binary_score(raw: float, sigmoid: float) -> float:
    if not math.isfinite(raw) or not math.isfinite(sigmoid) or sigmoid <= 0:
        raise ValueError('invalid binary margin or sigmoid')
    value = raw * sigmoid
    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    exp_value = math.exp(value)
    return exp_value / (1.0 + exp_value)


def compute_local_contributions(scorer: ModelScorer,
                                transaction: FeatureTransaction) -> dict:
    """Verify native additive output against the unchanged scoring path."""
    if not isinstance(scorer, ModelScorer):
        raise ModelUnavailable('trusted scorer required')
    existing = scorer.score(transaction)
    objective = scorer.booster.dump_model()['objective']
    if objective != 'binary sigmoid:1':
        raise ModelUnavailable('unsupported objective')
    row = {'transaction_id': transaction.transaction_id, **transaction.features}
    _validate_row(row)
    matrix = scorer.preprocessor.matrix(scorer.preprocessor.transform((row,)))
    currency = scorer.preprocessor.currency_vocabulary
    payment_format = scorer.preprocessor.format_vocabulary
    expected = [*(name for name in FEATURE_ORDER if name not in
                  ('current_payment_currency', 'current_payment_format')),
                *(f'current_payment_currency={value}' for value in currency),
                *(f'current_payment_format={value}' for value in payment_format)]
    if (scorer.manifest['matrix_feature_order'] != expected
            or matrix.shape != (1, len(expected))
            or scorer.booster.num_feature() != len(expected)):
        raise ModelUnavailable('matrix feature identity or order mismatch')
    iterations = scorer.booster.current_iteration()
    probability = np.asarray(scorer.booster.predict(matrix, num_iteration=iterations,
                                                     num_threads=4), dtype=np.float64)
    raw = np.asarray(scorer.booster.predict(matrix, raw_score=True,
                                             num_iteration=iterations, num_threads=4),
                     dtype=np.float64)
    contributions = np.asarray(scorer.booster.predict(matrix, pred_contrib=True,
                                                       num_iteration=iterations,
                                                       num_threads=4), dtype=np.float64)
    if (probability.shape != (1,) or raw.shape != (1,)
            or contributions.shape != (1, len(expected) + 1)
            or not np.isfinite(probability).all() or not np.isfinite(raw).all()
            or not np.isfinite(contributions).all()):
        raise ModelUnavailable('native contribution shape or value mismatch')
    score, raw_score = float(probability[0]), float(raw[0])
    values = [float(x) for x in contributions[0, :-1]]
    base = float(contributions[0, -1])
    if (abs(math.fsum((base, *values)) - raw_score) > 1e-8
            or abs(stable_binary_score(raw_score, 1.0) - score) > 1e-12
            or abs(score - existing.risk_score) > 1e-12):
        raise ModelUnavailable('native contribution reconstruction mismatch')
    groups = {name: 0.0 for name in FEATURE_ORDER}
    by_group = {name: [] for name in FEATURE_ORDER}
    for name, value in zip(expected, values, strict=True):
        key = name.split('=', 1)[0]
        by_group[key].append(value)
    for key, parts in by_group.items():
        groups[key] = math.fsum(parts)
    if abs(math.fsum(groups.values()) - math.fsum(values)) > 1e-8:
        raise ModelUnavailable('grouping sum mismatch')
    ordered = sorted(groups, key=lambda key: (-abs(groups[key]), key))
    top3 = [dict(feature_key=key, contribution=groups[key]) for key in ordered[:3]]
    remainder = math.fsum(groups[key] for key in ordered[3:])
    return dict(transaction_id=transaction.transaction_id, score=score,
                raw_score=raw_score, base_value=base,
                matrix_contributions=values, groups=groups,
                top3=top3, remainder=remainder, num_iteration=iterations,
                objective=objective)
