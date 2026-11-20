"""Deterministic validation metrics and current-phase LightGBM selection.

Inputs are precomputed validation scores. This module does not fit estimators,
read sealed labels, or apply a daily alert quota.
"""

import math
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import groupby
from typing import Any

import numpy as np

_TOP_K = (20, 50, 100)


@dataclass(frozen=True)
class ThresholdChoice:
    threshold: float
    f1: float
    precision: float
    recall: float


@dataclass(frozen=True)
class ValidationEvaluation:
    count: int
    positive_count: int
    prevalence: float
    threshold: float
    f1: float
    precision: float
    recall: float
    average_precision: float
    roc_auc: float
    brier_score: float
    confusion_matrix: dict[str, int]
    precision_at: dict[int, float]
    recall_at: dict[int, float]
    top_k_denominators: dict[int, int]
    pr_curve: tuple[tuple[float, float, float], ...]
    daily_alert_counts: dict[str, int]


def _validated_binary_scores(
    labels: Sequence[int], scores: Sequence[float],
) -> tuple[tuple[int, ...], tuple[float, ...]]:
    if len(labels) != len(scores) or len(labels) == 0:
        raise ValueError('labels and scores must have matching nonempty lengths')
    if any(isinstance(label, (bool, np.bool_)) or not isinstance(label, (int, np.integer))
           or label not in (0, 1) for label in labels):
        raise ValueError('labels must be binary integers')
    positives = sum(labels)
    if positives == 0 or positives == len(labels):
        raise ValueError('validation labels must contain both classes')
    checked_scores = []
    for score in scores:
        if isinstance(score, (bool, np.bool_)) or not isinstance(
            score, (int, float, np.integer, np.floating),
        ):
            raise ValueError('scores must be numeric and finite in [0,1]')
        value = float(score)
        if not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError('scores must be numeric and finite in [0,1]')
        checked_scores.append(value)
    return tuple(int(label) for label in labels), tuple(checked_scores)


def _score_groups(
    labels: tuple[int, ...], scores: tuple[float, ...],
) -> tuple[tuple[float, int, int], ...]:
    ordered = sorted(zip(scores, labels, strict=True), key=lambda pair: -pair[0])
    return tuple(
        (score, sum(label for _, label in group_rows), len(group_rows) - sum(
            label for _, label in group_rows
        ))
        for score, group in groupby(ordered, key=lambda pair: pair[0])
        for group_rows in (tuple(group),)
    )


def _choose_from_groups(
    groups: tuple[tuple[float, int, int], ...], positives: int,
) -> ThresholdChoice:
    tp = fp = 0
    best: tuple[float, int, int] | None = None
    for score, group_positive, group_negative in groups:
        tp += group_positive
        fp += group_negative
        predicted = tp + fp
        f1_denom = positives + predicted
        if best is None:
            best = (score, tp, fp)
            continue
        best_score, best_tp, best_fp = best
        best_predicted = best_tp + best_fp
        best_f1_denom = positives + best_predicted
        f1_comparison = tp * best_f1_denom - best_tp * f1_denom
        precision_comparison = tp * best_predicted - best_tp * predicted
        if (f1_comparison > 0 or (f1_comparison == 0 and precision_comparison > 0)
                or (f1_comparison == 0 and precision_comparison == 0
                    and score > best_score)):
            best = (score, tp, fp)
    assert best is not None
    score, tp, fp = best
    predicted = tp + fp
    return ThresholdChoice(
        threshold=score,
        f1=2 * tp / (positives + predicted),
        precision=tp / predicted,
        recall=tp / positives,
    )


def choose_threshold(labels: Sequence[int], scores: Sequence[float]) -> ThresholdChoice:
    """Maximize positive F1 over distinct scores, then precision and threshold."""
    checked_labels, checked_scores = _validated_binary_scores(labels, scores)
    return _choose_from_groups(_score_groups(checked_labels, checked_scores),
                               sum(checked_labels))


def _validated_identity_time(
    ids: Sequence[str], instants: Sequence[datetime], count: int,
) -> tuple[tuple[str, ...], tuple[datetime, ...]]:
    if len(ids) != count or len(instants) != count:
        raise ValueError('IDs and instants must align with validation scores')
    if any(not isinstance(identity, str) or not identity.strip() for identity in ids):
        raise ValueError('transaction IDs must be nonempty text')
    if len(set(ids)) != count:
        raise ValueError('validation transaction IDs must be unique')
    if any(not isinstance(instant, datetime) or instant.tzinfo is None
           or instant.utcoffset() is None for instant in instants):
        raise ValueError('validation instants must be timezone-aware')
    return tuple(ids), tuple(instant.astimezone(timezone.utc) for instant in instants)


