"""Frozen, label-free rules-v1 over history-v1 snapshots."""

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from fraudlens.data_contracts import ScoreRequestV2, _request_v2

RULE_VERSION = 'rules-v1'
POLICY = {
    'aggregation': 'sum_fired_weights_exact_decimal',
    'coverage_required': 'full_after_source_start_plus_24h',
    'feature_version': 'history-v1',
    'r1': {'feature': 'sender_out_count_24h', 'minimum': 3, 'weight': '0.35'},
    'r2': {'feature': 'receiver_in_count_24h', 'minimum': 3, 'weight': '0.30'},
    'r3': {
        'comparison': 'current_times_count_gte_multiplier_times_sum_exact_decimal',
        'count': 'sender_paid_count_same_currency_24h',
        'current': 'current_paid_amount', 'minimum_count': 3, 'multiplier': '2',
        'sum': 'sender_paid_sum_same_currency_24h', 'weight': '0.35',
        'when_count_below_minimum': 'comparison_unavailable_zero_contribution',
    },
    'rule_version': RULE_VERSION, 'score_kind': 'ordinal_rule_score',
}
POLICY_SHA256 = hashlib.sha256(json.dumps(
    POLICY, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode()).hexdigest()
assert POLICY_SHA256 == 'a281d38b8777b53882f4515dda7de927ff64dce43188e99c258419b1d605b5ce'


@dataclass(frozen=True)
class RuleReason:
    rule_id: str
    observed_count: int
    observed_amount: Decimal | None
    currency: str | None
    comparison: str
    threshold: str
    state: str
    contribution: Decimal
    rule_version: str = RULE_VERSION


@dataclass(frozen=True)
class RuleEvaluation:
    score: Decimal
    reasons: tuple[RuleReason, ...]
    policy_version: str = RULE_VERSION
    policy_sha256: str = POLICY_SHA256


def evaluate_rules(request: ScoreRequestV2) -> RuleEvaluation:
    """Evaluate exact frozen thresholds; absent history raises, not zero-fills."""
    _request_v2(request)
    if request.scorer_version != RULE_VERSION:
        raise ValueError('rule scorer version mismatch')
    values = request.feature_snapshot.feature_values
    sender = values['sender_out_count_24h']
    receiver = values['receiver_in_count_24h']
    count = values['sender_paid_count_same_currency_24h']
    amount = values['current_paid_amount']
    paid_sum = values['sender_paid_sum_same_currency_24h']
    currency = values['current_paid_currency']
    r1 = sender >= 3
    r2 = receiver >= 3
    r3_available = count >= 3
    r3 = r3_available and amount * count >= Decimal(2) * paid_sum
    reasons = (
        RuleReason('R1', sender, None, None, f'{sender} >= 3', '3',
                   'fired' if r1 else 'not_fired', Decimal('0.35') if r1 else Decimal(0)),
        RuleReason('R2', receiver, None, None, f'{receiver} >= 3', '3',
                   'fired' if r2 else 'not_fired', Decimal('0.30') if r2 else Decimal(0)),
        RuleReason('R3', count, amount, currency,
                   (f'{amount}*{count} >= 2*{paid_sum}' if r3_available
                    else 'comparison unavailable: fewer than 3 prior paid events'),
                   'current*count >= 2*prior_paid_sum; prior_count >= 3',
                   ('comparison_unavailable' if not r3_available else
                    'fired' if r3 else 'not_fired'),
                   Decimal('0.35') if r3 else Decimal(0)),
    )
    return RuleEvaluation(sum((item.contribution for item in reasons), Decimal(0)),
                          reasons)


class RuleScorer:
    """ScorerV2-compatible rules adapter; no model or provider dependency."""

    requires_artifact = False

    def score(self, request: ScoreRequestV2) -> dict:
        from fraudlens.explanations import rule_explanation

        result = evaluate_rules(request)
        snapshot = request.feature_snapshot
        return {
            'transaction_id': request.canonical_transaction.transaction_id,
            'dataset_version': request.dataset_version, 'run_id': request.run_id,
            'score': result.score, 'score_kind': 'ordinal_rule_score',
            'score_source': 'rules', 'scorer_version': RULE_VERSION,
            'feature_version': request.feature_version, 'artifact_version': RULE_VERSION,
            'event_time_utc': request.canonical_transaction.event_time_utc,
            'history_cutoff_exclusive_at': request.history_cutoff_exclusive_at,
            'scored_at': datetime.now(UTC),
            'history_coverage': {'state': snapshot.coverage_state,
                                 'start': snapshot.coverage_start},
            'explanation': rule_explanation(request, result),
        }