def evaluate_validation(
    labels: Sequence[int],
    scores: Sequence[float],
    transaction_ids: Sequence[str],
    occurred_at_utc: Sequence[datetime],
) -> ValidationEvaluation:
    """Report validation-only metrics and every UTC day's uncapped alert count."""
    checked_labels, checked_scores = _validated_binary_scores(labels, scores)
    ids, instants = _validated_identity_time(
        transaction_ids, occurred_at_utc, len(checked_labels),
    )
    count = len(checked_labels)
    positives = sum(checked_labels)
    negatives = count - positives
    groups = _score_groups(checked_labels, checked_scores)
    selected = _choose_from_groups(groups, positives)

    tp = fp = 0
    ap = auc_pairs = 0.0
    pr_curve = []
    for score, group_positive, group_negative in groups:
        lower_negatives = negatives - fp - group_negative
        auc_pairs += group_positive * (lower_negatives + group_negative / 2)
        tp += group_positive
        fp += group_negative
        precision = tp / (tp + fp)
        recall = tp / positives
        ap += group_positive / positives * precision
        pr_curve.append((recall, precision, score))

    ranked = sorted(range(count), key=lambda index: (-checked_scores[index], ids[index]))
    precision_at = {}
    recall_at = {}
    denominators = {}
    for k in _TOP_K:
        denominator = min(k, count)
        hits = sum(checked_labels[index] for index in ranked[:denominator])
        precision_at[k] = hits / denominator
        recall_at[k] = hits / positives
        denominators[k] = denominator

    alerts = tuple(score >= selected.threshold for score in checked_scores)
    true_positive = sum(label and alert for label, alert in zip(checked_labels, alerts,
                                                               strict=True))
    false_positive = sum(not label and alert for label, alert in zip(checked_labels, alerts,
                                                                    strict=True))
    by_day: Counter[str] = Counter()
    for instant, alert in zip(instants, alerts, strict=True):
        day = instant.date().isoformat()
        by_day[day] += int(alert)
    brier = sum((score - label) ** 2 for label, score in zip(checked_labels, checked_scores,
                                                            strict=True)) / count
    return ValidationEvaluation(
        count=count,
        positive_count=positives,
        prevalence=positives / count,
        threshold=selected.threshold,
        f1=selected.f1,
        precision=selected.precision,
        recall=selected.recall,
        average_precision=ap,
        roc_auc=auc_pairs / (positives * negatives),
        brier_score=brier,
        confusion_matrix={
            'tn': negatives - false_positive,
            'fp': false_positive,
            'fn': positives - true_positive,
            'tp': true_positive,
        },
        precision_at=precision_at,
        recall_at=recall_at,
        top_k_denominators=denominators,
        pr_curve=tuple(pr_curve),
        daily_alert_counts=dict(sorted(by_day.items())),
    )


def rank_lightgbm_candidates(
    results: Sequence[Mapping[str, Any]],
) -> Mapping[str, Any]:
    """Apply the current LightGBM-only frozen validation ranking."""
    if not results:
        raise ValueError('at least one LightGBM candidate result is required')
    validated = []
    seen_indices = set()
    for result in results:
        if not isinstance(result, Mapping) or result.get('family') != 'lightgbm':
            raise ValueError('current selection phase accepts LightGBM only')
        for name in ('f1', 'average_precision', 'precision_at_20'):
            value = result.get(name)
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not math.isfinite(value) or not 0 <= value <= 1):
                raise ValueError(f'{name} must be finite in [0,1]')
        for name in ('num_leaves', 'min_child_samples', 'best_iteration', 'candidate_index'):
            value = result.get(name)
            if type(value) is not int or value < (0 if name == 'candidate_index' else 1):
                raise ValueError(f'{name} must be a valid integer')
        rate = result.get('learning_rate')
        if (isinstance(rate, bool) or not isinstance(rate, (int, float))
                or not math.isfinite(rate) or rate <= 0):
            raise ValueError('learning_rate must be positive and finite')
        if result['candidate_index'] in seen_indices:
            raise ValueError('candidate indices must be unique')
        seen_indices.add(result['candidate_index'])
        validated.append(result)
    return min(validated, key=lambda item: (
        -item['f1'],
        -item['average_precision'],
        -item['precision_at_20'],
        item['num_leaves'],
        -item['min_child_samples'],
        item['learning_rate'],
        item['best_iteration'],
        item['candidate_index'],
    ))
